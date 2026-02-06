"""
Correlation engine for synchronized multi-feed simulation.

Spec section 11.8: Synchronizes all simulation feeds on a shared time axis
with proper dependency ordering (weather before PV).
"""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import TYPE_CHECKING

from src.core.time_series import IntervalMinutes, TimeRange
from src.models.correlation import (
    CorrelatedSnapshot,
    CorrelationConfig,
    DerivedMetrics,
)

if TYPE_CHECKING:
    from collections.abc import Iterator

    from src.simulators.consumer_load import ConsumerLoadSimulator
    from src.simulators.energy_meter import EnergyMeterSimulator
    from src.simulators.energy_price import EnergyPriceSimulator
    from src.simulators.pv_generation import PVGenerationSimulator
    from src.simulators.weather import WeatherSimulator


class CorrelationEngine:
    """
    Engine that synchronizes all simulation feeds on a shared time axis.

    Ensures proper dependency ordering:
    1. Weather is generated first (required for PV calculations)
    2. PV generation uses weather data
    3. All other feeds are generated in parallel

    All feeds share identical timestamps for correlation analysis.
    """

    def __init__(
        self,
        weather_simulator: WeatherSimulator | None = None,
        pv_simulators: list[PVGenerationSimulator] | None = None,
        meter_simulators: list[EnergyMeterSimulator] | None = None,
        load_simulators: list[ConsumerLoadSimulator] | None = None,
        price_simulator: EnergyPriceSimulator | None = None,
        interval: IntervalMinutes = IntervalMinutes.FIFTEEN_MINUTES,
    ) -> None:
        """
        Initialize the correlation engine.

        Args:
            weather_simulator: Weather station simulator (generated first for PV dependency).
            pv_simulators: List of PV generation simulators.
            meter_simulators: List of energy meter simulators.
            load_simulators: List of consumer load simulators.
            price_simulator: Energy price simulator.
            interval: Time interval for data generation.
        """
        self._weather_simulator = weather_simulator
        self._pv_simulators = pv_simulators or []
        self._meter_simulators = meter_simulators or []
        self._load_simulators = load_simulators or []
        self._price_simulator = price_simulator
        self._interval = interval

    @property
    def interval(self) -> IntervalMinutes:
        """Return the configured interval."""
        return self._interval

    @property
    def interval_minutes(self) -> int:
        """Return the interval in minutes."""
        return self._interval.value

    def align_timestamp(self, timestamp: datetime) -> datetime:
        """
        Align a timestamp to the configured interval boundary.

        Args:
            timestamp: The timestamp to align.

        Returns:
            The aligned timestamp (rounded down to interval boundary).
        """
        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=UTC)

        interval_seconds = self._interval.value * 60
        ts_seconds = int(timestamp.timestamp())
        aligned_seconds = (ts_seconds // interval_seconds) * interval_seconds
        return datetime.fromtimestamp(aligned_seconds, tz=UTC)

    def generate_snapshot(self, timestamp: datetime) -> CorrelatedSnapshot:
        """
        Generate a correlated snapshot at the given timestamp.

        Follows dependency order:
        1. Weather (first - required for PV)
        2. PV generation (depends on weather)
        3. Meters, loads, prices (parallel/independent)

        Args:
            timestamp: The timestamp for which to generate data.

        Returns:
            CorrelatedSnapshot with all feeds and derived metrics.
        """
        aligned_ts = self.align_timestamp(timestamp)

        # Step 1: Generate weather FIRST (dependency for PV)
        weather_reading = None
        if self._weather_simulator is not None:
            weather_point = self._weather_simulator.generate_at(aligned_ts)
            weather_reading = weather_point.value

        # Step 2: Generate PV readings (depends on weather being available)
        # PV simulators internally use weather data through their weather_simulator reference
        pv_readings = []
        for pv_sim in self._pv_simulators:
            pv_point = pv_sim.generate_at(aligned_ts)
            pv_readings.append(pv_point.value)

        # Step 3: Generate independent feeds (meters, loads, prices)
        meter_readings = []
        for meter_sim in self._meter_simulators:
            meter_point = meter_sim.generate_at(aligned_ts)
            meter_readings.append(meter_point.value)

        consumer_loads = []
        for load_sim in self._load_simulators:
            load_point = load_sim.generate_at(aligned_ts)
            consumer_loads.append(load_point.value)

        price_reading = None
        if self._price_simulator is not None:
            price_point = self._price_simulator.generate_at(aligned_ts)
            price_reading = price_point.value

        # Step 4: Calculate derived metrics
        metrics = self._calculate_metrics(
            meter_readings=meter_readings,
            consumer_loads=consumer_loads,
            pv_readings=pv_readings,
            price_reading=price_reading,
        )

        return CorrelatedSnapshot(
            timestamp=aligned_ts,
            weather=weather_reading,
            pv_readings=pv_readings,
            meter_readings=meter_readings,
            consumer_loads=consumer_loads,
            price=price_reading,
            metrics=metrics,
        )

    def _calculate_metrics(
        self,
        meter_readings: list,
        consumer_loads: list,
        pv_readings: list,
        price_reading,
    ) -> DerivedMetrics:
        """
        Calculate derived metrics from all feeds.

        Args:
            meter_readings: List of MeterReading objects.
            consumer_loads: List of ConsumerLoadReading objects.
            pv_readings: List of PVReading objects.
            price_reading: PriceReading object or None.

        Returns:
            DerivedMetrics with calculated values.
        """
        # Total consumption: sum of meter total power + consumer loads
        meter_consumption_kw = 0.0
        for meter in meter_readings:
            # Sum all three phases and convert from W to kW
            total_w = (
                meter.readings.active_power_l1_w
                + meter.readings.active_power_l2_w
                + meter.readings.active_power_l3_w
            )
            meter_consumption_kw += total_w / 1000.0

        load_consumption_kw = sum(load.device_power_kw for load in consumer_loads)
        total_consumption_kw = meter_consumption_kw + load_consumption_kw

        # Total generation: sum of all PV outputs
        total_generation_kw = sum(pv.readings.power_output_kw for pv in pv_readings)

        # Net grid power: consumption - generation
        # Positive = importing from grid, Negative = exporting to grid
        net_grid_power_kw = total_consumption_kw - total_generation_kw

        # Self-consumption ratio: how much of generation is self-consumed
        # If generation > consumption, we export the excess (self-consumption = consumption/generation)
        # If generation <= consumption, we use all generation (self-consumption = 1.0)
        # If no generation, ratio is 0 (or could be defined as 1.0 since no generation to self-consume)
        if total_generation_kw > 0:
            self_consumed_kw = min(total_generation_kw, total_consumption_kw)
            self_consumption_ratio = self_consumed_kw / total_generation_kw
        else:
            # No generation - ratio is 0 (nothing to self-consume)
            self_consumption_ratio = 0.0

        # Clamp ratio to 0-1 range for safety
        self_consumption_ratio = max(0.0, min(1.0, self_consumption_ratio))

        # Current cost rate (EUR/hour)
        # Only charged for grid imports (positive net_grid_power)
        # Export might have feed-in tariff but we charge 0 for simplicity
        if price_reading is not None and net_grid_power_kw > 0:
            # Cost = power (kW) * price (EUR/kWh) = EUR/hour
            current_cost_eur_per_hour = net_grid_power_kw * price_reading.price_eur_per_kwh
        else:
            # No cost if exporting or no price data
            current_cost_eur_per_hour = 0.0

        return DerivedMetrics(
            total_consumption_kw=total_consumption_kw,
            total_generation_kw=total_generation_kw,
            net_grid_power_kw=net_grid_power_kw,
            self_consumption_ratio=self_consumption_ratio,
            current_cost_eur_per_hour=current_cost_eur_per_hour,
        )

    def generate_range(self, time_range: TimeRange) -> list[CorrelatedSnapshot]:
        """
        Generate correlated snapshots for a time range.

        Args:
            time_range: The time range for which to generate data.

        Returns:
            List of CorrelatedSnapshots covering the range.
        """
        return list(self.iterate_range(time_range))

    def iterate_range(self, time_range: TimeRange) -> Iterator[CorrelatedSnapshot]:
        """
        Iterate over correlated snapshots for a time range.

        More memory-efficient than generate_range for large ranges.

        Args:
            time_range: The time range for which to generate data.

        Yields:
            CorrelatedSnapshots covering the range.
        """
        current = self.align_timestamp(time_range.start)
        end = self.align_timestamp(time_range.end)
        interval_delta = timedelta(minutes=self._interval.value)

        while current <= end:
            yield self.generate_snapshot(current)
            current += interval_delta

    def generate_batch(self, start: datetime, count: int) -> list[CorrelatedSnapshot]:
        """
        Generate a batch of consecutive correlated snapshots.

        Args:
            start: The starting timestamp (will be aligned).
            count: Number of snapshots to generate.

        Returns:
            List of consecutive CorrelatedSnapshots.
        """
        current = self.align_timestamp(start)
        interval_delta = timedelta(minutes=self._interval.value)
        snapshots = []

        for _ in range(count):
            snapshots.append(self.generate_snapshot(current))
            current += interval_delta

        return snapshots

    @classmethod
    def from_simulation_state(
        cls,
        simulation_state,
        config: CorrelationConfig | None = None,
        interval: IntervalMinutes = IntervalMinutes.FIFTEEN_MINUTES,
    ) -> CorrelationEngine:
        """
        Create a CorrelationEngine from a SimulationState instance.

        Args:
            simulation_state: SimulationState instance containing all simulators.
            config: Configuration specifying which simulators to include.
            interval: Time interval for data generation.

        Returns:
            Configured CorrelationEngine instance.
        """
        if config is None:
            config = CorrelationConfig()

        # Get weather simulator
        weather_sim = None
        if config.weather_station_id:
            weather_sim = simulation_state.get_weather_station(config.weather_station_id)

        # Get PV simulators
        pv_sims = []
        for pv_id in config.pv_system_ids:
            pv_sim = simulation_state.get_pv_system(pv_id)
            if pv_sim is not None:
                pv_sims.append(pv_sim)

        # Get meter simulators
        meter_sims = []
        for meter_id in config.meter_ids:
            meter_sim = simulation_state.get_meter(meter_id)
            if meter_sim is not None:
                meter_sims.append(meter_sim)

        # Get load simulators
        load_sims = []
        for load_id in config.load_ids:
            load_sim = simulation_state.get_load(load_id)
            if load_sim is not None:
                load_sims.append(load_sim)

        # Get price simulator
        price_sim = None
        if config.price_feed_id:
            price_sim = simulation_state.get_price_feed(config.price_feed_id)

        return cls(
            weather_simulator=weather_sim,
            pv_simulators=pv_sims,
            meter_simulators=meter_sims,
            load_simulators=load_sims,
            price_simulator=price_sim,
            interval=interval,
        )
