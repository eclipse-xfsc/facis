"""
Integration test fixtures using testcontainers.

Provides MQTT broker and simulator containers for integration testing.
"""

import asyncio
import json
import os
import time
from collections.abc import Generator
from datetime import UTC, datetime
from typing import Any

import paho.mqtt.client as mqtt
import pytest
from httpx import ASGITransport, AsyncClient
from testcontainers.core.container import DockerContainer
from testcontainers.core.waiting_utils import wait_for_logs

from src.api.rest.app import create_app
from src.api.rest.dependencies import SimulationState
from src.config import Settings


class MosquittoContainer(DockerContainer):
    """Eclipse Mosquitto MQTT broker container."""

    def __init__(
        self,
        image: str = "eclipse-mosquitto:2",
        port: int = 1883,
        **kwargs: Any,
    ) -> None:
        super().__init__(image, **kwargs)
        self.port = port
        self.with_exposed_ports(port)
        # Configure anonymous access
        self.with_command("mosquitto -c /mosquitto-no-auth.conf")
        # Create config for anonymous access
        self.with_env("MOSQUITTO_NO_AUTH", "true")

    def get_broker_url(self) -> str:
        """Get the MQTT broker URL."""
        host = self.get_container_host_ip()
        port = self.get_exposed_port(self.port)
        return f"{host}:{port}"

    def get_host(self) -> str:
        """Get the broker hostname."""
        return self.get_container_host_ip()

    def get_port(self) -> int:
        """Get the mapped broker port."""
        return int(self.get_exposed_port(self.port))


class MQTTMessageCollector:
    """Collects MQTT messages for testing."""

    def __init__(self, host: str, port: int) -> None:
        self.host = host
        self.port = port
        self.messages: dict[str, list[dict[str, Any]]] = {}
        self._client: mqtt.Client | None = None
        self._connected = False

    def _on_connect(
        self,
        client: mqtt.Client,
        userdata: Any,
        flags: Any,
        reason_code: Any,
        properties: Any = None,
    ) -> None:
        """Handle connection."""
        self._connected = True

    def _on_message(
        self,
        client: mqtt.Client,
        userdata: Any,
        message: mqtt.MQTTMessage,
    ) -> None:
        """Handle received message."""
        topic = message.topic
        try:
            payload = json.loads(message.payload.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError):
            payload = {"raw": message.payload.decode("utf-8", errors="replace")}

        if topic not in self.messages:
            self.messages[topic] = []

        self.messages[topic].append(
            {
                "payload": payload,
                "qos": message.qos,
                "retain": message.retain,
                "timestamp": datetime.now(UTC),
            }
        )

    def connect(self) -> None:
        """Connect to the MQTT broker."""
        self._client = mqtt.Client(
            callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
            client_id="test-collector",
            protocol=mqtt.MQTTv5,
        )
        self._client.on_connect = self._on_connect
        self._client.on_message = self._on_message
        self._client.connect(self.host, self.port, keepalive=60)
        self._client.loop_start()

        # Wait for connection
        timeout = 10
        start = time.time()
        while not self._connected and time.time() - start < timeout:
            time.sleep(0.1)

        if not self._connected:
            raise RuntimeError("Failed to connect to MQTT broker")

    def subscribe(self, topic: str, qos: int = 0) -> None:
        """Subscribe to a topic."""
        if self._client:
            self._client.subscribe(topic, qos=qos)

    def disconnect(self) -> None:
        """Disconnect from the broker."""
        if self._client:
            self._client.loop_stop()
            self._client.disconnect()

    def get_messages(self, topic: str) -> list[dict[str, Any]]:
        """Get messages received on a topic."""
        return self.messages.get(topic, [])

    def clear(self) -> None:
        """Clear collected messages."""
        self.messages.clear()

    def wait_for_messages(
        self,
        topic: str,
        count: int = 1,
        timeout: float = 10.0,
    ) -> list[dict[str, Any]]:
        """Wait for a specific number of messages on a topic."""
        start = time.time()
        while time.time() - start < timeout:
            messages = self.get_messages(topic)
            if len(messages) >= count:
                return messages[:count]
            time.sleep(0.1)
        return self.get_messages(topic)


@pytest.fixture(scope="session")
def mqtt_container() -> Generator[MosquittoContainer, None, None]:
    """
    Start an MQTT broker container for integration tests.

    This fixture has session scope to minimize container startup overhead.
    """
    # Create custom mosquitto config for anonymous access
    container = DockerContainer("eclipse-mosquitto:2")
    container.with_exposed_ports(1883)

    # Use a simple config allowing anonymous access
    config_content = """
listener 1883
allow_anonymous true
"""
    container.with_command(
        "sh -c \"echo 'listener 1883\nallow_anonymous true' > /tmp/mosquitto.conf && "
        'mosquitto -c /tmp/mosquitto.conf"'
    )

    with container:
        # Wait for broker to be ready
        time.sleep(2)  # Give broker time to start

        # Create a wrapper to access host and port
        class ContainerWrapper:
            def get_host(self) -> str:
                return container.get_container_host_ip()

            def get_port(self) -> int:
                return int(container.get_exposed_port(1883))

        yield ContainerWrapper()  # type: ignore


@pytest.fixture(scope="session")
def mqtt_host(mqtt_container) -> str:
    """Get the MQTT broker host."""
    return mqtt_container.get_host()


@pytest.fixture(scope="session")
def mqtt_port(mqtt_container) -> int:
    """Get the MQTT broker port."""
    return mqtt_container.get_port()


@pytest.fixture
def mqtt_collector(mqtt_host: str, mqtt_port: int) -> Generator[MQTTMessageCollector, None, None]:
    """
    Create an MQTT message collector for testing.

    Connects to the test broker and collects messages.
    """
    collector = MQTTMessageCollector(mqtt_host, mqtt_port)
    collector.connect()
    yield collector
    collector.disconnect()


@pytest.fixture
def integration_settings(mqtt_host: str, mqtt_port: int) -> Settings:
    """Create settings configured for integration testing."""
    os.environ["FACIS_ENV"] = "test"
    return Settings(
        simulation={
            "seed": 12345,
            "interval_minutes": 1,
            "speed_factor": 1.0,
        },
        mqtt={
            "host": mqtt_host,
            "port": mqtt_port,
            "client_id": "facis-integration-test",
            "qos": 1,
        },
        http={
            "host": "127.0.0.1",
            "port": 8080,
        },
        modbus={
            "host": "127.0.0.1",
            "port": 5020,  # Use non-privileged port for tests
        },
        meters=[
            {
                "id": "test-meter-001",
                "base_load_kw": 10.0,
                "peak_load_kw": 25.0,
            },
            {
                "id": "test-meter-002",
                "base_load_kw": 5.0,
                "peak_load_kw": 15.0,
            },
        ],
        pv_systems=[
            {
                "id": "test-pv-001",
                "nominal_capacity_kw": 10.0,
                "latitude": 52.52,
                "longitude": 13.405,
            },
        ],
        consumers=[
            {
                "id": "test-oven-001",
                "rated_power_kw": 3.5,
                "device_type": "industrial_oven",
            },
            {
                "id": "test-hvac-001",
                "rated_power_kw": 5.0,
                "device_type": "hvac",
            },
        ],
    )


@pytest.fixture
def simulation_state(integration_settings: Settings) -> Generator[SimulationState, None, None]:
    """Create and initialize simulation state for integration testing."""
    # Reset singleton for test isolation
    SimulationState.reset_instance()

    state = SimulationState.get_instance()
    state.initialize(integration_settings)
    yield state

    # Cleanup
    SimulationState.reset_instance()


@pytest.fixture
async def test_client(
    integration_settings: Settings,
) -> Generator[AsyncClient, None, None]:
    """Create an async HTTP test client."""
    # Reset singleton before creating app
    SimulationState.reset_instance()

    # Pre-initialize state with our settings
    state = SimulationState.get_instance()
    state.initialize(integration_settings)

    # Create app without MQTT (we'll test MQTT separately)
    from fastapi import FastAPI
    from fastapi.middleware.cors import CORSMiddleware

    from src.api.rest.routes import health, loads, meters, prices, pv, simulation, weather

    app = FastAPI(title="FACIS Test")
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(health.router, prefix="/api/v1")
    app.include_router(meters.router, prefix="/api/v1")
    app.include_router(prices.router, prefix="/api/v1")
    app.include_router(loads.router, prefix="/api/v1")
    app.include_router(weather.router, prefix="/api/v1")
    app.include_router(pv.router, prefix="/api/v1")
    app.include_router(simulation.router, prefix="/api/v1")

    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

    SimulationState.reset_instance()


@pytest.fixture
def sample_timestamp() -> datetime:
    """Return a sample timestamp for testing."""
    return datetime(2024, 6, 15, 12, 0, 0, tzinfo=UTC)
