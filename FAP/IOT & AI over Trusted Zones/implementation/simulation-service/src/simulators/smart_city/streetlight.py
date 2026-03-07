"""
Streetlight simulator.

Generates dimming levels and power based on time of day, sunrise/sunset,
and active city events in the same zone.
"""

from __future__ import annotations

import math
from datetime import datetime, timezone
from typing import TYPE_CHECKING

from src.core.random_generator import DeterministicRNG
from src.core.time_series import BaseTimeSeriesGenerator, IntervalMinutes
from src.models.smart_city.streetlight import StreetlightConfig, StreetlightReading
from src.simulators.smart_city.visibility import _calculate_sun_times

if TYPE_CHECKING:
    from src.models.smart_city.event import CityEventReading


def _base_dimming(hour: float, sunrise_hour: float, sunset_hour: float) -> float:
    """
    Calculate base dimming level from time of day and sun position.

    Returns dimming percentage (0=off, 100=full brightness).

    Schedule:
    - Full dark (night): 100%
    - Dawn transition: ramp down from 100% to 0%
    - Daylight: 0%
    - Dusk transition: ramp up from 0% to 100%

    Transitions are ~1 hour around sunrise/sunset.
    """
    dawn_start = sunrise_hour - 0.5
    dawn_end = sunrise_hour + 0.5
    dusk_start = sunset_hour - 0.5
    dusk_end = sunset_hour + 0.5

    if hour < dawn_start or hour >= dusk_end:
        # Full night
        return 100.0
    elif dawn_start <= hour < dawn_end:
        # Dawn transition: 100% → 0%
        progress = (hour - dawn_start) / (dawn_end - dawn_start)
        return 100.0 * (1.0 - progress)
    elif dawn_end <= hour < dusk_start:
        # Daylight
        return 0.0
    elif dusk_start <= hour < dusk_end:
        # Dusk transition: 0% → 100%
        progress = (hour - dusk_start) / (dusk_end - dusk_start)
        return 100.0 * progress
    else:
        return 0.0


class StreetlightSimulator(BaseTimeSeriesGenerator[StreetlightReading]):
    """
    Streetlight simulator with event-reactive dimming.

    Generates:
    - Dimming based on sunrise/sunset schedule
    - Boosted dimming during active events in the same zone
    - Power calculated from dimming level and rated power

    Event reaction:
    - Severity 2: +30% dimming increase (capped at 100%)
    - Severity 3: +50% dimming increase (capped at 100%)
    """

    def __init__(
        self,
        entity_id: str,
        rng: DeterministicRNG,
        interval: IntervalMinutes = IntervalMinutes.FIFTEEN_MINUTES,
        config: StreetlightConfig | None = None,
        city_id: str = "city-berlin",
        site_id: str = "",
        latitude: float = 52.52,
        longitude: float = 13.405,
    ) -> None:
        super().__init__(entity_id, rng, interval)

        if config is None:
            config = StreetlightConfig(light_id=entity_id, zone_id="zone-001")
        self._config = config
        self._city_id = city_id
        self._site_id = site_id
        self._latitude = latitude
        self._longitude = longitude

        # Active event for this zone (set externally by correlation engine)
        self._active_event: CityEventReading | None = None

    def set_active_event(self, event: CityEventReading | None) -> None:
        """Set the current active event for this light's zone."""
        self._active_event = event

    def generate_value(self, timestamp: datetime) -> StreetlightReading:
        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=timezone.utc)

        ts_ms = int(timestamp.timestamp() * 1000)
        ts_rng = self._rng.get_timestamp_rng(self._entity_id, ts_ms)

        # Calculate sunrise/sunset for this day
        sunrise_str, sunset_str = _calculate_sun_times(timestamp, self._latitude, self._longitude)
        sunrise_parts = sunrise_str.split(":")
        sunset_parts = sunset_str.split(":")
        sunrise_hour = int(sunrise_parts[0]) + int(sunrise_parts[1]) / 60.0
        sunset_hour = int(sunset_parts[0]) + int(sunset_parts[1]) / 60.0

        hour = timestamp.hour + timestamp.minute / 60.0

        # Base dimming from schedule
        dimming = _base_dimming(hour, sunrise_hour, sunset_hour)

        # Add small random variance (±3%)
        variance = float(ts_rng.uniform(-3.0, 3.0))
        dimming = max(0.0, min(100.0, dimming + variance))

        # Event-reactive boost
        if self._active_event is not None and self._active_event.active:
            if self._active_event.zone_id == self._config.zone_id:
                severity = self._active_event.severity.value
                if severity >= 3:
                    boost = 50.0
                elif severity >= 2:
                    boost = 30.0
                else:
                    boost = 0.0

                dimming = min(100.0, dimming + boost)

        # Calculate power from dimming
        power_w = (dimming / 100.0) * self._config.rated_power_w

        return StreetlightReading(
            site_id=self._site_id,
            city_id=self._city_id,
            zone_id=self._config.zone_id,
            light_id=self._config.light_id,
            timestamp=timestamp,
            dimming_level_pct=dimming,
            power_w=power_w,
        )
