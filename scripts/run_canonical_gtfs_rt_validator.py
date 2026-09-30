from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--jar", required=True, type=Path)
    parser.add_argument("--gtfs", required=True, type=Path)
    parser.add_argument("--rt-dir", required=True, type=Path)
    parser.add_argument("--out-dir", required=True, type=Path)
    parser.add_argument("--validator-commit", required=True)
    args = parser.parse_args()

    args.out_dir.mkdir(parents=True, exist_ok=True)
    command = [
        "java",
        "-jar",
        str(args.jar),
        "-gtfs",
        str(args.gtfs.resolve()),
        "-gtfsRealtimePath",
        str(args.rt_dir.resolve()),
    ]

    completed = subprocess.run(
        command,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )

    (args.out_dir / "stdout.txt").write_text(completed.stdout, encoding="utf-8")
    (args.out_dir / "stderr.txt").write_text(completed.stderr, encoding="utf-8")
    (args.out_dir / "command.json").write_text(
        json.dumps(
            {
                "command": command,
                "exit_code": completed.returncode,
                "validator_repository": "MobilityData/gtfs-realtime-validator",
                "validator_commit": args.validator_commit,
                "validator_jar": args.jar.name,
                "validator_jar_sha256": sha256(args.jar),
                "gtfs_static_sha256": sha256(args.gtfs),
                "realtime_inputs": {
                    p.name: sha256(p)
                    for p in sorted(args.rt_dir.glob("*.pb"))
                },
            },
            indent=2,
            sort_keys=True,
        )
        + "\n",
        encoding="utf-8",
    )

    result_candidates = sorted(args.rt_dir.glob("*.results.json"))
    if not result_candidates:
        result_candidates = sorted(args.rt_dir.glob("*results*.json"))

    if result_candidates:
        source = result_candidates[0]
        destination = args.out_dir / "validation-results.json"
        shutil.copyfile(source, destination)
        try:
            payload = json.loads(destination.read_text(encoding="utf-8"))
        except Exception:
            payload = None

        severities: dict[str, int] = {}
        if isinstance(payload, list):
            for entry in payload:
                try:
                    severity = entry["errorMessage"]["validationRule"]["severity"]
                except Exception:
                    continue
                severities[severity] = severities.get(severity, 0) + 1

        summary = {
            "validator_executed": True,
            "process_exit_code": completed.returncode,
            "result_file": destination.as_posix(),
            "result_sha256": sha256(destination),
            "reported_rule_groups_by_severity": severities,
            "blocking_error_group_count": severities.get("ERROR", 0),
            "pass_no_reported_error_groups": severities.get("ERROR", 0) == 0,
        }
    else:
        summary = {
            "validator_executed": True,
            "process_exit_code": completed.returncode,
            "result_file": None,
            "reported_rule_groups_by_severity": {},
            "blocking_error_group_count": None,
            "pass_no_reported_error_groups": False,
        }

    (args.out_dir / "summary.json").write_text(
        json.dumps(summary, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    manifest_path = args.out_dir.parent / "evidence_manifest.json"
    if manifest_path.exists():
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        manifest.setdefault("truth_boundary", {})["canonical_gtfs_rt_validator"] = (
            "EXECUTED_PASS_NO_ERROR_GROUPS"
            if summary["pass_no_reported_error_groups"] and completed.returncode == 0
            else "EXECUTED_REVIEW_REQUIRED"
        )
        manifest["canonical_validator"] = {
            "repository": "MobilityData/gtfs-realtime-validator",
            "commit": args.validator_commit,
            "jar_sha256": sha256(args.jar),
            **summary,
        }
        manifest_path.write_text(
            json.dumps(manifest, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

    print(json.dumps(summary, indent=2, sort_keys=True))
    if completed.returncode != 0:
        print(completed.stderr, file=sys.stderr)
        raise SystemExit(completed.returncode)
    if not result_candidates:
        raise SystemExit("validator produced no JSON result file")
    if summary["blocking_error_group_count"]:
        raise SystemExit(3)


if __name__ == "__main__":
    main()
