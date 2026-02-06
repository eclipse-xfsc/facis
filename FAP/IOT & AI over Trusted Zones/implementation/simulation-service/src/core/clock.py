"""
Simulation clock with time acceleration support.

Provides deterministic time management for simulations.
"""

from __future__ import annotations

import threading
import time
from collections.abc import Callable
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from enum import Enum


class ClockState(Enum):
    """Simulation clock states."""

    STOPPED = "stopped"
    RUNNING = "running"
    PAUSED = "paused"


@dataclass
class ClockSnapshot:
    """Snapshot of the simulation clock state."""

    simulation_time: datetime
    real_time: datetime
    acceleration: int
    state: ClockState
    elapsed_simulation_seconds: float
    elapsed_real_seconds: float

    @property
    def simulation_time_iso(self) -> str:
        """Return simulation time in ISO 8601 format."""
        return self.simulation_time.isoformat()

    @property
    def real_time_iso(self) -> str:
        """Return real time in ISO 8601 format."""
        return self.real_time.isoformat()


class SimulationClock:
    """
    Manages simulation time with support for acceleration.

    Features:
    - Time acceleration (1x to 1000x)
    - Pause/resume/reset functionality
    - Thread-safe operations
    - Callbacks for time events
    """

    def __init__(
        self,
        acceleration: int = 1,
        start_time: str | None = None,
    ) -> None:
        """
        Initialize the simulation clock.

        Args:
            acceleration: Time acceleration factor (1-1000).
            start_time: Simulation start time in ISO 8601 format.
                       If None, uses current UTC time.
        """
        if not 1 <= acceleration <= 1000:
            raise ValueError("Acceleration must be between 1 and 1000")

        self._acceleration = acceleration
        self._state = ClockState.STOPPED
        self._lock = threading.RLock()

        # Parse or set start time
        if start_time is not None:
            self._start_simulation_time = datetime.fromisoformat(start_time)
            if self._start_simulation_time.tzinfo is None:
                self._start_simulation_time = self._start_simulation_time.replace(
                    tzinfo=UTC
                )
        else:
            self._start_simulation_time = datetime.now(UTC)

        # Internal timing state
        self._start_real_time: float | None = None
        self._pause_real_time: float | None = None
        self._accumulated_pause_duration: float = 0.0
        self._current_simulation_time = self._start_simulation_time

        # Callbacks
        self._tick_callbacks: list[Callable[[datetime], None]] = []

    @property
    def acceleration(self) -> int:
        """Return the time acceleration factor."""
        return self._acceleration

    @acceleration.setter
    def acceleration(self, value: int) -> None:
        """Set the time acceleration factor."""
        if not 1 <= value <= 1000:
            raise ValueError("Acceleration must be between 1 and 1000")
        with self._lock:
            # Update simulation time before changing acceleration
            if self._state == ClockState.RUNNING:
                self._update_simulation_time()
            self._acceleration = value

    @property
    def state(self) -> ClockState:
        """Return the current clock state."""
        return self._state

    @property
    def simulation_time(self) -> datetime:
        """Return the current simulation time."""
        with self._lock:
            if self._state == ClockState.RUNNING:
                self._update_simulation_time()
            return self._current_simulation_time

    @property
    def simulation_time_iso(self) -> str:
        """Return current simulation time in ISO 8601 format."""
        return self.simulation_time.isoformat()

    @property
    def simulation_time_ms(self) -> int:
        """Return current simulation time as Unix milliseconds."""
        return int(self.simulation_time.timestamp() * 1000)

    def _update_simulation_time(self) -> None:
        """Update the current simulation time based on elapsed real time."""
        if self._start_real_time is None:
            return

        current_real = time.monotonic()
        elapsed_real = (
            current_real - self._start_real_time - self._accumulated_pause_duration
        )
        elapsed_simulation = elapsed_real * self._acceleration
        self._current_simulation_time = self._start_simulation_time + timedelta(
            seconds=elapsed_simulation
        )

    def start(self) -> None:
        """Start or resume the simulation clock."""
        with self._lock:
            if self._state == ClockState.RUNNING:
                return

            if self._state == ClockState.STOPPED:
                self._start_real_time = time.monotonic()
                self._accumulated_pause_duration = 0.0
            elif self._state == ClockState.PAUSED and self._pause_real_time is not None:
                pause_duration = time.monotonic() - self._pause_real_time
                self._accumulated_pause_duration += pause_duration
                self._pause_real_time = None

            self._state = ClockState.RUNNING

    def pause(self) -> None:
        """Pause the simulation clock."""
        with self._lock:
            if self._state != ClockState.RUNNING:
                return

            self._update_simulation_time()
            self._pause_real_time = time.monotonic()
            self._state = ClockState.PAUSED

    def reset(self, start_time: str | None = None) -> None:
        """
        Reset the simulation clock to initial state.

        Args:
            start_time: New start time in ISO 8601 format.
                       If None, uses the original start time.
        """
        with self._lock:
            self._state = ClockState.STOPPED
            self._start_real_time = None
            self._pause_real_time = None
            self._accumulated_pause_duration = 0.0

            if start_time is not None:
                self._start_simulation_time = datetime.fromisoformat(start_time)
                if self._start_simulation_time.tzinfo is None:
                    self._start_simulation_time = self._start_simulation_time.replace(
                        tzinfo=UTC
                    )

            self._current_simulation_time = self._start_simulation_time

    def set_time(self, simulation_time: str) -> None:
        """
        Set the simulation time directly.

        Args:
            simulation_time: New simulation time in ISO 8601 format.
        """
        with self._lock:
            new_time = datetime.fromisoformat(simulation_time)
            if new_time.tzinfo is None:
                new_time = new_time.replace(tzinfo=UTC)

            self._current_simulation_time = new_time

            if self._state == ClockState.RUNNING:
                self._start_simulation_time = new_time
                self._start_real_time = time.monotonic()
                self._accumulated_pause_duration = 0.0

    def advance(self, seconds: float) -> datetime:
        """
        Advance simulation time by the specified duration.

        Args:
            seconds: Number of simulation seconds to advance.

        Returns:
            The new simulation time.
        """
        with self._lock:
            if self._state == ClockState.RUNNING:
                self._update_simulation_time()

            self._current_simulation_time += timedelta(seconds=seconds)

            if self._state == ClockState.RUNNING:
                self._start_simulation_time = self._current_simulation_time
                self._start_real_time = time.monotonic()
                self._accumulated_pause_duration = 0.0

            return self._current_simulation_time

    def advance_to(self, target_time: str) -> datetime:
        """
        Advance simulation time to a specific timestamp.

        Args:
            target_time: Target time in ISO 8601 format.

        Returns:
            The new simulation time.
        """
        with self._lock:
            new_time = datetime.fromisoformat(target_time)
            if new_time.tzinfo is None:
                new_time = new_time.replace(tzinfo=UTC)

            if new_time < self._current_simulation_time:
                raise ValueError("Cannot advance to a time in the past")

            self._current_simulation_time = new_time

            if self._state == ClockState.RUNNING:
                self._start_simulation_time = new_time
                self._start_real_time = time.monotonic()
                self._accumulated_pause_duration = 0.0

            return self._current_simulation_time

    def get_snapshot(self) -> ClockSnapshot:
        """Get a snapshot of the current clock state."""
        with self._lock:
            if self._state == ClockState.RUNNING:
                self._update_simulation_time()

            elapsed_sim = (
                self._current_simulation_time - self._start_simulation_time
            ).total_seconds()

            elapsed_real = 0.0
            if self._start_real_time is not None:
                if (
                    self._state == ClockState.PAUSED
                    and self._pause_real_time is not None
                ):
                    elapsed_real = (
                        self._pause_real_time
                        - self._start_real_time
                        - self._accumulated_pause_duration
                    )
                elif self._state == ClockState.RUNNING:
                    elapsed_real = (
                        time.monotonic()
                        - self._start_real_time
                        - self._accumulated_pause_duration
                    )

            return ClockSnapshot(
                simulation_time=self._current_simulation_time,
                real_time=datetime.now(UTC),
                acceleration=self._acceleration,
                state=self._state,
                elapsed_simulation_seconds=elapsed_sim,
                elapsed_real_seconds=elapsed_real,
            )

    def register_tick_callback(self, callback: Callable[[datetime], None]) -> None:
        """Register a callback to be called on each tick."""
        self._tick_callbacks.append(callback)

    def unregister_tick_callback(self, callback: Callable[[datetime], None]) -> None:
        """Unregister a tick callback."""
        if callback in self._tick_callbacks:
            self._tick_callbacks.remove(callback)

    def tick(self) -> datetime:
        """
        Manually trigger a tick and notify callbacks.

        Returns:
            The current simulation time.
        """
        current_time = self.simulation_time
        for callback in self._tick_callbacks:
            callback(current_time)
        return current_time
