from pathlib import Path

from errata.gtfs import GTFSIndex
from errata.live.controlled_parser import parse_operational_transcript
from errata.models import Operation, ServiceChange
from errata.reducer import Reducer


ROOT = Path(__file__).resolve().parents[1]
GTFS = GTFSIndex(ROOT / "fixtures" / "gtfs_static")


def test_initial_fragmented_capture_reconstructs_bounded_ops():
    state = ServiceChange("ERR-PARSE-1")
    parsed = parse_operational_transcript(
        "Route. 55 West, skip. King Edward and Cumberland until 9:30.",
        GTFS,
        state,
    )
    assert parsed.operations == [
        "ROUTE=55",
        "DIRECTION=west",
        "SKIP=King Edward",
        "SKIP=Cumberland",
        "END=9:30",
    ]


def test_correction_capture_preserves_order_and_same_state_target():
    state = ServiceChange("ERR-PARSE-2")
    reducer = Reducer()
    expected = state.state_hash
    reducer.apply_batch(
        state,
        [
            Operation("r", "SET_ROUTE", expected, {"route_id": "R55"}, "s", "s", "test"),
            Operation("d", "SET_DIRECTION", expected, {"direction_id": 1}, "s", "s", "test"),
            Operation("sd", "SET_SERVICE_DATE", expected, {"service_date": "20260929"}, "s", "s", "test"),
            Operation("tw", "SET_TIME_WINDOW", expected, {"start_time": "09:00:00", "end_time": "09:30:00"}, "s", "s", "test"),
            Operation("k", "ADD_SKIP_STOP", expected, {"stop_id": "S_KING_EDWARD"}, "s", "s", "test"),
            Operation("c", "ADD_SKIP_STOP", expected, {"stop_id": "S_CUMBERLAND"}, "s", "s", "test"),
        ],
        GTFS,
    )
    parsed = parse_operational_transcript(
        "Wait. Keep. Cumberland, make it 10 AM.",
        GTFS,
        state,
    )
    assert parsed.operations == ["KEEP=Cumberland", "END=10am"]


def test_single_capture_self_repair_retains_spoken_order():
    state = ServiceChange("ERR-PARSE-3")
    parsed = parse_operational_transcript(
        "Route 55 west, skip King Edward and Cumberland, wait keep Cumberland, make it 10.",
        GTFS,
        state,
    )
    assert parsed.operations == [
        "ROUTE=55",
        "DIRECTION=west",
        "SKIP=King Edward",
        "SKIP=Cumberland",
        "KEEP=Cumberland",
        "END=10",
    ]


def test_realtime_stt_spaced_clock_separator_preserves_minutes():
    for utterance in (
        "Route 55 west, skip King Edward and Cumberland until 9: 30.",
        "Route 55 west, skip King Edward and Cumberland until 9 : 30.",
        "Route 55 west, skip King Edward and Cumberland until 09 : 30.",
    ):
        state = ServiceChange("ERR-PARSE-SPACED-TIME")
        parsed = parse_operational_transcript(utterance, GTFS, state)
        assert "END=9:30" in parsed.operations or "END=09:30" in parsed.operations
        assert "END=9" not in parsed.operations
        assert parsed.unresolved_cues == ()


def test_bounded_code_switch_correction_keeps_same_semantics():
    state = ServiceChange("ERR-PARSE-BILINGUAL")
    reducer = Reducer()
    expected = state.state_hash
    reducer.apply_batch(
        state,
        [
            Operation("r2", "SET_ROUTE", expected, {"route_id": "R55"}, "s", "s", "test"),
            Operation("d2", "SET_DIRECTION", expected, {"direction_id": 1}, "s", "s", "test"),
            Operation("sd2", "SET_SERVICE_DATE", expected, {"service_date": "20260929"}, "s", "s", "test"),
            Operation("tw2", "SET_TIME_WINDOW", expected, {"start_time": "09:00:00", "end_time": "09:30:00"}, "s", "s", "test"),
            Operation("k2", "ADD_SKIP_STOP", expected, {"stop_id": "S_KING_EDWARD"}, "s", "s", "test"),
            Operation("c2", "ADD_SKIP_STOP", expected, {"stop_id": "S_CUMBERLAND"}, "s", "s", "test"),
        ],
        GTFS,
    )

    parsed = parse_operational_transcript(
        "Wait, garde Cumberland. Make it 10.",
        GTFS,
        state,
    )

    assert parsed.operations == ["KEEP=Cumberland", "END=10"]
    assert parsed.unresolved_cues == ()
