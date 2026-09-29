from __future__ import annotations

from copy import deepcopy
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
import json
import re
from typing import Any

from errata.consequence import compute
from errata.models import Operation, ServiceChange
from errata.reducer import Reducer, DomainConflict, ReducerError, StaleState
from errata.validators import blocking_failures, validate


class PreparationError(Exception):
    pass


@dataclass
class BoundTranscript:
    item_id: str
    text: str


@dataclass
class PendingCall:
    call_id: str
    expected_hash: str
    operations: list[Operation]
    transcript: BoundTranscript
    raw_arguments: dict[str, Any]
    prepared_at: str


def _clock_text(text: str) -> str:
    """Strict bounded parser for the killer experiment, not a general NL time parser."""
    t = text.strip().lower().replace(".", "")
    m = re.fullmatch(r"(\d{1,2})(?::(\d{2}))?\s*(am|pm)?", t)
    if not m:
        raise PreparationError(f"UNRESOLVED_TIME:{text}")
    hour = int(m.group(1))
    minute = int(m.group(2) or "00")
    ampm = m.group(3)
    if minute > 59:
        raise PreparationError(f"UNRESOLVED_TIME:{text}")
    if ampm:
        if not 1 <= hour <= 12:
            raise PreparationError(f"UNRESOLVED_TIME:{text}")
        if ampm == "pm" and hour != 12:
            hour += 12
        elif ampm == "am" and hour == 12:
            hour = 0
    elif hour > 29:
        raise PreparationError(f"UNRESOLVED_TIME:{text}")
    return f"{hour:02d}:{minute:02d}:00"


class CandidateResolver:
    """Turns LLM-proposed mention operations into deterministic reducer operations."""

    DIRECTION_ALIASES = {
        "west": 1,
        "westbound": 1,
        "wb": 1,
        "east": 0,
        "eastbound": 0,
        "eb": 0,
    }

    def __init__(self, gtfs):
        self.gtfs = gtfs

    def _stop_from_current_skip_set(self, mention: str, state: ServiceChange) -> str | None:
        normalized = " ".join(mention.lower().replace("/", " ").split())
        hits = []
        for stop_id in state.skip_stops:
            stop = self.gtfs.stop_by_id.get(stop_id)
            if not stop:
                continue
            name = " ".join(stop.stop_name.lower().replace("/", " ").split())
            if normalized == name or normalized in name or name in normalized:
                hits.append(stop_id)
        return hits[0] if len(hits) == 1 else None

    def prepare(
        self,
        *,
        state: ServiceChange,
        call_id: str,
        arguments: dict[str, Any],
        transcript: BoundTranscript,
    ) -> PendingCall:
        candidates = arguments.get("operations")
        if not isinstance(candidates, list) or not candidates:
            raise PreparationError("EMPTY_OPERATION_BATCH")

        route_id = state.route_ref.value if state.route_ref else None
        direction_id = int(state.route_direction.value) if state.route_direction else None
        ops: list[Operation] = []
        expected_hash = state.state_hash

        for idx, candidate in enumerate(candidates):
            if not isinstance(candidate, dict):
                raise PreparationError("INVALID_OPERATION_OBJECT")
            kind = candidate.get("kind")
            text = str(candidate.get("text", "")).strip()
            if not text:
                raise PreparationError(f"EMPTY_VALUE:{kind}")

            payload: dict[str, Any]
            reducer_kind: str

            if kind == "SET_ROUTE_MENTION":
                resolved = self.gtfs.resolve_route(text)
                if not resolved:
                    raise PreparationError(f"UNRESOLVED_ROUTE:{text}")
                route_id = resolved
                reducer_kind, payload = "SET_ROUTE", {"route_id": resolved}

            elif kind == "SET_DIRECTION_MENTION":
                alias = " ".join(text.lower().split())
                if alias not in self.DIRECTION_ALIASES:
                    raise PreparationError(f"UNRESOLVED_DIRECTION:{text}")
                direction_id = self.DIRECTION_ALIASES[alias]
                reducer_kind, payload = "SET_DIRECTION", {"direction_id": direction_id}

            elif kind in ("ADD_SKIP_STOP_MENTION", "REMOVE_SKIP_STOP_MENTION"):
                if route_id is None or direction_id is None:
                    raise PreparationError("ROUTE_DIRECTION_REQUIRED_BEFORE_STOP")
                if kind == "REMOVE_SKIP_STOP_MENTION":
                    stop_id = self._stop_from_current_skip_set(text, state)
                    candidates_scored = []
                    if stop_id is None:
                        stop_id, candidates_scored = self.gtfs.resolve_stop(text, route_id, direction_id)
                else:
                    stop_id, candidates_scored = self.gtfs.resolve_stop(text, route_id, direction_id)
                if not stop_id:
                    raise PreparationError(
                        "UNRESOLVED_STOP:" + text + ":" + json.dumps(candidates_scored)
                    )
                reducer_kind = "ADD_SKIP_STOP" if kind == "ADD_SKIP_STOP_MENTION" else "REMOVE_SKIP_STOP"
                payload = {"stop_id": stop_id}

            elif kind == "SET_START_TIME_TEXT":
                reducer_kind, payload = "SET_TIME_WINDOW", {"start_time": _clock_text(text)}

            elif kind == "SET_END_TIME_TEXT":
                reducer_kind, payload = "SET_TIME_WINDOW", {"end_time": _clock_text(text)}

            elif kind == "SET_REASON_TEXT":
                reducer_kind, payload = "SET_REASON", {"reason": text.upper().replace(" ", "_")[:80]}

            else:
                raise PreparationError(f"UNKNOWN_CANDIDATE_KIND:{kind}")

            ops.append(
                Operation(
                    operation_id=f"{call_id}:{idx}",
                    kind=reducer_kind,
                    expected_hash=expected_hash,
                    payload=payload,
                    turn_id=transcript.item_id,
                    transcript_text=transcript.text,
                    source="voice_live_candidate",
                )
            )

        return PendingCall(
            call_id=call_id,
            expected_hash=expected_hash,
            operations=ops,
            transcript=transcript,
            raw_arguments=arguments,
            prepared_at=datetime.now(timezone.utc).isoformat(),
        )


class LiveTransactionCoordinator:
    """Enforces PREPARE → terminal reply state → APPLY/DISCARD."""

    def __init__(self, state: ServiceChange, reducer: Reducer, gtfs):
        self.state = state
        self.reducer = reducer
        self.gtfs = gtfs
        self.resolver = CandidateResolver(gtfs)
        self.latest_transcript: BoundTranscript | None = None
        self.pending: list[PendingCall] = []

    def bind_user_transcript(self, item_id: str, text: str) -> None:
        self.latest_transcript = BoundTranscript(item_id=item_id, text=text)

    def prepare_tool_call(self, event: dict[str, Any]) -> dict[str, Any]:
        if event.get("name") != "propose_service_change":
            raise PreparationError(f"UNSUPPORTED_TOOL:{event.get('name')}")
        if self.latest_transcript is None:
            raise PreparationError("NO_FINAL_TRANSCRIPT_BOUND")

        args = event.get("arguments", {})
        if isinstance(args, str):
            args = json.loads(args)
        call = self.resolver.prepare(
            state=self.state,
            call_id=event["call_id"],
            arguments=args,
            transcript=self.latest_transcript,
        )
        self.pending.append(call)
        return {
            "status": "PREPARED",
            "call_id": call.call_id,
            "expected_hash": call.expected_hash,
            "operation_count": len(call.operations),
            "canonical_revision": self.state.revision,
        }

    def discard_pending(self, reason: str) -> list[dict[str, Any]]:
        before = self.state.state_hash
        discarded = [
            {
                "call_id": p.call_id,
                "status": "DISCARDED",
                "reason": reason,
                "expected_hash": p.expected_hash,
                "canonical_hash_before": before,
                "canonical_hash_after": self.state.state_hash,
            }
            for p in self.pending
        ]
        self.pending.clear()
        return discarded

    def finalize_pending(self) -> list[dict[str, Any]]:
        if not self.pending:
            return []

        expected = self.state.state_hash
        if any(p.expected_hash != expected for p in self.pending):
            stale = self.discard_pending("STALE_PENDING_HASH")
            return stale

        # Dry-run in a deep copy first. Blocking validation never gets to mutate truth.
        dry_state = deepcopy(self.state)
        dry_reducer = deepcopy(self.reducer)
        dry_ops = [deepcopy(op) for p in self.pending for op in p.operations]

        try:
            dry_reducer.apply_batch(dry_state, dry_ops, self.gtfs)
            validation = validate(dry_state, self.gtfs)
            failures = blocking_failures(validation)
            if failures:
                results = [
                    {
                        "call_id": p.call_id,
                        "status": "REVIEW_REQUIRED",
                        "reason": "BLOCKING_VALIDATION",
                        "failures": [f.to_dict() for f in failures],
                    }
                    for p in self.pending
                ]
                self.pending.clear()
                return results
        except (PreparationError, DomainConflict, ReducerError, StaleState) as exc:
            results = [
                {"call_id": p.call_id, "status": "REJECTED", "reason": str(exc)}
                for p in self.pending
            ]
            self.pending.clear()
            return results

        real_ops = [deepcopy(op) for p in self.pending for op in p.operations]
        calls = [p.call_id for p in self.pending]
        before_hash = self.state.state_hash
        before_revision = self.state.revision
        try:
            applied = self.reducer.apply_batch(self.state, real_ops, self.gtfs)
        except (DomainConflict, ReducerError, StaleState) as exc:
            results = [
                {"call_id": call_id, "status": "REJECTED", "reason": str(exc)}
                for call_id in calls
            ]
            self.pending.clear()
            return results

        validation = validate(self.state, self.gtfs)
        impact = compute(self.state, self.gtfs)
        self.pending.clear()
        return [
            {
                "call_id": call_id,
                "status": "APPLIED",
                "change_id": self.state.change_id,
                "before_revision": before_revision,
                "revision": self.state.revision,
                "before_hash": before_hash,
                "state_hash": self.state.state_hash,
                "validation": [v.to_dict() for v in validation],
                "impact": impact,
            }
            for call_id in calls
        ]

    def route_keyterms(self, limit: int = 100) -> list[str]:
        if not self.state.route_ref or self.state.route_direction is None:
            return []
        route_id = self.state.route_ref.value
        direction_id = int(self.state.route_direction.value)
        trip_ids = {
            t["trip_id"]
            for t in self.gtfs.trips
            if t["route_id"] == route_id and int(t["direction_id"]) == direction_id
        }
        stop_ids = {
            st["stop_id"]
            for st in self.gtfs.stop_times
            if st["trip_id"] in trip_ids
        }
        names = sorted(
            {
                self.gtfs.stop_by_id[s].stop_name
                for s in stop_ids
                if s in self.gtfs.stop_by_id
            }
        )
        return names[:limit]

    def snapshot(self) -> dict[str, Any]:
        return {
            "state": self.state.semantic_dict(),
            "state_hash": self.state.state_hash,
            "revision": self.state.revision,
            "pending_call_ids": [p.call_id for p in self.pending],
            "latest_transcript": asdict(self.latest_transcript) if self.latest_transcript else None,
        }
