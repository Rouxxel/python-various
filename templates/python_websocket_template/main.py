"""
#############################################################################
### Main backend file
###
### @file main.py
### @author Sebastian Russo
### @date 2025
#############################################################################

Initializes the FastAPI app with WebSocket and HTTP health check.
"""

# Native imports
import os
from contextlib import asynccontextmanager

# Third-party imports
import uvicorn
from fastapi import FastAPI
from dotenv import load_dotenv

load_dotenv()

# Other files imports
from src.utils.custom_logger import log_handler
from src.core_specs.configuration.config_loader import config_loader
from src.core_specs.data.data_loader import data_loader
from src.api_endpoints.root_endpoint import router as root_router
from src.ws_endpoints.ws_root import router as ws_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan: log startup and shutdown."""
    port = config_loader["network"]["server_port"]
    log_handler.info(f"WebSocket Template server starting on port {port}")
    yield
    log_handler.info("WebSocket Template server shutting down")


app = FastAPI(
    lifespan=lifespan,
    title=os.getenv("API_TITLE", "WebSocket Template"),
    version=os.getenv("API_VERSION", "1.0.0"),
    description=os.getenv("API_DESCRIPTION", "WebSocket backend template with FastAPI"),
)

app.include_router(root_router)
app.include_router(ws_router)

if __name__ == "__main__":
    port = config_loader["network"]["server_port"]
    uvicorn.run(
        config_loader["network"]["uvicorn_app_reference"],
        host=config_loader["network"]["host"],
        port=config_loader["network"]["server_port"],
        reload=config_loader["network"]["reload"],
        workers=config_loader["network"]["workers"],
        proxy_headers=config_loader["network"]["proxy_headers"],
    )
