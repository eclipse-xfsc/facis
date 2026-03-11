"""Tests for streetlight simulator."""

import json
from datetime import datetime, timezone

import pytest

from src.core.random_generator import DeterministicRNG
from src.core.time_series import IntervalMinutes
from src.models.smart_city.event import CityEventReading, EventType, Severity
from src.models.smart_city.streetlight import StreetlightConfig, StreetlightReading
from src.simulators.smart_city.streetlight import StreetlightSimulator, _base_dimming


class TestStreetlightInitialization:
    """Tests for streetlight simulator initialization."""

    def test_initialization_with_defaults(self) -> None:
        """Test simulator initializes with default configuration."""
        rng = DeterministicRNG(seed=12345)
        sim = StreetlightSimulator("light-001", rng)

        assert sim.entity_id == "light-001"
        assert sim._config.light_id == "light-001"
        assert sim._config.zone_id == "zone-001"
        assert sim._config.rated_power_w == 150.0

    def test_initialization_with_custom_config(self) -> None:
        """Test simulator initializes with custom configuration."""
        rng = DeterministicRNG(seed=12345)
        config = StreetlightConfig(
            light_id="custom-light",
            zone_id="zone-042",
            rated_power_w=200.0,
        )
        sim = StreetlightSimulator(
            "custom-light",
            rng,
            config=config,
            city_id="city-lisbon",
            latitude=38.72,
            longitude=-9.14,
        )

        assert sim._config.zone_id == "zone-042"
        assert sim._config.rated_power_w == 200.0
        assert sim._city_id == "city-lisbon"
        assert sim._latitude == 38.72
        assert sim._longitude == -9.14


class TestDimmingSchedule:
    """Tests for dimming level based on time of day."""

    def test_full_brightness_at_midnight(self) -> None:
        """Test dimming is 100% (full brightness) at midnight."""
        rng = DeterministicRNG(seed=12345)
        sim = StreetlightSimulator("light-001", rng)

        midnight = datetime(2024, 6, 15, 0, 0, 0, tzinfo=timezone.utc)
        reading = sim.generate_at(midnight).value

        # At midnight the light should be at or near full brightness
        assert reading.dimming_level_pct >= 90.0

    def test_off_at_midday(self) -> None:
        """Test dimming is 0% (off) at midday when sun is up."""
        rng = DeterministicRNG(seed=12345)
        sim = StreetlightSimulator("light-001", rng)

        midday = datetime(2024, 6, 15, 12, 0, 0, tzinfo=timezone.utc)
        reading = sim.generate_at(midday).value

        # At midday in summer the light should be off (0% +/- small variance)
        assert reading.dimming_level_pct <= 10.0

    def test_base_dimming_full_night(self) -> None:
        """Test base dimming helper returns 100% for deep night hours."""
        # Berlin summer: sunrise ~4:50, sunset ~21:30
        # Using approximate values for the helper
        assert _base_dimming(0.0, sunrise_hour=5.0, sunset_hour=21.0) == 100.0
        assert _base_dimming(2.0, sunrise_hour=5.0, sunset_hour=21.0) == 100.0
        assert _base_dimming(23.0, sunrise_hour=5.0, sunset_hour=21.0) == 100.0

    def test_base_dimming_zero_during_day(self) -> None:
        """Test base dimming helper returns 0% during full daylight."""
        assert _base_dimming(12.0, sunrise_hour=5.0, sunset_hour=21.0) == 0.0
        assert _base_dimming(15.0, sunrise_hour=5.0, sunset_hour=21.0) == 0.0

    def test_base_dimming_dawn_ramp(self) -> None:
        """Test base dimming ramps down during dawn transition."""
        sunrise = 5.0
        sunset = 21.0

        # Just before dawn transition starts (sunrise - 0.5)
        pre_dawn = _base_dimming(sunrise - 0.6, sunrise, sunset)
        assert pre_dawn == 100.0

        # Mid-dawn (at sunrise): should be ~50%
        mid_dawn = _base_dimming(sunrise, sunrise, sunset)
        assert 40.0 <= mid_dawn <= 60.0

        # End of dawn transition (sunrise + 0.5): should be ~0%
        post_dawn = _base_dimming(sunrise + 0.5, sunrise, sunset)
        assert post_dawn == 0.0

    def test_base_dimming_dusk_ramp(self) -> None:
        """Test base dimming ramps up during dusk transition."""
        sunrise = 5.0
        sunset = 21.0

        # Just before dusk transition (sunset - 0.5): daylight still
        pre_dusk = _base_dimming(sunset - 0.6, sunrise, sunset)
        assert pre_dusk == 0.0

        # Mid-dusk (at sunset): should be ~50%
        mid_dusk = _base_dimming(sunset, sunrise, sunset)
        assert 40.0 <= mid_dusk <= 60.0

        # End of dusk transition (sunset + 0.5): should be 100%
        post_dusk = _base_dimming(sunset + 0.5, sunrise, sunset)
        assert post_dusk == 100.0


class TestEventReaction:
    """Tests for event-reactive dimming boost."""

    def _make_event(
        self, zone_id: str, severity: Severity, active: bool = True
    ) -> CityEventReading:
        """Helper to create a city event reading."""
        return CityEventReading(
            city_id="city-berlin",
            zone_id=zone_id,
            timestamp=datetime(2024, 6, 15, 14, 0, 0, tzinfo=timezone.utc),
            event_type=EventType.ACCIDENT,
            severity=severity,
            active=active,
        )

    def test_severity_2_adds_30_percent_boost(self) -> None:
        """Test severity >= 2 event causes +30% dimming boost."""
        rng = DeterministicRNG(seed=12345)
        config = StreetlightConfig(light_id="light-001", zone_id="zone-001")
        sim = StreetlightSimulator("light-001", rng, config=config)

        # Midday: base dimming ~0% so boost is clearly visible
        ts = datetime(2024, 6, 15, 12, 0, 0, tzinfo=timezone.utc)

        # Without event
        reading_no_event = sim.generate_at(ts).value
        base_dimming = reading_no_event.dimming_level_pct

        # With severity 2 event
        event = self._make_event("zone-001", Severity.MEDIUM)
        sim.set_active_event(event)
        reading_with_event = sim.generate_at(ts).value

        # Boost should be approximately +30%
        boost = reading_with_event.dimming_level_pct - base_dimming
        assert 25.0 <= boost <= 35.0

    def test_severity_3_adds_50_percent_boost(self) -> None:
        """Test severity >= 3 event causes +50% dimming boost."""
        rng = DeterministicRNG(seed=12345)
        config = StreetlightConfig(light_id="light-001", zone_id="zone-001")
        sim = StreetlightSimulator("light-001", rng, config=config)

        ts = datetime(2024, 6, 15, 12, 0, 0, tzinfo=timezone.utc)

        # Without event
        reading_no_event = sim.generate_at(ts).value
        base_dimming = reading_no_event.dimming_level_pct

        # With severity 3 event
        event = self._make_event("zone-001", Severity.HIGH)
        sim.set_active_event(event)
        reading_with_event = sim.generate_at(ts).value

        boost = reading_with_event.dimming_level_pct - base_dimming
        assert 45.0 <= boost <= 55.0

    def test_severity_1_no_boost(self) -> None:
        """Test severity 1 event does not boost dimming."""
        rng = DeterministicRNG(seed=12345)
        config = StreetlightConfig(light_id="light-001", zone_id="zone-001")
        sim = StreetlightSimulator("light-001", rng, config=config)

        ts = datetime(2024, 6, 15, 12, 0, 0, tzinfo=timezone.utc)

        reading_no_event = sim.generate_at(ts).value

        event = self._make_event("zone-001", Severity.LOW)
        sim.set_active_event(event)
        reading_with_event = sim.generate_at(ts).value

        assert reading_with_event.dimming_level_pct == reading_no_event.dimming_level_pct

    def test_inactive_event_no_boost(self) -> None:
        """Test inactive event does not boost dimming."""
        rng = DeterministicRNG(seed=12345)
        config = StreetlightConfig(light_id="light-001", zone_id="zone-001")
        sim = StreetlightSimulator("light-001", rng, config=config)

        ts = datetime(2024, 6, 15, 12, 0, 0, tzinfo=timezone.utc)

        reading_no_event = sim.generate_at(ts).value

        event = self._make_event("zone-001", Severity.HIGH, active=False)
        sim.set_active_event(event)
        reading_with_event = sim.generate_at(ts).value

        assert reading_with_event.dimming_level_pct == reading_no_event.dimming_level_pct

    def test_wrong_zone_no_boost(self) -> None:
        """Test event in a different zone does not boost dimming."""
        rng = DeterministicRNG(seed=12345)
        config = StreetlightConfig(light_id="light-001", zone_id="zone-001")
        sim = StreetlightSimulator("light-001", rng, config=config)

        ts = datetime(2024, 6, 15, 12, 0, 0, tzinfo=timezone.utc)

        reading_no_event = sim.generate_at(ts).value

        event = self._make_event("zone-999", Severity.HIGH)
        sim.set_active_event(event)
        reading_with_event = sim.generate_at(ts).value

        assert reading_with_event.dimming_level_pct == reading_no_event.dimming_level_pct

    def test_dimming_boost_capped_at_100(self) -> None:
        """Test dimming + boost never exceeds 100%."""
        rng = DeterministicRNG(seed=12345)
        config = StreetlightConfig(light_id="light-001", zone_id="zone-001")
        sim = StreetlightSimulator("light-001", rng, config=config)

        # Midnight: dimming ~100%, boost of 50% should still cap at 100%
        ts = datetime(2024, 6, 15, 0, 0, 0, tzinfo=timezone.utc)

        event = self._make_event("zone-001", Severity.HIGH)
        sim.set_active_event(event)
        reading = sim.generate_at(ts).value

        assert reading.dimming_level_pct <= 100.0


class TestPowerCalculation:
    """Tests for power calculation from dimming level."""

    def test_power_equals_dimming_times_rated(self) -> None:
        """Test power_w = (dimming_level_pct / 100) * rated_power_w."""
        rng = DeterministicRNG(seed=12345)
        config = StreetlightConfig(light_id="light-001", zone_id="zone-001", rated_power_w=150.0)
        sim = StreetlightSimulator("light-001", rng, config=config)

        ts = datetime(2024, 6, 15, 0, 0, 0, tzinfo=timezone.utc)
        reading = sim.generate_at(ts).value

        expected_power = (reading.dimming_level_pct / 100.0) * 150.0
        assert abs(reading.power_w - expected_power) < 0.01

    def test_power_zero_when_off(self) -> None:
        """Test power is near zero when light is off at midday."""
        rng = DeterministicRNG(seed=12345)
        sim = StreetlightSimulator("light-001", rng)

        midday = datetime(2024, 6, 15, 12, 0, 0, tzinfo=timezone.utc)
        reading = sim.generate_at(midday).value

        assert reading.power_w <= 15.0  # Near zero with small variance

    def test_power_proportional_to_rated(self) -> None:
        """Test power scales with rated power at same dimming."""
        ts = datetime(2024, 6, 15, 0, 0, 0, tzinfo=timezone.utc)

        rng1 = DeterministicRNG(seed=12345)
        config1 = StreetlightConfig(light_id="light-001", zone_id="zone-001", rated_power_w=100.0)
        sim1 = StreetlightSimulator("light-001", rng1, config=config1)
        reading1 = sim1.generate_at(ts).value

        rng2 = DeterministicRNG(seed=12345)
        config2 = StreetlightConfig(light_id="light-001", zone_id="zone-001", rated_power_w=200.0)
        sim2 = StreetlightSimulator("light-001", rng2, config=config2)
        reading2 = sim2.generate_at(ts).value

        # Same dimming level, double rated power => double power
        assert abs(reading2.power_w - 2.0 * reading1.power_w) < 0.01


class TestStreetlightDeterminism:
    """Tests for deterministic behavior."""

    def test_same_seed_produces_identical_readings(self) -> None:
        """Test that same seed produces identical readings."""
        ts = datetime(2024, 6, 15, 3, 0, 0, tzinfo=timezone.utc)

        results = []
        for _ in range(5):
            rng = DeterministicRNG(seed=42)
            sim = StreetlightSimulator("light-001", rng)
            reading = sim.generate_at(ts).value
            results.append(reading.dimming_level_pct)

        assert all(r == results[0] for r in results)

    def test_different_seeds_produce_different_readings(self) -> None:
        """Test that different seeds produce different readings."""
        ts = datetime(2024, 6, 15, 3, 0, 0, tzinfo=timezone.utc)

        rng1 = DeterministicRNG(seed=111)
        sim1 = StreetlightSimulator("light-001", rng1)
        reading1 = sim1.generate_at(ts).value

        rng2 = DeterministicRNG(seed=222)
        sim2 = StreetlightSimulator("light-001", rng2)
        reading2 = sim2.generate_at(ts).value

        # Variance component should differ
        assert reading1.dimming_level_pct != reading2.dimming_level_pct

    def test_different_entities_produce_different_readings(self) -> None:
        """Test that different entity IDs produce different readings."""
        ts = datetime(2024, 6, 15, 3, 0, 0, tzinfo=timezone.utc)
        rng = DeterministicRNG(seed=12345)

        sim1 = StreetlightSimulator("light-001", rng)
        sim2 = StreetlightSimulator("light-002", rng)

        reading1 = sim1.generate_at(ts).value
        reading2 = sim2.generate_at(ts).value

        assert reading1.dimming_level_pct != reading2.dimming_level_pct


class TestStreetlightJSONPayload:
    """Tests for JSON payload format."""

    def test_json_payload_has_type_streetlight(self) -> None:
        """Test JSON payload has type='streetlight'."""
        rng = DeterministicRNG(seed=12345)
        sim = StreetlightSimulator("light-001", rng)

        ts = datetime(2024, 6, 15, 0, 0, 0, tzinfo=timezone.utc)
        reading = sim.generate_at(ts).value
        payload = reading.to_json_payload()

        assert payload["type"] == "streetlight"

    def test_json_payload_structure(self) -> None:
        """Test JSON payload contains all required fields."""
        rng = DeterministicRNG(seed=12345)
        sim = StreetlightSimulator("light-001", rng)

        ts = datetime(2024, 6, 15, 0, 0, 0, tzinfo=timezone.utc)
        reading = sim.generate_at(ts).value
        payload = reading.to_json_payload()

        required_fields = [
            "type",
            "schema_version",
            "site_id",
            "city_id",
            "zone_id",
            "light_id",
            "asset_id",
            "timestamp",
            "dimming_level_pct",
            "power_w",
        ]
        for field in required_fields:
            assert field in payload

    def test_json_serialization(self) -> None:
        """Test payload can be serialized to valid JSON."""
        rng = DeterministicRNG(seed=12345)
        sim = StreetlightSimulator("light-001", rng)

        ts = datetime(2024, 6, 15, 12, 0, 0, tzinfo=timezone.utc)
        reading = sim.generate_at(ts).value
        payload = reading.to_json_payload()

        json_str = json.dumps(payload, indent=2)
        parsed = json.loads(json_str)
        assert parsed == payload

    def test_json_timestamp_format(self) -> None:
        """Test timestamp is in ISO 8601 with Z suffix."""
        rng = DeterministicRNG(seed=12345)
        sim = StreetlightSimulator("light-001", rng)

        ts = datetime(2024, 6, 15, 12, 0, 0, tzinfo=timezone.utc)
        reading = sim.generate_at(ts).value
        payload = reading.to_json_payload()

        assert payload["timestamp"].endswith("Z")
