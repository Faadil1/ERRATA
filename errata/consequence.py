from __future__ import annotations
from .gtfs import parse_gtfs_time


def compute(state, gtfs):
    route_id=state.route_ref.value
    direction=int(state.route_direction.value)
    start=parse_gtfs_time(state.start_time.value)
    end=parse_gtfs_time(state.end_time.value)
    service_date = state.service_date.value if state.service_date else None
    trips=gtfs.affected_trips(route_id,direction,start,end,service_date)
    skip_ids=sorted(state.skip_stops)
    skipped_stop_times=[]
    for trip_id in trips:
        seq=dict(gtfs.stop_sequence(trip_id))
        for stop_id in skip_ids:
            if stop_id in seq.values():
                stop_seq=next(k for k,v in seq.items() if v==stop_id)
                skipped_stop_times.append({"trip_id":trip_id,"stop_id":stop_id,"stop_sequence":stop_seq})
    return {
        "affected_trip_ids": trips,
        "affected_trip_count": len(trips),
        "skipped_stop_ids": skip_ids,
        "skipped_stop_time_count": len(skipped_stop_times),
        "skipped_stop_times": skipped_stop_times,
        "route_id": route_id,
        "direction_id": direction,
        "effective_window": [state.start_time.value,state.end_time.value],
    }
