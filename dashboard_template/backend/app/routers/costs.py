"""Costs router."""

from datetime import datetime

from fastapi import APIRouter, Query

from app.config import settings
from app.services.data_source import get_data_source

router = APIRouter(prefix="/costs", tags=["costs"])


@router.get("")
async def get_costs(
    from_date: str = Query(..., description="Start date (ISO format)"),
    to_date: str = Query(..., description="End date (ISO format)"),
) -> dict:
    """Get cost analytics."""
    if (
        not settings.feature_costs_module
        and settings.dashboard_data_mode == "live"
    ):
        return {
            "total_cost": 0,
            "cost_by_category": {},
            "unit_economics": {},
            "projections": [],
            "notes": [
                "Costs module disabled. Set FEATURE_COSTS_MODULE=true to enable."
            ],
        }

    data_source = get_data_source()
    from_dt = datetime.fromisoformat(from_date)
    to_dt = datetime.fromisoformat(to_date)
    return data_source.get_costs(from_dt, to_dt)
