"""Tests for energy price simulator."""

import json
from datetime import datetime, timezone

import pytest

from src.core.random_generator import DeterministicRNG
from src.core.time_series import IntervalMinutes, TimeRange
from src.models.price import PriceConfig, PriceReading, TariffType
from src.simulators.energy_price import (
    EnergyPriceSimulator,
    get_tariff_type,
    is_weekend,
)


class TestTariffTypes:
    """Tests for tariff type determination."""

    def test_night_tariff(self) -> None:
        """Test night tariff period (00:00-06:00)."""
        for hour in range(0, 6):
            ts = datetime(2024, 1, 1, hour, 0, 0, tzinfo=timezone.utc)
            assert get_tariff_type(ts) == TariffType.NIGHT

    def test_morning_peak_tariff(self) -> None:
        """Test morning peak tariff period (06:00-09:00)."""
        for hour in range(6, 9):
            ts = datetime(2024, 1, 1, hour, 0, 0, tzinfo=timezone.utc)
            assert get_tariff_type(ts) == TariffType.MORNING_PEAK

    def test_midday_tariff(self) -> None:
        """Test midday tariff period (09:00-17:00)."""
        for hour in range(9, 17):
            ts = datetime(2024, 1, 1, hour, 0, 0, tzinfo=timezone.utc)
            assert get_tariff_type(ts) == TariffType.MIDDAY

    def test_evening_peak_tariff(self) -> None:
        """Test evening peak tariff period (17:00-20:00)."""
        for hour in range(17, 20):
            ts = datetime(2024, 1, 1, hour, 0, 0, tzinfo=timezone.utc)
            assert get_tariff_type(ts) == TariffType.EVENING_PEAK

    def test_evening_tariff(self) -> None:
        """Test evening tariff period (20:00-00:00)."""
        for hour in range(20, 24):
            ts = datetime(2024, 1, 1, hour, 0, 0, tzinfo=timezone.utc)
            assert get_tariff_type(ts) == TariffType.EVENING


class TestWeekendDetection:
    """Tests for weekend detection."""

    def test_weekday_detection(self) -> None:
        """Test that Monday-Friday are not weekends."""
        # Monday 2024-01-01
        monday = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        assert not is_weekend(monday)

        # Friday 2024-01-05
        friday = datetime(2024, 1, 5, 12, 0, 0, tzinfo=timezone.utc)
        assert not is_weekend(friday)

    def test_weekend_detection(self) -> None:
        """Test that Saturday-Sunday are weekends."""
        # Saturday 2024-01-06
        saturday = datetime(2024, 1, 6, 12, 0, 0, tzinfo=timezone.utc)
        assert is_weekend(saturday)

        # Sunday 2024-01-07
        sunday = datetime(2024, 1, 7, 12, 0, 0, tzinfo=timezone.utc)
        assert is_weekend(sunday)


class TestPriceReading:
    """Tests for price reading data model."""

    def test_price_reading_creation(self) -> None:
        """Test creating a price reading."""
        reading = PriceReading(
            timestamp=datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc),
            price_eur_per_kwh=0.26,
            tariff_type=TariffType.MIDDAY,
        )

        assert reading.price_eur_per_kwh == 0.26
        assert reading.tariff_type == TariffType.MIDDAY

    def test_price_reading_to_json_payload(self) -> None:
        """Test JSON payload format."""
        reading = PriceReading(
            timestamp=datetime(2024, 1, 1, 14, 30, 0, tzinfo=timezone.utc),
            price_eur_per_kwh=0.2654,
            tariff_type=TariffType.MIDDAY,
        )

        payload = reading.to_json_payload()

        assert payload["timestamp"] == "2024-01-01T14:30:00Z"
        assert payload["price_eur_per_kwh"] == 0.2654
        assert payload["tariff_type"] == "midday"


class TestEnergyPriceSimulator:
    """Tests for EnergyPriceSimulator class."""

    def test_initialization_with_defaults(self) -> None:
        """Test simulator initializes with default configuration."""
        rng = DeterministicRNG(seed=12345)
        simulator = EnergyPriceSimulator("epex-spot-de", rng)

        assert simulator.entity_id == "epex-spot-de"
        assert simulator.config.feed_id == "epex-spot-de"
        assert simulator.config.night_price == 0.15
        assert simulator.config.evening_peak_price == 0.40

    def test_initialization_with_custom_config(self) -> None:
        """Test simulator initializes with custom configuration."""
        rng = DeterministicRNG(seed=12345)
        config = PriceConfig(
            feed_id="custom-feed",
            night_price=0.10,
            evening_peak_price=0.50,
        )
        simulator = EnergyPriceSimulator("custom-feed", rng, config=config)

        assert simulator.config.night_price == 0.10
        assert simulator.config.evening_peak_price == 0.50

    def test_generate_single_reading(self) -> None:
        """Test generating a single price reading."""
        rng = DeterministicRNG(seed=12345)
        simulator = EnergyPriceSimulator("epex-spot-de", rng)

        timestamp = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        point = simulator.generate_at(timestamp)

        reading = point.value
        assert isinstance(reading, PriceReading)
        assert reading.price_eur_per_kwh > 0
        assert reading.tariff_type == TariffType.MIDDAY

    def test_tariff_type_always_populated(self) -> None:
        """Test that tariff_type field is always populated."""
        rng = DeterministicRNG(seed=12345)
        simulator = EnergyPriceSimulator("epex-spot-de", rng)

        for hour in range(24):
            timestamp = datetime(2024, 1, 1, hour, 0, 0, tzinfo=timezone.utc)
            reading = simulator.generate_at(timestamp).value

            assert reading.tariff_type is not None
            assert isinstance(reading.tariff_type, TariffType)


class TestPricePatterns:
    """Tests for time-of-day price patterns."""

    def test_night_prices_lowest(self) -> None:
        """Test that night prices are the lowest."""
        rng = DeterministicRNG(seed=12345)
        simulator = EnergyPriceSimulator("epex-spot-de", rng)

        # Night price at 03:00
        night_ts = datetime(2024, 1, 1, 3, 0, 0, tzinfo=timezone.utc)
        night_reading = simulator.generate_at(night_ts).value

        # Evening peak at 19:00
        peak_ts = datetime(2024, 1, 1, 19, 0, 0, tzinfo=timezone.utc)
        peak_reading = simulator.generate_at(peak_ts).value

        assert night_reading.price_eur_per_kwh < peak_reading.price_eur_per_kwh

    def test_evening_peak_highest(self) -> None:
        """Test that evening peak prices are the highest."""
        rng = DeterministicRNG(seed=12345)
        simulator = EnergyPriceSimulator("epex-spot-de", rng)

        # Collect prices at different times
        times_and_prices = []
        for hour in [3, 8, 12, 19]:  # Night, morning peak, midday, evening peak
            ts = datetime(2024, 1, 1, hour, 0, 0, tzinfo=timezone.utc)
            reading = simulator.generate_at(ts).value
            times_and_prices.append((hour, reading.price_eur_per_kwh))

        # Evening peak (19:00) should be highest
        evening_peak_price = times_and_prices[3][1]
        for hour, price in times_and_prices[:3]:
            assert evening_peak_price > price, f"Evening peak should be higher than hour {hour}"

    def test_morning_peak_rising(self) -> None:
        """Test that morning peak (~0.33 EUR/kWh) is elevated."""
        rng = DeterministicRNG(seed=12345)
        simulator = EnergyPriceSimulator("epex-spot-de", rng)

        # Morning peak at 08:00
        morning_ts = datetime(2024, 1, 1, 8, 0, 0, tzinfo=timezone.utc)
        morning_reading = simulator.generate_at(morning_ts).value

        # Night at 03:00
        night_ts = datetime(2024, 1, 1, 3, 0, 0, tzinfo=timezone.utc)
        night_reading = simulator.generate_at(night_ts).value

        assert morning_reading.price_eur_per_kwh > night_reading.price_eur_per_kwh

    def test_midday_moderate(self) -> None:
        """Test that midday prices (~0.26 EUR/kWh) are moderate."""
        rng = DeterministicRNG(seed=12345)
        simulator = EnergyPriceSimulator("epex-spot-de", rng)

        # Midday at 12:00
        midday_ts = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        midday_reading = simulator.generate_at(midday_ts).value

        # Should be between night and evening peak (roughly)
        night_ts = datetime(2024, 1, 1, 3, 0, 0, tzinfo=timezone.utc)
        night_reading = simulator.generate_at(night_ts).value

        peak_ts = datetime(2024, 1, 1, 19, 0, 0, tzinfo=timezone.utc)
        peak_reading = simulator.generate_at(peak_ts).value

        assert night_reading.price_eur_per_kwh < midday_reading.price_eur_per_kwh
        assert midday_reading.price_eur_per_kwh < peak_reading.price_eur_per_kwh


class TestWeekendPricing:
    """Tests for weekend price discounts."""

    def test_weekend_prices_lower(self) -> None:
        """Test that weekend prices are 5-10% lower than weekdays."""
        rng = DeterministicRNG(seed=12345)
        # Use zero volatility for precise comparison
        config = PriceConfig(
            feed_id="test",
            volatility_pct=0.0,
        )
        simulator = EnergyPriceSimulator("test", rng, config=config)

        # Monday 10:00 (weekday)
        weekday_ts = datetime(2024, 1, 1, 10, 0, 0, tzinfo=timezone.utc)
        weekday_reading = simulator.generate_at(weekday_ts).value

        # Saturday 10:00 (weekend)
        weekend_ts = datetime(2024, 1, 6, 10, 0, 0, tzinfo=timezone.utc)
        weekend_reading = simulator.generate_at(weekend_ts).value

        # Weekend should be lower (without volatility, this is guaranteed)
        assert weekend_reading.price_eur_per_kwh < weekday_reading.price_eur_per_kwh

    def test_weekend_discount_range(self) -> None:
        """Test that weekend discount is in the 5-10% range."""
        rng = DeterministicRNG(seed=12345)
        config = PriceConfig(
            feed_id="test",
            weekend_discount_pct=7.5,
            volatility_pct=0.0,  # No volatility for precise testing
        )
        simulator = EnergyPriceSimulator("test", rng, config=config)

        # Same hour on weekday and weekend
        weekday_ts = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        weekend_ts = datetime(2024, 1, 6, 12, 0, 0, tzinfo=timezone.utc)

        weekday_price = simulator.generate_at(weekday_ts).value.price_eur_per_kwh
        weekend_price = simulator.generate_at(weekend_ts).value.price_eur_per_kwh

        # Weekend should be roughly 7.5% lower
        expected_ratio = 1 - 0.075
        actual_ratio = weekend_price / weekday_price

        assert 0.90 <= actual_ratio <= 0.95


class TestVolatility:
    """Tests for price volatility."""

    def test_prices_have_volatility(self) -> None:
        """Test that prices vary with random volatility."""
        rng = DeterministicRNG(seed=12345)
        config = PriceConfig(
            feed_id="test",
            volatility_pct=10.0,
        )
        simulator = EnergyPriceSimulator("test", rng, config=config)

        # Generate prices for same hour on different days
        prices = []
        for day in range(1, 8):  # 7 days
            ts = datetime(2024, 1, day, 12, 0, 0, tzinfo=timezone.utc)
            reading = simulator.generate_at(ts).value
            prices.append(reading.price_eur_per_kwh)

        # Prices should vary (not all identical)
        unique_prices = set(round(p, 4) for p in prices)
        assert len(unique_prices) > 1

    def test_volatility_bounded(self) -> None:
        """Test that volatility doesn't create extreme outliers."""
        rng = DeterministicRNG(seed=12345)
        config = PriceConfig(
            feed_id="test",
            volatility_pct=10.0,
            midday_price=0.26,
        )
        simulator = EnergyPriceSimulator("test", rng, config=config)

        # Generate many readings
        prices = []
        for day in range(1, 32):  # 31 days
            ts = datetime(2024, 1, day, 12, 0, 0, tzinfo=timezone.utc)
            if ts.weekday() < 5:  # Only weekdays for consistency
                reading = simulator.generate_at(ts).value
                prices.append(reading.price_eur_per_kwh)

        # Most prices should be within reasonable range
        avg_price = sum(prices) / len(prices)
        for price in prices:
            # Allow up to 50% deviation (very generous bound)
            assert 0.5 * avg_price <= price <= 1.5 * avg_price


class TestPriceFloor:
    """Tests for minimum price floor."""

    def test_prices_never_negative(self) -> None:
        """Test that prices never go negative."""
        rng = DeterministicRNG(seed=12345)
        simulator = EnergyPriceSimulator("epex-spot-de", rng)

        # Generate many readings
        for day in range(1, 32):
            for hour in range(24):
                ts = datetime(2024, 1, day, hour, 0, 0, tzinfo=timezone.utc)
                reading = simulator.generate_at(ts).value
                assert reading.price_eur_per_kwh >= 0

    def test_price_floor_enforced(self) -> None:
        """Test that price floor (0.05 EUR/kWh) is enforced."""
        rng = DeterministicRNG(seed=12345)
        config = PriceConfig(
            feed_id="test",
            min_price=0.05,
        )
        simulator = EnergyPriceSimulator("test", rng, config=config)

        # Generate many readings
        for day in range(1, 32):
            for hour in range(24):
                ts = datetime(2024, 1, day, hour, 0, 0, tzinfo=timezone.utc)
                reading = simulator.generate_at(ts).value
                assert reading.price_eur_per_kwh >= 0.05


class TestDeterminism:
    """Tests for deterministic behavior."""

    def test_same_seed_produces_identical_prices(self) -> None:
        """Test that same seed produces identical prices."""
        timestamp = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)

        results = []
        for _ in range(5):
            rng = DeterministicRNG(seed=12345)
            simulator = EnergyPriceSimulator("epex-spot-de", rng)
            reading = simulator.generate_at(timestamp).value
            results.append(reading.price_eur_per_kwh)

        assert all(r == results[0] for r in results)

    def test_different_feeds_produce_different_prices(self) -> None:
        """Test that different feed IDs produce different prices."""
        timestamp = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        rng = DeterministicRNG(seed=12345)

        sim1 = EnergyPriceSimulator("feed-001", rng)
        sim2 = EnergyPriceSimulator("feed-002", rng)

        price1 = sim1.generate_at(timestamp).value.price_eur_per_kwh
        price2 = sim2.generate_at(timestamp).value.price_eur_per_kwh

        assert price1 != price2


class TestJSONPayload:
    """Tests for JSON payload format."""

    def test_json_payload_structure(self) -> None:
        """Test that JSON payload matches spec structure."""
        rng = DeterministicRNG(seed=12345)
        simulator = EnergyPriceSimulator("epex-spot-de", rng)

        timestamp = datetime(2024, 1, 1, 14, 30, 0, tzinfo=timezone.utc)
        reading = simulator.generate_at(timestamp).value
        payload = reading.to_json_payload()

        # Check required fields
        assert "timestamp" in payload
        assert "price_eur_per_kwh" in payload
        assert "tariff_type" in payload

        # Check timestamp format (ISO 8601 with Z suffix)
        assert payload["timestamp"].endswith("Z")

        # Check tariff_type is valid string
        valid_tariffs = ["night", "morning_peak", "midday", "evening_peak", "evening"]
        assert payload["tariff_type"] in valid_tariffs

    def test_json_serialization(self) -> None:
        """Test that payload can be serialized to valid JSON."""
        rng = DeterministicRNG(seed=12345)
        simulator = EnergyPriceSimulator("epex-spot-de", rng)

        timestamp = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)
        reading = simulator.generate_at(timestamp).value
        payload = reading.to_json_payload()

        # Should serialize without errors
        json_str = json.dumps(payload, indent=2)
        assert json_str is not None

        # Should deserialize back
        parsed = json.loads(json_str)
        assert parsed == payload


class TestAnalyticsMethods:
    """Tests for analytics helper methods."""

    def test_get_average_daily_price(self) -> None:
        """Test calculating average daily price."""
        rng = DeterministicRNG(seed=12345)
        simulator = EnergyPriceSimulator("epex-spot-de", rng)

        date = datetime(2024, 1, 1, tzinfo=timezone.utc)
        avg_price = simulator.get_average_daily_price(date)

        # Average should be reasonable (between night and peak)
        assert 0.10 <= avg_price <= 0.50

    def test_get_price_range(self) -> None:
        """Test getting daily price range."""
        rng = DeterministicRNG(seed=12345)
        simulator = EnergyPriceSimulator("epex-spot-de", rng)

        date = datetime(2024, 1, 1, tzinfo=timezone.utc)
        min_price, max_price = simulator.get_price_range(date)

        assert min_price < max_price
        assert min_price >= 0.05  # Price floor
        assert max_price <= 1.0  # Reasonable upper bound
