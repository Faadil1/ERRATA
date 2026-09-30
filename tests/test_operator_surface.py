from pathlib import Path

from errata.operator_surface import OperatorSurfaceSession


ROOT = Path(__file__).resolve().parents[1]


def make_session():
    return OperatorSurfaceSession(
        gtfs_dir=ROOT / "fixtures" / "gtfs_static",
        evidence_file=ROOT
        / "evidence"
        / "external-acceptance-v0.1"
        / "CANONICAL-VALIDATOR-CI.json",
        change_id="ERR-UI-TEST",
        service_date="20260929",
        start_time="09:00:00",
    )


def test_operator_surface_canonical_correction_and_commit_guard():
    session = make_session()
    start = session.view()
    assert start["state"]["revision"] == 1
    assert start["state"]["status"] == "STAGED"

    first = session.amend_direct(
        "Route 55 west, skip King Edward and Cumberland until 9:30."
    )
    assert first["latest_transaction"]["status"] == "APPLIED"
    assert first["state"]["revision"] == 2
    old_hash = first["state"]["state_hash"]

    second = session.amend_direct("Wait, keep Cumberland. Make it 10.")
    assert second["latest_transaction"]["status"] == "APPLIED"
    assert second["state"]["revision"] == 3
    assert second["state"]["end_time"] == "10:00:00"
    assert [s["stop_id"] for s in second["state"]["skip_stops"]] == ["S_KING_EDWARD"]
    assert {d["field"] for d in second["latest_transaction"]["diff"]} == {
        "end_time",
        "skip_stops",
    }

    stale = session.commit(old_hash[:12], confirmed=True)
    assert stale["latest_transaction"]["status"] == "STALE_REVIEW"
    assert stale["state"]["revision"] == 3
    assert stale["state"]["status"] == "STAGED"

    current_hash = stale["state"]["state_hash"]
    committed = session.commit(current_hash[:12], confirmed=True)
    assert committed["latest_transaction"]["status"] == "COMMITTED"
    assert committed["latest_transaction"]["receipt"]["authority"] == "human_web_review"
    assert committed["state"]["status"] == "COMMITTED"


def test_operator_surface_review_required_has_zero_mutation():
    session = make_session()
    session.amend_direct(
        "Route 55 west, skip King Edward and Cumberland until 9:30."
    )
    before = session.view()
    result = session.amend_direct("Wait, keep Cumberland. Make it.")

    assert result["latest_transaction"]["status"] == "REVIEW_REQUIRED"
    assert "END_TIME_AFTER_MAKE_IT" in result["latest_transaction"]["reason"]
    assert result["state"]["revision"] == before["state"]["revision"]
    assert result["state"]["state_hash"] == before["state"]["state_hash"]


def test_operator_surface_requires_explicit_commit_confirmation():
    session = make_session()
    session.amend_direct(
        "Route 55 west, skip King Edward and Cumberland until 9:30."
    )
    current_hash = session.view()["state"]["state_hash"]
    result = session.commit(current_hash[:12], confirmed=False)

    assert result["latest_transaction"]["status"] == "REVIEW_REQUIRED"
    assert result["latest_transaction"]["reason"] == "EXPLICIT_REVIEW_CONFIRMATION_REQUIRED"
    assert result["state"]["status"] == "STAGED"


def test_operator_surface_loads_external_acceptance_evidence():
    session = make_session()
    evidence = session.view()["external_evidence"]
    assert evidence["status"] == "PROVEN_BOUNDED_SYNTHETIC_FIXTURE"
    assert evidence["validator"]["blocking_error_group_count"] == 0
    assert evidence["official_bindings_consumer"]["pass"] is True


def test_operator_surface_capabilities_and_post_commit_lock():
    session = make_session()
    initial = session.view()
    assert initial["capabilities"]["can_author"] is True
    assert initial["capabilities"]["commit_ready"] is False

    staged = session.amend_direct(
        "Route 55 west, skip King Edward and Cumberland until 9:30."
    )
    assert staged["capabilities"]["commit_ready"] is True
    staged_hash = staged["state"]["state_hash"]

    committed = session.commit(staged_hash[:12], confirmed=True)
    assert committed["state"]["status"] == "COMMITTED"
    assert committed["capabilities"]["can_author"] is False
    assert committed["capabilities"]["commit_ready"] is False

    after = session.amend_direct("Wait, keep Cumberland. Make it 10.")
    assert after["latest_transaction"]["status"] == "REJECTED"
    assert after["latest_transaction"]["reason"] == "CHANGE_ALREADY_COMMITTED"
    assert after["state"]["revision"] == committed["state"]["revision"]
    assert after["state"]["state_hash"] == committed["state"]["state_hash"]


def test_operator_surface_voice_uses_same_core_with_distinct_provenance():
    session = make_session()
    first = session.amend_voice(
        "Route 55 west, skip King Edward and Cumberland until 9:30.",
        assemblyai_session_id="aai-browser-test-1",
        boundary="ForceEndpoint",
        client_captured_at="2026-09-30T06:20:00Z",
    )
    assert first["latest_transaction"]["status"] == "APPLIED"
    assert first["latest_transaction"]["source"] == (
        "assemblyai_browser_voice_human_boundary"
    )
    assert first["latest_transaction"]["source_metadata"]["session_id"] == (
        "aai-browser-test-1"
    )
    assert first["latest_transaction"]["source_metadata"]["human_boundary"] == (
        "ForceEndpoint"
    )
    assert first["state"]["revision"] == 2

    second = session.amend_voice("Wait, keep Cumberland. Make it 10.")
    assert second["latest_transaction"]["status"] == "APPLIED"
    assert second["latest_transaction"]["source"] == (
        "assemblyai_browser_voice_human_boundary"
    )
    assert second["state"]["revision"] == 3
    assert second["state"]["end_time"] == "10:00:00"
    assert [s["stop_id"] for s in second["state"]["skip_stops"]] == [
        "S_KING_EDWARD"
    ]


def test_operator_surface_voice_review_required_has_zero_mutation():
    session = make_session()
    session.amend_voice(
        "Route 55 west, skip King Edward and Cumberland until 9:30."
    )
    before = session.view()
    result = session.amend_voice("Wait, keep Cumberland. Make it.")

    assert result["latest_transaction"]["status"] == "REVIEW_REQUIRED"
    assert result["state"]["revision"] == before["state"]["revision"]
    assert result["state"]["state_hash"] == before["state"]["state_hash"]


def test_operator_surface_evidence_receipt_contains_voice_history():
    session = make_session()
    session.amend_voice(
        "Route 55 west, skip King Edward and Cumberland until 9:30.",
        assemblyai_session_id="aai-proof-session",
        client_captured_at="2026-09-30T06:30:00Z",
    )
    receipt = session.evidence_receipt(
        runtime={
            "git_sha": "test-sha",
            "tracked_worktree_clean": True,
            "surface": "test",
        }
    )

    assert receipt["schema"] == "errata-browser-voice-receipt-v0.1"
    assert receipt["runtime"]["git_sha"] == "test-sha"
    assert receipt["state"]["revision"] == 2
    assert receipt["history"][0]["source"] == (
        "assemblyai_browser_voice_human_boundary"
    )
    assert receipt["history"][0]["source_metadata"]["session_id"] == (
        "aai-proof-session"
    )


def test_voice_preview_interprets_without_mutating_canonical_state():
    session = make_session()
    before = session.view()

    preview = session.preview_voice(
        "Route 55 west, skip King Edward and Cumberland until 9:30."
    )

    assert preview["schema"] == "errata-voice-preview-v0.1"
    assert preview["status"] == "READY_TO_APPLY"
    assert preview["raw_status"] == "APPLIED"
    assert preview["canonical_unchanged"] is True
    assert preview["canonical_revision"] == 1
    assert preview["candidate_revision"] == 2
    assert preview["candidate"]["route"] == "55"
    assert preview["candidate"]["end_time"] == "09:30:00"
    assert "King Edward" in preview["guidance"]["message"]
    assert "Nothing has changed yet" in preview["guidance"]["message"]

    after = session.view()
    assert after["state"]["revision"] == before["state"]["revision"]
    assert after["state"]["state_hash"] == before["state"]["state_hash"]
    assert after["history"] == before["history"]


def test_voice_preview_guides_incomplete_correction_without_mutation():
    session = make_session()
    session.amend_voice(
        "Route 55 west, skip King Edward and Cumberland until 9:30."
    )
    before = session.view()

    preview = session.preview_voice("Wait, keep Cumberland. Make it.")

    assert preview["status"] == "NEEDS_CLARIFICATION"
    assert preview["raw_status"] == "REVIEW_REQUIRED"
    assert "END_TIME_AFTER_MAKE_IT" in preview["reason"]
    assert "complete time" in preview["guidance"]["message"]
    assert "Make it 10" in preview["guidance"]["next_action"]

    after = session.view()
    assert after["state"]["revision"] == before["state"]["revision"]
    assert after["state"]["state_hash"] == before["state"]["state_hash"]
    assert after["history"] == before["history"]


def test_voice_preview_is_blocked_after_commit():
    session = make_session()
    staged = session.amend_direct(
        "Route 55 west, skip King Edward and Cumberland until 9:30."
    )
    session.commit(staged["state"]["state_hash"][:12], confirmed=True)

    preview = session.preview_voice("Wait, keep Cumberland. Make it 10.")

    assert preview["status"] == "BLOCKED"
    assert preview["reason"] == "CHANGE_ALREADY_COMMITTED"
    assert preview["canonical_unchanged"] is True
