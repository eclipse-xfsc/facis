"""Tests for KafkaPublisher with mocked confluent_kafka.Producer.

All tests mock the underlying confluent_kafka.Producer so no running
Kafka broker is required.
"""

import json
from unittest.mock import MagicMock, patch

import pytest

from src.api.kafka.producer import KafkaPublisher, PublishResult
from src.api.kafka.topics import KafkaTopics
from src.config import KafkaConfig

SAMPLE_PAYLOAD = {
    "type": "energy_meter",
    "schema_version": "1.0",
    "site_id": "site-berlin-001",
    "asset_id": "meter-001",
    "timestamp": "2026-02-15T10:30:00Z",
    "active_power_kw": 9.8,
}


class TestKafkaPublisherInit:
    """Tests for KafkaPublisher initialization."""

    def test_default_init(self) -> None:
        """Test publisher initializes with default bootstrap_servers and client_id."""
        publisher = KafkaPublisher()
        assert publisher._bootstrap_servers == "localhost:9092"
        assert publisher._client_id == "facis-simulator"
        assert publisher._producer is None

    def test_custom_init(self) -> None:
        """Test publisher initializes with custom parameters."""
        publisher = KafkaPublisher(
            bootstrap_servers="broker-1:9092,broker-2:9092",
            client_id="test-producer",
        )
        assert publisher._bootstrap_servers == "broker-1:9092,broker-2:9092"
        assert publisher._client_id == "test-producer"

    def test_from_config(self) -> None:
        """Test publisher is created correctly from KafkaConfig."""
        config = KafkaConfig(
            bootstrap_servers="kafka.example.com:9092",
            client_id="integration-test",
        )
        publisher = KafkaPublisher.from_config(config)
        assert publisher._bootstrap_servers == "kafka.example.com:9092"
        assert publisher._client_id == "integration-test"

    def test_is_connected_false_before_connect(self) -> None:
        """Test is_connected returns False before connect() is called."""
        publisher = KafkaPublisher()
        assert publisher.is_connected is False


class TestKafkaPublisherConnect:
    """Tests for KafkaPublisher.connect()."""

    @patch("src.api.kafka.producer.Producer")
    def test_connect_creates_producer(self, mock_producer_cls: MagicMock) -> None:
        """Test connect() creates a confluent_kafka.Producer instance."""
        publisher = KafkaPublisher(bootstrap_servers="broker:9092", client_id="test")
        result = publisher.connect()

        assert result is True
        assert publisher.is_connected is True
        mock_producer_cls.assert_called_once()
        call_kwargs = mock_producer_cls.call_args[0][0]
        assert call_kwargs["bootstrap.servers"] == "broker:9092"
        assert call_kwargs["client.id"] == "test"

    @patch("src.api.kafka.producer.Producer", side_effect=Exception("Broker unreachable"))
    def test_connect_returns_false_on_failure(self, mock_producer_cls: MagicMock) -> None:
        """Test connect() returns False when Producer creation fails."""
        publisher = KafkaPublisher()
        result = publisher.connect()

        assert result is False
        assert publisher.is_connected is False


class TestKafkaPublisherPublish:
    """Tests for KafkaPublisher.publish()."""

    @patch("src.api.kafka.producer.Producer")
    def test_publish_calls_produce(self, mock_producer_cls: MagicMock) -> None:
        """Test publish() calls producer.produce() with correct topic, key, and value."""
        mock_producer = MagicMock()
        mock_producer_cls.return_value = mock_producer

        publisher = KafkaPublisher()
        publisher.connect()
        result = publisher.publish(
            topic="sim.smart_energy.meter",
            payload=SAMPLE_PAYLOAD,
            key="meter-001",
        )

        assert result.success is True
        assert result.topic == "sim.smart_energy.meter"

        mock_producer.produce.assert_called_once()
        call_kwargs = mock_producer.produce.call_args[1]
        assert call_kwargs["topic"] == "sim.smart_energy.meter"
        assert call_kwargs["key"] == b"meter-001"
        assert call_kwargs["value"] == json.dumps(SAMPLE_PAYLOAD).encode("utf-8")

    @patch("src.api.kafka.producer.Producer")
    def test_publish_without_key(self, mock_producer_cls: MagicMock) -> None:
        """Test publish() works without a message key."""
        mock_producer = MagicMock()
        mock_producer_cls.return_value = mock_producer

        publisher = KafkaPublisher()
        publisher.connect()
        result = publisher.publish(topic="sim.smart_energy.price", payload=SAMPLE_PAYLOAD)

        assert result.success is True
        call_kwargs = mock_producer.produce.call_args[1]
        assert call_kwargs["key"] is None

    def test_publish_fails_when_not_connected(self) -> None:
        """Test publish() returns failure if connect() was not called."""
        publisher = KafkaPublisher()
        result = publisher.publish(topic="test-topic", payload=SAMPLE_PAYLOAD)

        assert result.success is False
        assert result.error == "Producer not initialized"

    @patch("src.api.kafka.producer.Producer")
    def test_publish_polls_for_delivery_reports(self, mock_producer_cls: MagicMock) -> None:
        """Test publish() calls producer.poll(0) after producing."""
        mock_producer = MagicMock()
        mock_producer_cls.return_value = mock_producer

        publisher = KafkaPublisher()
        publisher.connect()
        publisher.publish(topic="test-topic", payload=SAMPLE_PAYLOAD)

        mock_producer.poll.assert_called_once_with(0)


class TestKafkaPublisherDisconnect:
    """Tests for KafkaPublisher.disconnect()."""

    @patch("src.api.kafka.producer.Producer")
    def test_disconnect_flushes_producer(self, mock_producer_cls: MagicMock) -> None:
        """Test disconnect() calls producer.flush()."""
        mock_producer = MagicMock()
        mock_producer.flush.return_value = 0
        mock_producer_cls.return_value = mock_producer

        publisher = KafkaPublisher()
        publisher.connect()
        publisher.disconnect()

        mock_producer.flush.assert_called_once_with(timeout=10.0)
        assert publisher.is_connected is False

    @patch("src.api.kafka.producer.Producer")
    def test_disconnect_sets_producer_to_none(self, mock_producer_cls: MagicMock) -> None:
        """Test disconnect() clears the internal producer reference."""
        mock_producer = MagicMock()
        mock_producer.flush.return_value = 0
        mock_producer_cls.return_value = mock_producer

        publisher = KafkaPublisher()
        publisher.connect()
        assert publisher._producer is not None

        publisher.disconnect()
        assert publisher._producer is None

    def test_disconnect_noop_when_not_connected(self) -> None:
        """Test disconnect() does nothing when not connected."""
        publisher = KafkaPublisher()
        publisher.disconnect()  # Should not raise


class TestFeedSpecificPublishMethods:
    """Tests for feed-specific publish helpers (publish_meter_reading, etc.)."""

    @patch("src.api.kafka.producer.Producer")
    def test_publish_meter_reading(self, mock_producer_cls: MagicMock) -> None:
        """Test publish_meter_reading uses the correct Kafka topic."""
        mock_producer = MagicMock()
        mock_producer_cls.return_value = mock_producer

        publisher = KafkaPublisher()
        publisher.connect()
        result = publisher.publish_meter_reading("meter-001", SAMPLE_PAYLOAD)

        assert result.success is True
        call_kwargs = mock_producer.produce.call_args[1]
        assert call_kwargs["topic"] == KafkaTopics.METER
        assert call_kwargs["key"] == b"meter-001"

    @patch("src.api.kafka.producer.Producer")
    def test_publish_pv_reading(self, mock_producer_cls: MagicMock) -> None:
        """Test publish_pv_reading uses the correct Kafka topic."""
        mock_producer = MagicMock()
        mock_producer_cls.return_value = mock_producer

        publisher = KafkaPublisher()
        publisher.connect()
        result = publisher.publish_pv_reading("pv-system-001", {"type": "pv_generation"})

        assert result.success is True
        call_kwargs = mock_producer.produce.call_args[1]
        assert call_kwargs["topic"] == KafkaTopics.PV
        assert call_kwargs["key"] == b"pv-system-001"

    @patch("src.api.kafka.producer.Producer")
    def test_publish_weather(self, mock_producer_cls: MagicMock) -> None:
        """Test publish_weather uses the correct Kafka topic."""
        mock_producer = MagicMock()
        mock_producer_cls.return_value = mock_producer

        publisher = KafkaPublisher()
        publisher.connect()
        weather_payload = {"type": "weather", "site_id": "site-berlin-001"}
        result = publisher.publish_weather(weather_payload)

        assert result.success is True
        call_kwargs = mock_producer.produce.call_args[1]
        assert call_kwargs["topic"] == KafkaTopics.WEATHER
        assert call_kwargs["key"] == b"site-berlin-001"

    @patch("src.api.kafka.producer.Producer")
    def test_publish_spot_price(self, mock_producer_cls: MagicMock) -> None:
        """Test publish_spot_price uses the correct Kafka topic with no key."""
        mock_producer = MagicMock()
        mock_producer_cls.return_value = mock_producer

        publisher = KafkaPublisher()
        publisher.connect()
        result = publisher.publish_spot_price({"type": "energy_price"})

        assert result.success is True
        call_kwargs = mock_producer.produce.call_args[1]
        assert call_kwargs["topic"] == KafkaTopics.PRICE
        assert call_kwargs["key"] is None

    @patch("src.api.kafka.producer.Producer")
    def test_publish_consumer_load(self, mock_producer_cls: MagicMock) -> None:
        """Test publish_consumer_load uses the correct Kafka topic."""
        mock_producer = MagicMock()
        mock_producer_cls.return_value = mock_producer

        publisher = KafkaPublisher()
        publisher.connect()
        result = publisher.publish_consumer_load("oven-001", {"type": "consumer"})

        assert result.success is True
        call_kwargs = mock_producer.produce.call_args[1]
        assert call_kwargs["topic"] == KafkaTopics.CONSUMER
        assert call_kwargs["key"] == b"oven-001"
