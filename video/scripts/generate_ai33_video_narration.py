from __future__ import annotations

import argparse
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TRACKS_PATH = ROOT / "video" / "narration.json"
SOURCE = ROOT / "scripts" / "run_operator_surface.py"


def load_operator_module():
    spec = importlib.util.spec_from_file_location("errata_operator_surface", SOURCE)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"Could not load {SOURCE}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def probe_seconds(path: Path) -> float | None:
    try:
        result = subprocess.run(
            [
                "ffprobe",
                "-v",
                "error",
                "-show_entries",
                "format=duration",
                "-of",
                "default=noprint_wrappers=1:nokey=1",
                str(path),
            ],
            capture_output=True,
            text=True,
            check=True,
            timeout=20,
        )
        return round(float(result.stdout.strip()), 3)
    except Exception:
        return None


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Generate ERRATA video narration with the proven AI33 Pro TTS route."
    )
    parser.add_argument(
        "--track",
        action="append",
        help="Track name from video/narration.json. Repeatable. Omit to generate all tracks.",
    )
    args = parser.parse_args()

    tracks = json.loads(TRACKS_PATH.read_text(encoding="utf-8"))
    requested = args.track or list(tracks.keys())

    missing = [name for name in requested if name not in tracks]
    if missing:
        raise SystemExit(f"Unknown narration track(s): {', '.join(missing)}")

    module = load_operator_module()
    api_key = module.get_server_secret("AI33_API_KEY")
    if not api_key:
        raise SystemExit(
            "AI33_API_KEY is not available in Process/User/.env. "
            "Do not paste it into chat; configure it locally first."
        )

    summary: dict[str, dict] = {}
    for name in requested:
        cfg = tracks[name]
        output = ROOT / cfg["output"]
        output.parent.mkdir(parents=True, exist_ok=True)

        audio, meta = module.synthesize_errata_guidance(
            cfg["text"],
            api_key=api_key,
        )
        output.write_bytes(audio)
        duration = probe_seconds(output)
        slot_seconds = cfg.get("slot_seconds")
        start_seconds = cfg.get("start_seconds")
        sync_status = "UNBOUNDED"
        overflow_seconds = None
        if slot_seconds is not None and duration is not None:
            overflow_seconds = round(duration - float(slot_seconds), 3)
            sync_status = "SYNC_OK" if overflow_seconds <= 0 else "OVERFLOW"

        summary[name] = {
            "path": str(output.relative_to(ROOT)).replace("\\", "/"),
            "start_seconds": start_seconds,
            "slot_seconds": slot_seconds,
            "duration_seconds": duration,
            "sync_status": sync_status,
            "overflow_seconds": overflow_seconds,
            "voice_id": meta.get("voice_id"),
            "voice_label": meta.get("voice_label"),
            "provider_route": meta.get("provider_route"),
            "generation_ms": meta.get("generation_ms"),
            "credit_cost": meta.get("credit_cost"),
            "cache_hit": meta.get("cache_hit"),
        }
        print(
            f"Generated {name}: {summary[name]['path']} "
            f"({duration or 'duration unknown'}s, {sync_status})"
        )
        if sync_status == "OVERFLOW":
            raise SystemExit(
                f"{name} is {overflow_seconds:.3f}s too long for its "
                f"{slot_seconds}s video slot. Shorten the copy and regenerate."
            )

    manifest_path = ROOT / "video" / "narration-manifest.json"
    existing = {}
    if manifest_path.exists():
        try:
            existing = json.loads(manifest_path.read_text(encoding="utf-8"))
        except Exception:
            existing = {}
    existing.update(summary)
    manifest_path.write_text(
        json.dumps(existing, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print("No secret value was printed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
