"""
Industrial load curve patterns for energy meter simulation.

Provides realistic daily load profiles for weekdays and weekends.
"""

from datetime import datetime
from enum import Enum

import numpy as np


class DayType(Enum):
    """Type of day for load pattern selection."""

    WEEKDAY = "weekday"
    WEEKEND = "weekend"


# Weekday load curve (24 hours, normalized 0-1)
# Higher during business hours (06:00-18:00), lower at night
WEEKDAY_LOAD_CURVE = np.array(
    [
        0.30,  # 00:00 - Night shift minimal
        0.28,  # 01:00
        0.25,  # 02:00
        0.25,  # 03:00
        0.27,  # 04:00
        0.35,  # 05:00 - Early morning ramp-up
        0.55,  # 06:00 - Shift start
        0.75,  # 07:00 - Production ramp-up
        0.90,  # 08:00 - Full production
        0.95,  # 09:00 - Peak morning
        1.00,  # 10:00 - Maximum load
        0.98,  # 11:00
        0.85,  # 12:00 - Lunch break dip
        0.92,  # 13:00 - Afternoon production
        0.98,  # 14:00 - Peak afternoon
        0.95,  # 15:00
        0.88,  # 16:00 - Late afternoon
        0.70,  # 17:00 - Shift end ramp-down
        0.50,  # 18:00 - Evening shift
        0.45,  # 19:00
        0.40,  # 20:00
        0.38,  # 21:00
        0.35,  # 22:00
        0.32,  # 23:00
    ]
)

# Weekend load curve (reduced to ~60% of weekday)
WEEKEND_LOAD_CURVE = np.array(
    [
        0.20,  # 00:00 - Minimal overnight
        0.18,  # 01:00
        0.16,  # 02:00
        0.15,  # 03:00
        0.15,  # 04:00
        0.18,  # 05:00
        0.25,  # 06:00 - Slight morning increase
        0.35,  # 07:00
        0.45,  # 08:00 - Maintenance/monitoring
        0.50,  # 09:00
        0.55,  # 10:00 - Peak weekend activity
        0.52,  # 11:00
        0.45,  # 12:00
        0.48,  # 13:00
        0.50,  # 14:00
        0.48,  # 15:00
        0.42,  # 16:00
        0.35,  # 17:00
        0.30,  # 18:00
        0.28,  # 19:00
        0.25,  # 20:00
        0.23,  # 21:00
        0.22,  # 22:00
        0.21,  # 23:00
    ]
)


def get_day_type(timestamp: datetime) -> DayType:
    """
    Determine if a timestamp falls on a weekday or weekend.

    Args:
        timestamp: The datetime to check.

    Returns:
        DayType indicating weekday or weekend.
    """
    # Monday = 0, Sunday = 6
    if timestamp.weekday() >= 5:
        return DayType.WEEKEND
    return DayType.WEEKDAY


def get_load_factor(timestamp: datetime) -> float:
    """
    Get the load factor for a given timestamp.

    The load factor is a value between 0 and 1 that represents
    the relative load compared to peak capacity.

    Args:
        timestamp: The datetime for which to get the load factor.

    Returns:
        Load factor between 0 and 1.
    """
    hour = timestamp.hour
    minute = timestamp.minute

    day_type = get_day_type(timestamp)
    curve = WEEKDAY_LOAD_CURVE if day_type == DayType.WEEKDAY else WEEKEND_LOAD_CURVE

    # Interpolate between hours for smoother transitions
    current_hour_factor = curve[hour]
    next_hour_factor = curve[(hour + 1) % 24]

    # Linear interpolation based on minutes
    interpolation = minute / 60.0
    load_factor = current_hour_factor + (next_hour_factor - current_hour_factor) * interpolation

    return float(load_factor)


def get_load_factor_with_noise(
    timestamp: datetime,
    rng: np.random.Generator,
    noise_factor: float = 0.05,
) -> float:
    """
    Get the load factor with realistic noise added.

    Args:
        timestamp: The datetime for which to get the load factor.
        rng: NumPy random generator for deterministic noise.
        noise_factor: Amount of noise to add (default 5%).

    Returns:
        Load factor with noise, clamped between 0.1 and 1.0.
    """
    base_factor = get_load_factor(timestamp)
    noise = float(rng.normal(0, noise_factor))
    noisy_factor = base_factor + noise

    # Clamp to reasonable range
    return max(0.1, min(1.0, noisy_factor))


def calculate_power_from_load_factor(
    load_factor: float,
    base_power_kw: float,
    peak_power_kw: float,
) -> float:
    """
    Calculate actual power from load factor.

    Args:
        load_factor: Load factor between 0 and 1.
        base_power_kw: Minimum base load in kW.
        peak_power_kw: Maximum peak load in kW.

    Returns:
        Actual power in kW.
    """
    return base_power_kw + (peak_power_kw - base_power_kw) * load_factor


def distribute_power_across_phases(
    total_power_w: float,
    rng: np.random.Generator,
    imbalance_factor: float = 0.08,
) -> tuple[float, float, float]:
    """
    Distribute total power across three phases with realistic imbalance.

    Args:
        total_power_w: Total power in watts.
        rng: NumPy random generator.
        imbalance_factor: Maximum phase imbalance (default 8%).

    Returns:
        Tuple of (L1, L2, L3) power values in watts.
    """
    # Base distribution is 1/3 each
    base_share = total_power_w / 3

    # Add random imbalance to each phase
    imbalance_l1 = float(rng.uniform(-imbalance_factor, imbalance_factor))
    imbalance_l2 = float(rng.uniform(-imbalance_factor, imbalance_factor))
    # L3 compensates to maintain total
    imbalance_l3 = -(imbalance_l1 + imbalance_l2)

    l1 = base_share * (1 + imbalance_l1)
    l2 = base_share * (1 + imbalance_l2)
    l3 = base_share * (1 + imbalance_l3)

    return (l1, l2, l3)
