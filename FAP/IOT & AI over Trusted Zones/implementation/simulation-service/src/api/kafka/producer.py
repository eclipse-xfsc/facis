"""
Kafka data producer.

Publishes simulation data to Kafka topics using confluent-kafka.
"""

from __future__ import annotations

import json
import logging
import threading
from dataclasses import dataclass
from datetime import datetime
from typing import TYPE_CHECKING, Any

from confluent_kafka import KafkaError, Producer

from src.api.kafka.topics import KafkaTopics

if TYPE_CHECKING:
    from src.config import KafkaConfig

logger = logging.getLogger(__name__)


@dataclass
class PublishResult:
    """Result of a Kafka publish operation."""

    success: bool
    topic: str
    error: str | None = None


class KafkaPublisher:
    """
    Kafka producer with delivery confirmation and error handling.

    Features:
    - Synchronous-style publishing with delivery callbacks
    - JSON payload encoding
    - Key-based partitioning (by asset_id/meter_id)
    - Thread-safe publishing
    - Periodic poll for delivery reports
    """

    def __init__(
        self,
        bootstrap_servers: str = "localhost:9092",
        client_id: str = "facis-simulator",
        security_protocol: str = "PLAINTEXT",
        ssl_ca_location: str | None = None,
        ssl_certificate_location: str | None = None,
        ssl_key_location: str | None = None,
    ) -> None:
        """
        Initialize Kafka producer.

        Args:
            bootstrap_servers: Comma-separated Kafka broker addresses.
            client_id: Producer client identifier.
            security_protocol: PLAINTEXT or SSL.
            ssl_ca_location: Path to CA certificate for TLS.
            ssl_certificate_location: Path to client certificate for TLS.
            ssl_key_location: Path to client private key for TLS.
        """
        self._bootstrap_servers = bootstrap_servers
        self._client_id = client_id
        self._security_protocol = security_protocol
        self._ssl_ca_location = ssl_ca_location
        self._ssl_certificate_location = ssl_certificate_location
        self._ssl_key_location = ssl_key_location
        self._producer: Producer | None = None
        self._lock = threading.Lock()
        self._delivery_errors: list[str] = []

    @classmethod
    def from_config(cls, config: KafkaConfig) -> KafkaPublisher:
        """Create publisher from configuration object."""
        return cls(
            bootstrap_servers=config.bootstrap_servers,
            client_id=config.client_id,
            security_protocol=config.security_protocol,
            ssl_ca_location=config.ssl_ca_location,
            ssl_certificate_location=config.ssl_certificate_location,
            ssl_key_location=config.ssl_key_location,
        )

    @property
    def is_connected(self) -> bool:
        """Check if producer is initialized."""
        return self._producer is not None

    def _delivery_callback(self, err: KafkaError | None, msg: Any) -> None:
        """Handle delivery confirmation from Kafka broker."""
        if err is not None:
            error_msg = f"Delivery failed for {msg.topic()}: {err}"
            logger.error(error_msg)
            self._delivery_errors.append(error_msg)
        else:
            logger.debug(f"Delivered to {msg.topic()} [{msg.partition()}] @ offset {msg.offset()}")

    def connect(self) -> bool:
        """
        Initialize the Kafka producer.

        Returns:
            True if producer was created successfully.
        """
        try:
            config = {
                "bootstrap.servers": self._bootstrap_servers,
                "client.id": self._client_id,
                "acks": "all",
                "retries": 3,
                "retry.backoff.ms": 500,
                "linger.ms": 5,
                "batch.size": 16384,
            }
            if self._security_protocol == "SSL":
                config["security.protocol"] = "SSL"
                if self._ssl_ca_location:
                    config["ssl.ca.location"] = self._ssl_ca_location
                if self._ssl_certificate_location:
                    config["ssl.certificate.location"] = self._ssl_certificate_location
                if self._ssl_key_location:
                    config["ssl.key.location"] = self._ssl_key_location
                logger.info("Kafka producer configured with TLS/SSL")

            self._producer = Producer(config)
            logger.info(f"Kafka producer initialized for {self._bootstrap_servers}")
            return True
        except Exception as e:
            logger.error(f"Failed to create Kafka producer: {e}")
            return False

    def disconnect(self) -> None:
        """Flush pending messages and close the producer."""
        if self._producer is not None:
            try:
                remaining = self._producer.flush(timeout=10.0)
                if remaining > 0:
                    logger.warning(f"{remaining} messages were not delivered on shutdown")
            except Exception as e:
                logger.error(f"Error flushing Kafka producer: {e}")
            self._producer = None
            logger.info("Kafka producer disconnected")

    def publish(
        self,
        topic: str,
        payload: dict,
        key: str | None = None,
    ) -> PublishResult:
        """
        Publish a message to a Kafka topic.

        Args:
            topic: Kafka topic name.
            payload: Message payload (will be JSON-encoded).
            key: Optional message key for partitioning.

        Returns:
            PublishResult with success status.
        """
        if self._producer is None:
            return PublishResult(
                success=False,
                topic=topic,
                error="Producer not initialized",
            )

        try:
            payload_bytes = json.dumps(payload).encode("utf-8")
            key_bytes = key.encode("utf-8") if key else None

            with self._lock:
                self._producer.produce(
                    topic=topic,
                    value=payload_bytes,
                    key=key_bytes,
                    callback=self._delivery_callback,
                )
                # Trigger delivery report callbacks
                self._producer.poll(0)

            return PublishResult(success=True, topic=topic)
        except BufferError:
            # Local queue is full, flush and retry
            logger.warning(f"Producer queue full for {topic}, flushing...")
            self._producer.flush(timeout=5.0)
            try:
                self._producer.produce(
                    topic=topic,
                    value=payload_bytes,
                    key=key_bytes,
                    callback=self._delivery_callback,
                )
                return PublishResult(success=True, topic=topic)
            except Exception as e:
                return PublishResult(success=False, topic=topic, error=str(e))
        except Exception as e:
            logger.error(f"Error publishing to {topic}: {e}")
            return PublishResult(success=False, topic=topic, error=str(e))

    def flush(self, timeout: float = 5.0) -> int:
        """
        Flush pending messages.

        Args:
            timeout: Maximum time to wait in seconds.

        Returns:
            Number of messages still in queue after flush.
        """
        if self._producer is None:
            return 0
        return self._producer.flush(timeout=timeout)

    # =========================================================================
    # Feed-specific publish methods
    # =========================================================================

    def publish_meter_reading(self, meter_id: str, reading: dict) -> PublishResult:
        """Publish an energy meter reading."""
        return self.publish(
            topic=KafkaTopics.METER,
            payload=reading,
            key=meter_id,
        )

    def publish_pv_reading(self, system_id: str, reading: dict) -> PublishResult:
        """Publish a PV generation reading."""
        return self.publish(
            topic=KafkaTopics.PV,
            payload=reading,
            key=system_id,
        )

    def publish_weather(self, reading: dict) -> PublishResult:
        """Publish weather conditions."""
        return self.publish(
            topic=KafkaTopics.WEATHER,
            payload=reading,
            key=reading.get("site_id", "default"),
        )

    def publish_spot_price(self, reading: dict) -> PublishResult:
        """Publish current spot price."""
        return self.publish(
            topic=KafkaTopics.PRICE,
            payload=reading,
        )

    def publish_consumer_load(self, device_id: str, reading: dict) -> PublishResult:
        """Publish consumer load data."""
        return self.publish(
            topic=KafkaTopics.CONSUMER,
            payload=reading,
            key=device_id,
        )

    def publish_streetlight(self, light_id: str, reading: dict) -> PublishResult:
        """Publish streetlight telemetry."""
        return self.publish(
            topic=KafkaTopics.LIGHT,
            payload=reading,
            key=light_id,
        )

    def publish_traffic(self, zone_id: str, reading: dict) -> PublishResult:
        """Publish traffic/movement data."""
        return self.publish(
            topic=KafkaTopics.TRAFFIC,
            payload=reading,
            key=zone_id,
        )

    def publish_city_event(self, zone_id: str, reading: dict) -> PublishResult:
        """Publish city event data."""
        return self.publish(
            topic=KafkaTopics.EVENT,
            payload=reading,
            key=zone_id,
        )

    def publish_city_weather(self, city_id: str, reading: dict) -> PublishResult:
        """Publish city weather/visibility data."""
        return self.publish(
            topic=KafkaTopics.CITY_WEATHER,
            payload=reading,
            key=city_id,
        )


class KafkaFeedPublisher:
    """
    High-level Kafka feed publisher that integrates with SimulationState.

    Publishes all simulation feeds to their respective Kafka topics.
    """

    def __init__(self, publisher: KafkaPublisher) -> None:
        """
        Initialize feed publisher.

        Args:
            publisher: Underlying Kafka publisher.
        """
        self._publisher = publisher

    def publish_all_feeds(
        self,
        meters: dict[str, Any],
        pv_systems: dict[str, Any],
        weather_stations: dict[str, Any],
        price_feeds: dict[str, Any],
        loads: dict[str, Any],
        simulation_time: datetime,
    ) -> dict[str, list[PublishResult]]:
        """
        Publish all Smart Energy feeds at the current simulation time.

        Args:
            meters: Dict of meter_id -> EnergyMeterSimulator.
            pv_systems: Dict of system_id -> PVGenerationSimulator.
            weather_stations: Dict of station_id -> WeatherSimulator.
            price_feeds: Dict of feed_id -> EnergyPriceSimulator.
            loads: Dict of device_id -> ConsumerLoadSimulator.
            simulation_time: Current simulation timestamp.

        Returns:
            Dict mapping feed type to list of PublishResults.
        """
        results: dict[str, list[PublishResult]] = {
            "meters": [],
            "pv": [],
            "weather": [],
            "prices": [],
            "loads": [],
        }

        for meter_id, simulator in meters.items():
            reading = simulator.generate_at(simulation_time)
            if reading and reading.value:
                payload = reading.value.to_json_payload()
                result = self._publisher.publish_meter_reading(meter_id, payload)
                results["meters"].append(result)

        for system_id, simulator in pv_systems.items():
            reading = simulator.generate_at(simulation_time)
            if reading and reading.value:
                payload = reading.value.to_json_payload()
                result = self._publisher.publish_pv_reading(system_id, payload)
                results["pv"].append(result)

        for station_id, simulator in weather_stations.items():
            reading = simulator.generate_at(simulation_time)
            if reading and reading.value:
                payload = reading.value.to_json_payload()
                result = self._publisher.publish_weather(payload)
                results["weather"].append(result)
            break  # Only publish from first station

        for feed_id, simulator in price_feeds.items():
            reading = simulator.generate_at(simulation_time)
            if reading and reading.value:
                payload = reading.value.to_json_payload()
                result = self._publisher.publish_spot_price(payload)
                results["prices"].append(result)
            break  # Only publish from first feed

        for device_id, simulator in loads.items():
            reading = simulator.generate_at(simulation_time)
            if reading and reading.value:
                payload = reading.value.to_json_payload()
                result = self._publisher.publish_consumer_load(device_id, payload)
                results["loads"].append(result)

        # Flush to ensure delivery
        self._publisher.flush()

        return results
