"""
City weather/visibility data model.

Pydantic schema for visibility conditions including fog index and sunrise/sunset.
Combines Robert's weather/visibility + sunrise/sunset into one context feed.
"""

from datetime import datetime
from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field


class VisibilityLevel(str, Enum):
    """Visibility classification."""

    GOOD = "good"
    MEDIUM = "medium"
    POOR = "poor"


class VisibilityReading(BaseModel):
    """City weather/visibility reading with sunrise/sunset."""

    type: Literal["city_weather"] = Field(default="city_weather", description="Feed type")
    schema_version: str = Field(default="1.0", description="Schema version")
    city_id: str = Field(default="", description="City identifier")
    timestamp: datetime = Field(..., description="Reading timestamp in ISO 8601 format")
    fog_index: float = Field(
        ..., ge=0.0, le=100.0, description="Fog index (0=clear, 100=dense fog)"
    )
    visibility: VisibilityLevel = Field(..., description="Visibility classification")
    sunrise_time: str = Field(..., description="Today's sunrise time (HH:MM)")
    sunset_time: str = Field(..., description="Today's sunset time (HH:MM)")

    def to_json_payload(self) -> dict:
        """Convert to JSON payload."""
        return {
            "type": self.type,
            "schema_version": self.schema_version,
            "city_id": self.city_id,
            "timestamp": self.timestamp.isoformat().replace("+00:00", "Z"),
            "fog_index": round(self.fog_index, 1),
            "visibility": self.visibility.value,
            "sunrise_time": self.sunrise_time,
            "sunset_time": self.sunset_time,
        }
