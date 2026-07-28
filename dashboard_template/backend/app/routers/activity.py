"""Activity router."""

from datetime import datetime

from fastapi import APIRouter, Query

from app.services.data_source import get_data_source

router = APIRouter(prefix="/activity", tags=["activity"])


@router.get("")
async def get_activity(
    from_date: str = Query(..., description="Start date (ISO format)"),
    to_date: str = Query(..., description="End date (ISO format)"),
) -> dict:
    """Get activity/events analytics."""
    data_source = get_data_source()
    from_dt = datetime.fromisoformat(from_date)
    to_dt = datetime.fromisoformat(to_date)
    return data_source.get_activity(from_dt, to_dt)
