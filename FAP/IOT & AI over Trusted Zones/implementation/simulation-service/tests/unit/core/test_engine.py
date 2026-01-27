"""Unit tests for the simulation engine module."""

import pytest


class TestSimulationEngine:
    """Tests for SimulationEngine."""

    def test_engine_not_implemented(self) -> None:
        """Test that SimulationEngine raises NotImplementedError."""
        from src.core.engine import SimulationEngine

        with pytest.raises(NotImplementedError):
            SimulationEngine(settings=None)
