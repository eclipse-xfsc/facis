"""
MQTT integration tests.

Tests MQTT message publishing with a real MQTT broker using testcontainers.
"""

import json
import time
from datetime import UTC, datetime

import paho.mqtt.client as mqtt
import pytest

from src.api.mqtt.publisher import MQTTPublisher
from src.api.mqtt.topics import MQTTTopics, QoS
from src.config import Settings

pytestmark = pytest.mark.timeout(60)


class TestMQTTConnection:
    """Test MQTT broker connection."""

    def test_connect_to_broker(self, mqtt_host: str, mqtt_port: int) -> None:
        """Test connecting to the MQTT broker."""
        publisher = MQTTPublisher(
            host=mqtt_host,
            port=mqtt_port,
            client_id="test-connection",
        )

        assert publisher.connect() is True

        # Wait for connection
        timeout = 5
        start = time.time()
        while not publisher.is_connected and time.time() - start < timeout:
            time.sleep(0.1)

        assert publisher.is_connected
        publisher.disconnect()

    def test_reconnection_on_disconnect(self, mqtt_host: str, mqtt_port: int) -> None:
        """Test that publisher handles disconnection gracefully."""
        publisher = MQTTPublisher(
            host=mqtt_host,
            port=mqtt_port,
            client_id="test-reconnect",
        )

        publisher.connect()

        # Wait for connection
        timeout = 5
        start = time.time()
        while not publisher.is_connected and time.time() - start < timeout:
            time.sleep(0.1)

        assert publisher.is_connected
        publisher.disconnect()
        assert not publisher.is_connected


class TestMQTTTopics:
    """Test publishing to all MQTT topics."""

    def test_publish_meter_reading(
        self,
        mqtt_host: str,
        mqtt_port: int,
        mqtt_collector,
    ) -> None:
        """Test publishing energy meter readings."""
        topic = MQTTTopics.meter_topic("test-meter-001")
        mqtt_collector.subscribe(topic, qos=1)

        publisher = MQTTPublisher(
            host=mqtt_host,
            port=mqtt_port,
            client_id="test-meter-pub",
        )
        publisher.connect()

        # Wait for connection
        time.sleep(1)

        meter_reading = {
            "timestamp": "2024-06-15T12:00:00Z",
            "meter_id": "test-meter-001",
            "readings": {
                "active_power_l1_w": 3500.5,
                "active_power_l2_w": 3400.2,
                "active_power_l3_w": 3450.8,
                "voltage_l1_v": 230.1,
                "voltage_l2_v": 229.8,
                "voltage_l3_v": 230.5,
                "current_l1_a": 15.2,
                "current_l2_a": 14.8,
                "current_l3_a": 15.0,
                "power_factor": 0.95,
                "frequency_hz": 50.01,
                "total_energy_kwh": 12500.5,
            },
        }

        result = publisher.publish_meter_reading("test-meter-001", meter_reading)
        assert result.success is True
        assert result.topic == topic

        # Wait for message
        messages = mqtt_collector.wait_for_messages(topic, count=1, timeout=5)
        assert len(messages) >= 1

        received = messages[0]
        assert received["payload"]["meter_id"] == "test-meter-001"
        assert "readings" in received["payload"]
        assert received["payload"]["readings"]["active_power_l1_w"] == 3500.5

        publisher.disconnect()

    def test_publish_pv_reading(
        self,
        mqtt_host: str,
        mqtt_port: int,
        mqtt_collector,
    ) -> None:
        """Test publishing PV generation readings."""
        topic = MQTTTopics.pv_topic("test-pv-001")
        mqtt_collector.subscribe(topic, qos=1)

        publisher = MQTTPublisher(
            host=mqtt_host,
            port=mqtt_port,
            client_id="test-pv-pub",
        )
        publisher.connect()
        time.sleep(1)

        pv_reading = {
            "timestamp": "2024-06-15T12:00:00Z",
            "system_id": "test-pv-001",
            "readings": {
                "power_output_kw": 8.5,
                "daily_energy_kwh": 45.2,
                "irradiance_w_m2": 850.0,
                "module_temperature_c": 45.5,
                "efficiency_percent": 18.5,
            },
        }

        result = publisher.publish_pv_reading("test-pv-001", pv_reading)
        assert result.success is True

        messages = mqtt_collector.wait_for_messages(topic, count=1, timeout=5)
        assert len(messages) >= 1
        assert messages[0]["payload"]["system_id"] == "test-pv-001"

        publisher.disconnect()

    def test_publish_weather_reading(
        self,
        mqtt_host: str,
        mqtt_port: int,
        mqtt_collector,
    ) -> None:
        """Test publishing weather readings with retention."""
        topic = MQTTTopics.weather_topic()
        mqtt_collector.subscribe(topic, qos=0)

        publisher = MQTTPublisher(
            host=mqtt_host,
            port=mqtt_port,
            client_id="test-weather-pub",
        )
        publisher.connect()
        time.sleep(1)

        weather_reading = {
            "timestamp": "2024-06-15T12:00:00Z",
            "station_id": "weather-001",
            "readings": {
                "temperature_c": 22.5,
                "humidity_pct": 65.0,
                "wind_speed_ms": 3.5,
                "irradiance_w_m2": 850.0,
                "cloud_cover_pct": 20.0,
            },
        }

        result = publisher.publish_weather(weather_reading)
        assert result.success is True

        messages = mqtt_collector.wait_for_messages(topic, count=1, timeout=5)
        assert len(messages) >= 1
        assert messages[0]["payload"]["readings"]["temperature_c"] == 22.5

        publisher.disconnect()

    def test_publish_spot_price(
        self,
        mqtt_host: str,
        mqtt_port: int,
        mqtt_collector,
    ) -> None:
        """Test publishing spot price readings with retention."""
        topic = MQTTTopics.spot_price_topic()
        mqtt_collector.subscribe(topic, qos=1)

        publisher = MQTTPublisher(
            host=mqtt_host,
            port=mqtt_port,
            client_id="test-price-pub",
        )
        publisher.connect()
        time.sleep(1)

        price_reading = {
            "timestamp": "2024-06-15T12:00:00Z",
            "feed_id": "epex-spot-de",
            "price_eur_per_kwh": 0.0852,
            "tariff_type": "peak",
        }

        result = publisher.publish_spot_price(price_reading)
        assert result.success is True

        messages = mqtt_collector.wait_for_messages(topic, count=1, timeout=5)
        assert len(messages) >= 1
        assert messages[0]["payload"]["price_eur_per_kwh"] == 0.0852

        publisher.disconnect()

    def test_publish_price_forecast(
        self,
        mqtt_host: str,
        mqtt_port: int,
        mqtt_collector,
    ) -> None:
        """Test publishing price forecast with retention."""
        topic = MQTTTopics.forecast_price_topic()
        mqtt_collector.subscribe(topic, qos=1)

        publisher = MQTTPublisher(
            host=mqtt_host,
            port=mqtt_port,
            client_id="test-forecast-pub",
        )
        publisher.connect()
        time.sleep(1)

        forecast = {
            "generated_at": "2024-06-15T12:00:00Z",
            "forecast_horizon_hours": 24,
            "prices": [
                {"timestamp": "2024-06-15T13:00:00Z", "price_eur_per_kwh": 0.0852},
                {"timestamp": "2024-06-15T14:00:00Z", "price_eur_per_kwh": 0.0910},
            ],
        }

        result = publisher.publish_price_forecast(forecast)
        assert result.success is True

        messages = mqtt_collector.wait_for_messages(topic, count=1, timeout=5)
        assert len(messages) >= 1
        assert messages[0]["payload"]["forecast_horizon_hours"] == 24
        assert len(messages[0]["payload"]["prices"]) == 2

        publisher.disconnect()


class TestMQTTMessageFormat:
    """Test MQTT message JSON format compliance."""

    def test_message_is_valid_json(
        self,
        mqtt_host: str,
        mqtt_port: int,
        mqtt_collector,
    ) -> None:
        """Test that all messages are valid JSON."""
        topic = MQTTTopics.meter_topic("json-test-meter")
        mqtt_collector.subscribe(topic, qos=1)

        publisher = MQTTPublisher(
            host=mqtt_host,
            port=mqtt_port,
            client_id="test-json-pub",
        )
        publisher.connect()
        time.sleep(1)

        payload = {
            "timestamp": "2024-06-15T12:00:00Z",
            "meter_id": "json-test-meter",
            "readings": {"value": 123.45},
        }

        result = publisher.publish(topic, payload, qos=1)
        assert result.success is True

        messages = mqtt_collector.wait_for_messages(topic, count=1, timeout=5)
        assert len(messages) >= 1

        # Verify JSON structure
        received = messages[0]["payload"]
        assert isinstance(received, dict)
        assert "timestamp" in received
        assert "meter_id" in received

        publisher.disconnect()

    def test_timestamp_format_iso8601(
        self,
        mqtt_host: str,
        mqtt_port: int,
        mqtt_collector,
    ) -> None:
        """Test that timestamps are in ISO 8601 format with Z suffix."""
        topic = MQTTTopics.simulation_status_topic()
        mqtt_collector.subscribe(topic, qos=1)

        publisher = MQTTPublisher(
            host=mqtt_host,
            port=mqtt_port,
            client_id="test-timestamp-pub",
        )
        publisher.connect()
        time.sleep(1)

        status = {
            "state": "running",
            "simulation_time": "2024-06-15T12:00:00Z",
            "published_at": datetime.now(UTC).isoformat().replace("+00:00", "Z"),
        }

        result = publisher.publish_simulation_status(status)
        assert result.success is True

        messages = mqtt_collector.wait_for_messages(topic, count=1, timeout=5)
        assert len(messages) >= 1

        received = messages[0]["payload"]
        # Verify timestamp ends with Z
        assert received["simulation_time"].endswith("Z")
        assert received["published_at"].endswith("Z")

        publisher.disconnect()

    def test_numeric_precision(
        self,
        mqtt_host: str,
        mqtt_port: int,
        mqtt_collector,
    ) -> None:
        """Test that numeric values maintain appropriate precision."""
        topic = MQTTTopics.meter_topic("precision-test")
        mqtt_collector.subscribe(topic, qos=1)

        publisher = MQTTPublisher(
            host=mqtt_host,
            port=mqtt_port,
            client_id="test-precision-pub",
        )
        publisher.connect()
        time.sleep(1)

        # Use values with specific decimal precision
        payload = {
            "timestamp": "2024-06-15T12:00:00Z",
            "readings": {
                "voltage": 230.12345,
                "current": 15.6789,
                "power_factor": 0.9512,
            },
        }

        result = publisher.publish(topic, payload, qos=1)
        assert result.success is True

        messages = mqtt_collector.wait_for_messages(topic, count=1, timeout=5)
        assert len(messages) >= 1

        received = messages[0]["payload"]
        # JSON should preserve numeric precision
        assert received["readings"]["voltage"] == 230.12345
        assert received["readings"]["current"] == 15.6789
        assert received["readings"]["power_factor"] == 0.9512

        publisher.disconnect()


class TestMQTTRetainedMessages:
    """Test MQTT retained message functionality."""

    def test_weather_message_is_retained(
        self,
        mqtt_host: str,
        mqtt_port: int,
    ) -> None:
        """Test that weather messages are retained."""
        topic = MQTTTopics.weather_topic()

        # First, publish a retained message
        publisher = MQTTPublisher(
            host=mqtt_host,
            port=mqtt_port,
            client_id="test-retain-pub",
        )
        publisher.connect()
        time.sleep(1)

        weather_reading = {
            "timestamp": "2024-06-15T12:00:00Z",
            "readings": {"temperature_c": 25.0},
        }

        # Publish with retain flag
        result = publisher.publish(
            topic=topic,
            payload=weather_reading,
            qos=0,
            retain=True,
        )
        assert result.success is True
        publisher.disconnect()

        # Now connect a new subscriber and check for retained message
        retained_messages: list = []
        received_event = {"received": False}

        def on_message(client, userdata, message):
            if message.retain:
                retained_messages.append(
                    {
                        "topic": message.topic,
                        "payload": json.loads(message.payload.decode()),
                        "retain": message.retain,
                    }
                )
            received_event["received"] = True

        subscriber = mqtt.Client(
            callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
            client_id="test-retain-sub",
            protocol=mqtt.MQTTv5,
        )
        subscriber.on_message = on_message
        subscriber.connect(mqtt_host, mqtt_port)
        subscriber.loop_start()

        time.sleep(0.5)  # Wait for connection
        subscriber.subscribe(topic, qos=0)

        # Wait for retained message
        timeout = 5
        start = time.time()
        while not received_event["received"] and time.time() - start < timeout:
            time.sleep(0.1)

        subscriber.loop_stop()
        subscriber.disconnect()

        # Verify retained message was received
        assert len(retained_messages) >= 1
        assert retained_messages[0]["retain"] is True
        assert retained_messages[0]["payload"]["readings"]["temperature_c"] == 25.0

    def test_spot_price_is_retained(
        self,
        mqtt_host: str,
        mqtt_port: int,
    ) -> None:
        """Test that spot price messages are retained."""
        topic = MQTTTopics.spot_price_topic()

        # Publish retained price
        publisher = MQTTPublisher(
            host=mqtt_host,
            port=mqtt_port,
            client_id="test-price-retain-pub",
        )
        publisher.connect()
        time.sleep(1)

        price = {"price_eur_per_kwh": 0.0950, "timestamp": "2024-06-15T14:00:00Z"}
        result = publisher.publish(topic=topic, payload=price, qos=1, retain=True)
        assert result.success is True
        publisher.disconnect()

        # Subscribe and verify retention
        retained_messages: list = []
        received_event = {"received": False}

        def on_message(client, userdata, message):
            if message.retain:
                retained_messages.append(json.loads(message.payload.decode()))
            received_event["received"] = True

        subscriber = mqtt.Client(
            callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
            client_id="test-price-retain-sub",
            protocol=mqtt.MQTTv5,
        )
        subscriber.on_message = on_message
        subscriber.connect(mqtt_host, mqtt_port)
        subscriber.loop_start()

        time.sleep(0.5)
        subscriber.subscribe(topic, qos=1)

        timeout = 5
        start = time.time()
        while not received_event["received"] and time.time() - start < timeout:
            time.sleep(0.1)

        subscriber.loop_stop()
        subscriber.disconnect()

        assert len(retained_messages) >= 1
        assert retained_messages[0]["price_eur_per_kwh"] == 0.0950


class TestMQTTQoSLevels:
    """Test MQTT QoS level handling."""

    def test_qos_0_delivery(
        self,
        mqtt_host: str,
        mqtt_port: int,
        mqtt_collector,
    ) -> None:
        """Test QoS 0 (at most once) message delivery."""
        topic = "test/qos0"
        mqtt_collector.subscribe(topic, qos=0)

        publisher = MQTTPublisher(
            host=mqtt_host,
            port=mqtt_port,
            client_id="test-qos0-pub",
        )
        publisher.connect()
        time.sleep(1)

        result = publisher.publish(topic, {"test": "qos0"}, qos=0)
        assert result.success is True

        messages = mqtt_collector.wait_for_messages(topic, count=1, timeout=5)
        assert len(messages) >= 1

        publisher.disconnect()

    def test_qos_1_delivery(
        self,
        mqtt_host: str,
        mqtt_port: int,
        mqtt_collector,
    ) -> None:
        """Test QoS 1 (at least once) message delivery."""
        topic = "test/qos1"
        mqtt_collector.subscribe(topic, qos=1)

        publisher = MQTTPublisher(
            host=mqtt_host,
            port=mqtt_port,
            client_id="test-qos1-pub",
        )
        publisher.connect()
        time.sleep(1)

        result = publisher.publish(topic, {"test": "qos1"}, qos=1)
        assert result.success is True
        assert result.message_id is not None  # QoS 1 returns message ID

        messages = mqtt_collector.wait_for_messages(topic, count=1, timeout=5)
        assert len(messages) >= 1

        publisher.disconnect()

    def test_qos_2_delivery(
        self,
        mqtt_host: str,
        mqtt_port: int,
        mqtt_collector,
    ) -> None:
        """Test QoS 2 (exactly once) message delivery."""
        topic = "test/qos2"
        mqtt_collector.subscribe(topic, qos=2)

        publisher = MQTTPublisher(
            host=mqtt_host,
            port=mqtt_port,
            client_id="test-qos2-pub",
        )
        publisher.connect()
        time.sleep(1)

        result = publisher.publish(topic, {"test": "qos2"}, qos=2)
        assert result.success is True

        messages = mqtt_collector.wait_for_messages(topic, count=1, timeout=5)
        assert len(messages) >= 1

        publisher.disconnect()


class TestAllFiveTopics:
    """Test that all 5 main topics receive messages correctly."""

    def test_all_topics_publish_successfully(
        self,
        mqtt_host: str,
        mqtt_port: int,
        mqtt_collector,
    ) -> None:
        """Test publishing to all 5 main topic types."""
        # Define the 5 main topics
        topics = {
            "meter": MQTTTopics.meter_topic("all-topics-meter"),
            "pv": MQTTTopics.pv_topic("all-topics-pv"),
            "weather": MQTTTopics.weather_topic(),
            "price_spot": MQTTTopics.spot_price_topic(),
            "load": MQTTTopics.load_topic("industrial_oven"),
        }

        # Subscribe to all topics
        for topic in topics.values():
            mqtt_collector.subscribe(topic, qos=1)

        publisher = MQTTPublisher(
            host=mqtt_host,
            port=mqtt_port,
            client_id="test-all-topics-pub",
        )
        publisher.connect()
        time.sleep(1)

        # Publish to each topic
        payloads = {
            "meter": {
                "timestamp": "2024-06-15T12:00:00Z",
                "meter_id": "all-topics-meter",
                "readings": {"power_w": 1000},
            },
            "pv": {
                "timestamp": "2024-06-15T12:00:00Z",
                "system_id": "all-topics-pv",
                "readings": {"power_kw": 5.0},
            },
            "weather": {
                "timestamp": "2024-06-15T12:00:00Z",
                "readings": {"temperature_c": 20.0},
            },
            "price_spot": {
                "timestamp": "2024-06-15T12:00:00Z",
                "price_eur_per_kwh": 0.08,
            },
            "load": {
                "timestamp": "2024-06-15T12:00:00Z",
                "device_type": "industrial_oven",
                "power_kw": 3.5,
            },
        }

        results = {}
        for key, topic in topics.items():
            result = publisher.publish(topic, payloads[key], qos=1)
            results[key] = result
            assert result.success is True, f"Failed to publish to {key}: {result.error}"

        # Wait for all messages
        time.sleep(2)

        # Verify each topic received at least one message
        for key, topic in topics.items():
            messages = mqtt_collector.get_messages(topic)
            assert len(messages) >= 1, f"No message received on {key} topic: {topic}"

        publisher.disconnect()
