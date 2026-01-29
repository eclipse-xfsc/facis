"""
Consumer load simulator.

Simulates energy-intensive devices like industrial ovens with
schedule-based operation and duty cycle control.
"""

from __future__ import annotations

from datetime import datetime, timezone

from src.core.random_generator import DeterministicRNG
from src.core.time_series import BaseTimeSeriesGenerator, IntervalMinutes
from src.models.consumer_load import (
    ConsumerLoadConfig,
    ConsumerLoadReading,
    DeviceState,
    DeviceType,
)
from src.simulators.consumer_load.schedule import (
    calculate_device_power,
    calculate_device_state,
)


class ConsumerLoadSimulator(BaseTimeSeriesGenerator[ConsumerLoadReading]):
    """
    Consumer load device simulator.

    Simulates energy-intensive devices with:
    - Schedule-based operation (configurable time windows)
    - Duty cycle control during operating windows
    - No operation on weekends (configurable)
    - Power variance when device is ON

    Attributes:
        entity_id: Unique device identifier.
        config: Device configuration parameters.
    """

    def __init__(
        self,
        entity_id: str,
        rng: DeterministicRNG,
        interval: IntervalMinutes = IntervalMinutes.FIFTEEN_MINUTES,
        config: ConsumerLoadConfig | None = None,
    ) -> None:
        """
        Initialize the consumer load simulator.

        Args:
            entity_id: Unique device identifier.
            rng: Deterministic random number generator.
            interval: Time interval for readings.
            config: Device configuration. Uses defaults if None.
        """
        super().__init__(entity_id, rng, interval)

        if config is None:
            config = ConsumerLoadConfig(device_id=entity_id)
        self._config = config

    @property
    def config(self) -> ConsumerLoadConfig:
        """Return the device configuration."""
        return self._config

    def generate_value(self, timestamp: datetime) -> ConsumerLoadReading:
        """
        Generate a device reading for the given timestamp.

        Args:
            timestamp: The timestamp for the reading.

        Returns:
            Complete ConsumerLoadReading with state and power.
        """
        # Ensure timezone-aware timestamp
        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=timezone.utc)

        # Get deterministic RNG for this timestamp
        ts_ms = int(timestamp.timestamp() * 1000)
        ts_rng = self._rng.get_timestamp_rng(self._entity_id, ts_ms)

        # Calculate device state based on schedule and duty cycle
        state = calculate_device_state(timestamp, self._config, ts_rng)

        # Calculate power based on state
        power = calculate_device_power(state, self._config, ts_rng)

        return ConsumerLoadReading(
            timestamp=timestamp,
            device_id=self._entity_id,
            device_type=self._config.device_type,
            device_state=state,
            device_power_kw=power,
        )

    def is_operating(self, timestamp: datetime) -> bool:
        """
        Check if the device would be operating at a given time.

        Note: This only checks schedule, not duty cycle randomness.

        Args:
            timestamp: The datetime to check.

        Returns:
            True if device could operate (within schedule).
        """
        from src.simulators.consumer_load.schedule import should_device_operate

        return should_device_operate(timestamp, self._config)

    def get_rated_power(self) -> float:
        """Get the device's rated power in kW."""
        return self._config.rated_power_kw

    def get_duty_cycle(self) -> float:
        """Get the device's duty cycle percentage."""
        return self._config.duty_cycle_pct


class IndustrialOvenSimulator(ConsumerLoadSimulator):
    """
    Industrial oven simulator.

    Specialized consumer load simulator for industrial ovens with
    default settings matching typical oven operation patterns.
    """

    def __init__(
        self,
        entity_id: str,
        rng: DeterministicRNG,
        interval: IntervalMinutes = IntervalMinutes.FIFTEEN_MINUTES,
        rated_power_kw: float = 3.0,
        duty_cycle_pct: float = 70.0,
    ) -> None:
        """
        Initialize the industrial oven simulator.

        Args:
            entity_id: Unique oven identifier.
            rng: Deterministic random number generator.
            interval: Time interval for readings.
            rated_power_kw: Oven rated power (default 3 kW).
            duty_cycle_pct: Duty cycle during operation (default 70%).
        """
        config = ConsumerLoadConfig(
            device_id=entity_id,
            device_type=DeviceType.INDUSTRIAL_OVEN,
            rated_power_kw=rated_power_kw,
            duty_cycle_pct=duty_cycle_pct,
            power_variance_pct=5.0,
            operate_on_weekends=False,
        )
        super().__init__(entity_id, rng, interval, config)
