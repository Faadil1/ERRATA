from __future__ import annotations
from dataclasses import dataclass, field, asdict
from enum import Enum
from hashlib import sha256
from typing import Any
import json


class ProvStatus(str, Enum):
    SPOKEN = "SPOKEN"
    RESOLVED = "RESOLVED"
    DERIVED = "DERIVED"
    DEFAULTED = "DEFAULTED"
    UNRESOLVED = "UNRESOLVED"


class ChangeStatus(str, Enum):
    STAGED = "STAGED"
    COMMITTED = "COMMITTED"


@dataclass(frozen=True)
class ProvenancedValue:
    value: Any
    status: ProvStatus
    op_ids: tuple[str, ...] = ()


@dataclass
class Operation:
    operation_id: str
    kind: str
    expected_hash: str
    payload: dict[str, Any]
    turn_id: str
    transcript_text: str
    source: str = "voice"
    supersedes: list[str] = field(default_factory=list)
    status: str = "ACTIVE"
    superseded_by: list[str] = field(default_factory=list)


@dataclass
class ArtifactRef:
    artifact_id: str
    kind: str
    generated_from_hash: str
    status: str = "READY"


@dataclass
class ServiceChange:
    change_id: str
    revision: int = 0
    route_ref: ProvenancedValue | None = None
    route_direction: ProvenancedValue | None = None
    service_date: ProvenancedValue | None = None
    start_time: ProvenancedValue | None = None
    end_time: ProvenancedValue | None = None
    skip_stops: dict[str, ProvenancedValue] = field(default_factory=dict)
    closed_segment: tuple[int, int] | None = None
    reason: ProvenancedValue | None = None
    unresolved_items: list[dict[str, Any]] = field(default_factory=list)
    artifacts: list[ArtifactRef] = field(default_factory=list)
    status: ChangeStatus = ChangeStatus.STAGED
    committed_hash: str | None = None

    def semantic_dict(self, include_revision: bool = True, include_artifacts: bool = True) -> dict[str, Any]:
        def pv(x):
            if x is None:
                return None
            return {"value": x.value, "status": x.status.value, "op_ids": list(x.op_ids)}
        d = {
            "change_id": self.change_id,
            "route_ref": pv(self.route_ref),
            "route_direction": pv(self.route_direction),
            "service_date": pv(self.service_date),
            "start_time": pv(self.start_time),
            "end_time": pv(self.end_time),
            "skip_stops": {k: pv(v) for k, v in sorted(self.skip_stops.items())},
            "closed_segment": list(self.closed_segment) if self.closed_segment else None,
            "reason": pv(self.reason),
            "unresolved_items": self.unresolved_items,
            "status": self.status.value,
        }
        if include_revision:
            d["revision"] = self.revision
        if include_artifacts:
            d["artifacts"] = [asdict(a) for a in self.artifacts]
        return d

    @property
    def state_hash(self) -> str:
        # Exclude artifact lifecycle and commit marker from canonical semantic hash.
        payload = self.semantic_dict(include_revision=True, include_artifacts=False)
        payload.pop("status", None)
        canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)
        return sha256(canonical.encode("utf-8")).hexdigest()

    def normalized_business_state(self) -> dict[str, Any]:
        """Compare voice and baseline semantic intent, excluding provenance/revision/hash."""
        def raw(x):
            return None if x is None else x.value
        return {
            "route_ref": raw(self.route_ref),
            "route_direction": raw(self.route_direction),
            "service_date": raw(self.service_date),
            "start_time": raw(self.start_time),
            "end_time": raw(self.end_time),
            "skip_stops": sorted(self.skip_stops),
            "closed_segment": self.closed_segment,
            "reason": raw(self.reason),
            "unresolved_items": self.unresolved_items,
        }
