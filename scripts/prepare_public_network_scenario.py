from __future__ import annotations

import argparse
import csv
from datetime import datetime
import hashlib
import io
import json
from pathlib import Path
import re
import shutil
import zipfile


PREFERRED_ROUTES = ["7", "14", "11", "12", "15", "6", "85", "88", "25", "10"]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read_csv(zf: zipfile.ZipFile, name: str) -> list[dict[str, str]]:
    with zf.open(name) as raw:
        text = io.TextIOWrapper(raw, encoding="utf-8-sig", newline="")
        return list(csv.DictReader(text))


def gtfs_seconds(value: str) -> int:
    h, m, s = map(int, value.split(":"))
    return h * 3600 + m * 60 + s


def gtfs_time(seconds: int) -> str:
    h = seconds // 3600
    m = (seconds % 3600) // 60
    s = seconds % 60
    return f"{h:02d}:{m:02d}:{s:02d}"


def speech_time(seconds: int) -> str:
    h = seconds // 3600
    m = (seconds % 3600) // 60
    return f"{h}:{m:02d}"


def active_services(
    calendar: list[dict[str, str]],
    calendar_dates: list[dict[str, str]],
    service_date: str,
) -> set[str]:
    date = datetime.strptime(service_date, "%Y%m%d")
    weekday = [
        "monday", "tuesday", "wednesday", "thursday",
        "friday", "saturday", "sunday",
    ][date.weekday()]

    active: set[str] = set()
    for row in calendar:
        if row.get("start_date", "") <= service_date <= row.get("end_date", ""):
            if row.get(weekday) == "1":
                active.add(row["service_id"])

    for row in calendar_dates:
        if row.get("date") != service_date:
            continue
        if row.get("exception_type") == "1":
            active.add(row["service_id"])
        elif row.get("exception_type") == "2":
            active.discard(row["service_id"])
    return active


def normalize_name(value: str) -> str:
    return " ".join(re.sub(r"[^a-z0-9]+", " ", value.lower()).split())


def write_csv(path: Path, fieldnames: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in fieldnames})


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--zip", required=True, type=Path)
    parser.add_argument("--out-dir", required=True, type=Path)
    parser.add_argument("--service-date", required=True)
    parser.add_argument("--source-url", required=True)
    args = parser.parse_args()

    args.out_dir.mkdir(parents=True, exist_ok=True)
    subset_dir = args.out_dir / "gtfs_subset"
    subset_dir.mkdir(parents=True, exist_ok=True)

    with zipfile.ZipFile(args.zip) as zf:
        names = set(zf.namelist())
        required = {"routes.txt", "trips.txt", "stops.txt", "stop_times.txt"}
        missing = sorted(required - names)
        if missing:
            raise SystemExit(f"missing required GTFS files: {missing}")

        routes = read_csv(zf, "routes.txt")
        trips = read_csv(zf, "trips.txt")
        stops = read_csv(zf, "stops.txt")
        stop_times = read_csv(zf, "stop_times.txt")
        calendar = read_csv(zf, "calendar.txt") if "calendar.txt" in names else []
        calendar_dates = read_csv(zf, "calendar_dates.txt") if "calendar_dates.txt" in names else []
        feed_info = read_csv(zf, "feed_info.txt") if "feed_info.txt" in names else []
        agency = read_csv(zf, "agency.txt") if "agency.txt" in names else []

    active_service_ids = active_services(calendar, calendar_dates, args.service_date)
    if not active_service_ids:
        raise SystemExit(f"no active service IDs found for {args.service_date}")

    active_trips = [
        row for row in trips
        if row.get("service_id") in active_service_ids
        and (row.get("direction_id") or "").strip() in {"0", "1"}
    ]
    if not active_trips:
        raise SystemExit("no active trips with direction_id 0/1")

    stop_times_by_trip: dict[str, list[dict[str, str]]] = {}
    for row in stop_times:
        stop_times_by_trip.setdefault(row["trip_id"], []).append(row)
    for rows in stop_times_by_trip.values():
        rows.sort(key=lambda r: int(r.get("stop_sequence") or "0"))

    route_by_id = {r["route_id"]: r for r in routes}
    stop_by_id = {s["stop_id"]: s for s in stops}

    candidates: list[dict] = []
    route_directions: dict[tuple[str, int], list[dict[str, str]]] = {}
    for trip in active_trips:
        route_id = trip["route_id"]
        route = route_by_id.get(route_id)
        if not route:
            continue
        route_type = (route.get("route_type") or "").strip()
        short_name = (route.get("route_short_name") or "").strip()
        if route_type != "3" or not short_name:
            continue
        direction = int(trip["direction_id"])
        route_directions.setdefault((route_id, direction), []).append(trip)

    def preference(short_name: str) -> tuple[int, int, str]:
        try:
            idx = PREFERRED_ROUTES.index(short_name)
        except ValueError:
            idx = len(PREFERRED_ROUTES)
        try:
            numeric = int(short_name)
        except ValueError:
            numeric = 999999
        return (idx, numeric, short_name)

    for (route_id, direction), route_trips in route_directions.items():
        route = route_by_id[route_id]
        short_name = (route.get("route_short_name") or "").strip()
        usable = []
        for trip in route_trips:
            rows = stop_times_by_trip.get(trip["trip_id"], [])
            timed = [
                row for row in rows
                if row.get("departure_time") or row.get("arrival_time")
            ]
            if len(rows) < 6 or not timed:
                continue
            first_text = timed[0].get("departure_time") or timed[0].get("arrival_time")
            try:
                first_s = gtfs_seconds(first_text)
            except Exception:
                continue
            if first_s > 28 * 3600:
                continue
            usable.append((trip, rows, first_s))
        if len(usable) < 3:
            continue
        candidates.append({
            "route_id": route_id,
            "direction": direction,
            "route": route,
            "usable": usable,
            "preference": preference(short_name),
        })

    if not candidates:
        raise SystemExit("no suitable bus route/direction candidate found")

    candidates.sort(key=lambda c: (c["preference"], -len(c["usable"]), c["route_id"], c["direction"]))
    chosen = candidates[0]
    usable = chosen["usable"]

    target_s = 9 * 3600
    usable.sort(key=lambda item: (abs(item[2] - target_s), item[2], item[0]["trip_id"]))
    selected_trip, selected_rows, first_s = usable[0]

    route_stop_ids = {
        row["stop_id"]
        for trip, rows, _ in usable
        for row in rows
        if row.get("stop_id")
    }

    name_counts: dict[str, int] = {}
    for stop_id in route_stop_ids:
        stop = stop_by_id.get(stop_id)
        if not stop:
            continue
        key = normalize_name(stop.get("stop_name", ""))
        if key:
            name_counts[key] = name_counts.get(key, 0) + 1

    interior = []
    for row in selected_rows[1:-1]:
        stop = stop_by_id.get(row.get("stop_id", ""))
        if not stop:
            continue
        name = (stop.get("stop_name") or "").strip()
        key = normalize_name(name)
        if not key or name_counts.get(key) != 1:
            continue
        if len(name) > 70:
            continue
        interior.append((row, stop))

    if len(interior) < 2:
        raise SystemExit("selected trip does not have two uniquely named interior stops")

    mid = max(0, len(interior) // 2 - 1)
    stop_a_row, stop_a = interior[mid]
    stop_b_row, stop_b = interior[min(mid + 1, len(interior) - 1)]
    if stop_a["stop_id"] == stop_b["stop_id"]:
        raise SystemExit("failed to select two distinct stops")

    initial_end_s = first_s + 30 * 60
    corrected_end_s = first_s + 60 * 60
    if corrected_end_s > 29 * 3600 + 59 * 60:
        raise SystemExit("selected trip is too late for bounded parser time grammar")

    route_id = chosen["route_id"]
    direction = chosen["direction"]
    short_name = chosen["route"]["route_short_name"]
    selected_service_ids = {trip["service_id"] for trip, _, _ in usable}
    selected_trip_ids = {trip["trip_id"] for trip, _, _ in usable}

    subset_trips = [
        row for row in trips
        if row["trip_id"] in selected_trip_ids
    ]
    subset_stop_times = [
        row for row in stop_times
        if row["trip_id"] in selected_trip_ids
    ]
    subset_stop_ids = {row["stop_id"] for row in subset_stop_times}
    subset_stops = [row for row in stops if row["stop_id"] in subset_stop_ids]
    subset_routes = [row for row in routes if row["route_id"] == route_id]
    subset_calendar = [row for row in calendar if row.get("service_id") in selected_service_ids]
    subset_calendar_dates = [row for row in calendar_dates if row.get("service_id") in selected_service_ids]

    write_csv(subset_dir / "routes.txt", list(routes[0].keys()), subset_routes)
    write_csv(subset_dir / "trips.txt", list(trips[0].keys()), subset_trips)
    write_csv(subset_dir / "stops.txt", list(stops[0].keys()), subset_stops)
    write_csv(subset_dir / "stop_times.txt", list(stop_times[0].keys()), subset_stop_times)
    if calendar:
        write_csv(subset_dir / "calendar.txt", list(calendar[0].keys()), subset_calendar)
    if calendar_dates:
        write_csv(subset_dir / "calendar_dates.txt", list(calendar_dates[0].keys()), subset_calendar_dates)
    if agency:
        write_csv(subset_dir / "agency.txt", list(agency[0].keys()), agency)
    if feed_info:
        write_csv(subset_dir / "feed_info.txt", list(feed_info[0].keys()), feed_info)

    direction_word = "one" if direction == 1 else "zero"
    initial_text = (
        f"Route {short_name} direction {direction_word}, skip "
        f"{stop_a['stop_name']} and {stop_b['stop_name']} until {speech_time(initial_end_s)}."
    )
    correction_text = (
        f"Wait, keep {stop_b['stop_name']}. Make it {speech_time(corrected_end_s)}."
    )

    scenario = {
        "scenario_schema": "errata-public-network-v0.1",
        "provider": "OC Transpo",
        "source_url": args.source_url,
        "source_zip_sha256": sha256(args.zip),
        "service_date": args.service_date,
        "feed_info": feed_info[0] if feed_info else {},
        "route": {
            "route_id": route_id,
            "route_short_name": short_name,
            "route_long_name": chosen["route"].get("route_long_name"),
            "route_type": chosen["route"].get("route_type"),
        },
        "direction_id": direction,
        "representative_trip_id": selected_trip["trip_id"],
        "active_trip_count_in_subset": len(subset_trips),
        "start_time": gtfs_time(first_s),
        "initial_end_time": gtfs_time(initial_end_s),
        "corrected_end_time": gtfs_time(corrected_end_s),
        "skip_a": {
            "stop_id": stop_a["stop_id"],
            "stop_name": stop_a["stop_name"],
            "stop_sequence": int(stop_a_row["stop_sequence"]),
        },
        "skip_b_then_keep": {
            "stop_id": stop_b["stop_id"],
            "stop_name": stop_b["stop_name"],
            "stop_sequence": int(stop_b_row["stop_sequence"]),
        },
        "initial_text": initial_text,
        "correction_text": correction_text,
        "truth_boundary": "PUBLIC_GTFS_STATIC_SOURCE_NO_AGENCY_PRODUCTION_INTEGRATION",
    }

    (args.out_dir / "scenario.json").write_text(
        json.dumps(scenario, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    source_manifest = {
        "provider": "OC Transpo",
        "source_url": args.source_url,
        "downloaded_file": args.zip.name,
        "source_zip_bytes": args.zip.stat().st_size,
        "source_zip_sha256": sha256(args.zip),
        "feed_info": feed_info[0] if feed_info else {},
        "service_date_under_test": args.service_date,
        "truth_boundary": "PUBLIC_NON_SYNTHETIC_GTFS_STATIC",
    }
    (args.out_dir / "source_manifest.json").write_text(
        json.dumps(source_manifest, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    print(json.dumps(scenario, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
