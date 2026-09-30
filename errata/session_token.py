from __future__ import annotations

import base64
import hashlib
import hmac
import json
import zlib
from typing import Any


TOKEN_VERSION = "v1"


def _b64url_encode(data: bytes) -> str:
    return base64.urlsafe_b64encode(data).decode("ascii").rstrip("=")


def _b64url_decode(value: str) -> bytes:
    padding = "=" * (-len(value) % 4)
    return base64.urlsafe_b64decode(value + padding)


def encode_session_token(snapshot: dict[str, Any], secret: str) -> str:
    if not secret:
        raise ValueError("session token secret is required")
    raw = json.dumps(
        snapshot,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=False,
    ).encode("utf-8")
    compressed = zlib.compress(raw, level=9)
    payload = _b64url_encode(compressed)
    signed = f"{TOKEN_VERSION}.{payload}".encode("ascii")
    signature = hmac.new(
        secret.encode("utf-8"),
        signed,
        hashlib.sha256,
    ).digest()
    return f"{TOKEN_VERSION}.{payload}.{_b64url_encode(signature)}"


def decode_session_token(token: str, secret: str) -> dict[str, Any]:
    if not secret:
        raise ValueError("session token secret is required")
    parts = token.split(".")
    if len(parts) != 3 or parts[0] != TOKEN_VERSION:
        raise ValueError("invalid session token format")

    version, payload, signature = parts
    signed = f"{version}.{payload}".encode("ascii")
    expected = hmac.new(
        secret.encode("utf-8"),
        signed,
        hashlib.sha256,
    ).digest()
    supplied = _b64url_decode(signature)
    if not hmac.compare_digest(expected, supplied):
        raise ValueError("invalid session token signature")

    try:
        raw = zlib.decompress(_b64url_decode(payload))
        decoded = json.loads(raw.decode("utf-8"))
    except Exception as exc:
        raise ValueError("invalid session token payload") from exc
    if not isinstance(decoded, dict):
        raise ValueError("session token payload must be an object")
    return decoded
