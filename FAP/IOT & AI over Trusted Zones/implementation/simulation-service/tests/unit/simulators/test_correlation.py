"""Tests for correlation engine.

Acceptance criteria from spec section 11.8:
- Weather generated before PV (correct dependency order)
- All feeds share synchronized timestamps
- Derived metrics calculated correctly
- Self-consumption ratio in 0-1 range
- Deterministic output for same seed/time
- Batch generation for time ranges works
"""

from datetime import datetime, timezone

import pytest

from src.core.random_generator import DeterministicRNG
from src.core.time_series import IntervalMinutes, TimeRange
from src.models.consumer_load import ConsumerLoadConfig, DeviceType, OperatingWindow
from src.models.correlation import CorrelatedSnapshot, CorrelationConfig, DerivedMetrics
from src.models.meter import MeterConfig
from src.models.price import PriceConfig
from src.models.pv import PVConfig
from src.models.weather import WeatherConfig
from src.simulators.consumer_load import ConsumerLoadSimulator
from src.simulators.correlation import CorrelationEngine
from src.simulators.energy_meter import EnergyMeterSimulator
from src.simulators.energy_price import EnergyPriceSimulator
from src.simulators.pv_generation import PVGenerationSimulator
from src.simulators.weather import WeatherSimulator


class TestDerivedMetrics:
    """Tests for DerivedMetrics model."""

    def test_derived_metrics_creation(self) -> None:
        """Test creating derived metrics."""
        metrics = DerivedMetrics(
            total_consumption_kw=15.5,
            total_generation_kw=8.0,
            net_grid_power_kw=7.5,
            self_consumption_ratio=1.0,
            current_cost_eur_per_hour=1.95,
        )

        assert metrics.total_consumption_kw == 15.5
        assert metrics.total_generation_kw == 8.0
        assert metrics.net_grid_power_kw == 7.5
        assert metrics.self_consumption_ratio == 1.0
        assert metrics.current_cost_eur_per_hour == 1.95

    def test_self_consumption_ratio_bounds(self) -> None:
        """Test that self-consumption ratio must be in 0-1 range."""
        # Valid at bounds
        DerivedMetrics(
            total_consumption_kw=10.0,
            total_generation_kw=5.0,
            net_grid_power_kw=5.0,
            self_consumption_ratio=0.0,
            current_cost_eur_per_hour=0.0,
        )
        DerivedMetrics(
            total_consumption_kw=10.0,
            total_generation_kw=5.0,
            net_grid_power_kw=5.0,
            self_consumption_ratio=1.0,
            current_cost_eur_per_hour=0.0,
        )

        # Invalid below 0
        with pytest.raises(ValueError):
            DerivedMetrics(
                total_consumption_kw=10.0,
                total_generation_kw=5.0,
                net_grid_power_kw=5.0,
                self_consumption_ratio=-0.1,
                current_cost_eur_per_hour=0.0,
            )

        # Invalid above 1
        with pytest.raises(ValueError):
            DerivedMetrics(
                total_consumption_kw=10.0,
                total_generation_kw=5.0,
                net_grid_power_kw=5.0,
                self_consumption_ratio=1.1,
                current_cost_eur_per_hour=0.0,
            )

    def test_to_json_payload(self) -> None:
        """Test JSON payload format."""
        metrics = DerivedMetrics(
            total_consumption_kw=15.5678,
            total_generation_kw=8.1234,
            net_grid_power_kw=7.4444,
            self_consumption_ratio=0.87654,
            current_cost_eur_per_hour=1.95432,
        )

        payload = metrics.to_json_payload()

        assert payload["total_consumption_kw"] == 15.568
        assert payload["total_generation_kw"] == 8.123
        assert payload["net_grid_power_kw"] == 7.444
        assert payload["self_consumption_ratio"] == 0.8765
        assert payload["current_cost_eur_per_hour"] == 1.9543


class TestCorrelatedSnapshot:
    """Tests for CorrelatedSnapshot model."""

    def test_snapshot_creation_minimal(self) -> None:
        """Test creating a snapshot with minimal data."""
        ts = datetime(2024, 6, 15, 12, 0, 0, tzinfo=timezone.utc)
        metrics = DerivedMetrics(
            total_consumption_kw=0.0,
            total_generation_kw=0.0,
            net_grid_power_kw=0.0,
            self_consumption_ratio=0.0,
            current_cost_eur_per_hour=0.0,
        )

        snapshot = CorrelatedSnapshot(timestamp=ts, metrics=metrics)

        assert snapshot.timestamp == ts
        assert snapshot.weather is None
        assert snapshot.pv_readings == []
        assert snapshot.meter_readings == []
        assert snapshot.consumer_loads == []
        assert snapshot.price is None

    def test_timestamp_iso_format(self) -> None:
        """Test timestamp ISO format property."""
        ts = datetime(2024, 6, 15, 12, 30, 0, tzinfo=timezone.utc)
        metrics = DerivedMetrics(
            total_consumption_kw=0.0,
            total_generation_kw=0.0,
            net_grid_power_kw=0.0,
            self_consumption_ratio=0.0,
            current_cost_eur_per_hour=0.0,
        )

        snapshot = CorrelatedSnapshot(timestamp=ts, metrics=metrics)

        assert snapshot.timestamp_iso == "2024-06-15T12:30:00Z"


class TestCorrelationEngine:
    """Tests for CorrelationEngine."""

    @pytest.fixture
    def rng(self) -> DeterministicRNG:
        """Create a deterministic RNG with fixed seed."""
        return DeterministicRNG(seed=12345)

    @pytest.fixture
    def weather_simulator(self, rng: DeterministicRNG) -> WeatherSimulator:
        """Create a weather simulator."""
        config = WeatherConfig(latitude=52.52, longitude=13.405)
        return WeatherSimulator(entity_id="berlin-001", rng=rng, config=config)

    @pytest.fixture
    def pv_simulator(
        self, rng: DeterministicRNG, weather_simulator: WeatherSimulator
    ) -> PVGenerationSimulator:
        """Create a PV simulator linked to weather."""
        config = PVConfig(
            system_id="pv-001",
            weather_station_id="berlin-001",
            nominal_capacity_kwp=10.0,
        )
        return PVGenerationSimulator(
            entity_id="pv-001",
            rng=rng,
            weather_simulator=weather_simulator,
            config=config,
        )

    @pytest.fixture
    def meter_simulator(self, rng: DeterministicRNG) -> EnergyMeterSimulator:
        """Create an energy meter simulator."""
        config = MeterConfig(
            meter_id="meter-001",
            base_power_kw=10.0,
            peak_power_kw=25.0,
        )
        return EnergyMeterSimulator(entity_id="meter-001", rng=rng, config=config)

    @pytest.fixture
    def load_simulator(self, rng: DeterministicRNG) -> ConsumerLoadSimulator:
        """Create a consumer load simulator."""
        config = ConsumerLoadConfig(
            device_id="oven-001",
            device_type=DeviceType.INDUSTRIAL_OVEN,
            rated_power_kw=5.0,
            duty_cycle_pct=100.0,  # Always on for predictable testing
            operating_windows=[OperatingWindow(start_hour=0, end_hour=23)],
            operate_on_weekends=True,
        )
        return ConsumerLoadSimulator(entity_id="oven-001", rng=rng, config=config)

    @pytest.fixture
    def price_simulator(self, rng: DeterministicRNG) -> EnergyPriceSimulator:
        """Create an energy price simulator."""
        config = PriceConfig(feed_id="epex-spot")
        return EnergyPriceSimulator(entity_id="epex-spot", rng=rng, config=config)

    @pytest.fixture
    def correlation_engine(
        self,
        weather_simulator: WeatherSimulator,
        pv_simulator: PVGenerationSimulator,
        meter_simulator: EnergyMeterSimulator,
        load_simulator: ConsumerLoadSimulator,
        price_simulator: EnergyPriceSimulator,
    ) -> CorrelationEngine:
        """Create a fully configured correlation engine."""
        return CorrelationEngine(
            weather_simulator=weather_simulator,
            pv_simulators=[pv_simulator],
            meter_simulators=[meter_simulator],
            load_simulators=[load_simulator],
            price_simulator=price_simulator,
        )

    def test_generate_snapshot_basic(self, correlation_engine: CorrelationEngine) -> None:
        """Test basic snapshot generation."""
        ts = datetime(2024, 6, 15, 12, 0, 0, tzinfo=timezone.utc)
        snapshot = correlation_engine.generate_snapshot(ts)

        assert snapshot.timestamp == ts
        assert snapshot.weather is not None
        assert len(snapshot.pv_readings) == 1
        assert len(snapshot.meter_readings) == 1
        assert len(snapshot.consumer_loads) == 1
        assert snapshot.price is not None
        assert snapshot.metrics is not None

    def test_all_feeds_share_synchronized_timestamps(
        self, correlation_engine: CorrelationEngine
    ) -> None:
        """Test that all feeds share the same timestamp."""
        ts = datetime(2024, 6, 15, 14, 30, 0, tzinfo=timezone.utc)
        snapshot = correlation_engine.generate_snapshot(ts)

        # Timestamp should be aligned to 15-min boundary
        expected_ts = datetime(2024, 6, 15, 14, 30, 0, tzinfo=timezone.utc)

        assert snapshot.timestamp == expected_ts
        assert snapshot.weather.timestamp == expected_ts
        assert snapshot.pv_readings[0].timestamp == expected_ts
        assert snapshot.meter_readings[0].timestamp == expected_ts
        assert snapshot.consumer_loads[0].timestamp == expected_ts
        assert snapshot.price.timestamp == expected_ts

    def test_timestamp_alignment(self, correlation_engine: CorrelationEngine) -> None:
        """Test that unaligned timestamps get aligned to interval boundary."""
        # Timestamp at 14:37:45 should align to 14:30:00 for 15-min intervals
        ts = datetime(2024, 6, 15, 14, 37, 45, tzinfo=timezone.utc)
        snapshot = correlation_engine.generate_snapshot(ts)

        expected_ts = datetime(2024, 6, 15, 14, 30, 0, tzinfo=timezone.utc)
        assert snapshot.timestamp == expected_ts

    def test_deterministic_output_same_seed_time(
        self, rng: DeterministicRNG, weather_simulator: WeatherSimulator
    ) -> None:
        """Test that same seed and time produces identical output."""
        # Create two separate engines with same seed
        rng1 = DeterministicRNG(seed=99999)
        rng2 = DeterministicRNG(seed=99999)

        weather1 = WeatherSimulator(
            entity_id="test-station",
            rng=rng1,
            config=WeatherConfig(),
        )
        weather2 = WeatherSimulator(
            entity_id="test-station",
            rng=rng2,
            config=WeatherConfig(),
        )

        pv_config = PVConfig(system_id="test-pv", weather_station_id="test-station")
        pv1 = PVGenerationSimulator(
            entity_id="test-pv",
            rng=rng1,
            weather_simulator=weather1,
            config=pv_config,
        )
        pv2 = PVGenerationSimulator(
            entity_id="test-pv",
            rng=rng2,
            weather_simulator=weather2,
            config=pv_config,
        )

        engine1 = CorrelationEngine(
            weather_simulator=weather1,
            pv_simulators=[pv1],
        )
        engine2 = CorrelationEngine(
            weather_simulator=weather2,
            pv_simulators=[pv2],
        )

        ts = datetime(2024, 6, 15, 12, 0, 0, tzinfo=timezone.utc)

        snapshot1 = engine1.generate_snapshot(ts)
        snapshot2 = engine2.generate_snapshot(ts)

        # Weather should be identical
        assert (
            snapshot1.weather.conditions.temperature_c == snapshot2.weather.conditions.temperature_c
        )
        assert snapshot1.weather.conditions.ghi_w_m2 == snapshot2.weather.conditions.ghi_w_m2

        # PV should be identical
        assert (
            snapshot1.pv_readings[0].readings.power_output_kw
            == snapshot2.pv_readings[0].readings.power_output_kw
        )

        # Metrics should be identical
        assert snapshot1.metrics.total_generation_kw == snapshot2.metrics.total_generation_kw

    def test_different_seeds_produce_different_output(self) -> None:
        """Test that different seeds produce different output."""
        rng1 = DeterministicRNG(seed=11111)
        rng2 = DeterministicRNG(seed=22222)

        weather1 = WeatherSimulator(
            entity_id="test-station",
            rng=rng1,
            config=WeatherConfig(),
        )
        weather2 = WeatherSimulator(
            entity_id="test-station",
            rng=rng2,
            config=WeatherConfig(),
        )

        engine1 = CorrelationEngine(weather_simulator=weather1)
        engine2 = CorrelationEngine(weather_simulator=weather2)

        ts = datetime(2024, 6, 15, 12, 0, 0, tzinfo=timezone.utc)

        snapshot1 = engine1.generate_snapshot(ts)
        snapshot2 = engine2.generate_snapshot(ts)

        # Weather should be different (different random variance)
        # Note: base values are the same, but variance differs
        # This test may occasionally fail if variance happens to be identical
        # but statistically very unlikely
        assert (
            snapshot1.weather.conditions.temperature_c != snapshot2.weather.conditions.temperature_c
        )

    def test_self_consumption_ratio_in_valid_range(
        self, correlation_engine: CorrelationEngine
    ) -> None:
        """Test that self-consumption ratio is always in 0-1 range."""
        # Test multiple timestamps throughout the day
        test_times = [
            datetime(2024, 6, 15, 0, 0, 0, tzinfo=timezone.utc),  # Night
            datetime(2024, 6, 15, 6, 0, 0, tzinfo=timezone.utc),  # Dawn
            datetime(2024, 6, 15, 12, 0, 0, tzinfo=timezone.utc),  # Midday
            datetime(2024, 6, 15, 18, 0, 0, tzinfo=timezone.utc),  # Evening
            datetime(2024, 6, 15, 23, 0, 0, tzinfo=timezone.utc),  # Late night
        ]

        for ts in test_times:
            snapshot = correlation_engine.generate_snapshot(ts)
            assert 0.0 <= snapshot.metrics.self_consumption_ratio <= 1.0, (
                f"Self-consumption ratio {snapshot.metrics.self_consumption_ratio} "
                f"out of bounds at {ts}"
            )


class TestDerivedMetricsCalculations:
    """Tests for derived metrics calculations."""

    @pytest.fixture
    def rng(self) -> DeterministicRNG:
        """Create a deterministic RNG."""
        return DeterministicRNG(seed=12345)

    def test_net_grid_power_positive_when_consuming(self, rng: DeterministicRNG) -> None:
        """Test net grid power is positive when consumption > generation."""
        # Create engine with meter but no PV (zero generation)
        meter_config = MeterConfig(
            meter_id="meter-001",
            base_power_kw=20.0,  # High consumption
            peak_power_kw=30.0,
        )
        meter = EnergyMeterSimulator(entity_id="meter-001", rng=rng, config=meter_config)

        engine = CorrelationEngine(meter_simulators=[meter])

        ts = datetime(2024, 6, 15, 12, 0, 0, tzinfo=timezone.utc)
        snapshot = engine.generate_snapshot(ts)

        # No generation, positive consumption -> positive net grid power
        assert snapshot.metrics.total_generation_kw == 0.0
        assert snapshot.metrics.total_consumption_kw > 0.0
        assert snapshot.metrics.net_grid_power_kw > 0.0
        assert snapshot.metrics.net_grid_power_kw == snapshot.metrics.total_consumption_kw

    def test_net_grid_power_calculation(self, rng: DeterministicRNG) -> None:
        """Test net grid power = consumption - generation."""
        weather = WeatherSimulator(
            entity_id="weather-001",
            rng=rng,
            config=WeatherConfig(),
        )
        pv_config = PVConfig(
            system_id="pv-001",
            weather_station_id="weather-001",
            nominal_capacity_kwp=50.0,  # Large PV for high generation
        )
        pv = PVGenerationSimulator(
            entity_id="pv-001",
            rng=rng,
            weather_simulator=weather,
            config=pv_config,
        )
        meter_config = MeterConfig(
            meter_id="meter-001",
            base_power_kw=5.0,
            peak_power_kw=10.0,
        )
        meter = EnergyMeterSimulator(entity_id="meter-001", rng=rng, config=meter_config)

        engine = CorrelationEngine(
            weather_simulator=weather,
            pv_simulators=[pv],
            meter_simulators=[meter],
        )

        ts = datetime(2024, 6, 15, 12, 0, 0, tzinfo=timezone.utc)
        snapshot = engine.generate_snapshot(ts)

        expected_net = snapshot.metrics.total_consumption_kw - snapshot.metrics.total_generation_kw
        assert abs(snapshot.metrics.net_grid_power_kw - expected_net) < 0.001

    def test_self_consumption_ratio_all_consumed(self, rng: DeterministicRNG) -> None:
        """Test self-consumption ratio = 1 when all generation is consumed."""
        # High consumption, low generation -> all generation consumed
        weather = WeatherSimulator(
            entity_id="weather-001",
            rng=rng,
            config=WeatherConfig(),
        )
        pv_config = PVConfig(
            system_id="pv-001",
            weather_station_id="weather-001",
            nominal_capacity_kwp=1.0,  # Small PV
        )
        pv = PVGenerationSimulator(
            entity_id="pv-001",
            rng=rng,
            weather_simulator=weather,
            config=pv_config,
        )
        meter_config = MeterConfig(
            meter_id="meter-001",
            base_power_kw=50.0,  # High consumption
            peak_power_kw=100.0,
        )
        meter = EnergyMeterSimulator(entity_id="meter-001", rng=rng, config=meter_config)

        engine = CorrelationEngine(
            weather_simulator=weather,
            pv_simulators=[pv],
            meter_simulators=[meter],
        )

        # Midday for PV generation
        ts = datetime(2024, 6, 15, 12, 0, 0, tzinfo=timezone.utc)
        snapshot = engine.generate_snapshot(ts)

        # If generation > 0 and consumption > generation, ratio should be 1.0
        if snapshot.metrics.total_generation_kw > 0:
            if snapshot.metrics.total_consumption_kw >= snapshot.metrics.total_generation_kw:
                assert snapshot.metrics.self_consumption_ratio == 1.0

    def test_self_consumption_ratio_zero_generation(self, rng: DeterministicRNG) -> None:
        """Test self-consumption ratio = 0 when there's no generation."""
        # Night time - no PV generation
        meter_config = MeterConfig(meter_id="meter-001")
        meter = EnergyMeterSimulator(entity_id="meter-001", rng=rng, config=meter_config)

        engine = CorrelationEngine(meter_simulators=[meter])

        ts = datetime(2024, 6, 15, 2, 0, 0, tzinfo=timezone.utc)  # 2 AM
        snapshot = engine.generate_snapshot(ts)

        assert snapshot.metrics.total_generation_kw == 0.0
        assert snapshot.metrics.self_consumption_ratio == 0.0

    def test_cost_calculation_with_grid_import(self, rng: DeterministicRNG) -> None:
        """Test cost calculation when importing from grid."""
        meter_config = MeterConfig(
            meter_id="meter-001",
            base_power_kw=10.0,
        )
        meter = EnergyMeterSimulator(entity_id="meter-001", rng=rng, config=meter_config)

        price_config = PriceConfig(
            feed_id="price-001",
            midday_price=0.30,  # 0.30 EUR/kWh
            volatility_pct=0.0,  # No volatility for predictable test
        )
        price = EnergyPriceSimulator(entity_id="price-001", rng=rng, config=price_config)

        engine = CorrelationEngine(
            meter_simulators=[meter],
            price_simulator=price,
        )

        ts = datetime(2024, 6, 15, 12, 0, 0, tzinfo=timezone.utc)
        snapshot = engine.generate_snapshot(ts)

        # Cost = net_grid_power * price
        # Net grid power is positive (consuming, no generation)
        assert snapshot.metrics.net_grid_power_kw > 0
        assert snapshot.metrics.current_cost_eur_per_hour > 0

    def test_cost_zero_when_exporting(self, rng: DeterministicRNG) -> None:
        """Test cost is zero when exporting to grid."""
        weather = WeatherSimulator(
            entity_id="weather-001",
            rng=rng,
            config=WeatherConfig(),
        )
        pv_config = PVConfig(
            system_id="pv-001",
            weather_station_id="weather-001",
            nominal_capacity_kwp=100.0,  # Very large PV
        )
        pv = PVGenerationSimulator(
            entity_id="pv-001",
            rng=rng,
            weather_simulator=weather,
            config=pv_config,
        )
        meter_config = MeterConfig(
            meter_id="meter-001",
            base_power_kw=0.5,  # Very low consumption
            peak_power_kw=1.0,
        )
        meter = EnergyMeterSimulator(entity_id="meter-001", rng=rng, config=meter_config)

        price_config = PriceConfig(feed_id="price-001")
        price = EnergyPriceSimulator(entity_id="price-001", rng=rng, config=price_config)

        engine = CorrelationEngine(
            weather_simulator=weather,
            pv_simulators=[pv],
            meter_simulators=[meter],
            price_simulator=price,
        )

        # Midday with high generation
        ts = datetime(2024, 6, 15, 12, 0, 0, tzinfo=timezone.utc)
        snapshot = engine.generate_snapshot(ts)

        # If exporting (negative net grid power), cost should be 0
        if snapshot.metrics.net_grid_power_kw < 0:
            assert snapshot.metrics.current_cost_eur_per_hour == 0.0


class TestBatchGeneration:
    """Tests for batch generation of time ranges."""

    @pytest.fixture
    def simple_engine(self) -> CorrelationEngine:
        """Create a simple correlation engine for batch tests."""
        rng = DeterministicRNG(seed=12345)
        weather = WeatherSimulator(
            entity_id="weather-001",
            rng=rng,
            config=WeatherConfig(),
        )
        return CorrelationEngine(weather_simulator=weather)

    def test_generate_range(self, simple_engine: CorrelationEngine) -> None:
        """Test generating snapshots for a time range."""
        start = datetime(2024, 6, 15, 10, 0, 0, tzinfo=timezone.utc)
        end = datetime(2024, 6, 15, 12, 0, 0, tzinfo=timezone.utc)
        time_range = TimeRange(start=start, end=end)

        snapshots = simple_engine.generate_range(time_range)

        # 2 hours at 15-min intervals = 9 points (10:00, 10:15, ..., 12:00)
        assert len(snapshots) == 9

        # Verify timestamps are sequential
        for i in range(1, len(snapshots)):
            delta = snapshots[i].timestamp - snapshots[i - 1].timestamp
            assert delta.total_seconds() == 15 * 60  # 15 minutes

    def test_iterate_range(self, simple_engine: CorrelationEngine) -> None:
        """Test iterating over snapshots for a time range."""
        start = datetime(2024, 6, 15, 10, 0, 0, tzinfo=timezone.utc)
        end = datetime(2024, 6, 15, 11, 0, 0, tzinfo=timezone.utc)
        time_range = TimeRange(start=start, end=end)

        snapshots = list(simple_engine.iterate_range(time_range))

        # 1 hour at 15-min intervals = 5 points
        assert len(snapshots) == 5

    def test_generate_batch(self, simple_engine: CorrelationEngine) -> None:
        """Test generating a fixed number of consecutive snapshots."""
        start = datetime(2024, 6, 15, 10, 0, 0, tzinfo=timezone.utc)
        count = 4

        snapshots = simple_engine.generate_batch(start, count)

        assert len(snapshots) == 4
        assert snapshots[0].timestamp == start
        assert snapshots[3].timestamp == datetime(2024, 6, 15, 10, 45, 0, tzinfo=timezone.utc)

    def test_batch_determinism(self, simple_engine: CorrelationEngine) -> None:
        """Test that batch generation is deterministic."""
        start = datetime(2024, 6, 15, 10, 0, 0, tzinfo=timezone.utc)

        batch1 = simple_engine.generate_batch(start, 4)
        batch2 = simple_engine.generate_batch(start, 4)

        for s1, s2 in zip(batch1, batch2):
            assert s1.timestamp == s2.timestamp
            assert s1.weather.conditions.temperature_c == s2.weather.conditions.temperature_c


class TestWeatherPVDependency:
    """Tests for weather -> PV dependency ordering."""

    def test_pv_uses_weather_data(self) -> None:
        """Test that PV generation uses weather irradiance data."""
        rng = DeterministicRNG(seed=12345)

        weather_config = WeatherConfig(
            max_clear_sky_ghi_w_m2=1000.0,
            base_cloud_cover_percent=0.0,  # Clear sky
        )
        weather = WeatherSimulator(
            entity_id="weather-001",
            rng=rng,
            config=weather_config,
        )

        pv_config = PVConfig(
            system_id="pv-001",
            weather_station_id="weather-001",
            nominal_capacity_kwp=10.0,
        )
        pv = PVGenerationSimulator(
            entity_id="pv-001",
            rng=rng,
            weather_simulator=weather,
            config=pv_config,
        )

        engine = CorrelationEngine(
            weather_simulator=weather,
            pv_simulators=[pv],
        )

        # Midday should have high irradiance and PV output
        midday = datetime(2024, 6, 15, 12, 0, 0, tzinfo=timezone.utc)
        snapshot = engine.generate_snapshot(midday)

        assert snapshot.weather.conditions.ghi_w_m2 > 0
        assert snapshot.pv_readings[0].readings.power_output_kw > 0

        # Night should have zero irradiance and PV output
        night = datetime(2024, 6, 15, 2, 0, 0, tzinfo=timezone.utc)
        snapshot_night = engine.generate_snapshot(night)

        assert snapshot_night.weather.conditions.ghi_w_m2 == 0
        assert snapshot_night.pv_readings[0].readings.power_output_kw == 0

    def test_pv_irradiance_matches_weather(self) -> None:
        """Test that PV reading irradiance matches weather GHI."""
        rng = DeterministicRNG(seed=12345)

        weather = WeatherSimulator(
            entity_id="weather-001",
            rng=rng,
            config=WeatherConfig(),
        )

        pv_config = PVConfig(
            system_id="pv-001",
            weather_station_id="weather-001",
        )
        pv = PVGenerationSimulator(
            entity_id="pv-001",
            rng=rng,
            weather_simulator=weather,
            config=pv_config,
        )

        engine = CorrelationEngine(
            weather_simulator=weather,
            pv_simulators=[pv],
        )

        ts = datetime(2024, 6, 15, 12, 0, 0, tzinfo=timezone.utc)
        snapshot = engine.generate_snapshot(ts)

        # PV reading should use weather's GHI
        assert (
            snapshot.pv_readings[0].readings.irradiance_w_m2 == snapshot.weather.conditions.ghi_w_m2
        )


class TestCorrelationConfig:
    """Tests for CorrelationConfig."""

    def test_default_config(self) -> None:
        """Test default configuration values."""
        config = CorrelationConfig()

        assert config.weather_station_id == "berlin-001"
        assert config.pv_system_ids == ["pv-system-001"]
        assert config.meter_ids == ["janitza-umg96rm-001"]
        assert config.load_ids == ["industrial-oven-001"]
        assert config.price_feed_id == "epex-spot-de"

    def test_custom_config(self) -> None:
        """Test custom configuration."""
        config = CorrelationConfig(
            weather_station_id="custom-weather",
            pv_system_ids=["pv-1", "pv-2"],
            meter_ids=["meter-1", "meter-2", "meter-3"],
            load_ids=[],
            price_feed_id=None,
        )

        assert config.weather_station_id == "custom-weather"
        assert config.pv_system_ids == ["pv-1", "pv-2"]
        assert len(config.meter_ids) == 3
        assert config.load_ids == []
        assert config.price_feed_id is None


class TestHourlyInterval:
    """Tests for hourly interval configuration."""

    def test_hourly_interval_alignment(self) -> None:
        """Test that hourly interval aligns correctly."""
        rng = DeterministicRNG(seed=12345)
        weather = WeatherSimulator(
            entity_id="weather-001",
            rng=rng,
            config=WeatherConfig(),
            interval=IntervalMinutes.ONE_HOUR,
        )

        engine = CorrelationEngine(
            weather_simulator=weather,
            interval=IntervalMinutes.ONE_HOUR,
        )

        # 14:37 should align to 14:00 for hourly intervals
        ts = datetime(2024, 6, 15, 14, 37, 0, tzinfo=timezone.utc)
        snapshot = engine.generate_snapshot(ts)

        expected = datetime(2024, 6, 15, 14, 0, 0, tzinfo=timezone.utc)
        assert snapshot.timestamp == expected

    def test_hourly_batch_generation(self) -> None:
        """Test batch generation with hourly intervals."""
        rng = DeterministicRNG(seed=12345)
        weather = WeatherSimulator(
            entity_id="weather-001",
            rng=rng,
            config=WeatherConfig(),
            interval=IntervalMinutes.ONE_HOUR,
        )

        engine = CorrelationEngine(
            weather_simulator=weather,
            interval=IntervalMinutes.ONE_HOUR,
        )

        start = datetime(2024, 6, 15, 10, 0, 0, tzinfo=timezone.utc)
        snapshots = engine.generate_batch(start, 4)

        assert len(snapshots) == 4
        assert snapshots[0].timestamp.hour == 10
        assert snapshots[1].timestamp.hour == 11
        assert snapshots[2].timestamp.hour == 12
        assert snapshots[3].timestamp.hour == 13
