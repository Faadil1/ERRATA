from __future__ import annotations

import argparse
import csv
from collections import Counter, defaultdict
from datetime import datetime
import hashlib
import io
import json
from pathlib import Path
import shutil
import urllib.request
import zipfile


REQUIRED = ("agency.txt", "routes.txt", "trips.txt", "stops.txt", "stop_times.txt")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def read_csv(zf: zipfile.ZipFile, name: str) -> list[dict[str, str]]:
    with zf.open(name) as raw:
        text = io.TextIOWrapper(raw, encoding="utf-8-sig", newline="")
        return list(csv.DictReader(text))


def active_services(
    service_date: str,
    calendar: list[dict[str, str]],
    calendar_dates: list[dict[str, str]],
) -> set[str]:
    date = datetime.strptime(service_date, "%Y%m%d")
    weekday = ["monday","tuesday","wednesday","thursday","friday","saturday","sunday"][date.weekday()]
    active: set[str] = set()
    for row in calendar:
        if row.get("start_date", "") <= service_date <= row.get("end_date", "") and row.get(weekday) == "1":
            active.add(row.get("service_id", ""))
    for row in calendar_dates:
        if row.get("date") != service_date:
            continue
        sid = row.get("service_id", "")
        if row.get("exception_type") == "1":
            active.add(sid)
        elif row.get("exception_type") == "2":
            active.discard(sid)
    return {x for x in active if x}


def gtfs_seconds(value: str) -> int | None:
    if not value:
        return None
    try:
        h, m, s = map(int, value.split(":"))
        return h * 3600 + m * 60 + s
    except Exception:
        return None


def clock(value: int) -> str:
    h = value // 3600
    m = (value % 3600) // 60
    return f"{h:02d}:{m:02d}:00"


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--url", default="https://contenu.sto.ca/GTFS/GTFS.zip")
    p.add_argument("--service-date", default="20260930")
    p.add_argument("--out-dir", type=Path, default=Path("evidence/public-network-v0.1"))
    args = p.parse_args()

    req = urllib.request.Request(
        args.url,
        headers={"User-Agent": "ERRATA-public-network-reality-check/0.1"},
    )
    with urllib.request.urlopen(req, timeout=60) as response:
        data = response.read()
        headers = dict(response.headers.items())

    args.out_dir.mkdir(parents=True, exist_ok=True)
    zip_path = args.out_dir / "source_gtfs.zip"
    zip_path.write_bytes(data)

    with zipfile.ZipFile(io.BytesIO(data)) as zf:
        names = set(zf.namelist())
        missing = [name for name in REQUIRED if name not in names]
        if missing:
            raise SystemExit(f"missing required GTFS files: {missing}")

        agency = read_csv(zf, "agency.txt")
        routes = read_csv(zf, "routes.txt")
        trips = read_csv(zf, "trips.txt")
        stops = read_csv(zf, "stops.txt")
        stop_times = read_csv(zf, "stop_times.txt")
        calendar = read_csv(zf, "calendar.txt") if "calendar.txt" in names else []
        calendar_dates = read_csv(zf, "calendar_dates.txt") if "calendar_dates.txt" in names else []

        extracted = args.out_dir / "gtfs"
        if extracted.exists():
            shutil.rmtree(extracted)
        extracted.mkdir()
        for name in sorted(names):
            if name.endswith("/") or "/" in name:
                continue
            if name.lower().endswith(".txt") or name.lower().endswith(".pdf"):
                (extracted / name).write_bytes(zf.read(name))

    active = active_services(args.service_date, calendar, calendar_dates)
    active_trips = [
        trip for trip in trips
        if not active or trip.get("service_id", "") in active
    ]

    stops_by_id = {row["stop_id"]: row for row in stops}
    routes_by_id = {row["route_id"]: row for row in routes}
    trip_by_id = {row["trip_id"]: row for row in active_trips}

    stop_times_by_trip: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in stop_times:
        if row.get("trip_id") in trip_by_id:
            stop_times_by_trip[row["trip_id"]].append(row)
    for rows in stop_times_by_trip.values():
        rows.sort(key=lambda row: int(row.get("stop_sequence") or 0))

    groups: dict[tuple[str, str], list[dict[str, str]]] = defaultdict(list)
    for trip in active_trips:
        direction = (trip.get("direction_id") or "").strip()
        if direction in {"0", "1"}:
            groups[(trip["route_id"], direction)].append(trip)

    candidates = []
    for (route_id, direction), group in groups.items():
        route = routes_by_id.get(route_id, {})
        short = (route.get("route_short_name") or "").strip()
        if not short:
            continue
        representative = max(
            group,
            key=lambda trip: len(stop_times_by_trip.get(trip["trip_id"], [])),
        )
        seq = stop_times_by_trip.get(representative["trip_id"], [])
        if len(seq) < 5:
            continue

        route_stop_names = [
            stops_by_id.get(row.get("stop_id",""), {}).get("stop_name","").strip()
            for trip in group[:50]
            for row in stop_times_by_trip.get(trip["trip_id"], [])
        ]
        counts = Counter(name.lower() for name in route_stop_names if name)

        internal = []
        for row in seq[1:-1]:
            stop = stops_by_id.get(row.get("stop_id",""), {})
            name = (stop.get("stop_name") or "").strip()
            if not name or counts[name.lower()] > max(3, len(group)):
                continue
            internal.append({
                "stop_id": row.get("stop_id"),
                "stop_name": name,
                "stop_sequence": int(row.get("stop_sequence") or 0),
            })
        if len(internal) < 2:
            internal = [
                {
                    "stop_id": row.get("stop_id"),
                    "stop_name": stops_by_id.get(row.get("stop_id",""), {}).get("stop_name","").strip(),
                    "stop_sequence": int(row.get("stop_sequence") or 0),
                }
                for row in seq[1:-1]
                if stops_by_id.get(row.get("stop_id",""), {}).get("stop_name","").strip()
            ]
        if len(internal) < 2:
            continue

        chosen = [internal[len(internal)//3], internal[(2*len(internal))//3]]
        first_times = []
        for trip in group:
            rows = stop_times_by_trip.get(trip["trip_id"], [])
            values = [
                gtfs_seconds(row.get("departure_time") or row.get("arrival_time") or "")
                for row in rows
            ]
            values = [v for v in values if v is not None]
            if values:
                first_times.append(min(values))
        first_times.sort()
        if not first_times:
            continue

        # Pick a window around a dense portion of trips, bounded to at least 30 min.
        mid = first_times[len(first_times)//2]
        start = max(0, mid - 15*60)
        end = mid + 45*60
        affected = sum(1 for value in first_times if start <= value < end)
        headsigns = Counter((trip.get("trip_headsign") or "").strip() for trip in group)
        candidates.append({
            "route_id": route_id,
            "route_short_name": short,
            "route_long_name": route.get("route_long_name"),
            "direction_id": int(direction),
            "trip_count_active": len(group),
            "representative_trip_id": representative["trip_id"],
            "representative_headsign": representative.get("trip_headsign"),
            "common_headsigns": headsigns.most_common(5),
            "stop_a": chosen[0],
            "stop_b": chosen[1],
            "window_start": clock(start),
            "window_end": clock(end),
            "affected_trip_count_estimate": affected,
        })

    def score(item):
        numeric = 1 if item["route_short_name"].isdigit() else 0
        west_hint = 1 if any(
            word in (item.get("representative_headsign") or "").lower()
            for word in ("ouest", "west")
        ) and item["direction_id"] == 1 else 0
        east_hint = 1 if any(
            word in (item.get("representative_headsign") or "").lower()
            for word in ("est", "east")
        ) and item["direction_id"] == 0 else 0
        return (west_hint + east_hint, numeric, item["affected_trip_count_estimate"], item["trip_count_active"])

    candidates.sort(key=score, reverse=True)
    selected = candidates[0] if candidates else None

    report = {
        "evidence_schema": "errata-public-network-discovery-v0.1",
        "source": {
            "provider": "Société de transport de l'Outaouais (STO)",
            "official_url": args.url,
            "downloaded_at_utc": datetime.utcnow().isoformat() + "Z",
            "sha256": sha256_bytes(data),
            "bytes": len(data),
            "http_last_modified": headers.get("Last-Modified"),
            "http_etag": headers.get("ETag"),
            "terms_url": "https://sto.ca/affaires/espace-developpeurs-donnees-ouvertes/conditions-dutilisation-donnees-ouvertes-et-cle-api-de-la-sto/",
            "required_attribution_template_fr": "Le présent service intègre les données ouvertes fournies par la Société de transport de l'Outaouais (STO). La STO n'est pas responsable de l'exactitude de l'information générée par cette application. Dernière mise à jour : AAAA-MM-JJ.",
        },
        "service_date": args.service_date,
        "agency": agency,
        "counts": {
            "routes": len(routes),
            "trips_total": len(trips),
            "trips_active_or_unfiltered": len(active_trips),
            "stops": len(stops),
            "active_services": len(active),
            "candidate_route_directions": len(candidates),
        },
        "selected_candidate": selected,
        "top_candidates": candidates[:10],
        "truth_boundary": "PUBLIC_NON_SYNTHETIC_GTFS_STATIC_DISCOVERY_ONLY",
    }
    (args.out_dir / "discovery.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True))

    if selected is None:
        raise SystemExit("no suitable public-network scenario candidate discovered")


if __name__ == "__main__":
    main()
