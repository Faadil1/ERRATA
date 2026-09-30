from __future__ import annotations

import argparse
import csv
from datetime import datetime, timezone
from hashlib import sha256
import json
from pathlib import Path
import re
import shutil
import sys
import time
from urllib.request import Request, urlopen
import zipfile

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from errata.consequence import compute
from errata.gtfs import GTFSIndex, parse_gtfs_time
from errata.live.coordinator import LiveTransactionCoordinator
from errata.live.direct_entry import apply_direct_text
from errata.models import Operation, ServiceChange
from errata.reducer import Reducer
from errata.serializer import serialize_trip_updates


DEFAULT_URL = "https://contenu.sto.ca/GTFS/GTFS.zip"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def file_sha256(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()


def download(url: str, target: Path) -> dict:
    target.parent.mkdir(parents=True, exist_ok=True)
    request = Request(
        url,
        headers={
            "User-Agent": "ERRATA-public-network-probe/0.1 (+https://github.com/Faadil1/ERRATA)",
            "Accept": "application/zip,*/*;q=0.8",
        },
    )
    with urlopen(request, timeout=60) as response:
        body = response.read()
        target.write_bytes(body)
        headers = dict(response.headers.items())
        final_url = response.geturl()

    return {
        "requested_url": url,
        "final_url": final_url,
        "downloaded_at": utc_now(),
        "http_headers": {
            key: headers.get(key)
            for key in ("Last-Modified", "ETag", "Content-Length", "Content-Type")
            if headers.get(key) is not None
        },
        "bytes": len(body),
        "sha256": sha256(body).hexdigest(),
    }


def extract_gtfs(archive: Path, target: Path) -> Path:
    if target.exists():
        shutil.rmtree(target)
    target.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(archive) as zf:
        zf.extractall(target)

    required = {"routes.txt", "trips.txt", "stops.txt", "stop_times.txt"}
    candidates = [target, *[p for p in target.rglob("*") if p.is_dir()]]
    for candidate in candidates:
        names = {p.name for p in candidate.iterdir() if p.is_file()}
        if required.issubset(names):
            return candidate
    raise SystemExit("downloaded ZIP does not contain a recognizable GTFS root")


def gtfs_clock(seconds: int) -> str:
    seconds %= 30 * 3600
    h, rem = divmod(seconds, 3600)
    m, _ = divmod(rem, 60)
    return f"{h:02d}:{m:02d}:00"


def spoken_clock(seconds: int) -> str:
    value = gtfs_clock(seconds)
    h, m, _ = value.split(":")
    return f"{int(h)}:{m}" if m != "00" else str(int(h))


def normalized_name(value: str) -> str:
    return " ".join(re.sub(r"[^a-z0-9]+", " ", value.lower()).split())


def first_departure(rows: list[dict[str, str]]) -> int | None:
    values = []
    for row in rows:
        raw = row.get("departure_time") or row.get("arrival_time")
        if not raw:
            continue
        try:
            values.append(parse_gtfs_time(raw))
        except Exception:
            continue
    return min(values) if values else None


def select_scenario(gtfs: GTFSIndex, service_date: str) -> dict:
    stop_times_by_trip: dict[str, list[dict[str, str]]] = {}
    for row in gtfs.stop_times:
        stop_times_by_trip.setdefault(row["trip_id"], []).append(row)
    for rows in stop_times_by_trip.values():
        rows.sort(key=lambda r: int(r.get("stop_sequence") or 0))

    routes = sorted(
        gtfs.routes,
        key=lambda r: (
            0 if (r.get("route_short_name") or "").isdigit() else 1,
            len(r.get("route_short_name") or ""),
            r.get("route_short_name") or "",
            r["route_id"],
        ),
    )

    for route in routes:
        short = (route.get("route_short_name") or "").strip()
        if not short or not re.fullmatch(r"[A-Za-z0-9]+", short):
            continue

        for direction in (0, 1):
            active = gtfs.active_trip_ids(route["route_id"], direction, service_date)
            if not active:
                continue

            departures = []
            for trip_id in active:
                dep = first_departure(stop_times_by_trip.get(trip_id, []))
                if dep is not None and 6 * 3600 <= dep <= 20 * 3600:
                    departures.append((dep, trip_id))
            departures.sort()
            if not departures:
                continue

            allowed_stop_ids = {
                row["stop_id"]
                for trip_id in active
                for row in stop_times_by_trip.get(trip_id, [])
                if row.get("stop_id") in gtfs.stop_by_id
            }
            name_to_ids: dict[str, set[str]] = {}
            for stop_id in allowed_stop_ids:
                stop = gtfs.stop_by_id[stop_id]
                name_to_ids.setdefault(normalized_name(stop.stop_name), set()).add(stop_id)

            for dep, trip_id in departures:
                rows = stop_times_by_trip.get(trip_id, [])
                if len(rows) < 5:
                    continue
                internal = rows[1:-1]
                usable = []
                for row in internal:
                    stop_id = row["stop_id"]
                    stop = gtfs.stop_by_id.get(stop_id)
                    if stop is None:
                        continue
                    norm = normalized_name(stop.stop_name)
                    if not norm or len(stop.stop_name) > 60:
                        continue
                    if len(name_to_ids.get(norm, set())) != 1:
                        continue
                    if stop_id not in [item["stop_id"] for item in usable]:
                        usable.append({"stop_id": stop_id, "stop_name": stop.stop_name})
                if len(usable) < 2:
                    continue

                stop_a = usable[max(0, len(usable) // 3 - 1)]
                stop_b = usable[min(len(usable) - 1, max(1, (2 * len(usable)) // 3))]
                if stop_a["stop_id"] == stop_b["stop_id"]:
                    continue

                start_s = dep
                initial_end_s = dep + 45 * 60
                corrected_end_s = dep + 75 * 60
                initial_affected = gtfs.affected_trips(
                    route["route_id"], direction, start_s, initial_end_s, service_date
                )
                corrected_affected = gtfs.affected_trips(
                    route["route_id"], direction, start_s, corrected_end_s, service_date
                )
                if not initial_affected or not corrected_affected:
                    continue

                initial_text = (
                    f"Route {short} direction {direction}, skip {stop_a['stop_name']} "
                    f"and {stop_b['stop_name']} until {spoken_clock(initial_end_s)}."
                )
                correction_text = (
                    f"Wait, keep {stop_b['stop_name']}. "
                    f"Make it {spoken_clock(corrected_end_s)}."
                )
                return {
                    "agency_scope": "STO_PUBLIC_GTFS_STATIC",
                    "service_date": service_date,
                    "route_id": route["route_id"],
                    "route_short_name": short,
                    "route_long_name": route.get("route_long_name"),
                    "direction_id": direction,
                    "reference_trip_id": trip_id,
                    "start_time": gtfs_clock(start_s),
                    "initial_end_time": gtfs_clock(initial_end_s),
                    "corrected_end_time": gtfs_clock(corrected_end_s),
                    "skip_stop": stop_a,
                    "restore_stop": stop_b,
                    "initial_affected_trip_ids": initial_affected,
                    "corrected_affected_trip_ids": corrected_affected,
                    "initial_text": initial_text,
                    "correction_text": correction_text,
                }

    raise SystemExit(
        f"no bounded public-network scenario could be selected for service_date={service_date}"
    )


def seed_context(state, reducer, gtfs, service_date: str, start_time: str) -> None:
    expected = state.state_hash
    reducer.apply_batch(
        state,
        [
            Operation(
                operation_id="public-seed-service-date",
                kind="SET_SERVICE_DATE",
                expected_hash=expected,
                payload={"service_date": service_date},
                turn_id="public-source-context",
                transcript_text="Public GTFS scenario context",
                source="public_gtfs_context",
            ),
            Operation(
                operation_id="public-seed-start-time",
                kind="SET_TIME_WINDOW",
                expected_hash=expected,
                payload={"start_time": start_time},
                turn_id="public-source-context",
                transcript_text="Public GTFS scenario context",
                source="public_gtfs_context",
            ),
        ],
        gtfs,
    )


def run_scenario(gtfs_root: Path, scenario: dict, evidence_dir: Path) -> dict:
    gtfs = GTFSIndex(gtfs_root)
    state = ServiceChange("ERR-PUBLIC-STO-001")
    reducer = Reducer()
    seed_context(
        state,
        reducer,
        gtfs,
        scenario["service_date"],
        scenario["start_time"],
    )
    coord = LiveTransactionCoordinator(state, reducer, gtfs)

    initial = apply_direct_text(
        coord,
        label="public-initial",
        text=scenario["initial_text"],
        entry_elapsed_ms=0.0,
        call_id="public-initial",
    )
    if not initial.result or initial.result[0].get("status") != "APPLIED":
        raise SystemExit(f"public initial amendment did not apply: {initial.result}")

    correction = apply_direct_text(
        coord,
        label="public-correction",
        text=scenario["correction_text"],
        entry_elapsed_ms=0.0,
        call_id="public-correction",
    )
    if not correction.result or correction.result[0].get("status") != "APPLIED":
        raise SystemExit(f"public correction did not apply: {correction.result}")

    skip_id = scenario["skip_stop"]["stop_id"]
    restore_id = scenario["restore_stop"]["stop_id"]
    if set(state.skip_stops) != {skip_id}:
        raise SystemExit(
            f"public final skip set mismatch: expected only {skip_id}, got {sorted(state.skip_stops)}"
        )
    if restore_id in state.skip_stops:
        raise SystemExit(f"restored stop {restore_id} still skipped")
    if not state.end_time or state.end_time.value != scenario["corrected_end_time"]:
        raise SystemExit(
            f"public final end mismatch: expected {scenario['corrected_end_time']}, "
            f"got {state.end_time.value if state.end_time else None}"
        )

    impact = compute(state, gtfs)
    if impact["affected_trip_count"] < 1:
        raise SystemExit("public corrected state affects zero scheduled trips")
    if impact["skipped_stop_time_count"] < 1:
        raise SystemExit("public corrected state produces zero skipped stop-times")

    evidence_dir.mkdir(parents=True, exist_ok=True)
    rt_dir = evidence_dir / "rt"
    rt_dir.mkdir(parents=True, exist_ok=True)
    generated_at = int(time.time())
    pb = serialize_trip_updates(state, impact, generated_at=generated_at)
    pb_path = rt_dir / "TripUpdates.pb"
    pb_path.write_bytes(pb)

    result = {
        "evidence_schema": "errata-public-network-v0.1",
        "truth_boundary": "PUBLIC_STO_GTFS_STATIC_INPUT_LOCAL_MUTATION_NOT_AGENCY_PUBLISHED",
        "change_id": state.change_id,
        "revision": state.revision,
        "state_hash": state.state_hash,
        "state": coord.snapshot(),
        "scenario": scenario,
        "initial_result": initial.result,
        "correction_result": correction.result,
        "impact": impact,
        "artifact": {
            "path": pb_path.as_posix(),
            "bytes": len(pb),
            "sha256": sha256(pb).hexdigest(),
            "generated_at": generated_at,
        },
    }
    (evidence_dir / "scenario_result.json").write_text(
        json.dumps(result, indent=2, sort_keys=True, default=str) + "\n",
        encoding="utf-8",
    )
    return result


def parse_args():
    parser = argparse.ArgumentParser(
        description="Download official STO public GTFS, select a bounded real-network scenario, and run the ERRATA shared-core amendment mechanism."
    )
    parser.add_argument("--url", default=DEFAULT_URL)
    parser.add_argument("--service-date", default="20260930")
    parser.add_argument(
        "--work-dir",
        type=Path,
        default=ROOT / ".public-network" / "sto-v0.1",
    )
    parser.add_argument(
        "--evidence-dir",
        type=Path,
        default=ROOT / "evidence" / "public-network-v0.1",
    )
    return parser.parse_args()


def main():
    args = parse_args()
    args.work_dir.mkdir(parents=True, exist_ok=True)
    args.evidence_dir.mkdir(parents=True, exist_ok=True)

    archive = args.work_dir / "STO-GTFS.zip"
    provenance = download(args.url, archive)
    provenance["provider"] = "Société de transport de l'Outaouais (STO)"
    provenance["source_type"] = "PUBLIC_GTFS_SCHEDULE"
    provenance["service_date_used"] = args.service_date
    provenance["terms_url"] = (
        "https://www.sto.ca/affaires/espace-developpeurs-donnees-ouvertes/"
    )

    extracted = extract_gtfs(archive, args.work_dir / "extracted")
    gtfs = GTFSIndex(extracted)
    scenario = select_scenario(gtfs, args.service_date)

    public_zip = args.evidence_dir / "STO-GTFS-source.zip"
    shutil.copyfile(archive, public_zip)
    provenance["evidence_copy"] = {
        "path": public_zip.as_posix(),
        "bytes": public_zip.stat().st_size,
        "sha256": file_sha256(public_zip),
    }

    (args.evidence_dir / "source_provenance.json").write_text(
        json.dumps(provenance, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    (args.evidence_dir / "scenario.json").write_text(
        json.dumps(scenario, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    result = run_scenario(extracted, scenario, args.evidence_dir)
    print(
        json.dumps(
            {
                "source": provenance,
                "scenario": scenario,
                "final": {
                    "revision": result["revision"],
                    "state_hash": result["state_hash"],
                    "impact": result["impact"],
                    "artifact": result["artifact"],
                },
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
