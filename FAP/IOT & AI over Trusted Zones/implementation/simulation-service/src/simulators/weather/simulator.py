"""
Weather data simulator.

Generates correlated environmental data for PV generation calculation including:
- Temperature with daily and seasonal cycles
- Solar irradiance (GHI, DNI, DHI) with day/night patterns
- Wind speed and direction
- Cloud cover affecting irradiance
- Humidity correlated with temperature

Data structure follows spec section 11.5.
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from src.core.random_generator import DeterministicRNG
from src.core.time_series import BaseTimeSeriesGenerator, IntervalMinutes
from src.models.weather import (
    LocationData,
    WeatherConditions,
    WeatherConfig,
    WeatherReading,
)
from src.simulators.weather.irradiance import calculate_full_irradiance
from src.simulators.weather.temperature import (
    calculate_humidity_from_temperature,
    calculate_temperature,
)
from src.simulators.weather.wind import (
    calculate_cloud_cover,
    calculate_wind_direction,
    calculate_wind_speed,
)

if TYPE_CHECKING:
    pass


class WeatherSimulator(BaseTimeSeriesGenerator[WeatherReading]):
    """
    Environmental data feed simulator for PV generation correlation.

    Generates realistic weather data with:
    - Temperature: Daily cycle (coldest ~06:00, warmest ~15:00), seasonal variation
    - Solar irradiance: Zero at night, bell curve during day, peak ~1000 W/m² at noon
    - Cloud factor (0.5-1.0): Adds variability to irradiance
    - Configurable latitude: Affects day length and solar position

    The weather data feeds directly into PV generation calculations.

    Attributes:
        entity_id: Unique weather station identifier.
        config: Weather simulation configuration.
    """

    def __init__(
        self,
        entity_id: str,
        rng: DeterministicRNG,
        interval: IntervalMinutes = IntervalMinutes.FIFTEEN_MINUTES,
        config: WeatherConfig | None = None,
    ) -> None:
        """
        Initialize the weather simulator.

        Args:
            entity_id: Unique weather station identifier.
            rng: Deterministic random number generator.
            interval: Time interval for readings.
            config: Weather configuration. Uses defaults (Berlin) if None.
        """
        super().__init__(entity_id, rng, interval)

        if config is None:
            config = WeatherConfig()
        self._config = config

    @property
    def config(self) -> WeatherConfig:
        """Return the weather configuration."""
        return self._config

    @property
    def latitude(self) -> float:
        """Return the configured latitude."""
        return self._config.latitude

    @property
    def longitude(self) -> float:
        """Return the configured longitude."""
        return self._config.longitude

    def generate_value(self, timestamp: datetime) -> WeatherReading:
        """
        Generate weather reading for the given timestamp.

        Produces correlated weather data where:
        - Cloud cover affects solar irradiance
        - Temperature affects humidity
        - All values follow realistic daily/seasonal patterns

        Args:
            timestamp: The timestamp for the reading.

        Returns:
            Complete WeatherReading with all environmental data.
        """
        # Get deterministic RNG for this timestamp
        ts_ms = int(timestamp.timestamp() * 1000)
        ts_rng = self._rng.get_timestamp_rng(self._entity_id, ts_ms)

        # Calculate cloud cover first (affects irradiance)
        cloud_cover = calculate_cloud_cover(
            timestamp,
            self._config.base_cloud_cover_percent,
            ts_rng,
            self._config.cloud_variance_percent,
        )

        # Calculate temperature with daily and seasonal cycles
        temperature = calculate_temperature(
            timestamp,
            self._config.base_temperature_summer_c,
            self._config.base_temperature_winter_c,
            self._config.daily_temp_amplitude_c,
            ts_rng,
            self._config.temperature_variance_c,
        )

        # Calculate humidity (inversely correlated with temperature)
        humidity = calculate_humidity_from_temperature(
            temperature,
            self._config.base_humidity_percent,
            ts_rng,
            self._config.humidity_variance_percent,
        )

        # Calculate wind
        wind_speed = calculate_wind_speed(
            timestamp,
            self._config.base_wind_speed_ms,
            ts_rng,
            self._config.wind_variance_ms,
        )

        wind_direction = calculate_wind_direction(
            self._config.prevailing_wind_direction_deg,
            ts_rng,
            self._config.wind_direction_variance_deg,
        )

        # Calculate solar irradiance (affected by cloud cover)
        # Need fresh RNG for irradiance to avoid correlation
        irr_rng = self._rng.get_timestamp_rng(f"{self._entity_id}_irr", ts_ms)
        irradiance = calculate_full_irradiance(
            timestamp,
            self._config.latitude,
            self._config.longitude,
            cloud_cover,
            self._config.max_clear_sky_ghi_w_m2,
            irr_rng,
        )

        # Build the weather reading
        location = LocationData(
            latitude=self._config.latitude,
            longitude=self._config.longitude,
        )

        conditions = WeatherConditions(
            temperature_c=temperature,
            humidity_percent=humidity,
            wind_speed_ms=wind_speed,
            wind_direction_deg=wind_direction,
            cloud_cover_percent=cloud_cover,
            ghi_w_m2=irradiance.ghi_w_m2,
            dni_w_m2=irradiance.dni_w_m2,
            dhi_w_m2=irradiance.dhi_w_m2,
        )

        return WeatherReading(
            timestamp=timestamp,
            location=location,
            conditions=conditions,
        )

    def get_irradiance_for_pv(self, timestamp: datetime) -> float:
        """
        Get Global Horizontal Irradiance for PV generation calculation.

        Convenience method for PV simulator integration.

        Args:
            timestamp: The timestamp for the reading.

        Returns:
            GHI in W/m² for PV power calculation.
        """
        reading = self.generate_value(timestamp)
        return reading.conditions.ghi_w_m2

    def get_temperature_for_pv(self, timestamp: datetime) -> float:
        """
        Get temperature for PV efficiency calculation.

        PV efficiency decreases at higher temperatures.

        Args:
            timestamp: The timestamp for the reading.

        Returns:
            Temperature in Celsius.
        """
        reading = self.generate_value(timestamp)
        return reading.conditions.temperature_c
