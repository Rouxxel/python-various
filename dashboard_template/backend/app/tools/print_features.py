"""
Print Features Tool

Dumps the current configuration state including:
- Data mode
- Feature flags
- Hosting provider
- Environment variables (sanitized)

Usage:
    uv run python -m app.tools.print_features
"""

import os
from app.config import settings


def sanitize_value(value: str, key: str) -> str:
    """Sanitize sensitive values for display."""
    if any(sensitive in key.lower() for sensitive in ["key", "token", "secret", "password"]):
        return "***REDACTED***"
    return value


def print_config():
    """Print current configuration state."""
    print("=" * 60)
    print("DASHBOARD TEMPLATE CONFIGURATION")
    print("=" * 60)
    
    print("\n--- Data Mode ---")
    print(f"DASHBOARD_DATA_MODE: {settings.dashboard_data_mode}")
    
    print("\n--- Feature Flags ---")
    print(f"FEATURE_SUPABASE: {settings.feature_supabase}")
    print(f"FEATURE_VERCEL: {settings.feature_vercel}")
    print(f"FEATURE_HOST_HEALTH: {settings.feature_host_health}")
    print(f"FEATURE_STORAGE_METRICS: {settings.feature_storage_metrics}")
    print(f"FEATURE_COSTS_MODULE: {settings.feature_costs_module}")
    print(f"FEATURE_TEST_PROD_SWITCH: {settings.feature_test_prod_switch}")
    
    print("\n--- Hosting Provider ---")
    print(f"HOSTING_PROVIDER: {settings.hosting_provider}")
    
    print("\n--- Environment Variables (Sanitized) ---")
    env_vars = [
        "API_KEY",
        "FRONTEND_URL",
        "SUPABASE_URL",
        "SUPABASE_SERVICE_ROLE_KEY",
        "VERCEL_PROJECT_ID",
        "VERCEL_TOKEN",
        "RENDER_SERVICE_URL",
        "COSTS_UNIT_PRICE",
        "COSTS_UNIT_NAME",
    ]
    
    for var in env_vars:
        value = os.environ.get(var, "NOT SET")
        sanitized = sanitize_value(value, var)
        print(f"{var}: {sanitized}")
    
    print("\n--- Backend Configuration ---")
    print(f"DASHBOARD_BACKEND_HOST: {settings.dashboard_backend_host}")
    print(f"PORT: {os.environ.get('PORT', '8000')}")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    print_config()
