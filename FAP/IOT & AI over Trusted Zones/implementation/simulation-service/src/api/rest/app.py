"""
FastAPI application factory.

Main REST API application for FACIS Simulation Service.
"""

import asyncio
import logging
from contextlib import asynccontextmanager
from pathlib import Path

import yaml
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.kafka.producer import KafkaFeedPublisher, KafkaPublisher
from src.api.mqtt import MQTTFeedPublisher, MQTTPublisher
from src.api.orce.client import OrceClient
from src.api.orce.envelope import build_tick_envelope
from src.api.rest.dependencies import SimulationState
from src.api.rest.routes import health, loads, meters, prices, pv, simulation, weather
from src.core.engine import EngineState

logger = logging.getLogger(__name__)

# docs/openapi.yaml relative to project root (parent of src/)
_OPENAPI_SPEC = Path(__file__).resolve().parent.parent.parent.parent / "docs" / "openapi.yaml"


class PublishOrchestrator:
    """
    Unified publish orchestrator for all output channels.

    On each simulation tick:
    1. Advances simulation time
    2. Generates correlated Smart Energy snapshot
    3. Generates correlated Smart City snapshot
    4. Publishes to MQTT (if connected)
    5. Publishes to Kafka (if enabled)
    6. POSTs tick envelope to ORCE (if enabled)

    Each channel is independently enabled/disabled via config.
    """

    def __init__(
        self,
        state: SimulationState,
        mqtt_publisher: MQTTPublisher | None = None,
        mqtt_feed_publisher: MQTTFeedPublisher | None = None,
        kafka_publisher: KafkaPublisher | None = None,
        kafka_feed_publisher: KafkaFeedPublisher | None = None,
        orce_client: OrceClient | None = None,
    ) -> None:
        self._state = state
        self._mqtt_publisher = mqtt_publisher
        self._mqtt_feed_publisher = mqtt_feed_publisher
        self._kafka_publisher = kafka_publisher
        self._kafka_feed_publisher = kafka_feed_publisher
        self._orce_client = orce_client
        self._task: asyncio.Task | None = None
        self._running = False

    async def start(self) -> None:
        """Start the publishing loop."""
        self._running = True
        self._task = asyncio.create_task(self._publish_loop())
        logger.info("Publish orchestrator started")

    async def stop(self) -> None:
        """Stop the publishing loop."""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("Publish orchestrator stopped")

    async def _publish_loop(self) -> None:
        """Main publishing loop."""
        # Wait for MQTT connection if configured
        if self._mqtt_publisher:
            retries = 0
            while self._running and not self._mqtt_publisher.is_connected:
                await asyncio.sleep(1)
                retries += 1
                if retries >= 30:
                    logger.warning("Timeout waiting for MQTT connection — continuing without MQTT")
                    break

        settings = self._state.settings
        interval_minutes = settings.simulation.interval_minutes
        interval_seconds = interval_minutes * 60
        speed_factor = settings.simulation.speed_factor
        real_interval = interval_seconds / speed_factor

        logger.info(
            f"Publishing at {interval_minutes}min simulation intervals "
            f"(real: {real_interval:.1f}s with {speed_factor}x speed)"
        )

        while self._running:
            try:
                engine = self._state.engine
                if engine.state != EngineState.RUNNING:
                    await asyncio.sleep(1)
                    continue

                # Advance simulation time
                engine.advance(interval_seconds)
                sim_time = engine.simulation_time

                # Generate correlated snapshots
                energy_snapshot = None
                if self._state._energy_correlation:
                    energy_snapshot = self._state._energy_correlation.generate_snapshot(sim_time)

                city_snapshot = None
                if self._state._smart_city_correlation:
                    city_snapshot = self._state._smart_city_correlation.generate_snapshot(sim_time)

                # --- MQTT channel ---
                if (
                    self._mqtt_feed_publisher
                    and self._mqtt_publisher
                    and self._mqtt_publisher.is_connected
                ):
                    try:
                        self._mqtt_feed_publisher.publish_all_feeds(
                            meters=self._state._meters,
                            pv_systems=self._state._pv_systems,
                            weather_stations=self._state._weather_stations,
                            price_feeds=self._state._price_feeds,
                            loads=self._state._loads,
                            simulation_time=sim_time,
                        )
                        self._mqtt_feed_publisher.publish_simulation_status(
                            state=engine.state.value,
                            simulation_time=sim_time,
                            seed=engine.seed,
                            acceleration=engine.clock.acceleration,
                            entities={
                                "meters": len(self._state._meters),
                                "pv_systems": len(self._state._pv_systems),
                                "weather_stations": len(self._state._weather_stations),
                                "price_feeds": len(self._state._price_feeds),
                                "loads": len(self._state._loads),
                                "streetlights": len(self._state._streetlight_simulators),
                                "traffic_zones": len(self._state._traffic_simulators),
                            },
                        )
                    except Exception as e:
                        logger.error(f"MQTT publish error: {e}")

                # --- Kafka channel ---
                if self._kafka_feed_publisher:
                    try:
                        self._kafka_feed_publisher.publish_all_feeds(
                            meters=self._state._meters,
                            pv_systems=self._state._pv_systems,
                            weather_stations=self._state._weather_stations,
                            price_feeds=self._state._price_feeds,
                            loads=self._state._loads,
                            simulation_time=sim_time,
                        )
                        # Publish Smart City feeds to Kafka
                        if city_snapshot and self._kafka_publisher:
                            for light in city_snapshot.streetlights:
                                self._kafka_publisher.publish_streetlight(
                                    light.light_id, light.to_json_payload()
                                )
                            for traffic in city_snapshot.traffic_readings:
                                self._kafka_publisher.publish_traffic(
                                    traffic.zone_id, traffic.to_json_payload()
                                )
                            for event in city_snapshot.events:
                                self._kafka_publisher.publish_city_event(
                                    event.zone_id, event.to_json_payload()
                                )
                            if city_snapshot.visibility:
                                self._kafka_publisher.publish_city_weather(
                                    city_snapshot.city_id,
                                    city_snapshot.visibility.to_json_payload(),
                                )
                            self._kafka_publisher.flush()
                    except Exception as e:
                        logger.error(f"Kafka publish error: {e}")

                # --- ORCE channel ---
                if self._orce_client and energy_snapshot and city_snapshot:
                    try:
                        envelope = build_tick_envelope(
                            timestamp=sim_time,
                            site_id=settings.site_id,
                            energy_snapshot=energy_snapshot,
                            city_snapshot=city_snapshot,
                            mode=settings.simulation.mode,
                            seed=settings.simulation.seed,
                        )
                        await self._orce_client.send_tick(envelope)
                    except Exception as e:
                        logger.error(f"ORCE publish error: {e}")

                await asyncio.sleep(real_interval)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in publish loop: {e}")
                await asyncio.sleep(5)


# Global components (initialized in lifespan)
_mqtt_publisher: MQTTPublisher | None = None
_mqtt_feed_publisher: MQTTFeedPublisher | None = None
_kafka_publisher: KafkaPublisher | None = None
_kafka_feed_publisher: KafkaFeedPublisher | None = None
_orce_client: OrceClient | None = None
_orchestrator: PublishOrchestrator | None = None


def get_mqtt_publisher() -> MQTTPublisher | None:
    """Get the global MQTT publisher instance."""
    return _mqtt_publisher


def get_feed_publisher() -> MQTTFeedPublisher | None:
    """Get the global feed publisher instance."""
    return _mqtt_feed_publisher


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    global _mqtt_publisher, _mqtt_feed_publisher
    global _kafka_publisher, _kafka_feed_publisher
    global _orce_client, _orchestrator

    # Startup: Initialize simulation state
    state = SimulationState.get_instance()
    state.initialize()
    settings = state.settings

    # --- Initialize MQTT ---
    _mqtt_publisher = MQTTPublisher.from_config(settings.mqtt)
    _mqtt_feed_publisher = MQTTFeedPublisher(_mqtt_publisher)

    mqtt_connected = False
    if _mqtt_publisher.connect():
        logger.info("MQTT publisher connected")
        mqtt_connected = True
    else:
        logger.warning("MQTT publisher failed to connect — MQTT publishing disabled")

    # --- Initialize Kafka ---
    if settings.kafka.enabled:
        _kafka_publisher = KafkaPublisher.from_config(settings.kafka)
        if _kafka_publisher.connect():
            _kafka_feed_publisher = KafkaFeedPublisher(_kafka_publisher)
            logger.info("Kafka publisher connected")
        else:
            logger.warning("Kafka publisher failed to connect — Kafka publishing disabled")
            _kafka_publisher = None

    # --- Initialize ORCE ---
    if settings.orce.enabled:
        _orce_client = OrceClient.from_config(settings.orce)
        await _orce_client.connect()
        logger.info("ORCE client initialized")

    # --- Start orchestrator ---
    _orchestrator = PublishOrchestrator(
        state=state,
        mqtt_publisher=_mqtt_publisher if mqtt_connected else None,
        mqtt_feed_publisher=_mqtt_feed_publisher if mqtt_connected else None,
        kafka_publisher=_kafka_publisher,
        kafka_feed_publisher=_kafka_feed_publisher,
        orce_client=_orce_client,
    )
    await _orchestrator.start()

    # Auto-start simulation
    state.engine.start()
    logger.info("Simulation auto-started")

    yield

    # Shutdown: Cleanup
    if _orchestrator:
        await _orchestrator.stop()

    if _orce_client:
        await _orce_client.disconnect()

    if _kafka_publisher:
        _kafka_publisher.disconnect()

    if _mqtt_publisher:
        _mqtt_publisher.disconnect()
        logger.info("MQTT publisher disconnected")


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    # title, description, version live in docs/openapi.yaml and are served at /docs
    app = FastAPI(docs_url="/docs", redoc_url="/redoc", openapi_url="/openapi.json", lifespan=lifespan)

    # CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register routers
    app.include_router(health.router, prefix="/api/v1", tags=["Health & Configuration"])
    app.include_router(meters.router, prefix="/api/v1", tags=["Energy Meters"])
    app.include_router(prices.router, prefix="/api/v1", tags=["Energy Prices"])
    app.include_router(loads.router, prefix="/api/v1", tags=["Consumer Loads"])
    app.include_router(weather.router, prefix="/api/v1", tags=["Weather Data"])
    app.include_router(pv.router, prefix="/api/v1", tags=["PV Generation"])
    app.include_router(simulation.router, prefix="/api/v1", tags=["Simulation Control"])

    with open(_OPENAPI_SPEC, encoding="utf-8") as f:
        app.openapi_schema = yaml.safe_load(f)

    return app


# Create default app instance
app = create_app()
