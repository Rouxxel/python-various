#!/usr/bin/env python3
"""Verify optional provider configuration for live mode.

Usage:
    cd backend && uv run python -m app.tools.verify_providers
"""

from __future__ import annotations

from app.config import settings
from app.services.providers import get_provider_status


def _line(name: str, status: str, detail: str = "") -> str:
    suffix = f" — {detail}" if detail else ""
    return f"  {name:18} {status}{suffix}"


def main() -> int:
    print("Dashboard provider configuration")
    print(f"  data_mode           {settings.dashboard_data_mode}")
    print()
    print("Provider readiness (disabled | misconfigured | ready):")

    statuses = get_provider_status()
    checks = [
        ("supabase", settings.feature_supabase, statuses["supabase"]),
        ("vercel", settings.feature_vercel, statuses["vercel"]),
        ("datadog", settings.feature_datadog, statuses["datadog"]),
        ("private_database", settings.feature_private_database, statuses["private_database"]),
        ("host_health", settings.feature_host_health, settings.hosting_provider),
    ]

    warnings = 0
    for name, enabled, status in checks:
        if not enabled:
            print(_line(name, "disabled"))
            continue
        if status in {"ready", "render", "railway", "fly", "custom", "none"}:
            print(_line(name, "ok", str(status)))
        else:
            print(_line(name, "needs config", str(status)))
            warnings += 1

    print()
    if settings.dashboard_data_mode == "mock":
        print("Mock mode: provider credentials are optional.")
        return 0

    if warnings:
        print(f"{warnings} provider(s) need configuration for live mode.")
        print("See docs/EXTENDING_PROVIDERS.md and backend/.env.example")
        return 1

    print("All enabled providers appear configured.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
