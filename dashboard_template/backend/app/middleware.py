"""HTTP middleware for the dashboard backend."""

import logging
import uuid
from typing import Literal

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response

from app.config import settings

logger = logging.getLogger(__name__)

DashboardEnvironment = Literal["test", "prod"]


class CorrelationIdMiddleware(BaseHTTPMiddleware):
    """Attach a correlation ID to each request/response."""

    async def dispatch(self, request: Request, call_next) -> Response:
        correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
        request.state.correlation_id = correlation_id
        response = await call_next(request)
        response.headers["X-Correlation-ID"] = correlation_id
        return response


class DashboardEnvironmentMiddleware(BaseHTTPMiddleware):
    """Read X-Dashboard-Environment header and expose data mode on responses."""

    async def dispatch(self, request: Request, call_next) -> Response:
        env_header = request.headers.get("X-Dashboard-Environment", "test")
        request.state.dashboard_environment = (
            "prod" if env_header.lower() == "prod" else "test"
        )
        response = await call_next(request)
        response.headers["X-Data-Mode"] = settings.dashboard_data_mode
        return response


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log incoming requests at debug level."""

    async def dispatch(self, request: Request, call_next) -> Response:
        logger.debug(
            "%s %s env=%s",
            request.method,
            request.url.path,
            getattr(request.state, "dashboard_environment", "test"),
        )
        return await call_next(request)
