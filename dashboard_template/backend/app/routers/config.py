"""Configuration router for feature flags and settings."""

from fastapi import APIRouter

from app.config import settings
from app.core_specs.configuration.config_loader import config_loader
from app.services.providers import get_provider_status

_features_cfg = config_loader["endpoints"]["config_features"]
_env_cfg = config_loader["endpoints"]["config_env"]

router = APIRouter(prefix=_features_cfg["router_prefix"], tags=[_features_cfg["endpoint_tag"]])


@router.get(_features_cfg["endpoint_route"])
async def get_features() -> dict:
    """Get enabled features and current data mode."""
    return {
        "data_mode": settings.dashboard_data_mode,
        "features": {
            "supabase": settings.feature_supabase,
            "vercel": settings.feature_vercel,
            "host_health": settings.feature_host_health,
            "storage_metrics": settings.feature_storage_metrics,
            "costs_module": settings.feature_costs_module,
            "test_prod_switch": settings.feature_test_prod_switch,
            "datadog": settings.feature_datadog,
            "private_database": settings.feature_private_database,
        },
        "hosting_provider": settings.hosting_provider,
    }


@router.get(_env_cfg["endpoint_route"])
async def get_env_config() -> dict:
    """Sanitized environment configuration for the frontend."""
    return {
        "data_mode": settings.dashboard_data_mode,
        "hosting_provider": settings.hosting_provider,
        "test_available": settings.environment_available("test"),
        "prod_available": settings.environment_available("prod"),
        "providers": get_provider_status(),
    }
