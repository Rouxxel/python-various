"""Overview router."""

from datetime import datetime

from fastapi import APIRouter, Query

from app.core_specs.configuration.config_loader import config_loader
from app.services.data_source import get_data_source
from app.utils.custom_logger import log_handler

_cfg = config_loader["endpoints"]["overview"]
router = APIRouter(prefix=_cfg["router_prefix"], tags=[_cfg["endpoint_tag"]])


@router.get(_cfg["endpoint_route"])
async def get_overview(
    from_date: str = Query(..., description="Start date (ISO format)"),
    to_date: str = Query(..., description="End date (ISO format)"),
) -> dict:
    """Get overview metrics."""
    log_handler.debug("GET overview from=%s to=%s", from_date, to_date)
    data_source = get_data_source()
    from_dt = datetime.fromisoformat(from_date)
    to_dt = datetime.fromisoformat(to_date)
    return data_source.get_overview(from_dt, to_dt)
