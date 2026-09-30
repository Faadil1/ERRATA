from __future__ import annotations

import argparse
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import subprocess
import sys
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
    print("Ctrl+C to stop.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[surface] stopping")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
