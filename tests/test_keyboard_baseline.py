from pathlib import Path

from errata.gtfs import GTFSIndex
from errata.live.coordinator import LiveTransactionCoordinator
from errata.live.direct_entry import apply_direct_text
from errata.models import Operation, ServiceChange
from errata.reducer import Reducer


ROOT = Path(__file__).resolve().parents[1]
GTFS = GTFSIndex(ROOT / "fixtures" / "gtfs_static")


def _seed():
    state = ServiceChange("ERR-KEYBOARD-TEST")
    reducer = Reducer()
    expected = state.state_hash
    reducer.apply_batch(
        state,
        [
            Operation("sd", "SET_SERVICE_DATE", expected, {"service_date": "20260929"}, "s", "s", "test"),
            Operation("st", "SET_TIME_WINDOW", expected, {"start_time": "09:00:00"}, "s", "s", "test"),
        ],
        GTFS,
    )
    return state, reducer


def test_keyboard_baseline_reaches_same_semantic_state():
    state, reducer = _seed()
    coord = LiveTransactionCoordinator(state, reducer, GTFS)

    first = apply_direct_text(
        coord,
        label="initial",
        text="Route 55 west, skip King Edward and Cumberland until 9:30.",
        entry_elapsed_ms=1000.0,
        call_id="kb-1",
    )
    assert first.result[0]["status"] == "APPLIED"
    assert state.revision == 2

    second = apply_direct_text(
        coord,
        label="correction",
        text="Wait, keep Cumberland. Make it 10.",
        entry_elapsed_ms=500.0,
        call_id="kb-2",
    )
    assert second.result[0]["status"] == "APPLIED"
    assert state.revision == 3
    assert state.change_id == "ERR-KEYBOARD-TEST"
    assert state.route_ref.value == "R55"
    assert state.route_direction.value == 1
    assert state.end_time.value == "10:00:00"
    assert set(state.skip_stops) == {"S_KING_EDWARD"}
    assert state.unresolved_items == []
