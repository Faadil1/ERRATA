from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
from pathlib import Path
import shutil
import subprocess
import zipfile


FIXED_ZIP_TIME = (2026, 9, 29, 12, 0, 0)

STOP_COORDS = {
    "S_RIDEAU": ("45.4253", "-75.6903"),
    "S_KING_EDWARD": ("45.4265", "-75.6850"),
    "S_CUMBERLAND": ("45.4280", "-75.6815"),
    "S_LAURIER": ("45.4219", "-75.6881"),
    "S_RIVERSIDE": ("45.3900", "-75.6770"),
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_sha() -> str | None:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], text=True, stderr=subprocess.DEVNULL
        ).strip()
    except Exception:
        return None


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def csv_bytes(fieldnames: list[str], rows: list[dict[str, object]]) -> bytes:
    buffer = io.StringIO(newline="")
    writer = csv.DictWriter(buffer, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader()
    for row in rows:
        writer.writerow({key: row.get(key, "") for key in fieldnames})
    return buffer.getvalue().encode("utf-8")


def write_zip_member(zf: zipfile.ZipFile, name: str, data: bytes) -> None:
    info = zipfile.ZipInfo(name, FIXED_ZIP_TIME)
    info.compress_type = zipfile.ZIP_DEFLATED
    info.external_attr = 0o644 << 16
    zf.writestr(info, data)


def build_validator_gtfs(source: Path, target_zip: Path) -> None:
    routes = read_rows(source / "routes.txt")
    trips = read_rows(source / "trips.txt")
    stops = read_rows(source / "stops.txt")
    stop_times = read_rows(source / "stop_times.txt")

    validator_routes = [
        {
            "route_id": row["route_id"],
            "agency_id": "ERRATA",
            "route_short_name": row["route_short_name"],
            "route_long_name": row["route_long_name"],
            "route_type": "3",
        }
        for row in routes
    ]
    validator_stops = []
    for index, row in enumerate(stops):
        lat, lon = STOP_COORDS.get(
            row["stop_id"],
            (f"45.{4000 + index:04d}", f"-75.{6800 + index:04d}"),
        )
        validator_stops.append(
            {
                "stop_id": row["stop_id"],
                "stop_name": row["stop_name"],
                "stop_lat": lat,
                "stop_lon": lon,
            }
        )

    files = {
        "agency.txt": csv_bytes(
            ["agency_id", "agency_name", "agency_url", "agency_timezone"],
            [
                {
                    "agency_id": "ERRATA",
                    "agency_name": "ERRATA Synthetic Transit",
                    "agency_url": "https://example.com/",
                    "agency_timezone": "America/Toronto",
                }
            ],
        ),
        "calendar.txt": csv_bytes(
            [
                "service_id",
                "monday",
                "tuesday",
                "wednesday",
                "thursday",
                "friday",
                "saturday",
                "sunday",
                "start_date",
                "end_date",
            ],
            [
                {
                    "service_id": "WKD",
                    "monday": "1",
                    "tuesday": "1",
                    "wednesday": "1",
                    "thursday": "1",
                    "friday": "1",
                    "saturday": "1",
                    "sunday": "1",
                    "start_date": "20260901",
                    "end_date": "20261031",
                }
            ],
        ),
        "routes.txt": csv_bytes(
            [
                "route_id",
                "agency_id",
                "route_short_name",
                "route_long_name",
                "route_type",
            ],
            validator_routes,
        ),
        "stops.txt": csv_bytes(
            ["stop_id", "stop_name", "stop_lat", "stop_lon"],
            validator_stops,
        ),
        "trips.txt": csv_bytes(
            ["route_id", "service_id", "trip_id", "direction_id"],
            trips,
        ),
        "stop_times.txt": csv_bytes(
            [
                "trip_id",
                "arrival_time",
                "departure_time",
                "stop_id",
                "stop_sequence",
            ],
            stop_times,
        ),
    }

    with zipfile.ZipFile(target_zip, "w") as zf:
        for name in sorted(files):
            write_zip_member(zf, name, files[name])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--gtfs-dir", type=Path, default=Path("fixtures/gtfs_static"))
    parser.add_argument("--pb", type=Path, default=Path("evidence/errata_rev2.pb"))
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path("evidence/external-acceptance-v0.1"),
    )
    args = parser.parse_args()

    if not args.gtfs_dir.is_dir():
        raise SystemExit(f"GTFS directory not found: {args.gtfs_dir}")
    if not args.pb.is_file():
        raise SystemExit(f"GTFS-Realtime protobuf not found: {args.pb}")

    out = args.out_dir
    rt_dir = out / "rt"
    rt_dir.mkdir(parents=True, exist_ok=True)

    gtfs_zip = out / "gtfs_static.zip"
    build_validator_gtfs(args.gtfs_dir, gtfs_zip)

    trip_updates = rt_dir / "TripUpdates.pb"
    shutil.copyfile(args.pb, trip_updates)

    manifest = {
        "evidence_schema": "errata-external-acceptance-v0.1",
        "runtime_git_sha": git_sha(),
        "fixture_scope": "SYNTHETIC_GTFS_PACKAGED_FOR_EXTERNAL_VALIDATION",
        "inputs": {
            "gtfs_static_zip": {
                "path": gtfs_zip.as_posix(),
                "bytes": gtfs_zip.stat().st_size,
                "sha256": sha256(gtfs_zip),
            },
            "trip_updates": {
                "path": trip_updates.as_posix(),
                "bytes": trip_updates.stat().st_size,
                "sha256": sha256(trip_updates),
            },
        },
        "truth_boundary": {
            "official_bindings_consumer": "PENDING",
            "canonical_gtfs_rt_validator": "NOT_YET_RUN",
        },
    }
    manifest_path = out / "evidence_manifest.json"
    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(manifest, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
