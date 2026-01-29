"""
Janitza-compatible energy meter simulator.

Generates realistic power, voltage, current, and energy readings
with industrial consumption patterns.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import TYPE_CHECKING

from src.core.random_generator import DeterministicRNG
from src.core.time_series import BaseTimeSeriesGenerator, IntervalMinutes, TimeRange
from src.models.meter import MeterConfig, MeterReading, MeterReadings
from src.simulators.energy_meter.load_curves import (
    distribute_power_across_phases,
    get_load_factor_with_noise,
)

if TYPE_CHECKING:
    from collections.abc import Iterator


@dataclass
class EnergyState:
    """Tracks cumulative energy state for a meter."""

    total_energy_kwh: float = 0.0
    last_timestamp: datetime | None = None


class EnergyMeterSimulator(BaseTimeSeriesGenerator[MeterReading]):
    """
    Industrial energy meter simulator.

    Generates realistic meter readings including:
    - Active power with daily load curves (weekday/weekend patterns)
    - Three-phase voltage with realistic variance
    - Current derived from power using P = V * I * sqrt(3) * PF
    - Power factor in industrial range (0.95-0.99)
    - Frequency with small variations around 50Hz
    - Cumulative energy that always increases

    Attributes:
        entity_id: Unique meter identifier.
        config: Meter configuration parameters.
    """

    def __init__(
        self,
        entity_id: str,
        rng: DeterministicRNG,
        interval: IntervalMinutes = IntervalMinutes.FIFTEEN_MINUTES,
        config: MeterConfig | None = None,
    ) -> None:
        """
        Initialize the energy meter simulator.

        Args:
            entity_id: Unique meter identifier.
            rng: Deterministic random number generator.
            interval: Time interval for readings.
            config: Meter configuration. Uses defaults if None.
        """
        super().__init__(entity_id, rng, interval)

        if config is None:
            config = MeterConfig(meter_id=entity_id)
        self._config = config

        # Energy state tracking per entity
        self._energy_states: dict[str, EnergyState] = {}

    @property
    def config(self) -> MeterConfig:
        """Return the meter configuration."""
        return self._config

    def _get_energy_state(self, timestamp: datetime) -> EnergyState:
        """
        Get or initialize energy state for tracking cumulative energy.

        Energy must be calculated sequentially to ensure it's always increasing.
        """
        state_key = f"{self._entity_id}"
        if state_key not in self._energy_states:
            self._energy_states[state_key] = EnergyState(
                total_energy_kwh=self._config.initial_energy_kwh,
                last_timestamp=None,
            )
        return self._energy_states[state_key]

    def _calculate_energy_increment(
        self,
        power_kw: float,
        interval_hours: float,
    ) -> float:
        """
        Calculate energy increment for a time interval.

        Energy (kWh) = Power (kW) * Time (hours)

        Args:
            power_kw: Average power during interval in kW.
            interval_hours: Duration of interval in hours.

        Returns:
            Energy increment in kWh.
        """
        return power_kw * interval_hours

    def generate_value(self, timestamp: datetime) -> MeterReading:
        """
        Generate a meter reading for the given timestamp.

        Args:
            timestamp: The timestamp for the reading.

        Returns:
            Complete MeterReading with all values.
        """
        # Get deterministic RNG for this timestamp
        ts_ms = int(timestamp.timestamp() * 1000)
        ts_rng = self._rng.get_timestamp_rng(self._entity_id, ts_ms)

        # Calculate load factor with deterministic noise
        load_factor = get_load_factor_with_noise(timestamp, ts_rng, noise_factor=0.05)

        # Calculate total power from load factor
        total_power_kw = (
            self._config.base_power_kw
            + (self._config.peak_power_kw - self._config.base_power_kw) * load_factor
        )
        total_power_w = total_power_kw * 1000

        # Distribute power across phases with realistic imbalance
        power_l1, power_l2, power_l3 = distribute_power_across_phases(
            total_power_w, ts_rng, imbalance_factor=0.08
        )

        # Generate voltage for each phase (230V ±5%)
        voltage_variance = self._config.nominal_voltage_v * (
            self._config.voltage_variance_pct / 100
        )
        voltage_l1 = self._config.nominal_voltage_v + float(
            ts_rng.uniform(-voltage_variance, voltage_variance)
        )
        voltage_l2 = self._config.nominal_voltage_v + float(
            ts_rng.uniform(-voltage_variance, voltage_variance)
        )
        voltage_l3 = self._config.nominal_voltage_v + float(
            ts_rng.uniform(-voltage_variance, voltage_variance)
        )

        # Generate power factor (0.95-0.99)
        power_factor = float(
            ts_rng.uniform(self._config.power_factor_min, self._config.power_factor_max)
        )

        # Calculate current from power: I = P / (V * PF)
        # For single phase calculation (simplified)
        current_l1 = power_l1 / (voltage_l1 * power_factor) if voltage_l1 > 0 else 0
        current_l2 = power_l2 / (voltage_l2 * power_factor) if voltage_l2 > 0 else 0
        current_l3 = power_l3 / (voltage_l3 * power_factor) if voltage_l3 > 0 else 0

        # Generate frequency (50Hz ±0.05Hz)
        frequency = self._config.nominal_frequency_hz + float(
            ts_rng.uniform(
                -self._config.frequency_variance_hz,
                self._config.frequency_variance_hz,
            )
        )

        # Calculate cumulative energy
        # For deterministic calculation, we compute energy based on timestamp position
        total_energy = self._calculate_cumulative_energy(timestamp, total_power_kw)

        readings = MeterReadings(
            active_power_l1_w=power_l1,
            active_power_l2_w=power_l2,
            active_power_l3_w=power_l3,
            voltage_l1_v=voltage_l1,
            voltage_l2_v=voltage_l2,
            voltage_l3_v=voltage_l3,
            current_l1_a=current_l1,
            current_l2_a=current_l2,
            current_l3_a=current_l3,
            power_factor=power_factor,
            frequency_hz=frequency,
            total_energy_kwh=total_energy,
        )

        return MeterReading(
            timestamp=timestamp,
            meter_id=self._entity_id,
            readings=readings,
        )

    def _calculate_cumulative_energy(
        self,
        timestamp: datetime,
        current_power_kw: float,
    ) -> float:
        """
        Calculate cumulative energy at a given timestamp.

        For deterministic generation, we calculate energy by integrating
        the power curve from a reference start time.

        Args:
            timestamp: Current timestamp.
            current_power_kw: Current power reading in kW.

        Returns:
            Cumulative energy in kWh.
        """
        # Use a fixed reference point for deterministic calculation
        # Reference: Start of the year containing this timestamp
        reference_start = datetime(timestamp.year, 1, 1, 0, 0, 0, tzinfo=UTC)

        if timestamp <= reference_start:
            return self._config.initial_energy_kwh

        # Calculate total hours from reference
        delta = timestamp - reference_start
        total_hours = delta.total_seconds() / 3600

        # Estimate average power based on load curve characteristics
        # Weekday average ~0.6, weekend average ~0.35
        # Assuming 5 weekdays + 2 weekend days per week
        # Weighted average: (5 * 0.6 + 2 * 0.35) / 7 ≈ 0.53
        avg_load_factor = 0.53

        avg_power_kw = (
            self._config.base_power_kw
            + (self._config.peak_power_kw - self._config.base_power_kw) * avg_load_factor
        )

        # Calculate energy: E = P_avg * t
        energy_from_reference = avg_power_kw * total_hours

        return self._config.initial_energy_kwh + energy_from_reference

    def generate_range_with_energy_tracking(
        self,
        time_range: TimeRange,
    ) -> list[MeterReading]:
        """
        Generate readings over a range with accurate cumulative energy tracking.

        This method generates readings sequentially to ensure energy values
        are always increasing and accurately reflect the power consumption.

        Args:
            time_range: The time range to generate readings for.

        Returns:
            List of MeterReading objects with accurate cumulative energy.
        """
        readings = []
        cumulative_energy = self._config.initial_energy_kwh
        interval_hours = self._interval.value / 60.0

        for point in self.iterate_range(time_range):
            reading = point.value

            # Calculate actual energy increment from this reading's power
            total_power_kw = (
                reading.readings.active_power_l1_w
                + reading.readings.active_power_l2_w
                + reading.readings.active_power_l3_w
            ) / 1000

            energy_increment = self._calculate_energy_increment(total_power_kw, interval_hours)
            cumulative_energy += energy_increment

            # Update the reading with accurate cumulative energy
            updated_readings = MeterReadings(
                active_power_l1_w=reading.readings.active_power_l1_w,
                active_power_l2_w=reading.readings.active_power_l2_w,
                active_power_l3_w=reading.readings.active_power_l3_w,
                voltage_l1_v=reading.readings.voltage_l1_v,
                voltage_l2_v=reading.readings.voltage_l2_v,
                voltage_l3_v=reading.readings.voltage_l3_v,
                current_l1_a=reading.readings.current_l1_a,
                current_l2_a=reading.readings.current_l2_a,
                current_l3_a=reading.readings.current_l3_a,
                power_factor=reading.readings.power_factor,
                frequency_hz=reading.readings.frequency_hz,
                total_energy_kwh=cumulative_energy,
            )

            readings.append(
                MeterReading(
                    timestamp=reading.timestamp,
                    meter_id=reading.meter_id,
                    readings=updated_readings,
                )
            )

        return readings

    def iterate_range_with_energy_tracking(
        self,
        time_range: TimeRange,
    ) -> Iterator[MeterReading]:
        """
        Iterate over readings with accurate cumulative energy tracking.

        Memory-efficient version of generate_range_with_energy_tracking.

        Args:
            time_range: The time range to generate readings for.

        Yields:
            MeterReading objects with accurate cumulative energy.
        """
        cumulative_energy = self._config.initial_energy_kwh
        interval_hours = self._interval.value / 60.0

        for point in self.iterate_range(time_range):
            reading = point.value

            total_power_kw = (
                reading.readings.active_power_l1_w
                + reading.readings.active_power_l2_w
                + reading.readings.active_power_l3_w
            ) / 1000

            energy_increment = self._calculate_energy_increment(total_power_kw, interval_hours)
            cumulative_energy += energy_increment

            updated_readings = MeterReadings(
                active_power_l1_w=reading.readings.active_power_l1_w,
                active_power_l2_w=reading.readings.active_power_l2_w,
                active_power_l3_w=reading.readings.active_power_l3_w,
                voltage_l1_v=reading.readings.voltage_l1_v,
                voltage_l2_v=reading.readings.voltage_l2_v,
                voltage_l3_v=reading.readings.voltage_l3_v,
                current_l1_a=reading.readings.current_l1_a,
                current_l2_a=reading.readings.current_l2_a,
                current_l3_a=reading.readings.current_l3_a,
                power_factor=reading.readings.power_factor,
                frequency_hz=reading.readings.frequency_hz,
                total_energy_kwh=cumulative_energy,
            )

            yield MeterReading(
                timestamp=reading.timestamp,
                meter_id=reading.meter_id,
                readings=updated_readings,
            )
