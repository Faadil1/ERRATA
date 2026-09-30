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
