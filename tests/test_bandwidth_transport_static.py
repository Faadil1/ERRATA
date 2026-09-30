from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
COMMON = (ROOT / "api" / "bandwidth-common.js").read_text(encoding="utf-8")
VOICE = (ROOT / "api" / "bandwidth-voice.js").read_text(encoding="utf-8")
STREAM = (ROOT / "api" / "bandwidth-stream.js").read_text(encoding="utf-8")
GATHER = (ROOT / "api" / "bandwidth-gather.js").read_text(encoding="utf-8")
VERCEL = (ROOT / "vercel.json").read_text(encoding="utf-8")


def test_bandwidth_uses_native_pcmu_8khz_assemblyai_path():
    assert 'url.searchParams.set("sample_rate", "8000")' in STREAM
    assert 'url.searchParams.set("encoding", "pcm_mulaw")' in STREAM
    assert 'url.searchParams.set("speech_model", "universal-3-5-pro")' in STREAM
    assert 'message.eventType === "media"' in STREAM
    assert 'message.track !== "inbound"' in STREAM
    assert 'Buffer.from(payload, "base64")' in STREAM


def test_bandwidth_review_is_non_mutating_until_dtmf_one():
    assert '"/api/preview/voice"' in STREAM
    assert 'READY_TO_APPLY' in STREAM
    assert 'Nothing has been applied' in STREAM
    assert 'digit === "2"' in GATHER
    assert 'digit !== "1"' in GATHER
    assert 'boundary: "BandwidthDTMF1"' in GATHER
    assert '"/api/amend/voice"' in GATHER


def test_bandwidth_review_token_binds_call_and_canonical_state():
    assert 'canonicalRevision: preview.canonical_revision' in STREAM
    assert 'canonicalHash: preview.canonical_hash' in STREAM
    assert 'callId !== String(review.callId' in GATHER
    assert 'canonical_revision' in GATHER
    assert 'canonical_hash' in GATHER
    assert 'createHmac("sha256"' in COMMON


def test_bandwidth_webhook_and_stream_require_server_side_basic_auth():
    assert '"BANDWIDTH_WEBHOOK_USERNAME"' in VOICE
    assert '"BANDWIDTH_WEBHOOK_PASSWORD"' in VOICE
    assert '"BANDWIDTH_STREAM_USERNAME"' in STREAM
    assert '"BANDWIDTH_STREAM_PASSWORD"' in STREAM
    assert 'WWW-Authenticate' in COMMON


def test_bandwidth_replaces_live_call_bxml_with_oauth_client_credentials():
    assert 'https://api.bandwidth.com/api/v1/oauth2/token' in COMMON
    assert 'grant_type=client_credentials' in COMMON
    assert '/calls/${encodeURIComponent(callId)}/bxml' in COMMON
    assert '"Content-Type": "application/xml"' in COMMON
    assert 'method: "PUT"' in COMMON


def test_vercel_routes_bandwidth_before_python_catchall():
    for route in (
        '"/bandwidth/voice"',
        '"/api/bandwidth-stream"',
        '"/bandwidth/gather"',
    ):
        assert VERCEL.index(route) < VERCEL.index('"/(.*)"')


def test_bandwidth_bxml_root_matches_delivery_mode():
    # Call-initiation and Gather callbacks return normal BXML responses.
    assert "<Response>" in VOICE
    assert "<Response>" in GATHER

    # Direct PUT /calls/{callId}/bxml expects the dedicated Bxml root.
    assert "<Bxml>" in STREAM
    assert "</Bxml>" in STREAM
