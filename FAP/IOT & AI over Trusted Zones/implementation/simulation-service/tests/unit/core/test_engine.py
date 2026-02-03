"""Unit tests for the simulation engine module."""

from datetime import datetime, timezone

import pytest

from src.core.engine import EngineState, SimulationEngine
from src.core.random_generator import DeterministicRNG
from src.core.time_series import (
    BaseTimeSeriesGenerator,
    IntervalMinutes,
)


class MockGenerator(BaseTimeSeriesGenerator[float]):
    """Mock generator for testing."""

    def __init__(
        self,
        entity_id: str,
        rng: DeterministicRNG,
        interval: IntervalMinutes = IntervalMinutes.FIFTEEN_MINUTES,
        base_value: float = 100.0,
    ) -> None:
        super().__init__(entity_id, rng, interval)
        self._base_value = base_value

    def generate_value(self, timestamp: datetime) -> float:
        """Generate a deterministic value."""
        return self.get_deterministic_value(timestamp, self._base_value, 10.0)


class TestSimulationEngine:
    """Tests for SimulationEngine."""

    def test_initialization_with_defaults(self) -> None:
        """Test engine initializes with default values."""
        engine = SimulationEngine()

        assert engine.seed == 12345
        assert engine.state == EngineState.INITIALIZED
        assert engine.clock.acceleration == 1

    def test_initialization_with_settings(self) -> None:
        """Test engine initializes with custom settings."""
        from src.config import Settings, SimulationConfig

        settings = Settings(
            simulation=SimulationConfig(
                seed=99999,
                speed_factor=10.0,
                start_time="2024-01-01T00:00:00+00:00",
            )
        )

        engine = SimulationEngine(settings=settings)

        assert engine.seed == 99999
        assert engine.clock.acceleration == 10

    def test_start_changes_state(self) -> None:
        """Test that start() changes state to RUNNING."""
        engine = SimulationEngine()
        engine.start()
        assert engine.state == EngineState.RUNNING

    def test_pause_changes_state(self) -> None:
        """Test that pause() changes state to PAUSED."""
        engine = SimulationEngine()
        engine.start()
        engine.pause()
        assert engine.state == EngineState.PAUSED

    def test_resume_changes_state(self) -> None:
        """Test that resume() changes state back to RUNNING."""
        engine = SimulationEngine()
        engine.start()
        engine.pause()
        engine.resume()
        assert engine.state == EngineState.RUNNING

    def test_stop_changes_state(self) -> None:
        """Test that stop() changes state to STOPPED."""
        engine = SimulationEngine()
        engine.start()
        engine.stop()
        assert engine.state == EngineState.STOPPED

    def test_reset_returns_to_initialized(self) -> None:
        """Test that reset() returns to INITIALIZED state."""
        engine = SimulationEngine()
        engine.start()
        engine.reset()
        assert engine.state == EngineState.INITIALIZED

    def test_reset_with_new_seed(self) -> None:
        """Test reset with a new seed value."""
        engine = SimulationEngine()
        original_seed = engine.seed

        engine.reset(new_seed=54321)

        assert engine.seed == 54321
        assert engine.seed != original_seed


class TestGeneratorManagement:
    """Tests for generator registration and management."""

    def test_register_generator_type(self) -> None:
        """Test registering a generator type."""
        engine = SimulationEngine()
        engine.register_generator_type("mock", MockGenerator)

        # Should be able to create generators of this type
        generator = engine.create_generator("entity-001", "mock")
        assert generator is not None

    def test_create_generator(self) -> None:
        """Test creating a generator for an entity."""
        engine = SimulationEngine()
        engine.register_generator_type("mock", MockGenerator)

        generator = engine.create_generator(
            entity_id="meter-001",
            generator_type="mock",
            interval=IntervalMinutes.FIFTEEN_MINUTES,
            base_value=200.0,
        )

        assert generator.entity_id == "meter-001"
        assert generator.interval == IntervalMinutes.FIFTEEN_MINUTES

    def test_create_generator_unknown_type_raises_error(self) -> None:
        """Test that creating unknown generator type raises error."""
        engine = SimulationEngine()

        with pytest.raises(ValueError, match="Unknown generator type"):
            engine.create_generator("entity-001", "unknown_type")

    def test_get_generator(self) -> None:
        """Test getting a registered generator."""
        engine = SimulationEngine()
        engine.register_generator_type("mock", MockGenerator)
        engine.create_generator("entity-001", "mock")

        generator = engine.get_generator("entity-001")
        assert generator is not None
        assert generator.entity_id == "entity-001"

    def test_get_generator_not_found(self) -> None:
        """Test getting a non-existent generator returns None."""
        engine = SimulationEngine()
        generator = engine.get_generator("nonexistent")
        assert generator is None

    def test_remove_generator(self) -> None:
        """Test removing a generator."""
        engine = SimulationEngine()
        engine.register_generator_type("mock", MockGenerator)
        engine.create_generator("entity-001", "mock")

        result = engine.remove_generator("entity-001")
        assert result is True
        assert engine.get_generator("entity-001") is None

    def test_remove_nonexistent_generator(self) -> None:
        """Test removing a non-existent generator returns False."""
        engine = SimulationEngine()
        result = engine.remove_generator("nonexistent")
        assert result is False

    def test_list_entities(self) -> None:
        """Test listing registered entities."""
        engine = SimulationEngine()
        engine.register_generator_type("mock", MockGenerator)
        engine.create_generator("entity-001", "mock")
        engine.create_generator("entity-002", "mock")
        engine.create_generator("entity-003", "mock")

        entities = engine.list_entities()

        assert len(entities) == 3
        assert "entity-001" in entities
        assert "entity-002" in entities
        assert "entity-003" in entities


class TestDataGeneration:
    """Tests for data generation methods."""

    def test_generate_current(self) -> None:
        """Test generating data at current simulation time."""
        engine = SimulationEngine()
        engine.register_generator_type("mock", MockGenerator)
        engine.create_generator("meter-001", "mock")

        point = engine.generate_current("meter-001")

        assert point is not None
        assert isinstance(point.value, float)

    def test_generate_current_unknown_entity(self) -> None:
        """Test generating data for unknown entity returns None."""
        engine = SimulationEngine()
        point = engine.generate_current("unknown")
        assert point is None

    def test_generate_at_specific_time(self) -> None:
        """Test generating data at a specific timestamp."""
        engine = SimulationEngine()
        engine.register_generator_type("mock", MockGenerator)
        engine.create_generator("meter-001", "mock")

        point = engine.generate_at("meter-001", "2024-01-01T12:00:00+00:00")

        assert point is not None
        assert point.timestamp.hour == 12

    def test_generate_range(self) -> None:
        """Test generating data over a time range."""
        engine = SimulationEngine()
        engine.register_generator_type("mock", MockGenerator)
        engine.create_generator("meter-001", "mock")

        points = engine.generate_range(
            "meter-001",
            "2024-01-01T00:00:00+00:00",
            "2024-01-01T01:00:00+00:00",
        )

        assert len(points) == 5  # 00:00, 00:15, 00:30, 00:45, 01:00

    def test_generate_range_unknown_entity(self) -> None:
        """Test generating range for unknown entity returns empty list."""
        engine = SimulationEngine()
        points = engine.generate_range(
            "unknown",
            "2024-01-01T00:00:00+00:00",
            "2024-01-01T01:00:00+00:00",
        )
        assert points == []

    def test_generate_all_current(self) -> None:
        """Test generating data for all entities."""
        engine = SimulationEngine()
        engine.register_generator_type("mock", MockGenerator)
        engine.create_generator("meter-001", "mock")
        engine.create_generator("meter-002", "mock")
        engine.create_generator("pv-001", "mock")

        results = engine.generate_all_current()

        assert len(results) == 3
        assert "meter-001" in results
        assert "meter-002" in results
        assert "pv-001" in results


class TestEngineDeterminism:
    """Tests for determinism guarantees in the engine."""

    def test_same_seed_produces_identical_data(self) -> None:
        """Test that same seed produces identical data across runs."""
        entity_id = "meter-001"
        timestamp = "2024-01-01T12:00:00+00:00"

        results = []
        for _ in range(5):
            engine = SimulationEngine()
            engine.register_generator_type("mock", MockGenerator)
            engine.create_generator(entity_id, "mock")

            point = engine.generate_at(entity_id, timestamp)
            results.append(point.value)

        # All results should be identical
        assert all(r == results[0] for r in results)

    def test_different_seeds_produce_different_data(self) -> None:
        """Test that different seeds produce different data."""
        from src.config import Settings, SimulationConfig

        entity_id = "meter-001"
        timestamp = "2024-01-01T12:00:00+00:00"

        settings1 = Settings(simulation=SimulationConfig(seed=11111))
        settings2 = Settings(simulation=SimulationConfig(seed=22222))

        engine1 = SimulationEngine(settings=settings1)
        engine1.register_generator_type("mock", MockGenerator)
        engine1.create_generator(entity_id, "mock")

        engine2 = SimulationEngine(settings=settings2)
        engine2.register_generator_type("mock", MockGenerator)
        engine2.create_generator(entity_id, "mock")

        point1 = engine1.generate_at(entity_id, timestamp)
        point2 = engine2.generate_at(entity_id, timestamp)

        assert point1.value != point2.value

    def test_different_entities_produce_different_data(self) -> None:
        """Test that different entities produce different data."""
        engine = SimulationEngine()
        engine.register_generator_type("mock", MockGenerator)
        engine.create_generator("meter-001", "mock")
        engine.create_generator("meter-002", "mock")

        timestamp = "2024-01-01T12:00:00+00:00"
        point1 = engine.generate_at("meter-001", timestamp)
        point2 = engine.generate_at("meter-002", timestamp)

        assert point1.value != point2.value


class TestEngineSnapshot:
    """Tests for engine snapshot functionality."""

    def test_get_snapshot(self) -> None:
        """Test getting an engine snapshot."""
        engine = SimulationEngine()
        engine.register_generator_type("mock", MockGenerator)
        engine.create_generator("meter-001", "mock")
        engine.create_generator("meter-002", "mock")

        engine.start()
        snapshot = engine.get_snapshot()

        assert snapshot.state == EngineState.RUNNING
        assert snapshot.seed == 12345
        assert snapshot.acceleration == 1
        assert snapshot.active_entities == 2
        assert len(snapshot.registered_generators) == 2


class TestTimeAdvancement:
    """Tests for time advancement methods."""

    def test_advance_by_seconds(self) -> None:
        """Test advancing simulation time by seconds."""
        from src.config import Settings, SimulationConfig

        settings = Settings(simulation=SimulationConfig(start_time="2024-01-01T00:00:00+00:00"))
        engine = SimulationEngine(settings=settings)

        new_time = engine.advance(3600)  # 1 hour

        assert new_time.hour == 1

    def test_advance_to_specific_time(self) -> None:
        """Test advancing to a specific time."""
        from src.config import Settings, SimulationConfig

        settings = Settings(simulation=SimulationConfig(start_time="2024-01-01T00:00:00+00:00"))
        engine = SimulationEngine(settings=settings)

        new_time = engine.advance_to("2024-01-01T12:00:00+00:00")

        assert new_time.hour == 12


class TestIntervalSupport:
    """Tests for interval configuration."""

    def test_15_minute_interval(self) -> None:
        """Test 15-minute interval alignment."""
        engine = SimulationEngine()
        engine.register_generator_type("mock", MockGenerator)
        engine.create_generator(
            "meter-001",
            "mock",
            interval=IntervalMinutes.FIFTEEN_MINUTES,
        )

        points = engine.generate_range(
            "meter-001",
            "2024-01-01T00:00:00+00:00",
            "2024-01-01T01:00:00+00:00",
        )

        # Check timestamps are aligned to 15-minute boundaries
        for point in points:
            assert point.timestamp.minute % 15 == 0
            assert point.timestamp.second == 0

    def test_1_hour_interval(self) -> None:
        """Test 1-hour interval alignment."""
        engine = SimulationEngine()
        engine.register_generator_type("mock", MockGenerator)
        engine.create_generator(
            "meter-001",
            "mock",
            interval=IntervalMinutes.ONE_HOUR,
        )

        points = engine.generate_range(
            "meter-001",
            "2024-01-01T00:00:00+00:00",
            "2024-01-01T03:00:00+00:00",
        )

        # Should have 4 points: 00:00, 01:00, 02:00, 03:00
        assert len(points) == 4

        # Check timestamps are aligned to hour boundaries
        for point in points:
            assert point.timestamp.minute == 0
            assert point.timestamp.second == 0
