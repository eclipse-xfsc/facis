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

from src.api.mqtt import MQTTFeedPublisher, MQTTPublisher
from src.api.rest.dependencies import SimulationState
from src.api.rest.routes import health, loads, meters, prices, pv, simulation, weather
from src.core.engine import EngineState

logger = logging.getLogger(__name__)

# docs/openapi.yaml relative to project root (parent of src/)
_OPENAPI_SPEC = Path(__file__).resolve().parent.parent.parent.parent / "docs" / "openapi.yaml"


class MQTTPublishTask:
    """Background task for periodic MQTT publishing."""

    def __init__(
        self,
        state: SimulationState,
        publisher: MQTTPublisher,
        feed_publisher: MQTTFeedPublisher,
    ) -> None:
        self._state = state
        self._publisher = publisher
        self._feed_publisher = feed_publisher
        self._task: asyncio.Task | None = None
        self._running = False

    async def start(self) -> None:
        """Start the publishing task."""
        self._running = True
        self._task = asyncio.create_task(self._publish_loop())
        logger.info("MQTT publish task started")

    async def stop(self) -> None:
        """Stop the publishing task."""
        self._running = False
        if self._task:
            self._task.cancel()
            try:
                await self._task
            except asyncio.CancelledError:
                pass
        logger.info("MQTT publish task stopped")

    async def _publish_loop(self) -> None:
        """Main publishing loop."""
        # Wait for connection
        retries = 0
        while self._running and not self._publisher.is_connected:
            await asyncio.sleep(1)
            retries += 1
            if retries >= 30:
                logger.error("Timeout waiting for MQTT connection")
                return

        # Get publish interval from settings (in seconds)
        interval_minutes = self._state.settings.simulation.interval_minutes
        interval_seconds = interval_minutes * 60

        # Adjust for simulation speed factor
        speed_factor = self._state.settings.simulation.speed_factor
        real_interval = interval_seconds / speed_factor

        logger.info(
            f"MQTT publishing at {interval_minutes}min simulation intervals "
            f"(real: {real_interval:.1f}s with {speed_factor}x speed)"
        )

        while self._running:
            try:
                # Only publish when simulation is running
                engine = self._state.engine
                if engine.state == EngineState.RUNNING:
                    # Advance simulation time
                    engine.advance(interval_seconds)

                    # Publish all feeds
                    self._feed_publisher.publish_all_feeds(
                        meters=self._state._meters,
                        pv_systems=self._state._pv_systems,
                        weather_stations=self._state._weather_stations,
                        price_feeds=self._state._price_feeds,
                        loads=self._state._loads,
                        simulation_time=engine.simulation_time,
                    )

                    # Publish simulation status
                    self._feed_publisher.publish_simulation_status(
                        state=engine.state.value,
                        simulation_time=engine.simulation_time,
                        seed=engine.seed,
                        acceleration=engine.clock.acceleration,
                        entities={
                            "meters": len(self._state._meters),
                            "pv_systems": len(self._state._pv_systems),
                            "weather_stations": len(self._state._weather_stations),
                            "price_feeds": len(self._state._price_feeds),
                            "loads": len(self._state._loads),
                        },
                    )

                await asyncio.sleep(real_interval)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in MQTT publish loop: {e}")
                await asyncio.sleep(5)  # Back off on error


# Global MQTT components (initialized in lifespan)
_mqtt_publisher: MQTTPublisher | None = None
_feed_publisher: MQTTFeedPublisher | None = None
_publish_task: MQTTPublishTask | None = None


def get_mqtt_publisher() -> MQTTPublisher | None:
    """Get the global MQTT publisher instance."""
    return _mqtt_publisher


def get_feed_publisher() -> MQTTFeedPublisher | None:
    """Get the global feed publisher instance."""
    return _feed_publisher


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    global _mqtt_publisher, _feed_publisher, _publish_task

    # Startup: Initialize simulation state
    state = SimulationState.get_instance()
    state.initialize()

    # Initialize MQTT publisher
    settings = state.settings
    _mqtt_publisher = MQTTPublisher.from_config(settings.mqtt)
    _feed_publisher = MQTTFeedPublisher(_mqtt_publisher)

    # Connect to MQTT broker
    if _mqtt_publisher.connect():
        logger.info("MQTT publisher connected")

        # Start background publishing task
        _publish_task = MQTTPublishTask(state, _mqtt_publisher, _feed_publisher)
        await _publish_task.start()

        # Auto-start simulation for MQTT publishing
        state.engine.start()
        logger.info("Simulation auto-started for MQTT publishing")
    else:
        logger.warning("MQTT publisher failed to connect - MQTT publishing disabled")

    yield

    # Shutdown: Cleanup
    if _publish_task:
        await _publish_task.stop()

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
