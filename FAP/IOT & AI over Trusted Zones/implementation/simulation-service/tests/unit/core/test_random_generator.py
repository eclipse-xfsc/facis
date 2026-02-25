"""Unit tests for the random generator module."""

import pytest

from src.core.random_generator import DeterministicRNG


class TestDeterministicRNG:
    """Tests for DeterministicRNG."""

    def test_initialization_with_default_seed(self) -> None:
        """Test RNG initializes with default seed."""
        rng = DeterministicRNG()
        assert rng.seed == 12345

    def test_initialization_with_custom_seed(self) -> None:
        """Test RNG initializes with custom seed."""
        rng = DeterministicRNG(seed=42)
        assert rng.seed == 42

    def test_same_seed_produces_identical_sequence(self) -> None:
        """Test that same seed produces identical random sequence."""
        rng1 = DeterministicRNG(seed=12345)
        rng2 = DeterministicRNG(seed=12345)

        values1 = [rng1.random() for _ in range(100)]
        values2 = [rng2.random() for _ in range(100)]

        assert values1 == values2

    def test_different_seeds_produce_different_sequences(self) -> None:
        """Test that different seeds produce different sequences."""
        rng1 = DeterministicRNG(seed=12345)
        rng2 = DeterministicRNG(seed=54321)

        values1 = [rng1.random() for _ in range(10)]
        values2 = [rng2.random() for _ in range(10)]

        assert values1 != values2

    def test_reset_restores_initial_state(self) -> None:
        """Test that reset restores the RNG to its initial state."""
        rng = DeterministicRNG(seed=12345)

        # Generate some values
        initial_values = [rng.random() for _ in range(10)]

        # Generate more values
        _ = [rng.random() for _ in range(10)]

        # Reset and generate again
        rng.reset()
        reset_values = [rng.random() for _ in range(10)]

        assert initial_values == reset_values

    def test_entity_rng_produces_unique_sequences(self) -> None:
        """Test that different entities get different sequences."""
        rng = DeterministicRNG(seed=12345)

        entity1_rng = rng.get_entity_rng("entity-001")
        entity2_rng = rng.get_entity_rng("entity-002")

        values1 = [float(entity1_rng.random()) for _ in range(10)]
        values2 = [float(entity2_rng.random()) for _ in range(10)]

        assert values1 != values2

    def test_same_entity_same_seed_produces_identical_rng(self) -> None:
        """Test that same entity with same seed produces identical RNG."""
        rng1 = DeterministicRNG(seed=12345)
        rng2 = DeterministicRNG(seed=12345)

        entity1_rng = rng1.get_entity_rng("entity-001")
        entity2_rng = rng2.get_entity_rng("entity-001")

        values1 = [float(entity1_rng.random()) for _ in range(10)]
        values2 = [float(entity2_rng.random()) for _ in range(10)]

        assert values1 == values2

    def test_timestamp_rng_produces_deterministic_values(self) -> None:
        """Test that timestamp RNG produces deterministic values."""
        rng = DeterministicRNG(seed=12345)
        timestamp_ms = 1704067200000  # 2024-01-01 00:00:00 UTC

        ts_rng1 = rng.get_timestamp_rng("entity-001", timestamp_ms)
        ts_rng2 = rng.get_timestamp_rng("entity-001", timestamp_ms)

        value1 = float(ts_rng1.random())
        value2 = float(ts_rng2.random())

        assert value1 == value2

    def test_different_timestamps_produce_different_values(self) -> None:
        """Test that different timestamps produce different values."""
        rng = DeterministicRNG(seed=12345)
        ts1 = 1704067200000  # 2024-01-01 00:00:00 UTC
        ts2 = 1704070800000  # 2024-01-01 01:00:00 UTC

        ts_rng1 = rng.get_timestamp_rng("entity-001", ts1)
        ts_rng2 = rng.get_timestamp_rng("entity-001", ts2)

        value1 = float(ts_rng1.random())
        value2 = float(ts_rng2.random())

        assert value1 != value2

    def test_uniform_distribution(self) -> None:
        """Test uniform distribution method."""
        rng = DeterministicRNG(seed=12345)

        values = [rng.uniform(0.0, 100.0) for _ in range(1000)]

        assert all(0.0 <= v < 100.0 for v in values)
        assert min(values) < 10.0  # Should have values in lower range
        assert max(values) > 90.0  # Should have values in upper range

    def test_normal_distribution(self) -> None:
        """Test normal distribution method."""
        rng = DeterministicRNG(seed=12345)

        values = [rng.normal(50.0, 10.0) for _ in range(1000)]

        mean = sum(values) / len(values)
        assert 45.0 < mean < 55.0  # Mean should be close to 50

    def test_integers_distribution(self) -> None:
        """Test integer generation method."""
        rng = DeterministicRNG(seed=12345)

        values = [rng.integers(0, 100) for _ in range(1000)]

        assert all(isinstance(v, int) for v in values)
        assert all(0 <= v < 100 for v in values)

    def test_choice_method(self) -> None:
        """Test random choice method."""
        rng = DeterministicRNG(seed=12345)
        items = ["a", "b", "c", "d", "e"]

        choices = [rng.choice(items) for _ in range(100)]

        assert all(c in items for c in choices)
        # Should have variety
        assert len(set(choices)) > 1


class TestDeterminismGuarantees:
    """Tests specifically for determinism guarantees."""

    def test_cross_run_determinism(self) -> None:
        """Test that values are identical across multiple 'runs'."""
        seed = 99999
        entity_id = "test-meter-001"
        timestamp_ms = 1704067200000

        # Simulate multiple independent runs
        results = []
        for _ in range(5):
            rng = DeterministicRNG(seed=seed)
            ts_rng = rng.get_timestamp_rng(entity_id, timestamp_ms)
            results.append(float(ts_rng.random()))

        # All results should be identical
        assert all(r == results[0] for r in results)

    def test_order_independence_for_timestamp_queries(self) -> None:
        """Test that querying timestamps in different order gives same values."""
        rng = DeterministicRNG(seed=12345)
        entity_id = "entity-001"
        timestamps = [
            1704067200000,
            1704070800000,
            1704074400000,
        ]

        # Query in order
        values_ordered = []
        for ts in timestamps:
            ts_rng = rng.get_timestamp_rng(entity_id, ts)
            values_ordered.append(float(ts_rng.random()))

        # Query in reverse order (fresh RNG)
        rng2 = DeterministicRNG(seed=12345)
        values_reverse = []
        for ts in reversed(timestamps):
            ts_rng = rng2.get_timestamp_rng(entity_id, ts)
            values_reverse.append(float(ts_rng.random()))

        # Reverse the reverse to compare
        values_reverse.reverse()

        assert values_ordered == values_reverse

    def test_many_entities_unique_sequences(self) -> None:
        """Test that many entities all get unique sequences."""
        rng = DeterministicRNG(seed=12345)
        num_entities = 100

        first_values = []
        for i in range(num_entities):
            entity_rng = rng.get_entity_rng(f"entity-{i:03d}")
            first_values.append(float(entity_rng.random()))

        # All first values should be unique
        assert len(set(first_values)) == num_entities
