"""FastAPI dashboard application entry point."""

import os
from contextlib import asynccontextmanager

import httpx
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.core_specs.configuration.config_loader import config_loader
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
    health,
    infrastructure,
    overview,
    sessions,
    users,
)
from app.utils.custom_logger import log_handler, shutdown_logger

_app_cfg = config_loader["app"]
_network = config_loader["network"]
API_PREFIX = _app_cfg["api_prefix"]


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle: shared HTTP client."""
    log_handler.info(
        "Dashboard backend starting (mode=%s, port=%s)",
        settings.dashboard_data_mode,
        settings.dashboard_backend_port,
    )
    app.state.http_client = httpx.AsyncClient(timeout=httpx.Timeout(35.0))
    yield
    await app.state.http_client.aclose()
    shutdown_logger()


app = FastAPI(
    title=_app_cfg["title"],
    version=_app_cfg["version"],
    lifespan=lifespan,
)

app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(DashboardEnvironmentMiddleware)
app.add_middleware(CorrelationIdMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.dashboard_frontend_url, "http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix=API_PREFIX)
app.include_router(config.router, prefix=API_PREFIX)
app.include_router(overview.router, prefix=API_PREFIX)
app.include_router(users.router, prefix=API_PREFIX)
app.include_router(sessions.router, prefix=API_PREFIX)
app.include_router(activity.router, prefix=API_PREFIX)
app.include_router(ai.router, prefix=API_PREFIX)
app.include_router(infrastructure.router, prefix=API_PREFIX)
app.include_router(costs.router, prefix=API_PREFIX)


if __name__ == "__main__":
    host = settings.dashboard_backend_host
    if os.getenv("PORT"):
        host = "0.0.0.0"
    uvicorn.run(
        _network["uvicorn_app_reference"],
        host=host,
        port=settings.dashboard_backend_port,
        reload=_network["reload"],
        workers=_network["workers"],
        proxy_headers=_network["proxy_headers"],
        log_level=settings.log_level.lower(),
    )
