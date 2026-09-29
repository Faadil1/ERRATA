from __future__ import annotations

import asyncio
import base64
from dataclasses import asdict
from datetime import datetime, timezone
import json
import os
from pathlib import Path
from typing import Any

import websockets

from errata.evidence import append_jsonl, write_json
from errata.live.audio import LiveAudio
from errata.live.coordinator import LiveTransactionCoordinator, PreparationError
from errata.live.tool_schema import PROPOSE_SERVICE_CHANGE_TOOL, SYSTEM_PROMPT


VOICE_AGENT_WS = "wss://agents.assemblyai.com/v1/ws"


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


class LiveEvidenceRecorder:
    def __init__(self, root: str | Path):
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.events = self.root / "raw_assemblyai_events.jsonl"
        self.receipts = self.root / "transaction_receipts.jsonl"
        self.states = self.root / "states"
        self.states.mkdir(exist_ok=True)

    def event(self, direction: str, payload: dict[str, Any]) -> None:
        append_jsonl(
            self.events,
            {
                "observed_at": utc_now(),
                "direction": direction,
                "payload": payload,
                "evidence_state": "LIVE_CANDIDATE",
            },
        )

    def receipt(self, payload: dict[str, Any]) -> None:
        append_jsonl(
            self.receipts,
            {
                "observed_at": utc_now(),
                **payload,
                "evidence_state": "LIVE_CANDIDATE",
            },
        )

    def snapshot(self, coordinator: LiveTransactionCoordinator, event: str) -> None:
        rev = coordinator.state.revision
        write_json(
            self.states / f"rev-{rev:03d}-{event}.json",
            coordinator.snapshot(),
        )


class VoiceAgentSession:
    def __init__(
        self,
        coordinator: LiveTransactionCoordinator,
        evidence_dir: str | Path,
        *,
        api_key: str | None = None,
        voice: str = "ivy",
        greeting: str = "ERRATA ready. State changes are staged, never live.",
        generic_keyterms: list[str] | None = None,
    ):
        self.coordinator = coordinator
        self.api_key = api_key or os.environ.get("ASSEMBLYAI_API_KEY")
        if not self.api_key:
            raise RuntimeError("ASSEMBLYAI_API_KEY is required for a LIVE run")
        self.voice = voice
        self.greeting = greeting
        self.recorder = LiveEvidenceRecorder(evidence_dir)
        self.generic_keyterms = generic_keyterms or [
            "GTFS",
            "King Edward",
            "Cumberland",
            "Rideau",
            "route",
            "westbound",
            "eastbound",
        ]
        self.session_id: str | None = None
        self._last_keyterms: tuple[str, ...] = ()
        self._stop = asyncio.Event()
        self._active_ws = None
        self._force_drop = False
        self._resumed_once = False

    async def _send(self, ws, payload: dict[str, Any]) -> None:
        self.recorder.event("client_to_server", payload)
        await ws.send(json.dumps(payload))

    async def _initial_config(self, ws) -> None:
        await self._send(
            ws,
            {
                "type": "session.update",
                "session": {
                    "system_prompt": SYSTEM_PROMPT,
                    "greeting": self.greeting,
                    "tools": [PROPOSE_SERVICE_CHANGE_TOOL],
                    "output": {"voice": self.voice},
                    "input": {
                        "keyterms": self.generic_keyterms[:100],
                        "turn_detection": {
                            "interrupt_response": True,
                            "min_silence": 650,
                            "max_silence": 3500,
                        },
                    },
                },
            },
        )

    async def _update_keyterms_if_needed(self, ws) -> None:
        route_terms = self.coordinator.route_keyterms(limit=95)
        if not route_terms:
            return
        merged = []
        seen = set()
        for term in route_terms + self.generic_keyterms:
            key = term.lower()
            if key in seen:
                continue
            seen.add(key)
            merged.append(term)
            if len(merged) >= 100:
                break
        frozen = tuple(merged)
        if frozen == self._last_keyterms:
            return
        await self._send(
            ws,
            {"type": "session.update", "session": {"input": {"keyterms": merged}}},
        )
        self._last_keyterms = frozen
        self.recorder.receipt(
            {
                "event": "DYNAMIC_KEYTERMS_UPDATED",
                "count": len(merged),
                "state_hash": self.coordinator.state.state_hash,
                "revision": self.coordinator.state.revision,
            }
        )

    async def _send_audio(self, ws, audio: LiveAudio, ready: asyncio.Event) -> None:
        await ready.wait()
        while not self._stop.is_set():
            chunk = await audio.queue.get()
            payload = {
                "type": "input.audio",
                "audio": base64.b64encode(chunk).decode("ascii"),
            }
            # Raw audio is deliberately not duplicated into the JSON event log.
            await ws.send(json.dumps(payload))

    async def _handle_reply_done(self, ws, event: dict[str, Any], audio: LiveAudio) -> None:
        status = event.get("status")
        if status == "interrupted":
            audio.flush_output()
            discarded = self.coordinator.discard_pending("ASSEMBLYAI_REPLY_INTERRUPTED")
            for item in discarded:
                self.recorder.receipt(
                    {
                        "event": "PENDING_DISCARDED",
                        **item,
                    }
                )
            self.recorder.snapshot(self.coordinator, "interrupted")
            return

        results = self.coordinator.finalize_pending()
        if not results:
            return

        self.recorder.snapshot(self.coordinator, "reply-completed")
        for result in results:
            self.recorder.receipt({"event": "TOOL_FINALIZED", **result})
            # Tool results are returned only after terminal reply state.
            await self._send(
                ws,
                {
                    "type": "tool.result",
                    "call_id": result["call_id"],
                    "result": json.dumps(result, sort_keys=True),
                },
            )
        if any(r.get("status") == "APPLIED" for r in results):
            await self._update_keyterms_if_needed(ws)

    async def _receive(self, ws, audio: LiveAudio, ready: asyncio.Event) -> None:
        async for raw in ws:
            event = json.loads(raw)
            self.recorder.event("server_to_client", event)
            typ = event.get("type")

            if typ == "session.ready":
                self.session_id = event.get("session_id")
                ready.set()
                self.recorder.receipt(
                    {"event": "SESSION_READY", "session_id": self.session_id}
                )

            elif typ == "transcript.user":
                text = event.get("text", "")
                item_id = event.get("item_id") or f"unbound-{utc_now()}"
                self.coordinator.bind_user_transcript(item_id, text)
                self.recorder.receipt(
                    {
                        "event": "USER_TRANSCRIPT_BOUND",
                        "item_id": item_id,
                        "text": text,
                    }
                )

            elif typ == "tool.call":
                try:
                    prepared = self.coordinator.prepare_tool_call(event)
                    self.recorder.receipt({"event": "TOOL_PREPARED", **prepared})
                except (PreparationError, ValueError, json.JSONDecodeError) as exc:
                    # Nothing mutates. We still wait for reply.done before returning a result.
                    self.recorder.receipt(
                        {
                            "event": "TOOL_PREPARATION_REJECTED",
                            "call_id": event.get("call_id"),
                            "reason": str(exc),
                        }
                    )
                    # Register a synthetic pending rejection only in the evidence log.
                    # No canonical operation is created.

            elif typ == "reply.audio":
                data = event.get("data")
                if data:
                    audio.play_b64(data)

            elif typ == "reply.done":
                await self._handle_reply_done(ws, event, audio)

            elif typ == "session.error":
                self.recorder.receipt(
                    {
                        "event": "SESSION_ERROR",
                        "code": event.get("code"),
                        "message": event.get("message"),
                    }
                )

    async def _command_loop(self) -> None:
        print(
            "\nCommands: [snapshot] [commit <hash-prefix>] [drop] [quit]\n"
            "Use headphones for a barge-in test. Nothing publishes to an agency.\n"
        )
        while not self._stop.is_set():
            line = await asyncio.to_thread(input, "errata> ")
            cmd = line.strip()
            if not cmd:
                continue
            if cmd == "quit":
                self._stop.set()
                if self._active_ws:
                    await self._active_ws.close()
                return
            if cmd == "snapshot":
                snap = self.coordinator.snapshot()
                print(json.dumps(snap, indent=2, default=str))
                continue
            if cmd == "drop":
                self._force_drop = True
                if self._active_ws:
                    await self._active_ws.close(code=1012, reason="ERRATA deliberate recovery test")
                continue
            if cmd.startswith("commit "):
                reviewed = cmd.split(maxsplit=1)[1]
                try:
                    receipt = self.coordinator.human_commit(reviewed)
                except Exception as exc:
                    print(f"COMMIT REFUSED: {exc}")
                    self.recorder.receipt(
                        {"event": "HUMAN_COMMIT_REFUSED", "reason": str(exc)}
                    )
                else:
                    print(
                        f"COMMITTED {receipt['change_id']} rev={receipt['revision']} "
                        f"hash={receipt['state_hash']}"
                    )
                    self.recorder.receipt({"event": "HUMAN_COMMIT_ACCEPTED", **receipt})
                    self.recorder.snapshot(self.coordinator, "committed")
                continue
            print("Unknown command")

    async def _connection(self, *, resume: bool) -> None:
        headers = {"Authorization": f"Bearer {self.api_key}"}
        ready = asyncio.Event()
        audio = LiveAudio.create()
        audio.start()
        try:
            async with websockets.connect(
                VOICE_AGENT_WS,
                additional_headers=headers,
                max_size=8 * 1024 * 1024,
            ) as ws:
                self._active_ws = ws
                if resume:
                    if not self.session_id:
                        raise RuntimeError("Cannot resume without session_id")
                    await self._send(
                        ws,
                        {"type": "session.resume", "session_id": self.session_id},
                    )
                    # A resumed session still needs a ready signal before audio.
                else:
                    await self._initial_config(ws)

                sender = asyncio.create_task(self._send_audio(ws, audio, ready))
                receiver = asyncio.create_task(self._receive(ws, audio, ready))
                stopper = asyncio.create_task(self._stop.wait())
                done, pending = await asyncio.wait(
                    {sender, receiver, stopper},
                    return_when=asyncio.FIRST_COMPLETED,
                )
                for task in pending:
                    task.cancel()
                for task in done:
                    if task is not stopper:
                        exc = task.exception()
                        if exc:
                            raise exc
        finally:
            audio.stop()
            self._active_ws = None

    async def run(self) -> None:
        self.recorder.receipt(
            {
                "event": "LIVE_RUN_STARTED",
                "initial_state_hash": self.coordinator.state.state_hash,
                "initial_revision": self.coordinator.state.revision,
            }
        )
        command_task = asyncio.create_task(self._command_loop())
        try:
            while not self._stop.is_set():
                resume = self._resumed_once is False and self.session_id is not None
                try:
                    await self._connection(resume=resume)
                except asyncio.CancelledError:
                    raise
                except Exception as exc:
                    self.recorder.receipt(
                        {"event": "CONNECTION_ENDED", "reason": repr(exc)}
                    )
                    if self._stop.is_set():
                        break
                    if self.session_id and not self._resumed_once:
                        self._resumed_once = True
                        self.recorder.receipt(
                            {
                                "event": "SESSION_RESUME_ATTEMPT",
                                "session_id": self.session_id,
                            }
                        )
                        await asyncio.sleep(0.25)
                        continue
                    raise
                else:
                    if self._stop.is_set():
                        break
                    if self._force_drop and self.session_id and not self._resumed_once:
                        self._force_drop = False
                        self._resumed_once = True
                        self.recorder.receipt(
                            {
                                "event": "SESSION_RESUME_ATTEMPT",
                                "session_id": self.session_id,
                            }
                        )
                        await asyncio.sleep(0.25)
                        continue
                    break
        finally:
            self._stop.set()
            command_task.cancel()
            self.recorder.receipt(
                {
                    "event": "LIVE_RUN_ENDED",
                    "final_state_hash": self.coordinator.state.state_hash,
                    "final_revision": self.coordinator.state.revision,
                }
            )
