from __future__ import annotations

import asyncio
from datetime import datetime, timezone
import hashlib
from importlib.metadata import PackageNotFoundError, version
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
from urllib.parse import urlencode

import websockets

from errata.evidence import append_jsonl, write_json
from errata.live.controlled_parser import parse_operational_transcript
from errata.live.coordinator import LiveTransactionCoordinator, PreparationError


SAMPLE_RATE = 16000
BLOCK_FRAMES = 800
STREAM_BASE = "wss://streaming.assemblyai.com/v3/ws"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def package_version(name: str) -> str | None:
    try:
        return version(name)
    except PackageNotFoundError:
        return None


class ControlledStreamingCapture:
    def __init__(self, coordinator: LiveTransactionCoordinator, evidence_dir: str | Path):
        self.coordinator = coordinator
        self.api_key = os.environ.get("ASSEMBLYAI_API_KEY")
        if not self.api_key:
            raise RuntimeError("ASSEMBLYAI_API_KEY is required")
        self.root = Path(evidence_dir)
        self.root.mkdir(parents=True, exist_ok=True)
        self.events = self.root / "raw_streaming_events.jsonl"
        self.receipts = self.root / "controlled_capture_receipts.jsonl"
        self.fragments: list[str] = []
        self.turn_count = 0
        self._stop = asyncio.Event()
        self._ws = None
        self._audio_queue: asyncio.Queue[bytes] | None = None
        self._loop = None
        self.stream_session_id: str | None = None
        self.started_at = utc_now()
        self._write_runtime_manifest()
        write_json(self.root / "state-rev-001-start.json", self.coordinator.snapshot())

    def _git(self, *args: str) -> str | None:
        try:
            return subprocess.check_output(
                ["git", *args],
                stderr=subprocess.DEVNULL,
                text=True,
            ).strip()
        except Exception:
            return None

    def _write_runtime_manifest(self) -> None:
        tracked_diff = self._git("status", "--porcelain", "--untracked-files=no")
        write_json(
            self.root / "runtime_manifest.json",
            {
                "evidence_schema": "errata-controlled-streaming-v0.2",
                "started_at": self.started_at,
                "runtime_git_sha": self._git("rev-parse", "HEAD"),
                "git_branch": self._git("rev-parse", "--abbrev-ref", "HEAD"),
                "tracked_worktree_clean": tracked_diff == "" if tracked_diff is not None else None,
                "python_version": sys.version,
                "platform": platform.platform(),
                "packages": {
                    "websockets": package_version("websockets"),
                    "sounddevice": package_version("sounddevice"),
                    "protobuf": package_version("protobuf"),
                },
                "streaming_config": {
                    "endpoint": STREAM_BASE,
                    "sample_rate": SAMPLE_RATE,
                    "speech_model": "universal-3-5-pro",
                    "mode": "max_accuracy",
                    "voice_focus": "near-field",
                },
                "audio_persistence": "NOT_RECORDED",
                "api_key_persistence": "NOT_RECORDED",
            },
        )

    def _write_integrity_manifest(self) -> None:
        files = {}
        for path in sorted(self.root.iterdir()):
            if not path.is_file() or path.name == "evidence_manifest.json":
                continue
            data = path.read_bytes()
            files[path.name] = {
                "bytes": len(data),
                "sha256": hashlib.sha256(data).hexdigest(),
            }
        write_json(
            self.root / "evidence_manifest.json",
            {
                "generated_at": utc_now(),
                "runtime_git_sha": self._git("rev-parse", "HEAD"),
                "stream_session_id": self.stream_session_id,
                "files": files,
            },
        )

    def _log(self, path: Path, payload: dict) -> None:
        append_jsonl(path, {"observed_at": utc_now(), **payload})

    def _keyterms(self) -> list[str]:
        terms = []
        seen = set()
        for route in self.coordinator.gtfs.routes:
            short = str(route.get("route_short_name", "")).strip()
            if short:
                for term in (short, f"Route {short}"):
                    if term.lower() not in seen:
                        seen.add(term.lower())
                        terms.append(term)
        for stop in self.coordinator.gtfs.stop_by_id.values():
            if stop.stop_name.lower() not in seen:
                seen.add(stop.stop_name.lower())
                terms.append(stop.stop_name)
        for term in ("west", "westbound", "east", "eastbound", "skip", "keep", "Cumberland", "King Edward"):
            if term.lower() not in seen:
                seen.add(term.lower())
                terms.append(term)
        return terms[:100]

    def _url(self) -> str:
        params = {
            "sample_rate": SAMPLE_RATE,
            "speech_model": "universal-3-5-pro",
            "mode": "max_accuracy",
            "voice_focus": "near-field",
            "keyterms_prompt": json.dumps(self._keyterms()),
            "prompt": (
                "Transit operations dictation. Expect route numbers, directions, "
                "stop names, skip or keep corrections, and service end times."
            ),
        }
        return STREAM_BASE + "?" + urlencode(params)

    async def _send_audio(self):
        assert self._audio_queue is not None
        assert self._ws is not None
        while not self._stop.is_set():
            chunk = await self._audio_queue.get()
            await self._ws.send(chunk)

    async def _receive(self):
        assert self._ws is not None
        async for raw in self._ws:
            event = json.loads(raw)
            self._log(self.events, {"direction": "server_to_client", "payload": event})
            typ = event.get("type")
            if typ == "Begin":
                self.stream_session_id = event.get("id")
                self._log(
                    self.receipts,
                    {
                        "event": "STREAM_BEGIN",
                        "stream_session_id": self.stream_session_id,
                        "configuration": event.get("configuration"),
                    },
                )
                print(f"[stt] Begin id={self.stream_session_id}", flush=True)
            elif typ == "SpeechStarted":
                print("\n[stt] speech.started", flush=True)
            elif typ == "Turn":
                transcript = " ".join(str(event.get("transcript", "")).split())
                if not transcript:
                    continue
                if event.get("end_of_turn"):
                    self.fragments.append(transcript)
                    self.turn_count += 1
                    print(
                        f"\n[stt] FINAL[{self.turn_count}] conf={event.get('end_of_turn_confidence')}: "
                        f"{transcript}",
                        flush=True,
                    )
                else:
                    print(f"\r[stt] partial: {transcript[:180]}", end="", flush=True)
            elif typ == "Termination":
                print("\n[stt] terminated", flush=True)
                return

    async def _force_and_apply(self):
        assert self._ws is not None
        before_count = self.turn_count
        self._log(
            self.receipts,
            {
                "event": "HUMAN_APPLY",
                "revision": self.coordinator.state.revision,
                "state_hash": self.coordinator.state.state_hash,
                "buffered_fragment_count": len(self.fragments),
            },
        )
        await self._ws.send(json.dumps({"type": "ForceEndpoint"}))
        self._log(
            self.events,
            {"direction": "client_to_server", "payload": {"type": "ForceEndpoint"}},
        )

        wait_started = asyncio.get_running_loop().time()
        deadline = wait_started + 1.5
        while self.turn_count == before_count and asyncio.get_running_loop().time() < deadline:
            await asyncio.sleep(0.05)
        waited_ms = (asyncio.get_running_loop().time() - wait_started) * 1000.0
        forced_final_observed = self.turn_count > before_count
        self._log(
            self.receipts,
            {
                "event": "FORCE_ENDPOINT_RESULT",
                "turn_count_before": before_count,
                "turn_count_after": self.turn_count,
                "forced_final_observed": forced_final_observed,
                "waited_ms": round(waited_ms, 1),
                "revision": self.coordinator.state.revision,
                "state_hash": self.coordinator.state.state_hash,
            },
        )

        transcript = " ".join(self.fragments).strip()
        self.fragments.clear()
        if not transcript:
            self._log(
                self.receipts,
                {
                    "event": "CONTROLLED_CAPTURE_NOOP",
                    "reason": "NO_TRANSCRIPT_BUFFERED",
                    "revision": self.coordinator.state.revision,
                    "state_hash": self.coordinator.state.state_hash,
                },
            )
            print("[errata] CONTROLLED CAPTURE NOOP: no transcript buffered", flush=True)
            return

        parsed = parse_operational_transcript(
            transcript, self.coordinator.gtfs, self.coordinator.state
        )
        print(f"[errata] CAPTURED: {parsed.transcript}", flush=True)
        print(f"[errata] PARSED OPS: {parsed.operations}", flush=True)

        if not parsed.operations:
            self._log(
                self.receipts,
                {
                    "event": "CONTROLLED_CAPTURE_REVIEW",
                    "transcript": parsed.transcript,
                    "reason": "NO_BOUNDED_OPERATIONS",
                    "revision": self.coordinator.state.revision,
                    "state_hash": self.coordinator.state.state_hash,
                },
            )
            print("[errata] REVIEW_REQUIRED: no bounded operations resolved", flush=True)
            return

        item_id = f"controlled-turn-{self.turn_count}"
        self.coordinator.bind_user_transcript(item_id, parsed.transcript)
        try:
            prepared = self.coordinator.prepare_tool_call(
                {
                    "type": "tool.call",
                    "call_id": item_id,
                    "name": "stage_transit_change",
                    "arguments": {"operations": parsed.operations},
                }
            )
        except PreparationError as exc:
            print(f"[errata] PREPARATION REJECTED: {exc}", flush=True)
            self._log(
                self.receipts,
                {
                    "event": "CONTROLLED_CAPTURE_REJECTED",
                    "transcript": parsed.transcript,
                    "operations": parsed.operations,
                    "reason": str(exc),
                    "revision": self.coordinator.state.revision,
                    "state_hash": self.coordinator.state.state_hash,
                },
            )
            return

        print(
            f"[errata] PREPARED ops={prepared['operation_count']} "
            f"rev={prepared['canonical_revision']} "
            f"hash={prepared['expected_hash'][:16]}...",
            flush=True,
        )
        self._log(
            self.receipts,
            {
                "event": "CONTROLLED_CAPTURE_PREPARED",
                "call_id": item_id,
                "transcript": parsed.transcript,
                "operations": parsed.operations,
                **prepared,
            },
        )
        results = self.coordinator.finalize_pending()
        for result in results:
            print(
                f"[errata] {result.get('status')} rev={result.get('revision', self.coordinator.state.revision)} "
                f"hash={result.get('state_hash', self.coordinator.state.state_hash)[:16]}...",
                flush=True,
            )
            self._log(
                self.receipts,
                {
                    "event": "CONTROLLED_CAPTURE_FINALIZED",
                    "transcript": parsed.transcript,
                    "operations": parsed.operations,
                    **result,
                },
            )
        write_json(
            self.root / f"state-rev-{self.coordinator.state.revision:03d}.json",
            self.coordinator.snapshot(),
        )

    async def _commands(self):
        print(
            "\nControlled commands: [ENTER=apply] [apply] [clear] [snapshot] [commit <hash-prefix>] [quit]\n"
            "Speak naturally, then press ENTER immediately when YOU are done speaking.\n"
            "ENTER is the human transaction boundary and will issue ForceEndpoint.\n"
        )
        while not self._stop.is_set():
            raw = await asyncio.to_thread(input, "errata-ptt> ")
            cmd = raw.strip()
            if cmd == "" or cmd == "apply":
                await self._force_and_apply()
            elif cmd == "clear":
                self.fragments.clear()
                self._log(
                    self.receipts,
                    {
                        "event": "HUMAN_CLEAR_BUFFER",
                        "revision": self.coordinator.state.revision,
                        "state_hash": self.coordinator.state.state_hash,
                    },
                )
                print("[errata] transcript buffer cleared")
            elif cmd == "snapshot":
                snapshot = self.coordinator.snapshot()
                print(json.dumps(snapshot, indent=2, default=str))
                write_json(
                    self.root
                    / f"state-rev-{self.coordinator.state.revision:03d}-manual.json",
                    snapshot,
                )
                self._log(
                    self.receipts,
                    {
                        "event": "HUMAN_SNAPSHOT",
                        "revision": self.coordinator.state.revision,
                        "state_hash": self.coordinator.state.state_hash,
                        "status": self.coordinator.state.status.value,
                    },
                )
            elif cmd.startswith("commit "):
                token = cmd.split(maxsplit=1)[1]
                try:
                    receipt = self.coordinator.human_commit(token)
                except Exception as exc:
                    refusal = {
                        "event": "HUMAN_COMMIT_REFUSED",
                        "reviewed_hash_prefix": token,
                        "current_state_hash": self.coordinator.state.state_hash,
                        "revision": self.coordinator.state.revision,
                        "reason": str(exc),
                    }
                    self._log(self.receipts, refusal)
                    print(f"COMMIT REFUSED: {exc}")
                else:
                    self._log(
                        self.receipts,
                        {
                            "event": "HUMAN_COMMIT_ACCEPTED",
                            **receipt,
                        },
                    )
                    write_json(
                        self.root
                        / f"state-rev-{self.coordinator.state.revision:03d}-committed.json",
                        self.coordinator.snapshot(),
                    )
                    print(json.dumps(receipt, indent=2))
            elif cmd == "quit":
                self._log(
                    self.receipts,
                    {
                        "event": "HUMAN_QUIT",
                        "revision": self.coordinator.state.revision,
                        "state_hash": self.coordinator.state.state_hash,
                        "status": self.coordinator.state.status.value,
                    },
                )
                write_json(self.root / "state-final.json", self.coordinator.snapshot())
                self._stop.set()
                if self._ws is not None:
                    try:
                        await self._ws.send(json.dumps({"type": "Terminate"}))
                        self._log(
                            self.events,
                            {
                                "direction": "client_to_server",
                                "payload": {"type": "Terminate"},
                            },
                        )
                    except Exception:
                        pass
                return
            elif cmd:
                print("Unknown command")

    async def run(self):
        try:
            import sounddevice as sd
        except (ImportError, OSError) as exc:
            raise RuntimeError(
                "sounddevice/PortAudio is required only for the microphone run; "
                "install PortAudio for your OS and requirements-live.txt"
            ) from exc

        self._loop = asyncio.get_running_loop()
        self._audio_queue = asyncio.Queue(maxsize=100)

        def on_audio(indata, frames, time_info, status):
            chunk = bytes(indata)

            def enqueue():
                if not self._audio_queue.full():
                    self._audio_queue.put_nowait(chunk)

            self._loop.call_soon_threadsafe(enqueue)

        headers = {"Authorization": self.api_key}
        try:
            async with websockets.connect(
                self._url(),
                additional_headers=headers,
                max_size=8 * 1024 * 1024,
            ) as ws:
                self._ws = ws
                with sd.RawInputStream(
                    samplerate=SAMPLE_RATE,
                    blocksize=BLOCK_FRAMES,
                    channels=1,
                    dtype="int16",
                    callback=on_audio,
                ):
                    sender = asyncio.create_task(self._send_audio())
                    receiver = asyncio.create_task(self._receive())
                    commands = asyncio.create_task(self._commands())
                    done, pending = await asyncio.wait(
                        {sender, receiver, commands},
                        return_when=asyncio.FIRST_COMPLETED,
                    )
                    self._stop.set()
                    for task in pending:
                        task.cancel()
                    for task in done:
                        if task is not commands:
                            exc = task.exception()
                            if exc:
                                raise exc
        finally:
            self._write_integrity_manifest()
