"""
Meter API schemas.

Request/response schemas for meter endpoints.
"""


from pydantic import BaseModel, Field


class MeterReadingsSchema(BaseModel):
    """Meter readings for all phases."""

    active_power_l1_w: float = Field(..., description="Active power phase L1 in watts")
    active_power_l2_w: float = Field(..., description="Active power phase L2 in watts")
    active_power_l3_w: float = Field(..., description="Active power phase L3 in watts")
    voltage_l1_v: float = Field(..., description="Voltage phase L1 in volts")
    voltage_l2_v: float = Field(..., description="Voltage phase L2 in volts")
    voltage_l3_v: float = Field(..., description="Voltage phase L3 in volts")
    current_l1_a: float = Field(..., description="Current phase L1 in amperes")
    current_l2_a: float = Field(..., description="Current phase L2 in amperes")
    current_l3_a: float = Field(..., description="Current phase L3 in amperes")
    power_factor: float = Field(..., description="Power factor")
    frequency_hz: float = Field(..., description="Grid frequency in Hz")
    total_energy_kwh: float = Field(..., description="Total cumulative energy in kWh")


class MeterReadingResponse(BaseModel):
    """Single meter reading response."""

    timestamp: str = Field(..., description="Reading timestamp (ISO 8601)")
    meter_id: str = Field(..., description="Meter identifier")
    readings: MeterReadingsSchema = Field(..., description="Meter readings")


class MeterInfo(BaseModel):
    """Meter information."""

    meter_id: str = Field(..., description="Meter identifier")
    type: str = Field(default="janitza_umg96rm", description="Meter type")
    base_power_kw: float = Field(..., description="Base load power in kW")
    peak_power_kw: float = Field(..., description="Peak load power in kW")
    nominal_voltage_v: float = Field(default=230.0, description="Nominal voltage")


class MeterListResponse(BaseModel):
    """List of meters response."""

    meters: list[MeterInfo] = Field(..., description="List of meters")
    count: int = Field(..., description="Number of meters")


class MeterHistoryResponse(BaseModel):
    """Historical meter readings response."""

    meter_id: str = Field(..., description="Meter identifier")
    readings: list[MeterReadingResponse] = Field(..., description="Historical readings")
    count: int = Field(..., description="Number of readings")
    limit: int = Field(..., description="Maximum requested")
    has_more: bool = Field(..., description="Whether more data is available")
    start_time: str | None = Field(default=None, description="Query start time")
    end_time: str | None = Field(default=None, description="Query end time")
    interval: str = Field(..., description="Data interval")
