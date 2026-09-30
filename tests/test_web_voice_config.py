from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
APP_JS = (ROOT / "web" / "operator" / "app.js").read_text(encoding="utf-8")


def test_browser_voice_uses_context_aware_assemblyai_streaming():
    assert 'speechMode: "balanced"' in APP_JS
    assert 'wsUrl.searchParams.set("agent_context", VOICE_COPY.greeting)' in APP_JS
    assert '"type":"UpdateConfiguration"' not in APP_JS  # ensure payload is constructed, not an opaque hard-coded string
    assert 'const payload = { type: "UpdateConfiguration" };' in APP_JS
    assert 'payload.agent_context' in APP_JS
    assert 'payload.keyterms_prompt' in APP_JS
    assert 'context_carryover: "provider-default-on"' in APP_JS


def test_dynamic_keyterms_follow_canonical_state():
    assert 'function assemblyAIKeytermsForState' in APP_JS
    assert '"King Edward", "Cumberland", "Route 55"' in APP_JS
    assert 'refreshAssemblyAIStateBias(payload, "canonical-amendment-applied")' in APP_JS


def test_agent_context_is_published_only_after_completed_guidance_playback():
    assert 'publishAssemblyAIAgentContext(text, "ai33-guidance-complete")' in APP_JS
    assert 'publishAssemblyAIAgentContext(text, "browser-guidance-complete")' in APP_JS
