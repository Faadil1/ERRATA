from __future__ import annotations
from copy import deepcopy
from dataclasses import dataclass
from typing import Iterable
from .models import ServiceChange, Operation, ProvenancedValue, ProvStatus, ArtifactRef


class ReducerError(Exception): pass
class StaleState(ReducerError): pass
class UnresolvedError(ReducerError): pass
class DomainConflict(ReducerError): pass


@dataclass
class ApplyResult:
    before_hash: str
    after_hash: str
    before_revision: int
    after_revision: int
    duplicate: bool = False


class Reducer:
    def __init__(self):
        self.applied_ids: set[str] = set()
        self.operations: list[Operation] = []

    def apply_batch(self, state: ServiceChange, ops: list[Operation], gtfs_index=None) -> ApplyResult:
        if not ops:
            return ApplyResult(state.state_hash, state.state_hash, state.revision, state.revision)
        expected = ops[0].expected_hash
        if expected != state.state_hash:
            raise StaleState(f"expected={expected} current={state.state_hash}")
        if any(op.expected_hash != expected for op in ops):
            raise StaleState("batch expected hashes differ")

        if all(op.operation_id in self.applied_ids for op in ops):
            return ApplyResult(state.state_hash, state.state_hash, state.revision, state.revision, duplicate=True)
        if any(op.operation_id in self.applied_ids for op in ops):
            raise ReducerError("mixed duplicate/new batch not allowed")

        before = deepcopy(state)
        before_hash = state.state_hash
        before_revision = state.revision
        staged = deepcopy(state)
        op_by_id = {o.operation_id: o for o in self.operations}

        for op in ops:
            k, p = op.kind, op.payload
            pv = lambda val, status=ProvStatus.SPOKEN: ProvenancedValue(val, status, (op.operation_id,))
            if k == "SET_ROUTE": staged.route_ref = pv(p["route_id"], ProvStatus.RESOLVED)
            elif k == "SET_DIRECTION": staged.route_direction = pv(int(p["direction_id"]), ProvStatus.RESOLVED)
            elif k == "SET_TIME_WINDOW":
                if "start_time" in p: staged.start_time = pv(p["start_time"])
                if "end_time" in p: staged.end_time = pv(p["end_time"])
            elif k == "SET_SERVICE_DATE": staged.service_date = pv(p["service_date"])
            elif k == "SET_REASON": staged.reason = pv(p["reason"])
            elif k == "ADD_SKIP_STOP":
                stop_id = p["stop_id"]
                staged.skip_stops[stop_id] = pv(stop_id, ProvStatus.RESOLVED)
            elif k == "REMOVE_SKIP_STOP":
                stop_id = p["stop_id"]
                if stop_id not in staged.skip_stops:
                    raise DomainConflict(f"cannot keep {stop_id}; it is not currently skipped")
                if staged.closed_segment and gtfs_index:
                    seq = gtfs_index.stop_by_id[stop_id].stop_sequence
                    if seq is None:
                        raise DomainConflict(
                            "closed-segment validation requires trip-specific stop sequence"
                        )
                    lo, hi = staged.closed_segment
                    if lo <= seq <= hi:
                        raise DomainConflict(f"{stop_id} lies inside closed segment {staged.closed_segment}")
                old_pv = staged.skip_stops.pop(stop_id)
                op.supersedes.extend(old_pv.op_ids)
                for old_id in old_pv.op_ids:
                    old = op_by_id.get(old_id)
                    if old:
                        old.status = "SUPERSEDED"
                        old.superseded_by.append(op.operation_id)
            elif k == "SET_CLOSED_SEGMENT": staged.closed_segment = (int(p["from_sequence"]), int(p["to_sequence"]))
            elif k == "CLEAR_UNRESOLVED": staged.unresolved_items = []
            else:
                raise ReducerError(f"unknown op kind {k}")

        staged.revision += 1
        # Any previous artifacts tied to old canonical state become stale.
        for art in staged.artifacts:
            if art.generated_from_hash != staged.state_hash:
                art.status = "STALE"

        # minimal-correction invariant will be asserted in tests by comparing allowed fields.
        state.__dict__.clear(); state.__dict__.update(deepcopy(staged.__dict__))
        self.operations.extend(ops)
        self.applied_ids.update(o.operation_id for o in ops)
        return ApplyResult(before_hash, state.state_hash, before_revision, state.revision)

    def attach_artifact(self, state: ServiceChange, artifact_id: str, kind: str):
        state.artifacts.append(ArtifactRef(artifact_id, kind, state.state_hash, "READY"))
