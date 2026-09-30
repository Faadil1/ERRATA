from __future__ import annotations
from .protobuf_subset import FeedMessage


def serialize_trip_updates(state, impact, generated_at: int = 0) -> bytes:
    msg=FeedMessage(); msg.header.gtfs_realtime_version='2.0'; msg.header.incrementality=0
    if generated_at: msg.header.timestamp=generated_at
    skips_by_trip={}
    for row in impact['skipped_stop_times']:
        skips_by_trip.setdefault(row['trip_id'],[]).append(row)
    for trip_id, rows in sorted(skips_by_trip.items()):
        e=msg.entity.add(); e.id=f"errata:{state.change_id}:{state.revision}:{trip_id}"
        e.trip_update.trip.trip_id=trip_id
        e.trip_update.trip.schedule_relationship=0
        e.trip_update.trip.route_id=state.route_ref.value
        e.trip_update.trip.direction_id=int(state.route_direction.value)
        if generated_at:
            e.trip_update.timestamp=generated_at
        for row in sorted(rows,key=lambda r:r['stop_sequence']):
            s=e.trip_update.stop_time_update.add(); s.stop_sequence=row['stop_sequence']; s.stop_id=row['stop_id']; s.schedule_relationship=1
    return msg.SerializeToString(deterministic=True)
