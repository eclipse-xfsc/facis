"""
Traffic/movement data model.

Pydantic schema for zone-level traffic index.
"""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class TrafficReading(BaseModel):
    """Traffic/movement reading for a zone."""

    type: Literal["traffic"] = Field(default="traffic", description="Feed type")
    schema_version: str = Field(default="1.0", description="Schema version")
    city_id: str = Field(default="", description="City identifier")
    zone_id: str = Field(..., description="Zone identifier")
    timestamp: datetime = Field(..., description="Reading timestamp in ISO 8601 format")
    traffic_index: float = Field(
        ..., ge=0.0, le=100.0, description="Traffic index (0=empty, 100=gridlock)"
    )

    def to_json_payload(self) -> dict:
        """Convert to JSON payload."""
        return {
            "type": self.type,
            "schema_version": self.schema_version,
            "city_id": self.city_id,
            "zone_id": self.zone_id,
            "timestamp": self.timestamp.isoformat().replace("+00:00", "Z"),
            "traffic_index": round(self.traffic_index, 1),
        }
