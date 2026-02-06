"""
Simulation API schemas.

Request/response schemas for simulation control endpoints.
"""

from pydantic import BaseModel, Field


class SimulationStatusResponse(BaseModel):
    """Simulation status response."""

    state: str = Field(..., description="Current simulation state")
    simulation_time: str = Field(..., description="Current simulation time (ISO 8601)")
    seed: int = Field(..., description="Simulation seed")
    acceleration: int = Field(..., description="Time acceleration factor")
    registered_entities: int = Field(..., description="Number of registered entities")


class SimulationStartRequest(BaseModel):
    """Request to start simulation."""

    start_time: str | None = Field(
        default=None, description="Start time (ISO 8601), uses current if not provided"
    )


class SimulationStartResponse(BaseModel):
    """Response after starting simulation."""

    status: str = Field(default="started", description="Operation status")
    message: str = Field(..., description="Status message")
    simulation_time: str = Field(..., description="Current simulation time")


class SimulationPauseResponse(BaseModel):
    """Response after pausing simulation."""

    status: str = Field(default="paused", description="Operation status")
    message: str = Field(..., description="Status message")
    simulation_time: str = Field(..., description="Paused simulation time")


class SimulationResetRequest(BaseModel):
    """Request to reset simulation."""

    seed: int | None = Field(default=None, description="New seed value")
    start_time: str | None = Field(default=None, description="New start time (ISO 8601)")


class SimulationResetResponse(BaseModel):
    """Response after resetting simulation."""

    status: str = Field(default="reset", description="Operation status")
    message: str = Field(..., description="Status message")
    seed: int = Field(..., description="Current seed value")
    simulation_time: str = Field(..., description="Reset simulation time")
