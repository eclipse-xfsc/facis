"""
Consumer load data model.

Pydantic schema for energy-intensive device readings.
"""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class DeviceState(str, Enum):
    """Device operating state."""

    ON = "ON"
    OFF = "OFF"


class DeviceType(str, Enum):
    """Type of consumer device."""

    INDUSTRIAL_OVEN = "industrial_oven"
    HVAC = "hvac"
    COMPRESSOR = "compressor"
    PUMP = "pump"
    GENERIC = "generic"


class OperatingWindow(BaseModel):
    """Defines an operating time window."""

    start_hour: int = Field(..., ge=0, le=23, description="Start hour (0-23)")
    end_hour: int = Field(..., ge=0, le=23, description="End hour (0-23)")

    def contains_hour(self, hour: int) -> bool:
        """Check if the given hour falls within this window."""
        if self.start_hour <= self.end_hour:
            return self.start_hour <= hour < self.end_hour
        # Handle overnight windows (e.g., 22-06)
        return hour >= self.start_hour or hour < self.end_hour


class ConsumerLoadReading(BaseModel):
    """Consumer device reading for a specific timestamp."""

    timestamp: datetime = Field(..., description="Reading timestamp in ISO 8601 format")
    device_id: str = Field(..., description="Unique device identifier")
    device_type: DeviceType = Field(..., description="Type of device")
    device_state: DeviceState = Field(..., description="Current device state (ON/OFF)")
    device_power_kw: float = Field(..., ge=0.0, description="Current power consumption in kW")

    def to_json_payload(self) -> dict:
        """Convert to JSON payload matching spec structure."""
        return {
            "timestamp": self.timestamp.isoformat().replace("+00:00", "Z"),
            "device_id": self.device_id,
            "device_type": self.device_type.value,
            "device_state": self.device_state.value,
            "device_power_kw": round(self.device_power_kw, 3),
        }


class ConsumerLoadConfig(BaseModel):
    """Configuration for a consumer load device."""

    device_id: str = Field(..., description="Unique device identifier")
    device_type: DeviceType = Field(
        default=DeviceType.INDUSTRIAL_OVEN, description="Type of device"
    )
    rated_power_kw: float = Field(default=3.0, ge=0.0, description="Rated power consumption in kW")
    power_variance_pct: float = Field(
        default=5.0, ge=0.0, le=20.0, description="Power variance percentage when ON"
    )
    duty_cycle_pct: float = Field(
        default=70.0, ge=0.0, le=100.0, description="Duty cycle percentage during operating windows"
    )
    operating_windows: list[OperatingWindow] = Field(
        default_factory=lambda: [
            OperatingWindow(start_hour=7, end_hour=9),
            OperatingWindow(start_hour=11, end_hour=13),
            OperatingWindow(start_hour=15, end_hour=17),
        ],
        description="Operating time windows (weekdays only)",
    )
    operate_on_weekends: bool = Field(
        default=False, description="Whether device operates on weekends"
    )
