"""
Weather API schemas.

Pydantic schemas for weather endpoints.
"""

from pydantic import BaseModel, Field


class LocationSchema(BaseModel):
    """Location data in API response."""

    latitude: float = Field(..., description="Latitude in degrees")
    longitude: float = Field(..., description="Longitude in degrees")


class ConditionsSchema(BaseModel):
    """Weather conditions in API response."""

    temperature_c: float = Field(..., description="Temperature in Celsius")
    humidity_percent: float = Field(..., description="Relative humidity percentage")
    wind_speed_ms: float = Field(..., description="Wind speed in m/s")
    wind_direction_deg: float = Field(..., description="Wind direction in degrees")
    cloud_cover_percent: float = Field(..., description="Cloud cover percentage")
    ghi_w_m2: float = Field(..., description="Global Horizontal Irradiance in W/m²")
    dni_w_m2: float = Field(..., description="Direct Normal Irradiance in W/m²")
    dhi_w_m2: float = Field(..., description="Diffuse Horizontal Irradiance in W/m²")


class WeatherReadingResponse(BaseModel):
    """Weather reading API response matching spec section 11.5."""

    timestamp: str = Field(..., description="Reading timestamp in ISO 8601 format")
    location: LocationSchema = Field(..., description="Geographic location")
    conditions: ConditionsSchema = Field(..., description="Weather conditions")


class WeatherStationInfo(BaseModel):
    """Weather station information."""

    station_id: str = Field(..., description="Weather station identifier")
    latitude: float = Field(..., description="Station latitude")
    longitude: float = Field(..., description="Station longitude")
    base_temperature_summer_c: float = Field(..., description="Base summer temperature")
    base_temperature_winter_c: float = Field(..., description="Base winter temperature")


class WeatherListResponse(BaseModel):
    """Weather stations list response."""

    stations: list[WeatherStationInfo] = Field(..., description="List of weather stations")
    count: int = Field(..., description="Number of stations")


class WeatherHistoryResponse(BaseModel):
    """Weather history API response."""

    station_id: str = Field(..., description="Weather station identifier")
    readings: list[WeatherReadingResponse] = Field(..., description="Historical readings")
    count: int = Field(..., description="Number of readings returned")
    limit: int = Field(..., description="Requested limit")
    has_more: bool = Field(..., description="Whether more results exist")
    start_time: str = Field(..., description="Query start time")
    end_time: str = Field(..., description="Query end time")
    interval: str = Field(..., description="Data interval")
