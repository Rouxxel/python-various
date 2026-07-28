"""Datadog provider placeholder.

Set FEATURE_DATADOG=true plus DATADOG_API_KEY and DATADOG_APP_KEY.
"""

from __future__ import annotations

import logging
from typing import Any

import httpx

from app.config import settings

logger = logging.getLogger(__name__)


def get_status() -> str:
    if not settings.feature_datadog:
        return "disabled"
    if settings.datadog_api_key and settings.datadog_app_key:
        return "ready"
    return "misconfigured"


def _base_url() -> str:
    return f"https://api.{settings.datadog_site}"


async def query_metrics(
    query: str,
    from_ts: int,
    to_ts: int,
) -> dict[str, Any]:
    """Query Datadog metrics — reference implementation."""
    if not settings.feature_datadog:
        return {"series": [], "notes": ["Set FEATURE_DATADOG=true to enable."]}

    if not settings.datadog_api_key or not settings.datadog_app_key:
        return {
            "series": [],
            "notes": ["Set DATADOG_API_KEY and DATADOG_APP_KEY."],
        }

    headers = {
        "DD-API-KEY": settings.datadog_api_key,
        "DD-APPLICATION-KEY": settings.datadog_app_key,
    }
    try:
        async with httpx.AsyncClient(timeout=20.0) as client:
            response = await client.get(
                f"{_base_url()}/api/v1/query",
                params={"query": query, "from": from_ts, "to": to_ts},
                headers=headers,
            )
        if response.status_code >= 400:
            return {
                "series": [],
                "notes": [f"Datadog HTTP {response.status_code}: {response.text[:200]}"],
            }
        return {"series": response.json().get("series", []), "notes": []}
    except Exception as exc:
        logger.warning("Datadog query failed: %s", exc)
        return {"series": [], "notes": [str(exc)]}


async def validate_credentials() -> dict[str, Any]:
    """Validate Datadog API keys with a lightweight validate endpoint."""
    status = get_status()
    if status != "ready":
        return {"status": status, "notes": ["Configure Datadog keys to validate."]}

    headers = {
        "DD-API-KEY": settings.datadog_api_key,
        "DD-APPLICATION-KEY": settings.datadog_app_key,
    }
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(
                f"{_base_url()}/api/v1/validate",
                headers=headers,
            )
        if response.status_code == 200:
            return {"status": "connected", "notes": []}
        return {
            "status": "error",
            "notes": [f"Datadog validate HTTP {response.status_code}"],
        }
    except Exception as exc:
        return {"status": "unavailable", "notes": [str(exc)]}
