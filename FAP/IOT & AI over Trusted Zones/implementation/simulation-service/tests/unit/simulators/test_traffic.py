"""Tests for traffic simulator."""

import json
from datetime import datetime, timezone

import pytest

from src.core.random_generator import DeterministicRNG
from src.core.time_series import IntervalMinutes
from src.models.smart_city.traffic import TrafficReading
from src.simulators.smart_city.traffic import TrafficSimulator, _base_traffic_index


class TestRushHourPeaks:
    """Tests for rush hour traffic patterns."""

    def test_morning_rush_hour_high(self) -> None:
        """Test traffic index is high during morning rush (07-09)."""
        rng = DeterministicRNG(seed=12345)
        sim = TrafficSimulator("traffic-001", rng, zone_id="zone-001")

        # Wednesday (weekday) at 08:00
        ts = datetime(2024, 6, 12, 8, 0, 0, tzinfo=timezone.utc)
        reading = sim.generate_at(ts).value

        assert 60.0 <= reading.traffic_index <= 100.0

    def test_evening_rush_hour_high(self) -> None:
        """Test traffic index is high during evening rush (17-19)."""
        rng = DeterministicRNG(seed=12345)
        sim = TrafficSimulator("traffic-001", rng, zone_id="zone-001")

        # Wednesday (weekday) at 18:00
        ts = datetime(2024, 6, 12, 18, 0, 0, tzinfo=timezone.utc)
        reading = sim.generate_at(ts).value

        assert 60.0 <= reading.traffic_index <= 100.0

    def test_base_traffic_morning_rush(self) -> None:
        """Test base traffic index for morning rush peak at 08:00."""
        index = _base_traffic_index(8.0, is_weekend=False)
        assert 60.0 <= index <= 90.0

    def test_base_traffic_evening_rush(self) -> None:
        """Test base traffic index for evening rush peak at 18:00."""
        index = _base_traffic_index(18.0, is_weekend=False)
        assert 60.0 <= index <= 90.0


class TestNightLow:
    """Tests for low traffic at night."""

    def test_night_traffic_low_midnight(self) -> None:
        """Test traffic index is low at midnight (00:00)."""
        rng = DeterministicRNG(seed=12345)
        sim = TrafficSimulator("traffic-001", rng, zone_id="zone-001")

        # Wednesday at midnight
        ts = datetime(2024, 6, 12, 0, 0, 0, tzinfo=timezone.utc)
        reading = sim.generate_at(ts).value

        assert reading.traffic_index <= 25.0

    def test_night_traffic_low_3am(self) -> None:
        """Test traffic index is low at 03:00."""
        rng = DeterministicRNG(seed=12345)
        sim = TrafficSimulator("traffic-001", rng, zone_id="zone-001")

        ts = datetime(2024, 6, 12, 3, 0, 0, tzinfo=timezone.utc)
        reading = sim.generate_at(ts).value

        assert reading.traffic_index <= 25.0

    def test_base_traffic_night_hours(self) -> None:
        """Test base traffic index is 5-15 during night (23-05)."""
        for hour in [0.0, 1.0, 2.0, 3.0, 4.0, 23.5]:
            index = _base_traffic_index(hour, is_weekend=False)
            assert 5.0 <= index <= 25.0, f"Hour {hour}: index={index}"


class TestWeekendReduction:
    """Tests for weekend traffic reduction."""

    def test_weekend_lower_than_weekday_rush(self) -> None:
        """Test weekend traffic is lower than weekday during rush hour."""
        rng_weekday = DeterministicRNG(seed=12345)
        sim_weekday = TrafficSimulator("traffic-001", rng_weekday, zone_id="zone-001")

        rng_weekend = DeterministicRNG(seed=12345)
        sim_weekend = TrafficSimulator("traffic-001", rng_weekend, zone_id="zone-001")

        # Wednesday 08:00 (weekday)
        ts_weekday = datetime(2024, 6, 12, 8, 0, 0, tzinfo=timezone.utc)
        reading_weekday = sim_weekday.generate_at(ts_weekday).value

        # Saturday 08:00 (weekend)
        ts_weekend = datetime(2024, 6, 15, 8, 0, 0, tzinfo=timezone.utc)
        reading_weekend = sim_weekend.generate_at(ts_weekend).value

        assert reading_weekend.traffic_index < reading_weekday.traffic_index

    def test_base_traffic_weekend_reduction(self) -> None:
        """Test base traffic index has ~30% weekend reduction."""
        weekday_index = _base_traffic_index(8.0, is_weekend=False)
        weekend_index = _base_traffic_index(8.0, is_weekend=True)

        expected_weekend = weekday_index * 0.7
        assert abs(weekend_index - expected_weekend) < 0.1

    def test_weekend_detection_saturday(self) -> None:
        """Test Saturday is detected as weekend (weekday() >= 5)."""
        saturday = datetime(2024, 6, 15, 8, 0, 0, tzinfo=timezone.utc)
        assert saturday.weekday() >= 5

    def test_weekend_detection_sunday(self) -> None:
        """Test Sunday is detected as weekend."""
        sunday = datetime(2024, 6, 16, 8, 0, 0, tzinfo=timezone.utc)
        assert sunday.weekday() >= 5


class TestTrafficDeterminism:
    """Tests for deterministic behavior."""

    def test_same_seed_produces_identical_readings(self) -> None:
        """Test that same seed produces identical traffic readings."""
        ts = datetime(2024, 6, 15, 8, 0, 0, tzinfo=timezone.utc)

        results = []
        for _ in range(5):
            rng = DeterministicRNG(seed=42)
            sim = TrafficSimulator("traffic-001", rng)
            reading = sim.generate_at(ts).value
            results.append(reading.traffic_index)

        assert all(r == results[0] for r in results)

    def test_different_seeds_produce_different_readings(self) -> None:
        """Test that different seeds produce different readings."""
        ts = datetime(2024, 6, 15, 8, 0, 0, tzinfo=timezone.utc)

        rng1 = DeterministicRNG(seed=111)
        sim1 = TrafficSimulator("traffic-001", rng1)
        reading1 = sim1.generate_at(ts).value

        rng2 = DeterministicRNG(seed=222)
        sim2 = TrafficSimulator("traffic-001", rng2)
        reading2 = sim2.generate_at(ts).value

        assert reading1.traffic_index != reading2.traffic_index

    def test_different_entities_produce_different_readings(self) -> None:
        """Test that different entity IDs produce different readings."""
        ts = datetime(2024, 6, 15, 8, 0, 0, tzinfo=timezone.utc)
        rng = DeterministicRNG(seed=12345)

        sim1 = TrafficSimulator("traffic-001", rng)
        sim2 = TrafficSimulator("traffic-002", rng)

        reading1 = sim1.generate_at(ts).value
        reading2 = sim2.generate_at(ts).value

        assert reading1.traffic_index != reading2.traffic_index


class TestTrafficJSONPayload:
    """Tests for JSON payload format."""

    def test_json_payload_has_type_traffic(self) -> None:
        """Test JSON payload has type='traffic'."""
        rng = DeterministicRNG(seed=12345)
        sim = TrafficSimulator("traffic-001", rng)

        ts = datetime(2024, 6, 15, 12, 0, 0, tzinfo=timezone.utc)
        reading = sim.generate_at(ts).value
        payload = reading.to_json_payload()

        assert payload["type"] == "traffic"

    def test_json_payload_structure(self) -> None:
        """Test JSON payload contains all required fields."""
        rng = DeterministicRNG(seed=12345)
        sim = TrafficSimulator("traffic-001", rng)

        ts = datetime(2024, 6, 15, 12, 0, 0, tzinfo=timezone.utc)
        reading = sim.generate_at(ts).value
        payload = reading.to_json_payload()

        required_fields = [
            "type",
            "schema_version",
            "city_id",
            "zone_id",
            "timestamp",
            "traffic_index",
        ]
        for field in required_fields:
            assert field in payload

    def test_json_serialization(self) -> None:
        """Test payload can be serialized to valid JSON."""
        rng = DeterministicRNG(seed=12345)
        sim = TrafficSimulator("traffic-001", rng)

        ts = datetime(2024, 6, 15, 12, 0, 0, tzinfo=timezone.utc)
        reading = sim.generate_at(ts).value
        payload = reading.to_json_payload()

        json_str = json.dumps(payload, indent=2)
        parsed = json.loads(json_str)
        assert parsed == payload

    def test_json_timestamp_format(self) -> None:
        """Test timestamp is in ISO 8601 with Z suffix."""
        rng = DeterministicRNG(seed=12345)
        sim = TrafficSimulator("traffic-001", rng)

        ts = datetime(2024, 6, 15, 12, 0, 0, tzinfo=timezone.utc)
        reading = sim.generate_at(ts).value
        payload = reading.to_json_payload()

        assert payload["timestamp"].endswith("Z")

    def test_traffic_index_in_valid_range(self) -> None:
        """Test traffic index is always in 0-100 range across a full day."""
        rng = DeterministicRNG(seed=12345)
        sim = TrafficSimulator("traffic-001", rng)

        for hour in range(24):
            ts = datetime(2024, 6, 15, hour, 0, 0, tzinfo=timezone.utc)
            reading = sim.generate_at(ts).value
            assert 0.0 <= reading.traffic_index <= 100.0
