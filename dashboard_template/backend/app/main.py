"""FastAPI dashboard application entry point."""

import os
from contextlib import asynccontextmanager

import httpx
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.logging_config import setup_logging
from app.middleware import (
    CorrelationIdMiddleware,
    DashboardEnvironmentMiddleware,
    RequestLoggingMiddleware,
)
from app.routers import (
    activity,
    ai,
    config,
    costs,
    infrastructure,
    overview,
    sessions,
    users,
)
from app.services.providers import get_provider_status

setup_logging(settings.log_level)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle: shared HTTP client."""
    app.state.http_client = httpx.AsyncClient(timeout=httpx.Timeout(35.0))
    yield
    await app.state.http_client.aclose()


app = FastAPI(title="Analytics Dashboard", version="1.0.0", lifespan=lifespan)

# Add middleware (LIFO order)
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(DashboardEnvironmentMiddleware)
app.add_middleware(CorrelationIdMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.dashboard_frontend_url, "http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers (paths match frontend api.ts)
app.include_router(config.router, prefix="/api")
app.include_router(overview.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(sessions.router, prefix="/api")
app.include_router(activity.router, prefix="/api")
app.include_router(ai.router, prefix="/api")
app.include_router(infrastructure.router, prefix="/api")
app.include_router(costs.router, prefix="/api")


@app.get("/api/health")
async def health() -> dict:
    """Health check endpoint."""
    return {
        "status": "ok",
        "data_mode": settings.dashboard_data_mode,
        "providers": get_provider_status(),
    }


if __name__ == "__main__":
    host = settings.dashboard_backend_host
    if os.getenv("PORT"):
        host = "0.0.0.0"
    uvicorn.run(
        "app.main:app",
        host=host,
        port=settings.dashboard_backend_port,
        reload=True,
        log_level=settings.log_level.lower(),
    )
