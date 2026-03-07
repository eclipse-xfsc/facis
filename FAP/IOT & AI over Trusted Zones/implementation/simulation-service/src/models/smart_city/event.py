"""
City event data model.

Pydantic schema for city events (accidents, emergencies, public events).
"""

from datetime import datetime
from enum import Enum
from typing import Literal

from pydantic import BaseModel, Field


class EventType(str, Enum):
    """Type of city event."""

    ACCIDENT = "accident"
    EMERGENCY = "emergency"
    EVENT = "event"


class Severity(int, Enum):
    """Event severity level."""

    LOW = 1
    MEDIUM = 2
    HIGH = 3


class CityEventReading(BaseModel):
    """City event reading for a zone."""

    type: Literal["city_event"] = Field(default="city_event", description="Feed type")
    schema_version: str = Field(default="1.0", description="Schema version")
    city_id: str = Field(default="", description="City identifier")
    zone_id: str = Field(..., description="Zone identifier")
    timestamp: datetime = Field(..., description="Reading timestamp in ISO 8601 format")
    event_type: EventType = Field(..., description="Type of event")
    severity: Severity = Field(..., description="Event severity (1-3)")
    active: bool = Field(default=True, description="Whether event is currently active")

    def to_json_payload(self) -> dict:
        """Convert to JSON payload."""
        return {
            "type": self.type,
            "schema_version": self.schema_version,
            "city_id": self.city_id,
            "zone_id": self.zone_id,
            "timestamp": self.timestamp.isoformat().replace("+00:00", "Z"),
            "event_type": self.event_type.value,
            "severity": self.severity.value,
            "active": self.active,
        }
