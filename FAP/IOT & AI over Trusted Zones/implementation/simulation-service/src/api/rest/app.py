"""
FastAPI application factory.

Main REST API application.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.rest.routes import health, meters, simulation


def create_app() -> FastAPI:
    """Create and configure the FastAPI application."""
    app = FastAPI(
        title="FACIS Simulation Service",
        description="Deterministic simulation service for FACIS IoT & AI demonstrator",
        version="1.0.0",
        docs_url="/api/docs",
        openapi_url="/api/openapi.json",
    )
    
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    app.include_router(health.router, prefix="/api/v1", tags=["health"])
    app.include_router(meters.router, prefix="/api/v1", tags=["meters"])
    app.include_router(simulation.router, prefix="/api/v1", tags=["simulation"])
    
    return app
