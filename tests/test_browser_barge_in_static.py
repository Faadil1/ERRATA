from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
APP_JS = (ROOT / "web" / "operator" / "app.js").read_text(encoding="utf-8")
INDEX = (ROOT / "web" / "operator" / "index.html").read_text(encoding="utf-8")


def test_barge_in_is_explicit_opt_in_and_evidence_backed():
    assert 'bargeInEnabled: false' in APP_JS
    assert 'message.type === "SpeechStarted"' in APP_JS
    assert '"VOICE_BARGE_IN"' in APP_JS
    assert '"BARGE_IN_MODE_CHANGED"' in APP_JS
    assert 'canonical_unchanged: true' in APP_JS
    assert 'id="toggleBargeIn"' in INDEX
    assert 'aria-pressed="false"' in INDEX


def test_barge_in_streams_mic_only_during_active_playback_when_enabled():
    assert 'voiceCapture.bargeInEnabled && voiceCapture.speaking' in APP_JS
    assert '(!echoGuardActive() || mayStreamDuringPlayback)' in APP_JS


def test_microphone_failures_are_explained_without_mutation():
    assert '"NotAllowedError"' in APP_JS
    assert '"NotFoundError"' in APP_JS
    assert '"NotReadableError"' in APP_JS
    assert '"VOICE_START_FAILED"' in APP_JS
