import json

import app as vercel_app


def _payload(response):
    return json.loads(response.body.decode("utf-8"))


def test_vercel_signed_session_survives_request_rehydration(monkeypatch):
    monkeypatch.setenv("ERRATA_SESSION_HMAC_KEY", "ci-session-secret")

    first = _payload(vercel_app.get_change(None))
    token = first.pop("_session_token")
    assert first["state"]["revision"] == 1
    assert first["truth_label"] == "PUBLIC_VERCEL_SIGNED_BROWSER_SESSION"

    amended = _payload(
        vercel_app.amend_direct(
            {"text": "Route 55 west, skip King Edward and Cumberland until 9:30."},
            token,
        )
    )
    token2 = amended.pop("_session_token")
    assert amended["state"]["revision"] == 2
    expected_hash = amended["state"]["state_hash"]

    resumed = _payload(vercel_app.get_change(token2))
    assert resumed["state"]["revision"] == 2
    assert resumed["state"]["state_hash"] == expected_hash
    assert resumed["runtime_state_model"]["kind"] == "SIGNED_BROWSER_SESSION"
    assert resumed["runtime_state_model"]["shared_multi_operator_store"] is False


def test_vercel_signed_session_rejects_tampering(monkeypatch):
    monkeypatch.setenv("ERRATA_SESSION_HMAC_KEY", "ci-session-secret")
    first = _payload(vercel_app.get_change(None))
    token = first["_session_token"]
    head, payload, signature = token.split(".")
    replacement = "A" if payload[-1] != "A" else "B"
    tampered = f"{head}.{payload[:-1]}{replacement}.{signature}"

    try:
        vercel_app.get_change(tampered)
    except Exception as exc:
        assert getattr(exc, "status_code", None) == 401
    else:
        raise AssertionError("tampered public session was accepted")


def test_vercel_runtime_health_binds_exact_git_sha(monkeypatch):
    monkeypatch.setenv("ERRATA_SESSION_HMAC_KEY", "ci-session-secret")
    monkeypatch.setenv("ERRATA_RUNTIME_GIT_SHA", "deadbeef1234")

    health = _payload(vercel_app.get_health())

    assert health["runtime"] == "vercel-fastapi"
    assert health["git_sha"] == "deadbeef1234"
    assert health["state_model"] == "SIGNED_BROWSER_SESSION"
    assert health["session_signing_ready"] is True
    assert health["full_public_voice_ready"] is False


def test_signed_session_token_remains_header_sized_after_canonical_rev3(monkeypatch):
    monkeypatch.setenv("ERRATA_SESSION_HMAC_KEY", "ci-session-secret")

    first = _payload(vercel_app.get_change(None))
    token = first["_session_token"]

    base = _payload(
        vercel_app.amend_voice(
            {
                "text": "Route 55 west, skip King Edward and Cumberland until 9:30.",
                "assemblyai_session_id": "ci-vercel-session",
                "boundary": "ForceEndpoint",
                "client_captured_at": "2026-09-30T00:00:00Z",
            },
            token,
        )
    )
    token = base["_session_token"]

    corrected = _payload(
        vercel_app.amend_voice(
            {
                "text": "Wait, keep Cumberland. Make it 10.",
                "assemblyai_session_id": "ci-vercel-session",
                "boundary": "ForceEndpoint",
                "client_captured_at": "2026-09-30T00:00:05Z",
            },
            token,
        )
    )
    token = corrected["_session_token"]

    assert corrected["state"]["revision"] == 3
    assert len(token.encode("utf-8")) < 12_000


def test_vercel_api_entrypoint_exports_canonical_fastapi_app():
    from api.index import app as entry_app

    assert entry_app is vercel_app.app
    paths = {route.path for route in entry_app.routes}
    assert "/api/health" in paths
    assert "/api/change" in paths
