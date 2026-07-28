"""Optional third-party provider clients.

Each module is safe to import when credentials are missing — callers receive
empty payloads and instructional notes[] instead of exceptions.
"""

from app.config import settings
from app.services.providers import datadog, database, supabase, vercel


def get_provider_status() -> dict[str, str]:
    """Summarize provider configuration for /api/health."""
    return {
        "supabase": supabase.get_status(),
        "vercel": vercel.get_status(),
        "datadog": datadog.get_status(),
        "private_database": database.get_status(),
    }


__all__ = [
    "datadog",
    "database",
    "get_provider_status",
    "supabase",
    "vercel",
]
