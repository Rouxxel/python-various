"""Live infrastructure payload builder — composes optional providers."""

from __future__ import annotations

from typing import Any, Literal

from app.config import settings
from app.services.hosting import get_hosting_service
from app.services.providers import datadog, database, supabase, vercel


def _service_url_for_provider() -> str:
    urls = {
        "render": settings.render_service_url,
        "railway": settings.railway_service_url,
        "fly": settings.fly_service_url,
        "custom": settings.custom_service_url,
    }
    return urls.get(settings.hosting_provider, "")


async def build(env: Literal["test", "prod"] = "test") -> dict[str, Any]:
    """Build infrastructure response for live mode."""
    notes: list[str] = []
    host_health: dict[str, Any] = {}
    deployments: list[Any] = []
    storage: list[Any] = []
    database_tables: list[Any] = []
    datadog_status: dict[str, Any] | None = None

    if settings.feature_host_health:
        service_url = _service_url_for_provider()
        if service_url:
            hosting = get_hosting_service()
            host_health = await hosting.check_health(service_url)
        else:
            notes.append(
                f"Host health enabled but no URL for provider '{settings.hosting_provider}'."
            )
    else:
        notes.append("Host health disabled. Set FEATURE_HOST_HEALTH=true to enable.")

    if settings.feature_vercel:
        vercel_data = await vercel.list_deployments(env)
        deployments = vercel_data.get("deployments", [])
        notes.extend(vercel_data.get("notes", []))
    else:
        notes.append("Vercel disabled. Set FEATURE_VERCEL=true to enable deployments.")

    if settings.feature_storage_metrics:
        storage_data = await supabase.list_storage_buckets(env)
        storage = storage_data.get("buckets", [])
        notes.extend(storage_data.get("notes", []))

    if settings.feature_private_database:
        db_data = database.list_table_row_counts()
        database_tables = db_data.get("tables", [])
        notes.extend(db_data.get("notes", []))
    elif settings.feature_supabase:
        db_data = await supabase.list_table_row_counts(env)
        database_tables = db_data.get("tables", [])
        notes.extend(db_data.get("notes", []))
    else:
        notes.append(
            "Database section disabled. Enable FEATURE_SUPABASE or FEATURE_PRIVATE_DATABASE."
        )

    if settings.feature_datadog:
        datadog_status = await datadog.validate_credentials()
        notes.extend(datadog_status.get("notes", []))

    return {
        "host_health": host_health,
        "deployments": deployments,
        "storage": storage,
        "database": {"tables": database_tables},
        "datadog": datadog_status,
        "notes": notes,
        "environment": env,
    }
