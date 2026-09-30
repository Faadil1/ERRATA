from errata.session_token import decode_session_token, encode_session_token


def test_signed_session_token_roundtrip_and_tamper_rejection():
    snapshot = {
        "schema": "errata-session-snapshot-v0.1",
        "state": {"revision": 3, "state_hash": "abc"},
    }
    token = encode_session_token(snapshot, "test-secret")
    assert decode_session_token(token, "test-secret") == snapshot

    head, payload, signature = token.split(".")
    replacement = "A" if payload[-1] != "A" else "B"
    tampered = f"{head}.{payload[:-1]}{replacement}.{signature}"

    try:
        decode_session_token(tampered, "test-secret")
    except ValueError as exc:
        assert "signature" in str(exc)
    else:
        raise AssertionError("tampered token was accepted")
