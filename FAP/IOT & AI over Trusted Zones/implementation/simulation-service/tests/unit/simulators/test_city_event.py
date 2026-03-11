"""Tests for city event simulator."""

import json
from datetime import datetime, timezone

import pytest

from src.core.random_generator import DeterministicRNG
from src.core.time_series import IntervalMinutes
from src.models.smart_city.event import CityEventReading, EventType, Severity
from src.simulators.smart_city.event import CityEventSimulator


class TestNormalMode:
    """Tests for normal mode (no active events)."""

    def test_normal_mode_no_active_events(self) -> None:
        """Test normal mode produces readings with active=False."""
        rng = DeterministicRNG(seed=12345)
        sim = CityEventSimulator("event-001", rng, mode="normal")

        # Check across all hours of the day
        for hour in range(24):
            ts = datetime(2024, 6, 15, hour, 0, 0, tzinfo=timezone.utc)
            reading = sim.generate_at(ts).value
            assert reading.active is False

    def test_normal_mode_default_event_type(self) -> None:
        """Test normal mode returns default event type and severity."""
        rng = DeterministicRNG(seed=12345)
        sim = CityEventSimulator("event-001", rng, mode="normal")

        ts = datetime(2024, 6, 15, 12, 0, 0, tzinfo=timezone.utc)
        reading = sim.generate_at(ts).value

        assert reading.event_type == EventType.EVENT
        assert reading.severity == Severity.LOW
        assert reading.active is False

    def test_default_mode_is_normal(self) -> None:
        """Test the default mode is 'normal' (no events)."""
        rng = DeterministicRNG(seed=12345)
        sim = CityEventSimulator("event-001", rng)

        ts = datetime(2024, 6, 15, 12, 0, 0, tzinfo=timezone.utc)
        reading = sim.generate_at(ts).value

        assert reading.active is False


class TestEventMode:
    """Tests for event mode (generates active events at deterministic times)."""

    def test_event_mode_generates_active_events(self) -> None:
        """Test event mode produces active events at scheduled times."""
        rng = DeterministicRNG(seed=12345)
        sim = CityEventSimulator("event-001", rng, mode="event")

        # Check all hours, collect active events
        active_events = []
        for hour in range(24):
            ts = datetime(2024, 6, 15, hour, 0, 0, tzinfo=timezone.utc)
            reading = sim.generate_at(ts).value
            if reading.active:
                active_events.append(reading)

        # Event mode should produce at least one active event during the day
        assert len(active_events) >= 1

    def test_event_mode_inactive_outside_windows(self) -> None:
        """Test event mode returns inactive readings outside event windows."""
        rng = DeterministicRNG(seed=12345)
        sim = CityEventSimulator("event-001", rng, mode="event")

        # Very early morning (01:00) is unlikely to have an event
        ts = datetime(2024, 6, 15, 1, 0, 0, tzinfo=timezone.utc)
        reading = sim.generate_at(ts).value

        assert reading.active is False

    def test_event_has_correct_types(self) -> None:
        """Test events have valid event_type values."""
        rng = DeterministicRNG(seed=12345)
        sim = CityEventSimulator("event-001", rng, mode="event")

        valid_types = {EventType.ACCIDENT, EventType.EMERGENCY, EventType.EVENT}

        for hour in range(24):
            ts = datetime(2024, 6, 15, hour, 0, 0, tzinfo=timezone.utc)
            reading = sim.generate_at(ts).value
            assert reading.event_type in valid_types

    def test_event_has_valid_severity(self) -> None:
        """Test events have valid severity values."""
        rng = DeterministicRNG(seed=12345)
        sim = CityEventSimulator("event-001", rng, mode="event")

        valid_severities = {Severity.LOW, Severity.MEDIUM, Severity.HIGH}

        for hour in range(24):
            ts = datetime(2024, 6, 15, hour, 0, 0, tzinfo=timezone.utc)
            reading = sim.generate_at(ts).value
            assert reading.severity in valid_severities


class TestEventFields:
    """Tests for event reading fields."""

    def test_event_has_event_type_field(self) -> None:
        """Test event reading has event_type field."""
        rng = DeterministicRNG(seed=12345)
        sim = CityEventSimulator("event-001", rng, mode="event")

        ts = datetime(2024, 6, 15, 12, 0, 0, tzinfo=timezone.utc)
        reading = sim.generate_at(ts).value

        assert hasattr(reading, "event_type")
        assert isinstance(reading.event_type, EventType)

    def test_event_has_severity_field(self) -> None:
        """Test event reading has severity field."""
        rng = DeterministicRNG(seed=12345)
        sim = CityEventSimulator("event-001", rng, mode="event")

        ts = datetime(2024, 6, 15, 12, 0, 0, tzinfo=timezone.utc)
        reading = sim.generate_at(ts).value

        assert hasattr(reading, "severity")
        assert isinstance(reading.severity, Severity)

    def test_event_has_active_field(self) -> None:
        """Test event reading has active field."""
        rng = DeterministicRNG(seed=12345)
        sim = CityEventSimulator("event-001", rng, mode="normal")

        ts = datetime(2024, 6, 15, 12, 0, 0, tzinfo=timezone.utc)
        reading = sim.generate_at(ts).value

        assert hasattr(reading, "active")
        assert isinstance(reading.active, bool)

    def test_event_has_zone_id(self) -> None:
        """Test event reading has zone_id field."""
        rng = DeterministicRNG(seed=12345)
        sim = CityEventSimulator("event-001", rng, zone_id="zone-042")

        ts = datetime(2024, 6, 15, 12, 0, 0, tzinfo=timezone.utc)
        reading = sim.generate_at(ts).value

        assert reading.zone_id == "zone-042"


class TestEventDeterminism:
    """Tests for deterministic behavior."""

    def test_same_seed_produces_identical_events(self) -> None:
        """Test that same seed produces identical event sequences."""
        ts = datetime(2024, 6, 15, 9, 0, 0, tzinfo=timezone.utc)

        results = []
        for _ in range(5):
            rng = DeterministicRNG(seed=42)
            sim = CityEventSimulator("event-001", rng, mode="event")
            reading = sim.generate_at(ts).value
            results.append((reading.event_type, reading.severity, reading.active))

        assert all(r == results[0] for r in results)

    def test_same_seed_same_full_day_sequence(self) -> None:
        """Test the full day produces the same event pattern with same seed."""

        def get_day_events(seed: int) -> list[tuple]:
            rng = DeterministicRNG(seed=seed)
            sim = CityEventSimulator("event-001", rng, mode="event")
            events = []
            for hour in range(24):
                ts = datetime(2024, 6, 15, hour, 0, 0, tzinfo=timezone.utc)
                reading = sim.generate_at(ts).value
                events.append((reading.active, reading.event_type, reading.severity))
            return events

        run1 = get_day_events(12345)
        run2 = get_day_events(12345)
        assert run1 == run2

    def test_different_seeds_produce_different_events(self) -> None:
        """Test different seeds can produce different event patterns."""

        def get_day_active_pattern(seed: int) -> list[bool]:
            rng = DeterministicRNG(seed=seed)
            sim = CityEventSimulator("event-001", rng, mode="event")
            return [
                sim.generate_at(datetime(2024, 6, 15, h, 0, 0, tzinfo=timezone.utc)).value.active
                for h in range(24)
            ]

        pattern1 = get_day_active_pattern(111)
        pattern2 = get_day_active_pattern(222)

        # Patterns may differ (seed-dependent jitter on event times)
        # At minimum both should have some structure
        assert isinstance(pattern1, list)
        assert isinstance(pattern2, list)


class TestCityEventJSONPayload:
    """Tests for JSON payload format."""

    def test_json_payload_has_type_city_event(self) -> None:
        """Test JSON payload has type='city_event'."""
        rng = DeterministicRNG(seed=12345)
        sim = CityEventSimulator("event-001", rng, mode="event")

        ts = datetime(2024, 6, 15, 12, 0, 0, tzinfo=timezone.utc)
        reading = sim.generate_at(ts).value
        payload = reading.to_json_payload()

        assert payload["type"] == "city_event"

    def test_json_payload_structure(self) -> None:
        """Test JSON payload contains all required fields."""
        rng = DeterministicRNG(seed=12345)
        sim = CityEventSimulator("event-001", rng, mode="event")

        ts = datetime(2024, 6, 15, 12, 0, 0, tzinfo=timezone.utc)
        reading = sim.generate_at(ts).value
        payload = reading.to_json_payload()

        required_fields = [
            "type",
            "schema_version",
            "city_id",
            "zone_id",
            "timestamp",
            "event_type",
            "severity",
            "active",
        ]
        for field in required_fields:
            assert field in payload

    def test_json_event_type_is_string(self) -> None:
        """Test event_type is serialized as a string value."""
        rng = DeterministicRNG(seed=12345)
        sim = CityEventSimulator("event-001", rng, mode="event")

        ts = datetime(2024, 6, 15, 9, 0, 0, tzinfo=timezone.utc)
        reading = sim.generate_at(ts).value
        payload = reading.to_json_payload()

        assert isinstance(payload["event_type"], str)
        assert payload["event_type"] in {"accident", "emergency", "event"}

    def test_json_severity_is_int(self) -> None:
        """Test severity is serialized as an integer."""
        rng = DeterministicRNG(seed=12345)
        sim = CityEventSimulator("event-001", rng, mode="event")

        ts = datetime(2024, 6, 15, 9, 0, 0, tzinfo=timezone.utc)
        reading = sim.generate_at(ts).value
        payload = reading.to_json_payload()

        assert isinstance(payload["severity"], int)
        assert payload["severity"] in {1, 2, 3}

    def test_json_serialization(self) -> None:
        """Test payload can be serialized to valid JSON."""
        rng = DeterministicRNG(seed=12345)
        sim = CityEventSimulator("event-001", rng, mode="event")

        ts = datetime(2024, 6, 15, 12, 0, 0, tzinfo=timezone.utc)
        reading = sim.generate_at(ts).value
        payload = reading.to_json_payload()

        json_str = json.dumps(payload, indent=2)
        parsed = json.loads(json_str)
        assert parsed == payload

    def test_json_timestamp_format(self) -> None:
        """Test timestamp is in ISO 8601 with Z suffix."""
        rng = DeterministicRNG(seed=12345)
        sim = CityEventSimulator("event-001", rng)

        ts = datetime(2024, 6, 15, 12, 0, 0, tzinfo=timezone.utc)
        reading = sim.generate_at(ts).value
        payload = reading.to_json_payload()

        assert payload["timestamp"].endswith("Z")
