"""Unit tests for the simulation clock module."""

import pytest


class TestSimulationClock:
    """Tests for SimulationClock."""

    def test_clock_not_implemented(self) -> None:
        """Test that SimulationClock raises NotImplementedError."""
        from src.core.clock import SimulationClock

        with pytest.raises(NotImplementedError):
            SimulationClock()
