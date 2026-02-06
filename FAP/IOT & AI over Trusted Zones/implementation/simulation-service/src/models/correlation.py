"""
Correlated snapshot data model.

Pydantic schema for synchronized multi-feed data snapshots with derived metrics.
Spec section 11.8: Correlation Engine.
"""

from datetime import datetime

from pydantic import BaseModel, Field, computed_field

from src.models.consumer_load import ConsumerLoadReading
from src.models.meter import MeterReading
from src.models.price import PriceReading
from src.models.pv import PVReading
from src.models.weather import WeatherReading


class DerivedMetrics(BaseModel):
    """Derived metrics calculated from correlated feeds."""

    total_consumption_kw: float = Field(
        ...,
        ge=0,
        description="Total consumption from all meters and loads in kW",
    )
    total_generation_kw: float = Field(
        ...,
        ge=0,
        description="Total generation from all PV systems in kW",
    )
    net_grid_power_kw: float = Field(
        ...,
        description="Net power from grid (positive=import, negative=export) in kW",
    )
    self_consumption_ratio: float = Field(
        ...,
        ge=0.0,
        le=1.0,
        description="Ratio of self-consumed generation (0-1)",
    )
    current_cost_eur_per_hour: float = Field(
        ...,
        description="Current cost rate based on net grid power and price in EUR/hour",
    )

    def to_json_payload(self) -> dict:
        """Convert to JSON payload."""
        return {
            "total_consumption_kw": round(self.total_consumption_kw, 3),
            "total_generation_kw": round(self.total_generation_kw, 3),
            "net_grid_power_kw": round(self.net_grid_power_kw, 3),
            "self_consumption_ratio": round(self.self_consumption_ratio, 4),
            "current_cost_eur_per_hour": round(self.current_cost_eur_per_hour, 4),
        }


class CorrelatedSnapshot(BaseModel):
    """
    Synchronized snapshot of all simulation feeds at a single timestamp.

    Contains readings from all simulators plus derived metrics.
    All feeds share the same timestamp for correlation analysis.
    """

    timestamp: datetime = Field(
        ...,
        description="Synchronized timestamp for all feeds (ISO 8601)",
    )

    # Individual feed readings
    weather: WeatherReading | None = Field(
        default=None,
        description="Weather conditions at this timestamp",
    )
    pv_readings: list[PVReading] = Field(
        default_factory=list,
        description="PV generation readings from all systems",
    )
    meter_readings: list[MeterReading] = Field(
        default_factory=list,
        description="Energy meter readings from all meters",
    )
    consumer_loads: list[ConsumerLoadReading] = Field(
        default_factory=list,
        description="Consumer load readings from all devices",
    )
    price: PriceReading | None = Field(
        default=None,
        description="Energy price at this timestamp",
    )

    # Derived metrics
    metrics: DerivedMetrics = Field(
        ...,
        description="Derived metrics calculated from all feeds",
    )

    @computed_field
    @property
    def timestamp_iso(self) -> str:
        """Return timestamp in ISO 8601 format."""
        return self.timestamp.isoformat().replace("+00:00", "Z")

    def to_json_payload(self) -> dict:
        """Convert to JSON payload matching spec structure."""
        return {
            "timestamp": self.timestamp_iso,
            "weather": self.weather.to_json_payload() if self.weather else None,
            "pv_readings": [pv.to_json_payload() for pv in self.pv_readings],
            "meter_readings": [meter.to_json_payload() for meter in self.meter_readings],
            "consumer_loads": [load.to_json_payload() for load in self.consumer_loads],
            "price": self.price.to_json_payload() if self.price else None,
            "metrics": self.metrics.to_json_payload(),
        }


class CorrelationConfig(BaseModel):
    """Configuration for the correlation engine."""

    # IDs of simulators to include in correlation
    weather_station_id: str | None = Field(
        default="berlin-001",
        description="Weather station ID to include",
    )
    pv_system_ids: list[str] = Field(
        default_factory=lambda: ["pv-system-001"],
        description="PV system IDs to include",
    )
    meter_ids: list[str] = Field(
        default_factory=lambda: ["janitza-umg96rm-001"],
        description="Meter IDs to include",
    )
    load_ids: list[str] = Field(
        default_factory=lambda: ["industrial-oven-001"],
        description="Consumer load device IDs to include",
    )
    price_feed_id: str | None = Field(
        default="epex-spot-de",
        description="Price feed ID to include",
    )
