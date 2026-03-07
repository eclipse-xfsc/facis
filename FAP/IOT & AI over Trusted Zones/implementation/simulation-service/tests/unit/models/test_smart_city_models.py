"""Tests for smart city data models."""

import json
from datetime import datetime, timezone

import pytest

from src.models.smart_city.event import CityEventReading, EventType, Severity
from src.models.smart_city.streetlight import StreetlightReading
from src.models.smart_city.traffic import TrafficReading
from src.models.smart_city.visibility import VisibilityLevel, VisibilityReading


class TestStreetlightReading:
    """Tests for StreetlightReading data model."""

    def test_instantiation_with_valid_data(self) -> None:
        """Test that StreetlightReading can be instantiated with valid data."""
        reading = StreetlightReading(
            zone_id="zone-A",
            light_id="light-001",
            city_id="lisbon",
            timestamp=datetime(2026, 2, 15, 12, 0, 0, tzinfo=timezone.utc),
            dimming_level_pct=75.0,
            power_w=112.5,
        )

        assert reading.type == "streetlight"
        assert reading.schema_version == "1.0"
        assert reading.zone_id == "zone-A"
        assert reading.light_id == "light-001"
        assert reading.city_id == "lisbon"
        assert reading.dimming_level_pct == 75.0
        assert reading.power_w == 112.5

    def test_required_fields_present(self) -> None:
        """Test that type, schema_version, and timestamp are present."""
        reading = StreetlightReading(
            zone_id="zone-A",
            light_id="light-001",
            timestamp=datetime(2026, 2, 15, 12, 0, 0, tzinfo=timezone.utc),
            dimming_level_pct=50.0,
            power_w=75.0,
        )

        assert reading.type == "streetlight"
        assert reading.schema_version == "1.0"
        assert reading.timestamp == datetime(2026, 2, 15, 12, 0, 0, tzinfo=timezone.utc)

    def test_type_is_streetlight(self) -> None:
        """Test that the type field is always 'streetlight'."""
        reading = StreetlightReading(
            zone_id="zone-B",
            light_id="light-002",
            timestamp=datetime(2026, 2, 15, 12, 0, 0, tzinfo=timezone.utc),
            dimming_level_pct=0.0,
            power_w=0.0,
        )

        assert reading.type == "streetlight"

    def test_dimming_level_pct_minimum(self) -> None:
        """Test dimming_level_pct accepts minimum value of 0."""
        reading = StreetlightReading(
            zone_id="zone-A",
            light_id="light-001",
            timestamp=datetime(2026, 2, 15, 12, 0, 0, tzinfo=timezone.utc),
            dimming_level_pct=0.0,
            power_w=0.0,
        )

        assert reading.dimming_level_pct == 0.0

    def test_dimming_level_pct_maximum(self) -> None:
        """Test dimming_level_pct accepts maximum value of 100."""
        reading = StreetlightReading(
            zone_id="zone-A",
            light_id="light-001",
            timestamp=datetime(2026, 2, 15, 12, 0, 0, tzinfo=timezone.utc),
            dimming_level_pct=100.0,
            power_w=150.0,
        )

        assert reading.dimming_level_pct == 100.0

    def test_dimming_level_pct_below_range_rejected(self) -> None:
        """Test dimming_level_pct rejects values below 0."""
        with pytest.raises(ValueError):
            StreetlightReading(
                zone_id="zone-A",
                light_id="light-001",
                timestamp=datetime(2026, 2, 15, 12, 0, 0, tzinfo=timezone.utc),
                dimming_level_pct=-1.0,
                power_w=0.0,
            )

    def test_dimming_level_pct_above_range_rejected(self) -> None:
        """Test dimming_level_pct rejects values above 100."""
        with pytest.raises(ValueError):
            StreetlightReading(
                zone_id="zone-A",
                light_id="light-001",
                timestamp=datetime(2026, 2, 15, 12, 0, 0, tzinfo=timezone.utc),
                dimming_level_pct=101.0,
                power_w=150.0,
            )

    def test_to_json_payload_contains_all_fields(self) -> None:
        """Test that to_json_payload produces correct JSON with all required fields."""
        reading = StreetlightReading(
            zone_id="zone-A",
            light_id="light-001",
            city_id="lisbon",
            timestamp=datetime(2026, 2, 15, 14, 30, 0, tzinfo=timezone.utc),
            dimming_level_pct=80.0,
            power_w=120.0,
        )

        payload = reading.to_json_payload()

        assert payload["type"] == "streetlight"
        assert payload["schema_version"] == "1.0"
        assert payload["timestamp"] == "2026-02-15T14:30:00Z"
        assert payload["zone_id"] == "zone-A"
        assert payload["light_id"] == "light-001"
        assert payload["city_id"] == "lisbon"
        assert payload["asset_id"] == "light-001"
        assert payload["dimming_level_pct"] == 80.0
        assert payload["power_w"] == 120.0

    def test_to_json_payload_serializable(self) -> None:
        """Test that payload can be serialized to valid JSON."""
        reading = StreetlightReading(
            zone_id="zone-A",
            light_id="light-001",
            timestamp=datetime(2026, 2, 15, 12, 0, 0, tzinfo=timezone.utc),
            dimming_level_pct=50.0,
            power_w=75.0,
        )

        payload = reading.to_json_payload()
        json_str = json.dumps(payload)
        assert json_str is not None

        parsed = json.loads(json_str)
        assert parsed == payload

    def test_asset_id_matches_light_id(self) -> None:
        """Test that asset_id property returns the light_id."""
        reading = StreetlightReading(
            zone_id="zone-A",
            light_id="light-042",
            timestamp=datetime(2026, 2, 15, 12, 0, 0, tzinfo=timezone.utc),
            dimming_level_pct=50.0,
            power_w=75.0,
        )

        assert reading.asset_id == "light-042"


class TestTrafficReading:
    """Tests for TrafficReading data model."""

    def test_instantiation_with_valid_data(self) -> None:
        """Test that TrafficReading can be instantiated with valid data."""
        reading = TrafficReading(
            zone_id="zone-A",
            city_id="lisbon",
            timestamp=datetime(2026, 2, 15, 8, 0, 0, tzinfo=timezone.utc),
            traffic_index=65.3,
        )

        assert reading.type == "traffic"
        assert reading.schema_version == "1.0"
        assert reading.zone_id == "zone-A"
        assert reading.city_id == "lisbon"
        assert reading.traffic_index == 65.3

    def test_required_fields_present(self) -> None:
        """Test that type, schema_version, and timestamp are present."""
        reading = TrafficReading(
            zone_id="zone-B",
            timestamp=datetime(2026, 2, 15, 12, 0, 0, tzinfo=timezone.utc),
            traffic_index=40.0,
        )

        assert reading.type == "traffic"
        assert reading.schema_version == "1.0"
        assert reading.timestamp == datetime(2026, 2, 15, 12, 0, 0, tzinfo=timezone.utc)

    def test_type_is_traffic(self) -> None:
        """Test that the type field is always 'traffic'."""
        reading = TrafficReading(
            zone_id="zone-C",
            timestamp=datetime(2026, 2, 15, 12, 0, 0, tzinfo=timezone.utc),
            traffic_index=0.0,
        )

        assert reading.type == "traffic"

    def test_traffic_index_minimum(self) -> None:
        """Test traffic_index accepts minimum value of 0."""
        reading = TrafficReading(
            zone_id="zone-A",
            timestamp=datetime(2026, 2, 15, 3, 0, 0, tzinfo=timezone.utc),
            traffic_index=0.0,
        )

        assert reading.traffic_index == 0.0

    def test_traffic_index_maximum(self) -> None:
        """Test traffic_index accepts maximum value of 100."""
        reading = TrafficReading(
            zone_id="zone-A",
            timestamp=datetime(2026, 2, 15, 17, 0, 0, tzinfo=timezone.utc),
            traffic_index=100.0,
        )

        assert reading.traffic_index == 100.0

    def test_traffic_index_below_range_rejected(self) -> None:
        """Test traffic_index rejects values below 0."""
        with pytest.raises(ValueError):
            TrafficReading(
                zone_id="zone-A",
                timestamp=datetime(2026, 2, 15, 12, 0, 0, tzinfo=timezone.utc),
                traffic_index=-1.0,
            )

    def test_traffic_index_above_range_rejected(self) -> None:
        """Test traffic_index rejects values above 100."""
        with pytest.raises(ValueError):
            TrafficReading(
                zone_id="zone-A",
                timestamp=datetime(2026, 2, 15, 12, 0, 0, tzinfo=timezone.utc),
                traffic_index=100.1,
            )

    def test_to_json_payload_contains_all_fields(self) -> None:
        """Test that to_json_payload produces correct JSON with all required fields."""
        reading = TrafficReading(
            zone_id="zone-A",
            city_id="lisbon",
            timestamp=datetime(2026, 2, 15, 8, 30, 0, tzinfo=timezone.utc),
            traffic_index=72.5,
        )

        payload = reading.to_json_payload()

        assert payload["type"] == "traffic"
        assert payload["schema_version"] == "1.0"
        assert payload["timestamp"] == "2026-02-15T08:30:00Z"
        assert payload["zone_id"] == "zone-A"
        assert payload["city_id"] == "lisbon"
        assert payload["traffic_index"] == 72.5

    def test_to_json_payload_serializable(self) -> None:
        """Test that payload can be serialized to valid JSON."""
        reading = TrafficReading(
            zone_id="zone-A",
            timestamp=datetime(2026, 2, 15, 12, 0, 0, tzinfo=timezone.utc),
            traffic_index=50.0,
        )

        payload = reading.to_json_payload()
        json_str = json.dumps(payload)
        assert json_str is not None

        parsed = json.loads(json_str)
        assert parsed == payload


class TestCityEventReading:
    """Tests for CityEventReading data model."""

    def test_instantiation_with_valid_data(self) -> None:
        """Test that CityEventReading can be instantiated with valid data."""
        reading = CityEventReading(
            zone_id="zone-A",
            city_id="lisbon",
            timestamp=datetime(2026, 2, 15, 10, 0, 0, tzinfo=timezone.utc),
            event_type=EventType.ACCIDENT,
            severity=Severity.HIGH,
            active=True,
        )

        assert reading.type == "city_event"
        assert reading.schema_version == "1.0"
        assert reading.zone_id == "zone-A"
        assert reading.city_id == "lisbon"
        assert reading.event_type == EventType.ACCIDENT
        assert reading.severity == Severity.HIGH
        assert reading.active is True

    def test_required_fields_present(self) -> None:
        """Test that type, schema_version, and timestamp are present."""
        reading = CityEventReading(
            zone_id="zone-B",
            timestamp=datetime(2026, 2, 15, 12, 0, 0, tzinfo=timezone.utc),
            event_type=EventType.EMERGENCY,
            severity=Severity.MEDIUM,
        )

        assert reading.type == "city_event"
        assert reading.schema_version == "1.0"
        assert reading.timestamp == datetime(2026, 2, 15, 12, 0, 0, tzinfo=timezone.utc)

    def test_type_is_city_event(self) -> None:
        """Test that the type field is always 'city_event'."""
        reading = CityEventReading(
            zone_id="zone-A",
            timestamp=datetime(2026, 2, 15, 12, 0, 0, tzinfo=timezone.utc),
            event_type=EventType.EVENT,
            severity=Severity.LOW,
        )

        assert reading.type == "city_event"

    def test_event_type_accident(self) -> None:
        """Test event_type accepts ACCIDENT enum value."""
        reading = CityEventReading(
            zone_id="zone-A",
            timestamp=datetime(2026, 2, 15, 12, 0, 0, tzinfo=timezone.utc),
            event_type=EventType.ACCIDENT,
            severity=Severity.HIGH,
        )

        assert reading.event_type == EventType.ACCIDENT
        assert reading.event_type.value == "accident"

    def test_event_type_emergency(self) -> None:
        """Test event_type accepts EMERGENCY enum value."""
        reading = CityEventReading(
            zone_id="zone-A",
            timestamp=datetime(2026, 2, 15, 12, 0, 0, tzinfo=timezone.utc),
            event_type=EventType.EMERGENCY,
            severity=Severity.HIGH,
        )

        assert reading.event_type == EventType.EMERGENCY
        assert reading.event_type.value == "emergency"

    def test_event_type_event(self) -> None:
        """Test event_type accepts EVENT enum value."""
        reading = CityEventReading(
            zone_id="zone-A",
            timestamp=datetime(2026, 2, 15, 12, 0, 0, tzinfo=timezone.utc),
            event_type=EventType.EVENT,
            severity=Severity.LOW,
        )

        assert reading.event_type == EventType.EVENT
        assert reading.event_type.value == "event"

    def test_severity_low(self) -> None:
        """Test severity accepts LOW value (1)."""
        reading = CityEventReading(
            zone_id="zone-A",
            timestamp=datetime(2026, 2, 15, 12, 0, 0, tzinfo=timezone.utc),
            event_type=EventType.EVENT,
            severity=Severity.LOW,
        )

        assert reading.severity == Severity.LOW
        assert reading.severity.value == 1

    def test_severity_medium(self) -> None:
        """Test severity accepts MEDIUM value (2)."""
        reading = CityEventReading(
            zone_id="zone-A",
            timestamp=datetime(2026, 2, 15, 12, 0, 0, tzinfo=timezone.utc),
            event_type=EventType.ACCIDENT,
            severity=Severity.MEDIUM,
        )

        assert reading.severity == Severity.MEDIUM
        assert reading.severity.value == 2

    def test_severity_high(self) -> None:
        """Test severity accepts HIGH value (3)."""
        reading = CityEventReading(
            zone_id="zone-A",
            timestamp=datetime(2026, 2, 15, 12, 0, 0, tzinfo=timezone.utc),
            event_type=EventType.EMERGENCY,
            severity=Severity.HIGH,
        )

        assert reading.severity == Severity.HIGH
        assert reading.severity.value == 3

    def test_severity_invalid_value_rejected(self) -> None:
        """Test severity rejects values outside 1-3 range."""
        with pytest.raises(ValueError):
            CityEventReading(
                zone_id="zone-A",
                timestamp=datetime(2026, 2, 15, 12, 0, 0, tzinfo=timezone.utc),
                event_type=EventType.ACCIDENT,
                severity=4,
            )

    def test_active_defaults_to_true(self) -> None:
        """Test that active field defaults to True."""
        reading = CityEventReading(
            zone_id="zone-A",
            timestamp=datetime(2026, 2, 15, 12, 0, 0, tzinfo=timezone.utc),
            event_type=EventType.ACCIDENT,
            severity=Severity.HIGH,
        )

        assert reading.active is True

    def test_active_can_be_false(self) -> None:
        """Test that active field can be set to False."""
        reading = CityEventReading(
            zone_id="zone-A",
            timestamp=datetime(2026, 2, 15, 12, 0, 0, tzinfo=timezone.utc),
            event_type=EventType.ACCIDENT,
            severity=Severity.HIGH,
            active=False,
        )

        assert reading.active is False

    def test_to_json_payload_contains_all_fields(self) -> None:
        """Test that to_json_payload produces correct JSON with all required fields."""
        reading = CityEventReading(
            zone_id="zone-A",
            city_id="lisbon",
            timestamp=datetime(2026, 2, 15, 10, 15, 0, tzinfo=timezone.utc),
            event_type=EventType.ACCIDENT,
            severity=Severity.HIGH,
            active=True,
        )

        payload = reading.to_json_payload()

        assert payload["type"] == "city_event"
        assert payload["schema_version"] == "1.0"
        assert payload["timestamp"] == "2026-02-15T10:15:00Z"
        assert payload["zone_id"] == "zone-A"
        assert payload["city_id"] == "lisbon"
        assert payload["event_type"] == "accident"
        assert payload["severity"] == 3
        assert payload["active"] is True

    def test_to_json_payload_serializable(self) -> None:
        """Test that payload can be serialized to valid JSON."""
        reading = CityEventReading(
            zone_id="zone-A",
            timestamp=datetime(2026, 2, 15, 12, 0, 0, tzinfo=timezone.utc),
            event_type=EventType.EMERGENCY,
            severity=Severity.MEDIUM,
        )

        payload = reading.to_json_payload()
        json_str = json.dumps(payload)
        assert json_str is not None

        parsed = json.loads(json_str)
        assert parsed == payload


class TestVisibilityReading:
    """Tests for VisibilityReading data model."""

    def test_instantiation_with_valid_data(self) -> None:
        """Test that VisibilityReading can be instantiated with valid data."""
        reading = VisibilityReading(
            city_id="lisbon",
            timestamp=datetime(2026, 2, 15, 7, 0, 0, tzinfo=timezone.utc),
            fog_index=30.0,
            visibility=VisibilityLevel.MEDIUM,
            sunrise_time="07:15",
            sunset_time="18:05",
        )

        assert reading.type == "city_weather"
        assert reading.schema_version == "1.0"
        assert reading.city_id == "lisbon"
        assert reading.fog_index == 30.0
        assert reading.visibility == VisibilityLevel.MEDIUM
        assert reading.sunrise_time == "07:15"
        assert reading.sunset_time == "18:05"

    def test_required_fields_present(self) -> None:
        """Test that type, schema_version, and timestamp are present."""
        reading = VisibilityReading(
            timestamp=datetime(2026, 2, 15, 12, 0, 0, tzinfo=timezone.utc),
            fog_index=10.0,
            visibility=VisibilityLevel.GOOD,
            sunrise_time="06:45",
            sunset_time="19:30",
        )

        assert reading.type == "city_weather"
        assert reading.schema_version == "1.0"
        assert reading.timestamp == datetime(2026, 2, 15, 12, 0, 0, tzinfo=timezone.utc)

    def test_type_is_city_weather(self) -> None:
        """Test that the type field is always 'city_weather'."""
        reading = VisibilityReading(
            timestamp=datetime(2026, 2, 15, 12, 0, 0, tzinfo=timezone.utc),
            fog_index=0.0,
            visibility=VisibilityLevel.GOOD,
            sunrise_time="06:00",
            sunset_time="20:00",
        )

        assert reading.type == "city_weather"

    def test_fog_index_minimum(self) -> None:
        """Test fog_index accepts minimum value of 0."""
        reading = VisibilityReading(
            timestamp=datetime(2026, 2, 15, 12, 0, 0, tzinfo=timezone.utc),
            fog_index=0.0,
            visibility=VisibilityLevel.GOOD,
            sunrise_time="06:00",
            sunset_time="20:00",
        )

        assert reading.fog_index == 0.0

    def test_fog_index_maximum(self) -> None:
        """Test fog_index accepts maximum value of 100."""
        reading = VisibilityReading(
            timestamp=datetime(2026, 2, 15, 6, 0, 0, tzinfo=timezone.utc),
            fog_index=100.0,
            visibility=VisibilityLevel.POOR,
            sunrise_time="07:30",
            sunset_time="17:45",
        )

        assert reading.fog_index == 100.0

    def test_fog_index_below_range_rejected(self) -> None:
        """Test fog_index rejects values below 0."""
        with pytest.raises(ValueError):
            VisibilityReading(
                timestamp=datetime(2026, 2, 15, 12, 0, 0, tzinfo=timezone.utc),
                fog_index=-0.1,
                visibility=VisibilityLevel.GOOD,
                sunrise_time="06:00",
                sunset_time="20:00",
            )

    def test_fog_index_above_range_rejected(self) -> None:
        """Test fog_index rejects values above 100."""
        with pytest.raises(ValueError):
            VisibilityReading(
                timestamp=datetime(2026, 2, 15, 12, 0, 0, tzinfo=timezone.utc),
                fog_index=100.1,
                visibility=VisibilityLevel.POOR,
                sunrise_time="06:00",
                sunset_time="20:00",
            )

    def test_visibility_good(self) -> None:
        """Test visibility accepts GOOD enum value."""
        reading = VisibilityReading(
            timestamp=datetime(2026, 2, 15, 12, 0, 0, tzinfo=timezone.utc),
            fog_index=5.0,
            visibility=VisibilityLevel.GOOD,
            sunrise_time="06:00",
            sunset_time="20:00",
        )

        assert reading.visibility == VisibilityLevel.GOOD
        assert reading.visibility.value == "good"

    def test_visibility_medium(self) -> None:
        """Test visibility accepts MEDIUM enum value."""
        reading = VisibilityReading(
            timestamp=datetime(2026, 2, 15, 12, 0, 0, tzinfo=timezone.utc),
            fog_index=45.0,
            visibility=VisibilityLevel.MEDIUM,
            sunrise_time="06:00",
            sunset_time="20:00",
        )

        assert reading.visibility == VisibilityLevel.MEDIUM
        assert reading.visibility.value == "medium"

    def test_visibility_poor(self) -> None:
        """Test visibility accepts POOR enum value."""
        reading = VisibilityReading(
            timestamp=datetime(2026, 2, 15, 12, 0, 0, tzinfo=timezone.utc),
            fog_index=85.0,
            visibility=VisibilityLevel.POOR,
            sunrise_time="06:00",
            sunset_time="20:00",
        )

        assert reading.visibility == VisibilityLevel.POOR
        assert reading.visibility.value == "poor"

    def test_sunrise_and_sunset_times(self) -> None:
        """Test that sunrise_time and sunset_time are stored correctly."""
        reading = VisibilityReading(
            timestamp=datetime(2026, 2, 15, 12, 0, 0, tzinfo=timezone.utc),
            fog_index=20.0,
            visibility=VisibilityLevel.GOOD,
            sunrise_time="07:22",
            sunset_time="17:58",
        )

        assert reading.sunrise_time == "07:22"
        assert reading.sunset_time == "17:58"

    def test_to_json_payload_contains_all_fields(self) -> None:
        """Test that to_json_payload produces correct JSON with all required fields."""
        reading = VisibilityReading(
            city_id="lisbon",
            timestamp=datetime(2026, 2, 15, 7, 30, 0, tzinfo=timezone.utc),
            fog_index=45.5,
            visibility=VisibilityLevel.MEDIUM,
            sunrise_time="07:15",
            sunset_time="18:05",
        )

        payload = reading.to_json_payload()

        assert payload["type"] == "city_weather"
        assert payload["schema_version"] == "1.0"
        assert payload["timestamp"] == "2026-02-15T07:30:00Z"
        assert payload["city_id"] == "lisbon"
        assert payload["fog_index"] == 45.5
        assert payload["visibility"] == "medium"
        assert payload["sunrise_time"] == "07:15"
        assert payload["sunset_time"] == "18:05"

    def test_to_json_payload_serializable(self) -> None:
        """Test that payload can be serialized to valid JSON."""
        reading = VisibilityReading(
            timestamp=datetime(2026, 2, 15, 12, 0, 0, tzinfo=timezone.utc),
            fog_index=10.0,
            visibility=VisibilityLevel.GOOD,
            sunrise_time="06:30",
            sunset_time="19:45",
        )

        payload = reading.to_json_payload()
        json_str = json.dumps(payload)
        assert json_str is not None

        parsed = json.loads(json_str)
        assert parsed == payload


class TestAllModelsCommonFields:
    """Tests that verify common fields across all smart city models."""

    def test_all_models_have_type_field(self) -> None:
        """Test that all four models have a type field."""
        streetlight = StreetlightReading(
            zone_id="zone-A",
            light_id="light-001",
            timestamp=datetime(2026, 2, 15, 12, 0, 0, tzinfo=timezone.utc),
            dimming_level_pct=50.0,
            power_w=75.0,
        )
        traffic = TrafficReading(
            zone_id="zone-A",
            timestamp=datetime(2026, 2, 15, 12, 0, 0, tzinfo=timezone.utc),
            traffic_index=50.0,
        )
        event = CityEventReading(
            zone_id="zone-A",
            timestamp=datetime(2026, 2, 15, 12, 0, 0, tzinfo=timezone.utc),
            event_type=EventType.ACCIDENT,
            severity=Severity.HIGH,
        )
        visibility = VisibilityReading(
            timestamp=datetime(2026, 2, 15, 12, 0, 0, tzinfo=timezone.utc),
            fog_index=20.0,
            visibility=VisibilityLevel.GOOD,
            sunrise_time="06:30",
            sunset_time="19:45",
        )

        assert streetlight.type == "streetlight"
        assert traffic.type == "traffic"
        assert event.type == "city_event"
        assert visibility.type == "city_weather"

    def test_all_models_have_schema_version(self) -> None:
        """Test that all four models have a schema_version field defaulting to '1.0'."""
        streetlight = StreetlightReading(
            zone_id="zone-A",
            light_id="light-001",
            timestamp=datetime(2026, 2, 15, 12, 0, 0, tzinfo=timezone.utc),
            dimming_level_pct=50.0,
            power_w=75.0,
        )
        traffic = TrafficReading(
            zone_id="zone-A",
            timestamp=datetime(2026, 2, 15, 12, 0, 0, tzinfo=timezone.utc),
            traffic_index=50.0,
        )
        event = CityEventReading(
            zone_id="zone-A",
            timestamp=datetime(2026, 2, 15, 12, 0, 0, tzinfo=timezone.utc),
            event_type=EventType.ACCIDENT,
            severity=Severity.HIGH,
        )
        visibility = VisibilityReading(
            timestamp=datetime(2026, 2, 15, 12, 0, 0, tzinfo=timezone.utc),
            fog_index=20.0,
            visibility=VisibilityLevel.GOOD,
            sunrise_time="06:30",
            sunset_time="19:45",
        )

        assert streetlight.schema_version == "1.0"
        assert traffic.schema_version == "1.0"
        assert event.schema_version == "1.0"
        assert visibility.schema_version == "1.0"

    def test_all_models_have_timestamp(self) -> None:
        """Test that all four models have a timestamp field."""
        ts = datetime(2026, 2, 15, 12, 0, 0, tzinfo=timezone.utc)

        streetlight = StreetlightReading(
            zone_id="zone-A",
            light_id="light-001",
            timestamp=ts,
            dimming_level_pct=50.0,
            power_w=75.0,
        )
        traffic = TrafficReading(
            zone_id="zone-A",
            timestamp=ts,
            traffic_index=50.0,
        )
        event = CityEventReading(
            zone_id="zone-A",
            timestamp=ts,
            event_type=EventType.ACCIDENT,
            severity=Severity.HIGH,
        )
        visibility = VisibilityReading(
            timestamp=ts,
            fog_index=20.0,
            visibility=VisibilityLevel.GOOD,
            sunrise_time="06:30",
            sunset_time="19:45",
        )

        assert streetlight.timestamp == ts
        assert traffic.timestamp == ts
        assert event.timestamp == ts
        assert visibility.timestamp == ts

    def test_all_payloads_have_required_keys(self) -> None:
        """Test that all to_json_payload outputs contain type, schema_version, timestamp."""
        ts = datetime(2026, 2, 15, 12, 0, 0, tzinfo=timezone.utc)

        models = [
            StreetlightReading(
                zone_id="zone-A",
                light_id="light-001",
                timestamp=ts,
                dimming_level_pct=50.0,
                power_w=75.0,
            ),
            TrafficReading(
                zone_id="zone-A",
                timestamp=ts,
                traffic_index=50.0,
            ),
            CityEventReading(
                zone_id="zone-A",
                timestamp=ts,
                event_type=EventType.ACCIDENT,
                severity=Severity.HIGH,
            ),
            VisibilityReading(
                timestamp=ts,
                fog_index=20.0,
                visibility=VisibilityLevel.GOOD,
                sunrise_time="06:30",
                sunset_time="19:45",
            ),
        ]

        for model in models:
            payload = model.to_json_payload()
            assert "type" in payload, f"Missing 'type' in {model.__class__.__name__}"
            assert "schema_version" in payload, (
                f"Missing 'schema_version' in {model.__class__.__name__}"
            )
            assert "timestamp" in payload, f"Missing 'timestamp' in {model.__class__.__name__}"
            assert payload["timestamp"].endswith("Z"), (
                f"Timestamp should end with 'Z' in {model.__class__.__name__}"
            )
