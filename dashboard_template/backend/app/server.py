"""Production ASGI entry point."""

import os

import uvicorn

from app.core_specs.configuration.config_loader import config_loader
from app.config import settings

_network = config_loader["network"]

if __name__ == "__main__":
    host = os.getenv("DASHBOARD_BACKEND_HOST", _network["host"])
    if os.getenv("PORT"):
        host = "0.0.0.0"
    port = settings.dashboard_backend_port
    uvicorn.run(
        _network["uvicorn_app_reference"],
        host=host,
        port=port,
        workers=_network["workers"],
        proxy_headers=_network["proxy_headers"],
        log_level=settings.log_level.lower(),
    )
