"""
Price endpoints.

GET /api/v1/prices/current
GET /api/v1/prices/forecast
GET /api/v1/prices/history
"""

from datetime import UTC, datetime, timedelta

from fastapi import APIRouter, Depends, HTTPException, Query

from src.api.rest.dependencies import SimulationState, get_simulation_state
from src.api.rest.schemas import (
    IntervalParam,
    PriceCurrentResponse,
    PriceForecastResponse,
    PriceHistoryResponse,
    PriceReadingResponse,
)
from src.core.time_series import IntervalMinutes, TimeRange

router = APIRouter()


def _convert_interval(interval: IntervalParam) -> IntervalMinutes:
    """Convert API interval parameter to internal IntervalMinutes."""
    if interval == IntervalParam.ONE_HOUR:
        return IntervalMinutes.ONE_HOUR
    return IntervalMinutes.FIFTEEN_MINUTES


def _price_reading_to_response(reading) -> PriceReadingResponse:
    """Convert internal price reading to API response."""
    return PriceReadingResponse(
        timestamp=reading.timestamp.isoformat().replace("+00:00", "Z"),
        price_eur_per_kwh=round(reading.price_eur_per_kwh, 4),
        tariff_type=reading.tariff_type.value,
    )


@router.get("/prices/current", response_model=PriceCurrentResponse)
async def get_current_price(
    state: SimulationState = Depends(get_simulation_state),
) -> PriceCurrentResponse:
    """
    Get current energy price.

    Returns the current simulated electricity price.
    """
    price_feed = state.get_default_price_feed()
    if price_feed is None:
        raise HTTPException(status_code=404, detail="Price feed not configured")

    current_time = state.engine.simulation_time
    point = price_feed.generate_at(current_time)
    reading = point.value

    return PriceCurrentResponse(
        feed_id="epex-spot-de",
        current=_price_reading_to_response(reading),
    )


@router.get("/prices/forecast", response_model=PriceForecastResponse)
async def get_price_forecast(
    hours: int = Query(default=24, ge=1, le=168, description="Forecast hours (max 168)"),
    interval: IntervalParam = Query(
        default=IntervalParam.ONE_HOUR, description="Forecast interval"
    ),
    state: SimulationState = Depends(get_simulation_state),
) -> PriceForecastResponse:
    """
    Get price forecast.

    Returns forecasted prices for the specified duration.
    Default is 24 hours at 1-hour intervals.
    """
    price_feed = state.get_default_price_feed()
    if price_feed is None:
        raise HTTPException(status_code=404, detail="Price feed not configured")

    # Forecast starts from current simulation time
    current_time = state.engine.simulation_time
    end_time = current_time + timedelta(hours=hours)

    # Create time range
    time_range = TimeRange(start=current_time, end=end_time)

    # Convert interval
    internal_interval = _convert_interval(interval)

    # Create a temporary simulator with the requested interval
    from src.simulators.energy_price import EnergyPriceSimulator

    temp_simulator = EnergyPriceSimulator(
        entity_id="epex-spot-de",
        rng=state.engine.rng,
        interval=internal_interval,
        config=price_feed.config,
    )

    # Generate forecast
    forecast_points = []
    for point in temp_simulator.iterate_range(time_range):
        forecast_points.append(_price_reading_to_response(point.value))

    return PriceForecastResponse(
        feed_id="epex-spot-de",
        forecast=forecast_points,
        count=len(forecast_points),
        start_time=current_time.isoformat().replace("+00:00", "Z"),
        end_time=end_time.isoformat().replace("+00:00", "Z"),
        interval=interval.value,
    )


@router.get("/prices/history", response_model=PriceHistoryResponse)
async def get_price_history(
    start_time: datetime | None = Query(default=None, description="Start time (ISO 8601)"),
    end_time: datetime | None = Query(default=None, description="End time (ISO 8601)"),
    interval: IntervalParam = Query(default=IntervalParam.FIFTEEN_MIN, description="Data interval"),
    limit: int = Query(default=100, ge=1, le=1000, description="Maximum results"),
    state: SimulationState = Depends(get_simulation_state),
) -> PriceHistoryResponse:
    """
    Get historical prices.

    Returns historical prices for the specified time range.
    If no time range is specified, returns the last 24 hours.
    """
    price_feed = state.get_default_price_feed()
    if price_feed is None:
        raise HTTPException(status_code=404, detail="Price feed not configured")

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
    from src.simulators.energy_price import EnergyPriceSimulator

    temp_simulator = EnergyPriceSimulator(
        entity_id="epex-spot-de",
        rng=state.engine.rng,
        interval=internal_interval,
        config=price_feed.config,
    )

    # Generate prices
    prices = []
    count = 0
    for point in temp_simulator.iterate_range(time_range):
        if count >= limit:
            break
        prices.append(_price_reading_to_response(point.value))
        count += 1

    # Check if there's more data
    has_more = count >= limit

    return PriceHistoryResponse(
        feed_id="epex-spot-de",
        prices=prices,
        count=len(prices),
        limit=limit,
        has_more=has_more,
        start_time=start_time.isoformat().replace("+00:00", "Z"),
        end_time=end_time.isoformat().replace("+00:00", "Z"),
        interval=interval.value,
    )
