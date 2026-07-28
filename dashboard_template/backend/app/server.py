"""Production ASGI entry point."""

import os

import uvicorn

from app.main import app

if __name__ == "__main__":
    host = os.getenv("DASHBOARD_BACKEND_HOST", "0.0.0.0")
    port = int(os.getenv("PORT", os.getenv("DASHBOARD_BACKEND_PORT", "8001")))
    uvicorn.run("app.main:app", host=host, port=port, log_level="info")
