"""Unit tests for the random generator module."""

import pytest


class TestDeterministicRNG:
    """Tests for DeterministicRNG."""

    def test_rng_not_implemented(self) -> None:
        """Test that DeterministicRNG raises NotImplementedError."""
        from src.core.random_generator import DeterministicRNG

        with pytest.raises(NotImplementedError):
            DeterministicRNG()
