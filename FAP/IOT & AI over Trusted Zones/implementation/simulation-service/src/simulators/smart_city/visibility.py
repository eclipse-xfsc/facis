"""
City visibility and sunrise/sunset simulator.

Generates fog index, visibility classification, and daily sunrise/sunset times.
"""

from __future__ import annotations

import math
from datetime import datetime, timezone

from src.core.random_generator import DeterministicRNG
from src.core.time_series import BaseTimeSeriesGenerator, IntervalMinutes
from src.models.smart_city.visibility import VisibilityLevel, VisibilityReading


def _calculate_sun_times(date: datetime, latitude: float, longitude: float) -> tuple[str, str]:
    """
    Calculate approximate sunrise and sunset times.

    Uses a simplified equation of time approach.

    Args:
        date: The date for calculation.
        latitude: Location latitude in degrees.
        longitude: Location longitude in degrees.

    Returns:
        Tuple of (sunrise_time, sunset_time) as "HH:MM" strings in UTC.
    """
    day_of_year = date.timetuple().tm_yday

    # Solar declination (simplified)
    declination = 23.45 * math.sin(math.radians(360 / 365 * (day_of_year - 81)))
    declination_rad = math.radians(declination)
    latitude_rad = math.radians(latitude)

    # Hour angle at sunrise/sunset
    cos_hour_angle = -math.tan(latitude_rad) * math.tan(declination_rad)
    cos_hour_angle = max(-1.0, min(1.0, cos_hour_angle))  # Clamp for polar regions
    hour_angle = math.degrees(math.acos(cos_hour_angle))

    # Solar noon (approximate, based on longitude offset from UTC)
    solar_noon_hours = 12.0 - longitude / 15.0

    sunrise_hours = solar_noon_hours - hour_angle / 15.0
    sunset_hours = solar_noon_hours + hour_angle / 15.0

    # Clamp to valid range
    sunrise_hours = max(0.0, min(23.99, sunrise_hours))
    sunset_hours = max(0.0, min(23.99, sunset_hours))

    sunrise_h = int(sunrise_hours)
    sunrise_m = int((sunrise_hours - sunrise_h) * 60)
    sunset_h = int(sunset_hours)
    sunset_m = int((sunset_hours - sunset_h) * 60)

    return f"{sunrise_h:02d}:{sunrise_m:02d}", f"{sunset_h:02d}:{sunset_m:02d}"


def _fog_index_from_time(hour: float) -> float:
    """
    Calculate base fog index from time of day.

    Fog is highest at dawn (05-08), clears by midday, builds again at dusk.

    Args:
        hour: Hour of day as float (e.g., 6.5 = 06:30).

    Returns:
        Base fog index (0-100).
    """
    if 4.0 <= hour < 8.0:
        # Peak fog at dawn (~06:00)
        peak_factor = 1.0 - abs(hour - 6.0) / 2.0
        return 50.0 * max(0.0, peak_factor)
    elif 8.0 <= hour < 14.0:
        # Clearing through morning
        return max(0.0, 25.0 * (1.0 - (hour - 8.0) / 6.0))
    elif 20.0 <= hour < 24.0:
        # Building at dusk
        return 15.0 * ((hour - 20.0) / 4.0)
    elif 0.0 <= hour < 4.0:
        # Night fog
        return 20.0
    else:
        # Afternoon - minimal
        return 5.0


def _classify_visibility(fog_index: float) -> VisibilityLevel:
    """Classify visibility from fog index."""
    if fog_index < 30.0:
        return VisibilityLevel.GOOD
    elif fog_index < 60.0:
        return VisibilityLevel.MEDIUM
    else:
        return VisibilityLevel.POOR


class VisibilitySimulator(BaseTimeSeriesGenerator[VisibilityReading]):
    """
    City visibility and sun times simulator.

    Generates:
    - Fog index with daily cycle (peak at dawn)
    - Visibility classification (good/medium/poor)
    - Sunrise/sunset times calculated from latitude and date
    """

    def __init__(
        self,
        entity_id: str,
        rng: DeterministicRNG,
        interval: IntervalMinutes = IntervalMinutes.FIFTEEN_MINUTES,
        city_id: str = "city-berlin",
        latitude: float = 52.52,
        longitude: float = 13.405,
    ) -> None:
        super().__init__(entity_id, rng, interval)
        self._city_id = city_id
        self._latitude = latitude
        self._longitude = longitude

    def generate_value(self, timestamp: datetime) -> VisibilityReading:
        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=timezone.utc)

        ts_ms = int(timestamp.timestamp() * 1000)
        ts_rng = self._rng.get_timestamp_rng(self._entity_id, ts_ms)

        hour = timestamp.hour + timestamp.minute / 60.0

        # Base fog index from time of day
        base_fog = _fog_index_from_time(hour)

        # Add random variance
        variance = float(ts_rng.uniform(-10.0, 10.0))
        fog_index = max(0.0, min(100.0, base_fog + variance))

        visibility = _classify_visibility(fog_index)

        sunrise, sunset = _calculate_sun_times(timestamp, self._latitude, self._longitude)

        return VisibilityReading(
            city_id=self._city_id,
            timestamp=timestamp,
            fog_index=fog_index,
            visibility=visibility,
            sunrise_time=sunrise,
            sunset_time=sunset,
        )
