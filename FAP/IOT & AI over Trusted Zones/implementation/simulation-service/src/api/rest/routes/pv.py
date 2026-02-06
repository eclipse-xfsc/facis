"""
PV generation endpoints.

GET /api/v1/pv
GET /api/v1/pv/{system_id}/current
GET /api/v1/pv/{system_id}/history
"""

from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query

from src.api.rest.dependencies import SimulationState, get_simulation_state
from src.api.rest.schemas import (
    IntervalParam,
    PVHistoryResponse,
    PVListResponse,
    PVReadingResponse,
    PVReadingsSchema,
    PVSystemInfo,
)
from src.core.time_series import IntervalMinutes, TimeRange
from src.models.pv import PVReading

router = APIRouter()


def _convert_interval(interval: IntervalParam) -> IntervalMinutes:
    """Convert API interval parameter to internal IntervalMinutes."""
    if interval == IntervalParam.ONE_HOUR:
        return IntervalMinutes.ONE_HOUR
    return IntervalMinutes.FIFTEEN_MINUTES


def _pv_reading_to_response(reading: PVReading) -> PVReadingResponse:
    """Convert internal PV reading to API response."""
    return PVReadingResponse(
        timestamp=reading.timestamp.isoformat().replace("+00:00", "Z"),
        system_id=reading.system_id,
        readings=PVReadingsSchema(
            power_output_kw=round(reading.readings.power_output_kw, 2),
            daily_energy_kwh=round(reading.readings.daily_energy_kwh, 1),
            irradiance_w_m2=round(reading.readings.irradiance_w_m2, 1),
            module_temperature_c=round(reading.readings.module_temperature_c, 1),
            efficiency_percent=round(reading.readings.efficiency_percent, 1),
        ),
    )


@router.get("/pv", response_model=PVListResponse)
async def list_pv_systems(
    state: SimulationState = Depends(get_simulation_state),
) -> PVListResponse:
    """
    List all registered PV systems.

    Returns information about all configured photovoltaic systems.
    """
    systems = []
    for system_id in state.list_pv_systems():
        simulator = state.get_pv_system(system_id)
        if simulator:
            systems.append(
                PVSystemInfo(
                    system_id=system_id,
                    weather_station_id=simulator.config.weather_station_id,
                    nominal_capacity_kwp=simulator.config.nominal_capacity_kwp,
                    system_losses_percent=simulator.config.system_losses_percent,
                    temperature_coefficient_pct_per_c=simulator.config.temperature_coefficient_pct_per_c,
                )
            )

    return PVListResponse(systems=systems, count=len(systems))


@router.get("/pv/{system_id}/current", response_model=PVReadingResponse)
async def get_pv_current(
    system_id: str,
    state: SimulationState = Depends(get_simulation_state),
) -> PVReadingResponse:
    """
    Get current PV generation reading.

    Returns the current simulated PV output for the specified system.
    Power output is correlated with weather data (irradiance, temperature).
    """
    simulator = state.get_pv_system(system_id)
    if simulator is None:
        raise HTTPException(
            status_code=404,
            detail=f"PV system '{system_id}' not found",
        )

    current_time = state.engine.simulation_time
    point = simulator.generate_at(current_time)
    reading = point.value

    return _pv_reading_to_response(reading)


@router.get("/pv/{system_id}/history", response_model=PVHistoryResponse)
async def get_pv_history(
    system_id: str,
    start_time: datetime | None = Query(default=None, description="Start time (ISO 8601)"),
    end_time: datetime | None = Query(default=None, description="End time (ISO 8601)"),
    interval: IntervalParam = Query(default=IntervalParam.FIFTEEN_MIN, description="Data interval"),
    limit: int = Query(default=100, ge=1, le=1000, description="Maximum results"),
    state: SimulationState = Depends(get_simulation_state),
) -> PVHistoryResponse:
    """
    Get historical PV generation data.

    Returns historical PV readings for the specified time range.
    If no time range is specified, returns the last 24 hours.
    """
    simulator = state.get_pv_system(system_id)
    if simulator is None:
        raise HTTPException(
            status_code=404,
            detail=f"PV system '{system_id}' not found",
        )

    # Default time range: last 24 hours from current simulation time
    current_time = state.engine.simulation_time
    if end_time is None:
        end_time = current_time
    if start_time is None:
        start_time = end_time - timedelta(hours=24)

    # Ensure timezone awareness
    if start_time.tzinfo is None:
        start_time = start_time.replace(tzinfo=UTC)
    if end_time.tzinfo is None:
        end_time = end_time.replace(tzinfo=UTC)

    # Create time range
    time_range = TimeRange(start=start_time, end=end_time)

    # Convert interval
    internal_interval = _convert_interval(interval)

    # Create a temporary simulator with the requested interval
    from src.simulators.pv_generation import PVGenerationSimulator

    temp_simulator = PVGenerationSimulator(
        entity_id=system_id,
        rng=state.engine.rng,
        weather_simulator=simulator.weather_simulator,
        interval=internal_interval,
        config=simulator.config,
    )

    # Generate readings
    points = temp_simulator.generate_range(time_range)

    # Apply limit
    has_more = len(points) > limit
    points = points[:limit]

    # Convert to response format
    response_readings = [_pv_reading_to_response(p.value) for p in points]

    return PVHistoryResponse(
        system_id=system_id,
        readings=response_readings,
        count=len(response_readings),
        limit=limit,
        has_more=has_more,
        start_time=start_time.isoformat().replace("+00:00", "Z"),
        end_time=end_time.isoformat().replace("+00:00", "Z"),
        interval=interval.value,
    )
