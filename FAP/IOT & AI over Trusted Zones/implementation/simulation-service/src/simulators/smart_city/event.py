"""
City event simulator.

Generates deterministic city events (accidents, emergencies, public events).
Events are probabilistic but seeded for reproducibility.
"""

from __future__ import annotations

from datetime import datetime, timezone

from src.core.random_generator import DeterministicRNG
from src.core.time_series import BaseTimeSeriesGenerator, IntervalMinutes
from src.models.smart_city.event import CityEventReading, EventType, Severity

# Pre-defined event slots for deterministic generation.
# Each slot defines: (hour, duration_minutes, event_type, severity)
_NORMAL_DAY_EVENTS: list[tuple[int, int, EventType, Severity]] = []

_EVENT_DAY_EVENTS: list[tuple[int, int, EventType, Severity]] = [
    (9, 30, EventType.ACCIDENT, Severity.MEDIUM),
    (14, 45, EventType.EMERGENCY, Severity.HIGH),
    (20, 20, EventType.EVENT, Severity.LOW),
]


class CityEventSimulator(BaseTimeSeriesGenerator[CityEventReading]):
    """
    City event simulator.

    In normal mode: no events (all readings have active=False).
    In event mode: 2-3 pre-defined events at deterministic times.

    Events are determined by seed and day, ensuring reproducibility.
    Duration is checked per-timestamp to set active=True/False.
    """

    def __init__(
        self,
        entity_id: str,
        rng: DeterministicRNG,
        interval: IntervalMinutes = IntervalMinutes.FIFTEEN_MINUTES,
        city_id: str = "city-berlin",
        zone_id: str = "zone-001",
        mode: str = "normal",
    ) -> None:
        super().__init__(entity_id, rng, interval)
        self._city_id = city_id
        self._zone_id = zone_id
        self._mode = mode

    def _get_events_for_day(
        self, timestamp: datetime
    ) -> list[tuple[int, int, EventType, Severity]]:
        """Get the event schedule for a given day."""
        if self._mode != "event":
            return _NORMAL_DAY_EVENTS

        # Use seed + day to deterministically vary event times slightly
        day_seed = int(timestamp.date().toordinal())
        ts_rng = self._rng.get_timestamp_rng(self._entity_id, day_seed)

        events = []
        for base_hour, duration, event_type, severity in _EVENT_DAY_EVENTS:
            # Add ±1 hour jitter based on seed
            jitter = int(ts_rng.uniform(-1, 2))
            hour = max(0, min(23, base_hour + jitter))
            events.append((hour, duration, event_type, severity))

        return events

    def generate_value(self, timestamp: datetime) -> CityEventReading:
        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=timezone.utc)

        events = self._get_events_for_day(timestamp)
        current_minute_of_day = timestamp.hour * 60 + timestamp.minute

        # Check if any event is active at this time
        for event_hour, duration, event_type, severity in events:
            event_start = event_hour * 60
            event_end = event_start + duration

            if event_start <= current_minute_of_day < event_end:
                return CityEventReading(
                    city_id=self._city_id,
                    zone_id=self._zone_id,
                    timestamp=timestamp,
                    event_type=event_type,
                    severity=severity,
                    active=True,
                )

        # No active event — return inactive reading
        return CityEventReading(
            city_id=self._city_id,
            zone_id=self._zone_id,
            timestamp=timestamp,
            event_type=EventType.EVENT,
            severity=Severity.LOW,
            active=False,
        )
