from pathlib import Path
import csv

from errata.consequence import compute
from errata.gtfs import GTFSIndex
from errata.live.controlled_parser import parse_operational_transcript
from errata.live.coordinator import LiveTransactionCoordinator
from errata.live.direct_entry import apply_direct_text
from errata.models import Operation, ServiceChange
from errata.reducer import Reducer


ROOT = Path(__file__).resolve().parents[1]


def _write_csv(path: Path, fieldnames, rows):
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def test_standard_gtfs_without_stop_sequence_and_calendar_filter(tmp_path):
    _write_csv(
        tmp_path / "routes.txt",
        ["route_id", "route_short_name", "route_long_name"],
        [{"route_id": "R9", "route_short_name": "9", "route_long_name": "Public Route"}],
    )
    _write_csv(
        tmp_path / "stops.txt",
        ["stop_id", "stop_name", "stop_lat", "stop_lon"],
        [
            {"stop_id": "A", "stop_name": "Alpha", "stop_lat": "45.1", "stop_lon": "-75.1"},
            {"stop_id": "B", "stop_name": "Bravo", "stop_lat": "45.2", "stop_lon": "-75.2"},
            {"stop_id": "C", "stop_name": "Charlie", "stop_lat": "45.3", "stop_lon": "-75.3"},
        ],
    )
    _write_csv(
        tmp_path / "trips.txt",
        ["route_id", "service_id", "trip_id", "direction_id"],
        [
            {"route_id": "R9", "service_id": "WKD", "trip_id": "T1", "direction_id": "1"},
            {"route_id": "R9", "service_id": "SAT", "trip_id": "T2", "direction_id": "1"},
        ],
    )
    _write_csv(
        tmp_path / "stop_times.txt",
        ["trip_id", "arrival_time", "departure_time", "stop_id", "stop_sequence"],
        [
            {"trip_id": "T1", "arrival_time": "09:00:00", "departure_time": "09:00:00", "stop_id": "A", "stop_sequence": "1"},
            {"trip_id": "T1", "arrival_time": "09:05:00", "departure_time": "09:05:00", "stop_id": "B", "stop_sequence": "2"},
            {"trip_id": "T1", "arrival_time": "09:10:00", "departure_time": "09:10:00", "stop_id": "C", "stop_sequence": "3"},
            {"trip_id": "T2", "arrival_time": "09:10:00", "departure_time": "09:10:00", "stop_id": "A", "stop_sequence": "1"},
        ],
    )
    _write_csv(
        tmp_path / "calendar.txt",
        ["service_id", "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday", "start_date", "end_date"],
        [
            {"service_id": "WKD", "monday": "1", "tuesday": "1", "wednesday": "1", "thursday": "1", "friday": "1", "saturday": "0", "sunday": "0", "start_date": "20260901", "end_date": "20261031"},
            {"service_id": "SAT", "monday": "0", "tuesday": "0", "wednesday": "0", "thursday": "0", "friday": "0", "saturday": "1", "sunday": "0", "start_date": "20260901", "end_date": "20261031"},
        ],
    )

    gtfs = GTFSIndex(tmp_path)
    assert gtfs.stop_by_id["A"].stop_sequence is None
    assert gtfs.service_active("WKD", "20260930") is True
    assert gtfs.service_active("SAT", "20260930") is False
    assert gtfs.affected_trips("R9", 1, 8 * 3600, 10 * 3600, "20260930") == ["T1"]


def test_explicit_direction_id_wording_uses_shared_core():
    gtfs = GTFSIndex(ROOT / "fixtures" / "gtfs_static")
    state = ServiceChange("ERR-DIRECTION-ID")
    reducer = Reducer()
    expected = state.state_hash
    reducer.apply_batch(
        state,
        [
            Operation("sd", "SET_SERVICE_DATE", expected, {"service_date": "20260929"}, "s", "s", "test"),
            Operation("st", "SET_TIME_WINDOW", expected, {"start_time": "09:00:00"}, "s", "s", "test"),
        ],
        gtfs,
    )
    coord = LiveTransactionCoordinator(state, reducer, gtfs)

    parsed = parse_operational_transcript(
        "Route 55 direction 1, skip King Edward and Cumberland until 9:30.",
        gtfs,
        state,
    )
    assert "DIRECTION=1" in parsed.operations

    result = apply_direct_text(
        coord,
        label="public-safe-direction",
        text="Route 55 direction 1, skip King Edward and Cumberland until 9:30.",
        entry_elapsed_ms=0.0,
        call_id="dir-id",
    )
    assert result.result[0]["status"] == "APPLIED"
    impact = compute(state, gtfs)
    assert impact["affected_trip_count"] == 2
