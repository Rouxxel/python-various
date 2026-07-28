"""Configuration router for feature flags and settings."""

from fastapi import APIRouter

from app.config import settings
from app.services.providers import get_provider_status

router = APIRouter(prefix="/config", tags=["config"])


@router.get("/features")
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


@router.get("/env")
async def get_env_config() -> dict:
    """Sanitized environment configuration for the frontend."""
    return {
        "data_mode": settings.dashboard_data_mode,
        "hosting_provider": settings.hosting_provider,
        "test_available": settings.environment_available("test"),
        "prod_available": settings.environment_available("prod"),
        "providers": get_provider_status(),
    }
