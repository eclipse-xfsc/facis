"""
Weather data model.

Pydantic schema for weather conditions including solar irradiance.
"""

from datetime import datetime

from pydantic import BaseModel, Field


class LocationData(BaseModel):
    """Geographic location data."""

    latitude: float = Field(..., ge=-90, le=90, description="Latitude in degrees")
    longitude: float = Field(..., ge=-180, le=180, description="Longitude in degrees")


class WeatherConditions(BaseModel):
    """Weather measurement values."""

    temperature_c: float = Field(..., description="Temperature in Celsius")
    humidity_percent: float = Field(..., ge=0, le=100, description="Relative humidity percentage")
    wind_speed_ms: float = Field(..., ge=0, description="Wind speed in m/s")
    wind_direction_deg: float = Field(
        ..., ge=0, lt=360, description="Wind direction in degrees (0=N, 90=E)"
    )
    cloud_cover_percent: float = Field(..., ge=0, le=100, description="Cloud cover percentage")
    ghi_w_m2: float = Field(..., ge=0, description="Global Horizontal Irradiance in W/m²")
    dni_w_m2: float = Field(..., ge=0, description="Direct Normal Irradiance in W/m²")
    dhi_w_m2: float = Field(..., ge=0, description="Diffuse Horizontal Irradiance in W/m²")


class WeatherReading(BaseModel):
    """Complete weather reading payload matching spec section 11.5."""

    timestamp: datetime = Field(..., description="Reading timestamp in ISO 8601 format")
    location: LocationData = Field(..., description="Geographic location")
    conditions: WeatherConditions = Field(..., description="Weather conditions")

    def to_json_payload(self) -> dict:
        """Convert to JSON payload matching spec structure."""
        return {
            "timestamp": self.timestamp.isoformat().replace("+00:00", "Z"),
            "location": {
                "latitude": round(self.location.latitude, 4),
                "longitude": round(self.location.longitude, 4),
            },
            "conditions": {
                "temperature_c": round(self.conditions.temperature_c, 1),
                "humidity_percent": round(self.conditions.humidity_percent, 1),
                "wind_speed_ms": round(self.conditions.wind_speed_ms, 1),
                "wind_direction_deg": round(self.conditions.wind_direction_deg, 0),
                "cloud_cover_percent": round(self.conditions.cloud_cover_percent, 1),
                "ghi_w_m2": round(self.conditions.ghi_w_m2, 1),
                "dni_w_m2": round(self.conditions.dni_w_m2, 1),
                "dhi_w_m2": round(self.conditions.dhi_w_m2, 1),
            },
        }


class WeatherConfig(BaseModel):
    """Configuration for weather simulation."""

    # Location defaults to Berlin
    latitude: float = Field(default=52.52, ge=-90, le=90, description="Latitude")
    longitude: float = Field(default=13.405, ge=-180, le=180, description="Longitude")

    # Temperature parameters (Celsius)
    base_temperature_summer_c: float = Field(default=20.0, description="Base summer temperature")
    base_temperature_winter_c: float = Field(default=2.0, description="Base winter temperature")
    daily_temp_amplitude_c: float = Field(default=8.0, description="Daily temperature amplitude")
    temperature_variance_c: float = Field(default=2.0, description="Random temperature variance")

    # Solar parameters
    max_clear_sky_ghi_w_m2: float = Field(default=1000.0, ge=0, description="Maximum clear sky GHI")

    # Cloud parameters
    base_cloud_cover_percent: float = Field(
        default=40.0, ge=0, le=100, description="Average cloud cover"
    )
    cloud_variance_percent: float = Field(default=20.0, ge=0, description="Cloud cover variance")

    # Wind parameters
    base_wind_speed_ms: float = Field(default=4.0, ge=0, description="Average wind speed")
    wind_variance_ms: float = Field(default=3.0, ge=0, description="Wind speed variance")
    prevailing_wind_direction_deg: float = Field(
        default=270.0, ge=0, lt=360, description="Prevailing wind direction"
    )
    wind_direction_variance_deg: float = Field(
        default=45.0, ge=0, description="Wind direction variance"
    )

    # Humidity parameters
    base_humidity_percent: float = Field(default=65.0, ge=0, le=100, description="Average humidity")
    humidity_variance_percent: float = Field(default=15.0, ge=0, description="Humidity variance")
