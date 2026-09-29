from pathlib import Path

import pytest

from errata.gtfs import GTFSIndex
from errata.live.coordinator import LiveTransactionCoordinator, PreparationError
from errata.models import Operation, ServiceChange
from errata.reducer import Reducer, StaleState


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "fixtures" / "gtfs_static"


def seed_context(state, reducer, gtfs):
    expected = state.state_hash
    ops = [
        Operation(
            operation_id="seed-date",
            kind="SET_SERVICE_DATE",
            expected_hash=expected,
            payload={"service_date": "20260929"},
            turn_id="system",
            transcript_text="system session context",
            source="system_default",
        ),
        Operation(
            operation_id="seed-start",
            kind="SET_TIME_WINDOW",
            expected_hash=expected,
            payload={"start_time": "09:00:00"},
            turn_id="system",
            transcript_text="system session context",
            source="system_default",
        ),
    ]
    reducer.apply_batch(state, ops, gtfs)


def tool(call_id, operations):
    return {
        "type": "tool.call",
        "call_id": call_id,
        "name": "propose_service_change",
        "arguments": {"operations": operations},
    }


def test_prepare_interrupt_apply_amend_commit_contract():
    gtfs = GTFSIndex(FIXTURE)
    state = ServiceChange("ERR-LIVE-TEST")
    reducer = Reducer()
    seed_context(state, reducer, gtfs)
    coord = LiveTransactionCoordinator(state, reducer, gtfs)

    # Initial spoken change: PREPARE must not mutate truth.
    coord.bind_user_transcript(
        "turn-1",
        "Route 55 west, skip King Edward and Cumberland until 9:30.",
    )
    before_prepare = state.state_hash
    prepared = coord.prepare_tool_call(
        tool(
            "call-1",
            [
                {"kind": "SET_ROUTE_MENTION", "text": "55"},
                {"kind": "SET_DIRECTION_MENTION", "text": "west"},
                {"kind": "ADD_SKIP_STOP_MENTION", "text": "King Edward"},
                {"kind": "ADD_SKIP_STOP_MENTION", "text": "Cumberland"},
                {"kind": "SET_END_TIME_TEXT", "text": "9:30"},
            ],
        )
    )
    assert prepared["status"] == "PREPARED"
    assert state.state_hash == before_prepare
    assert state.revision == 1

    applied = coord.finalize_pending()
    assert applied[0]["status"] == "APPLIED"
    assert state.revision == 2
    assert set(state.skip_stops) == {"S_KING_EDWARD", "S_CUMBERLAND"}
    assert state.end_time.value == "09:30:00"
    assert reducer.operations[-1].transcript_text.endswith("9:30.")

    # Attach derived artifacts so a later amendment must invalidate them.
    reducer.attach_artifact(state, "A-LIVE", "SERVICE_ALERT")
    reducer.attach_artifact(state, "T-LIVE", "TRIP_UPDATE")
    before_correction = state.normalized_business_state()
    rev2_hash = state.state_hash

    # Simulated true interruption boundary: prepare, then discard. No reducer call.
    coord.bind_user_transcript("turn-2", "Wait—")
    coord.prepare_tool_call(
        tool(
            "call-interrupted",
            [{"kind": "ADD_SKIP_STOP_MENTION", "text": "Laurier"}],
        )
    )
    interrupt_hash = state.state_hash
    discarded = coord.discard_pending("ASSEMBLYAI_REPLY_INTERRUPTED")
    assert discarded[0]["status"] == "DISCARDED"
    assert state.state_hash == interrupt_hash
    assert state.revision == 2
    assert "S_LAURIER" not in state.skip_stops

    # Spoken self-repair amends the same change and only targeted fields.
    coord.bind_user_transcript("turn-3", "Wait — keep Cumberland. Make it 10.")
    coord.prepare_tool_call(
        tool(
            "call-2",
            [
                {"kind": "REMOVE_SKIP_STOP_MENTION", "text": "Cumberland"},
                {"kind": "SET_END_TIME_TEXT", "text": "10"},
            ],
        )
    )
    amended = coord.finalize_pending()
    assert amended[0]["status"] == "APPLIED"
    assert state.change_id == "ERR-LIVE-TEST"
    assert state.revision == 3
    assert set(state.skip_stops) == {"S_KING_EDWARD"}
    assert state.end_time.value == "10:00:00"

    after_correction = state.normalized_business_state()
    changed = {k for k in before_correction if before_correction[k] != after_correction[k]}
    assert changed == {"end_time", "skip_stops"}
    assert all(a.status == "STALE" for a in state.artifacts)

    # Superseded history is preserved rather than overwritten.
    old_cumberland = next(o for o in reducer.operations if o.operation_id == "call-1:3")
    correction = next(o for o in reducer.operations if o.operation_id == "call-2:0")
    assert old_cumberland.status == "SUPERSEDED"
    assert correction.supersedes == ["call-1:3"]

    # State-driven recognition biasing is derived from deterministic route context.
    keyterms = coord.route_keyterms()
    assert "King Edward" in keyterms
    assert "Cumberland" in keyterms

    # Human authority is hash-bound.
    with pytest.raises(StaleState):
        coord.human_commit(rev2_hash[:16])

    current = state.state_hash
    receipt = coord.human_commit(current[:16])
    assert receipt["authority"] == "human_terminal_command"
    assert receipt["state_hash"] == current
    assert state.committed_hash == current


def test_unresolved_stop_never_mutates():
    gtfs = GTFSIndex(FIXTURE)
    state = ServiceChange("ERR-LIVE-NEG")
    reducer = Reducer()
    seed_context(state, reducer, gtfs)
    coord = LiveTransactionCoordinator(state, reducer, gtfs)
    coord.bind_user_transcript(
        "turn-neg",
        "Route 55 west, skip Hovercraft Terminal until 9:30.",
    )
    before = state.state_hash

    with pytest.raises(PreparationError):
        coord.prepare_tool_call(
            tool(
                "call-neg",
                [
                    {"kind": "SET_ROUTE_MENTION", "text": "55"},
                    {"kind": "SET_DIRECTION_MENTION", "text": "west"},
                    {"kind": "ADD_SKIP_STOP_MENTION", "text": "Hovercraft Terminal"},
                    {"kind": "SET_END_TIME_TEXT", "text": "9:30"},
                ],
            )
        )

    assert state.state_hash == before
    assert state.revision == 1
    assert coord.pending == []
