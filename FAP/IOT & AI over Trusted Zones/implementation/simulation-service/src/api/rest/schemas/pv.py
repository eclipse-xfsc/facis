"""
PV API schemas.

Request/response schemas for PV endpoints matching spec section 11.6.
"""

from pydantic import BaseModel, Field


class PVReadingsSchema(BaseModel):
    """PV system readings in API response."""

    power_output_kw: float = Field(..., description="Current power output in kW")
    daily_energy_kwh: float = Field(..., description="Cumulative energy generated today in kWh")
    irradiance_w_m2: float = Field(..., description="Current solar irradiance in W/m²")
    module_temperature_c: float = Field(..., description="Module temperature in Celsius")
    efficiency_percent: float = Field(..., description="Current system efficiency percentage")


class PVReadingResponse(BaseModel):
    """PV reading API response matching spec section 11.6."""

    timestamp: str = Field(..., description="Reading timestamp in ISO 8601 format")
    system_id: str = Field(..., description="PV system identifier")
    readings: PVReadingsSchema = Field(..., description="PV system readings")


class PVSystemInfo(BaseModel):
    """PV system information."""

    system_id: str = Field(..., description="PV system identifier")
    weather_station_id: str = Field(..., description="Associated weather station")
    nominal_capacity_kwp: float = Field(..., description="Nominal capacity in kWp")
    system_losses_percent: float = Field(..., description="System losses percentage")
    temperature_coefficient_pct_per_c: float = Field(
        ..., description="Temperature coefficient (%/°C)"
    )


class PVListResponse(BaseModel):
    """PV systems list response."""

    systems: list[PVSystemInfo] = Field(..., description="List of PV systems")
    count: int = Field(..., description="Number of systems")


class PVHistoryResponse(BaseModel):
    """PV history API response."""

    system_id: str = Field(..., description="PV system identifier")
    readings: list[PVReadingResponse] = Field(..., description="Historical readings")
    count: int = Field(..., description="Number of readings returned")
    limit: int = Field(..., description="Requested limit")
    has_more: bool = Field(..., description="Whether more results exist")
    start_time: str = Field(..., description="Query start time")
    end_time: str = Field(..., description="Query end time")
    interval: str = Field(..., description="Data interval")
