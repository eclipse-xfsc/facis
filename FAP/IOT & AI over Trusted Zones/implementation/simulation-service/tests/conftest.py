"""
Pytest configuration and fixtures.

Shared fixtures for all tests.
"""

import os
from datetime import UTC, datetime

import pytest

from src.api.rest.dependencies import SimulationState
from src.config import Settings


@pytest.fixture(scope="session")
def test_settings() -> Settings:
    """Create test settings."""
    os.environ["FACIS_ENV"] = "test"
    return Settings(
        simulation={
            "seed": 12345,
            "interval_minutes": 1,
            "speed_factor": 1.0,
        },
        mqtt={
            "host": os.environ.get("MQTT_BROKER", "localhost"),
            "port": int(os.environ.get("MQTT_PORT", "1883")),
            "client_id": "facis-test",
            "qos": 1,
        },
        meters=[
            {
                "id": "test-meter-001",
                "base_load_kw": 10.0,
                "peak_load_kw": 25.0,
            }
        ],
        pv_systems=[
            {
                "id": "test-pv-001",
                "nominal_capacity_kw": 10.0,
            }
        ],
        consumers=[
            {
                "id": "test-oven-001",
                "rated_power_kw": 3.5,
                "device_type": "industrial_oven",
            }
        ],
    )


@pytest.fixture
def simulation_state(test_settings: Settings) -> SimulationState:
    """Create and initialize simulation state for testing."""
    # Reset singleton for isolation
    SimulationState.reset_instance()

    state = SimulationState.get_instance()
    state.initialize(test_settings)
    return state


@pytest.fixture
def sample_timestamp() -> datetime:
    """Return a sample timestamp for testing."""
    return datetime(2024, 6, 15, 12, 0, 0, tzinfo=UTC)
