"""
Consumer load endpoints.

GET /api/v1/loads
GET /api/v1/loads/{id}/current
GET /api/v1/loads/{id}/history
"""

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Query

from src.api.rest.dependencies import SimulationState, get_simulation_state
from src.api.rest.schemas import (
    ConsumerLoadCurrentResponse,
    ConsumerLoadHistoryResponse,
    ConsumerLoadInfo,
    ConsumerLoadListResponse,
    ConsumerLoadReadingResponse,
    IntervalParam,
    OperatingWindowSchema,
)
from src.core.time_series import IntervalMinutes, TimeRange

router = APIRouter()


def _convert_interval(interval: IntervalParam) -> IntervalMinutes:
    """Convert API interval parameter to internal IntervalMinutes."""
    if interval == IntervalParam.ONE_HOUR:
        return IntervalMinutes.ONE_HOUR
    return IntervalMinutes.FIFTEEN_MINUTES


def _load_reading_to_response(reading) -> ConsumerLoadReadingResponse:
    """Convert internal consumer load reading to API response."""
    return ConsumerLoadReadingResponse(
        timestamp=reading.timestamp.isoformat().replace("+00:00", "Z"),
        device_id=reading.device_id,
        device_type=reading.device_type.value,
        device_state=reading.device_state.value,
        device_power_kw=round(reading.device_power_kw, 3),
    )


@router.get("/loads", response_model=ConsumerLoadListResponse)
async def list_loads(
    state: SimulationState = Depends(get_simulation_state),
) -> ConsumerLoadListResponse:
    """
    List all registered consumer load devices.

    Returns information about all configured devices.
    """
    devices = []
    for device_id in state.list_loads():
        simulator = state.get_load(device_id)
        if simulator:
            config = simulator.config
            windows = [
                OperatingWindowSchema(
                    start_hour=w.start_hour,
                    end_hour=w.end_hour,
                )
                for w in config.operating_windows
            ]
            devices.append(
                ConsumerLoadInfo(
                    device_id=device_id,
                    device_type=config.device_type.value,
                    rated_power_kw=config.rated_power_kw,
                    duty_cycle_pct=config.duty_cycle_pct,
                    operate_on_weekends=config.operate_on_weekends,
                    operating_windows=windows,
                )
            )

    return ConsumerLoadListResponse(devices=devices, count=len(devices))


@router.get("/loads/{device_id}/current", response_model=ConsumerLoadCurrentResponse)
async def get_load_current(
    device_id: str,
    state: SimulationState = Depends(get_simulation_state),
) -> ConsumerLoadCurrentResponse:
    """
    Get current device reading.

    Returns the current simulated reading for the specified device.
    """
    simulator = state.get_load(device_id)
    if simulator is None:
        raise HTTPException(status_code=404, detail=f"Device '{device_id}' not found")

    current_time = state.engine.simulation_time
    point = simulator.generate_at(current_time)
    reading = point.value

    return ConsumerLoadCurrentResponse(
        device_id=device_id,
        current=_load_reading_to_response(reading),
    )


@router.get("/loads/{device_id}/history", response_model=ConsumerLoadHistoryResponse)
async def get_load_history(
    device_id: str,
    start_time: datetime | None = Query(default=None, description="Start time (ISO 8601)"),
    end_time: datetime | None = Query(default=None, description="End time (ISO 8601)"),
    interval: IntervalParam = Query(default=IntervalParam.FIFTEEN_MIN, description="Data interval"),
    limit: int = Query(default=100, ge=1, le=1000, description="Maximum results"),
    state: SimulationState = Depends(get_simulation_state),
) -> ConsumerLoadHistoryResponse:
    """
    Get historical device readings.

    Returns historical readings for the specified time range.
    If no time range is specified, returns the last 24 hours.
    """
    simulator = state.get_load(device_id)
    if simulator is None:
        raise HTTPException(status_code=404, detail=f"Device '{device_id}' not found")

    # Default time range: last 24 hours from current simulation time
    current_time = state.engine.simulation_time
    if end_time is None:
        end_time = current_time
    if start_time is None:
        start_time = end_time - timedelta(hours=24)

    # Ensure timezone awareness
    if start_time.tzinfo is None:
        start_time = start_time.replace(tzinfo=timezone.utc)
    if end_time.tzinfo is None:
        end_time = end_time.replace(tzinfo=timezone.utc)

    # Create time range
    time_range = TimeRange(start=start_time, end=end_time)

    # Convert interval
    internal_interval = _convert_interval(interval)

    # Create a temporary simulator with the requested interval
    from src.simulators.consumer_load import ConsumerLoadSimulator

    temp_simulator = ConsumerLoadSimulator(
        entity_id=device_id,
        rng=state.engine.rng,
        interval=internal_interval,
        config=simulator.config,
    )

    # Generate readings
    readings = []
    count = 0
    for point in temp_simulator.iterate_range(time_range):
        if count >= limit:
            break
        readings.append(_load_reading_to_response(point.value))
        count += 1

    # Check if there's more data
    has_more = count >= limit

    return ConsumerLoadHistoryResponse(
        device_id=device_id,
        readings=readings,
        count=len(readings),
        limit=limit,
        has_more=has_more,
        start_time=start_time.isoformat().replace("+00:00", "Z"),
        end_time=end_time.isoformat().replace("+00:00", "Z"),
        interval=interval.value,
    )
