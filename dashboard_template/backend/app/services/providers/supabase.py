"""Supabase provider placeholder.

Install optional dependency: uv sync --extra supabase

Implement list_table_row_counts() with your schema when ready for live data.
"""

from __future__ import annotations

import logging
from typing import Any, Literal

import httpx

from app.config import settings

logger = logging.getLogger(__name__)


def get_status() -> str:
    """Return disabled | misconfigured | ready."""
    if not settings.feature_supabase:
        return "disabled"
    creds = settings.credentials_for("test")
    if creds.supabase_url and creds.supabase_service_role_key:
        return "ready"
    return "misconfigured"


async def check_connection(env: Literal["test", "prod"] = "test") -> dict[str, Any]:
    """Ping Supabase REST API. Reference implementation for live mode."""
    if not settings.feature_supabase:
        return {"status": "disabled", "notes": ["Set FEATURE_SUPABASE=true to enable."]}

    creds = settings.credentials_for(env)
    if not creds.supabase_url or not creds.supabase_service_role_key:
        return {
            "status": "misconfigured",
            "notes": [
                f"Configure SUPABASE_URL_{env.upper()} and "
                f"SUPABASE_SERVICE_ROLE_KEY_{env.upper()}."
            ],
        }

    url = creds.supabase_url.rstrip("/")
    headers = {
        "apikey": creds.supabase_service_role_key,
        "Authorization": f"Bearer {creds.supabase_service_role_key}",
    }
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(f"{url}/rest/v1/", headers=headers)
        if response.status_code < 400:
            return {
                "status": "connected",
                "notes": [
                    "Supabase reachable. Implement list_table_row_counts() in "
                    "app/services/providers/supabase.py for row counts."
                ],
            }
        return {
            "status": "error",
            "notes": [f"Supabase returned HTTP {response.status_code}."],
        }
    except Exception as exc:
        logger.warning("Supabase connection failed: %s", exc)
        return {"status": "unavailable", "notes": [str(exc)]}


async def list_table_row_counts(
    env: Literal["test", "prod"] = "test",
    tables: list[str] | None = None,
) -> dict[str, Any]:
    """Return table row counts — implement with supabase-py or SQL when ready."""
    connection = await check_connection(env)
    if connection.get("status") != "connected":
        return {"tables": [], **connection}

    # Optional: use supabase-py when installed
    try:
        from supabase import create_client  # type: ignore[import-untyped]

        creds = settings.credentials_for(env)
        client = create_client(creds.supabase_url, creds.supabase_service_role_key)
        target_tables = tables or ["users", "sessions", "events"]
        rows: list[dict[str, Any]] = []
        for table in target_tables:
            result = (
                client.table(table)
                .select("id", count="exact")
                .limit(1)
                .execute()
            )
            count = result.count if result.count is not None else 0
            rows.append({"name": table, "row_count": count})
        return {"tables": rows, "status": "connected", "notes": []}
    except ImportError:
        return {
            "tables": [],
            "status": "connected",
            "notes": [
                "Install supabase extra: uv sync --extra supabase",
                "Then implement list_table_row_counts() or pass explicit table names.",
            ],
        }
    except Exception as exc:
        logger.warning("Supabase table query failed: %s", exc)
        return {
            "tables": [],
            "status": "error",
            "notes": [str(exc)],
        }


async def list_storage_buckets(env: Literal["test", "prod"] = "test") -> dict[str, Any]:
    """Storage metrics placeholder — implement with Supabase Storage API."""
    if not settings.feature_storage_metrics:
        return {"buckets": [], "notes": ["Set FEATURE_STORAGE_METRICS=true to enable."]}
    return {
        "buckets": [],
        "notes": [
            "Implement list_storage_buckets() using Supabase Storage API "
            "or supabase-py storage.list_buckets()."
        ],
    }
