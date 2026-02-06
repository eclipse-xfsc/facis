"""
MQTT data publisher.

Publishes simulation data to MQTT topics with automatic reconnection.
"""

from __future__ import annotations

import asyncio
import json
import logging
import threading
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Any

import paho.mqtt.client as mqtt

from src.api.mqtt.topics import MQTTTopics

if TYPE_CHECKING:
    from src.config import MqttConfig

logger = logging.getLogger(__name__)


class ConnectionState(str, Enum):
    """MQTT connection state."""

    DISCONNECTED = "disconnected"
    CONNECTING = "connecting"
    CONNECTED = "connected"
    RECONNECTING = "reconnecting"


@dataclass
class PublishResult:
    """Result of a publish operation."""

    success: bool
    topic: str
    message_id: int | None = None
    error: str | None = None


class MQTTPublisher:
    """
    MQTT publisher with automatic reconnection and QoS support.

    Features:
    - Automatic reconnection with exponential backoff
    - QoS 0, 1, and 2 support
    - Retained message support
    - Thread-safe publishing
    - Connection state tracking
    """

    # Reconnection settings
    RECONNECT_MIN_DELAY = 1  # seconds
    RECONNECT_MAX_DELAY = 60  # seconds
    RECONNECT_MULTIPLIER = 2

    def __init__(
        self,
        host: str = "localhost",
        port: int = 1883,
        client_id: str = "facis-simulator",
        username: str | None = None,
        password: str | None = None,
        default_qos: int = 1,
    ) -> None:
        """
        Initialize MQTT publisher.

        Args:
            host: MQTT broker hostname.
            port: MQTT broker port.
            client_id: Client identifier.
            username: Optional username for authentication.
            password: Optional password for authentication.
            default_qos: Default QoS level for publishes.
        """
        self._host = host
        self._port = port
        self._client_id = client_id
        self._username = username
        self._password = password
        self._default_qos = default_qos

        self._state = ConnectionState.DISCONNECTED
        self._reconnect_delay = self.RECONNECT_MIN_DELAY
        self._lock = threading.Lock()
        self._stop_event = threading.Event()

        # Create MQTT client (paho-mqtt 2.0+ API)
        self._client = mqtt.Client(
            callback_api_version=mqtt.CallbackAPIVersion.VERSION2,
            client_id=client_id,
            protocol=mqtt.MQTTv5,
        )

        # Set up callbacks
        self._client.on_connect = self._on_connect
        self._client.on_disconnect = self._on_disconnect
        self._client.on_publish = self._on_publish

        # Set credentials if provided
        if username and password:
            self._client.username_pw_set(username, password)

        # Enable automatic reconnect
        self._client.reconnect_delay_set(
            min_delay=self.RECONNECT_MIN_DELAY,
            max_delay=self.RECONNECT_MAX_DELAY,
        )

    @classmethod
    def from_config(cls, config: MqttConfig) -> MQTTPublisher:
        """Create publisher from configuration object."""
        return cls(
            host=config.host,
            port=config.port,
            client_id=config.client_id,
            username=config.username,
            password=config.password,
            default_qos=config.qos,
        )

    @property
    def state(self) -> ConnectionState:
        """Get current connection state."""
        return self._state

    @property
    def is_connected(self) -> bool:
        """Check if connected to broker."""
        return self._state == ConnectionState.CONNECTED

    def _on_connect(
        self,
        client: mqtt.Client,
        userdata: Any,
        flags: mqtt.ConnectFlags,
        reason_code: mqtt.ReasonCode,
        properties: mqtt.Properties | None,
    ) -> None:
        """Handle connection established."""
        if reason_code == mqtt.CONNACK_ACCEPTED or reason_code.value == 0:
            self._state = ConnectionState.CONNECTED
            self._reconnect_delay = self.RECONNECT_MIN_DELAY
            logger.info(f"Connected to MQTT broker at {self._host}:{self._port}")
        else:
            self._state = ConnectionState.DISCONNECTED
            logger.error(f"Connection failed: {reason_code}")

    def _on_disconnect(
        self,
        client: mqtt.Client,
        userdata: Any,
        disconnect_flags: mqtt.DisconnectFlags,
        reason_code: mqtt.ReasonCode,
        properties: mqtt.Properties | None,
    ) -> None:
        """Handle disconnection."""
        if self._state != ConnectionState.DISCONNECTED:
            self._state = ConnectionState.RECONNECTING
            logger.warning(f"Disconnected from MQTT broker: {reason_code}")

    def _on_publish(
        self,
        client: mqtt.Client,
        userdata: Any,
        mid: int,
        reason_codes: list[mqtt.ReasonCode],
        properties: mqtt.Properties | None,
    ) -> None:
        """Handle publish acknowledgment."""
        logger.debug(f"Message {mid} published successfully")

    def connect(self) -> bool:
        """
        Connect to the MQTT broker.

        Returns:
            True if connection initiated successfully.
        """
        try:
            self._state = ConnectionState.CONNECTING
            self._client.connect(self._host, self._port, keepalive=60)
            self._client.loop_start()
            logger.info(f"Connecting to MQTT broker at {self._host}:{self._port}...")
            return True
        except Exception as e:
            self._state = ConnectionState.DISCONNECTED
            logger.error(f"Failed to connect to MQTT broker: {e}")
            return False

    def disconnect(self) -> None:
        """Disconnect from the MQTT broker."""
        self._stop_event.set()
        self._client.loop_stop()
        self._client.disconnect()
        self._state = ConnectionState.DISCONNECTED
        logger.info("Disconnected from MQTT broker")

    def publish(
        self,
        topic: str,
        payload: dict | str,
        qos: int | None = None,
        retain: bool = False,
    ) -> PublishResult:
        """
        Publish a message to a topic.

        Args:
            topic: MQTT topic to publish to.
            payload: Message payload (dict will be JSON-encoded).
            qos: QoS level (0, 1, or 2). Uses default if None.
            retain: Whether to retain the message.

        Returns:
            PublishResult with success status and details.
        """
        if qos is None:
            qos = self._default_qos

        # Encode payload
        if isinstance(payload, dict):
            payload_str = json.dumps(payload)
        else:
            payload_str = str(payload)

        if not self.is_connected:
            logger.warning(f"Cannot publish to {topic}: not connected")
            return PublishResult(
                success=False,
                topic=topic,
                error="Not connected to broker",
            )

        try:
            with self._lock:
                result = self._client.publish(
                    topic=topic,
                    payload=payload_str,
                    qos=qos,
                    retain=retain,
                )

            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                logger.debug(f"Published to {topic} (QoS={qos}, retain={retain})")
                return PublishResult(
                    success=True,
                    topic=topic,
                    message_id=result.mid,
                )
            else:
                error = mqtt.error_string(result.rc)
                logger.error(f"Failed to publish to {topic}: {error}")
                return PublishResult(
                    success=False,
                    topic=topic,
                    error=error,
                )
        except Exception as e:
            logger.error(f"Error publishing to {topic}: {e}")
            return PublishResult(
                success=False,
                topic=topic,
                error=str(e),
            )

    # =========================================================================
    # Feed-specific publish methods
    # =========================================================================

    def publish_meter_reading(self, meter_id: str, reading: dict) -> PublishResult:
        """
        Publish an energy meter reading.

        Args:
            meter_id: Meter identifier.
            reading: Meter reading payload (from MeterReading.to_json_payload()).

        Returns:
            PublishResult.
        """
        topic = MQTTTopics.meter_topic(meter_id)
        return self.publish(
            topic=topic,
            payload=reading,
            qos=MQTTTopics.METER.qos,
            retain=MQTTTopics.METER.retained,
        )

    def publish_pv_reading(self, system_id: str, reading: dict) -> PublishResult:
        """
        Publish a PV generation reading.

        Args:
            system_id: PV system identifier.
            reading: PV reading payload (from PVReading.to_json_payload()).

        Returns:
            PublishResult.
        """
        topic = MQTTTopics.pv_topic(system_id)
        return self.publish(
            topic=topic,
            payload=reading,
            qos=MQTTTopics.PV.qos,
            retain=MQTTTopics.PV.retained,
        )

    def publish_weather(self, reading: dict) -> PublishResult:
        """
        Publish weather conditions.

        Args:
            reading: Weather reading payload (from WeatherReading.to_json_payload()).

        Returns:
            PublishResult.
        """
        return self.publish(
            topic=MQTTTopics.weather_topic(),
            payload=reading,
            qos=MQTTTopics.WEATHER.qos,
            retain=MQTTTopics.WEATHER.retained,
        )

    def publish_spot_price(self, reading: dict) -> PublishResult:
        """
        Publish current spot price.

        Args:
            reading: Price reading payload (from PriceReading.to_json_payload()).

        Returns:
            PublishResult.
        """
        return self.publish(
            topic=MQTTTopics.spot_price_topic(),
            payload=reading,
            qos=MQTTTopics.PRICE_SPOT.qos,
            retain=MQTTTopics.PRICE_SPOT.retained,
        )

    def publish_price_forecast(self, forecast: dict) -> PublishResult:
        """
        Publish price forecast.

        Args:
            forecast: Price forecast payload with list of future prices.

        Returns:
            PublishResult.
        """
        return self.publish(
            topic=MQTTTopics.forecast_price_topic(),
            payload=forecast,
            qos=MQTTTopics.PRICE_FORECAST.qos,
            retain=MQTTTopics.PRICE_FORECAST.retained,
        )

    def publish_load(self, device_type: str, reading: dict) -> PublishResult:
        """
        Publish consumer load data.

        Args:
            device_type: Type of device (e.g., 'industrial_oven', 'hvac').
            reading: Load reading payload (from ConsumerLoadReading.to_json_payload()).

        Returns:
            PublishResult.
        """
        topic = MQTTTopics.load_topic(device_type)
        return self.publish(
            topic=topic,
            payload=reading,
            qos=MQTTTopics.LOAD.qos,
            retain=MQTTTopics.LOAD.retained,
        )

    def publish_alert(self, alert: dict) -> PublishResult:
        """
        Publish a system alert.

        Args:
            alert: Alert payload with severity, message, and metadata.

        Returns:
            PublishResult.
        """
        return self.publish(
            topic=MQTTTopics.alerts_topic(),
            payload=alert,
            qos=MQTTTopics.ALERTS.qos,
            retain=MQTTTopics.ALERTS.retained,
        )

    def publish_simulation_status(self, status: dict) -> PublishResult:
        """
        Publish simulation status.

        Args:
            status: Simulation status payload.

        Returns:
            PublishResult.
        """
        return self.publish(
            topic=MQTTTopics.simulation_status_topic(),
            payload=status,
            qos=MQTTTopics.SIMULATION_STATUS.qos,
            retain=MQTTTopics.SIMULATION_STATUS.retained,
        )


class MQTTFeedPublisher:
    """
    High-level MQTT feed publisher that integrates with SimulationState.

    Publishes all simulation feeds to their respective MQTT topics.
    """

    def __init__(self, publisher: MQTTPublisher) -> None:
        """
        Initialize feed publisher.

        Args:
            publisher: Underlying MQTT publisher.
        """
        self._publisher = publisher
        self._running = False
        self._task: asyncio.Task | None = None

    @property
    def is_running(self) -> bool:
        """Check if the feed publisher is running."""
        return self._running

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
        Publish all feeds at the current simulation time.

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

        # Publish meter readings
        for meter_id, simulator in meters.items():
            reading = simulator.generate_at(simulation_time)
            if reading and reading.value:
                payload = reading.value.to_json_payload()
                result = self._publisher.publish_meter_reading(meter_id, payload)
                results["meters"].append(result)

        # Publish PV readings
        for system_id, simulator in pv_systems.items():
            reading = simulator.generate_at(simulation_time)
            if reading and reading.value:
                payload = reading.value.to_json_payload()
                result = self._publisher.publish_pv_reading(system_id, payload)
                results["pv"].append(result)

        # Publish weather (from first weather station)
        for station_id, simulator in weather_stations.items():
            reading = simulator.generate_at(simulation_time)
            if reading and reading.value:
                payload = reading.value.to_json_payload()
                result = self._publisher.publish_weather(payload)
                results["weather"].append(result)
            break  # Only publish from first station

        # Publish prices
        for feed_id, simulator in price_feeds.items():
            reading = simulator.generate_at(simulation_time)
            if reading and reading.value:
                payload = reading.value.to_json_payload()
                result = self._publisher.publish_spot_price(payload)
                results["prices"].append(result)

                # Generate and publish forecast (next 24 hours)
                forecast = self._generate_price_forecast(simulator, simulation_time)
                if forecast:
                    result = self._publisher.publish_price_forecast(forecast)
                    results["prices"].append(result)
            break  # Only publish from first feed

        # Publish consumer loads
        for device_id, simulator in loads.items():
            reading = simulator.generate_at(simulation_time)
            if reading and reading.value:
                payload = reading.value.to_json_payload()
                device_type = payload.get("device_type", "generic")
                result = self._publisher.publish_load(device_type, payload)
                results["loads"].append(result)

        return results

    def _generate_price_forecast(self, simulator: Any, current_time: datetime) -> dict | None:
        """Generate 24-hour price forecast."""
        from datetime import timedelta

        try:
            forecast_prices = []
            for hours_ahead in range(1, 25):
                future_time = current_time + timedelta(hours=hours_ahead)
                reading = simulator.generate_at(future_time)
                if reading and reading.value:
                    forecast_prices.append(
                        {
                            "timestamp": future_time.isoformat().replace("+00:00", "Z"),
                            "price_eur_per_kwh": round(reading.value.price_eur_per_kwh, 4),
                            "tariff_type": reading.value.tariff_type.value,
                        }
                    )

            if forecast_prices:
                return {
                    "generated_at": current_time.isoformat().replace("+00:00", "Z"),
                    "forecast_horizon_hours": 24,
                    "prices": forecast_prices,
                }
        except Exception as e:
            logger.error(f"Failed to generate price forecast: {e}")

        return None

    def publish_simulation_status(
        self,
        state: str,
        simulation_time: datetime,
        seed: int,
        acceleration: int,
        entities: dict[str, int],
    ) -> PublishResult:
        """
        Publish current simulation status.

        Args:
            state: Engine state (initialized, running, paused, stopped).
            simulation_time: Current simulation time.
            seed: Random seed.
            acceleration: Time acceleration factor.
            entities: Dict with counts of each entity type.

        Returns:
            PublishResult.
        """
        status = {
            "state": state,
            "simulation_time": simulation_time.isoformat().replace("+00:00", "Z"),
            "seed": seed,
            "acceleration": acceleration,
            "entities": entities,
            "published_at": datetime.now().isoformat().replace("+00:00", "Z"),
        }
        return self._publisher.publish_simulation_status(status)

    def publish_alert(
        self,
        severity: str,
        message: str,
        source: str,
        details: dict | None = None,
    ) -> PublishResult:
        """
        Publish a system alert.

        Args:
            severity: Alert severity (info, warning, error, critical).
            message: Alert message.
            source: Source of the alert.
            details: Optional additional details.

        Returns:
            PublishResult.
        """
        alert = {
            "timestamp": datetime.now().isoformat().replace("+00:00", "Z"),
            "severity": severity,
            "message": message,
            "source": source,
        }
        if details:
            alert["details"] = details

        return self._publisher.publish_alert(alert)
