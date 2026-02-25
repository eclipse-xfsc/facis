"""
Solar irradiance simulation.

Models Global Horizontal Irradiance (GHI), Direct Normal Irradiance (DNI),
and Diffuse Horizontal Irradiance (DHI) based on:
- Solar position (altitude and azimuth)
- Time of day (zero at night, bell curve during day)
- Day length (affected by latitude and season)
- Cloud cover factor (0.5-1.0 multiplier)
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from numpy.random import Generator


@dataclass
class SolarPosition:
    """Solar position in the sky."""

    altitude_deg: float  # Angle above horizon (0-90)
    azimuth_deg: float  # Compass direction (0=N, 90=E, 180=S, 270=W)
    is_daylight: bool  # True if sun is above horizon


@dataclass
class IrradianceReading:
    """Solar irradiance components."""

    ghi_w_m2: float  # Global Horizontal Irradiance
    dni_w_m2: float  # Direct Normal Irradiance
    dhi_w_m2: float  # Diffuse Horizontal Irradiance


def calculate_solar_position(
    timestamp: datetime,
    latitude: float,
    longitude: float,
) -> SolarPosition:
    """
    Calculate solar position (altitude and azimuth) for a location and time.

    Uses simplified astronomical calculations suitable for simulation.

    Args:
        timestamp: The datetime (must be timezone-aware or assumed UTC).
        latitude: Location latitude in degrees (-90 to 90).
        longitude: Location longitude in degrees (-180 to 180).

    Returns:
        SolarPosition with altitude, azimuth, and daylight flag.
    """
    # Ensure UTC
    if timestamp.tzinfo is None:
        timestamp = timestamp.replace(tzinfo=timezone.utc)

    # Day of year (1-365)
    day_of_year = timestamp.timetuple().tm_yday

    # Decimal hour in UTC
    hour_utc = timestamp.hour + timestamp.minute / 60.0 + timestamp.second / 3600.0

    # Solar declination (angle of sun relative to equator)
    # Varies from -23.45 (winter solstice) to +23.45 (summer solstice)
    declination_rad = math.radians(23.45 * math.sin(2 * math.pi * (284 + day_of_year) / 365))

    # Equation of time (correction for Earth's elliptical orbit)
    b = 2 * math.pi * (day_of_year - 81) / 365
    eot_minutes = 9.87 * math.sin(2 * b) - 7.53 * math.cos(b) - 1.5 * math.sin(b)

    # Solar time
    # Time offset due to longitude (4 minutes per degree from standard meridian)
    # Using 0° as reference (UTC)
    time_offset = 4 * longitude  # minutes
    solar_time = hour_utc * 60 + time_offset + eot_minutes  # in minutes

    # Hour angle (degrees from solar noon)
    # At solar noon, hour angle = 0
    # Each hour = 15 degrees (360/24)
    hour_angle_deg = (solar_time / 4.0) - 180  # Convert minutes to degrees, shift noon to 0
    hour_angle_rad = math.radians(hour_angle_deg)

    # Latitude in radians
    lat_rad = math.radians(latitude)

    # Solar altitude (elevation angle)
    sin_altitude = math.sin(lat_rad) * math.sin(declination_rad) + math.cos(lat_rad) * math.cos(
        declination_rad
    ) * math.cos(hour_angle_rad)
    altitude_rad = math.asin(max(-1, min(1, sin_altitude)))
    altitude_deg = math.degrees(altitude_rad)

    # Solar azimuth
    cos_azimuth = (math.sin(declination_rad) - math.sin(lat_rad) * math.sin(altitude_rad)) / (
        math.cos(lat_rad) * math.cos(altitude_rad) + 1e-10
    )
    cos_azimuth = max(-1, min(1, cos_azimuth))

    if hour_angle_deg < 0:
        azimuth_deg = math.degrees(math.acos(cos_azimuth))
    else:
        azimuth_deg = 360 - math.degrees(math.acos(cos_azimuth))

    return SolarPosition(
        altitude_deg=max(0, altitude_deg),  # Clamp to horizon
        azimuth_deg=azimuth_deg,
        is_daylight=altitude_deg > 0,
    )


def calculate_day_length_hours(day_of_year: int, latitude: float) -> float:
    """
    Calculate day length in hours for a given day and latitude.

    Args:
        day_of_year: Day of year (1-365).
        latitude: Latitude in degrees.

    Returns:
        Day length in hours.
    """
    # Solar declination
    declination_rad = math.radians(23.45 * math.sin(2 * math.pi * (284 + day_of_year) / 365))
    lat_rad = math.radians(latitude)

    # Hour angle at sunrise/sunset
    cos_hour_angle = -math.tan(lat_rad) * math.tan(declination_rad)

    # Handle polar day/night
    if cos_hour_angle < -1:
        return 24.0  # Polar day
    if cos_hour_angle > 1:
        return 0.0  # Polar night

    hour_angle_rad = math.acos(cos_hour_angle)
    day_length = 2 * math.degrees(hour_angle_rad) / 15  # Convert to hours

    return day_length


def calculate_clear_sky_ghi(
    solar_altitude_deg: float,
    max_ghi_w_m2: float = 1000.0,
) -> float:
    """
    Calculate clear-sky Global Horizontal Irradiance.

    GHI follows a bell curve based on solar altitude, peaking at solar noon.

    Args:
        solar_altitude_deg: Solar altitude angle in degrees.
        max_ghi_w_m2: Maximum GHI at zenith (clear sky).

    Returns:
        Clear-sky GHI in W/m².
    """
    if solar_altitude_deg <= 0:
        return 0.0

    # GHI is proportional to sin(altitude)
    # This naturally creates a bell curve during the day
    altitude_rad = math.radians(solar_altitude_deg)

    # Apply atmospheric attenuation using air mass approximation
    # Air mass = 1/sin(altitude) but capped to avoid infinity at horizon
    air_mass = 1.0 / max(math.sin(altitude_rad), 0.05)

    # Simple atmospheric transmission model
    # Transmission decreases with air mass
    transmission = 0.7 ** (air_mass**0.678)

    # Clear sky GHI
    ghi = max_ghi_w_m2 * math.sin(altitude_rad) * transmission

    return max(0, ghi)


def apply_cloud_factor(
    clear_sky_ghi: float,
    cloud_cover_percent: float,
    rng: Generator | None = None,
) -> float:
    """
    Apply cloud cover reduction to GHI.

    Cloud factor ranges from 1.0 (clear) to 0.5 (fully overcast).
    Adds some variability for realistic cloud movement.

    Args:
        clear_sky_ghi: Clear-sky GHI in W/m².
        cloud_cover_percent: Cloud cover percentage (0-100).
        rng: Optional random generator for variability.

    Returns:
        Cloud-adjusted GHI in W/m².
    """
    if clear_sky_ghi <= 0:
        return 0.0

    # Base cloud factor: 1.0 at 0% clouds, 0.5 at 100% clouds
    base_factor = 1.0 - 0.5 * (cloud_cover_percent / 100.0)

    # Add realistic variability (clouds are not uniform)
    if rng is not None:
        variability = float(rng.uniform(-0.05, 0.05))
        base_factor = max(0.3, min(1.0, base_factor + variability))

    return clear_sky_ghi * base_factor


def calculate_irradiance_components(
    ghi_w_m2: float,
    solar_altitude_deg: float,
    cloud_cover_percent: float,
) -> IrradianceReading:
    """
    Calculate DNI and DHI from GHI and conditions.

    Uses the DIRINT model approximation for splitting GHI into
    direct and diffuse components.

    Args:
        ghi_w_m2: Global Horizontal Irradiance in W/m².
        solar_altitude_deg: Solar altitude angle in degrees.
        cloud_cover_percent: Cloud cover percentage.

    Returns:
        IrradianceReading with GHI, DNI, and DHI.
    """
    if ghi_w_m2 <= 0 or solar_altitude_deg <= 0:
        return IrradianceReading(ghi_w_m2=0, dni_w_m2=0, dhi_w_m2=0)

    altitude_rad = math.radians(solar_altitude_deg)

    # Clearness index approximation based on cloud cover
    # kt = GHI / extraterrestrial irradiance
    # For simplicity, estimate based on cloud cover
    kt = 1.0 - 0.7 * (cloud_cover_percent / 100.0)

    # Diffuse fraction increases with cloud cover
    # Using simplified Erbs correlation
    if kt <= 0.22:
        diffuse_fraction = 1.0 - 0.09 * kt
    elif kt <= 0.80:
        diffuse_fraction = 0.9511 - 0.1604 * kt + 4.388 * kt**2 - 16.638 * kt**3 + 12.336 * kt**4
    else:
        diffuse_fraction = 0.165

    # Calculate components
    dhi = ghi_w_m2 * diffuse_fraction
    direct_horizontal = ghi_w_m2 - dhi

    # DNI = direct_horizontal / sin(altitude)
    dni = direct_horizontal / max(math.sin(altitude_rad), 0.05)

    return IrradianceReading(
        ghi_w_m2=max(0, ghi_w_m2),
        dni_w_m2=max(0, min(dni, 1200)),  # Cap DNI at reasonable maximum
        dhi_w_m2=max(0, dhi),
    )


def calculate_full_irradiance(
    timestamp: datetime,
    latitude: float,
    longitude: float,
    cloud_cover_percent: float,
    max_ghi_w_m2: float = 1000.0,
    rng: Generator | None = None,
) -> IrradianceReading:
    """
    Calculate complete irradiance values for a timestamp and location.

    Combines solar position, clear-sky model, and cloud effects.

    Args:
        timestamp: The datetime for calculation.
        latitude: Location latitude in degrees.
        longitude: Location longitude in degrees.
        cloud_cover_percent: Cloud cover percentage (0-100).
        max_ghi_w_m2: Maximum clear-sky GHI.
        rng: Optional random generator for cloud variability.

    Returns:
        Complete IrradianceReading with GHI, DNI, and DHI.
    """
    # Get solar position
    solar_pos = calculate_solar_position(timestamp, latitude, longitude)

    if not solar_pos.is_daylight:
        return IrradianceReading(ghi_w_m2=0, dni_w_m2=0, dhi_w_m2=0)

    # Calculate clear-sky GHI
    clear_sky_ghi = calculate_clear_sky_ghi(
        solar_pos.altitude_deg,
        max_ghi_w_m2,
    )

    # Apply cloud cover
    actual_ghi = apply_cloud_factor(clear_sky_ghi, cloud_cover_percent, rng)

    # Split into components
    return calculate_irradiance_components(
        actual_ghi,
        solar_pos.altitude_deg,
        cloud_cover_percent,
    )
