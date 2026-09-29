from __future__ import annotations

import argparse
import asyncio
from datetime import datetime
import os
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    # Direct script execution sets sys.path[0] to scripts/, not the repository root.
    # Add the repo root explicitly so `python scripts/run_live_assemblyai.py` works
    # without requiring an editable package install or PYTHONPATH mutation.
    sys.path.insert(0, str(ROOT))

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

from errata.gtfs import GTFSIndex
from errata.live.coordinator import LiveTransactionCoordinator
from errata.live.session import VoiceAgentSession
from errata.models import Operation, ServiceChange
from errata.reducer import Reducer


def seed_context(state, reducer, gtfs, service_date: str, start_time: str):
    expected = state.state_hash
    ops = [
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
    ]
    reducer.apply_batch(state, ops, gtfs)


def parse_args():
    p = argparse.ArgumentParser(
        description="Run ERRATA's credentialed microphone-driven AssemblyAI Prototype Killer."
    )
    p.add_argument("--gtfs", default=str(ROOT / "fixtures" / "gtfs_static"))
    p.add_argument("--service-date", default=datetime.now().strftime("%Y%m%d"))
    p.add_argument("--start-time", default="09:00:00")
    p.add_argument("--change-id", default="ERR-LIVE-001")
    p.add_argument("--voice", default="anna")
    p.add_argument(
        "--evidence-dir",
        default=str(
            ROOT
            / "evidence"
            / "live-assemblyai-v0.1"
            / datetime.now().strftime("%Y%m%d-%H%M%S")
        ),
    )
    return p.parse_args()


async def main():
    if load_dotenv:
        load_dotenv()

    args = parse_args()
    gtfs = GTFSIndex(args.gtfs)
    state = ServiceChange(args.change_id)
    reducer = Reducer()
    seed_context(state, reducer, gtfs, args.service_date, args.start_time)
    coord = LiveTransactionCoordinator(state, reducer, gtfs)

    print("ERRATA LIVE ASSEMBLYAI PROTOTYPE KILLER")
    print(f"change_id={state.change_id} revision={state.revision}")
    print(f"initial_hash={state.state_hash}")
    print(f"evidence_dir={args.evidence_dir}")
    print("")
    print("Canonical first task:")
    print('  "Route 55 west, skip King Edward and Cumberland until 9:30."')
    print('  Then interrupt/correct: "Wait — keep Cumberland. Make it 10."')
    print("")
    print("Evidence remains LIVE_CANDIDATE until receipts are audited.")
    print(f"voice={args.voice}")
    print("Waiting for [aai] session.ready before speaking...")

    session = VoiceAgentSession(
        coord,
        args.evidence_dir,
        api_key=os.environ.get("ASSEMBLYAI_API_KEY"),
        voice=args.voice,
    )
    await session.run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
