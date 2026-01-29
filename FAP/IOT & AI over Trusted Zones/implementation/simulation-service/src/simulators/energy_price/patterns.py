"""
Price pattern models.

Daily peak/off-peak patterns and tariff period definitions.
"""

from datetime import datetime

import numpy as np

from src.models.price import TariffType

# Tariff period definitions (hour ranges)
TARIFF_PERIODS: dict[TariffType, tuple[int, int]] = {
    TariffType.NIGHT: (0, 6),  # 00:00 - 06:00
    TariffType.MORNING_PEAK: (6, 9),  # 06:00 - 09:00
    TariffType.MIDDAY: (9, 17),  # 09:00 - 17:00
    TariffType.EVENING_PEAK: (17, 20),  # 17:00 - 20:00
    TariffType.EVENING: (20, 24),  # 20:00 - 00:00
}


# Hourly price multipliers for smooth intra-period transitions
# This creates a more realistic curve within each tariff period
HOURLY_MULTIPLIERS = np.array(
    [
        0.90,  # 00:00 - Deep night, lowest
        0.85,  # 01:00
        0.82,  # 02:00 - Absolute minimum
        0.83,  # 03:00
        0.88,  # 04:00 - Early morning start
        0.95,  # 05:00 - Pre-dawn ramp
        1.05,  # 06:00 - Morning peak begins
        1.15,  # 07:00 - Morning ramp
        1.25,  # 08:00 - Peak morning
        1.10,  # 09:00 - Transition to midday
        1.05,  # 10:00
        1.00,  # 11:00 - Midday baseline
        0.98,  # 12:00 - Lunch dip (solar peak)
        0.95,  # 13:00 - Solar generation peak
        0.97,  # 14:00
        1.02,  # 15:00 - Afternoon rise
        1.08,  # 16:00
        1.20,  # 17:00 - Evening peak begins
        1.35,  # 18:00 - Peak demand
        1.40,  # 19:00 - Maximum evening peak
        1.15,  # 20:00 - Post-peak decline
        1.05,  # 21:00
        0.98,  # 22:00
        0.93,  # 23:00 - Late evening
    ]
)


def get_tariff_type(timestamp: datetime) -> TariffType:
    """
    Determine the tariff type for a given timestamp.

    Args:
        timestamp: The datetime to check.

    Returns:
        TariffType for the given hour.
    """
    hour = timestamp.hour

    for tariff_type, (start_hour, end_hour) in TARIFF_PERIODS.items():
        if start_hour <= hour < end_hour:
            return tariff_type

    # Default fallback (should not reach here)
    return TariffType.NIGHT


def is_weekend(timestamp: datetime) -> bool:
    """
    Check if a timestamp falls on a weekend.

    Args:
        timestamp: The datetime to check.

    Returns:
        True if Saturday or Sunday, False otherwise.
    """
    return timestamp.weekday() >= 5


def get_hourly_multiplier(timestamp: datetime) -> float:
    """
    Get the hourly price multiplier for smooth transitions.

    Args:
        timestamp: The datetime for the multiplier.

    Returns:
        Multiplier value (typically 0.8-1.4).
    """
    hour = timestamp.hour
    minute = timestamp.minute

    # Interpolate between hours for smoother transitions
    current_mult = HOURLY_MULTIPLIERS[hour]
    next_mult = HOURLY_MULTIPLIERS[(hour + 1) % 24]

    interpolation = minute / 60.0
    return float(current_mult + (next_mult - current_mult) * interpolation)


def calculate_base_price(
    timestamp: datetime,
    night_price: float,
    morning_peak_price: float,
    midday_price: float,
    evening_peak_price: float,
    evening_price: float,
) -> float:
    """
    Calculate the base price for a timestamp based on tariff period.

    Args:
        timestamp: The datetime for pricing.
        night_price: Base price for night tariff.
        morning_peak_price: Base price for morning peak.
        midday_price: Base price for midday.
        evening_peak_price: Base price for evening peak.
        evening_price: Base price for evening.

    Returns:
        Base price in EUR/kWh.
    """
    tariff = get_tariff_type(timestamp)

    tariff_prices = {
        TariffType.NIGHT: night_price,
        TariffType.MORNING_PEAK: morning_peak_price,
        TariffType.MIDDAY: midday_price,
        TariffType.EVENING_PEAK: evening_peak_price,
        TariffType.EVENING: evening_price,
    }

    return tariff_prices[tariff]


def apply_weekend_discount(price: float, discount_pct: float) -> float:
    """
    Apply weekend discount to a price.

    Args:
        price: Original price.
        discount_pct: Discount percentage (e.g., 7.5 for 7.5%).

    Returns:
        Discounted price.
    """
    return price * (1 - discount_pct / 100)


def apply_volatility(
    price: float,
    rng: np.random.Generator,
    volatility_pct: float,
) -> float:
    """
    Apply random volatility to a price.

    Args:
        price: Base price.
        rng: NumPy random generator for deterministic noise.
        volatility_pct: Volatility percentage (e.g., 10 for ±10%).

    Returns:
        Price with volatility applied.
    """
    # Use normal distribution for realistic price movements
    volatility_factor = volatility_pct / 100
    noise = float(rng.normal(0, volatility_factor))
    return price * (1 + noise)


def enforce_price_floor(price: float, min_price: float) -> float:
    """
    Ensure price doesn't go below the minimum floor.

    Args:
        price: Calculated price.
        min_price: Minimum allowed price.

    Returns:
        Price floored at minimum.
    """
    return max(price, min_price)
