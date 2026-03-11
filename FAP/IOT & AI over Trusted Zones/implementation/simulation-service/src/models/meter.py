"""
Energy meter reading data model.

Pydantic schema for Janitza meter readings.
"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, computed_field


class MeterReadings(BaseModel):
    """Individual meter readings for all phases."""

    active_power_l1_w: float = Field(..., description="Active power phase L1 in watts")
    active_power_l2_w: float = Field(..., description="Active power phase L2 in watts")
    active_power_l3_w: float = Field(..., description="Active power phase L3 in watts")
    voltage_l1_v: float = Field(..., description="Voltage phase L1 in volts")
    voltage_l2_v: float = Field(..., description="Voltage phase L2 in volts")
    voltage_l3_v: float = Field(..., description="Voltage phase L3 in volts")
    current_l1_a: float = Field(..., description="Current phase L1 in amperes")
    current_l2_a: float = Field(..., description="Current phase L2 in amperes")
    current_l3_a: float = Field(..., description="Current phase L3 in amperes")
    power_factor: float = Field(..., ge=0.0, le=1.0, description="Power factor")
    frequency_hz: float = Field(..., description="Grid frequency in Hz")
    total_energy_kwh: float = Field(..., ge=0.0, description="Total cumulative energy in kWh")


class MeterReading(BaseModel):
    """Complete meter reading payload."""

    type: Literal["energy_meter"] = Field(default="energy_meter", description="Feed type")
    schema_version: str = Field(default="1.0", description="Schema version")
    site_id: str = Field(default="", description="Site identifier for correlation")
    timestamp: datetime = Field(..., description="Reading timestamp in ISO 8601 format")
    meter_id: str = Field(..., description="Unique meter identifier")
    readings: MeterReadings = Field(..., description="Meter readings")

    @computed_field
    @property
    def asset_id(self) -> str:
        """Asset identifier (same as meter_id)."""
        return self.meter_id

    @computed_field
    @property
    def active_power_kw(self) -> float:
        """Total active power across all phases in kW."""
        total_w = (
            self.readings.active_power_l1_w
            + self.readings.active_power_l2_w
            + self.readings.active_power_l3_w
        )
        return round(total_w / 1000.0, 3)

    @computed_field
    @property
    def active_energy_kwh_total(self) -> float:
        """Monotonic energy counter in kWh."""
        return self.readings.total_energy_kwh

    def to_json_payload(self) -> dict:
        """Convert to JSON payload matching spec structure."""
        return {
            "type": self.type,
            "schema_version": self.schema_version,
            "site_id": self.site_id,
            "asset_id": self.asset_id,
            "timestamp": self.timestamp.isoformat().replace("+00:00", "Z"),
            "meter_id": self.meter_id,
            "active_power_kw": self.active_power_kw,
            "active_energy_kwh_total": round(self.active_energy_kwh_total, 2),
            "readings": {
                "active_power_l1_w": round(self.readings.active_power_l1_w, 1),
                "active_power_l2_w": round(self.readings.active_power_l2_w, 1),
                "active_power_l3_w": round(self.readings.active_power_l3_w, 1),
                "voltage_l1_v": round(self.readings.voltage_l1_v, 1),
                "voltage_l2_v": round(self.readings.voltage_l2_v, 1),
                "voltage_l3_v": round(self.readings.voltage_l3_v, 1),
                "current_l1_a": round(self.readings.current_l1_a, 2),
                "current_l2_a": round(self.readings.current_l2_a, 2),
                "current_l3_a": round(self.readings.current_l3_a, 2),
                "power_factor": round(self.readings.power_factor, 2),
                "frequency_hz": round(self.readings.frequency_hz, 2),
                "total_energy_kwh": round(self.readings.total_energy_kwh, 2),
            },
        }


class MeterConfig(BaseModel):
    """Configuration for an energy meter."""

    meter_id: str = Field(..., description="Unique meter identifier")
    base_power_kw: float = Field(default=10.0, ge=0.0, description="Base load power in kW")
    peak_power_kw: float = Field(default=25.0, ge=0.0, description="Peak load power in kW")
    nominal_voltage_v: float = Field(default=230.0, description="Nominal voltage in volts")
    voltage_variance_pct: float = Field(
        default=5.0, ge=0.0, le=10.0, description="Voltage variance percentage"
    )
    nominal_frequency_hz: float = Field(default=50.0, description="Nominal frequency in Hz")
    frequency_variance_hz: float = Field(
        default=0.05, ge=0.0, description="Frequency variance in Hz"
    )
    power_factor_min: float = Field(
        default=0.95, ge=0.8, le=1.0, description="Minimum power factor"
    )
    power_factor_max: float = Field(
        default=0.99, ge=0.8, le=1.0, description="Maximum power factor"
    )
    initial_energy_kwh: float = Field(
        default=0.0, ge=0.0, description="Initial energy reading in kWh"
    )
