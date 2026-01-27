"""
Meter data endpoints.

GET /api/v1/meters
GET /api/v1/meters/{id}/current
GET /api/v1/meters/{id}/history
"""

from fastapi import APIRouter

router = APIRouter()


@router.get("/meters")
async def list_meters() -> dict:
    raise NotImplementedError("list_meters not yet implemented")


@router.get("/meters/{meter_id}/current")
async def get_meter_current(meter_id: str) -> dict:
    raise NotImplementedError("get_meter_current not yet implemented")


@router.get("/meters/{meter_id}/history")
async def get_meter_history(meter_id: str) -> dict:
    raise NotImplementedError("get_meter_history not yet implemented")
