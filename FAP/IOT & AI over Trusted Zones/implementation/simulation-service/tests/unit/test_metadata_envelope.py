"""Tests for metadata envelope fields across all Smart Energy models.

Verifies that every model includes the required metadata fields
(type, schema_version, timestamp) in its JSON payload, alongside
its domain-specific fields.
"""

from datetime import datetime, timezone

import pytest

from src.models.consumer_load import (
    ConsumerLoadConfig,
    ConsumerLoadReading,
    DeviceState,
    DeviceType,
)
from src.models.meter import MeterConfig, MeterReading, MeterReadings
from src.models.price import PriceReading, TariffType
from src.models.pv import PVConfig, PVReading, PVReadings
from src.models.weather import LocationData, WeatherConditions, WeatherReading

SAMPLE_TIMESTAMP = datetime(2026, 2, 15, 10, 30, 0, tzinfo=timezone.utc)


def _make_meter_reading() -> MeterReading:
    """Build a realistic MeterReading for the Berlin campus meter."""
    readings = MeterReadings(
        active_power_l1_w=3500.0,
        active_power_l2_w=3200.0,
        active_power_l3_w=3100.0,
        voltage_l1_v=230.4,
        voltage_l2_v=229.8,
        voltage_l3_v=230.1,
        current_l1_a=15.2,
        current_l2_a=13.9,
        current_l3_a=13.5,
        power_factor=0.97,
        frequency_hz=50.01,
        total_energy_kwh=12450.75,
    )
    return MeterReading(
        site_id="site-berlin-001",
        timestamp=SAMPLE_TIMESTAMP,
        meter_id="meter-001",
        readings=readings,
    )


def _make_pv_reading() -> PVReading:
    """Build a realistic PVReading for a 10 kWp rooftop array."""
    readings = PVReadings(
        power_output_kw=7.85,
        daily_energy_kwh=32.4,
        irradiance_w_m2=820.0,
        module_temperature_c=38.2,
        efficiency_percent=16.3,
    )
    return PVReading(
        site_id="site-berlin-001",
        timestamp=SAMPLE_TIMESTAMP,
        system_id="pv-system-001",
        readings=readings,
    )


def _make_weather_reading() -> WeatherReading:
    """Build a realistic WeatherReading for Berlin in February."""
    location = LocationData(latitude=52.52, longitude=13.405)
    conditions = WeatherConditions(
        temperature_c=4.3,
        humidity_percent=72.0,
        wind_speed_ms=3.8,
        wind_direction_deg=245.0,
        cloud_cover_percent=55.0,
        ghi_w_m2=280.0,
        dni_w_m2=350.0,
        dhi_w_m2=95.0,
    )
    return WeatherReading(
        site_id="site-berlin-001",
        timestamp=SAMPLE_TIMESTAMP,
        location=location,
        conditions=conditions,
    )


def _make_price_reading() -> PriceReading:
    """Build a realistic PriceReading for a midday tariff period."""
    return PriceReading(
        timestamp=SAMPLE_TIMESTAMP,
        price_eur_per_kwh=0.2645,
        tariff_type=TariffType.MIDDAY,
    )


def _make_consumer_load_reading() -> ConsumerLoadReading:
    """Build a realistic ConsumerLoadReading for an industrial oven."""
    return ConsumerLoadReading(
        site_id="site-berlin-001",
        timestamp=SAMPLE_TIMESTAMP,
        device_id="oven-001",
        device_type=DeviceType.INDUSTRIAL_OVEN,
        device_state=DeviceState.ON,
        device_power_kw=3.42,
    )


class TestMeterReadingEnvelope:
    """Metadata envelope tests for MeterReading."""

    def test_type_field(self) -> None:
        """Test payload includes correct type literal."""
        payload = _make_meter_reading().to_json_payload()
        assert payload["type"] == "energy_meter"

    def test_schema_version(self) -> None:
        """Test payload includes schema_version 1.0."""
        payload = _make_meter_reading().to_json_payload()
        assert payload["schema_version"] == "1.0"

    def test_timestamp_iso8601(self) -> None:
        """Test timestamp is ISO 8601 string ending in Z."""
        payload = _make_meter_reading().to_json_payload()
        assert isinstance(payload["timestamp"], str)
        assert payload["timestamp"].endswith("Z")

    def test_domain_fields_present(self) -> None:
        """Test payload contains site_id, asset_id, active_power_kw, active_energy_kwh_total."""
        payload = _make_meter_reading().to_json_payload()
        assert "site_id" in payload
        assert "asset_id" in payload
        assert "active_power_kw" in payload
        assert "active_energy_kwh_total" in payload

    def test_active_power_computed(self) -> None:
        """Test active_power_kw is the sum of all phases in kW."""
        reading = _make_meter_reading()
        payload = reading.to_json_payload()
        expected_kw = round((3500.0 + 3200.0 + 3100.0) / 1000.0, 3)
        assert payload["active_power_kw"] == expected_kw

    def test_asset_id_equals_meter_id(self) -> None:
        """Test asset_id mirrors meter_id."""
        payload = _make_meter_reading().to_json_payload()
        assert payload["asset_id"] == "meter-001"


class TestPVReadingEnvelope:
    """Metadata envelope tests for PVReading."""

    def test_type_field(self) -> None:
        """Test payload includes correct type literal."""
        payload = _make_pv_reading().to_json_payload()
        assert payload["type"] == "pv_generation"

    def test_schema_version(self) -> None:
        """Test payload includes schema_version 1.0."""
        payload = _make_pv_reading().to_json_payload()
        assert payload["schema_version"] == "1.0"

    def test_timestamp_iso8601(self) -> None:
        """Test timestamp is ISO 8601 string ending in Z."""
        payload = _make_pv_reading().to_json_payload()
        assert isinstance(payload["timestamp"], str)
        assert payload["timestamp"].endswith("Z")

    def test_domain_fields_present(self) -> None:
        """Test payload contains site_id, asset_id, pv_power_kw, pv_system_id."""
        payload = _make_pv_reading().to_json_payload()
        assert "site_id" in payload
        assert "asset_id" in payload
        assert "pv_power_kw" in payload
        assert "pv_system_id" in payload

    def test_asset_id_equals_system_id(self) -> None:
        """Test asset_id mirrors system_id."""
        payload = _make_pv_reading().to_json_payload()
        assert payload["asset_id"] == "pv-system-001"


class TestWeatherReadingEnvelope:
    """Metadata envelope tests for WeatherReading."""

    def test_type_field(self) -> None:
        """Test payload includes correct type literal."""
        payload = _make_weather_reading().to_json_payload()
        assert payload["type"] == "weather"

    def test_schema_version(self) -> None:
        """Test payload includes schema_version 1.0."""
        payload = _make_weather_reading().to_json_payload()
        assert payload["schema_version"] == "1.0"

    def test_timestamp_iso8601(self) -> None:
        """Test timestamp is ISO 8601 string ending in Z."""
        payload = _make_weather_reading().to_json_payload()
        assert isinstance(payload["timestamp"], str)
        assert payload["timestamp"].endswith("Z")

    def test_domain_fields_present(self) -> None:
        """Test payload contains site_id, temperature_c, solar_irradiance_w_m2."""
        payload = _make_weather_reading().to_json_payload()
        assert "site_id" in payload
        assert "temperature_c" in payload
        assert "solar_irradiance_w_m2" in payload

    def test_temperature_matches_conditions(self) -> None:
        """Test top-level temperature_c matches nested conditions value."""
        payload = _make_weather_reading().to_json_payload()
        assert payload["temperature_c"] == payload["conditions"]["temperature_c"]


class TestPriceReadingEnvelope:
    """Metadata envelope tests for PriceReading."""

    def test_type_field(self) -> None:
        """Test payload includes correct type literal."""
        payload = _make_price_reading().to_json_payload()
        assert payload["type"] == "energy_price"

    def test_schema_version(self) -> None:
        """Test payload includes schema_version 1.0."""
        payload = _make_price_reading().to_json_payload()
        assert payload["schema_version"] == "1.0"

    def test_timestamp_iso8601(self) -> None:
        """Test timestamp is ISO 8601 string ending in Z."""
        payload = _make_price_reading().to_json_payload()
        assert isinstance(payload["timestamp"], str)
        assert payload["timestamp"].endswith("Z")

    def test_domain_fields_present(self) -> None:
        """Test payload contains price_eur_per_kwh and tariff_type but no site_id."""
        payload = _make_price_reading().to_json_payload()
        assert "price_eur_per_kwh" in payload
        assert "tariff_type" in payload
        assert "site_id" not in payload

    def test_tariff_type_value(self) -> None:
        """Test tariff_type is serialised as its string value."""
        payload = _make_price_reading().to_json_payload()
        assert payload["tariff_type"] == "midday"


class TestConsumerLoadReadingEnvelope:
    """Metadata envelope tests for ConsumerLoadReading."""

    def test_type_field(self) -> None:
        """Test payload includes correct type literal."""
        payload = _make_consumer_load_reading().to_json_payload()
        assert payload["type"] == "consumer"

    def test_schema_version(self) -> None:
        """Test payload includes schema_version 1.0."""
        payload = _make_consumer_load_reading().to_json_payload()
        assert payload["schema_version"] == "1.0"

    def test_timestamp_iso8601(self) -> None:
        """Test timestamp is ISO 8601 string ending in Z."""
        payload = _make_consumer_load_reading().to_json_payload()
        assert isinstance(payload["timestamp"], str)
        assert payload["timestamp"].endswith("Z")

    def test_domain_fields_present(self) -> None:
        """Test payload contains site_id, asset_id, device_power_kw, device_state."""
        payload = _make_consumer_load_reading().to_json_payload()
        assert "site_id" in payload
        assert "asset_id" in payload
        assert "device_power_kw" in payload
        assert "device_state" in payload

    def test_device_state_value(self) -> None:
        """Test device_state is serialised as its string value."""
        payload = _make_consumer_load_reading().to_json_payload()
        assert payload["device_state"] == "ON"

    def test_asset_id_equals_device_id(self) -> None:
        """Test asset_id mirrors device_id."""
        payload = _make_consumer_load_reading().to_json_payload()
        assert payload["asset_id"] == "oven-001"
