from __future__ import annotations

import argparse
from hashlib import sha256
import json
from pathlib import Path

from google.transit import gtfs_realtime_pb2


def file_sha256(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--evidence-dir", required=True, type=Path)
    args = parser.parse_args()

    evidence_dir = args.evidence_dir
    scenario = json.loads((evidence_dir / "scenario.json").read_text(encoding="utf-8"))
    pb_path = evidence_dir / "rt" / "TripUpdates.pb"

    feed = gtfs_realtime_pb2.FeedMessage()
    feed.ParseFromString(pb_path.read_bytes())
    if not feed.IsInitialized():
        raise SystemExit("official bindings parsed an uninitialized FeedMessage")

    entities = []
    skipped_stop_ids: set[str] = set()
    for entity in feed.entity:
        if not entity.HasField("trip_update"):
            continue
        update = entity.trip_update
        row = {
            "entity_id": entity.id,
            "trip_id": update.trip.trip_id if update.trip.HasField("trip_id") else None,
            "route_id": update.trip.route_id if update.trip.HasField("route_id") else None,
            "direction_id": (
                update.trip.direction_id if update.trip.HasField("direction_id") else None
            ),
            "start_date": (
                update.trip.start_date if update.trip.HasField("start_date") else None
            ),
            "skipped_stops": [],
        }
        for stop in update.stop_time_update:
            if int(stop.schedule_relationship) == 1 and stop.stop_id:
                row["skipped_stops"].append(stop.stop_id)
                skipped_stop_ids.add(stop.stop_id)
        entities.append(row)

    expected_skip = scenario["skip_stop"]["stop_id"]
    expected_restored = scenario["restore_stop"]["stop_id"]
    expected_route = scenario["route_id"]
    expected_direction = scenario["direction_id"]
    expected_date = scenario["service_date"]

    checks = {
        "trip_updates_present": bool(entities),
        "expected_skip_observed": expected_skip in skipped_stop_ids,
        "restored_stop_not_skipped": expected_restored not in skipped_stop_ids,
        "route_matches": all(row["route_id"] == expected_route for row in entities),
        "direction_matches": all(row["direction_id"] == expected_direction for row in entities),
        "service_date_matches": all(row["start_date"] == expected_date for row in entities),
    }
    passed = all(checks.values())

    receipt = {
        "consumer": "MobilityData gtfs-realtime-bindings",
        "input": {
            "path": pb_path.as_posix(),
            "bytes": pb_path.stat().st_size,
            "sha256": file_sha256(pb_path),
        },
        "scenario": {
            "route_id": expected_route,
            "route_short_name": scenario["route_short_name"],
            "direction_id": expected_direction,
            "service_date": expected_date,
            "expected_skip_stop_id": expected_skip,
            "expected_restored_stop_id": expected_restored,
        },
        "decoded_trip_update_count": len(entities),
        "decoded_entities": entities,
        "skipped_stop_ids": sorted(skipped_stop_ids),
        "checks": checks,
        "pass": passed,
    }

    receipt_path = evidence_dir / "official_bindings_consumer.json"
    receipt_path.write_text(
        json.dumps(receipt, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    manifest_path = evidence_dir / "evidence_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    manifest.setdefault("truth_boundary", {})["official_bindings_consumer"] = (
        "PROVEN" if passed else "FAILED"
    )
    manifest["official_bindings_consumer"] = {
        "result_path": receipt_path.as_posix(),
        "result_sha256": file_sha256(receipt_path),
        "package": "gtfs-realtime-bindings",
        "checks": checks,
        "pass": passed,
    }
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    print(json.dumps(receipt, indent=2, sort_keys=True))
    if not passed:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
