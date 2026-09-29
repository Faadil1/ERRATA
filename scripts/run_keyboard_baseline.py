from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import platform
import subprocess
import sys
from time import perf_counter

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from errata.gtfs import GTFSIndex
from errata.live.coordinator import LiveTransactionCoordinator
from errata.live.direct_entry import apply_direct_text, result_dict
from errata.models import Operation, ServiceChange
from errata.reducer import Reducer


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def git(*args: str) -> str | None:
    try:
        return subprocess.check_output(
            ["git", *args], stderr=subprocess.DEVNULL, text=True
        ).strip()
    except Exception:
        return None


def seed_context(state, reducer, gtfs, service_date: str, start_time: str):
    expected = state.state_hash
    reducer.apply_batch(
        state,
        [
            Operation(
                operation_id="seed-service-date",
                kind="SET_SERVICE_DATE",
                expected_hash=expected,
                payload={"service_date": service_date},
                turn_id="system-context",
                transcript_text="CLI session context",
                source="system_default",
            ),
            Operation(
                operation_id="seed-start-time",
                kind="SET_TIME_WINDOW",
                expected_hash=expected,
                payload={"start_time": start_time},
                turn_id="system-context",
                transcript_text="CLI session context",
                source="system_default",
            ),
        ],
        gtfs,
    )


def timed_input(prompt: str) -> tuple[str, float]:
    started = perf_counter()
    text = input(prompt)
    elapsed_ms = (perf_counter() - started) * 1000.0
    return text.strip(), elapsed_ms


def parse_args():
    p = argparse.ArgumentParser(
        description="Measure direct keyboard entry for the same ERRATA semantic task used by the voice Prototype Killer."
    )
    p.add_argument("--gtfs", default=str(ROOT / "fixtures" / "gtfs_static"))
    p.add_argument("--service-date", default="20260929")
    p.add_argument("--start-time", default="09:00:00")
    p.add_argument("--change-id", default="ERR-KEYBOARD-001")
    p.add_argument(
        "--evidence-dir",
        default=str(
            ROOT
            / "evidence"
            / "keyboard-baseline-v0.1"
            / datetime.now().strftime("%Y%m%d-%H%M%S")
        ),
    )
    return p.parse_args()


def main():
    args = parse_args()
    root = Path(args.evidence_dir)
    root.mkdir(parents=True, exist_ok=True)

    gtfs = GTFSIndex(args.gtfs)
    state = ServiceChange(args.change_id)
    reducer = Reducer()
    seed_context(state, reducer, gtfs, args.service_date, args.start_time)
    coord = LiveTransactionCoordinator(state, reducer, gtfs)

    print("ERRATA KEYBOARD/DIRECT-ENTRY BASELINE")
    print("Use the same wording as the voice run. Timing begins when each prompt appears.")
    print("")
    print('Initial target: Route 55 west, skip King Edward and Cumberland until 9:30.')
    initial_text, initial_ms = timed_input("baseline-initial> ")
    initial = apply_direct_text(
        coord,
        label="initial",
        text=initial_text,
        entry_elapsed_ms=initial_ms,
        call_id="keyboard-initial",
    )
    print(
        f"[baseline] initial rev={initial.revision} "
        f"entry_ms={initial.entry_elapsed_ms:.1f} "
        f"processing_ms={initial.processing_elapsed_ms:.1f}"
    )

    print("")
    print('Correction target: Wait, keep Cumberland. Make it 10.')
    correction_text, correction_ms = timed_input("baseline-correction> ")
    correction = apply_direct_text(
        coord,
        label="correction",
        text=correction_text,
        entry_elapsed_ms=correction_ms,
        call_id="keyboard-correction",
    )
    print(
        f"[baseline] correction rev={correction.revision} "
        f"entry_ms={correction.entry_elapsed_ms:.1f} "
        f"processing_ms={correction.processing_elapsed_ms:.1f}"
    )

    payload = {
        "evidence_schema": "errata-keyboard-baseline-v0.1",
        "captured_at": utc_now(),
        "runtime_git_sha": git("rev-parse", "HEAD"),
        "git_branch": git("rev-parse", "--abbrev-ref", "HEAD"),
        "tracked_worktree_clean": git("status", "--porcelain", "--untracked-files=no") == "",
        "platform": platform.platform(),
        "python_version": sys.version,
        "scenario": {
            "service_date": args.service_date,
            "start_time": args.start_time,
        },
        "measurements": [result_dict(initial), result_dict(correction)],
        "final_state": coord.snapshot(),
    }
    path = root / "keyboard_baseline.json"
    path.write_text(json.dumps(payload, indent=2, sort_keys=True, default=str) + "\n", encoding="utf-8")
    print(f"[baseline] evidence={path}")
    print(json.dumps(coord.snapshot(), indent=2, default=str))


if __name__ == "__main__":
    main()
