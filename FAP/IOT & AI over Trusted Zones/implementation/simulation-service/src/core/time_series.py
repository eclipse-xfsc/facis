"""
Base time-series generator class.

Provides foundation for all time-series based simulators.
Supports deterministic, reproducible data generation for demos, testing, and evaluation.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from enum import Enum
from typing import TYPE_CHECKING, Generic, TypeVar

from src.core.random_generator import DeterministicRNG

if TYPE_CHECKING:
    from collections.abc import Iterator

T = TypeVar("T")


class IntervalMinutes(Enum):
    """Supported time intervals for data generation."""

    FIFTEEN_MINUTES = 15
    ONE_HOUR = 60


@dataclass(frozen=True)
class TimeSeriesPoint(Generic[T]):
    """A single point in a time series."""

    timestamp: datetime
    value: T

    @property
    def timestamp_iso(self) -> str:
        """Return timestamp in ISO 8601 format."""
        return self.timestamp.isoformat()

    @property
    def timestamp_ms(self) -> int:
        """Return timestamp as Unix milliseconds."""
        return int(self.timestamp.timestamp() * 1000)


@dataclass
class TimeRange:
    """Represents a time range for batch generation."""

    start: datetime
    end: datetime

    def __post_init__(self) -> None:
        """Validate the time range."""
        if self.start >= self.end:
            raise ValueError("Start time must be before end time")

    @classmethod
    def from_iso(cls, start_iso: str, end_iso: str) -> TimeRange:
        """Create a TimeRange from ISO 8601 strings."""
        start = datetime.fromisoformat(start_iso)
        end = datetime.fromisoformat(end_iso)
        if start.tzinfo is None:
            start = start.replace(tzinfo=UTC)
        if end.tzinfo is None:
            end = end.replace(tzinfo=UTC)
        return cls(start=start, end=end)

    def count_intervals(self, interval: IntervalMinutes) -> int:
        """Count the number of intervals in this range."""
        delta = self.end - self.start
        total_minutes = delta.total_seconds() / 60
        return int(total_minutes // interval.value)


class BaseTimeSeriesGenerator(ABC, Generic[T]):
    """
    Abstract base class for time-series generators.

    Provides deterministic, reproducible data generation based on:
    - Seed value (same seed = identical sequences)
    - Entity ID (different entities = different sequences)
    - Timestamp alignment to configured intervals

    Subclasses must implement the `generate_value` method.
    """

    def __init__(
        self,
        entity_id: str,
        rng: DeterministicRNG,
        interval: IntervalMinutes = IntervalMinutes.FIFTEEN_MINUTES,
    ) -> None:
        """
        Initialize the time-series generator.

        Args:
            entity_id: Unique identifier for the entity being simulated.
            rng: Deterministic random number generator.
            interval: Time interval for data generation (15 min or 1 hour).
        """
        self._entity_id = entity_id
        self._rng = rng
        self._interval = interval

    @property
    def entity_id(self) -> str:
        """Return the entity ID."""
        return self._entity_id

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

    @abstractmethod
    def generate_value(self, timestamp: datetime) -> T:
        """
        Generate a value for the given timestamp.

        This method must be implemented by subclasses to provide
        domain-specific value generation logic.

        Args:
            timestamp: The timestamp for which to generate a value.

        Returns:
            The generated value.
        """
        pass

    def generate_at(self, timestamp: datetime) -> TimeSeriesPoint[T]:
        """
        Generate a time-series point at the given timestamp.

        The timestamp is aligned to the configured interval boundary.
        Same seed + entity + timestamp always produces identical values.

        Args:
            timestamp: The timestamp for which to generate data.

        Returns:
            A TimeSeriesPoint containing the aligned timestamp and value.
        """
        aligned_ts = self.align_timestamp(timestamp)
        value = self.generate_value(aligned_ts)
        return TimeSeriesPoint(timestamp=aligned_ts, value=value)

    def generate_range(self, time_range: TimeRange) -> list[TimeSeriesPoint[T]]:
        """
        Generate time-series data for a historical range.

        Args:
            time_range: The time range for which to generate data.

        Returns:
            A list of TimeSeriesPoints covering the range.
        """
        return list(self.iterate_range(time_range))

    def iterate_range(self, time_range: TimeRange) -> Iterator[TimeSeriesPoint[T]]:
        """
        Iterate over time-series data for a historical range.

        More memory-efficient than generate_range for large ranges.

        Args:
            time_range: The time range for which to generate data.

        Yields:
            TimeSeriesPoints covering the range.
        """
        current = self.align_timestamp(time_range.start)
        end = self.align_timestamp(time_range.end)
        interval_delta = timedelta(minutes=self._interval.value)

        while current <= end:
            value = self.generate_value(current)
            yield TimeSeriesPoint(timestamp=current, value=value)
            current += interval_delta

    def generate_batch(self, start: datetime, count: int) -> list[TimeSeriesPoint[T]]:
        """
        Generate a batch of consecutive time-series points.

        Args:
            start: The starting timestamp (will be aligned).
            count: Number of points to generate.

        Returns:
            A list of consecutive TimeSeriesPoints.
        """
        current = self.align_timestamp(start)
        interval_delta = timedelta(minutes=self._interval.value)
        points = []

        for _ in range(count):
            value = self.generate_value(current)
            points.append(TimeSeriesPoint(timestamp=current, value=value))
            current += interval_delta

        return points

    def get_deterministic_value(
        self, timestamp: datetime, base_value: float, variance: float
    ) -> float:
        """
        Get a deterministic random value for a timestamp.

        Helper method for subclasses to generate reproducible values.

        Args:
            timestamp: The timestamp for the value.
            base_value: The base/mean value.
            variance: The variance to apply.

        Returns:
            A deterministic value based on seed + entity + timestamp.
        """
        aligned_ts = self.align_timestamp(timestamp)
        ts_ms = int(aligned_ts.timestamp() * 1000)
        rng = self._rng.get_timestamp_rng(self._entity_id, ts_ms)
        return base_value + float(rng.normal(0, variance))

    def get_deterministic_uniform(
        self, timestamp: datetime, low: float, high: float
    ) -> float:
        """
        Get a deterministic uniform random value for a timestamp.

        Args:
            timestamp: The timestamp for the value.
            low: Lower bound (inclusive).
            high: Upper bound (exclusive).

        Returns:
            A deterministic uniform value based on seed + entity + timestamp.
        """
        aligned_ts = self.align_timestamp(timestamp)
        ts_ms = int(aligned_ts.timestamp() * 1000)
        rng = self._rng.get_timestamp_rng(self._entity_id, ts_ms)
        return float(rng.uniform(low, high))
