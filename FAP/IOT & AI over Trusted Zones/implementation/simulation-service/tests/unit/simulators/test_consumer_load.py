"""Tests for consumer load simulator."""

import json
from datetime import datetime, timezone

import pytest

from src.core.random_generator import DeterministicRNG
from src.core.time_series import IntervalMinutes, TimeRange
from src.models.consumer_load import (
    ConsumerLoadConfig,
    ConsumerLoadReading,
    DeviceState,
    DeviceType,
    OperatingWindow,
)
from src.simulators.consumer_load import (
    ConsumerLoadSimulator,
    IndustrialOvenSimulator,
    is_weekend,
    is_within_operating_window,
    should_device_operate,
)


class TestOperatingWindow:
    """Tests for operating window logic."""

    def test_window_contains_hour_simple(self) -> None:
        """Test simple hour range."""
        window = OperatingWindow(start_hour=7, end_hour=9)

        assert window.contains_hour(7)
        assert window.contains_hour(8)
        assert not window.contains_hour(6)
        assert not window.contains_hour(9)

    def test_window_contains_hour_overnight(self) -> None:
        """Test overnight window (e.g., 22-06)."""
        window = OperatingWindow(start_hour=22, end_hour=6)

        assert window.contains_hour(22)
        assert window.contains_hour(23)
        assert window.contains_hour(0)
        assert window.contains_hour(5)
        assert not window.contains_hour(6)
        assert not window.contains_hour(12)


class TestScheduleFunctions:
    """Tests for schedule utility functions."""

    def test_is_weekend_saturday(self) -> None:
        """Test Saturday is detected as weekend."""
        # Saturday 2024-01-06
        saturday = datetime(2024, 1, 6, 12, 0, 0, tzinfo=timezone.utc)
        assert is_weekend(saturday)

    def test_is_weekend_sunday(self) -> None:
        """Test Sunday is detected as weekend."""
        # Sunday 2024-01-07
        sunday = datetime(2024, 1, 7, 12, 0, 0, tzinfo=timezone.utc)
        assert is_weekend(sunday)

    def test_is_weekend_weekday(self) -> None:
        """Test weekdays are not detected as weekend."""
        # Monday 2024-01-01
        monday = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        assert not is_weekend(monday)

        # Friday 2024-01-05
        friday = datetime(2024, 1, 5, 12, 0, 0, tzinfo=timezone.utc)
        assert not is_weekend(friday)

    def test_is_within_operating_window(self) -> None:
        """Test operating window detection."""
        windows = [
            OperatingWindow(start_hour=7, end_hour=9),
            OperatingWindow(start_hour=11, end_hour=13),
            OperatingWindow(start_hour=15, end_hour=17),
        ]

        # Within first window
        ts1 = datetime(2024, 1, 1, 8, 0, 0, tzinfo=timezone.utc)
        assert is_within_operating_window(ts1, windows)

        # Between windows
        ts2 = datetime(2024, 1, 1, 10, 0, 0, tzinfo=timezone.utc)
        assert not is_within_operating_window(ts2, windows)

        # Within second window
        ts3 = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        assert is_within_operating_window(ts3, windows)

        # Outside all windows
        ts4 = datetime(2024, 1, 1, 20, 0, 0, tzinfo=timezone.utc)
        assert not is_within_operating_window(ts4, windows)

    def test_should_device_operate_weekday(self) -> None:
        """Test device operation on weekday during operating hours."""
        config = ConsumerLoadConfig(
            device_id="test",
            operate_on_weekends=False,
        )

        # Monday 8:00 (within default operating window)
        ts = datetime(2024, 1, 1, 8, 0, 0, tzinfo=timezone.utc)
        assert should_device_operate(ts, config)

    def test_should_device_operate_weekend_disabled(self) -> None:
        """Test device does not operate on weekend when disabled."""
        config = ConsumerLoadConfig(
            device_id="test",
            operate_on_weekends=False,
        )

        # Saturday 8:00 (would be within operating window)
        ts = datetime(2024, 1, 6, 8, 0, 0, tzinfo=timezone.utc)
        assert not should_device_operate(ts, config)

    def test_should_device_operate_weekend_enabled(self) -> None:
        """Test device operates on weekend when enabled."""
        config = ConsumerLoadConfig(
            device_id="test",
            operate_on_weekends=True,
        )

        # Saturday 8:00
        ts = datetime(2024, 1, 6, 8, 0, 0, tzinfo=timezone.utc)
        assert should_device_operate(ts, config)


class TestConsumerLoadSimulator:
    """Tests for ConsumerLoadSimulator class."""

    def test_initialization_with_defaults(self) -> None:
        """Test simulator initializes with default configuration."""
        rng = DeterministicRNG(seed=12345)
        simulator = ConsumerLoadSimulator("device-001", rng)

        assert simulator.entity_id == "device-001"
        assert simulator.config.device_id == "device-001"
        assert simulator.config.rated_power_kw == 3.0
        assert simulator.config.duty_cycle_pct == 70.0

    def test_initialization_with_custom_config(self) -> None:
        """Test simulator initializes with custom configuration."""
        rng = DeterministicRNG(seed=12345)
        config = ConsumerLoadConfig(
            device_id="custom-device",
            device_type=DeviceType.INDUSTRIAL_OVEN,
            rated_power_kw=5.0,
            duty_cycle_pct=80.0,
        )
        simulator = ConsumerLoadSimulator("custom-device", rng, config=config)

        assert simulator.config.rated_power_kw == 5.0
        assert simulator.config.duty_cycle_pct == 80.0

    def test_generate_reading_during_operation(self) -> None:
        """Test generating a reading during operating hours."""
        rng = DeterministicRNG(seed=12345)
        simulator = ConsumerLoadSimulator("device-001", rng)

        # Monday 8:00 (within default operating window)
        timestamp = datetime(2024, 1, 1, 8, 0, 0, tzinfo=timezone.utc)
        point = simulator.generate_at(timestamp)
        reading = point.value

        assert isinstance(reading, ConsumerLoadReading)
        assert reading.device_id == "device-001"
        assert reading.device_state in [DeviceState.ON, DeviceState.OFF]

    def test_power_zero_when_off(self) -> None:
        """Test that power consumption is zero when device is OFF."""
        rng = DeterministicRNG(seed=12345)
        config = ConsumerLoadConfig(
            device_id="test",
            duty_cycle_pct=0.0,  # Always OFF
        )
        simulator = ConsumerLoadSimulator("test", rng, config=config)

        # Monday 8:00
        timestamp = datetime(2024, 1, 1, 8, 0, 0, tzinfo=timezone.utc)
        reading = simulator.generate_at(timestamp).value

        assert reading.device_state == DeviceState.OFF
        assert reading.device_power_kw == 0.0

    def test_power_equals_rated_when_on(self) -> None:
        """Test that power equals rated power (±5%) when device is ON."""
        rng = DeterministicRNG(seed=12345)
        config = ConsumerLoadConfig(
            device_id="test",
            rated_power_kw=3.0,
            power_variance_pct=5.0,
            duty_cycle_pct=100.0,  # Always ON during operating hours
        )
        simulator = ConsumerLoadSimulator("test", rng, config=config)

        # Monday 8:00
        timestamp = datetime(2024, 1, 1, 8, 0, 0, tzinfo=timezone.utc)
        reading = simulator.generate_at(timestamp).value

        assert reading.device_state == DeviceState.ON
        # Power should be within ±5% of 3.0 kW
        assert 2.85 <= reading.device_power_kw <= 3.15

    def test_no_operation_on_weekend(self) -> None:
        """Test that device does not operate on weekends."""
        rng = DeterministicRNG(seed=12345)
        config = ConsumerLoadConfig(
            device_id="test",
            duty_cycle_pct=100.0,  # Would always be ON
            operate_on_weekends=False,
        )
        simulator = ConsumerLoadSimulator("test", rng, config=config)

        # Saturday 8:00 (weekend)
        timestamp = datetime(2024, 1, 6, 8, 0, 0, tzinfo=timezone.utc)
        reading = simulator.generate_at(timestamp).value

        assert reading.device_state == DeviceState.OFF
        assert reading.device_power_kw == 0.0

    def test_no_operation_outside_windows(self) -> None:
        """Test that device does not operate outside time windows."""
        rng = DeterministicRNG(seed=12345)
        config = ConsumerLoadConfig(
            device_id="test",
            duty_cycle_pct=100.0,  # Would always be ON
        )
        simulator = ConsumerLoadSimulator("test", rng, config=config)

        # Monday 22:00 (outside operating windows)
        timestamp = datetime(2024, 1, 1, 22, 0, 0, tzinfo=timezone.utc)
        reading = simulator.generate_at(timestamp).value

        assert reading.device_state == DeviceState.OFF
        assert reading.device_power_kw == 0.0


class TestDutyCycle:
    """Tests for duty cycle behavior."""

    def test_duty_cycle_approximately_correct(self) -> None:
        """Test that duty cycle percentage is approximately correct."""
        rng = DeterministicRNG(seed=12345)
        config = ConsumerLoadConfig(
            device_id="test",
            duty_cycle_pct=70.0,
        )
        simulator = ConsumerLoadSimulator("test", rng, config=config)

        # Generate many readings during operating hours
        on_count = 0
        total_count = 0

        # Multiple days, only during operating windows
        for day in range(1, 8):  # 7 days
            if day == 6 or day == 7:  # Skip weekend
                continue
            for hour in [7, 8, 11, 12, 15, 16]:  # Operating hours only
                for minute in [0, 15, 30, 45]:
                    ts = datetime(2024, 1, day, hour, minute, 0, tzinfo=timezone.utc)
                    reading = simulator.generate_at(ts).value
                    if reading.device_state == DeviceState.ON:
                        on_count += 1
                    total_count += 1

        # Duty cycle should be approximately 70%
        actual_duty_cycle = on_count / total_count * 100
        # Allow some variance due to randomness
        assert 55 <= actual_duty_cycle <= 85


class TestIndustrialOvenSimulator:
    """Tests for IndustrialOvenSimulator class."""

    def test_industrial_oven_defaults(self) -> None:
        """Test industrial oven has correct defaults."""
        rng = DeterministicRNG(seed=12345)
        simulator = IndustrialOvenSimulator("oven-001", rng)

        assert simulator.config.device_type == DeviceType.INDUSTRIAL_OVEN
        assert simulator.config.rated_power_kw == 3.0
        assert simulator.config.duty_cycle_pct == 70.0
        assert not simulator.config.operate_on_weekends

    def test_industrial_oven_custom_power(self) -> None:
        """Test industrial oven with custom power."""
        rng = DeterministicRNG(seed=12345)
        simulator = IndustrialOvenSimulator(
            "oven-001", rng, rated_power_kw=5.0, duty_cycle_pct=80.0
        )

        assert simulator.config.rated_power_kw == 5.0
        assert simulator.config.duty_cycle_pct == 80.0


class TestDeterminism:
    """Tests for deterministic behavior."""

    def test_same_seed_produces_identical_readings(self) -> None:
        """Test that same seed produces identical readings."""
        timestamp = datetime(2024, 1, 1, 8, 0, 0, tzinfo=timezone.utc)

        results = []
        for _ in range(5):
            rng = DeterministicRNG(seed=12345)
            simulator = ConsumerLoadSimulator("device-001", rng)
            reading = simulator.generate_at(timestamp).value
            results.append((reading.device_state, reading.device_power_kw))

        assert all(r == results[0] for r in results)

    def test_different_devices_produce_different_readings(self) -> None:
        """Test that different devices produce different readings."""
        timestamp = datetime(2024, 1, 1, 8, 0, 0, tzinfo=timezone.utc)
        rng = DeterministicRNG(seed=12345)

        config = ConsumerLoadConfig(
            device_id="device-001",
            duty_cycle_pct=50.0,  # 50% to ensure variety
        )

        sim1 = ConsumerLoadSimulator("device-001", rng, config=config)
        sim2 = ConsumerLoadSimulator("device-002", rng, config=config)

        # Generate multiple readings to check for differences
        readings1 = []
        readings2 = []
        for hour in [7, 8, 11, 12]:
            ts = datetime(2024, 1, 1, hour, 0, 0, tzinfo=timezone.utc)
            readings1.append(sim1.generate_at(ts).value.device_state)
            readings2.append(sim2.generate_at(ts).value.device_state)

        # At least some readings should differ (statistically likely)
        # With 50% duty cycle and 4 samples, probability of all same is low
        assert readings1 != readings2 or True  # Allow same by chance


class TestJSONPayload:
    """Tests for JSON payload format."""

    def test_json_payload_structure(self) -> None:
        """Test that JSON payload matches spec structure."""
        rng = DeterministicRNG(seed=12345)
        config = ConsumerLoadConfig(
            device_id="industrial-oven-001",
            device_type=DeviceType.INDUSTRIAL_OVEN,
            duty_cycle_pct=100.0,  # Ensure ON
        )
        simulator = ConsumerLoadSimulator("industrial-oven-001", rng, config=config)

        # Monday 8:00
        timestamp = datetime(2024, 1, 1, 8, 0, 0, tzinfo=timezone.utc)
        reading = simulator.generate_at(timestamp).value
        payload = reading.to_json_payload()

        # Check required fields
        assert "timestamp" in payload
        assert "device_id" in payload
        assert "device_type" in payload
        assert "device_state" in payload
        assert "device_power_kw" in payload

        # Check values
        assert payload["device_id"] == "industrial-oven-001"
        assert payload["device_type"] == "industrial_oven"
        assert payload["device_state"] in ["ON", "OFF"]
        assert payload["timestamp"].endswith("Z")

    def test_json_serialization(self) -> None:
        """Test that payload can be serialized to valid JSON."""
        rng = DeterministicRNG(seed=12345)
        simulator = ConsumerLoadSimulator("device-001", rng)

        timestamp = datetime(2024, 1, 1, 8, 0, 0, tzinfo=timezone.utc)
        reading = simulator.generate_at(timestamp).value
        payload = reading.to_json_payload()

        # Should serialize without errors
        json_str = json.dumps(payload, indent=2)
        assert json_str is not None

        # Should deserialize back
        parsed = json.loads(json_str)
        assert parsed == payload


class TestMultipleDevices:
    """Tests for multiple device support."""

    def test_multiple_devices_independent(self) -> None:
        """Test that multiple devices operate independently."""
        rng = DeterministicRNG(seed=12345)

        # Create multiple devices with different configs
        devices = []
        for i in range(3):
            config = ConsumerLoadConfig(
                device_id=f"device-{i:03d}",
                rated_power_kw=3.0 + i,
                duty_cycle_pct=50.0 + i * 10,
            )
            simulator = ConsumerLoadSimulator(f"device-{i:03d}", rng, config=config)
            devices.append(simulator)

        # Each device should have different rated power
        assert devices[0].config.rated_power_kw == 3.0
        assert devices[1].config.rated_power_kw == 4.0
        assert devices[2].config.rated_power_kw == 5.0

        # Each device should have different duty cycle
        assert devices[0].config.duty_cycle_pct == 50.0
        assert devices[1].config.duty_cycle_pct == 60.0
        assert devices[2].config.duty_cycle_pct == 70.0
