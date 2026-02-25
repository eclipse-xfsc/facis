"""
Wind speed and direction simulation.

Models realistic wind patterns with:
- Base wind speed with daily variation
- Prevailing wind direction with variance
- Gustiness and variability
"""

from __future__ import annotations

import math
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from numpy.random import Generator


def get_diurnal_wind_factor(timestamp: datetime) -> float:
    """
    Calculate daily wind variation factor.

    Wind is typically stronger during afternoon (thermal convection)
    and calmer at night and early morning.

    Args:
        timestamp: The datetime for calculation.

    Returns:
        Wind factor multiplier (0.6 to 1.4).
    """
    hour = timestamp.hour + timestamp.minute / 60.0

    # Wind peaks around 14:00-15:00, minimum around 06:00
    # Using cosine function shifted appropriately
    angle = 2 * math.pi * (hour - 14) / 24
    factor = 1.0 - 0.4 * math.cos(angle)

    return max(0.6, min(1.4, factor))


def calculate_wind_speed(
    timestamp: datetime,
    base_speed_ms: float,
    rng: Generator | None = None,
    variance_ms: float = 0.0,
) -> float:
    """
    Calculate wind speed with diurnal variation and gustiness.

    Args:
        timestamp: The datetime for calculation.
        base_speed_ms: Base wind speed in m/s.
        rng: Optional random generator for variance.
        variance_ms: Standard deviation for gustiness.

    Returns:
        Wind speed in m/s.
    """
    # Apply diurnal variation
    diurnal_factor = get_diurnal_wind_factor(timestamp)
    speed = base_speed_ms * diurnal_factor

    # Add random gustiness
    if rng is not None and variance_ms > 0:
        # Use log-normal for more realistic wind gusts (always positive, skewed)
        gust = float(rng.normal(0, variance_ms))
        speed += gust

    # Wind speed must be non-negative
    return max(0.0, speed)


def calculate_wind_direction(
    prevailing_direction_deg: float,
    rng: Generator | None = None,
    variance_deg: float = 0.0,
) -> float:
    """
    Calculate wind direction with variability around prevailing direction.

    Args:
        prevailing_direction_deg: Prevailing wind direction (0=N, 90=E).
        rng: Optional random generator for variance.
        variance_deg: Standard deviation for direction variation.

    Returns:
        Wind direction in degrees (0-360).
    """
    direction = prevailing_direction_deg

    # Add random variation
    if rng is not None and variance_deg > 0:
        deviation = float(rng.normal(0, variance_deg))
        direction += deviation

    # Normalize to 0-360 range
    direction = direction % 360
    if direction < 0:
        direction += 360

    return direction


def calculate_cloud_cover(
    timestamp: datetime,
    base_cover_percent: float,
    rng: Generator | None = None,
    variance_percent: float = 0.0,
) -> float:
    """
    Calculate cloud cover with some temporal persistence.

    Cloud cover tends to increase during afternoon due to convection,
    and can be more variable during transitional weather.

    Args:
        timestamp: The datetime for calculation.
        base_cover_percent: Base cloud cover percentage.
        rng: Optional random generator for variance.
        variance_percent: Standard deviation for cloud variability.

    Returns:
        Cloud cover percentage (0-100).
    """
    hour = timestamp.hour + timestamp.minute / 60.0

    # Clouds often build during afternoon, clearer at night
    # Peak cloud cover around 14:00-16:00
    angle = 2 * math.pi * (hour - 15) / 24
    diurnal_variation = -0.15 * math.cos(angle)  # ±15% variation

    cover = base_cover_percent * (1 + diurnal_variation)

    # Add random variability
    if rng is not None and variance_percent > 0:
        noise = float(rng.normal(0, variance_percent))
        cover += noise

    # Clamp to valid range
    return max(0.0, min(100.0, cover))
