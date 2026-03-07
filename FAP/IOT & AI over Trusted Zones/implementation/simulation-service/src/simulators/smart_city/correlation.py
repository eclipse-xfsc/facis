"""
Smart City correlation engine.

Synchronizes all Smart City feeds and implements event→dimming correlation.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING

from pydantic import BaseModel, Field

from src.models.smart_city.event import CityEventReading
from src.models.smart_city.streetlight import StreetlightReading
from src.models.smart_city.traffic import TrafficReading
from src.models.smart_city.visibility import VisibilityReading

if TYPE_CHECKING:
    from collections.abc import Iterator

    from src.simulators.smart_city.event import CityEventSimulator
    from src.simulators.smart_city.streetlight import StreetlightSimulator
    from src.simulators.smart_city.traffic import TrafficSimulator
    from src.simulators.smart_city.visibility import VisibilitySimulator


class SmartCitySnapshot(BaseModel):
    """Synchronized snapshot of all Smart City feeds at a single timestamp."""

    timestamp: datetime = Field(..., description="Synchronized timestamp")
    city_id: str = Field(default="", description="City identifier")

    streetlights: list[StreetlightReading] = Field(default_factory=list)
    traffic_readings: list[TrafficReading] = Field(default_factory=list)
    events: list[CityEventReading] = Field(default_factory=list)
    visibility: VisibilityReading | None = Field(default=None)

    def to_json_payload(self) -> dict:
        """Convert to JSON payload."""
        return {
            "timestamp": self.timestamp.isoformat().replace("+00:00", "Z"),
            "city_id": self.city_id,
            "streetlights": [s.to_json_payload() for s in self.streetlights],
            "traffic_readings": [t.to_json_payload() for t in self.traffic_readings],
            "events": [e.to_json_payload() for e in self.events],
            "visibility": self.visibility.to_json_payload() if self.visibility else None,
        }


class SmartCityCorrelationEngine:
    """
    Engine that synchronizes all Smart City feeds with event→dimming correlation.

    Dependency ordering:
    1. Events generated first (needed by streetlights)
    2. Events passed to streetlight simulators for reactive dimming
    3. Traffic and visibility generated independently
    """

    def __init__(
        self,
        event_simulators: list[CityEventSimulator] | None = None,
        streetlight_simulators: list[StreetlightSimulator] | None = None,
        traffic_simulators: list[TrafficSimulator] | None = None,
        visibility_simulator: VisibilitySimulator | None = None,
        city_id: str = "city-berlin",
        interval_minutes: int = 1,
    ) -> None:
        self._event_simulators = event_simulators or []
        self._streetlight_simulators = streetlight_simulators or []
        self._traffic_simulators = traffic_simulators or []
        self._visibility_simulator = visibility_simulator
        self._city_id = city_id
        self._interval_minutes = interval_minutes

    def generate_snapshot(self, timestamp: datetime) -> SmartCitySnapshot:
        """
        Generate a correlated Smart City snapshot.

        Order:
        1. Generate events (needed by streetlights)
        2. Pass active events to streetlights, then generate
        3. Generate traffic and visibility independently
        """
        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=UTC)

        # Step 1: Generate events first
        events: list[CityEventReading] = []
        active_events_by_zone: dict[str, CityEventReading] = {}

        for event_sim in self._event_simulators:
            event_point = event_sim.generate_at(timestamp)
            event = event_point.value
            events.append(event)
            if event.active:
                active_events_by_zone[event.zone_id] = event

        # Step 2: Set active events on streetlights, then generate
        streetlights: list[StreetlightReading] = []
        for light_sim in self._streetlight_simulators:
            zone_id = light_sim._config.zone_id
            active_event = active_events_by_zone.get(zone_id)
            light_sim.set_active_event(active_event)

            light_point = light_sim.generate_at(timestamp)
            streetlights.append(light_point.value)

        # Step 3: Generate traffic
        traffic_readings: list[TrafficReading] = []
        for traffic_sim in self._traffic_simulators:
            traffic_point = traffic_sim.generate_at(timestamp)
            traffic_readings.append(traffic_point.value)

        # Step 4: Generate visibility
        visibility = None
        if self._visibility_simulator is not None:
            vis_point = self._visibility_simulator.generate_at(timestamp)
            visibility = vis_point.value

        return SmartCitySnapshot(
            timestamp=timestamp,
            city_id=self._city_id,
            streetlights=streetlights,
            traffic_readings=traffic_readings,
            events=events,
            visibility=visibility,
        )

    def generate_range(self, start: datetime, end: datetime) -> list[SmartCitySnapshot]:
        """Generate snapshots for a time range."""
        return list(self.iterate_range(start, end))

    def iterate_range(self, start: datetime, end: datetime) -> Iterator[SmartCitySnapshot]:
        """Iterate over snapshots for a time range."""
        if start.tzinfo is None:
            start = start.replace(tzinfo=UTC)
        if end.tzinfo is None:
            end = end.replace(tzinfo=UTC)

        current = start
        delta = timedelta(minutes=self._interval_minutes)

        while current <= end:
            yield self.generate_snapshot(current)
            current += delta
