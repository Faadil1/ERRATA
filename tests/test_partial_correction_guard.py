from pathlib import Path

from errata.gtfs import GTFSIndex
from errata.live.controlled_parser import parse_operational_transcript
from errata.models import Operation, ServiceChange
from errata.reducer import Reducer

ROOT = Path(__file__).resolve().parents[1]
GTFS = GTFSIndex(ROOT / "fixtures" / "gtfs_static")


def seeded_state():
    state = ServiceChange("ERR-PARTIAL-GUARD")
    reducer = Reducer()
    expected = state.state_hash
    reducer.apply_batch(
        state,
        [
            Operation("r", "SET_ROUTE", expected, {"route_id": "R55"}, "t", "t", "test"),
            Operation("d", "SET_DIRECTION", expected, {"direction_id": 1}, "t", "t", "test"),
            Operation("sd", "SET_SERVICE_DATE", expected, {"service_date": "20260929"}, "t", "t", "test"),
            Operation("tw", "SET_TIME_WINDOW", expected, {"start_time": "09:00:00", "end_time": "09:30:00"}, "t", "t", "test"),
            Operation("k", "ADD_SKIP_STOP", expected, {"stop_id": "S_KING_EDWARD"}, "t", "t", "test"),
            Operation("c", "ADD_SKIP_STOP", expected, {"stop_id": "S_CUMBERLAND"}, "t", "t", "test"),
        ],
        GTFS,
    )
    return state


def test_partial_time_correction_is_not_complete():
    parsed = parse_operational_transcript(
        "Wait, keep Cumberland, make it turn.",
        GTFS,
        seeded_state(),
    )
    assert parsed.operations == ["KEEP=Cumberland"]
    assert parsed.unresolved_cues == ("END_TIME_AFTER_MAKE_IT",)


def test_repeated_keep_is_deduplicated():
    parsed = parse_operational_transcript(
        "Wait, keep Cumberland, make it turn. Wait, keep. Cumberland. "
        "Wait, keep Cumberland, make it 10.",
        GTFS,
        seeded_state(),
    )
    assert parsed.operations == ["KEEP=Cumberland", "END=10"]
    assert parsed.unresolved_cues == ()


def test_ouest_maps_to_west():
    parsed = parse_operational_transcript(
        "Route 55 ouest, skip King Edward and Cumberland until 9:30.",
        GTFS,
        ServiceChange("ERR-OUEST"),
    )
    assert "DIRECTION=west" in parsed.operations
    assert parsed.unresolved_cues == ()


def test_u_turn_mishearing_is_review_only():
    parsed = parse_operational_transcript(
        "Wait, keep Cumberland, make U-turn.",
        GTFS,
        seeded_state(),
    )
    assert parsed.operations == ["KEEP=Cumberland"]
    assert parsed.unresolved_cues == ("UNRESOLVED_MAKE_CUE",)


def test_unbound_numeric_time_after_keep_is_review_only():
    parsed = parse_operational_transcript(
        "We will keep Cumberland, McKitten. Wait, keep Cumberland, McKitten 10.",
        GTFS,
        seeded_state(),
    )
    assert parsed.operations == ["KEEP=Cumberland"]
    assert "UNBOUND_TIME_VALUE" in parsed.unresolved_cues


def test_unbound_word_time_after_keep_is_review_only():
    parsed = parse_operational_transcript(
        "Wait, keep Cumberland, ten.",
        GTFS,
        seeded_state(),
    )
    assert parsed.operations == ["KEEP=Cumberland"]
    assert "UNBOUND_TIME_VALUE" in parsed.unresolved_cues


def test_explicit_direction_id_is_bounded():
    parsed = parse_operational_transcript(
        "Route 55 direction one, skip King Edward until 9:30.",
        GTFS,
        ServiceChange("ERR-DIRECTION-ID"),
    )
    assert "DIRECTION=1" in parsed.operations
    assert "SKIP=King Edward" in parsed.operations
