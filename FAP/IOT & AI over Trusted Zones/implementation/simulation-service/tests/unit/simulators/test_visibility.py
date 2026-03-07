"""Tests for visibility simulator."""

import json
from datetime import datetime, timezone

import pytest

from src.core.random_generator import DeterministicRNG
from src.core.time_series import IntervalMinutes
from src.models.smart_city.visibility import VisibilityLevel, VisibilityReading
from src.simulators.smart_city.visibility import (
    VisibilitySimulator,
    _calculate_sun_times,
    _classify_visibility,
    _fog_index_from_time,
)


class TestFogIndex:
    """Tests for fog index based on time of day."""

    def test_fog_higher_at_dawn(self) -> None:
        """Test fog index is higher during dawn hours (05-08)."""
        rng = DeterministicRNG(seed=12345)
        sim = VisibilitySimulator("vis-001", rng)

        # 06:00 (peak dawn fog)
        dawn = datetime(2024, 6, 15, 6, 0, 0, tzinfo=timezone.utc)
        reading_dawn = sim.generate_at(dawn).value

        # 12:00 (midday, fog should be cleared)
        midday = datetime(2024, 6, 15, 12, 0, 0, tzinfo=timezone.utc)
        reading_midday = sim.generate_at(midday).value

        assert reading_dawn.fog_index > reading_midday.fog_index

    def test_fog_clears_midday(self) -> None:
        """Test fog index is low at midday."""
        rng = DeterministicRNG(seed=12345)
        sim = VisibilitySimulator("vis-001", rng)

        midday = datetime(2024, 6, 15, 12, 0, 0, tzinfo=timezone.utc)
        reading = sim.generate_at(midday).value

        # Midday fog should be low (base ~5 with variance +-10)
        assert reading.fog_index <= 30.0

    def test_base_fog_peak_at_dawn(self) -> None:
        """Test base fog index peaks around 06:00."""
        fog_6am = _fog_index_from_time(6.0)
        fog_noon = _fog_index_from_time(12.0)
        fog_15 = _fog_index_from_time(15.0)

        assert fog_6am > fog_noon
        assert fog_6am > fog_15

    def test_base_fog_dawn_range(self) -> None:
        """Test base fog index in dawn range (05-08) is elevated."""
        for hour in [5.0, 6.0, 7.0]:
            fog = _fog_index_from_time(hour)
            assert fog >= 0.0  # Should be non-negative
            # At 6.0 specifically, peak factor = 1.0 => fog = 50.0
            if hour == 6.0:
                assert fog == 50.0

    def test_base_fog_afternoon_minimal(self) -> None:
        """Test base fog index is minimal in the afternoon."""
        fog = _fog_index_from_time(15.0)
        assert fog == 5.0

    def test_fog_index_always_in_range(self) -> None:
        """Test fog index stays in 0-100 range across all hours."""
        rng = DeterministicRNG(seed=12345)
        sim = VisibilitySimulator("vis-001", rng)

        for hour in range(24):
            ts = datetime(2024, 6, 15, hour, 0, 0, tzinfo=timezone.utc)
            reading = sim.generate_at(ts).value
            assert 0.0 <= reading.fog_index <= 100.0


class TestVisibilityClassification:
    """Tests for visibility classification based on fog index."""

    def test_good_visibility_when_fog_below_30(self) -> None:
        """Test fog_index < 30 classifies as 'good'."""
        assert _classify_visibility(0.0) == VisibilityLevel.GOOD
        assert _classify_visibility(15.0) == VisibilityLevel.GOOD
        assert _classify_visibility(29.9) == VisibilityLevel.GOOD

    def test_medium_visibility_when_fog_30_to_60(self) -> None:
        """Test 30 <= fog_index < 60 classifies as 'medium'."""
        assert _classify_visibility(30.0) == VisibilityLevel.MEDIUM
        assert _classify_visibility(45.0) == VisibilityLevel.MEDIUM
        assert _classify_visibility(59.9) == VisibilityLevel.MEDIUM

    def test_poor_visibility_when_fog_above_60(self) -> None:
        """Test fog_index >= 60 classifies as 'poor'."""
        assert _classify_visibility(60.0) == VisibilityLevel.POOR
        assert _classify_visibility(80.0) == VisibilityLevel.POOR
        assert _classify_visibility(100.0) == VisibilityLevel.POOR

    def test_classification_boundary_30(self) -> None:
        """Test exact boundary at fog_index=30."""
        assert _classify_visibility(29.99) == VisibilityLevel.GOOD
        assert _classify_visibility(30.0) == VisibilityLevel.MEDIUM

    def test_classification_boundary_60(self) -> None:
        """Test exact boundary at fog_index=60."""
        assert _classify_visibility(59.99) == VisibilityLevel.MEDIUM
        assert _classify_visibility(60.0) == VisibilityLevel.POOR


class TestSunriseSunset:
    """Tests for sunrise/sunset time calculation."""

    def test_sunrise_before_sunset(self) -> None:
        """Test sunrise time is before sunset time."""
        rng = DeterministicRNG(seed=12345)
        sim = VisibilitySimulator("vis-001", rng)

        ts = datetime(2024, 6, 15, 12, 0, 0, tzinfo=timezone.utc)
        reading = sim.generate_at(ts).value

        sunrise_parts = reading.sunrise_time.split(":")
        sunset_parts = reading.sunset_time.split(":")
        sunrise_hour = int(sunrise_parts[0]) + int(sunrise_parts[1]) / 60.0
        sunset_hour = int(sunset_parts[0]) + int(sunset_parts[1]) / 60.0

        assert sunrise_hour < sunset_hour

    def test_sunrise_sunset_reasonable_summer_berlin(self) -> None:
        """Test sunrise/sunset are reasonable for summer in Berlin."""
        ts = datetime(2024, 6, 15, 12, 0, 0, tzinfo=timezone.utc)
        sunrise, sunset = _calculate_sun_times(ts, latitude=52.52, longitude=13.405)

        sunrise_parts = sunrise.split(":")
        sunset_parts = sunset.split(":")
        sunrise_hour = int(sunrise_parts[0]) + int(sunrise_parts[1]) / 60.0
        sunset_hour = int(sunset_parts[0]) + int(sunset_parts[1]) / 60.0

        # Berlin summer (simplified calc): sunrise ~02:30-05:00 UTC, sunset ~19:30-22:00 UTC
        assert 2.0 <= sunrise_hour <= 6.0
        assert 19.0 <= sunset_hour <= 23.0

    def test_sunrise_sunset_format(self) -> None:
        """Test sunrise/sunset are in HH:MM format."""
        rng = DeterministicRNG(seed=12345)
        sim = VisibilitySimulator("vis-001", rng)

        ts = datetime(2024, 6, 15, 12, 0, 0, tzinfo=timezone.utc)
        reading = sim.generate_at(ts).value

        # Verify HH:MM format
        assert len(reading.sunrise_time.split(":")) == 2
        assert len(reading.sunset_time.split(":")) == 2

        sunrise_h, sunrise_m = reading.sunrise_time.split(":")
        assert 0 <= int(sunrise_h) <= 23
        assert 0 <= int(sunrise_m) <= 59

    def test_longer_days_in_summer_vs_winter(self) -> None:
        """Test day length is longer in summer than winter at high latitude."""
        summer = datetime(2024, 6, 15, 12, 0, 0, tzinfo=timezone.utc)
        winter = datetime(2024, 12, 15, 12, 0, 0, tzinfo=timezone.utc)

        sunrise_s, sunset_s = _calculate_sun_times(summer, 52.52, 13.405)
        sunrise_w, sunset_w = _calculate_sun_times(winter, 52.52, 13.405)

        def day_length(sunrise: str, sunset: str) -> float:
            sr = int(sunrise.split(":")[0]) + int(sunrise.split(":")[1]) / 60.0
            ss = int(sunset.split(":")[0]) + int(sunset.split(":")[1]) / 60.0
            return ss - sr

        assert day_length(sunrise_s, sunset_s) > day_length(sunrise_w, sunset_w)

    def test_sunrise_sunset_present_in_reading(self) -> None:
        """Test that sunrise and sunset fields are populated."""
        rng = DeterministicRNG(seed=12345)
        sim = VisibilitySimulator("vis-001", rng)

        ts = datetime(2024, 6, 15, 12, 0, 0, tzinfo=timezone.utc)
        reading = sim.generate_at(ts).value

        assert reading.sunrise_time is not None
        assert reading.sunset_time is not None
        assert len(reading.sunrise_time) > 0
        assert len(reading.sunset_time) > 0


class TestVisibilityDeterminism:
    """Tests for deterministic behavior."""

    def test_same_seed_produces_identical_readings(self) -> None:
        """Test that same seed produces identical visibility readings."""
        ts = datetime(2024, 6, 15, 6, 0, 0, tzinfo=timezone.utc)

        results = []
        for _ in range(5):
            rng = DeterministicRNG(seed=42)
            sim = VisibilitySimulator("vis-001", rng)
            reading = sim.generate_at(ts).value
            results.append(reading.fog_index)

        assert all(r == results[0] for r in results)

    def test_different_seeds_produce_different_readings(self) -> None:
        """Test that different seeds produce different readings."""
        ts = datetime(2024, 6, 15, 6, 0, 0, tzinfo=timezone.utc)

        rng1 = DeterministicRNG(seed=111)
        sim1 = VisibilitySimulator("vis-001", rng1)
        reading1 = sim1.generate_at(ts).value

        rng2 = DeterministicRNG(seed=222)
        sim2 = VisibilitySimulator("vis-001", rng2)
        reading2 = sim2.generate_at(ts).value

        assert reading1.fog_index != reading2.fog_index

    def test_different_entities_produce_different_readings(self) -> None:
        """Test that different entity IDs produce different readings."""
        ts = datetime(2024, 6, 15, 6, 0, 0, tzinfo=timezone.utc)
        rng = DeterministicRNG(seed=12345)

        sim1 = VisibilitySimulator("vis-001", rng)
        sim2 = VisibilitySimulator("vis-002", rng)

        reading1 = sim1.generate_at(ts).value
        reading2 = sim2.generate_at(ts).value

        assert reading1.fog_index != reading2.fog_index


class TestVisibilityJSONPayload:
    """Tests for JSON payload format."""

    def test_json_payload_has_type_city_weather(self) -> None:
        """Test JSON payload has type='city_weather'."""
        rng = DeterministicRNG(seed=12345)
        sim = VisibilitySimulator("vis-001", rng)

        ts = datetime(2024, 6, 15, 12, 0, 0, tzinfo=timezone.utc)
        reading = sim.generate_at(ts).value
        payload = reading.to_json_payload()

        assert payload["type"] == "city_weather"

    def test_json_payload_structure(self) -> None:
        """Test JSON payload contains all required fields."""
        rng = DeterministicRNG(seed=12345)
        sim = VisibilitySimulator("vis-001", rng)

        ts = datetime(2024, 6, 15, 12, 0, 0, tzinfo=timezone.utc)
        reading = sim.generate_at(ts).value
        payload = reading.to_json_payload()

        required_fields = [
            "type",
            "schema_version",
            "city_id",
            "timestamp",
            "fog_index",
            "visibility",
            "sunrise_time",
            "sunset_time",
        ]
        for field in required_fields:
            assert field in payload

    def test_json_visibility_is_string(self) -> None:
        """Test visibility field is serialized as a string."""
        rng = DeterministicRNG(seed=12345)
        sim = VisibilitySimulator("vis-001", rng)

        ts = datetime(2024, 6, 15, 12, 0, 0, tzinfo=timezone.utc)
        reading = sim.generate_at(ts).value
        payload = reading.to_json_payload()

        assert isinstance(payload["visibility"], str)
        assert payload["visibility"] in {"good", "medium", "poor"}

    def test_json_serialization(self) -> None:
        """Test payload can be serialized to valid JSON."""
        rng = DeterministicRNG(seed=12345)
        sim = VisibilitySimulator("vis-001", rng)

        ts = datetime(2024, 6, 15, 12, 0, 0, tzinfo=timezone.utc)
        reading = sim.generate_at(ts).value
        payload = reading.to_json_payload()

        json_str = json.dumps(payload, indent=2)
        parsed = json.loads(json_str)
        assert parsed == payload

    def test_json_timestamp_format(self) -> None:
        """Test timestamp is in ISO 8601 with Z suffix."""
        rng = DeterministicRNG(seed=12345)
        sim = VisibilitySimulator("vis-001", rng)

        ts = datetime(2024, 6, 15, 12, 0, 0, tzinfo=timezone.utc)
        reading = sim.generate_at(ts).value
        payload = reading.to_json_payload()

        assert payload["timestamp"].endswith("Z")
