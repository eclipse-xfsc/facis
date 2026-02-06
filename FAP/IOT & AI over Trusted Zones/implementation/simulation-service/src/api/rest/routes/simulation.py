"""
Simulation control endpoints.

POST /api/v1/simulation/start
POST /api/v1/simulation/pause
POST /api/v1/simulation/reset
GET /api/v1/simulation/status
"""

from fastapi import APIRouter, Depends

from src.api.rest.dependencies import SimulationState, get_simulation_state
from src.api.rest.schemas import (
    SimulationPauseResponse,
    SimulationResetRequest,
    SimulationResetResponse,
    SimulationStartRequest,
    SimulationStartResponse,
    SimulationStatusResponse,
)
from src.core.engine import EngineState

router = APIRouter()


@router.get("/simulation/status", response_model=SimulationStatusResponse)
async def get_simulation_status(
    state: SimulationState = Depends(get_simulation_state),
) -> SimulationStatusResponse:
    """
    Get current simulation status.

    Returns the current state, time, and configuration of the simulation.
    """
    snapshot = state.engine.get_snapshot()

    return SimulationStatusResponse(
        state=snapshot.state.value,
        simulation_time=snapshot.simulation_time_iso,
        seed=snapshot.seed,
        acceleration=snapshot.acceleration,
        registered_entities=snapshot.active_entities + len(state._price_feeds),
    )


@router.post("/simulation/start", response_model=SimulationStartResponse)
async def start_simulation(
    request: SimulationStartRequest | None = None,
    state: SimulationState = Depends(get_simulation_state),
) -> SimulationStartResponse:
    """
    Start the simulation.

    Begins or resumes the simulation clock.
    Optionally specify a start time.
    """
    engine = state.engine

    # Set start time if provided
    if request and request.start_time:
        engine.clock.set_time(request.start_time)

    # Start or resume
    if engine.state == EngineState.PAUSED:
        engine.resume()
        message = "Simulation resumed"
    else:
        engine.start()
        message = "Simulation started"

    return SimulationStartResponse(
        status="started",
        message=message,
        simulation_time=engine.simulation_time_iso,
    )


@router.post("/simulation/pause", response_model=SimulationPauseResponse)
async def pause_simulation(
    state: SimulationState = Depends(get_simulation_state),
) -> SimulationPauseResponse:
    """
    Pause the simulation.

    Pauses the simulation clock. Can be resumed with /start.
    """
    engine = state.engine

    if engine.state == EngineState.RUNNING:
        engine.pause()
        message = "Simulation paused"
    else:
        message = f"Simulation was not running (state: {engine.state.value})"

    return SimulationPauseResponse(
        status="paused",
        message=message,
        simulation_time=engine.simulation_time_iso,
    )


@router.post("/simulation/reset", response_model=SimulationResetResponse)
async def reset_simulation(
    request: SimulationResetRequest | None = None,
    state: SimulationState = Depends(get_simulation_state),
) -> SimulationResetResponse:
    """
    Reset the simulation.

    Resets the simulation to initial state.
    Optionally specify a new seed or start time.
    """
    new_seed = request.seed if request else None
    start_time = request.start_time if request else None

    # Reset with optional new seed
    state.reset(new_seed=new_seed)

    # Set new start time if provided
    if start_time:
        state.engine.clock.reset(start_time=start_time)

    return SimulationResetResponse(
        status="reset",
        message="Simulation reset to initial state",
        seed=state.engine.seed,
        simulation_time=state.engine.simulation_time_iso,
    )
