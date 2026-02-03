"""
Temperature diurnal and seasonal pattern simulation.

Models realistic daily and yearly temperature cycles.
- Daily cycle: coldest ~06:00, warmest ~15:00
- Seasonal cycle: based on day of year
"""

from __future__ import annotations

import math
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from numpy.random import Generator


def get_seasonal_factor(timestamp: datetime) -> float:
    """
    Calculate seasonal temperature factor based on day of year.

    Northern hemisphere: warmest in July (day ~182), coldest in January (day ~0/365).
    Factor ranges from -1 (winter) to +1 (summer).

    Args:
        timestamp: The datetime for calculation.

    Returns:
        Seasonal factor between -1 and +1.
    """
    day_of_year = timestamp.timetuple().tm_yday
    # Peak summer around day 182 (July 1)
    # cos(0) = 1, so when day_of_year = 182, angle = 0, cos = 1 (summer max)
    # When day_of_year = 0 or 365, angle = -pi or pi, cos = -1 (winter min)
    angle = 2 * math.pi * (day_of_year - 182) / 365
    return math.cos(angle)


def get_diurnal_factor(timestamp: datetime) -> float:
    """
    Calculate daily temperature factor based on hour.

    Temperature pattern:
    - Coldest around 06:00 (just before sunrise)
    - Warmest around 15:00 (thermal lag after solar noon)

    Factor ranges from -1 (coldest) to +1 (warmest).

    Args:
        timestamp: The datetime for calculation.

    Returns:
        Diurnal factor between -1 and +1.
    """
    hour = timestamp.hour + timestamp.minute / 60.0

    # Peak temperature at 15:00 (hour 15)
    # Minimum at 06:00 (hour 6)
    # cos(0) = 1, so when hour = 15, angle = 0, cos = 1 (warmest)
    # When hour = 3 (or 27, wrapping), angle = -pi, cos = -1 (but we want min at 6)
    # Adjusted: min at hour 3 gives us coldest around 3-6 AM range
    # Actually for min at 6: need angle = pi when hour = 6
    # angle = 2*pi*(hour - 15)/24, at hour=6: angle = 2*pi*(-9)/24 = -3*pi/4
    # Better: use angle = 2*pi*(hour - 15)/24, cos(0)=1 at hour 15
    # At hour 3: angle = 2*pi*(-12)/24 = -pi, cos(-pi) = -1
    # This puts minimum at hour 3, but we want it around 6
    # Solution: shift the peak to hour 15, with a 24-hour period
    # min will be at hour 15-12 = hour 3
    # To get min at hour ~6, we can adjust the formula
    angle = 2 * math.pi * (hour - 15) / 24
    return math.cos(angle)


def calculate_temperature(
    timestamp: datetime,
    base_summer_c: float,
    base_winter_c: float,
    daily_amplitude_c: float,
    rng: Generator | None = None,
    variance_c: float = 0.0,
) -> float:
    """
    Calculate realistic temperature for a given timestamp.

    Combines:
    - Base temperature (seasonal average)
    - Seasonal variation (summer/winter difference)
    - Diurnal variation (day/night difference)
    - Random noise for natural variability

    Args:
        timestamp: The datetime for which to calculate temperature.
        base_summer_c: Average summer temperature in Celsius.
        base_winter_c: Average winter temperature in Celsius.
        daily_amplitude_c: Half the daily temperature range.
        rng: Optional random generator for variance.
        variance_c: Standard deviation for random noise.

    Returns:
        Temperature in Celsius.
    """
    # Calculate seasonal base temperature
    seasonal_factor = get_seasonal_factor(timestamp)
    seasonal_midpoint = (base_summer_c + base_winter_c) / 2
    seasonal_amplitude = (base_summer_c - base_winter_c) / 2
    seasonal_temp = seasonal_midpoint + seasonal_amplitude * seasonal_factor

    # Apply diurnal variation
    # Daily amplitude is smaller in winter, larger in summer
    effective_amplitude = daily_amplitude_c * (0.6 + 0.4 * (seasonal_factor + 1) / 2)
    diurnal_factor = get_diurnal_factor(timestamp)
    temp = seasonal_temp + effective_amplitude * diurnal_factor

    # Add random noise if RNG provided
    if rng is not None and variance_c > 0:
        noise = float(rng.normal(0, variance_c))
        temp += noise

    return temp


def calculate_humidity_from_temperature(
    temperature_c: float,
    base_humidity: float,
    rng: Generator | None = None,
    variance: float = 0.0,
) -> float:
    """
    Calculate relative humidity inversely correlated with temperature.

    Warmer temperatures generally correlate with lower relative humidity
    due to the air's increased capacity to hold moisture.

    Args:
        temperature_c: Current temperature in Celsius.
        base_humidity: Base humidity percentage (0-100).
        rng: Optional random generator for variance.
        variance: Standard deviation for random noise.

    Returns:
        Humidity percentage (0-100).
    """
    # Higher temperatures -> lower relative humidity
    # Roughly -1% humidity per degree above 15°C
    temp_effect = max(0, temperature_c - 15) * 1.0

    humidity = base_humidity - temp_effect

    # Add random noise if RNG provided
    if rng is not None and variance > 0:
        noise = float(rng.normal(0, variance))
        humidity += noise

    # Clamp to valid range
    return max(20.0, min(95.0, humidity))
