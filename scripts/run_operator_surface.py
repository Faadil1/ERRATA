from __future__ import annotations

import argparse
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import uuid
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

try:
    from dotenv import load_dotenv
except ImportError:
    load_dotenv = None

from errata.operator_surface import OperatorSurfaceSession


ASSEMBLYAI_STREAMING_TOKEN_URL = (
    "https://streaming.assemblyai.com/v3/token?expires_in_seconds=60"
)
AI33_BASE_URL = os.environ.get("AI33_BASE_URL", "https://api.ai33.pro").rstrip("/")
AI33_ERRATA_VOICE_ID = os.environ.get(
    "AI33_ERRATA_VOICE_ID",
    "elevenlabs_yG30oCchdy9JCUsKqYfV",
)
AI33_ERRATA_VOICE_LABEL = os.environ.get(
    "AI33_ERRATA_VOICE_LABEL",
    "Zach / George V2",
)
AI33_ERRATA_SPEED = float(os.environ.get("AI33_ERRATA_SPEED", "0.98"))


def git_runtime_metadata() -> dict:
    def run_git(*args: str) -> str | None:
        try:
            completed = subprocess.run(
                ["git", *args],
                cwd=ROOT,
                capture_output=True,
                text=True,
                check=True,
                timeout=5,
            )
            return completed.stdout.strip()
        except Exception:
            return None

    sha = run_git("rev-parse", "HEAD")
    branch = run_git("rev-parse", "--abbrev-ref", "HEAD")
    status = run_git("status", "--porcelain")
    return {
        "git_sha": sha,
        "git_branch": branch,
        "tracked_worktree_clean": status == "" if status is not None else None,
        "surface": "local-python-http",
    }


def _multipart_form(fields: dict[str, str]) -> tuple[bytes, str]:
    boundary = f"----ERRATA{uuid.uuid4().hex}"
    chunks: list[bytes] = []
    for name, value in fields.items():
        chunks.append(f"--{boundary}\r\n".encode("utf-8"))
        chunks.append(
            (
                f'Content-Disposition: form-data; name="{name}"\r\n\r\n'
            ).encode("utf-8")
        )
        chunks.append(str(value).encode("utf-8"))
        chunks.append(b"\r\n")
    chunks.append(f"--{boundary}--\r\n".encode("utf-8"))
    return b"".join(chunks), boundary


def _ai33_json(
    path: str,
    *,
    api_key: str,
    method: str = "GET",
    data: bytes | None = None,
    content_type: str | None = None,
    timeout: int = 30,
) -> dict:
    headers = {"xi-api-key": api_key}
    if content_type:
        headers["Content-Type"] = content_type
    request = Request(
        f"{AI33_BASE_URL}{path}",
        data=data,
        headers=headers,
        method=method,
    )
    try:
        with urlopen(request, timeout=timeout) as response:
            raw = response.read()
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(
            f"AI33 {method} {path} failed with HTTP {exc.code}: {detail}"
        ) from exc
    except URLError as exc:
        raise RuntimeError(
            f"AI33 {method} {path} failed: {exc.reason}"
        ) from exc

    try:
        payload = json.loads(raw.decode("utf-8"))
    except Exception as exc:
        raise RuntimeError(
            f"AI33 {method} {path} returned non-JSON response"
        ) from exc

    if payload.get("success") is False:
        raise RuntimeError(
            str(
                payload.get("message")
                or payload.get("error")
                or "AI33 request reported success=false"
            )
        )
    return payload


def synthesize_errata_guidance(
    text: str,
    *,
    api_key: str | None,
    voice_id: str | None = None,
) -> tuple[bytes, dict]:
    """Generate ERRATA guidance through the user's proven AI33 v3 TTS route."""
    if not api_key:
        raise RuntimeError("AI33_API_KEY is not configured on the server")

    text = text.strip()
    if not text:
        raise ValueError("text is required")
    if len(text) > 1600:
        raise ValueError("guidance text is too long")

    selected_voice = (voice_id or AI33_ERRATA_VOICE_ID).strip()
    if not selected_voice:
        raise ValueError("AI33 voice_id is required")

    body, boundary = _multipart_form(
        {
            "text": text,
            "voice_id": selected_voice,
            "speed": str(AI33_ERRATA_SPEED),
            "with_transcript": "false",
            "file_name": "errata-guidance.mp3",
        }
    )
    created = _ai33_json(
        "/v3/text-to-speech",
        api_key=api_key,
        method="POST",
        data=body,
        content_type=f"multipart/form-data; boundary={boundary}",
        timeout=45,
    )
    task_id = created.get("task_id")
    if not task_id:
        raise RuntimeError("AI33 TTS returned no task_id")

    deadline = time.monotonic() + 90
    task: dict | None = None
    while time.monotonic() < deadline:
        task = _ai33_json(
            f"/v1/task/{task_id}",
            api_key=api_key,
            timeout=20,
        )
        status = str(task.get("status") or "").lower()
        if status == "done":
            break
        if status in {"failed", "error"}:
            raise RuntimeError(
                str(
                    task.get("error_message")
                    or task.get("message")
                    or f"AI33 TTS task {task_id} failed"
                )
            )
        time.sleep(1.5)
    else:
        raise RuntimeError(f"AI33 TTS task {task_id} timed out")

    metadata = task.get("metadata") or {}
    audio_url = (
        metadata.get("audio_url")
        or metadata.get("url")
        or metadata.get("output_url")
    )
    if not audio_url:
        raise RuntimeError("AI33 TTS completed without audio URL")

    try:
        with urlopen(str(audio_url), timeout=30) as response:
            audio = response.read()
    except HTTPError as exc:
        raise RuntimeError(
            f"AI33 audio download failed with HTTP {exc.code}"
        ) from exc
    except URLError as exc:
        raise RuntimeError(
            f"AI33 audio download failed: {exc.reason}"
        ) from exc

    if not audio:
        raise RuntimeError("AI33 audio response was empty")

    return audio, {
        "task_id": task_id,
        "voice_id": selected_voice,
        "voice_label": AI33_ERRATA_VOICE_LABEL,
        "speed": AI33_ERRATA_SPEED,
        "credit_cost": task.get("credit_cost"),
        "provider_route": "AI33 v3 TTS -> ElevenLabs",
    }


def voice_capabilities() -> dict:
    return {
        "assemblyai_streaming": {
            "available": bool(os.environ.get("ASSEMBLYAI_API_KEY")),
            "provider": "AssemblyAI",
        },
        "neural_tts": {
            "available": bool(os.environ.get("AI33_API_KEY")),
            "provider": "AI33 Pro",
            "api_version": "v3",
            "route": "AI33 v3 TTS -> ElevenLabs",
            "default_voice": AI33_ERRATA_VOICE_ID,
            "voices": [
                {
                    "id": AI33_ERRATA_VOICE_ID,
                    "label": AI33_ERRATA_VOICE_LABEL,
                }
            ],
            "speed": AI33_ERRATA_SPEED,
            "disclosure": "AI-generated voice",
        },
        "browser_tts_fallback": True,
        "echo_cooldown_ms": 750,
    }


def mint_assemblyai_streaming_token(api_key: str | None) -> dict:
    """Mint a short-lived browser token without exposing the API key."""
    if not api_key:
        raise RuntimeError("ASSEMBLYAI_API_KEY is not configured on the server")

    request = Request(
        ASSEMBLYAI_STREAMING_TOKEN_URL,
        headers={"Authorization": api_key},
        method="GET",
    )
    try:
        with urlopen(request, timeout=10) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(
            f"AssemblyAI token request failed with HTTP {exc.code}: {detail}"
        ) from exc
    except URLError as exc:
        raise RuntimeError(f"AssemblyAI token request failed: {exc.reason}") from exc

    token = payload.get("token")
    if not token:
        raise RuntimeError("AssemblyAI token response did not include a token")
    return {
        "token": token,
        "expires_in_seconds": 60,
        "transport": "assemblyai_streaming_v3",
    }


CONTENT_TYPES = {
    ".html": "text/html; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".js": "application/javascript; charset=utf-8",
    ".svg": "image/svg+xml",
    ".json": "application/json; charset=utf-8",
}


class OperatorHandler(BaseHTTPRequestHandler):
    session: OperatorSurfaceSession
    web_root: Path

    def log_message(self, fmt: str, *args) -> None:
        print(f"[surface] {self.address_string()} {fmt % args}")

    def _send_json(self, payload, status=HTTPStatus.OK) -> None:
        body = json.dumps(payload, indent=2, sort_keys=True, default=str).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _send_bytes(
        self,
        body: bytes,
        *,
        content_type: str,
        status=HTTPStatus.OK,
        extra_headers: dict[str, str] | None = None,
    ) -> None:
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        for key, value in (extra_headers or {}).items():
            self.send_header(key, value)
        self.end_headers()
        self.wfile.write(body)

    def _read_json(self) -> dict:
        try:
            size = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            size = 0
        if size <= 0:
            return {}
        raw = self.rfile.read(size)
        try:
            payload = json.loads(raw.decode("utf-8"))
        except Exception as exc:
            raise ValueError(f"invalid JSON: {exc}") from exc
        if not isinstance(payload, dict):
            raise ValueError("JSON object required")
        return payload

    def _serve_static(self, relative: str) -> None:
        if relative in ("", "/"):
            relative = "index.html"
        relative = relative.lstrip("/")
        target = (self.web_root / relative).resolve()
        root = self.web_root.resolve()
        if root not in target.parents and target != root:
            self.send_error(HTTPStatus.FORBIDDEN)
            return
        if not target.is_file():
            self.send_error(HTTPStatus.NOT_FOUND)
            return
        body = target.read_bytes()
        self.send_response(HTTPStatus.OK)
        self.send_header("Content-Type", CONTENT_TYPES.get(target.suffix, "application/octet-stream"))
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if path == "/api/change":
            self._send_json(self.session.view())
            return
        if path == "/api/evidence":
            self._send_json(self.session.view()["external_evidence"])
            return
        if path == "/api/session-receipt":
            self._send_json(
                self.session.evidence_receipt(runtime=git_runtime_metadata())
            )
            return
        if path == "/api/voice-capabilities":
            self._send_json(voice_capabilities())
            return
        if path == "/api/voice-token":
            try:
                self._send_json(
                    mint_assemblyai_streaming_token(
                        os.environ.get("ASSEMBLYAI_API_KEY")
                    )
                )
            except RuntimeError as exc:
                self._send_json(
                    {"error": "VOICE_TOKEN_UNAVAILABLE", "detail": str(exc)},
                    status=HTTPStatus.SERVICE_UNAVAILABLE,
                )
            return
        self._serve_static(path)

    def do_POST(self) -> None:
        path = urlparse(self.path).path
        try:
            payload = self._read_json()
            if path == "/api/tts/guidance":
                try:
                    audio, tts_meta = synthesize_errata_guidance(
                        str(payload.get("text", "")),
                        api_key=os.environ.get("AI33_API_KEY"),
                        voice_id=(
                            str(payload.get("voice_id"))
                            if payload.get("voice_id")
                            else None
                        ),
                    )
                    self._send_bytes(
                        audio,
                        content_type="audio/mpeg",
                        extra_headers={
                            "X-ERRATA-TTS-Provider": "AI33-Pro",
                            "X-ERRATA-TTS-Route": "AI33-v3-TTS-to-ElevenLabs",
                            "X-ERRATA-TTS-Voice": str(tts_meta["voice_id"]),
                            "X-ERRATA-TTS-Task": str(tts_meta["task_id"]),
                            "X-ERRATA-TTS-Disclosure": "AI-generated voice",
                        },
                    )
                except RuntimeError as exc:
                    self._send_json(
                        {"error": "AI33_TTS_UNAVAILABLE", "detail": str(exc)},
                        status=HTTPStatus.SERVICE_UNAVAILABLE,
                    )
                return
            if path == "/api/amend/direct":
                self._send_json(self.session.amend_direct(str(payload.get("text", ""))))
                return
            if path == "/api/preview/voice":
                self._send_json(
                    self.session.preview_voice(str(payload.get("text", "")))
                )
                return
            if path == "/api/amend/voice":
                self._send_json(
                    self.session.amend_voice(
                        str(payload.get("text", "")),
                        assemblyai_session_id=(
                            str(payload.get("assemblyai_session_id"))
                            if payload.get("assemblyai_session_id")
                            else None
                        ),
                        boundary=str(payload.get("boundary") or "ForceEndpoint"),
                        client_captured_at=(
                            str(payload.get("client_captured_at"))
                            if payload.get("client_captured_at")
                            else None
                        ),
                    )
                )
                return
            if path == "/api/commit":
                self._send_json(
                    self.session.commit(
                        str(payload.get("reviewed_hash", "")),
                        confirmed=payload.get("confirmed") is True,
                    )
                )
                return
            if path == "/api/reset-demo":
                self._send_json(self.session.reset())
                return
            self._send_json({"error": "not found"}, status=HTTPStatus.NOT_FOUND)
        except ValueError as exc:
            self._send_json({"error": str(exc)}, status=HTTPStatus.BAD_REQUEST)
        except Exception as exc:
            self._send_json(
                {"error": type(exc).__name__, "detail": str(exc)},
                status=HTTPStatus.INTERNAL_SERVER_ERROR,
            )


def parse_args():
    parser = argparse.ArgumentParser(
        description="Run ERRATA's local operator review surface over the shared deterministic core."
    )
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", default=8765, type=int)
    parser.add_argument("--change-id", default="ERR-UI-001")
    parser.add_argument("--service-date", default="20260929")
    parser.add_argument("--start-time", default="09:00:00")
    parser.add_argument("--gtfs", default=str(ROOT / "fixtures" / "gtfs_static"))
    parser.add_argument("--web-root", default=str(ROOT / "web" / "operator"))
    parser.add_argument(
        "--evidence-file",
        default=str(
            ROOT
            / "evidence"
            / "external-acceptance-v0.1"
            / "CANONICAL-VALIDATOR-CI.json"
        ),
    )
    return parser.parse_args()


def main() -> None:
    if load_dotenv:
        load_dotenv()

    args = parse_args()
    session = OperatorSurfaceSession(
        gtfs_dir=args.gtfs,
        evidence_file=args.evidence_file,
        change_id=args.change_id,
        service_date=args.service_date,
        start_time=args.start_time,
    )

    OperatorHandler.session = session
    OperatorHandler.web_root = Path(args.web_root)
    server = ThreadingHTTPServer((args.host, args.port), OperatorHandler)

    print("ERRATA OPERATOR REVIEW SURFACE")
    print(f"url=http://{args.host}:{args.port}")
    print(f"change_id={args.change_id}")
    print("truth=SYNTHETIC_FIXTURE_LOCAL_SURFACE")
    print(
        "browser_voice="
        + ("READY" if os.environ.get("ASSEMBLYAI_API_KEY") else "BLOCKED_NO_API_KEY")
    )
    print(
        "neural_tts="
        + ("READY_AI33" if os.environ.get("AI33_API_KEY") else "FALLBACK_BROWSER")
    )
    print("Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[surface] stopping")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
