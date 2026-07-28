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
import asyncio
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
from src.resources.cache.redis_client import close_redis
from src.resources.cache.redis_pubsub_service import (
    start_broadcast_listener,
    stop_broadcast_listener,
)
from src.resources.ws_broadcast_service import deliver_local_broadcast
from src.api_endpoints.root_endpoint import router as root_router
from src.ws_endpoints.ws_root import router as ws_router
from src.ws_endpoints.specific_ws_group_1.example_echo_ws import router as example_ws_router_1
from src.ws_endpoints.specific_ws_group_2.example_broadcast_ws import router as example_ws_router_2


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan: log startup, start optional Redis pub/sub, shutdown cleanly."""
    port = config_loader["network"]["server_port"]
    log_handler.info(f"WebSocket Template server starting on port {port}")
    loop = asyncio.get_running_loop()
    start_broadcast_listener(loop, deliver_local_broadcast)
    yield
    stop_broadcast_listener()
    close_redis()
    log_handler.info("WebSocket Template server shutting down")


app = FastAPI(
    lifespan=lifespan,
    title=os.getenv("API_TITLE", "WebSocket Template"),
    version=os.getenv("API_VERSION", "1.0.0"),
    description=os.getenv("API_DESCRIPTION", "WebSocket backend template with FastAPI"),
)

app.include_router(root_router)
app.include_router(ws_router)
app.include_router(example_ws_router_1)
app.include_router(example_ws_router_2)

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
