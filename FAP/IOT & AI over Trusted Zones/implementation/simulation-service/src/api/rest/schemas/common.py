"""
Common API schemas.

Shared request/response schemas used across endpoints.
"""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class IntervalParam(str, Enum):
    """Supported time intervals for data queries."""

    FIFTEEN_MIN = "15min"
    ONE_HOUR = "1hour"


class TimeRangeQuery(BaseModel):
    """Query parameters for time range filtering."""

    start_time: datetime | None = Field(default=None, description="Start time (ISO 8601)")
    end_time: datetime | None = Field(default=None, description="End time (ISO 8601)")
    interval: IntervalParam = Field(default=IntervalParam.FIFTEEN_MIN, description="Data interval")
    limit: int = Field(default=100, ge=1, le=1000, description="Maximum number of results")


class PaginatedResponse(BaseModel):
    """Base schema for paginated responses."""

    count: int = Field(..., description="Number of items returned")
    limit: int = Field(..., description="Maximum items requested")
    has_more: bool = Field(..., description="Whether more items are available")


class ErrorResponse(BaseModel):
    """Standard error response."""

    error: str = Field(..., description="Error type")
    message: str = Field(..., description="Error message")
    detail: str | None = Field(default=None, description="Additional details")


class HealthResponse(BaseModel):
    """Health check response."""

    status: str = Field(..., description="Service status")
    service: str = Field(..., description="Service name")
    version: str = Field(..., description="Service version")
    timestamp: str = Field(..., description="Current timestamp")


class ConfigResponse(BaseModel):
    """Configuration response."""

    seed: int = Field(..., description="Simulation seed")
    time_acceleration: int = Field(..., description="Time acceleration factor")
    start_time: str | None = Field(default=None, description="Simulation start time")
    simulation_state: str = Field(..., description="Current simulation state")
    registered_meters: list[str] = Field(..., description="List of meter IDs")
    registered_price_feeds: list[str] = Field(..., description="List of price feed IDs")


class ConfigUpdateRequest(BaseModel):
    """Request to update configuration."""

    seed: int | None = Field(default=None, description="New simulation seed")
    time_acceleration: int | None = Field(
        default=None, ge=1, le=1000, description="Time acceleration factor"
    )
