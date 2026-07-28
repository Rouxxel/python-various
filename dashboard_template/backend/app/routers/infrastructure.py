"""Infrastructure router."""

from fastapi import APIRouter, Request

from app.config import settings
from app.core_specs.configuration.config_loader import config_loader
from app.services.data_source import get_data_source
from app.services.hosting import get_hosting_service

_cfg = config_loader["endpoints"]["infrastructure"]
router = APIRouter(prefix=_cfg["router_prefix"], tags=[_cfg["endpoint_tag"]])


def _service_url_for_provider() -> str:
    urls = {
        "render": settings.render_service_url,
        "railway": settings.railway_service_url,
        "fly": settings.fly_service_url,
        "custom": settings.custom_service_url,
    }
    return urls.get(settings.hosting_provider, "")


@router.get(_cfg["endpoint_route"])
async def get_infrastructure(request: Request) -> dict:
    """Get infrastructure metrics."""
    env = getattr(request.state, "dashboard_environment", "test")

    if settings.dashboard_data_mode == "live":
        from app.services.live.infrastructure_builder import build

        return await build(env)

    return get_data_source().get_infrastructure()


@router.post(_cfg["wake_route"])
async def wake_host() -> dict:
    """Wake a sleeping hosting service (e.g. Render free tier)."""
    if not settings.feature_host_health:
        return {
            "status": "disabled",
            "message": "Host health disabled. Set FEATURE_HOST_HEALTH=true to enable.",
        }

    service_url = _service_url_for_provider()
    if not service_url:
        return {
            "status": "misconfigured",
            "message": (
                f"No service URL configured for hosting provider "
                f"'{settings.hosting_provider}'."
            ),
        }

    hosting = get_hosting_service()
    return await hosting.wake(service_url)
