"""
Health check and configuration endpoints.

GET /api/v1/health
GET /api/v1/config
PUT /api/v1/config
"""

from datetime import UTC, datetime

from fastapi import APIRouter, Depends

from src.api.rest.dependencies import SimulationState, get_simulation_state
from src.api.rest.schemas import (
    ConfigResponse,
    ConfigUpdateRequest,
    HealthResponse,
)

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check() -> HealthResponse:
    """
    Health check endpoint.

    Returns the service status and version information.
    """
    return HealthResponse(
        status="healthy",
        service="facis-simulation-service",
        version="1.0.0",
        timestamp=datetime.now(UTC).isoformat().replace("+00:00", "Z"),
    )


@router.get("/config", response_model=ConfigResponse)
async def get_config(
    state: SimulationState = Depends(get_simulation_state),
) -> ConfigResponse:
    """
    Get current service configuration.

    Returns simulation settings, registered entities, and current state.
    """
    engine = state.engine
    snapshot = engine.get_snapshot()

    return ConfigResponse(
        seed=snapshot.seed,
        time_acceleration=snapshot.acceleration,
        start_time=snapshot.simulation_time_iso,
        simulation_state=snapshot.state.value,
        registered_meters=state.list_meters(),
        registered_price_feeds=list(state._price_feeds.keys()),
    )


@router.put("/config", response_model=ConfigResponse)
async def update_config(
    request: ConfigUpdateRequest,
    state: SimulationState = Depends(get_simulation_state),
) -> ConfigResponse:
    """
    Update service configuration.

    Allows updating simulation seed and time acceleration.
    Note: Changing seed will reset the simulation.
    """
    if request.seed is not None:
        state.reset(new_seed=request.seed)

    if request.time_acceleration is not None:
        state.engine.clock.acceleration = request.time_acceleration

    return await get_config(state)
