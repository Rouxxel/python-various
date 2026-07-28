"""Private database provider placeholder.

Install optional dependency: uv sync --extra database

Use DATABASE_URL for Postgres/MySQL on a private server or VPN.
"""

from __future__ import annotations

import logging
from typing import Any

from app.config import settings

logger = logging.getLogger(__name__)


def get_status() -> str:
    if not settings.feature_private_database:
        return "disabled"
    if settings.database_url:
        return "ready"
    return "misconfigured"


def check_connection() -> dict[str, Any]:
    """Test database connectivity when SQLAlchemy is installed."""
    if not settings.feature_private_database:
        return {"status": "disabled", "notes": ["Set FEATURE_PRIVATE_DATABASE=true."]}
    if not settings.database_url:
        return {
            "status": "misconfigured",
            "notes": ["Set DATABASE_URL to your private Postgres/MySQL connection string."],
        }

    try:
        from sqlalchemy import create_engine, text

        engine = create_engine(settings.database_url, pool_pre_ping=True)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"status": "connected", "notes": []}
    except ImportError:
        return {
            "status": "ready",
            "notes": [
                "Install database extra: uv sync --extra database",
                "Then implement query helpers in this module.",
            ],
        }
    except Exception as exc:
        logger.warning("Database connection failed: %s", exc)
        return {"status": "unavailable", "notes": [str(exc)]}


def list_table_row_counts(tables: list[str] | None = None) -> dict[str, Any]:
    """Example row counts for private Postgres — customize SQL for your schema."""
    connection = check_connection()
    if connection.get("status") not in {"connected"}:
        return {"tables": [], **connection}

    try:
        from sqlalchemy import create_engine, text

        target_tables = tables or ["users", "sessions", "events"]
        engine = create_engine(settings.database_url, pool_pre_ping=True)
        rows: list[dict[str, Any]] = []
        with engine.connect() as conn:
            for table in target_tables:
                result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                count = result.scalar_one()
                rows.append({"name": table, "row_count": int(count)})
        return {"tables": rows, "status": "connected", "notes": []}
    except Exception as exc:
        logger.warning("Database table query failed: %s", exc)
        return {"tables": [], "status": "error", "notes": [str(exc)]}
