"""
Weather data endpoints.

GET /api/v1/weather
GET /api/v1/weather/{station_id}/current
GET /api/v1/weather/{station_id}/history
"""

from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query

from src.api.rest.dependencies import SimulationState, get_simulation_state
from src.api.rest.schemas import (
    ConditionsSchema,
    IntervalParam,
    LocationSchema,
    WeatherHistoryResponse,
    WeatherListResponse,
    WeatherReadingResponse,
    WeatherStationInfo,
)
from src.core.time_series import IntervalMinutes, TimeRange
from src.models.weather import WeatherReading

router = APIRouter()


def _convert_interval(interval: IntervalParam) -> IntervalMinutes:
    """Convert API interval parameter to internal IntervalMinutes."""
    if interval == IntervalParam.ONE_HOUR:
        return IntervalMinutes.ONE_HOUR
    return IntervalMinutes.FIFTEEN_MINUTES


def _weather_reading_to_response(reading: WeatherReading) -> WeatherReadingResponse:
    """Convert internal weather reading to API response."""
    return WeatherReadingResponse(
        timestamp=reading.timestamp.isoformat().replace("+00:00", "Z"),
        location=LocationSchema(
            latitude=round(reading.location.latitude, 4),
            longitude=round(reading.location.longitude, 4),
        ),
        conditions=ConditionsSchema(
            temperature_c=round(reading.conditions.temperature_c, 1),
            humidity_percent=round(reading.conditions.humidity_percent, 1),
            wind_speed_ms=round(reading.conditions.wind_speed_ms, 1),
            wind_direction_deg=round(reading.conditions.wind_direction_deg, 0),
            cloud_cover_percent=round(reading.conditions.cloud_cover_percent, 1),
            ghi_w_m2=round(reading.conditions.ghi_w_m2, 1),
            dni_w_m2=round(reading.conditions.dni_w_m2, 1),
            dhi_w_m2=round(reading.conditions.dhi_w_m2, 1),
        ),
    )


@router.get("/weather", response_model=WeatherListResponse)
async def list_weather_stations(
    state: SimulationState = Depends(get_simulation_state),
) -> WeatherListResponse:
    """
    List all registered weather stations.

    Returns information about all configured weather data feeds.
    """
    stations = []
    for station_id in state.list_weather_stations():
        simulator = state.get_weather_station(station_id)
        if simulator:
            stations.append(
                WeatherStationInfo(
                    station_id=station_id,
                    latitude=simulator.config.latitude,
                    longitude=simulator.config.longitude,
                    base_temperature_summer_c=simulator.config.base_temperature_summer_c,
                    base_temperature_winter_c=simulator.config.base_temperature_winter_c,
                )
            )

    return WeatherListResponse(stations=stations, count=len(stations))


@router.get("/weather/{station_id}/current", response_model=WeatherReadingResponse)
async def get_weather_current(
    station_id: str,
    state: SimulationState = Depends(get_simulation_state),
) -> WeatherReadingResponse:
    """
    Get current weather reading.

    Returns the current simulated weather data for the specified station.
    Includes temperature, humidity, wind, cloud cover, and solar irradiance.
    """
    simulator = state.get_weather_station(station_id)
    if simulator is None:
        raise HTTPException(
            status_code=404,
            detail=f"Weather station '{station_id}' not found",
        )

    current_time = state.engine.simulation_time
    point = simulator.generate_at(current_time)
    reading = point.value

    return _weather_reading_to_response(reading)


@router.get("/weather/{station_id}/history", response_model=WeatherHistoryResponse)
async def get_weather_history(
    station_id: str,
    start_time: datetime | None = Query(default=None, description="Start time (ISO 8601)"),
    end_time: datetime | None = Query(default=None, description="End time (ISO 8601)"),
    interval: IntervalParam = Query(default=IntervalParam.FIFTEEN_MIN, description="Data interval"),
    limit: int = Query(default=100, ge=1, le=1000, description="Maximum results"),
    state: SimulationState = Depends(get_simulation_state),
) -> WeatherHistoryResponse:
    """
    Get historical weather data.

    Returns historical weather readings for the specified time range.
    If no time range is specified, returns the last 24 hours.
    """
    simulator = state.get_weather_station(station_id)
    if simulator is None:
        raise HTTPException(
            status_code=404,
            detail=f"Weather station '{station_id}' not found",
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
    from src.simulators.weather import WeatherSimulator

    temp_simulator = WeatherSimulator(
        entity_id=station_id,
        rng=state.engine.rng,
        interval=internal_interval,
        config=simulator.config,
    )

    # Generate readings
    points = temp_simulator.generate_range(time_range)

    # Apply limit
    has_more = len(points) > limit
    points = points[:limit]

    # Convert to response format
    response_readings = [_weather_reading_to_response(p.value) for p in points]

    return WeatherHistoryResponse(
        station_id=station_id,
        readings=response_readings,
        count=len(response_readings),
        limit=limit,
        has_more=has_more,
        start_time=start_time.isoformat().replace("+00:00", "Z"),
        end_time=end_time.isoformat().replace("+00:00", "Z"),
        interval=interval.value,
    )
