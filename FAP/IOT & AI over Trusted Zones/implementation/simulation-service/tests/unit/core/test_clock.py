"""Unit tests for the simulation clock module."""

import time
from datetime import datetime, timezone

import pytest

from src.core.clock import ClockState, SimulationClock


class TestSimulationClock:
    """Tests for SimulationClock."""

    def test_initialization_with_defaults(self) -> None:
        """Test clock initializes with default values."""
        clock = SimulationClock()
        assert clock.acceleration == 1
        assert clock.state == ClockState.STOPPED

    def test_initialization_with_custom_acceleration(self) -> None:
        """Test clock initializes with custom acceleration."""
        clock = SimulationClock(acceleration=10)
        assert clock.acceleration == 10

    def test_initialization_with_start_time(self) -> None:
        """Test clock initializes with custom start time."""
        start_time = "2024-01-01T00:00:00+00:00"
        clock = SimulationClock(start_time=start_time)
        assert clock.simulation_time_iso.startswith("2024-01-01T00:00:00")

    def test_invalid_acceleration_too_low(self) -> None:
        """Test that acceleration below 1 raises error."""
        with pytest.raises(ValueError, match="Acceleration must be between 1 and 1000"):
            SimulationClock(acceleration=0)

    def test_invalid_acceleration_too_high(self) -> None:
        """Test that acceleration above 1000 raises error."""
        with pytest.raises(ValueError, match="Acceleration must be between 1 and 1000"):
            SimulationClock(acceleration=1001)

    def test_start_changes_state_to_running(self) -> None:
        """Test that start() changes state to RUNNING."""
        clock = SimulationClock()
        assert clock.state == ClockState.STOPPED

        clock.start()
        assert clock.state == ClockState.RUNNING

    def test_pause_changes_state_to_paused(self) -> None:
        """Test that pause() changes state to PAUSED."""
        clock = SimulationClock()
        clock.start()
        clock.pause()
        assert clock.state == ClockState.PAUSED

    def test_pause_does_nothing_when_not_running(self) -> None:
        """Test that pause() does nothing when not running."""
        clock = SimulationClock()
        clock.pause()
        assert clock.state == ClockState.STOPPED

    def test_reset_returns_to_stopped(self) -> None:
        """Test that reset() returns to STOPPED state."""
        clock = SimulationClock(start_time="2024-01-01T00:00:00+00:00")
        clock.start()
        clock.reset()
        assert clock.state == ClockState.STOPPED
        assert clock.simulation_time_iso.startswith("2024-01-01T00:00:00")

    def test_reset_with_new_start_time(self) -> None:
        """Test reset with a new start time."""
        clock = SimulationClock(start_time="2024-01-01T00:00:00+00:00")
        clock.start()
        clock.reset(start_time="2024-06-15T12:00:00+00:00")
        assert clock.simulation_time_iso.startswith("2024-06-15T12:00:00")

    def test_acceleration_property_setter(self) -> None:
        """Test that acceleration can be changed."""
        clock = SimulationClock(acceleration=1)
        clock.acceleration = 100
        assert clock.acceleration == 100

    def test_acceleration_setter_validates_range(self) -> None:
        """Test that acceleration setter validates range."""
        clock = SimulationClock()
        with pytest.raises(ValueError):
            clock.acceleration = 0
        with pytest.raises(ValueError):
            clock.acceleration = 1001

    def test_set_time_directly(self) -> None:
        """Test setting simulation time directly."""
        clock = SimulationClock()
        clock.set_time("2024-06-15T12:00:00+00:00")
        assert clock.simulation_time_iso.startswith("2024-06-15T12:00:00")

    def test_advance_by_seconds(self) -> None:
        """Test advancing time by seconds."""
        clock = SimulationClock(start_time="2024-01-01T00:00:00+00:00")
        new_time = clock.advance(3600)  # 1 hour
        assert new_time.hour == 1
        assert clock.simulation_time.hour == 1

    def test_advance_to_specific_time(self) -> None:
        """Test advancing to a specific time."""
        clock = SimulationClock(start_time="2024-01-01T00:00:00+00:00")
        new_time = clock.advance_to("2024-01-01T12:00:00+00:00")
        assert new_time.hour == 12

    def test_advance_to_past_raises_error(self) -> None:
        """Test that advancing to the past raises an error."""
        clock = SimulationClock(start_time="2024-01-01T12:00:00+00:00")
        with pytest.raises(ValueError, match="Cannot advance to a time in the past"):
            clock.advance_to("2024-01-01T00:00:00+00:00")

    def test_simulation_time_ms(self) -> None:
        """Test simulation_time_ms property."""
        clock = SimulationClock(start_time="2024-01-01T00:00:00+00:00")
        expected_ms = 1704067200000
        assert clock.simulation_time_ms == expected_ms

    def test_get_snapshot(self) -> None:
        """Test getting a clock snapshot."""
        clock = SimulationClock(acceleration=10, start_time="2024-01-01T00:00:00+00:00")
        clock.start()

        snapshot = clock.get_snapshot()

        assert snapshot.acceleration == 10
        assert snapshot.state == ClockState.RUNNING
        assert snapshot.simulation_time_iso.startswith("2024-01-01")


class TestClockAcceleration:
    """Tests for time acceleration behavior."""

    def test_accelerated_time_advances_faster(self) -> None:
        """Test that accelerated time advances faster than real time."""
        clock = SimulationClock(acceleration=100, start_time="2024-01-01T00:00:00+00:00")
        initial_time = clock.simulation_time

        clock.start()
        time.sleep(0.1)  # Wait 100ms of real time
        clock.pause()

        elapsed = (clock.simulation_time - initial_time).total_seconds()

        # With 100x acceleration, 0.1s real time should be ~10s simulation time
        # Allow some tolerance for timing variations
        assert elapsed >= 5.0  # At least 5 seconds
        assert elapsed <= 20.0  # At most 20 seconds


class TestClockCallbacks:
    """Tests for tick callbacks."""

    def test_register_tick_callback(self) -> None:
        """Test registering a tick callback."""
        clock = SimulationClock()
        callback_times: list[datetime] = []

        def callback(sim_time: datetime) -> None:
            callback_times.append(sim_time)

        clock.register_tick_callback(callback)
        clock.tick()

        assert len(callback_times) == 1

    def test_unregister_tick_callback(self) -> None:
        """Test unregistering a tick callback."""
        clock = SimulationClock()
        callback_times: list[datetime] = []

        def callback(sim_time: datetime) -> None:
            callback_times.append(sim_time)

        clock.register_tick_callback(callback)
        clock.unregister_tick_callback(callback)
        clock.tick()

        assert len(callback_times) == 0

    def test_tick_returns_simulation_time(self) -> None:
        """Test that tick() returns the current simulation time."""
        clock = SimulationClock(start_time="2024-01-01T00:00:00+00:00")
        tick_time = clock.tick()
        assert tick_time == clock.simulation_time


class TestClockPauseResume:
    """Tests for pause/resume behavior."""

    def test_pause_preserves_simulation_time(self) -> None:
        """Test that pausing preserves the simulation time."""
        clock = SimulationClock(acceleration=10, start_time="2024-01-01T00:00:00+00:00")

        clock.start()
        time.sleep(0.05)
        clock.pause()

        paused_time = clock.simulation_time

        # Wait a bit while paused
        time.sleep(0.05)

        # Time should not have changed
        assert clock.simulation_time == paused_time

    def test_resume_continues_from_paused_time(self) -> None:
        """Test that resuming continues from the paused time."""
        clock = SimulationClock(acceleration=100, start_time="2024-01-01T00:00:00+00:00")

        clock.start()
        time.sleep(0.05)
        clock.pause()
        paused_time = clock.simulation_time

        time.sleep(0.05)  # Wait while paused
        clock.start()  # Resume
        time.sleep(0.05)
        clock.pause()

        # Time should have advanced from paused_time
        assert clock.simulation_time > paused_time
