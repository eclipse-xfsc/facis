"""
Device schedule and duty cycle logic.

Determines when devices should operate based on time windows and duty cycles.
"""

from datetime import datetime

import numpy as np

from src.models.consumer_load import ConsumerLoadConfig, DeviceState, OperatingWindow


def is_weekend(timestamp: datetime) -> bool:
    """
    Check if a timestamp falls on a weekend.

    Args:
        timestamp: The datetime to check.

    Returns:
        True if Saturday or Sunday, False otherwise.
    """
    return timestamp.weekday() >= 5


def is_within_operating_window(
    timestamp: datetime,
    operating_windows: list[OperatingWindow],
) -> bool:
    """
    Check if a timestamp falls within any operating window.

    Args:
        timestamp: The datetime to check.
        operating_windows: List of operating time windows.

    Returns:
        True if within any window, False otherwise.
    """
    hour = timestamp.hour

    for window in operating_windows:
        if window.contains_hour(hour):
            return True

    return False


def should_device_operate(
    timestamp: datetime,
    config: ConsumerLoadConfig,
) -> bool:
    """
    Determine if a device should be allowed to operate at a given time.

    This checks schedule constraints but not duty cycle.

    Args:
        timestamp: The datetime to check.
        config: Device configuration.

    Returns:
        True if device can operate (schedule permits), False otherwise.
    """
    # Check weekend restriction
    if is_weekend(timestamp) and not config.operate_on_weekends:
        return False

    # Check if within operating windows
    return is_within_operating_window(timestamp, config.operating_windows)


def calculate_device_state(
    timestamp: datetime,
    config: ConsumerLoadConfig,
    rng: np.random.Generator,
) -> DeviceState:
    """
    Calculate the device state (ON/OFF) for a given timestamp.

    Uses deterministic random selection based on duty cycle.

    Args:
        timestamp: The datetime for the state.
        config: Device configuration.
        rng: NumPy random generator for deterministic selection.

    Returns:
        DeviceState.ON or DeviceState.OFF.
    """
    # First check if device is allowed to operate
    if not should_device_operate(timestamp, config):
        return DeviceState.OFF

    # Device can operate - apply duty cycle
    # Generate a random value [0, 1) and compare to duty cycle
    duty_cycle = config.duty_cycle_pct / 100.0
    random_value = float(rng.random())

    if random_value < duty_cycle:
        return DeviceState.ON
    return DeviceState.OFF


def calculate_device_power(
    state: DeviceState,
    config: ConsumerLoadConfig,
    rng: np.random.Generator,
) -> float:
    """
    Calculate device power consumption based on state.

    Args:
        state: Current device state.
        config: Device configuration.
        rng: NumPy random generator for power variance.

    Returns:
        Power consumption in kW.
    """
    if state == DeviceState.OFF:
        return 0.0

    # Device is ON - apply rated power with variance
    variance = config.rated_power_kw * (config.power_variance_pct / 100.0)
    noise = float(rng.uniform(-variance, variance))
    power = config.rated_power_kw + noise

    # Ensure power is non-negative
    return max(0.0, power)


def get_operating_hours_per_day(config: ConsumerLoadConfig) -> float:
    """
    Calculate total operating hours per day from windows.

    Args:
        config: Device configuration.

    Returns:
        Total hours per day the device can operate.
    """
    total_hours = 0.0
    for window in config.operating_windows:
        if window.start_hour <= window.end_hour:
            total_hours += window.end_hour - window.start_hour
        else:
            # Overnight window
            total_hours += (24 - window.start_hour) + window.end_hour
    return total_hours


def estimate_daily_energy_consumption(config: ConsumerLoadConfig) -> float:
    """
    Estimate daily energy consumption based on schedule and duty cycle.

    Args:
        config: Device configuration.

    Returns:
        Estimated daily energy in kWh.
    """
    operating_hours = get_operating_hours_per_day(config)
    effective_hours = operating_hours * (config.duty_cycle_pct / 100.0)
    return config.rated_power_kw * effective_hours
