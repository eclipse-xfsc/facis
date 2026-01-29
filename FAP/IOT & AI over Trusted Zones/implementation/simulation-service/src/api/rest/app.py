"""
FastAPI application factory.

Main REST API application for FACIS Simulation Service.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.rest.dependencies import SimulationState
from src.api.rest.routes import health, loads, meters, prices, simulation


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup: Initialize simulation state
    state = SimulationState.get_instance()
    state.initialize()
    yield
    # Shutdown: Cleanup if needed
    pass


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="FACIS Simulation Service",
        description=(
            "Deterministic simulation service for FACIS IoT & AI demonstrator. "
            "Provides simulated energy meter readings and electricity prices."
        ),
        version="1.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
    )

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
    app.include_router(simulation.router, prefix="/api/v1", tags=["Simulation Control"])

    return app


# Create default app instance
app = create_app()
