"""Unit tests for the time-series generator module."""

import time
from datetime import datetime, timedelta, timezone

import pytest

from src.core.random_generator import DeterministicRNG
from src.core.time_series import (
    BaseTimeSeriesGenerator,
    IntervalMinutes,
    TimeRange,
    TimeSeriesPoint,
)


class SimpleGenerator(BaseTimeSeriesGenerator[float]):
    """Simple concrete implementation for testing."""

    def __init__(
        self,
        entity_id: str,
        rng: DeterministicRNG,
        interval: IntervalMinutes = IntervalMinutes.FIFTEEN_MINUTES,
        base_value: float = 100.0,
        variance: float = 10.0,
    ) -> None:
        super().__init__(entity_id, rng, interval)
        self._base_value = base_value
        self._variance = variance

    def generate_value(self, timestamp: datetime) -> float:
        """Generate a deterministic value for the timestamp."""
        return self.get_deterministic_value(timestamp, self._base_value, self._variance)


class TestTimeSeriesPoint:
    """Tests for TimeSeriesPoint."""

    def test_point_creation(self) -> None:
        """Test creating a time-series point."""
        ts = datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
        point = TimeSeriesPoint(timestamp=ts, value=42.0)

        assert point.timestamp == ts
        assert point.value == 42.0

    def test_timestamp_iso_format(self) -> None:
        """Test timestamp ISO 8601 format."""
        ts = datetime(2024, 1, 1, 12, 30, 0, tzinfo=timezone.utc)
        point = TimeSeriesPoint(timestamp=ts, value=0)

        assert point.timestamp_iso == "2024-01-01T12:30:00+00:00"

    def test_timestamp_ms(self) -> None:
        """Test timestamp as Unix milliseconds."""
        ts = datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
        point = TimeSeriesPoint(timestamp=ts, value=0)

        expected_ms = 1704067200000
        assert point.timestamp_ms == expected_ms


class TestTimeRange:
    """Tests for TimeRange."""

    def test_range_creation(self) -> None:
        """Test creating a time range."""
        start = datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
        end = datetime(2024, 1, 2, 0, 0, 0, tzinfo=timezone.utc)
        time_range = TimeRange(start=start, end=end)

        assert time_range.start == start
        assert time_range.end == end

    def test_invalid_range_raises_error(self) -> None:
        """Test that start >= end raises error."""
        start = datetime(2024, 1, 2, 0, 0, 0, tzinfo=timezone.utc)
        end = datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc)

        with pytest.raises(ValueError, match="Start time must be before end time"):
            TimeRange(start=start, end=end)

    def test_from_iso(self) -> None:
        """Test creating range from ISO strings."""
        time_range = TimeRange.from_iso("2024-01-01T00:00:00", "2024-01-02T00:00:00")
        assert time_range.start.day == 1
        assert time_range.end.day == 2

    def test_count_intervals_15min(self) -> None:
        """Test counting 15-minute intervals."""
        time_range = TimeRange.from_iso(
            "2024-01-01T00:00:00",
            "2024-01-01T01:00:00",  # 1 hour = 4 intervals
        )
        count = time_range.count_intervals(IntervalMinutes.FIFTEEN_MINUTES)
        assert count == 4

    def test_count_intervals_1hour(self) -> None:
        """Test counting 1-hour intervals."""
        time_range = TimeRange.from_iso(
            "2024-01-01T00:00:00",
            "2024-01-02T00:00:00",  # 24 hours
        )
        count = time_range.count_intervals(IntervalMinutes.ONE_HOUR)
        assert count == 24


class TestBaseTimeSeriesGenerator:
    """Tests for BaseTimeSeriesGenerator."""

    def test_generator_properties(self) -> None:
        """Test generator property accessors."""
        rng = DeterministicRNG(seed=12345)
        generator = SimpleGenerator("entity-001", rng, IntervalMinutes.FIFTEEN_MINUTES)

        assert generator.entity_id == "entity-001"
        assert generator.interval == IntervalMinutes.FIFTEEN_MINUTES
        assert generator.interval_minutes == 15

    def test_align_timestamp_15min(self) -> None:
        """Test timestamp alignment to 15-minute boundaries."""
        rng = DeterministicRNG(seed=12345)
        generator = SimpleGenerator("entity-001", rng, IntervalMinutes.FIFTEEN_MINUTES)

        # 12:07:30 should align to 12:00:00
        ts = datetime(2024, 1, 1, 12, 7, 30, tzinfo=timezone.utc)
        aligned = generator.align_timestamp(ts)

        assert aligned.hour == 12
        assert aligned.minute == 0
        assert aligned.second == 0

    def test_align_timestamp_1hour(self) -> None:
        """Test timestamp alignment to 1-hour boundaries."""
        rng = DeterministicRNG(seed=12345)
        generator = SimpleGenerator("entity-001", rng, IntervalMinutes.ONE_HOUR)

        # 12:45:30 should align to 12:00:00
        ts = datetime(2024, 1, 1, 12, 45, 30, tzinfo=timezone.utc)
        aligned = generator.align_timestamp(ts)

        assert aligned.hour == 12
        assert aligned.minute == 0
        assert aligned.second == 0

    def test_generate_at(self) -> None:
        """Test generating a single point."""
        rng = DeterministicRNG(seed=12345)
        generator = SimpleGenerator("entity-001", rng)

        ts = datetime(2024, 1, 1, 12, 7, 30, tzinfo=timezone.utc)
        point = generator.generate_at(ts)

        assert isinstance(point, TimeSeriesPoint)
        assert point.timestamp.minute == 0  # Aligned
        assert isinstance(point.value, float)

    def test_generate_range(self) -> None:
        """Test generating a range of points."""
        rng = DeterministicRNG(seed=12345)
        generator = SimpleGenerator("entity-001", rng, IntervalMinutes.FIFTEEN_MINUTES)

        time_range = TimeRange.from_iso("2024-01-01T00:00:00", "2024-01-01T01:00:00")
        points = generator.generate_range(time_range)

        # 00:00, 00:15, 00:30, 00:45, 01:00 = 5 points
        assert len(points) == 5

    def test_generate_batch(self) -> None:
        """Test generating a batch of consecutive points."""
        rng = DeterministicRNG(seed=12345)
        generator = SimpleGenerator("entity-001", rng, IntervalMinutes.FIFTEEN_MINUTES)

        start = datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
        points = generator.generate_batch(start, count=4)

        assert len(points) == 4
        assert points[0].timestamp.minute == 0
        assert points[1].timestamp.minute == 15
        assert points[2].timestamp.minute == 30
        assert points[3].timestamp.minute == 45


class TestDeterminismGuarantees:
    """Tests for determinism guarantees in time-series generation."""

    def test_same_seed_entity_timestamp_produces_identical_values(self) -> None:
        """Test that same seed + entity + timestamp = identical value."""
        seed = 12345
        entity_id = "meter-001"
        ts = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)

        # Generate value twice with fresh instances
        rng1 = DeterministicRNG(seed=seed)
        generator1 = SimpleGenerator(entity_id, rng1)
        point1 = generator1.generate_at(ts)

        rng2 = DeterministicRNG(seed=seed)
        generator2 = SimpleGenerator(entity_id, rng2)
        point2 = generator2.generate_at(ts)

        assert point1.value == point2.value

    def test_different_entities_produce_different_values(self) -> None:
        """Test that different entities produce different values."""
        seed = 12345
        ts = datetime(2024, 1, 1, 12, 0, 0, tzinfo=timezone.utc)

        rng = DeterministicRNG(seed=seed)
        generator1 = SimpleGenerator("meter-001", rng)
        generator2 = SimpleGenerator("meter-002", rng)

        point1 = generator1.generate_at(ts)
        point2 = generator2.generate_at(ts)

        assert point1.value != point2.value

    def test_cross_run_determinism(self) -> None:
        """Test that values are reproducible across runs."""
        seed = 99999
        entity_id = "pv-system-001"

        results = []
        for _ in range(5):
            rng = DeterministicRNG(seed=seed)
            generator = SimpleGenerator(entity_id, rng)
            time_range = TimeRange.from_iso("2024-01-01T00:00:00", "2024-01-01T06:00:00")
            points = generator.generate_range(time_range)
            results.append([p.value for p in points])

        # All runs should produce identical results
        for result in results[1:]:
            assert result == results[0]

    def test_order_independence(self) -> None:
        """Test that query order doesn't affect values."""
        seed = 12345
        entity_id = "entity-001"
        timestamps = [datetime(2024, 1, 1, hour, 0, 0, tzinfo=timezone.utc) for hour in range(24)]

        # Generate in forward order
        rng1 = DeterministicRNG(seed=seed)
        generator1 = SimpleGenerator(entity_id, rng1)
        forward_values = [generator1.generate_at(ts).value for ts in timestamps]

        # Generate in reverse order
        rng2 = DeterministicRNG(seed=seed)
        generator2 = SimpleGenerator(entity_id, rng2)
        reverse_values = [generator2.generate_at(ts).value for ts in reversed(timestamps)]
        reverse_values.reverse()

        assert forward_values == reverse_values


class TestPerformance:
    """Performance tests for time-series generation."""

    def test_one_year_15min_generation_under_5_seconds(self) -> None:
        """
        Test that 1 year of 15-min data generates in <5 seconds.

        1 year = 366 days * 24 hours * 4 (15-min intervals) = 35,136 points (2024 is leap year)
        """
        rng = DeterministicRNG(seed=12345)
        generator = SimpleGenerator("meter-001", rng, IntervalMinutes.FIFTEEN_MINUTES)

        start = datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
        end = datetime(2025, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
        time_range = TimeRange(start=start, end=end)

        # 2024 is a leap year (366 days)
        expected_points = 366 * 24 * 4 + 1  # +1 for end point

        start_time = time.perf_counter()
        points = generator.generate_range(time_range)
        elapsed = time.perf_counter() - start_time

        assert len(points) == expected_points
        assert elapsed < 5.0, f"Generation took {elapsed:.2f}s, expected <5s"

    def test_one_year_1hour_generation_under_2_seconds(self) -> None:
        """
        Test that 1 year of 1-hour data generates quickly.

        1 year = 366 days * 24 hours = 8,784 points (2024 is leap year)
        """
        rng = DeterministicRNG(seed=12345)
        generator = SimpleGenerator("meter-001", rng, IntervalMinutes.ONE_HOUR)

        start = datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
        end = datetime(2025, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
        time_range = TimeRange(start=start, end=end)

        # 2024 is a leap year (366 days)
        expected_points = 366 * 24 + 1  # +1 for end point

        start_time = time.perf_counter()
        points = generator.generate_range(time_range)
        elapsed = time.perf_counter() - start_time

        assert len(points) == expected_points
        assert elapsed < 2.0, f"Generation took {elapsed:.2f}s, expected <2s"

    def test_multiple_entities_parallel_generation(self) -> None:
        """Test generating data for multiple entities."""
        rng = DeterministicRNG(seed=12345)
        num_entities = 10

        generators = [
            SimpleGenerator(f"entity-{i:03d}", rng, IntervalMinutes.FIFTEEN_MINUTES)
            for i in range(num_entities)
        ]

        time_range = TimeRange.from_iso(
            "2024-01-01T00:00:00",
            "2024-02-01T00:00:00",  # 1 month
        )

        start_time = time.perf_counter()
        all_points = []
        for generator in generators:
            points = generator.generate_range(time_range)
            all_points.append(points)
        elapsed = time.perf_counter() - start_time

        # Each entity should have same number of points
        expected_per_entity = 31 * 24 * 4 + 1  # 31 days
        for points in all_points:
            assert len(points) == expected_per_entity

        # Should complete in reasonable time
        assert elapsed < 10.0, f"Generation took {elapsed:.2f}s"

    def test_iterator_memory_efficiency(self) -> None:
        """Test that iterator doesn't load all data at once."""
        rng = DeterministicRNG(seed=12345)
        generator = SimpleGenerator("meter-001", rng, IntervalMinutes.FIFTEEN_MINUTES)

        start = datetime(2024, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
        end = datetime(2025, 1, 1, 0, 0, 0, tzinfo=timezone.utc)
        time_range = TimeRange(start=start, end=end)

        # Iterate and count without storing all points
        count = 0
        for _ in generator.iterate_range(time_range):
            count += 1
            if count > 100:  # Just verify it works, don't iterate all
                break

        assert count > 100
