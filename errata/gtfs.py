from __future__ import annotations
import csv
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from difflib import SequenceMatcher


def parse_gtfs_time(value: str) -> int:
    h, m, s = map(int, value.split(":"))
    return h * 3600 + m * 60 + s


@dataclass(frozen=True)
class Stop:
    stop_id: str
    stop_name: str
    # stop_sequence is trip-specific in standard GTFS. This optional field exists
    # only for backward compatibility with the original synthetic fixture.
    stop_sequence: int | None = None


class GTFSIndex:
    def __init__(self, folder: str | Path):
        folder = Path(folder)
        with open(folder / "routes.txt", newline="", encoding="utf-8-sig") as f:
            self.routes = list(csv.DictReader(f))
        with open(folder / "trips.txt", newline="", encoding="utf-8-sig") as f:
            self.trips = list(csv.DictReader(f))
        with open(folder / "stops.txt", newline="", encoding="utf-8-sig") as f:
            rows = list(csv.DictReader(f))
            self.stops = [
                Stop(
                    r["stop_id"],
                    r["stop_name"],
                    int(r["stop_sequence"]) if r.get("stop_sequence") else None,
                )
                for r in rows
            ]
        with open(folder / "stop_times.txt", newline="", encoding="utf-8-sig") as f:
            self.stop_times = list(csv.DictReader(f))

        self.calendar = self._read_optional(folder / "calendar.txt")
        self.calendar_dates = self._read_optional(folder / "calendar_dates.txt")
        self.stop_by_id = {s.stop_id: s for s in self.stops}
        self.route_by_id = {r["route_id"]: r for r in self.routes}

    @staticmethod
    def _read_optional(path: Path) -> list[dict[str, str]]:
        if not path.exists():
            return []
        with open(path, newline="", encoding="utf-8-sig") as f:
            return list(csv.DictReader(f))

    @staticmethod
    def _direction_value(trip: dict[str, str]) -> int | None:
        raw = (trip.get("direction_id") or "").strip()
        if raw not in {"0", "1"}:
            return None
        return int(raw)

    def resolve_route(self, spoken: str) -> str | None:
        norm = spoken.lower().replace("route", "").strip()
        words = {"fifty-five": "55", "fifty five": "55", "five five": "55"}
        norm = words.get(norm, norm)
        hits = [
            r
            for r in self.routes
            if (r.get("route_short_name") or "").lower() == norm
            or r["route_id"].lower() == norm
        ]
        return hits[0]["route_id"] if len(hits) == 1 else None

    def _trip_ids(self, route_id: str, direction_id: int) -> set[str]:
        return {
            t["trip_id"]
            for t in self.trips
            if t["route_id"] == route_id and self._direction_value(t) == direction_id
        }

    def resolve_stop(
        self,
        mention: str,
        route_id: str,
        direction_id: int,
        threshold: float = 0.72,
    ) -> tuple[str | None, list[tuple[str, float]]]:
        trip_ids = self._trip_ids(route_id, direction_id)
        allowed_ids = {
            st["stop_id"] for st in self.stop_times if st["trip_id"] in trip_ids
        }
        m = " ".join(mention.lower().replace("/", " ").split())
        scored = []
        for s in self.stops:
            if s.stop_id not in allowed_ids:
                continue
            n = " ".join(s.stop_name.lower().replace("/", " ").split())
            score = 1.0 if m == n else SequenceMatcher(None, m, n).ratio()
            if m in n or n in m:
                score = max(score, 0.92)
            scored.append((s.stop_id, score))
        scored.sort(key=lambda x: x[1], reverse=True)
        if not scored or scored[0][1] < threshold:
            return None, scored[:3]
        if len(scored) > 1 and scored[1][1] >= scored[0][1] - 0.03:
            return None, scored[:3]
        return scored[0][0], scored[:3]

    def service_active(self, service_id: str, service_date: str) -> bool:
        """Evaluate GTFS calendar/calendar_dates for YYYYMMDD.

        If a fixture provides neither calendar table, preserve the original bounded
        behavior and treat all services as active.
        """
        if not self.calendar and not self.calendar_dates:
            return True

        try:
            date = datetime.strptime(service_date, "%Y%m%d")
        except ValueError:
            return False

        weekday = [
            "monday",
            "tuesday",
            "wednesday",
            "thursday",
            "friday",
            "saturday",
            "sunday",
        ][date.weekday()]

        active = False
        for row in self.calendar:
            if row.get("service_id") != service_id:
                continue
            start = row.get("start_date", "")
            end = row.get("end_date", "")
            if start <= service_date <= end and row.get(weekday) == "1":
                active = True
                break

        for row in self.calendar_dates:
            if row.get("service_id") != service_id:
                continue
            if row.get("date") != service_date:
                continue
            if row.get("exception_type") == "1":
                active = True
            elif row.get("exception_type") == "2":
                active = False

        return active

    def active_trip_ids(
        self, route_id: str, direction_id: int, service_date: str | None = None
    ) -> set[str]:
        candidates = [
            t
            for t in self.trips
            if t["route_id"] == route_id and self._direction_value(t) == direction_id
        ]
        if not service_date:
            return {t["trip_id"] for t in candidates}
        return {
            t["trip_id"]
            for t in candidates
            if self.service_active(t.get("service_id", ""), service_date)
        }

    def affected_trips(
        self,
        route_id: str,
        direction_id: int,
        start_s: int,
        end_s: int,
        service_date: str | None = None,
    ) -> list[str]:
        candidates = self.active_trip_ids(route_id, direction_id, service_date)
        result = []
        by_trip: dict[str, list[dict[str, str]]] = {}
        for row in self.stop_times:
            trip_id = row["trip_id"]
            if trip_id in candidates:
                by_trip.setdefault(trip_id, []).append(row)

        for trip_id in sorted(candidates):
            first = min(
                (
                    parse_gtfs_time(st.get("departure_time") or st.get("arrival_time") or "")
                    for st in by_trip.get(trip_id, [])
                    if (st.get("departure_time") or st.get("arrival_time"))
                ),
                default=None,
            )
            if first is not None and start_s <= first < end_s:
                result.append(trip_id)
        return sorted(result)

    def stop_sequence(self, trip_id: str) -> list[tuple[int, str]]:
        seq = [
            (int(st["stop_sequence"]), st["stop_id"])
            for st in self.stop_times
            if st["trip_id"] == trip_id and st.get("stop_sequence")
        ]
        return sorted(seq)
