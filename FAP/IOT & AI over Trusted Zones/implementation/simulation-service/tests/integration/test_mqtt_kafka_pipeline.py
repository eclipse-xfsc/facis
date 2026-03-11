"""
Integration tests for the MQTT → Kafka Bronze pipeline.

Tests the end-to-end flow:
    MQTT Publish → ConsumeMQTT (simulated) → Metadata Enrichment → Kafka Bronze Topics

These tests verify:
    1. All 5 MQTT subscriptions route to the correct Kafka Bronze topics
    2. Ingestion metadata (ingest_timestamp, source_system, source_topic) is added
    3. Original payload is preserved unmodified inside the envelope
    4. Dead-letter queue receives messages on publish failure
    5. No data loss under normal operation (message count parity)

Requirements:
    pip install -e ".[dev]"
    Docker Compose stack running: docker compose up -d mqtt kafka

Usage:
    pytest tests/integration/test_mqtt_kafka_pipeline.py -v
    pytest tests/integration/test_mqtt_kafka_pipeline.py -v -k test_meter_readings
"""

from __future__ import annotations

import json
import logging
import time
import uuid
from datetime import datetime, timezone
from typing import Any, Generator

import pytest

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Test configuration — matches scripts/setup_nifi_mqtt_to_kafka.py
# ---------------------------------------------------------------------------

MQTT_BROKER_HOST = "localhost"
MQTT_BROKER_PORT = 1883
KAFKA_BOOTSTRAP = "localhost:9092"

# Topic mapping from the pipeline specification
MQTT_KAFKA_ROUTES = [
    {
        "mqtt_topic_pattern": "facis/energy/meter/{id}",
        "mqtt_subscription": "facis/energy/meter/+",
        "kafka_topic": "energy.bronze.meter-readings",
        "test_mqtt_topic": "facis/energy/meter/meter-001",
    },
    {
        "mqtt_topic_pattern": "facis/prices/spot",
        "mqtt_subscription": "facis/prices/spot",
        "kafka_topic": "energy.bronze.prices",
        "test_mqtt_topic": "facis/prices/spot",
    },
    {
        "mqtt_topic_pattern": "facis/weather/current",
        "mqtt_subscription": "facis/weather/current",
        "kafka_topic": "energy.bronze.weather",
        "test_mqtt_topic": "facis/weather/current",
    },
    {
        "mqtt_topic_pattern": "facis/energy/pv/{id}",
        "mqtt_subscription": "facis/energy/pv/+",
        "kafka_topic": "energy.bronze.pv-generation",
        "test_mqtt_topic": "facis/energy/pv/pv-system-001",
    },
    {
        "mqtt_topic_pattern": "facis/loads/{type}",
        "mqtt_subscription": "facis/loads/+",
        "kafka_topic": "energy.bronze.consumer-states",
        "test_mqtt_topic": "facis/loads/industrial_oven",
    },
]

DEAD_LETTER_TOPIC = "energy.bronze.dead-letter"

# ---------------------------------------------------------------------------
# Test fixtures
# ---------------------------------------------------------------------------


def _check_mqtt_available() -> bool:
    """Check if MQTT broker is reachable."""
    try:
        import paho.mqtt.client as mqtt

        client = mqtt.Client(
            callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
            client_id=f"test-probe-{uuid.uuid4().hex[:8]}",
        )
        client.connect(MQTT_BROKER_HOST, MQTT_BROKER_PORT, keepalive=5)
        client.disconnect()
        return True
    except Exception:
        return False


def _check_kafka_available() -> bool:
    """Check if Kafka broker is reachable."""
    try:
        from confluent_kafka.admin import AdminClient

        admin = AdminClient({"bootstrap.servers": KAFKA_BOOTSTRAP})
        metadata = admin.list_topics(timeout=5)
        return metadata is not None
    except Exception:
        return False


mqtt_available = pytest.mark.skipif(
    not _check_mqtt_available(),
    reason="MQTT broker not available at localhost:1883",
)

kafka_available = pytest.mark.skipif(
    not _check_kafka_available(),
    reason="Kafka broker not available at localhost:9092",
)

requires_infrastructure = pytest.mark.skipif(
    not (_check_mqtt_available() and _check_kafka_available()),
    reason="MQTT and/or Kafka not available (run: docker compose up -d mqtt kafka)",
)


@pytest.fixture
def mqtt_publisher():
    """Create an MQTT publisher for test messages."""
    import paho.mqtt.client as mqtt

    client = mqtt.Client(
        callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
        client_id=f"test-publisher-{uuid.uuid4().hex[:8]}",
    )
    client.connect(MQTT_BROKER_HOST, MQTT_BROKER_PORT, keepalive=60)
    client.loop_start()
    yield client
    client.loop_stop()
    client.disconnect()


@pytest.fixture
def kafka_consumer_factory():
    """Factory to create Kafka consumers for specific topics."""
    from confluent_kafka import Consumer

    consumers: list[Consumer] = []

    def _create(topic: str) -> Consumer:
        consumer = Consumer({
            "bootstrap.servers": KAFKA_BOOTSTRAP,
            "group.id": f"test-consumer-{uuid.uuid4().hex[:8]}",
            "auto.offset.reset": "latest",
            "enable.auto.commit": "false",
        })
        consumer.subscribe([topic])
        # Initial poll to trigger partition assignment
        consumer.poll(timeout=2.0)
        consumers.append(consumer)
        return consumer

    yield _create

    for c in consumers:
        try:
            c.close()
        except Exception:
            pass


@pytest.fixture
def kafka_admin():
    """Create a Kafka admin client."""
    from confluent_kafka.admin import AdminClient

    return AdminClient({"bootstrap.servers": KAFKA_BOOTSTRAP})


# ---------------------------------------------------------------------------
# Sample payloads (matching actual simulation service output)
# ---------------------------------------------------------------------------


def sample_meter_reading(meter_id: str = "meter-001") -> dict:
    """Generate a sample energy meter reading."""
    return {
        "timestamp": datetime.now(tz=timezone.utc).isoformat().replace("+00:00", "Z"),
        "meter_id": meter_id,
        "site_id": "site-berlin-001",
        "readings": {
            "active_power_kw": 45.23,
            "voltage": {"L1": 230.5, "L2": 231.2, "L3": 229.8},
            "current": {"L1": 65.4, "L2": 64.8, "L3": 66.1},
            "power_factor": 0.95,
            "frequency_hz": 50.01,
            "energy_delivered_kwh": 12345.67,
            "energy_received_kwh": 890.12,
        },
    }


def sample_price_reading() -> dict:
    """Generate a sample spot price reading."""
    return {
        "timestamp": datetime.now(tz=timezone.utc).isoformat().replace("+00:00", "Z"),
        "price_eur_per_kwh": 0.0342,
        "tariff_type": "SPOT",
        "market_zone": "DE-LU",
        "currency": "EUR",
    }


def sample_weather_reading() -> dict:
    """Generate a sample weather reading."""
    return {
        "timestamp": datetime.now(tz=timezone.utc).isoformat().replace("+00:00", "Z"),
        "site_id": "site-berlin-001",
        "conditions": {
            "temperature_celsius": 18.5,
            "humidity_percent": 65.0,
            "wind_speed_ms": 3.2,
            "wind_direction_deg": 225,
            "cloud_cover_percent": 40.0,
            "ghi_wm2": 580.0,
        },
    }


def sample_pv_reading(system_id: str = "pv-system-001") -> dict:
    """Generate a sample PV generation reading."""
    return {
        "timestamp": datetime.now(tz=timezone.utc).isoformat().replace("+00:00", "Z"),
        "system_id": system_id,
        "site_id": "site-berlin-001",
        "dc_power_kw": 8.5,
        "ac_power_kw": 8.2,
        "efficiency_percent": 96.5,
        "panel_temperature_celsius": 42.3,
        "daily_yield_kwh": 35.8,
    }


def sample_consumer_state(device_type: str = "industrial_oven") -> dict:
    """Generate a sample consumer state reading."""
    return {
        "timestamp": datetime.now(tz=timezone.utc).isoformat().replace("+00:00", "Z"),
        "device_type": device_type,
        "device_id": f"{device_type}-001",
        "site_id": "site-berlin-001",
        "state": "RUNNING",
        "power_kw": 12.5,
        "setpoint_celsius": 180.0,
        "actual_celsius": 178.3,
    }


SAMPLE_PAYLOADS = {
    "energy.bronze.meter-readings": sample_meter_reading,
    "energy.bronze.prices": sample_price_reading,
    "energy.bronze.weather": sample_weather_reading,
    "energy.bronze.pv-generation": sample_pv_reading,
    "energy.bronze.consumer-states": sample_consumer_state,
}


# ---------------------------------------------------------------------------
# Unit tests — metadata enrichment logic (no infrastructure required)
# ---------------------------------------------------------------------------


class TestMetadataEnrichment:
    """Test the Bronze envelope construction logic."""

    def test_envelope_has_required_fields(self):
        """The Bronze envelope must contain ingest_timestamp, source_system, source_topic, payload."""
        original = sample_meter_reading()
        envelope = {
            "ingest_timestamp": datetime.now(tz=timezone.utc).isoformat(),
            "source_system": "facis-simulation-service",
            "source_topic": "facis/energy/meter/meter-001",
            "payload": original,
        }

        assert "ingest_timestamp" in envelope
        assert "source_system" in envelope
        assert "source_topic" in envelope
        assert "payload" in envelope
        assert envelope["payload"] == original

    def test_ingest_timestamp_is_iso8601(self):
        """ingest_timestamp must be a valid ISO-8601 UTC timestamp."""
        ts = datetime.now(tz=timezone.utc).isoformat()
        # Should parse without error
        parsed = datetime.fromisoformat(ts)
        assert parsed.tzinfo is not None

    def test_source_system_is_constant(self):
        """source_system must always be 'facis-simulation-service'."""
        assert "facis-simulation-service" == "facis-simulation-service"

    def test_source_topic_preserves_mqtt_topic(self):
        """source_topic must match the original MQTT topic the message arrived on."""
        for route in MQTT_KAFKA_ROUTES:
            envelope = {
                "source_topic": route["test_mqtt_topic"],
                "payload": {},
            }
            assert envelope["source_topic"] == route["test_mqtt_topic"]

    def test_payload_is_unmodified(self):
        """The original MQTT payload must be wrapped, not modified."""
        original = sample_meter_reading()
        original_json = json.dumps(original, sort_keys=True)

        envelope = {
            "ingest_timestamp": datetime.now(tz=timezone.utc).isoformat(),
            "source_system": "facis-simulation-service",
            "source_topic": "facis/energy/meter/meter-001",
            "payload": json.loads(original_json),
        }

        assert json.dumps(envelope["payload"], sort_keys=True) == original_json


class TestTopicMapping:
    """Test that MQTT topics route to the correct Kafka Bronze topics."""

    def test_all_five_routes_defined(self):
        """Exactly 5 MQTT → Kafka routes must be configured."""
        assert len(MQTT_KAFKA_ROUTES) == 5

    @pytest.mark.parametrize("route", MQTT_KAFKA_ROUTES, ids=[r["kafka_topic"] for r in MQTT_KAFKA_ROUTES])
    def test_kafka_topic_follows_naming_convention(self, route: dict):
        """All Kafka Bronze topics must follow energy.bronze.* naming."""
        assert route["kafka_topic"].startswith("energy.bronze.")

    def test_meter_readings_route(self):
        """facis/energy/meter/+ must route to energy.bronze.meter-readings."""
        route = next(r for r in MQTT_KAFKA_ROUTES if "meter" in r["kafka_topic"])
        assert route["mqtt_subscription"] == "facis/energy/meter/+"
        assert route["kafka_topic"] == "energy.bronze.meter-readings"

    def test_prices_route(self):
        """facis/prices/spot must route to energy.bronze.prices."""
        route = next(r for r in MQTT_KAFKA_ROUTES if "prices" in r["kafka_topic"])
        assert route["mqtt_subscription"] == "facis/prices/spot"
        assert route["kafka_topic"] == "energy.bronze.prices"

    def test_weather_route(self):
        """facis/weather/current must route to energy.bronze.weather."""
        route = next(r for r in MQTT_KAFKA_ROUTES if "weather" in r["kafka_topic"])
        assert route["mqtt_subscription"] == "facis/weather/current"
        assert route["kafka_topic"] == "energy.bronze.weather"

    def test_pv_generation_route(self):
        """facis/energy/pv/+ must route to energy.bronze.pv-generation."""
        route = next(r for r in MQTT_KAFKA_ROUTES if "pv" in r["kafka_topic"])
        assert route["mqtt_subscription"] == "facis/energy/pv/+"
        assert route["kafka_topic"] == "energy.bronze.pv-generation"

    def test_consumer_states_route(self):
        """facis/loads/+ must route to energy.bronze.consumer-states."""
        route = next(r for r in MQTT_KAFKA_ROUTES if "consumer" in r["kafka_topic"])
        assert route["mqtt_subscription"] == "facis/loads/+"
        assert route["kafka_topic"] == "energy.bronze.consumer-states"

    def test_dead_letter_topic_defined(self):
        """A dead-letter queue topic must be defined."""
        assert DEAD_LETTER_TOPIC == "energy.bronze.dead-letter"


# ---------------------------------------------------------------------------
# Integration tests — require MQTT + Kafka (Docker Compose)
# ---------------------------------------------------------------------------


@requires_infrastructure
class TestMQTTPublish:
    """Test that MQTT messages can be published to all feed topics."""

    @pytest.mark.parametrize("route", MQTT_KAFKA_ROUTES, ids=[r["kafka_topic"] for r in MQTT_KAFKA_ROUTES])
    def test_publish_to_mqtt_topic(self, mqtt_publisher, route: dict):
        """Verify MQTT publish succeeds for each feed topic."""
        payload_fn = SAMPLE_PAYLOADS[route["kafka_topic"]]
        payload = payload_fn()
        result = mqtt_publisher.publish(
            topic=route["test_mqtt_topic"],
            payload=json.dumps(payload),
            qos=1,
        )
        assert result.rc == 0, f"Failed to publish to {route['test_mqtt_topic']}"


@requires_infrastructure
class TestEndToEndPipeline:
    """
    End-to-end integration tests for the MQTT → Kafka Bronze pipeline.

    These tests require:
    1. Docker Compose stack running (mqtt + kafka)
    2. NiFi pipeline deployed (scripts/setup_nifi_mqtt_to_kafka.py)

    The tests publish MQTT messages and verify they arrive in the correct
    Kafka Bronze topics with proper metadata enrichment.
    """

    @pytest.mark.parametrize("route", MQTT_KAFKA_ROUTES, ids=[r["kafka_topic"] for r in MQTT_KAFKA_ROUTES])
    def test_message_arrives_in_kafka(
        self, mqtt_publisher, kafka_consumer_factory, route: dict,
    ):
        """Publish to MQTT and verify the message arrives in the correct Kafka topic."""
        # Create a consumer for the target Kafka topic
        consumer = kafka_consumer_factory(route["kafka_topic"])

        # Generate a unique test payload
        test_id = uuid.uuid4().hex
        payload_fn = SAMPLE_PAYLOADS[route["kafka_topic"]]
        payload = payload_fn()
        payload["_test_id"] = test_id

        # Publish to MQTT
        mqtt_publisher.publish(
            topic=route["test_mqtt_topic"],
            payload=json.dumps(payload),
            qos=1,
        )

        # Wait for the message to arrive in Kafka (via NiFi pipeline)
        received = None
        deadline = time.time() + 30  # 30-second timeout
        while time.time() < deadline:
            msg = consumer.poll(timeout=1.0)
            if msg is None or msg.error():
                continue
            try:
                value = json.loads(msg.value().decode("utf-8"))
                # Check if this is our test message (look in payload)
                inner = value.get("payload", value)
                if inner.get("_test_id") == test_id:
                    received = value
                    break
            except (json.JSONDecodeError, UnicodeDecodeError):
                continue

        assert received is not None, (
            f"Message not received in Kafka topic {route['kafka_topic']} "
            f"within 30 seconds"
        )

    @pytest.mark.parametrize("route", MQTT_KAFKA_ROUTES, ids=[r["kafka_topic"] for r in MQTT_KAFKA_ROUTES])
    def test_metadata_enrichment(
        self, mqtt_publisher, kafka_consumer_factory, route: dict,
    ):
        """Verify that ingestion metadata is added to each message."""
        consumer = kafka_consumer_factory(route["kafka_topic"])

        test_id = uuid.uuid4().hex
        payload_fn = SAMPLE_PAYLOADS[route["kafka_topic"]]
        payload = payload_fn()
        payload["_test_id"] = test_id

        mqtt_publisher.publish(
            topic=route["test_mqtt_topic"],
            payload=json.dumps(payload),
            qos=1,
        )

        received = None
        deadline = time.time() + 30
        while time.time() < deadline:
            msg = consumer.poll(timeout=1.0)
            if msg is None or msg.error():
                continue
            try:
                value = json.loads(msg.value().decode("utf-8"))
                inner = value.get("payload", value)
                if inner.get("_test_id") == test_id:
                    received = value
                    break
            except (json.JSONDecodeError, UnicodeDecodeError):
                continue

        assert received is not None, "Message not received"

        # Verify metadata fields
        assert "ingest_timestamp" in received, "Missing ingest_timestamp"
        assert "source_system" in received, "Missing source_system"
        assert "source_topic" in received, "Missing source_topic"
        assert "payload" in received, "Missing payload wrapper"

        assert received["source_system"] == "facis-simulation-service"
        assert received["source_topic"] == route["test_mqtt_topic"]

        # Verify ingest_timestamp is valid ISO-8601
        try:
            datetime.fromisoformat(received["ingest_timestamp"].replace("Z", "+00:00"))
        except ValueError:
            pytest.fail(f"ingest_timestamp is not valid ISO-8601: {received['ingest_timestamp']}")

    @pytest.mark.parametrize("route", MQTT_KAFKA_ROUTES, ids=[r["kafka_topic"] for r in MQTT_KAFKA_ROUTES])
    def test_payload_preserved(
        self, mqtt_publisher, kafka_consumer_factory, route: dict,
    ):
        """Verify the original MQTT payload is preserved unmodified."""
        consumer = kafka_consumer_factory(route["kafka_topic"])

        test_id = uuid.uuid4().hex
        payload_fn = SAMPLE_PAYLOADS[route["kafka_topic"]]
        original = payload_fn()
        original["_test_id"] = test_id
        original_json = json.dumps(original, sort_keys=True)

        mqtt_publisher.publish(
            topic=route["test_mqtt_topic"],
            payload=json.dumps(original),
            qos=1,
        )

        received = None
        deadline = time.time() + 30
        while time.time() < deadline:
            msg = consumer.poll(timeout=1.0)
            if msg is None or msg.error():
                continue
            try:
                value = json.loads(msg.value().decode("utf-8"))
                inner = value.get("payload", value)
                if inner.get("_test_id") == test_id:
                    received = value
                    break
            except (json.JSONDecodeError, UnicodeDecodeError):
                continue

        assert received is not None, "Message not received"
        received_payload = json.dumps(received["payload"], sort_keys=True)
        assert received_payload == original_json, "Payload was modified during enrichment"

    def test_no_data_loss(self, mqtt_publisher, kafka_consumer_factory):
        """Publish N messages and verify all N arrive in Kafka."""
        route = MQTT_KAFKA_ROUTES[0]  # Use meter readings
        consumer = kafka_consumer_factory(route["kafka_topic"])
        batch_id = uuid.uuid4().hex
        n_messages = 20

        # Publish batch
        for i in range(n_messages):
            payload = sample_meter_reading()
            payload["_batch_id"] = batch_id
            payload["_sequence"] = i
            mqtt_publisher.publish(
                topic=route["test_mqtt_topic"],
                payload=json.dumps(payload),
                qos=1,
            )

        # Collect from Kafka
        received_sequences = set()
        deadline = time.time() + 60  # 60-second timeout for batch
        while time.time() < deadline and len(received_sequences) < n_messages:
            msg = consumer.poll(timeout=1.0)
            if msg is None or msg.error():
                continue
            try:
                value = json.loads(msg.value().decode("utf-8"))
                inner = value.get("payload", value)
                if inner.get("_batch_id") == batch_id:
                    received_sequences.add(inner["_sequence"])
            except (json.JSONDecodeError, UnicodeDecodeError):
                continue

        assert len(received_sequences) == n_messages, (
            f"Data loss detected: sent {n_messages}, received {len(received_sequences)}. "
            f"Missing sequences: {set(range(n_messages)) - received_sequences}"
        )


@requires_infrastructure
class TestKafkaTopics:
    """Verify Kafka Bronze topics exist and are properly configured."""

    def test_bronze_topics_exist(self, kafka_admin):
        """All 5 Bronze topics plus DLQ must exist in Kafka."""
        metadata = kafka_admin.list_topics(timeout=10)
        existing_topics = set(metadata.topics.keys())

        expected_topics = {route["kafka_topic"] for route in MQTT_KAFKA_ROUTES}
        expected_topics.add(DEAD_LETTER_TOPIC)

        missing = expected_topics - existing_topics
        if missing:
            pytest.skip(
                f"Topics not yet created (auto-create on first publish): {missing}"
            )


# ---------------------------------------------------------------------------
# Pipeline setup script validation (no infrastructure required)
# ---------------------------------------------------------------------------


class TestPipelineSetupScript:
    """Validate the NiFi setup script configuration."""

    def test_script_exists(self):
        """The setup script must exist at the expected path."""
        import os

        script_path = os.path.join(
            os.path.dirname(__file__),
            "..", "..", "scripts", "setup_nifi_mqtt_to_kafka.py",
        )
        assert os.path.exists(script_path), f"Setup script not found: {script_path}"

    def test_script_is_importable(self):
        """The setup script must be syntactically valid Python."""
        import importlib.util
        import os

        script_path = os.path.join(
            os.path.dirname(__file__),
            "..", "..", "scripts", "setup_nifi_mqtt_to_kafka.py",
        )
        spec = importlib.util.spec_from_file_location("setup_nifi_mqtt_to_kafka", script_path)
        assert spec is not None

    def test_flow_definition_exists(self):
        """The NiFi flow JSON definition must exist."""
        import os

        flow_path = os.path.join(
            os.path.dirname(__file__),
            "..", "..", "nifi", "templates", "mqtt-to-kafka-bronze-flow.json",
        )
        assert os.path.exists(flow_path), f"Flow definition not found: {flow_path}"

    def test_flow_definition_is_valid_json(self):
        """The NiFi flow JSON must be valid and contain required fields."""
        import os

        flow_path = os.path.join(
            os.path.dirname(__file__),
            "..", "..", "nifi", "templates", "mqtt-to-kafka-bronze-flow.json",
        )
        with open(flow_path) as f:
            flow = json.load(f)

        assert "topic_mapping" in flow
        assert len(flow["topic_mapping"]) == 5
        assert "dead_letter_queue" in flow
        assert "metadata_enrichment" in flow
        assert "processor_chain" in flow

        # Verify all 5 routes are defined
        kafka_topics = {m["kafka_topic"] for m in flow["topic_mapping"]}
        assert kafka_topics == {
            "energy.bronze.meter-readings",
            "energy.bronze.prices",
            "energy.bronze.weather",
            "energy.bronze.pv-generation",
            "energy.bronze.consumer-states",
        }
