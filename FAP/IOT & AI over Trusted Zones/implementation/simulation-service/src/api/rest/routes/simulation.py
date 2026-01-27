"""
Simulation control endpoints.

POST /api/v1/simulation/start
POST /api/v1/simulation/pause
POST /api/v1/simulation/reset
"""

from fastapi import APIRouter

router = APIRouter()


@router.post("/simulation/start")
async def start_simulation() -> dict:
    raise NotImplementedError("start_simulation not yet implemented")


@router.post("/simulation/pause")
async def pause_simulation() -> dict:
    raise NotImplementedError("pause_simulation not yet implemented")


@router.post("/simulation/reset")
async def reset_simulation() -> dict:
    raise NotImplementedError("reset_simulation not yet implemented")


@router.get("/simulation/status")
async def get_simulation_status() -> dict:
    raise NotImplementedError("get_simulation_status not yet implemented")
