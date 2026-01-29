"""Tests for energy meter simulator."""

import json
from datetime import datetime, timedelta, timezone

import pytest

from src.core.random_generator import DeterministicRNG
from src.core.time_series import IntervalMinutes, TimeRange
from src.models.meter import MeterConfig, MeterReading
from src.simulators.energy_meter import (
    DayType,
    EnergyMeterSimulator,
    get_day_type,
    get_load_factor,
)


class TestLoadCurves:
    """Tests for load curve functionality."""

    def test_get_day_type_weekday(self) -> None:
        """Test that Monday-Friday are identified as weekdays."""
        # Monday 2024-01-01
        monday = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        assert get_day_type(monday) == DayType.WEEKDAY

        # Friday 2024-01-05
        friday = datetime(2024, 1, 5, 12, 0, 0, tzinfo=timezone.utc)
        assert get_day_type(friday) == DayType.WEEKDAY

    def test_get_day_type_weekend(self) -> None:
        """Test that Saturday-Sunday are identified as weekend."""
        # Saturday 2024-01-06
        saturday = datetime(2024, 1, 6, 12, 0, 0, tzinfo=timezone.utc)
        assert get_day_type(saturday) == DayType.WEEKEND

        # Sunday 2024-01-07
        sunday = datetime(2024, 1, 7, 12, 0, 0, tzinfo=timezone.utc)
        assert get_day_type(sunday) == DayType.WEEKEND

    def test_load_factor_peak_hours_weekday(self) -> None:
        """Test that load factor is higher during peak hours on weekdays."""
        # Monday at 10:00 (peak)
        peak_time = datetime(2024, 1, 1, 10, 0, 0, tzinfo=timezone.utc)
        peak_factor = get_load_factor(peak_time)

        # Monday at 03:00 (off-peak)
        offpeak_time = datetime(2024, 1, 1, 3, 0, 0, tzinfo=timezone.utc)
        offpeak_factor = get_load_factor(offpeak_time)

        assert peak_factor > offpeak_factor
        assert peak_factor >= 0.9  # Peak should be high
        assert offpeak_factor <= 0.4  # Off-peak should be low

    def test_load_factor_weekend_lower(self) -> None:
        """Test that weekend load is lower than weekday at same hour."""
        # Monday 10:00
        weekday_time = datetime(2024, 1, 1, 10, 0, 0, tzinfo=timezone.utc)
        weekday_factor = get_load_factor(weekday_time)

        # Saturday 10:00
        weekend_time = datetime(2024, 1, 6, 10, 0, 0, tzinfo=timezone.utc)
        weekend_factor = get_load_factor(weekend_time)

        assert weekend_factor < weekday_factor
        # Weekend should be roughly 60% of weekday
        assert weekend_factor < weekday_factor * 0.7

    def test_load_factor_interpolation(self) -> None:
        """Test that load factor interpolates smoothly between hours."""
        base_time = datetime(2024, 1, 1, 10, 0, 0, tzinfo=timezone.utc)

        # Get factors at 10:00, 10:15, 10:30, 10:45
        factors = []
        for minutes in [0, 15, 30, 45]:
            ts = base_time.replace(minute=minutes)
            factors.append(get_load_factor(ts))

        # Values should change gradually
        for i in range(len(factors) - 1):
            diff = abs(factors[i + 1] - factors[i])
            assert diff < 0.1  # No sudden jumps


class TestMeterReading:
    """Tests for meter reading data model."""

    def test_meter_reading_to_json_payload(self) -> None:
        """Test that meter reading converts to correct JSON format."""
        from src.models.meter import MeterReadings

        reading = MeterReading(
            timestamp=datetime(2026, 1, 21, 14, 30, 0, tzinfo=timezone.utc),
            meter_id="janitza-umg96rm-001",
            readings=MeterReadings(
                active_power_l1_w=1234.5,
                active_power_l2_w=1156.2,
                active_power_l3_w=1089.7,
                voltage_l1_v=230.5,
                voltage_l2_v=231.2,
                voltage_l3_v=229.8,
                current_l1_a=5.36,
                current_l2_a=5.01,
                current_l3_a=4.74,
                power_factor=0.95,
                frequency_hz=50.01,
                total_energy_kwh=15234.56,
            ),
        )

        payload = reading.to_json_payload()

        assert payload["timestamp"] == "2026-01-21T14:30:00Z"
        assert payload["meter_id"] == "janitza-umg96rm-001"
        assert payload["readings"]["active_power_l1_w"] == 1234.5
        assert payload["readings"]["voltage_l1_v"] == 230.5
        assert payload["readings"]["current_l1_a"] == 5.36
        assert payload["readings"]["power_factor"] == 0.95
        assert payload["readings"]["frequency_hz"] == 50.01
        assert payload["readings"]["total_energy_kwh"] == 15234.56

        # Verify it's valid JSON
        json_str = json.dumps(payload)
        assert json_str is not None


class TestEnergyMeterSimulator:
    """Tests for EnergyMeterSimulator class."""

    def test_initialization_with_defaults(self) -> None:
        """Test simulator initializes with default configuration."""
        rng = DeterministicRNG(seed=12345)
        simulator = EnergyMeterSimulator("meter-001", rng)

        assert simulator.entity_id == "meter-001"
        assert simulator.config.meter_id == "meter-001"
        assert simulator.config.base_power_kw == 10.0
        assert simulator.config.peak_power_kw == 25.0

    def test_initialization_with_custom_config(self) -> None:
        """Test simulator initializes with custom configuration."""
        rng = DeterministicRNG(seed=12345)
        config = MeterConfig(
            meter_id="custom-meter",
            base_power_kw=5.0,
            peak_power_kw=50.0,
            initial_energy_kwh=1000.0,
        )
        simulator = EnergyMeterSimulator("custom-meter", rng, config=config)

        assert simulator.config.base_power_kw == 5.0
        assert simulator.config.peak_power_kw == 50.0
        assert simulator.config.initial_energy_kwh == 1000.0

    def test_generate_single_reading(self) -> None:
        """Test generating a single meter reading."""
        rng = DeterministicRNG(seed=12345)
        simulator = EnergyMeterSimulator("meter-001", rng)

        timestamp = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        point = simulator.generate_at(timestamp)

        reading = point.value
        assert isinstance(reading, MeterReading)
        assert reading.meter_id == "meter-001"
        assert reading.readings.active_power_l1_w > 0
        assert reading.readings.voltage_l1_v > 0
        assert reading.readings.current_l1_a > 0

    def test_voltage_within_tolerance(self) -> None:
        """Test that voltage is within ±5% of 230V nominal."""
        rng = DeterministicRNG(seed=12345)
        simulator = EnergyMeterSimulator("meter-001", rng)

        # Generate multiple readings
        for hour in range(24):
            timestamp = datetime(2024, 1, 1, hour, 0, 0, tzinfo=timezone.utc)
            reading = simulator.generate_at(timestamp).value

            # Check all phases are within tolerance
            nominal = 230.0
            tolerance = nominal * 0.05  # 5%

            assert abs(reading.readings.voltage_l1_v - nominal) <= tolerance
            assert abs(reading.readings.voltage_l2_v - nominal) <= tolerance
            assert abs(reading.readings.voltage_l3_v - nominal) <= tolerance

    def test_power_factor_in_range(self) -> None:
        """Test that power factor is between 0.95 and 0.99."""
        rng = DeterministicRNG(seed=12345)
        simulator = EnergyMeterSimulator("meter-001", rng)

        for hour in range(24):
            timestamp = datetime(2024, 1, 1, hour, 0, 0, tzinfo=timezone.utc)
            reading = simulator.generate_at(timestamp).value

            assert 0.95 <= reading.readings.power_factor <= 0.99

    def test_frequency_within_tolerance(self) -> None:
        """Test that frequency is within ±0.05Hz of 50Hz."""
        rng = DeterministicRNG(seed=12345)
        simulator = EnergyMeterSimulator("meter-001", rng)

        for hour in range(24):
            timestamp = datetime(2024, 1, 1, hour, 0, 0, tzinfo=timezone.utc)
            reading = simulator.generate_at(timestamp).value

            assert abs(reading.readings.frequency_hz - 50.0) <= 0.05

    def test_current_correlates_with_power(self) -> None:
        """Test that current values correlate with power draw."""
        rng = DeterministicRNG(seed=12345)
        simulator = EnergyMeterSimulator("meter-001", rng)

        # Generate readings at peak (high power) and off-peak (low power)
        peak_time = datetime(2024, 1, 1, 10, 0, 0, tzinfo=timezone.utc)
        offpeak_time = datetime(2024, 1, 1, 3, 0, 0, tzinfo=timezone.utc)

        peak_reading = simulator.generate_at(peak_time).value
        offpeak_reading = simulator.generate_at(offpeak_time).value

        # Total power
        peak_power = (
            peak_reading.readings.active_power_l1_w
            + peak_reading.readings.active_power_l2_w
            + peak_reading.readings.active_power_l3_w
        )
        offpeak_power = (
            offpeak_reading.readings.active_power_l1_w
            + offpeak_reading.readings.active_power_l2_w
            + offpeak_reading.readings.active_power_l3_w
        )

        # Total current
        peak_current = (
            peak_reading.readings.current_l1_a
            + peak_reading.readings.current_l2_a
            + peak_reading.readings.current_l3_a
        )
        offpeak_current = (
            offpeak_reading.readings.current_l1_a
            + offpeak_reading.readings.current_l2_a
            + offpeak_reading.readings.current_l3_a
        )

        # Higher power should mean higher current
        assert peak_power > offpeak_power
        assert peak_current > offpeak_current


class TestEnergyAccumulation:
    """Tests for cumulative energy tracking."""

    def test_energy_always_increasing(self) -> None:
        """Test that cumulative energy is always increasing."""
        rng = DeterministicRNG(seed=12345)
        simulator = EnergyMeterSimulator("meter-001", rng)

        time_range = TimeRange.from_iso(
            "2024-01-01T00:00:00",
            "2024-01-02T00:00:00",
        )

        readings = simulator.generate_range_with_energy_tracking(time_range)

        prev_energy = 0.0
        for reading in readings:
            assert reading.readings.total_energy_kwh >= prev_energy
            prev_energy = reading.readings.total_energy_kwh

    def test_energy_increment_proportional_to_power(self) -> None:
        """Test that energy increment is proportional to power."""
        rng = DeterministicRNG(seed=12345)
        config = MeterConfig(
            meter_id="meter-001",
            base_power_kw=10.0,
            peak_power_kw=10.0,  # Constant power for easier testing
            initial_energy_kwh=0.0,
        )
        simulator = EnergyMeterSimulator("meter-001", rng, config=config)

        time_range = TimeRange.from_iso(
            "2024-01-01T00:00:00",
            "2024-01-01T01:00:00",  # 1 hour
        )

        readings = simulator.generate_range_with_energy_tracking(time_range)

        # With constant 10kW for 1 hour, energy should be approximately 10 kWh
        # (5 readings at 15-min intervals = 1.25 hours of increments)
        final_reading = readings[-1]

        # Allow variance due to noise in power values and 5 intervals * 0.25h = 1.25h
        # Expected: ~10kW * 1.25h = ~12.5 kWh (accounting for 5 intervals)
        assert 8.0 <= final_reading.readings.total_energy_kwh <= 15.0


class TestDailyPatterns:
    """Tests for daily load patterns."""

    def test_weekday_vs_weekend_power(self) -> None:
        """Test that weekend power is lower than weekday."""
        rng = DeterministicRNG(seed=12345)
        simulator = EnergyMeterSimulator("meter-001", rng)

        # Monday 10:00 (peak weekday)
        weekday_time = datetime(2024, 1, 1, 10, 0, 0, tzinfo=timezone.utc)
        weekday_reading = simulator.generate_at(weekday_time).value

        # Saturday 10:00 (weekend)
        weekend_time = datetime(2024, 1, 6, 10, 0, 0, tzinfo=timezone.utc)
        weekend_reading = simulator.generate_at(weekend_time).value

        weekday_power = (
            weekday_reading.readings.active_power_l1_w
            + weekday_reading.readings.active_power_l2_w
            + weekday_reading.readings.active_power_l3_w
        )
        weekend_power = (
            weekend_reading.readings.active_power_l1_w
            + weekend_reading.readings.active_power_l2_w
            + weekend_reading.readings.active_power_l3_w
        )

        # Weekend should be significantly lower (roughly 60%)
        assert weekend_power < weekday_power
        assert weekend_power < weekday_power * 0.8

    def test_power_follows_daily_curve(self) -> None:
        """Test that power follows the expected daily curve."""
        rng = DeterministicRNG(seed=12345)
        simulator = EnergyMeterSimulator("meter-001", rng)

        # Generate readings for a full weekday
        hourly_powers = []
        for hour in range(24):
            timestamp = datetime(2024, 1, 1, hour, 0, 0, tzinfo=timezone.utc)
            reading = simulator.generate_at(timestamp).value
            total_power = (
                reading.readings.active_power_l1_w
                + reading.readings.active_power_l2_w
                + reading.readings.active_power_l3_w
            )
            hourly_powers.append(total_power)

        # Morning should be lower than midday
        assert hourly_powers[6] < hourly_powers[10]

        # Midday (10:00) should be higher than midnight
        assert hourly_powers[10] > hourly_powers[0]

        # Lunch dip should be visible (12:00 slightly lower than 10:00 and 14:00)
        assert hourly_powers[12] < hourly_powers[10]


class TestDeterminism:
    """Tests for deterministic behavior."""

    def test_same_seed_produces_identical_readings(self) -> None:
        """Test that same seed produces identical readings."""
        timestamp = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)

        results = []
        for _ in range(5):
            rng = DeterministicRNG(seed=12345)
            simulator = EnergyMeterSimulator("meter-001", rng)
            reading = simulator.generate_at(timestamp).value
            results.append(reading.readings.active_power_l1_w)

        assert all(r == results[0] for r in results)

    def test_different_meters_produce_different_readings(self) -> None:
        """Test that different meters produce different readings."""
        timestamp = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        rng = DeterministicRNG(seed=12345)

        sim1 = EnergyMeterSimulator("meter-001", rng)
        sim2 = EnergyMeterSimulator("meter-002", rng)

        reading1 = sim1.generate_at(timestamp).value
        reading2 = sim2.generate_at(timestamp).value

        # Power values should be different due to different entity seeds
        assert reading1.readings.active_power_l1_w != reading2.readings.active_power_l1_w


class TestJSONPayload:
    """Tests for JSON payload format."""

    def test_json_payload_structure(self) -> None:
        """Test that JSON payload matches spec structure exactly."""
        rng = DeterministicRNG(seed=12345)
        simulator = EnergyMeterSimulator("janitza-umg96rm-001", rng)

        timestamp = datetime(2026, 1, 21, 14, 30, 0, tzinfo=timezone.utc)
        reading = simulator.generate_at(timestamp).value

        payload = reading.to_json_payload()

        # Check required fields
        assert "timestamp" in payload
        assert "meter_id" in payload
        assert "readings" in payload

        # Check readings structure
        readings = payload["readings"]
        required_fields = [
            "active_power_l1_w",
            "active_power_l2_w",
            "active_power_l3_w",
            "voltage_l1_v",
            "voltage_l2_v",
            "voltage_l3_v",
            "current_l1_a",
            "current_l2_a",
            "current_l3_a",
            "power_factor",
            "frequency_hz",
            "total_energy_kwh",
        ]
        for field in required_fields:
            assert field in readings

        # Check timestamp format (ISO 8601 with Z suffix)
        assert payload["timestamp"].endswith("Z")

    def test_json_serialization(self) -> None:
        """Test that payload can be serialized to valid JSON."""
        rng = DeterministicRNG(seed=12345)
        simulator = EnergyMeterSimulator("meter-001", rng)

        timestamp = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        reading = simulator.generate_at(timestamp).value
        payload = reading.to_json_payload()

        # Should serialize without errors
        json_str = json.dumps(payload, indent=2)
        assert json_str is not None

        # Should deserialize back
        parsed = json.loads(json_str)
        assert parsed == payload
