"""Vercel provider placeholder.

Set FEATURE_VERCEL=true and VERCEL_API_TOKEN to fetch deployments in live mode.
"""

from __future__ import annotations

import logging
from typing import Any, Literal

import httpx

from app.config import settings

logger = logging.getLogger(__name__)

VERCEL_API = "https://api.vercel.com"


def get_status() -> str:
    if not settings.feature_vercel:
        return "disabled"
    if settings.vercel_api_token:
        return "ready"
    return "misconfigured"


async def list_deployments(
    env: Literal["test", "prod"] = "test",
    limit: int = 5,
) -> dict[str, Any]:
    """Fetch recent deployments — reference stub using Vercel REST API."""
    if not settings.feature_vercel:
        return {"deployments": [], "notes": ["Set FEATURE_VERCEL=true to enable."]}

    if not settings.vercel_api_token:
        return {
            "deployments": [],
            "notes": ["Set VERCEL_API_TOKEN to fetch deployments."],
        }

    creds = settings.credentials_for(env)
    if not creds.vercel_project_id:
        return {
            "deployments": [],
            "notes": [f"Set VERCEL_PROJECT_ID_{env.upper()} for this environment."],
        }

    params: dict[str, str | int] = {
        "projectId": creds.vercel_project_id,
        "limit": limit,
    }
    if settings.vercel_team_id:
        params["teamId"] = settings.vercel_team_id

    headers = {"Authorization": f"Bearer {settings.vercel_api_token}"}
    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(
                f"{VERCEL_API}/v6/deployments",
                params=params,
                headers=headers,
            )
        if response.status_code >= 400:
            return {
                "deployments": [],
                "notes": [f"Vercel API HTTP {response.status_code}: {response.text[:200]}"],
            }
        data = response.json()
        deployments = [
            {
                "id": item.get("uid"),
                "url": item.get("url"),
                "state": item.get("state"),
                "created_at": item.get("createdAt"),
            }
            for item in data.get("deployments", [])
        ]
        return {"deployments": deployments, "notes": []}
    except Exception as exc:
        logger.warning("Vercel deployments fetch failed: %s", exc)
        return {"deployments": [], "notes": [str(exc)]}


async def get_web_analytics(
    env: Literal["test", "prod"] = "test",
) -> dict[str, Any]:
    """Web analytics placeholder — Vercel Analytics API varies by plan."""
    if not settings.feature_vercel:
        return {"metrics": {}, "notes": ["Set FEATURE_VERCEL=true to enable."]}
    return {
        "metrics": {},
        "notes": [
            "Implement get_web_analytics() using the Vercel Analytics API "
            "for your plan. See docs/EXTENDING_PROVIDERS.md."
        ],
    }
