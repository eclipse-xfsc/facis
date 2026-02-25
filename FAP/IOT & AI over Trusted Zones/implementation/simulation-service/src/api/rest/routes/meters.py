"""
Meter data endpoints.

GET /api/v1/meters
GET /api/v1/meters/{id}/current
GET /api/v1/meters/{id}/history
"""

from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query

from src.api.rest.dependencies import SimulationState, get_simulation_state
from src.api.rest.schemas import (
    IntervalParam,
    MeterHistoryResponse,
    MeterInfo,
    MeterListResponse,
    MeterReadingResponse,
    MeterReadingsSchema,
)
from src.core.time_series import IntervalMinutes, TimeRange

router = APIRouter()


def _convert_interval(interval: IntervalParam) -> IntervalMinutes:
    """Convert API interval parameter to internal IntervalMinutes."""
    if interval == IntervalParam.ONE_HOUR:
        return IntervalMinutes.ONE_HOUR
    return IntervalMinutes.FIFTEEN_MINUTES


def _meter_reading_to_response(reading) -> MeterReadingResponse:
    """Convert internal meter reading to API response."""
    return MeterReadingResponse(
        timestamp=reading.timestamp.isoformat().replace("+00:00", "Z"),
        meter_id=reading.meter_id,
        readings=MeterReadingsSchema(
            active_power_l1_w=round(reading.readings.active_power_l1_w, 1),
            active_power_l2_w=round(reading.readings.active_power_l2_w, 1),
            active_power_l3_w=round(reading.readings.active_power_l3_w, 1),
            voltage_l1_v=round(reading.readings.voltage_l1_v, 1),
            voltage_l2_v=round(reading.readings.voltage_l2_v, 1),
            voltage_l3_v=round(reading.readings.voltage_l3_v, 1),
            current_l1_a=round(reading.readings.current_l1_a, 2),
            current_l2_a=round(reading.readings.current_l2_a, 2),
            current_l3_a=round(reading.readings.current_l3_a, 2),
            power_factor=round(reading.readings.power_factor, 2),
            frequency_hz=round(reading.readings.frequency_hz, 2),
            total_energy_kwh=round(reading.readings.total_energy_kwh, 2),
        ),
    )


@router.get("/meters", response_model=MeterListResponse)
async def list_meters(
    state: SimulationState = Depends(get_simulation_state),
) -> MeterListResponse:
    """
    List all registered meters.

    Returns information about all configured energy meters.
    """
    meters = []
    for meter_id in state.list_meters():
        simulator = state.get_meter(meter_id)
        if simulator:
            meters.append(
                MeterInfo(
                    meter_id=meter_id,
                    type="janitza_umg96rm",
                    base_power_kw=simulator.config.base_power_kw,
                    peak_power_kw=simulator.config.peak_power_kw,
                    nominal_voltage_v=simulator.config.nominal_voltage_v,
                )
            )

    return MeterListResponse(meters=meters, count=len(meters))


@router.get("/meters/{meter_id}/current", response_model=MeterReadingResponse)
async def get_meter_current(
    meter_id: str,
    state: SimulationState = Depends(get_simulation_state),
) -> MeterReadingResponse:
    """
    Get current meter reading.

    Returns the current simulated reading for the specified meter.
    """
    simulator = state.get_meter(meter_id)
    if simulator is None:
        raise HTTPException(status_code=404, detail=f"Meter '{meter_id}' not found")

    current_time = state.engine.simulation_time
    point = simulator.generate_at(current_time)
    reading = point.value

    return _meter_reading_to_response(reading)


@router.get("/meters/{meter_id}/history", response_model=MeterHistoryResponse)
async def get_meter_history(
    meter_id: str,
    start_time: datetime | None = Query(default=None, description="Start time (ISO 8601)"),
    end_time: datetime | None = Query(default=None, description="End time (ISO 8601)"),
    interval: IntervalParam = Query(default=IntervalParam.FIFTEEN_MIN, description="Data interval"),
    limit: int = Query(default=100, ge=1, le=1000, description="Maximum results"),
    state: SimulationState = Depends(get_simulation_state),
) -> MeterHistoryResponse:
    """
    Get historical meter readings.

    Returns historical readings for the specified time range.
    If no time range is specified, returns the last 24 hours.
    """
    simulator = state.get_meter(meter_id)
    if simulator is None:
        raise HTTPException(status_code=404, detail=f"Meter '{meter_id}' not found")

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
    from src.simulators.energy_meter import EnergyMeterSimulator

    temp_simulator = EnergyMeterSimulator(
        entity_id=meter_id,
        rng=state.engine.rng,
        interval=internal_interval,
        config=simulator.config,
    )

    # Generate readings with energy tracking
    readings = temp_simulator.generate_range_with_energy_tracking(time_range)

    # Apply limit
    has_more = len(readings) > limit
    readings = readings[:limit]

    # Convert to response format
    response_readings = [_meter_reading_to_response(r) for r in readings]

    return MeterHistoryResponse(
        meter_id=meter_id,
        readings=response_readings,
        count=len(response_readings),
        limit=limit,
        has_more=has_more,
        start_time=start_time.isoformat().replace("+00:00", "Z"),
        end_time=end_time.isoformat().replace("+00:00", "Z"),
        interval=interval.value,
    )
