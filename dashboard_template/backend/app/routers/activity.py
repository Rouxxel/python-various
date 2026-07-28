"""Activity router."""

from datetime import datetime

from fastapi import APIRouter, Query

from app.core_specs.configuration.config_loader import config_loader
from app.services.data_source import get_data_source

_cfg = config_loader["endpoints"]["activity"]
router = APIRouter(prefix=_cfg["router_prefix"], tags=[_cfg["endpoint_tag"]])


@router.get(_cfg["endpoint_route"])
async def get_activity(
    from_date: str = Query(..., description="Start date (ISO format)"),
    to_date: str = Query(..., description="End date (ISO format)"),
) -> dict:
    """Get activity/events analytics."""
    data_source = get_data_source()
    from_dt = datetime.fromisoformat(from_date)
    to_dt = datetime.fromisoformat(to_date)
    return data_source.get_activity(from_dt, to_dt)
