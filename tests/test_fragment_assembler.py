from pathlib import Path

from errata.gtfs import GTFSIndex
from errata.live.fragment_assembler import RepairFragmentAssembler
from errata.models import Operation, ServiceChange
from errata.reducer import Reducer


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "fixtures" / "gtfs_static"


def _seed_changed_state():
    gtfs = GTFSIndex(FIXTURE)
    state = ServiceChange("ERR-FRAG")
    reducer = Reducer()
    expected = state.state_hash
    ops = [
        Operation("s1", "SET_ROUTE", expected, {"route_id": "R55"}, "seed", "seed", "test"),
        Operation("s2", "SET_DIRECTION", expected, {"direction_id": 1}, "seed", "seed", "test"),
        Operation("s3", "SET_SERVICE_DATE", expected, {"service_date": "20260929"}, "seed", "seed", "test"),
        Operation("s4", "SET_TIME_WINDOW", expected, {"start_time": "09:00:00", "end_time": "09:30:00"}, "seed", "seed", "test"),
        Operation("s5", "ADD_SKIP_STOP", expected, {"stop_id": "S_KING_EDWARD"}, "seed", "seed", "test"),
        Operation("s6", "ADD_SKIP_STOP", expected, {"stop_id": "S_CUMBERLAND"}, "seed", "seed", "test"),
    ]
    reducer.apply_batch(state, ops, gtfs)
    return gtfs, state


def test_fragmented_keep_correction_is_recovered_conservatively():
    gtfs, state = _seed_changed_state()
    assembler = RepairFragmentAssembler()
    assembler.add("u1", "Wait.")
    assembler.add("u2", "Keep.")
    assembler.add("u3", "Cumberland, make it 10.")

    assert assembler.correction_operations(state, gtfs) == [
        "KEEP=Cumberland",
        "END=10",
    ]


def test_misheard_skip_fragment_never_becomes_fallback_skip():
    gtfs, state = _seed_changed_state()
    assembler = RepairFragmentAssembler()
    assembler.add("u1", "Wait, skip.")
    assembler.add("u2", "Cumberland, make it 10.")

    # We may recover the explicit time correction, but we intentionally refuse
    # to infer a SKIP operation from fragmented fallback context.
    assert assembler.correction_operations(state, gtfs) == ["END=10"]


def test_no_keep_target_means_no_keep_operation():
    gtfs, state = _seed_changed_state()
    assembler = RepairFragmentAssembler()
    assembler.add("u1", "Keep.")
    assembler.add("u2", "Something else.")

    assert assembler.correction_operations(state, gtfs) == []
