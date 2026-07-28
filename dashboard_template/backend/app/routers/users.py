"""Users router."""

from datetime import datetime

from fastapi import APIRouter, Query

from app.services.data_source import get_data_source

router = APIRouter(prefix="/users", tags=["users"])


@router.get("")
async def get_users(
    from_date: str = Query(..., description="Start date (ISO format)"),
    to_date: str = Query(..., description="End date (ISO format)"),
) -> dict:
    """Get user analytics."""
    data_source = get_data_source()
    from_dt = datetime.fromisoformat(from_date)
    to_dt = datetime.fromisoformat(to_date)
    return data_source.get_users(from_dt, to_dt)
