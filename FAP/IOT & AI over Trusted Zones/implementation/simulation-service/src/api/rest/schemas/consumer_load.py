"""
Consumer load API schemas.

Request/response schemas for consumer load endpoints.
"""

from pydantic import BaseModel, Field


class OperatingWindowSchema(BaseModel):
    """Operating time window."""

    start_hour: int = Field(..., ge=0, le=23, description="Start hour (0-23)")
    end_hour: int = Field(..., ge=0, le=23, description="End hour (0-23)")


class ConsumerLoadReadingResponse(BaseModel):
    """Single consumer load reading response."""

    timestamp: str = Field(..., description="Reading timestamp (ISO 8601)")
    device_id: str = Field(..., description="Device identifier")
    device_type: str = Field(..., description="Type of device")
    device_state: str = Field(..., description="Device state (ON/OFF)")
    device_power_kw: float = Field(..., description="Current power consumption in kW")


class ConsumerLoadInfo(BaseModel):
    """Consumer load device information."""

    device_id: str = Field(..., description="Device identifier")
    device_type: str = Field(..., description="Type of device")
    rated_power_kw: float = Field(..., description="Rated power in kW")
    duty_cycle_pct: float = Field(..., description="Duty cycle percentage")
    operate_on_weekends: bool = Field(..., description="Whether operates on weekends")
    operating_windows: list[OperatingWindowSchema] = Field(
        ..., description="Operating time windows"
    )


class ConsumerLoadListResponse(BaseModel):
    """List of consumer loads response."""

    devices: list[ConsumerLoadInfo] = Field(..., description="List of devices")
    count: int = Field(..., description="Number of devices")


class ConsumerLoadCurrentResponse(BaseModel):
    """Current consumer load reading response."""

    device_id: str = Field(..., description="Device identifier")
    current: ConsumerLoadReadingResponse = Field(..., description="Current reading")


class ConsumerLoadHistoryResponse(BaseModel):
    """Historical consumer load readings response."""

    device_id: str = Field(..., description="Device identifier")
    readings: list[ConsumerLoadReadingResponse] = Field(..., description="Historical readings")
    count: int = Field(..., description="Number of readings")
    limit: int = Field(..., description="Maximum requested")
    has_more: bool = Field(..., description="Whether more data is available")
    start_time: str | None = Field(default=None, description="Query start time")
    end_time: str | None = Field(default=None, description="Query end time")
    interval: str = Field(..., description="Data interval")
