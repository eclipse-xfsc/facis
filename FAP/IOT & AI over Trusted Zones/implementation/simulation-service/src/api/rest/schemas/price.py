"""
Price API schemas.

Request/response schemas for price endpoints.
"""

from pydantic import BaseModel, Field


class PriceReadingResponse(BaseModel):
    """Single price reading response."""

    timestamp: str = Field(..., description="Price timestamp (ISO 8601)")
    price_eur_per_kwh: float = Field(..., description="Price in EUR per kWh")
    tariff_type: str = Field(..., description="Current tariff period")


class PriceCurrentResponse(BaseModel):
    """Current price response."""

    feed_id: str = Field(default="epex-spot-de", description="Price feed identifier")
    current: PriceReadingResponse = Field(..., description="Current price reading")


class PriceForecastResponse(BaseModel):
    """Price forecast response."""

    feed_id: str = Field(default="epex-spot-de", description="Price feed identifier")
    forecast: list[PriceReadingResponse] = Field(..., description="Forecasted prices")
    count: int = Field(..., description="Number of forecast points")
    start_time: str = Field(..., description="Forecast start time")
    end_time: str = Field(..., description="Forecast end time")
    interval: str = Field(..., description="Forecast interval")


class PriceHistoryResponse(BaseModel):
    """Historical prices response."""

    feed_id: str = Field(default="epex-spot-de", description="Price feed identifier")
    prices: list[PriceReadingResponse] = Field(..., description="Historical prices")
    count: int = Field(..., description="Number of prices")
    limit: int = Field(..., description="Maximum requested")
    has_more: bool = Field(..., description="Whether more data is available")
    start_time: str | None = Field(default=None, description="Query start time")
    end_time: str | None = Field(default=None, description="Query end time")
    interval: str = Field(..., description="Data interval")
