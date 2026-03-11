"""
Streetlight telemetry data model.

Pydantic schema for streetlight dimming and power readings.
"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class StreetlightReading(BaseModel):
    """Streetlight telemetry reading."""

    type: Literal["streetlight"] = Field(default="streetlight", description="Feed type")
    schema_version: str = Field(default="1.0", description="Schema version")
    site_id: str = Field(default="", description="Site identifier")
    city_id: str = Field(default="", description="City identifier")
    zone_id: str = Field(..., description="Zone identifier (links to events/traffic)")
    light_id: str = Field(..., description="Unique streetlight identifier")
    timestamp: datetime = Field(..., description="Reading timestamp in ISO 8601 format")
    dimming_level_pct: float = Field(
        ..., ge=0.0, le=100.0, description="Dimming level percentage (0=off, 100=full)"
    )
    power_w: float = Field(..., ge=0.0, description="Estimated power consumption in watts")

    @property
    def asset_id(self) -> str:
        """Asset identifier (same as light_id)."""
        return self.light_id

    def to_json_payload(self) -> dict:
        """Convert to JSON payload."""
        return {
            "type": self.type,
            "schema_version": self.schema_version,
            "site_id": self.site_id,
            "city_id": self.city_id,
            "zone_id": self.zone_id,
            "light_id": self.light_id,
            "asset_id": self.asset_id,
            "timestamp": self.timestamp.isoformat().replace("+00:00", "Z"),
            "dimming_level_pct": round(self.dimming_level_pct, 1),
            "power_w": round(self.power_w, 1),
        }


class StreetlightConfig(BaseModel):
    """Configuration for a streetlight."""

    light_id: str = Field(..., description="Unique streetlight identifier")
    zone_id: str = Field(..., description="Zone this light belongs to")
    rated_power_w: float = Field(
        default=150.0, ge=0.0, description="Rated power at 100% dimming in watts"
    )
