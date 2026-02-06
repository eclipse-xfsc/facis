"""
Main simulation orchestrator.

Coordinates all simulators and manages simulation lifecycle.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import TYPE_CHECKING, Any

from src.core.clock import SimulationClock
from src.core.random_generator import DeterministicRNG
from src.core.time_series import (
    BaseTimeSeriesGenerator,
    IntervalMinutes,
    TimeRange,
    TimeSeriesPoint,
)

if TYPE_CHECKING:
    from src.config import Settings

logger = logging.getLogger(__name__)


class EngineState(Enum):
    """Simulation engine states."""

    INITIALIZED = "initialized"
    RUNNING = "running"
    PAUSED = "paused"
    STOPPED = "stopped"


@dataclass
class GeneratorConfig:
    """Configuration for a time-series generator."""

    entity_id: str
    generator_type: str
    interval: IntervalMinutes = IntervalMinutes.FIFTEEN_MINUTES
    parameters: dict[str, Any] = field(default_factory=dict)


@dataclass
class EngineSnapshot:
    """Snapshot of the simulation engine state."""

    state: EngineState
    simulation_time: datetime
    simulation_time_iso: str
    seed: int
    acceleration: int
    registered_generators: list[str]
    active_entities: int


class SimulationEngine:
    """
    Core simulation engine that orchestrates all simulators.

    Provides:
    - Deterministic, reproducible data generation
    - Support for 15-minute and 1-hour intervals
    - Batch generation for historical ranges
    - Multiple entity support with unique sequences
    - Pause/resume/reset functionality
    """

    def __init__(self, settings: Settings | None = None) -> None:
        """
        Initialize the simulation engine.

        Args:
            settings: Configuration settings. If None, uses defaults.
        """
        # Extract configuration
        if settings is not None:
            seed = settings.simulation.seed
            # speed_factor is a float (e.g., 10.0 for 10x), convert to int for clock
            acceleration = int(settings.simulation.speed_factor)
            start_time = settings.simulation.start_time
        else:
            seed = 12345
            acceleration = 1
            start_time = None

        self._seed = seed
        self._rng = DeterministicRNG(seed)
        self._clock = SimulationClock(acceleration=acceleration, start_time=start_time)
        self._state = EngineState.INITIALIZED

        # Generator registry: entity_id -> generator
        self._generators: dict[str, BaseTimeSeriesGenerator] = {}

        # Generator factories: type_name -> factory function
        self._generator_factories: dict[str, type[BaseTimeSeriesGenerator]] = {}

        logger.info(f"SimulationEngine initialized with seed={seed}, acceleration={acceleration}")

    @property
    def seed(self) -> int:
        """Return the simulation seed."""
        return self._seed

    @property
    def rng(self) -> DeterministicRNG:
        """Return the deterministic RNG."""
        return self._rng

    @property
    def clock(self) -> SimulationClock:
        """Return the simulation clock."""
        return self._clock

    @property
    def state(self) -> EngineState:
        """Return the current engine state."""
        return self._state

    @property
    def simulation_time(self) -> datetime:
        """Return the current simulation time."""
        return self._clock.simulation_time

    @property
    def simulation_time_iso(self) -> str:
        """Return simulation time in ISO 8601 format."""
        return self._clock.simulation_time_iso

    def register_generator_type(
        self, type_name: str, factory: type[BaseTimeSeriesGenerator]
    ) -> None:
        """
        Register a generator factory for a given type.

        Args:
            type_name: Name of the generator type.
            factory: Generator class to instantiate.
        """
        self._generator_factories[type_name] = factory
        logger.debug(f"Registered generator type: {type_name}")

    def create_generator(
        self,
        entity_id: str,
        generator_type: str,
        interval: IntervalMinutes = IntervalMinutes.FIFTEEN_MINUTES,
        **kwargs: Any,
    ) -> BaseTimeSeriesGenerator:
        """
        Create and register a generator for an entity.

        Args:
            entity_id: Unique identifier for the entity.
            generator_type: Type of generator to create.
            interval: Time interval for data generation.
            **kwargs: Additional parameters for the generator.

        Returns:
            The created generator.

        Raises:
            ValueError: If generator type is not registered.
        """
        if generator_type not in self._generator_factories:
            raise ValueError(f"Unknown generator type: {generator_type}")

        factory = self._generator_factories[generator_type]
        generator = factory(
            entity_id=entity_id,
            rng=self._rng,
            interval=interval,
            **kwargs,
        )
        self._generators[entity_id] = generator
        logger.debug(f"Created generator for entity: {entity_id}")
        return generator

    def get_generator(self, entity_id: str) -> BaseTimeSeriesGenerator | None:
        """Get a registered generator by entity ID."""
        return self._generators.get(entity_id)

    def remove_generator(self, entity_id: str) -> bool:
        """Remove a generator by entity ID."""
        if entity_id in self._generators:
            del self._generators[entity_id]
            logger.debug(f"Removed generator for entity: {entity_id}")
            return True
        return False

    def list_entities(self) -> list[str]:
        """Return list of registered entity IDs."""
        return list(self._generators.keys())

    def start(self) -> None:
        """Start the simulation."""
        if self._state == EngineState.RUNNING:
            logger.warning("Simulation already running")
            return

        self._clock.start()
        self._state = EngineState.RUNNING
        logger.info("Simulation started")

    def pause(self) -> None:
        """Pause the simulation."""
        if self._state != EngineState.RUNNING:
            logger.warning("Simulation not running")
            return

        self._clock.pause()
        self._state = EngineState.PAUSED
        logger.info("Simulation paused")

    def resume(self) -> None:
        """Resume a paused simulation."""
        if self._state != EngineState.PAUSED:
            logger.warning("Simulation not paused")
            return

        self._clock.start()
        self._state = EngineState.RUNNING
        logger.info("Simulation resumed")

    def stop(self) -> None:
        """Stop the simulation."""
        self._clock.pause()
        self._state = EngineState.STOPPED
        logger.info("Simulation stopped")

    def reset(self, start_time: str | None = None, new_seed: int | None = None) -> None:
        """
        Reset the simulation to initial state.

        Args:
            start_time: New start time in ISO 8601 format.
            new_seed: New seed value (if None, keeps current seed).
        """
        self._clock.reset(start_time)
        self._state = EngineState.INITIALIZED

        if new_seed is not None:
            self._seed = new_seed
            self._rng = DeterministicRNG(new_seed)

            # Recreate generators with new RNG
            for entity_id, generator in self._generators.items():
                generator._rng = self._rng

        logger.info(f"Simulation reset (seed={self._seed})")

    def generate_current(self, entity_id: str) -> TimeSeriesPoint | None:
        """
        Generate data for an entity at the current simulation time.

        Args:
            entity_id: The entity to generate data for.

        Returns:
            The generated time-series point, or None if entity not found.
        """
        generator = self._generators.get(entity_id)
        if generator is None:
            logger.warning(f"Generator not found for entity: {entity_id}")
            return None

        return generator.generate_at(self._clock.simulation_time)

    def generate_at(self, entity_id: str, timestamp: datetime | str) -> TimeSeriesPoint | None:
        """
        Generate data for an entity at a specific timestamp.

        Args:
            entity_id: The entity to generate data for.
            timestamp: The timestamp (datetime or ISO 8601 string).

        Returns:
            The generated time-series point, or None if entity not found.
        """
        generator = self._generators.get(entity_id)
        if generator is None:
            logger.warning(f"Generator not found for entity: {entity_id}")
            return None

        if isinstance(timestamp, str):
            timestamp = datetime.fromisoformat(timestamp)
            if timestamp.tzinfo is None:
                timestamp = timestamp.replace(tzinfo=UTC)

        return generator.generate_at(timestamp)

    def generate_range(
        self,
        entity_id: str,
        start: datetime | str,
        end: datetime | str,
    ) -> list[TimeSeriesPoint]:
        """
        Generate batch data for an entity over a time range.

        Args:
            entity_id: The entity to generate data for.
            start: Range start (datetime or ISO 8601 string).
            end: Range end (datetime or ISO 8601 string).

        Returns:
            List of time-series points covering the range.
        """
        generator = self._generators.get(entity_id)
        if generator is None:
            logger.warning(f"Generator not found for entity: {entity_id}")
            return []

        if isinstance(start, str):
            start = datetime.fromisoformat(start)
            if start.tzinfo is None:
                start = start.replace(tzinfo=UTC)

        if isinstance(end, str):
            end = datetime.fromisoformat(end)
            if end.tzinfo is None:
                end = end.replace(tzinfo=UTC)

        time_range = TimeRange(start=start, end=end)
        return generator.generate_range(time_range)

    def generate_all_current(self) -> dict[str, TimeSeriesPoint]:
        """
        Generate data for all entities at the current simulation time.

        Returns:
            Dictionary mapping entity IDs to their generated points.
        """
        results = {}
        current_time = self._clock.simulation_time

        for entity_id, generator in self._generators.items():
            results[entity_id] = generator.generate_at(current_time)

        return results

    def get_snapshot(self) -> EngineSnapshot:
        """Get a snapshot of the current engine state."""
        return EngineSnapshot(
            state=self._state,
            simulation_time=self._clock.simulation_time,
            simulation_time_iso=self._clock.simulation_time_iso,
            seed=self._seed,
            acceleration=self._clock.acceleration,
            registered_generators=list(self._generators.keys()),
            active_entities=len(self._generators),
        )

    def advance(self, seconds: float) -> datetime:
        """
        Advance simulation time by the specified duration.

        Args:
            seconds: Number of simulation seconds to advance.

        Returns:
            The new simulation time.
        """
        return self._clock.advance(seconds)

    def advance_to(self, target_time: str) -> datetime:
        """
        Advance simulation time to a specific timestamp.

        Args:
            target_time: Target time in ISO 8601 format.

        Returns:
            The new simulation time.
        """
        return self._clock.advance_to(target_time)
