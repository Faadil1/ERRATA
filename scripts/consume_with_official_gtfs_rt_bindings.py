from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

from google.transit import gtfs_realtime_pb2


def decode_feed(path: Path) -> dict:
    data = path.read_bytes()
    feed = gtfs_realtime_pb2.FeedMessage()
    feed.ParseFromString(data)

    if not feed.IsInitialized():
        raise SystemExit("official bindings parsed an uninitialized FeedMessage")
    if not feed.header.gtfs_realtime_version:
        raise SystemExit("missing gtfs_realtime_version")

    entities = []
    skipped = []
    for entity in feed.entity:
        if not entity.HasField("trip_update"):
            continue
        update = entity.trip_update
        trip = update.trip
        stops = []
        for stop in update.stop_time_update:
            row = {
                "stop_sequence": stop.stop_sequence if stop.HasField("stop_sequence") else None,
                "stop_id": stop.stop_id if stop.HasField("stop_id") else None,
                "schedule_relationship": int(stop.schedule_relationship),
            }
            stops.append(row)
            if row["schedule_relationship"] == 1 and row["stop_id"]:
                skipped.append(row["stop_id"])
        entities.append(
            {
                "entity_id": entity.id,
                "trip_id": trip.trip_id if trip.HasField("trip_id") else None,
                "route_id": trip.route_id if trip.HasField("route_id") else None,
                "direction_id": trip.direction_id if trip.HasField("direction_id") else None,
                "stops": stops,
            }
        )

    if not entities:
        raise SystemExit("official bindings decoded no TripUpdate entities")

    return {
        "consumer": "MobilityData gtfs-realtime-bindings",
        "gtfs_realtime_version": feed.header.gtfs_realtime_version,
        "input_file": path.name,
        "input_sha256": hashlib.sha256(data).hexdigest(),
        "trip_update_entities": entities,
        "skipped_stop_ids": sorted(set(skipped)),
    }


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pb", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    parser.add_argument("--expect-skip", action="append", default=[])
    parser.add_argument("--expect-not-skip", action="append", default=[])
    args = parser.parse_args()

    result = decode_feed(args.pb)
    skipped = set(result["skipped_stop_ids"])

    missing = sorted(set(args.expect_skip) - skipped)
    forbidden = sorted(set(args.expect_not_skip) & skipped)
    result["assertions"] = {
        "expected_skips": args.expect_skip,
        "expected_not_skipped": args.expect_not_skip,
        "missing_expected_skips": missing,
        "unexpected_skips": forbidden,
        "pass": not missing and not forbidden,
    }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, sort_keys=True))

    if missing or forbidden:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
