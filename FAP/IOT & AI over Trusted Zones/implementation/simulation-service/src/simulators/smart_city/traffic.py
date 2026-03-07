"""
Traffic/movement simulator.

Generates zone-level traffic index with rush hour patterns.
"""

from __future__ import annotations

from datetime import datetime, timezone

from src.core.random_generator import DeterministicRNG
from src.core.time_series import BaseTimeSeriesGenerator, IntervalMinutes
from src.models.smart_city.traffic import TrafficReading


def _base_traffic_index(hour: float, is_weekend: bool) -> float:
    """
    Calculate base traffic index from time of day.

    Weekday pattern:
    - Night (23-05): 5-15
    - Morning rush (07-09): 60-90
    - Midday (10-16): 30-50
    - Evening rush (17-19): 60-90
    - Evening (20-22): 20-35

    Weekend: ~30% reduction.
    """
    if 0.0 <= hour < 5.0:
        index = 10.0
    elif 5.0 <= hour < 7.0:
        # Ramp up to morning rush
        index = 10.0 + 55.0 * ((hour - 5.0) / 2.0)
    elif 7.0 <= hour < 9.0:
        # Morning rush peak
        peak_factor = 1.0 - abs(hour - 8.0)
        index = 65.0 + 20.0 * peak_factor
    elif 9.0 <= hour < 10.0:
        # Post-rush decline
        index = 65.0 - 25.0 * (hour - 9.0)
    elif 10.0 <= hour < 16.0:
        # Midday plateau
        index = 40.0
    elif 16.0 <= hour < 17.0:
        # Ramp up to evening rush
        index = 40.0 + 30.0 * (hour - 16.0)
    elif 17.0 <= hour < 19.0:
        # Evening rush peak
        peak_factor = 1.0 - abs(hour - 18.0)
        index = 70.0 + 15.0 * peak_factor
    elif 19.0 <= hour < 21.0:
        # Post-rush decline
        index = 70.0 - 40.0 * ((hour - 19.0) / 2.0)
    elif 21.0 <= hour < 23.0:
        # Late evening
        index = 30.0 - 15.0 * ((hour - 21.0) / 2.0)
    else:
        # Night
        index = 10.0

    if is_weekend:
        index *= 0.7

    return max(0.0, min(100.0, index))


class TrafficSimulator(BaseTimeSeriesGenerator[TrafficReading]):
    """
    Zone-level traffic simulator.

    Generates traffic index (0-100) with:
    - Rush hour peaks (morning 07-09, evening 17-19)
    - Night lows
    - Weekend reduction (~30%)
    - Random variance per reading
    """

    def __init__(
        self,
        entity_id: str,
        rng: DeterministicRNG,
        interval: IntervalMinutes = IntervalMinutes.FIFTEEN_MINUTES,
        city_id: str = "city-berlin",
        zone_id: str = "zone-001",
    ) -> None:
        super().__init__(entity_id, rng, interval)
        self._city_id = city_id
        self._zone_id = zone_id

    def generate_value(self, timestamp: datetime) -> TrafficReading:
        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=timezone.utc)

        ts_ms = int(timestamp.timestamp() * 1000)
        ts_rng = self._rng.get_timestamp_rng(self._entity_id, ts_ms)

        hour = timestamp.hour + timestamp.minute / 60.0
        is_weekend = timestamp.weekday() >= 5

        base_index = _base_traffic_index(hour, is_weekend)
        variance = float(ts_rng.uniform(-8.0, 8.0))
        traffic_index = max(0.0, min(100.0, base_index + variance))

        return TrafficReading(
            city_id=self._city_id,
            zone_id=self._zone_id,
            timestamp=timestamp,
            traffic_index=traffic_index,
        )
