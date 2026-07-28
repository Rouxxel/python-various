"""Overview router."""

from datetime import datetime

from fastapi import APIRouter, Query

from app.services.data_source import get_data_source

router = APIRouter(prefix="/overview", tags=["overview"])


@router.get("")
async def get_overview(
    from_date: str = Query(..., description="Start date (ISO format)"),
    to_date: str = Query(..., description="End date (ISO format)"),
) -> dict:
    """Get overview metrics."""
    data_source = get_data_source()
    from_dt = datetime.fromisoformat(from_date)
    to_dt = datetime.fromisoformat(to_date)
    return data_source.get_overview(from_dt, to_dt)
