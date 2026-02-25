"""
PV generation reading data model.

Pydantic schema for photovoltaic system readings matching spec section 11.6.
"""

from datetime import datetime

from pydantic import BaseModel, Field


class PVReadings(BaseModel):
    """PV system measurement values."""

    power_output_kw: float = Field(..., ge=0, description="Current power output in kW")
    daily_energy_kwh: float = Field(
        ..., ge=0, description="Cumulative energy generated today in kWh"
    )
    irradiance_w_m2: float = Field(..., ge=0, description="Current solar irradiance in W/m²")
    module_temperature_c: float = Field(..., description="Module temperature in Celsius")
    efficiency_percent: float = Field(
        ..., ge=0, le=100, description="Current system efficiency percentage"
    )


class PVReading(BaseModel):
    """Complete PV reading payload matching spec section 11.6."""

    timestamp: datetime = Field(..., description="Reading timestamp in ISO 8601 format")
    system_id: str = Field(..., description="PV system identifier")
    readings: PVReadings = Field(..., description="PV system readings")

    def to_json_payload(self) -> dict:
        """Convert to JSON payload matching spec structure."""
        return {
            "timestamp": self.timestamp.isoformat().replace("+00:00", "Z"),
            "system_id": self.system_id,
            "readings": {
                "power_output_kw": round(self.readings.power_output_kw, 2),
                "daily_energy_kwh": round(self.readings.daily_energy_kwh, 1),
                "irradiance_w_m2": round(self.readings.irradiance_w_m2, 1),
                "module_temperature_c": round(self.readings.module_temperature_c, 1),
                "efficiency_percent": round(self.readings.efficiency_percent, 1),
            },
        }


class PVConfig(BaseModel):
    """Configuration for PV generation simulation."""

    # System identification
    system_id: str = Field(default="pv-system-001", description="PV system identifier")

    # Weather station to correlate with
    weather_station_id: str = Field(
        default="berlin-001",
        description="Weather station ID for irradiance and temperature data",
    )

    # System specifications
    nominal_capacity_kwp: float = Field(
        default=10.0,
        ge=0,
        description="Nominal capacity of PV system in kWp",
    )

    # Performance parameters
    system_losses_percent: float = Field(
        default=15.0,
        ge=0,
        le=50,
        description="Total system losses (wiring, inverter, soiling, etc.) in percent",
    )

    temperature_coefficient_pct_per_c: float = Field(
        default=-0.4,
        le=0,
        description="Power temperature coefficient (negative, typically -0.3 to -0.5%/°C)",
    )

    reference_temperature_c: float = Field(
        default=25.0,
        description="Reference temperature for rated output (typically 25°C STC)",
    )

    # Module characteristics
    noct_c: float = Field(
        default=45.0,
        ge=20,
        le=60,
        description="Nominal Operating Cell Temperature in Celsius",
    )
