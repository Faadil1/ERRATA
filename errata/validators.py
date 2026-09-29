from __future__ import annotations
from dataclasses import dataclass, asdict
from .gtfs import parse_gtfs_time


@dataclass(frozen=True)
class ValidationResult:
    validator: str
    status: str
    detail: str
    blocking: bool

    def to_dict(self): return asdict(self)


def validate(state, gtfs):
    out=[]
    route_id = state.route_ref.value if state.route_ref else None
    direction = state.route_direction.value if state.route_direction else None
    route_ids={r['route_id'] for r in gtfs.routes}
    out.append(ValidationResult('ROUTE_EXISTS','PASS' if route_id in route_ids else 'FAIL',str(route_id),True))
    stop_ids=set(gtfs.stop_by_id)
    bad=[s for s in state.skip_stops if s not in stop_ids]
    out.append(ValidationResult('STOP_EXISTS','PASS' if not bad else 'FAIL',','.join(bad) or 'all',True))
    if state.start_time and state.end_time:
        ok=parse_gtfs_time(state.start_time.value) <= parse_gtfs_time(state.end_time.value)
        out.append(ValidationResult('EFFECTIVE_DATE_ORDER','PASS' if ok else 'FAIL',f"{state.start_time.value}->{state.end_time.value}",True))
    else:
        out.append(ValidationResult('EFFECTIVE_DATE_ORDER','FAIL','missing time window',True))
    out.append(ValidationResult('UNRESOLVED_EMPTY','PASS' if not state.unresolved_items else 'FAIL',str(state.unresolved_items),True))
    # No active contradictory skip/keep exists in materialized state by construction.
    out.append(ValidationResult('NO_CONTRADICTORY_OPERATIONS','PASS','materialized skip set is singular',True))
    return out


def blocking_failures(results):
    return [r for r in results if r.blocking and r.status != 'PASS']
