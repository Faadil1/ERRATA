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
