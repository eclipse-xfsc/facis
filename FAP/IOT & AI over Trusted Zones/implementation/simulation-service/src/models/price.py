"""
Energy price data model.

Pydantic schema for energy market prices.
"""

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class TariffType(str, Enum):
    """Electricity tariff types based on time of day."""

    NIGHT = "night"  # 00:00-06:00
    MORNING_PEAK = "morning_peak"  # 06:00-09:00
    MIDDAY = "midday"  # 09:00-17:00
    EVENING_PEAK = "evening_peak"  # 17:00-20:00
    EVENING = "evening"  # 20:00-00:00


class PriceReading(BaseModel):
    """Energy price reading for a specific timestamp."""

    timestamp: datetime = Field(..., description="Price timestamp in ISO 8601 format")
    price_eur_per_kwh: float = Field(..., ge=0.0, description="Price in EUR per kWh")
    tariff_type: TariffType = Field(..., description="Current tariff period type")

    def to_json_payload(self) -> dict:
        """Convert to JSON payload matching spec structure."""
        return {
            "timestamp": self.timestamp.isoformat().replace("+00:00", "Z"),
            "price_eur_per_kwh": round(self.price_eur_per_kwh, 4),
            "tariff_type": self.tariff_type.value,
        }


class PriceConfig(BaseModel):
    """Configuration for energy price simulation."""

    feed_id: str = Field(default="epex-spot-de", description="Price feed identifier")

    # Base prices per tariff type (EUR/kWh)
    night_price: float = Field(default=0.15, ge=0.0, description="Night tariff base price")
    morning_peak_price: float = Field(default=0.33, ge=0.0, description="Morning peak base price")
    midday_price: float = Field(default=0.26, ge=0.0, description="Midday base price")
    evening_peak_price: float = Field(default=0.40, ge=0.0, description="Evening peak base price")
    evening_price: float = Field(default=0.22, ge=0.0, description="Evening base price")

    # Weekend discount (percentage)
    weekend_discount_pct: float = Field(
        default=7.5, ge=0.0, le=50.0, description="Weekend price discount percentage"
    )

    # Volatility settings
    volatility_pct: float = Field(
        default=10.0, ge=0.0, le=50.0, description="Price volatility percentage"
    )

    # Price floor (never go below this)
    min_price: float = Field(default=0.05, ge=0.0, description="Minimum price floor in EUR/kWh")
