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
from errata.live.tool_schema import TOOLS, SYSTEM_PROMPT


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
        voice: str = "anna",
        greeting: str | None = None,
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
        self._resume_next = False
        self._resume_attempted = False
        self._pending_rejections: list[dict[str, Any]] = []

    async def _send(self, ws, payload: dict[str, Any]) -> None:
        self.recorder.event("client_to_server", payload)
        await ws.send(json.dumps(payload))

    def _initial_network_keyterms(self) -> list[str]:
        terms: list[str] = []
        seen: set[str] = set()
        for route in self.coordinator.gtfs.routes:
            short = str(route.get("route_short_name", "")).strip()
            if not short:
                continue
            for term in (short, f"Route {short}"):
                key = term.lower()
                if key not in seen:
                    seen.add(key)
                    terms.append(term)
        for term in self.generic_keyterms:
            key = term.lower()
            if key not in seen:
                seen.add(key)
                terms.append(term)
        return terms[:100]

    async def _initial_config(self, ws) -> None:
        session_config = {
            "system_prompt": SYSTEM_PROMPT,
            "tools": TOOLS,
            "output": {"voice": self.voice},
            "input": {
                "keyterms": self._initial_network_keyterms(),
                "turn_detection": {
                    "interrupt_response": True,
                    "min_silence": 1600,
                    "max_silence": 6000,
                },
            },
        }
        if self.greeting:
            session_config["greeting"] = self.greeting
        await self._send(
            ws,
            {
                "type": "session.update",
                "session": session_config,
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
            self._pending_rejections.clear()
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
        if self._pending_rejections:
            results = results + self._pending_rejections
            self._pending_rejections = []
        if not results:
            return

        self.recorder.snapshot(self.coordinator, "reply-completed")
        for result in results:
            print(
                f"[errata] {result.get('status')} call={result.get('call_id')} "
                f"rev={result.get('revision', self.coordinator.state.revision)} "
                f"hash={result.get('state_hash', self.coordinator.state.state_hash)[:16]}...",
                flush=True,
            )
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
                print(f"\n[aai] session.ready id={self.session_id} voice={self.voice}", flush=True)
                print("[aai] microphone streaming enabled", flush=True)
                self.recorder.receipt(
                    {"event": "SESSION_READY", "session_id": self.session_id}
                )

            elif typ == "session.updated":
                print("[aai] session.updated", flush=True)

            elif typ == "input.speech.started":
                print("\n[aai] speech.started", flush=True)

            elif typ == "input.speech.stopped":
                print("[aai] speech.stopped", flush=True)

            elif typ == "transcript.user.delta":
                text = event.get("text", "")
                if text:
                    print(f"\r[aai] hearing: {text[:160]}", end="", flush=True)

            elif typ == "transcript.user":
                text = event.get("text", "")
                print(f"\n[aai] USER: {text}", flush=True)
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
                print(
                    f"[aai] TOOL CALL {event.get('name')} id={event.get('call_id')} "
                    f"args={json.dumps(event.get('arguments'), ensure_ascii=False)}",
                    flush=True,
                )
                try:
                    prepared = self.coordinator.prepare_tool_call(event)
                    print(
                        f"[errata] PREPARED call={prepared['call_id']} "
                        f"ops={prepared['operation_count']} rev={prepared['canonical_revision']} "
                        f"hash={prepared['expected_hash'][:16]}...",
                        flush=True,
                    )
                    self.recorder.receipt({"event": "TOOL_PREPARED", **prepared})
                except (PreparationError, ValueError, json.JSONDecodeError) as exc:
                    # Nothing mutates. The rejection is held until reply.done so the
                    # tool lifecycle obeys the same terminal-reply boundary.
                    rejection = {
                        "call_id": event.get("call_id"),
                        "status": "REJECTED",
                        "reason": str(exc),
                    }
                    self._pending_rejections.append(rejection)
                    print(
                        f"[errata] PREPARATION REJECTED call={event.get('call_id')}: {exc}",
                        flush=True,
                    )
                    self.recorder.receipt(
                        {
                            "event": "TOOL_PREPARATION_REJECTED",
                            **rejection,
                        }
                    )

            elif typ == "transcript.agent":
                text = event.get("text", "")
                interrupted = event.get("interrupted")
                print(f"[aai] AGENT: {text}" + (" [interrupted]" if interrupted else ""), flush=True)

            elif typ == "reply.audio":
                data = event.get("data")
                if data:
                    audio.play_b64(data)

            elif typ == "reply.done":
                print(f"[aai] reply.done status={event.get('status', 'completed')}", flush=True)
                await self._handle_reply_done(ws, event, audio)

            elif typ == "session.error":
                code = event.get("code")
                message = event.get("message")
                self.recorder.receipt(
                    {
                        "event": "SESSION_ERROR",
                        "code": code,
                        "message": message,
                    }
                )
                print(f"\n[aai] SESSION ERROR {code}: {message}", flush=True)
                raise RuntimeError(f"AssemblyAI session.error {code}: {message}")

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

                receiver = asyncio.create_task(self._receive(ws, audio, ready))
                ready_task = asyncio.create_task(ready.wait())
                done, pending = await asyncio.wait(
                    {receiver, ready_task},
                    timeout=10,
                    return_when=asyncio.FIRST_COMPLETED,
                )
                if not done:
                    receiver.cancel()
                    ready_task.cancel()
                    raise TimeoutError("AssemblyAI did not emit session.ready within 10 seconds")
                if receiver in done:
                    exc = receiver.exception()
                    if exc:
                        raise exc
                    raise RuntimeError("AssemblyAI connection closed before session.ready")
                ready_task.cancel()

                sender = asyncio.create_task(self._send_audio(ws, audio, ready))
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
                resume = self._resume_next
                self._resume_next = False
                try:
                    await self._connection(resume=resume)
                except asyncio.CancelledError:
                    raise
                except Exception as exc:
                    print(f"\n[aai] connection ended: {exc!r}", flush=True)
                    self.recorder.receipt(
                        {"event": "CONNECTION_ENDED", "reason": repr(exc)}
                    )
                    if self._stop.is_set():
                        break
                    if self.session_id and not self._resume_attempted:
                        self._resume_attempted = True
                        self._resume_next = True
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
                    if self._force_drop and self.session_id and not self._resume_attempted:
                        self._force_drop = False
                        self._resume_attempted = True
                        self._resume_next = True
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
