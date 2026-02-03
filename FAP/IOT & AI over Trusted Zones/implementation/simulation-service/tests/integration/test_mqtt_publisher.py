"""
Integration tests for MQTT publisher.

Tests verify that all simulation feeds are published to correct MQTT topics
with proper QoS levels and message structures.

NOTE: These tests require a running MQTT broker. Use docker-compose to start one:
    docker-compose up -d mqtt

Or set MQTT_BROKER and MQTT_PORT environment variables.
"""

import json
import os
import threading
import time
from collections import defaultdict
from datetime import UTC, datetime
from typing import Any

import paho.mqtt.client as mqtt
import pytest

from src.api.mqtt import MQTTFeedPublisher, MQTTPublisher, MQTTTopics, QoS
from src.api.rest.dependencies import SimulationState

# =============================================================================
# Test Fixtures
# =============================================================================


@pytest.fixture(scope="module")
def mqtt_broker_host() -> str:
    """Get MQTT broker hostname."""
    return os.environ.get("MQTT_BROKER", "localhost")


@pytest.fixture(scope="module")
def mqtt_broker_port() -> int:
    """Get MQTT broker port."""
    return int(os.environ.get("MQTT_PORT", "1883"))


@pytest.fixture
def mqtt_publisher(mqtt_broker_host: str, mqtt_broker_port: int) -> MQTTPublisher:
    """Create and connect MQTT publisher for testing."""
    publisher = MQTTPublisher(
        host=mqtt_broker_host,
        port=mqtt_broker_port,
        client_id=f"test-publisher-{time.time_ns()}",
        default_qos=1,
    )
    connected = publisher.connect()

    if not connected:
        pytest.skip(f"Could not connect to MQTT broker at {mqtt_broker_host}:{mqtt_broker_port}")

    # Wait for connection
    for _ in range(50):  # 5 seconds max
        if publisher.is_connected:
            break
        time.sleep(0.1)

    if not publisher.is_connected:
        pytest.skip("MQTT connection timeout")

    yield publisher

    publisher.disconnect()


class MQTTTestSubscriber:
    """Test subscriber to capture MQTT messages."""

    def __init__(self, host: str, port: int) -> None:
        self.host = host
        self.port = port
        self.messages: dict[str, list[dict]] = defaultdict(list)
        self.connected = False
        self._lock = threading.Lock()

        # Create client with unique ID
        self._client = mqtt.Client(
            callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
            client_id=f"test-subscriber-{time.time_ns()}",
        )
        self._client.on_connect = self._on_connect
        self._client.on_message = self._on_message

    def _on_connect(
        self,
        client: mqtt.Client,
        userdata: Any,
        flags: mqtt.ConnectFlags,
        reason_code: mqtt.ReasonCode,
        properties: mqtt.Properties | None,
    ) -> None:
        self.connected = True

    def _on_message(
        self,
        client: mqtt.Client,
        userdata: Any,
        msg: mqtt.MQTTMessage,
    ) -> None:
        """Handle incoming messages."""
        try:
            payload = json.loads(msg.payload.decode())
            with self._lock:
                self.messages[msg.topic].append(
                    {
                        "payload": payload,
                        "qos": msg.qos,
                        "retain": msg.retain,
                        "timestamp": time.time(),
                    }
                )
        except json.JSONDecodeError:
            pass

    def connect(self) -> bool:
        """Connect to broker."""
        try:
            self._client.connect(self.host, self.port)
            self._client.loop_start()

            # Wait for connection
            for _ in range(50):
                if self.connected:
                    return True
                time.sleep(0.1)
        except Exception:
            pass
        return False

    def disconnect(self) -> None:
        """Disconnect from broker."""
        self._client.loop_stop()
        self._client.disconnect()

    def subscribe(self, topic: str, qos: int = 0) -> None:
        """Subscribe to a topic."""
        self._client.subscribe(topic, qos)

    def get_messages(self, topic: str, timeout: float = 2.0) -> list[dict]:
        """Get messages received on a topic."""
        start = time.time()
        while time.time() - start < timeout:
            with self._lock:
                if topic in self.messages:
                    return list(self.messages[topic])
            time.sleep(0.1)
        return []

    def clear(self) -> None:
        """Clear received messages."""
        with self._lock:
            self.messages.clear()


@pytest.fixture
def mqtt_subscriber(mqtt_broker_host: str, mqtt_broker_port: int) -> MQTTTestSubscriber:
    """Create test subscriber."""
    subscriber = MQTTTestSubscriber(mqtt_broker_host, mqtt_broker_port)
    if not subscriber.connect():
        pytest.skip("Could not connect subscriber to MQTT broker")

    yield subscriber

    subscriber.disconnect()


# =============================================================================
# Topic Structure Tests
# =============================================================================


class TestMQTTTopics:
    """Test MQTT topic configuration."""

    def test_meter_topic_format(self) -> None:
        """Test meter topic includes meter ID."""
        topic = MQTTTopics.meter_topic("test-meter-001")
        assert topic == "facis/energy/meter/test-meter-001"

    def test_pv_topic_format(self) -> None:
        """Test PV topic includes system ID."""
        topic = MQTTTopics.pv_topic("pv-system-001")
        assert topic == "facis/energy/pv/pv-system-001"

    def test_weather_topic_format(self) -> None:
        """Test weather topic is static."""
        topic = MQTTTopics.weather_topic()
        assert topic == "facis/weather/current"

    def test_price_topics(self) -> None:
        """Test price topics."""
        assert MQTTTopics.spot_price_topic() == "facis/prices/spot"
        assert MQTTTopics.forecast_price_topic() == "facis/prices/forecast"

    def test_load_topic_format(self) -> None:
        """Test load topic includes device type."""
        topic = MQTTTopics.load_topic("industrial_oven")
        assert topic == "facis/loads/industrial_oven"

    def test_alerts_topic(self) -> None:
        """Test alerts topic."""
        assert MQTTTopics.alerts_topic() == "facis/events/alerts"

    def test_simulation_status_topic(self) -> None:
        """Test simulation status topic."""
        assert MQTTTopics.simulation_status_topic() == "facis/simulation/status"

    def test_qos_levels(self) -> None:
        """Test QoS levels are configured correctly."""
        assert MQTTTopics.METER.qos == QoS.AT_LEAST_ONCE  # 1
        assert MQTTTopics.PV.qos == QoS.AT_LEAST_ONCE  # 1
        assert MQTTTopics.WEATHER.qos == QoS.AT_MOST_ONCE  # 0
        assert MQTTTopics.PRICE_SPOT.qos == QoS.AT_LEAST_ONCE  # 1
        assert MQTTTopics.PRICE_FORECAST.qos == QoS.AT_LEAST_ONCE  # 1
        assert MQTTTopics.LOAD.qos == QoS.AT_MOST_ONCE  # 0
        assert MQTTTopics.ALERTS.qos == QoS.EXACTLY_ONCE  # 2
        assert MQTTTopics.SIMULATION_STATUS.qos == QoS.AT_LEAST_ONCE  # 1

    def test_retained_flags(self) -> None:
        """Test retained message flags."""
        assert MQTTTopics.WEATHER.retained is True
        assert MQTTTopics.PRICE_SPOT.retained is True
        assert MQTTTopics.PRICE_FORECAST.retained is True
        assert MQTTTopics.SIMULATION_STATUS.retained is True
        assert MQTTTopics.METER.retained is False
        assert MQTTTopics.PV.retained is False
        assert MQTTTopics.LOAD.retained is False


# =============================================================================
# Publisher Connection Tests
# =============================================================================


class TestMQTTPublisherConnection:
    """Test MQTT publisher connection handling."""

    def test_connect_success(self, mqtt_broker_host: str, mqtt_broker_port: int) -> None:
        """Test successful connection to broker."""
        publisher = MQTTPublisher(
            host=mqtt_broker_host,
            port=mqtt_broker_port,
            client_id=f"test-{time.time_ns()}",
        )

        result = publisher.connect()
        assert result is True

        # Wait for connection
        time.sleep(0.5)
        assert publisher.is_connected

        publisher.disconnect()
        assert not publisher.is_connected

    def test_connect_invalid_host(self) -> None:
        """Test connection failure with invalid host."""
        publisher = MQTTPublisher(
            host="invalid-host-that-does-not-exist",
            port=1883,
            client_id="test-invalid",
        )

        publisher.connect()
        # Connection initiation may succeed, but actual connection will fail
        time.sleep(0.5)
        assert not publisher.is_connected

        publisher.disconnect()


# =============================================================================
# Message Publishing Tests
# =============================================================================


class TestMQTTPublishing:
    """Test MQTT message publishing."""

    def test_publish_meter_reading(
        self,
        mqtt_publisher: MQTTPublisher,
        mqtt_subscriber: MQTTTestSubscriber,
    ) -> None:
        """Test publishing meter reading to correct topic."""
        meter_id = "test-meter-001"
        topic = MQTTTopics.meter_topic(meter_id)

        # Subscribe to meter topic
        mqtt_subscriber.subscribe(topic, qos=1)
        time.sleep(0.2)  # Allow subscription to complete

        # Publish meter reading
        reading = {
            "timestamp": "2024-06-15T12:00:00Z",
            "meter_id": meter_id,
            "readings": {
                "active_power_l1_w": 1234.5,
                "active_power_l2_w": 1234.5,
                "active_power_l3_w": 1234.5,
                "voltage_l1_v": 230.1,
                "voltage_l2_v": 230.2,
                "voltage_l3_v": 230.3,
                "current_l1_a": 5.36,
                "current_l2_a": 5.36,
                "current_l3_a": 5.36,
                "power_factor": 0.98,
                "frequency_hz": 50.01,
                "total_energy_kwh": 12345.67,
            },
        }

        result = mqtt_publisher.publish_meter_reading(meter_id, reading)
        assert result.success is True
        assert result.topic == topic

        # Verify message received
        messages = mqtt_subscriber.get_messages(topic, timeout=2.0)
        assert len(messages) >= 1

        received = messages[-1]["payload"]
        assert received["meter_id"] == meter_id
        assert "readings" in received
        assert received["readings"]["active_power_l1_w"] == 1234.5

    def test_publish_pv_reading(
        self,
        mqtt_publisher: MQTTPublisher,
        mqtt_subscriber: MQTTTestSubscriber,
    ) -> None:
        """Test publishing PV reading to correct topic."""
        system_id = "test-pv-001"
        topic = MQTTTopics.pv_topic(system_id)

        mqtt_subscriber.subscribe(topic, qos=1)
        time.sleep(0.2)

        reading = {
            "timestamp": "2024-06-15T12:00:00Z",
            "system_id": system_id,
            "readings": {
                "power_output_kw": 7.5,
                "daily_energy_kwh": 45.2,
                "irradiance_w_m2": 850.0,
                "module_temperature_c": 42.5,
                "efficiency_percent": 18.5,
            },
        }

        result = mqtt_publisher.publish_pv_reading(system_id, reading)
        assert result.success is True

        messages = mqtt_subscriber.get_messages(topic, timeout=2.0)
        assert len(messages) >= 1
        assert messages[-1]["payload"]["system_id"] == system_id

    def test_publish_weather_retained(
        self,
        mqtt_publisher: MQTTPublisher,
        mqtt_subscriber: MQTTTestSubscriber,
    ) -> None:
        """Test weather message is retained."""
        topic = MQTTTopics.weather_topic()

        mqtt_subscriber.subscribe(topic, qos=0)
        time.sleep(0.2)

        reading = {
            "timestamp": "2024-06-15T12:00:00Z",
            "location": {"latitude": 52.52, "longitude": 13.405},
            "conditions": {
                "temperature_c": 22.5,
                "humidity_percent": 65.0,
                "wind_speed_ms": 4.5,
                "wind_direction_deg": 270,
                "cloud_cover_percent": 30.0,
                "ghi_w_m2": 750.0,
                "dni_w_m2": 600.0,
                "dhi_w_m2": 150.0,
            },
        }

        result = mqtt_publisher.publish_weather(reading)
        assert result.success is True

        messages = mqtt_subscriber.get_messages(topic, timeout=2.0)
        assert len(messages) >= 1
        # Note: retained flag may be False for messages received after subscribe
        assert messages[-1]["payload"]["conditions"]["temperature_c"] == 22.5

    def test_publish_spot_price(
        self,
        mqtt_publisher: MQTTPublisher,
        mqtt_subscriber: MQTTTestSubscriber,
    ) -> None:
        """Test publishing spot price."""
        topic = MQTTTopics.spot_price_topic()

        mqtt_subscriber.subscribe(topic, qos=1)
        time.sleep(0.2)

        reading = {
            "timestamp": "2024-06-15T12:00:00Z",
            "price_eur_per_kwh": 0.2567,
            "tariff_type": "midday",
        }

        result = mqtt_publisher.publish_spot_price(reading)
        assert result.success is True

        messages = mqtt_subscriber.get_messages(topic, timeout=2.0)
        assert len(messages) >= 1
        assert messages[-1]["payload"]["price_eur_per_kwh"] == 0.2567

    def test_publish_price_forecast(
        self,
        mqtt_publisher: MQTTPublisher,
        mqtt_subscriber: MQTTTestSubscriber,
    ) -> None:
        """Test publishing price forecast."""
        topic = MQTTTopics.forecast_price_topic()

        mqtt_subscriber.subscribe(topic, qos=1)
        time.sleep(0.2)

        forecast = {
            "generated_at": "2024-06-15T12:00:00Z",
            "forecast_horizon_hours": 24,
            "prices": [
                {
                    "timestamp": "2024-06-15T13:00:00Z",
                    "price_eur_per_kwh": 0.26,
                    "tariff_type": "midday",
                },
                {
                    "timestamp": "2024-06-15T14:00:00Z",
                    "price_eur_per_kwh": 0.27,
                    "tariff_type": "midday",
                },
            ],
        }

        result = mqtt_publisher.publish_price_forecast(forecast)
        assert result.success is True

        messages = mqtt_subscriber.get_messages(topic, timeout=2.0)
        assert len(messages) >= 1
        assert messages[-1]["payload"]["forecast_horizon_hours"] == 24

    def test_publish_consumer_load(
        self,
        mqtt_publisher: MQTTPublisher,
        mqtt_subscriber: MQTTTestSubscriber,
    ) -> None:
        """Test publishing consumer load data."""
        device_type = "industrial_oven"
        topic = MQTTTopics.load_topic(device_type)

        mqtt_subscriber.subscribe(topic, qos=0)
        time.sleep(0.2)

        reading = {
            "timestamp": "2024-06-15T12:00:00Z",
            "device_id": "oven-001",
            "device_type": device_type,
            "device_state": "ON",
            "device_power_kw": 3.2,
        }

        result = mqtt_publisher.publish_load(device_type, reading)
        assert result.success is True

        messages = mqtt_subscriber.get_messages(topic, timeout=2.0)
        assert len(messages) >= 1
        assert messages[-1]["payload"]["device_state"] == "ON"

    def test_publish_alert(
        self,
        mqtt_publisher: MQTTPublisher,
        mqtt_subscriber: MQTTTestSubscriber,
    ) -> None:
        """Test publishing system alert with QoS 2."""
        topic = MQTTTopics.alerts_topic()

        mqtt_subscriber.subscribe(topic, qos=2)
        time.sleep(0.2)

        alert = {
            "timestamp": "2024-06-15T12:00:00Z",
            "severity": "warning",
            "message": "High temperature detected",
            "source": "pv-system-001",
        }

        result = mqtt_publisher.publish_alert(alert)
        assert result.success is True

        messages = mqtt_subscriber.get_messages(topic, timeout=2.0)
        assert len(messages) >= 1
        assert messages[-1]["payload"]["severity"] == "warning"

    def test_publish_simulation_status(
        self,
        mqtt_publisher: MQTTPublisher,
        mqtt_subscriber: MQTTTestSubscriber,
    ) -> None:
        """Test publishing simulation status."""
        topic = MQTTTopics.simulation_status_topic()

        mqtt_subscriber.subscribe(topic, qos=1)
        time.sleep(0.2)

        status = {
            "state": "running",
            "simulation_time": "2024-06-15T12:00:00Z",
            "seed": 12345,
            "acceleration": 1,
            "entities": {
                "meters": 2,
                "pv_systems": 2,
                "weather_stations": 1,
                "price_feeds": 1,
                "loads": 4,
            },
        }

        result = mqtt_publisher.publish_simulation_status(status)
        assert result.success is True

        messages = mqtt_subscriber.get_messages(topic, timeout=2.0)
        assert len(messages) >= 1
        assert messages[-1]["payload"]["state"] == "running"


# =============================================================================
# Feed Publisher Integration Tests
# =============================================================================


class TestMQTTFeedPublisher:
    """Test integrated feed publishing from simulation state."""

    def test_publish_all_feeds(
        self,
        mqtt_publisher: MQTTPublisher,
        mqtt_subscriber: MQTTTestSubscriber,
        simulation_state: SimulationState,
    ) -> None:
        """Test publishing all feeds at once."""
        feed_publisher = MQTTFeedPublisher(mqtt_publisher)

        # Subscribe to all topics
        mqtt_subscriber.subscribe("facis/#", qos=1)
        time.sleep(0.3)

        # Publish all feeds
        timestamp = datetime(2024, 6, 15, 12, 0, 0, tzinfo=UTC)
        results = feed_publisher.publish_all_feeds(
            meters=simulation_state._meters,
            pv_systems=simulation_state._pv_systems,
            weather_stations=simulation_state._weather_stations,
            price_feeds=simulation_state._price_feeds,
            loads=simulation_state._loads,
            simulation_time=timestamp,
        )

        # Verify results
        assert len(results["meters"]) > 0
        assert all(r.success for r in results["meters"])

        assert len(results["pv"]) > 0
        assert all(r.success for r in results["pv"])

        assert len(results["weather"]) > 0
        assert all(r.success for r in results["weather"])

        assert len(results["prices"]) > 0
        assert all(r.success for r in results["prices"])

        # Check messages received
        time.sleep(0.5)

        # Verify meter messages
        meter_topic = MQTTTopics.meter_topic("test-meter-001")
        meter_msgs = mqtt_subscriber.get_messages(meter_topic, timeout=1.0)
        assert len(meter_msgs) >= 1

        # Verify weather messages
        weather_msgs = mqtt_subscriber.get_messages(MQTTTopics.weather_topic(), timeout=1.0)
        assert len(weather_msgs) >= 1

        # Verify price messages
        price_msgs = mqtt_subscriber.get_messages(MQTTTopics.spot_price_topic(), timeout=1.0)
        assert len(price_msgs) >= 1

    def test_publish_simulation_status(
        self,
        mqtt_publisher: MQTTPublisher,
        mqtt_subscriber: MQTTTestSubscriber,
    ) -> None:
        """Test publishing simulation status via feed publisher."""
        feed_publisher = MQTTFeedPublisher(mqtt_publisher)

        topic = MQTTTopics.simulation_status_topic()
        mqtt_subscriber.subscribe(topic, qos=1)
        time.sleep(0.2)

        timestamp = datetime(2024, 6, 15, 12, 0, 0, tzinfo=UTC)
        result = feed_publisher.publish_simulation_status(
            state="running",
            simulation_time=timestamp,
            seed=12345,
            acceleration=10,
            entities={
                "meters": 2,
                "pv_systems": 2,
                "weather_stations": 1,
                "price_feeds": 1,
                "loads": 4,
            },
        )

        assert result.success is True

        messages = mqtt_subscriber.get_messages(topic, timeout=2.0)
        assert len(messages) >= 1
        assert messages[-1]["payload"]["acceleration"] == 10


# =============================================================================
# JSON Payload Validation Tests
# =============================================================================


class TestMQTTPayloadStructure:
    """Test that JSON payloads match spec structures."""

    def test_meter_payload_structure(
        self,
        mqtt_publisher: MQTTPublisher,
        mqtt_subscriber: MQTTTestSubscriber,
        simulation_state: SimulationState,
    ) -> None:
        """Test meter payload has all required fields."""
        meter_id = "test-meter-001"
        topic = MQTTTopics.meter_topic(meter_id)

        mqtt_subscriber.subscribe(topic, qos=1)
        time.sleep(0.2)

        # Generate and publish reading
        meter = simulation_state.get_meter(meter_id)
        assert meter is not None

        timestamp = datetime(2024, 6, 15, 12, 0, 0, tzinfo=UTC)
        reading = meter.generate_at(timestamp)
        assert reading is not None

        payload = reading.value.to_json_payload()
        result = mqtt_publisher.publish_meter_reading(meter_id, payload)
        assert result.success is True

        messages = mqtt_subscriber.get_messages(topic, timeout=2.0)
        assert len(messages) >= 1

        received = messages[-1]["payload"]

        # Verify required fields
        assert "timestamp" in received
        assert "meter_id" in received
        assert "readings" in received

        readings = received["readings"]
        required_fields = [
            "active_power_l1_w",
            "active_power_l2_w",
            "active_power_l3_w",
            "voltage_l1_v",
            "voltage_l2_v",
            "voltage_l3_v",
            "current_l1_a",
            "current_l2_a",
            "current_l3_a",
            "power_factor",
            "frequency_hz",
            "total_energy_kwh",
        ]
        for field in required_fields:
            assert field in readings, f"Missing field: {field}"

    def test_pv_payload_structure(
        self,
        mqtt_publisher: MQTTPublisher,
        mqtt_subscriber: MQTTTestSubscriber,
        simulation_state: SimulationState,
    ) -> None:
        """Test PV payload has all required fields."""
        system_id = "test-pv-001"
        topic = MQTTTopics.pv_topic(system_id)

        mqtt_subscriber.subscribe(topic, qos=1)
        time.sleep(0.2)

        pv = simulation_state.get_pv_system(system_id)
        assert pv is not None

        timestamp = datetime(2024, 6, 15, 12, 0, 0, tzinfo=UTC)
        reading = pv.generate_at(timestamp)
        assert reading is not None

        payload = reading.value.to_json_payload()
        result = mqtt_publisher.publish_pv_reading(system_id, payload)
        assert result.success is True

        messages = mqtt_subscriber.get_messages(topic, timeout=2.0)
        assert len(messages) >= 1

        received = messages[-1]["payload"]

        assert "timestamp" in received
        assert "system_id" in received
        assert "readings" in received

        readings = received["readings"]
        required_fields = [
            "power_output_kw",
            "daily_energy_kwh",
            "irradiance_w_m2",
            "module_temperature_c",
            "efficiency_percent",
        ]
        for field in required_fields:
            assert field in readings, f"Missing field: {field}"

    def test_weather_payload_structure(
        self,
        mqtt_publisher: MQTTPublisher,
        mqtt_subscriber: MQTTTestSubscriber,
        simulation_state: SimulationState,
    ) -> None:
        """Test weather payload has all required fields."""
        topic = MQTTTopics.weather_topic()

        mqtt_subscriber.subscribe(topic, qos=0)
        time.sleep(0.2)

        weather = simulation_state.get_weather_station("weather-001")
        assert weather is not None

        timestamp = datetime(2024, 6, 15, 12, 0, 0, tzinfo=UTC)
        reading = weather.generate_at(timestamp)
        assert reading is not None

        payload = reading.value.to_json_payload()
        result = mqtt_publisher.publish_weather(payload)
        assert result.success is True

        messages = mqtt_subscriber.get_messages(topic, timeout=2.0)
        assert len(messages) >= 1

        received = messages[-1]["payload"]

        assert "timestamp" in received
        assert "location" in received
        assert "conditions" in received

        location = received["location"]
        assert "latitude" in location
        assert "longitude" in location

        conditions = received["conditions"]
        required_fields = [
            "temperature_c",
            "humidity_percent",
            "wind_speed_ms",
            "wind_direction_deg",
            "cloud_cover_percent",
            "ghi_w_m2",
            "dni_w_m2",
            "dhi_w_m2",
        ]
        for field in required_fields:
            assert field in conditions, f"Missing field: {field}"

    def test_price_payload_structure(
        self,
        mqtt_publisher: MQTTPublisher,
        mqtt_subscriber: MQTTTestSubscriber,
        simulation_state: SimulationState,
    ) -> None:
        """Test price payload has all required fields."""
        topic = MQTTTopics.spot_price_topic()

        mqtt_subscriber.subscribe(topic, qos=1)
        time.sleep(0.2)

        price_feed = simulation_state.get_default_price_feed()
        assert price_feed is not None

        timestamp = datetime(2024, 6, 15, 12, 0, 0, tzinfo=UTC)
        reading = price_feed.generate_at(timestamp)
        assert reading is not None

        payload = reading.value.to_json_payload()
        result = mqtt_publisher.publish_spot_price(payload)
        assert result.success is True

        messages = mqtt_subscriber.get_messages(topic, timeout=2.0)
        assert len(messages) >= 1

        received = messages[-1]["payload"]

        assert "timestamp" in received
        assert "price_eur_per_kwh" in received
        assert "tariff_type" in received
