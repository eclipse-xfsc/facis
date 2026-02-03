"""Weather Data Simulator.

Environmental data feed for PV generation correlation.
"""

from src.simulators.weather.irradiance import (
    IrradianceReading,
    SolarPosition,
    calculate_clear_sky_ghi,
    calculate_day_length_hours,
    calculate_full_irradiance,
    calculate_solar_position,
)
from src.simulators.weather.simulator import WeatherSimulator
from src.simulators.weather.temperature import (
    calculate_humidity_from_temperature,
    calculate_temperature,
    get_diurnal_factor,
    get_seasonal_factor,
)
from src.simulators.weather.wind import (
    calculate_cloud_cover,
    calculate_wind_direction,
    calculate_wind_speed,
)

__all__ = [
    # Main simulator
    "WeatherSimulator",
    # Temperature functions
    "calculate_temperature",
    "calculate_humidity_from_temperature",
    "get_seasonal_factor",
    "get_diurnal_factor",
    # Irradiance functions and types
    "calculate_solar_position",
    "calculate_day_length_hours",
    "calculate_clear_sky_ghi",
    "calculate_full_irradiance",
    "SolarPosition",
    "IrradianceReading",
    # Wind functions
    "calculate_wind_speed",
    "calculate_wind_direction",
    "calculate_cloud_cover",
]
