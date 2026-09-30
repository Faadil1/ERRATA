from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Header, HTTPException
from fastapi.responses import JSONResponse, Response
from fastapi.staticfiles import StaticFiles

from errata.operator_surface import OperatorSurfaceSession
from errata.session_token import decode_session_token, encode_session_token
from scripts.run_operator_surface import (
    get_server_secret,
    mint_assemblyai_streaming_token,
    synthesize_errata_guidance,
    voice_capabilities,
)


ROOT = Path(__file__).resolve().parent
GTFS_DIR = ROOT / "fixtures" / "gtfs_static"
EVIDENCE_FILE = (
    ROOT
    / "evidence"
    / "external-acceptance-v0.1"
    / "CANONICAL-VALIDATOR-CI.json"
)

app = FastAPI(title="ERRATA", docs_url=None, redoc_url=None)


def _session_secret() -> str:
    for name in ("ERRATA_SESSION_HMAC_KEY", "ASSEMBLYAI_API_KEY", "AI33_API_KEY"):
        value = get_server_secret(name)
        if value:
            return value
    raise HTTPException(
        status_code=503,
        detail=(
            "SERVER_SESSION_SECRET_REQUIRED: configure ERRATA_SESSION_HMAC_KEY "
            "or a server-side AssemblyAI/AI33 key before using the public state API"
        ),
    )


def _new_session() -> OperatorSurfaceSession:
    return OperatorSurfaceSession(
        gtfs_dir=GTFS_DIR,
        evidence_file=EVIDENCE_FILE if EVIDENCE_FILE.exists() else None,
    )


def _load_session(token: str | None) -> OperatorSurfaceSession:
    secret = _session_secret()
    if not token:
        return _new_session()
    try:
        snapshot = decode_session_token(token, secret)
        return OperatorSurfaceSession.from_snapshot(
            snapshot,
            gtfs_dir=GTFS_DIR,
            evidence_file=EVIDENCE_FILE if EVIDENCE_FILE.exists() else None,
        )
    except ValueError as exc:
        raise HTTPException(status_code=401, detail=f"INVALID_SESSION_TOKEN: {exc}") from exc


def _publicize(payload: dict[str, Any]) -> dict[str, Any]:
    payload = dict(payload)
    payload["truth_label"] = "PUBLIC_VERCEL_SIGNED_BROWSER_SESSION"
    payload["connection"] = {
        "status": "PUBLIC_READY",
        "detail": (
            "Vercel FastAPI runtime using the shared ERRATA core and an "
            "integrity-protected browser session snapshot."
        ),
    }
    payload["runtime_state_model"] = {
        "kind": "SIGNED_BROWSER_SESSION",
        "shared_multi_operator_store": False,
        "cold_start_continuity": True,
        "rollback_resistance": False,
    }
    return payload


def _session_response(
    session: OperatorSurfaceSession,
    payload: dict[str, Any],
    *,
    status_code: int = 200,
) -> JSONResponse:
    public_payload = _publicize(payload)
    public_payload["_session_token"] = encode_session_token(
        session.export_snapshot(),
        _session_secret(),
    )
    return JSONResponse(public_payload, status_code=status_code)


def _runtime_metadata() -> dict[str, Any]:
    return {
        "surface": "vercel-fastapi-signed-browser-session",
        "git_sha": os.environ.get("VERCEL_GIT_COMMIT_SHA"),
        "git_branch": os.environ.get("VERCEL_GIT_COMMIT_REF"),
        "vercel_url": os.environ.get("VERCEL_URL"),
        "deployment_id": os.environ.get("VERCEL_DEPLOYMENT_ID"),
        "state_model": "SIGNED_BROWSER_SESSION",
        "shared_multi_operator_store": False,
    }


@app.get("/api/change")
def get_change(x_errata_session: str | None = Header(default=None)):
    session = _load_session(x_errata_session)
    return _session_response(session, session.view())


@app.get("/api/evidence")
def get_evidence(x_errata_session: str | None = Header(default=None)):
    session = _load_session(x_errata_session)
    return _session_response(session, session.view()["external_evidence"])


@app.get("/api/session-receipt")
def get_receipt(x_errata_session: str | None = Header(default=None)):
    session = _load_session(x_errata_session)
    receipt = session.evidence_receipt(runtime=_runtime_metadata())
    receipt["truth_boundary"] = (
        "PUBLIC_VERCEL_SIGNED_BROWSER_SESSION; integrity-protected browser "
        "snapshot, not shared durable multi-operator storage, agency integration, "
        "or production deployment"
    )
    return _session_response(session, receipt)


@app.get("/api/voice-capabilities")
def get_voice_capabilities():
    payload = voice_capabilities()
    payload["runtime"] = "vercel"
    payload["signed_browser_session"] = bool(
        get_server_secret("ERRATA_SESSION_HMAC_KEY")
        or get_server_secret("ASSEMBLYAI_API_KEY")
        or get_server_secret("AI33_API_KEY")
    )
    return JSONResponse(payload)


@app.get("/api/voice-token")
def get_voice_token():
    try:
        return JSONResponse(
            mint_assemblyai_streaming_token(
                get_server_secret("ASSEMBLYAI_API_KEY")
            )
        )
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@app.post("/api/preview/voice")
def preview_voice(
    payload: dict[str, Any],
    x_errata_session: str | None = Header(default=None),
):
    session = _load_session(x_errata_session)
    result = session.preview_voice(str(payload.get("text", "")))
    return _session_response(session, result)


@app.post("/api/amend/direct")
def amend_direct(
    payload: dict[str, Any],
    x_errata_session: str | None = Header(default=None),
):
    session = _load_session(x_errata_session)
    return _session_response(
        session,
        session.amend_direct(str(payload.get("text", ""))),
    )


@app.post("/api/amend/voice")
def amend_voice(
    payload: dict[str, Any],
    x_errata_session: str | None = Header(default=None),
):
    session = _load_session(x_errata_session)
    return _session_response(
        session,
        session.amend_voice(
            str(payload.get("text", "")),
            assemblyai_session_id=payload.get("assemblyai_session_id"),
            boundary=str(payload.get("boundary") or "ForceEndpoint"),
            client_captured_at=payload.get("client_captured_at"),
        ),
    )


@app.post("/api/commit")
def commit(
    payload: dict[str, Any],
    x_errata_session: str | None = Header(default=None),
):
    session = _load_session(x_errata_session)
    return _session_response(
        session,
        session.commit(
            str(payload.get("reviewed_hash", "")),
            confirmed=bool(payload.get("confirmed")),
        ),
    )


@app.post("/api/reset-demo")
def reset_demo():
    session = _new_session()
    return _session_response(session, session.view())


@app.post("/api/tts/guidance")
def tts_guidance(payload: dict[str, Any]):
    try:
        audio, meta = synthesize_errata_guidance(
            str(payload.get("text", "")),
            api_key=get_server_secret("AI33_API_KEY"),
            voice_id=(
                str(payload.get("voice_id"))
                if payload.get("voice_id")
                else None
            ),
        )
    except (RuntimeError, ValueError) as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc

    return Response(
        content=audio,
        media_type="audio/mpeg",
        headers={
            "Cache-Control": "private, max-age=86400",
            "X-ERRATA-TTS-Provider": "AI33-Pro",
            "X-ERRATA-TTS-Route": "AI33-v3-TTS-to-ElevenLabs",
            "X-ERRATA-TTS-Voice": str(meta["voice_id"]),
            "X-ERRATA-TTS-Task": str(meta["task_id"]),
            "X-ERRATA-TTS-Generation-Ms": str(meta["generation_ms"]),
            "X-ERRATA-TTS-Credit-Cost": str(meta.get("credit_cost") or ""),
            "X-ERRATA-TTS-Cache": "HIT" if meta.get("cache_hit") else "MISS",
            "X-ERRATA-TTS-Disclosure": "AI-generated voice",
        },
    )


app.mount(
    "/",
    StaticFiles(directory=str(ROOT / "web" / "operator"), html=True),
    name="operator",
)
