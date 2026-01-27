"""
Health check endpoints.

GET /api/v1/health
"""

from datetime import UTC, datetime

from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
async def health_check() -> dict:
    """Health check endpoint."""
    return {
        "status": "healthy",
        "service": "facis-simulation-service",
        "version": "1.0.0",
        "timestamp": datetime.now(UTC).isoformat(),
    }


@router.get("/config")
async def get_config() -> dict:
    """Get current service configuration."""
    raise NotImplementedError("get_config not yet implemented")
