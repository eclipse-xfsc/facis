"""
PV generation simulator.

Models photovoltaic power output based on weather data correlation.

Output is calculated as:
    P = P_nom × (G / G_stc) × (1 + γ × (T_mod - T_ref)) × (1 - losses)

Where:
    P_nom: Nominal capacity (kWp)
    G: Current irradiance (W/m²)
    G_stc: Standard Test Conditions irradiance (1000 W/m²)
    γ: Temperature coefficient (%/°C, negative)
    T_mod: Module temperature (°C)
    T_ref: Reference temperature (25°C)
    losses: System losses (wiring, inverter, soiling, etc.)

Data structure follows spec section 11.6.
"""

from __future__ import annotations

from datetime import UTC, date, datetime, timedelta
from typing import TYPE_CHECKING

from src.core.random_generator import DeterministicRNG
from src.core.time_series import BaseTimeSeriesGenerator, IntervalMinutes
from src.models.pv import PVConfig, PVReading, PVReadings

if TYPE_CHECKING:
    from src.simulators.weather import WeatherSimulator


# Standard Test Conditions irradiance (W/m²)
STC_IRRADIANCE_W_M2 = 1000.0


class PVGenerationSimulator(BaseTimeSeriesGenerator[PVReading]):
    """
    Photovoltaic power generation simulator.

    Generates realistic PV output correlated with weather data:
    - Power proportional to solar irradiance (zero at night)
    - Temperature coefficient reduces output in heat (-0.4%/°C above 25°C)
    - System losses (~15%) applied to all output
    - Output capped at nominal capacity

    Requires a weather simulator for irradiance and temperature data.

    Attributes:
        entity_id: Unique PV system identifier.
        config: PV system configuration.
        weather_simulator: Weather simulator for irradiance data.
    """

    def __init__(
        self,
        entity_id: str,
        rng: DeterministicRNG,
        weather_simulator: WeatherSimulator,
        interval: IntervalMinutes = IntervalMinutes.FIFTEEN_MINUTES,
        config: PVConfig | None = None,
    ) -> None:
        """
        Initialize the PV generation simulator.

        Args:
            entity_id: Unique PV system identifier.
            rng: Deterministic random number generator.
            weather_simulator: Weather simulator for irradiance and temperature.
            interval: Time interval for readings.
            config: PV system configuration. Uses defaults if None.
        """
        super().__init__(entity_id, rng, interval)

        if config is None:
            config = PVConfig(system_id=entity_id)
        self._config = config
        self._weather_simulator = weather_simulator

        # Track daily energy accumulation
        self._last_energy_date: date | None = None
        self._daily_energy_kwh: float = 0.0

    @property
    def config(self) -> PVConfig:
        """Return the PV configuration."""
        return self._config

    @property
    def weather_simulator(self) -> WeatherSimulator:
        """Return the associated weather simulator."""
        return self._weather_simulator

    @property
    def nominal_capacity_kwp(self) -> float:
        """Return the nominal capacity in kWp."""
        return self._config.nominal_capacity_kwp

    def calculate_module_temperature(self, ambient_temp_c: float, irradiance_w_m2: float) -> float:
        """
        Calculate module temperature based on ambient temperature and irradiance.

        Uses simplified NOCT model:
            T_mod = T_amb + (NOCT - 20) × (G / 800)

        Args:
            ambient_temp_c: Ambient temperature in Celsius.
            irradiance_w_m2: Solar irradiance in W/m².

        Returns:
            Module temperature in Celsius.
        """
        if irradiance_w_m2 <= 0:
            return ambient_temp_c

        # NOCT model: module heats up above ambient based on irradiance
        noct_rise = (self._config.noct_c - 20.0) * (irradiance_w_m2 / 800.0)
        return ambient_temp_c + noct_rise

    def calculate_temperature_derating(self, module_temp_c: float) -> float:
        """
        Calculate temperature derating factor.

        Power decreases by ~0.4% per degree above reference temperature (25°C).

        Args:
            module_temp_c: Module temperature in Celsius.

        Returns:
            Temperature derating factor (1.0 = no derating, <1.0 = reduced output).
        """
        temp_diff = module_temp_c - self._config.reference_temperature_c
        # Temperature coefficient is negative (e.g., -0.4 means -0.4%/°C)
        derating = 1.0 + (self._config.temperature_coefficient_pct_per_c / 100.0) * temp_diff
        # Clamp to reasonable range (can't generate negative power, but can exceed at low temps)
        return max(0.0, min(1.2, derating))

    def calculate_power_output(self, irradiance_w_m2: float, module_temp_c: float) -> float:
        """
        Calculate PV power output.

        Args:
            irradiance_w_m2: Solar irradiance in W/m².
            module_temp_c: Module temperature in Celsius.

        Returns:
            Power output in kW.
        """
        # Zero output when no irradiance (night)
        if irradiance_w_m2 <= 0:
            return 0.0

        # Base output proportional to irradiance
        irradiance_factor = irradiance_w_m2 / STC_IRRADIANCE_W_M2

        # Temperature derating
        temp_factor = self.calculate_temperature_derating(module_temp_c)

        # System losses
        loss_factor = 1.0 - (self._config.system_losses_percent / 100.0)

        # Calculate power
        power_kw = self._config.nominal_capacity_kwp * irradiance_factor * temp_factor * loss_factor

        # Cap at nominal capacity (can't exceed rated power)
        return min(power_kw, self._config.nominal_capacity_kwp)

    def calculate_efficiency(self, power_output_kw: float, irradiance_w_m2: float) -> float:
        """
        Calculate current system efficiency.

        Efficiency = (Power output) / (Irradiance × Area equivalent)

        For simplicity, we express this as percentage of theoretical maximum.

        Args:
            power_output_kw: Current power output in kW.
            irradiance_w_m2: Current irradiance in W/m².

        Returns:
            Efficiency percentage.
        """
        if irradiance_w_m2 <= 0 or power_output_kw <= 0:
            return 0.0

        # Theoretical maximum at this irradiance (no losses, no temp derating)
        theoretical_max = self._config.nominal_capacity_kwp * (
            irradiance_w_m2 / STC_IRRADIANCE_W_M2
        )

        if theoretical_max <= 0:
            return 0.0

        # Efficiency as percentage of theoretical
        efficiency = (power_output_kw / theoretical_max) * 100.0
        return min(100.0, efficiency)

    def _update_daily_energy(
        self, timestamp: datetime, power_kw: float, interval_minutes: int
    ) -> float:
        """
        Update and return daily energy accumulation.

        Resets at midnight UTC.

        Args:
            timestamp: Current timestamp.
            power_kw: Current power output in kW.
            interval_minutes: Interval duration in minutes.

        Returns:
            Cumulative daily energy in kWh.
        """
        current_date = timestamp.date()

        # Reset at new day
        if self._last_energy_date is None or current_date != self._last_energy_date:
            self._daily_energy_kwh = 0.0
            self._last_energy_date = current_date

        # Add energy for this interval (kW × hours)
        energy_kwh = power_kw * (interval_minutes / 60.0)
        self._daily_energy_kwh += energy_kwh

        return self._daily_energy_kwh

    def generate_value(self, timestamp: datetime) -> PVReading:
        """
        Generate PV reading for the given timestamp.

        Gets weather data from the associated weather simulator and calculates
        PV output based on irradiance, temperature, and system parameters.

        Args:
            timestamp: The timestamp for the reading.

        Returns:
            Complete PVReading with power output and system metrics.
        """
        # Get weather data at this timestamp
        weather_reading = self._weather_simulator.generate_value(timestamp)

        # Extract relevant weather values
        irradiance_w_m2 = weather_reading.conditions.ghi_w_m2
        ambient_temp_c = weather_reading.conditions.temperature_c

        # Calculate module temperature
        module_temp_c = self.calculate_module_temperature(ambient_temp_c, irradiance_w_m2)

        # Calculate power output
        power_kw = self.calculate_power_output(irradiance_w_m2, module_temp_c)

        # Update daily energy
        daily_energy_kwh = self._update_daily_energy(timestamp, power_kw, self._interval.value)

        # Calculate efficiency
        efficiency = self.calculate_efficiency(power_kw, irradiance_w_m2)

        # Build reading
        readings = PVReadings(
            power_output_kw=power_kw,
            daily_energy_kwh=daily_energy_kwh,
            irradiance_w_m2=irradiance_w_m2,
            module_temperature_c=module_temp_c,
            efficiency_percent=efficiency,
        )

        return PVReading(
            timestamp=timestamp,
            system_id=self._config.system_id,
            readings=readings,
        )

    def generate_daily_profile(self, date: datetime) -> list[PVReading]:
        """
        Generate a full day's PV profile.

        Useful for visualization and analysis.

        Args:
            date: The date for which to generate the profile.

        Returns:
            List of PVReadings for the entire day at configured intervals.
        """
        # Reset daily energy tracking for clean profile
        self._daily_energy_kwh = 0.0
        self._last_energy_date = date.date()

        # Start of day
        if date.tzinfo is None:
            start = datetime(date.year, date.month, date.day, tzinfo=UTC)
        else:
            start = datetime(date.year, date.month, date.day, tzinfo=date.tzinfo).replace(
                hour=0, minute=0, second=0, microsecond=0
            )

        readings = []
        interval_delta = timedelta(minutes=self._interval.value)
        current = start

        # Generate for 24 hours
        while current < start + timedelta(days=1):
            reading = self.generate_value(current)
            readings.append(reading)
            current += interval_delta

        return readings
