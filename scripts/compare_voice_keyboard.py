from __future__ import annotations

import argparse
from datetime import datetime
import json
from pathlib import Path


def parse_time(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def read_jsonl(path: Path) -> list[dict]:
    rows = []
    if not path.exists():
        return rows
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip():
            rows.append(json.loads(line))
    return rows


def parse_args():
    p = argparse.ArgumentParser(
        description="Compare instrumented ERRATA voice capture timing with direct keyboard entry."
    )
    p.add_argument("--voice-dir", required=True)
    p.add_argument("--keyboard-dir", required=True)
    return p.parse_args()


def main():
    args = parse_args()
    voice_dir = Path(args.voice_dir)
    keyboard_dir = Path(args.keyboard_dir)

    events = read_jsonl(voice_dir / "raw_streaming_events.jsonl")
    receipts = read_jsonl(voice_dir / "controlled_capture_receipts.jsonl")
    keyboard = json.loads((keyboard_dir / "keyboard_baseline.json").read_text(encoding="utf-8"))

    applies = [r for r in receipts if r.get("event") == "HUMAN_APPLY"]
    finalized = [r for r in receipts if r.get("event") == "CONTROLLED_CAPTURE_FINALIZED"]
    speech = [
        e for e in events
        if e.get("payload", {}).get("type") == "SpeechStarted" and e.get("observed_at")
    ]

    if len(applies) < 2 or len(finalized) < 2 or len(speech) < 2:
        raise SystemExit(
            "Voice evidence is not instrumented enough: need >=2 SpeechStarted, "
            ">=2 HUMAN_APPLY, and >=2 CONTROLLED_CAPTURE_FINALIZED records."
        )

    voice_rows = []
    previous_apply_time = None
    for idx, apply in enumerate(applies[:2]):
        apply_time = parse_time(apply["observed_at"])
        candidates = []
        for ev in speech:
            t = parse_time(ev["observed_at"])
            if t <= apply_time and (previous_apply_time is None or t > previous_apply_time):
                candidates.append(t)
        if not candidates:
            raise SystemExit(f"No SpeechStarted found for voice phase {idx + 1}")
        start = min(candidates)
        final = finalized[idx]
        final_time = parse_time(final["observed_at"])
        voice_rows.append(
            {
                "phase": "initial" if idx == 0 else "correction",
                "speech_to_apply_ms": (apply_time - start).total_seconds() * 1000.0,
                "speech_to_applied_ms": (final_time - start).total_seconds() * 1000.0,
                "operations": final.get("operations"),
                "revision": final.get("revision"),
                "state_hash": final.get("state_hash"),
            }
        )
        previous_apply_time = apply_time

    keyboard_rows = {
        row["label"]: row for row in keyboard.get("measurements", [])
    }

    comparison = {
        "voice_runtime_git_sha": (
            json.loads((voice_dir / "runtime_manifest.json").read_text(encoding="utf-8"))
            .get("runtime_git_sha")
            if (voice_dir / "runtime_manifest.json").exists()
            else None
        ),
        "keyboard_runtime_git_sha": keyboard.get("runtime_git_sha"),
        "phases": [],
    }

    for v in voice_rows:
        k = keyboard_rows.get(v["phase"])
        if not k:
            raise SystemExit(f"Missing keyboard measurement for {v['phase']}")
        comparison["phases"].append(
            {
                "phase": v["phase"],
                "voice_speech_to_apply_ms": round(v["speech_to_apply_ms"], 1),
                "voice_speech_to_applied_ms": round(v["speech_to_applied_ms"], 1),
                "keyboard_entry_ms": round(k["entry_elapsed_ms"], 1),
                "keyboard_total_ms": round(k["total_elapsed_ms"], 1),
                "voice_operations": v["operations"],
                "keyboard_operations": k["parsed_operations"],
                "voice_revision": v["revision"],
                "keyboard_revision": k["revision"],
                "semantic_operation_match": v["operations"] == k["parsed_operations"],
            }
        )

    out = voice_dir / "voice_vs_keyboard_comparison.json"
    out.write_text(json.dumps(comparison, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(comparison, indent=2))
    print(f"comparison={out}")


if __name__ == "__main__":
    main()
