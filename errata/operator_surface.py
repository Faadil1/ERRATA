from __future__ import annotations

from copy import deepcopy
from dataclasses import asdict
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
from threading import RLock
from time import time
from typing import Any

from errata.consequence import compute
from errata.gtfs import GTFSIndex
from errata.live.coordinator import LiveTransactionCoordinator, PreparationError
from errata.live.direct_entry import apply_direct_text
from errata.models import ChangeStatus, Operation, ServiceChange
from errata.reducer import Reducer, ReducerError, StaleState
from errata.serializer import serialize_trip_updates
from errata.validators import validate


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _pv_value(value):
    return None if value is None else value.value


def _business_diff(before: dict[str, Any], after: dict[str, Any]) -> list[dict[str, Any]]:
    ordered = [
        "route_ref",
        "route_direction",
        "service_date",
        "start_time",
        "end_time",
        "skip_stops",
        "closed_segment",
        "reason",
        "unresolved_items",
    ]
    return [
        {"field": key, "before": before.get(key), "after": after.get(key)}
        for key in ordered
        if before.get(key) != after.get(key)
    ]


class OperatorSurfaceSession:
    """Thin product surface over the canonical ERRATA Python core.

    This class owns no alternate business rules. It delegates parsing, resolution,
    validation, reduction, consequence calculation, serialization, and commit
    authority to the existing shared core.
    """

    def __init__(
        self,
        *,
        gtfs_dir: str | Path,
        evidence_file: str | Path | None = None,
        change_id: str = "ERR-UI-001",
        service_date: str = "20260929",
        start_time: str = "09:00:00",
    ):
        self.gtfs_dir = Path(gtfs_dir)
        self.evidence_file = Path(evidence_file) if evidence_file else None
        self.change_id = change_id
        self.service_date = service_date
        self.start_time = start_time
        self._lock = RLock()
        self._counter = 0
        self.reset()

    def _seed_context(self) -> None:
        expected = self.state.state_hash
        self.reducer.apply_batch(
            self.state,
            [
                Operation(
                    operation_id="ui-seed-service-date",
                    kind="SET_SERVICE_DATE",
                    expected_hash=expected,
                    payload={"service_date": self.service_date},
                    turn_id="ui-system-context",
                    transcript_text="Operator surface session context",
                    source="system_default",
                ),
                Operation(
                    operation_id="ui-seed-start-time",
                    kind="SET_TIME_WINDOW",
                    expected_hash=expected,
                    payload={"start_time": self.start_time},
                    turn_id="ui-system-context",
                    transcript_text="Operator surface session context",
                    source="system_default",
                ),
            ],
            self.gtfs,
        )

    def reset(self) -> dict[str, Any]:
        with self._lock:
            self.gtfs = GTFSIndex(self.gtfs_dir)
            self.state = ServiceChange(self.change_id)
            self.reducer = Reducer()
            self._seed_context()
            self.coordinator = LiveTransactionCoordinator(self.state, self.reducer, self.gtfs)
            self._counter = 0
            self._artifact_cache: dict[str, dict[str, Any]] = {}
            self.history: list[dict[str, Any]] = []
            self.latest_transaction: dict[str, Any] = {
                "status": "EMPTY",
                "observed_at": utc_now(),
                "detail": "No operator amendment has been applied in this session.",
            }
            return self.view()

    def _next_call_id(self) -> str:
        self._counter += 1
        return f"operator-ui-{self._counter}"

    def _evidence_summary(self) -> dict[str, Any]:
        if self.evidence_file and self.evidence_file.exists():
            try:
                payload = json.loads(self.evidence_file.read_text(encoding="utf-8"))
                return {
                    "status": "PROVEN_BOUNDED_SYNTHETIC_FIXTURE",
                    "source": self.evidence_file.as_posix(),
                    "workflow_run_id": payload.get("workflow_run_id"),
                    "artifact": payload.get("artifact"),
                    "validator": payload.get("validator"),
                    "inputs": payload.get("inputs"),
                    "official_bindings_consumer": payload.get("official_bindings_consumer"),
                    "truth_boundary": payload.get("truth_boundary"),
                }
            except Exception as exc:
                return {
                    "status": "EVIDENCE_READ_ERROR",
                    "source": self.evidence_file.as_posix(),
                    "detail": str(exc),
                }
        return {
            "status": "NOT_LOADED",
            "detail": "No checked-in external acceptance evidence file is available.",
        }

    def _validation(self) -> list[dict[str, Any]]:
        return [row.to_dict() for row in validate(self.state, self.gtfs)]

    def _impact(self) -> dict[str, Any] | None:
        required = (
            self.state.route_ref,
            self.state.route_direction,
            self.state.start_time,
            self.state.end_time,
        )
        if not all(required):
            return None
        return compute(self.state, self.gtfs)

    def _current_artifact(self) -> dict[str, Any]:
        impact = self._impact()
        if impact is None:
            return {
                "status": "NOT_GENERATED",
                "detail": "Route, direction, start, and end time are required.",
            }
        state_hash = self.state.state_hash
        cached = self._artifact_cache.get(state_hash)
        if cached is not None:
            return deepcopy(cached)

        generated_at = int(time())
        payload = serialize_trip_updates(self.state, impact, generated_at=generated_at)
        artifact = {
            "status": "CURRENT_LOCAL",
            "generated_from_hash": state_hash,
            "bytes": len(payload),
            "sha256": sha256(payload).hexdigest(),
            "generated_at": generated_at,
            "canonical_validator_scope": "REFERENCE_EVIDENCE_ONLY",
        }
        self._artifact_cache[state_hash] = artifact
        return deepcopy(artifact)

    def _state_view(self) -> dict[str, Any]:
        stop_names = {
            stop_id: self.gtfs.stop_by_id[stop_id].stop_name
            for stop_id in sorted(self.state.skip_stops)
            if stop_id in self.gtfs.stop_by_id
        }
        return {
            "change_id": self.state.change_id,
            "revision": self.state.revision,
            "state_hash": self.state.state_hash,
            "status": self.state.status.value,
            "route": _pv_value(self.state.route_ref),
            "direction": _pv_value(self.state.route_direction),
            "service_date": _pv_value(self.state.service_date),
            "start_time": _pv_value(self.state.start_time),
            "end_time": _pv_value(self.state.end_time),
            "skip_stops": [
                {"stop_id": stop_id, "stop_name": stop_names.get(stop_id, stop_id)}
                for stop_id in sorted(self.state.skip_stops)
            ],
            "reason": _pv_value(self.state.reason),
            "unresolved_items": deepcopy(self.state.unresolved_items),
            "pending_call_ids": [pending.call_id for pending in self.coordinator.pending],
            "committed_hash": self.state.committed_hash,
        }

    def view(self) -> dict[str, Any]:
        with self._lock:
            validation = self._validation()
            blocking_clear = all(row["status"] == "PASS" for row in validation)
            can_author = self.state.status == ChangeStatus.STAGED
            commit_ready = (
                can_author
                and blocking_clear
                and not self.coordinator.pending
            )
            return {
                "surface_schema": "errata-operator-review-v0.1",
                "observed_at": utc_now(),
                "truth_label": "SYNTHETIC_FIXTURE_LOCAL_SURFACE",
                "connection": {
                    "status": "LOCAL_READY",
                    "detail": "Browser surface is attached to the shared deterministic Python core.",
                },
                "capabilities": {
                    "can_author": can_author,
                    "commit_ready": commit_ready,
                    "can_reset_demo": True,
                },
                "state": self._state_view(),
                "validation": validation,
                "impact": self._impact(),
                "artifact": self._current_artifact(),
                "latest_transaction": deepcopy(self.latest_transaction),
                "history": deepcopy(self.history),
                "external_evidence": self._evidence_summary(),
            }

    def _amend_text(
        self,
        text: str,
        *,
        source: str,
        label: str,
        source_metadata: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        text = text.strip()
        if not text:
            raise ValueError("text is required")

        with self._lock:
            before_hash = self.state.state_hash
            before_revision = self.state.revision
            before_business = deepcopy(self.state.normalized_business_state())
            call_id = self._next_call_id()

            if self.state.status == ChangeStatus.COMMITTED:
                transaction = {
                    "call_id": call_id,
                    "source": source,
                    "source_metadata": deepcopy(source_metadata) if source_metadata else None,
                    "text": text,
                    "status": "REJECTED",
                    "reason": "CHANGE_ALREADY_COMMITTED",
                    "before_revision": before_revision,
                    "revision": self.state.revision,
                    "before_hash": before_hash,
                    "state_hash": self.state.state_hash,
                    "diff": [],
                    "observed_at": utc_now(),
                }
                self.latest_transaction = transaction
                self.history.append(deepcopy(transaction))
                return self.view()

            try:
                result = apply_direct_text(
                    self.coordinator,
                    label=label,
                    text=text,
                    entry_elapsed_ms=0.0,
                    call_id=call_id,
                )
                outcome = result.result[0] if result.result else {"status": "REJECTED", "reason": "NO_RESULT"}
                status = outcome.get("status", "UNKNOWN")
                reason = outcome.get("reason")
                parsed_operations = result.parsed_operations
            except PreparationError as exc:
                status = "REVIEW_REQUIRED"
                reason = str(exc)
                parsed_operations = []
                outcome = {"status": status, "reason": reason}
            except (ReducerError, StaleState) as exc:
                status = "REJECTED"
                reason = str(exc)
                parsed_operations = []
                outcome = {"status": status, "reason": reason}

            after_business = deepcopy(self.state.normalized_business_state())
            transaction = {
                "call_id": call_id,
                "source": source,
                "source_metadata": deepcopy(source_metadata) if source_metadata else None,
                "text": text,
                "parsed_operations": parsed_operations,
                "status": status,
                "reason": reason,
                "before_revision": before_revision,
                "revision": self.state.revision,
                "before_hash": before_hash,
                "state_hash": self.state.state_hash,
                "diff": _business_diff(before_business, after_business),
                "outcome": outcome,
                "observed_at": utc_now(),
            }
            self.latest_transaction = transaction
            self.history.append(deepcopy(transaction))
            return self.view()

    def amend_direct(self, text: str) -> dict[str, Any]:
        return self._amend_text(
            text,
            source="human_direct_entry",
            label="operator-surface-direct",
        )

    def amend_voice(
        self,
        text: str,
        *,
        assemblyai_session_id: str | None = None,
        boundary: str = "ForceEndpoint",
        client_captured_at: str | None = None,
    ) -> dict[str, Any]:
        """Apply a browser-captured AssemblyAI transcript through the same core.

        Voice capture remains upstream and probabilistic. Canonical mutation still
        happens only after the explicit human apply boundary on the web surface.
        """
        metadata = {
            "provider": "AssemblyAI",
            "transport": "streaming_v3",
            "session_id": assemblyai_session_id,
            "human_boundary": boundary,
            "client_captured_at": client_captured_at,
        }
        return self._amend_text(
            text,
            source="assemblyai_browser_voice_human_boundary",
            label="operator-surface-voice",
            source_metadata=metadata,
        )

    def evidence_receipt(self, runtime: dict[str, Any] | None = None) -> dict[str, Any]:
        """Return an immutable-style snapshot suitable for local proof capture."""
        with self._lock:
            return {
                "schema": "errata-browser-voice-receipt-v0.1",
                "generated_at": utc_now(),
                "truth_boundary": (
                    "LOCAL_BROWSER_PRODUCT_PROOF; not Cloudflare deployment, "
                    "agency integration, or external operator evidence"
                ),
                "runtime": deepcopy(runtime) if runtime else None,
                "state": self._state_view(),
                "validation": self._validation(),
                "history": deepcopy(self.history),
                "external_evidence": self._evidence_summary(),
            }

    def commit(self, reviewed_hash: str, *, confirmed: bool) -> dict[str, Any]:
        token = reviewed_hash.strip()
        with self._lock:
            before_hash = self.state.state_hash
            before_revision = self.state.revision

            if not confirmed:
                transaction = {
                    "source": "human_web_review",
                    "status": "REVIEW_REQUIRED",
                    "reason": "EXPLICIT_REVIEW_CONFIRMATION_REQUIRED",
                    "before_revision": before_revision,
                    "revision": self.state.revision,
                    "before_hash": before_hash,
                    "state_hash": self.state.state_hash,
                    "diff": [],
                    "observed_at": utc_now(),
                }
                self.latest_transaction = transaction
                self.history.append(deepcopy(transaction))
                return self.view()

            try:
                receipt = self.coordinator.human_commit(
                    token,
                    authority="human_web_review",
                )
                transaction = {
                    "source": "human_web_review",
                    "status": "COMMITTED",
                    "reason": None,
                    "before_revision": before_revision,
                    "revision": self.state.revision,
                    "before_hash": before_hash,
                    "state_hash": self.state.state_hash,
                    "diff": [],
                    "receipt": receipt,
                    "observed_at": utc_now(),
                }
            except StaleState as exc:
                transaction = {
                    "source": "human_web_review",
                    "status": "STALE_REVIEW",
                    "reason": str(exc),
                    "before_revision": before_revision,
                    "revision": self.state.revision,
                    "before_hash": before_hash,
                    "state_hash": self.state.state_hash,
                    "diff": [],
                    "observed_at": utc_now(),
                }
            except ReducerError as exc:
                transaction = {
                    "source": "human_web_review",
                    "status": "REJECTED",
                    "reason": str(exc),
                    "before_revision": before_revision,
                    "revision": self.state.revision,
                    "before_hash": before_hash,
                    "state_hash": self.state.state_hash,
                    "diff": [],
                    "observed_at": utc_now(),
                }

            self.latest_transaction = transaction
            self.history.append(deepcopy(transaction))
            return self.view()
