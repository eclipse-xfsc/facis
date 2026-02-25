"""
Energy price simulator.

Models EPEX Spot day-ahead market prices with time-dependent patterns.
For analytical correlation purposes only, not billing.
"""

from __future__ import annotations

from datetime import UTC, datetime

from src.core.random_generator import DeterministicRNG
from src.core.time_series import BaseTimeSeriesGenerator, IntervalMinutes
from src.models.price import PriceConfig, PriceReading, TariffType
from src.simulators.energy_price.patterns import (
    apply_volatility,
    apply_weekend_discount,
    calculate_base_price,
    enforce_price_floor,
    get_hourly_multiplier,
    get_tariff_type,
    is_weekend,
)


class EnergyPriceSimulator(BaseTimeSeriesGenerator[PriceReading]):
    """
    Energy price feed simulator.

    Generates realistic electricity prices with:
    - Time-of-day pricing (night, morning peak, midday, evening peak)
    - Weekend discounts (5-10% lower)
    - Random volatility for realism
    - Price floor to prevent negative prices

    Prices are for analytical correlation only, not billing purposes.

    Attributes:
        entity_id: Unique price feed identifier.
        config: Price feed configuration parameters.
    """

    def __init__(
        self,
        entity_id: str,
        rng: DeterministicRNG,
        interval: IntervalMinutes = IntervalMinutes.FIFTEEN_MINUTES,
        config: PriceConfig | None = None,
    ) -> None:
        """
        Initialize the energy price simulator.

        Args:
            entity_id: Unique price feed identifier.
            rng: Deterministic random number generator.
            interval: Time interval for price updates.
            config: Price configuration. Uses defaults if None.
        """
        super().__init__(entity_id, rng, interval)

        if config is None:
            config = PriceConfig(feed_id=entity_id)
        self._config = config

    @property
    def config(self) -> PriceConfig:
        """Return the price configuration."""
        return self._config

    def generate_value(self, timestamp: datetime) -> PriceReading:
        """
        Generate a price reading for the given timestamp.

        The price calculation follows this sequence:
        1. Determine tariff type based on hour
        2. Get base price for tariff period
        3. Apply hourly multiplier for smooth transitions
        4. Apply weekend discount if applicable
        5. Add random volatility
        6. Enforce minimum price floor

        Args:
            timestamp: The timestamp for the price reading.

        Returns:
            Complete PriceReading with price and tariff type.
        """
        # Ensure timezone-aware timestamp
        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=UTC)

        # Get deterministic RNG for this timestamp
        ts_ms = int(timestamp.timestamp() * 1000)
        ts_rng = self._rng.get_timestamp_rng(self._entity_id, ts_ms)

        # 1. Determine tariff type
        tariff_type = get_tariff_type(timestamp)

        # 2. Get base price for tariff period
        base_price = calculate_base_price(
            timestamp=timestamp,
            night_price=self._config.night_price,
            morning_peak_price=self._config.morning_peak_price,
            midday_price=self._config.midday_price,
            evening_peak_price=self._config.evening_peak_price,
            evening_price=self._config.evening_price,
        )

        # 3. Apply hourly multiplier for smooth intra-period transitions
        hourly_mult = get_hourly_multiplier(timestamp)
        price = base_price * hourly_mult

        # 4. Apply weekend discount if applicable
        if is_weekend(timestamp):
            price = apply_weekend_discount(price, self._config.weekend_discount_pct)

        # 5. Add random volatility
        price = apply_volatility(price, ts_rng, self._config.volatility_pct)

        # 6. Enforce minimum price floor (never negative)
        price = enforce_price_floor(price, self._config.min_price)

        return PriceReading(
            timestamp=timestamp,
            price_eur_per_kwh=price,
            tariff_type=tariff_type,
        )

    def get_current_tariff(self, timestamp: datetime) -> TariffType:
        """
        Get the current tariff type for a timestamp.

        Args:
            timestamp: The datetime to check.

        Returns:
            Current TariffType.
        """
        return get_tariff_type(timestamp)

    def get_average_daily_price(self, date: datetime) -> float:
        """
        Calculate the average price for a given day.

        Useful for daily cost estimates and analytics.

        Args:
            date: Any timestamp on the target day.

        Returns:
            Average price in EUR/kWh for the day.
        """
        # Generate prices for each hour of the day
        start_of_day = date.replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=UTC)

        total_price = 0.0
        num_readings = 0

        for hour in range(24):
            for minute in [0, 15, 30, 45]:
                ts = start_of_day.replace(hour=hour, minute=minute)
                reading = self.generate_value(ts)
                total_price += reading.price_eur_per_kwh
                num_readings += 1

        return total_price / num_readings if num_readings > 0 else 0.0

    def get_price_range(self, date: datetime) -> tuple[float, float]:
        """
        Get the min and max price for a given day.

        Args:
            date: Any timestamp on the target day.

        Returns:
            Tuple of (min_price, max_price) in EUR/kWh.
        """
        start_of_day = date.replace(hour=0, minute=0, second=0, microsecond=0, tzinfo=UTC)

        prices = []
        for hour in range(24):
            ts = start_of_day.replace(hour=hour, minute=0)
            reading = self.generate_value(ts)
            prices.append(reading.price_eur_per_kwh)

        return (min(prices), max(prices))
