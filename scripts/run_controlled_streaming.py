from __future__ import annotations

import argparse
import asyncio
from datetime import datetime
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

from errata.gtfs import GTFSIndex
from errata.live.controlled_streaming import ControlledStreamingCapture
from errata.live.coordinator import LiveTransactionCoordinator
from errata.models import Operation, ServiceChange
from errata.reducer import Reducer


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


def parse_args():
    p = argparse.ArgumentParser(
        description="Run ERRATA with AssemblyAI Universal-3.5 Pro streaming and human-controlled turn boundaries."
    )
    p.add_argument("--gtfs", default=str(ROOT / "fixtures" / "gtfs_static"))
    p.add_argument("--service-date", default=datetime.now().strftime("%Y%m%d"))
    p.add_argument("--start-time", default="09:00:00")
    p.add_argument("--change-id", default="ERR-LIVE-001")
    p.add_argument(
        "--evidence-dir",
        default=str(
            ROOT
            / "evidence"
            / "controlled-streaming-v0.1"
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

    print("ERRATA CONTROLLED STREAMING PROTOTYPE KILLER")
    print("AssemblyAI Universal-3.5 Pro Realtime")
    print("Turn authority: ERRATA/human controlled; provider turns are accumulated")
    print(f"change_id={state.change_id} revision={state.revision}")
    print(f"initial_hash={state.state_hash}")
    print(f"evidence_dir={args.evidence_dir}")
    print("")
    print("Workflow:")
    print('  1) Speak: "Route 55 west, skip King Edward and Cumberland until 9:30."')
    print("  2) Press ENTER immediately when you finish speaking")
    print("  3) Wait for APPLIED rev=2")
    print('  4) Speak: "Wait, keep Cumberland. Make it 10."')
    print("  5) Press ENTER immediately when you finish speaking")
    print("  6) Type: snapshot")
    print("")
    print("Provider end-of-turn splits do NOT mutate canonical state.")
    print("Pressing ENTER is the explicit human transaction boundary.")

    await ControlledStreamingCapture(coord, args.evidence_dir).run()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        pass
