"""Health check router."""

from fastapi import APIRouter

from app.config import settings
from app.core_specs.configuration.config_loader import config_loader
from app.services.providers import get_provider_status

_cfg = config_loader["endpoints"]["health"]

router = APIRouter(prefix=_cfg["router_prefix"], tags=[_cfg["endpoint_tag"]])


@router.get(_cfg["endpoint_route"])
async def health() -> dict:
    """Health check endpoint."""
    return {
        "status": "ok",
        "data_mode": settings.dashboard_data_mode,
        "providers": get_provider_status(),
    }
