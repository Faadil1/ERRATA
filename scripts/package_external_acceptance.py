from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import zipfile


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_sha() -> str | None:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], text=True, stderr=subprocess.DEVNULL
        ).strip()
    except Exception:
        return None


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
    with zipfile.ZipFile(gtfs_zip, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(args.gtfs_dir.rglob("*")):
            if path.is_file():
                zf.write(path, path.relative_to(args.gtfs_dir).as_posix())

    trip_updates = rt_dir / "TripUpdates.pb"
    shutil.copyfile(args.pb, trip_updates)

    manifest = {
        "evidence_schema": "errata-external-acceptance-v0.1",
        "runtime_git_sha": git_sha(),
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
