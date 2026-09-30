from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
VOICE = (ROOT / "api" / "twilio-voice.js").read_text(encoding="utf-8")
STREAM = (ROOT / "api" / "twilio-stream.js").read_text(encoding="utf-8")
VERCEL = (ROOT / "vercel.json").read_text(encoding="utf-8")


def test_twilio_transport_preserves_human_apply_boundary():
    assert 'boundary: "TwilioDTMF1"' in STREAM
    assert 'latestPreview?.status !== "READY_TO_APPLY"' in STREAM
    assert 'if (!previewSmsDelivered)' in STREAM
    assert 'digit === "1"' in STREAM
    assert 'digit === "2"' in STREAM


def test_twilio_audio_matches_assemblyai_native_phone_format():
    assert 'url.searchParams.set("sample_rate", "8000")' in STREAM
    assert 'url.searchParams.set("encoding", "pcm_mulaw")' in STREAM
    assert 'url.searchParams.set("speech_model", "universal-3-5-pro")' in STREAM
    assert 'url.searchParams.set("mode", "balanced")' in STREAM
    assert 'Buffer.from(payload, "base64")' in STREAM


def test_twilio_webhook_and_media_stream_validate_signatures():
    assert 'twilio.validateRequest' in VOICE
    assert 'twilio.validateRequest' in STREAM
    assert 'x-twilio-signature' in VOICE.lower()
    assert 'x-twilio-signature' in STREAM.lower()


def test_vercel_routes_twilio_transport_before_python_catchall():
    voice_index = VERCEL.index('"/twilio/voice"')
    stream_index = VERCEL.index('"/api/twilio-stream"')
    catchall_index = VERCEL.index('"/(.*)"')

    assert voice_index < catchall_index
    assert stream_index < catchall_index
