"""
#############################################################################
### Main backend file
###
### @file main.py
### @author Sebastian Russo
### @date 2025
#############################################################################

Local RPC-style HTTP + JSON backend for a review UI. Uses procedure calls and
SSE streaming for long agent runs — not a resource-oriented REST API.
"""

import os
from contextlib import asynccontextmanager

import uvicorn
from dotenv import load_dotenv
from fastapi import FastAPI
from slowapi.errors import RateLimitExceeded

load_dotenv()

from src.core_specs.configuration.config_loader import config_loader
from src.core_specs.data.data_loader import data_loader
from src.resources.cache.redis_client import close_redis
from src.rpc_endpoints.procedures.invoke_procedure import router as invoke_router
from src.rpc_endpoints.procedures.start_agent_run_procedure import (
    router as start_agent_run_router,
)
from src.rpc_endpoints.procedures.stream_agent_run_procedure import (
    router as stream_agent_run_router,
)
from src.rpc_endpoints.root_endpoint import router as root_router
from src.utils.custom_logger import log_handler
from src.utils.limiter import limiter
from src.utils.request_limiter import rate_limit_handler


@asynccontextmanager
async def lifespan(app: FastAPI):
    port = config_loader["network"]["server_port"]
    log_handler.info(f"RPC API Template server starting on port {port}")
    yield
    close_redis()
    log_handler.info("RPC API Template server shutting down")


app = FastAPI(
    lifespan=lifespan,
    title=os.getenv("API_TITLE", "RPC API Template"),
    version=os.getenv("API_VERSION", "1.0.0"),
    description=os.getenv(
        "API_DESCRIPTION",
        "Local RPC-style HTTP + JSON API with streaming for long agent runs",
    ),
)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, rate_limit_handler)

app.include_router(root_router)
app.include_router(invoke_router)
app.include_router(start_agent_run_router)
app.include_router(stream_agent_run_router)


if __name__ == "__main__":
    port = config_loader["network"]["server_port"]

    uvicorn.run(
        config_loader["network"]["uvicorn_app_reference"],
        host=config_loader["network"]["host"],
        port=port,
        reload=config_loader["network"]["reload"],
        workers=config_loader["network"]["workers"],
        proxy_headers=config_loader["network"]["proxy_headers"],
    )

    log_handler(f"Loaded configuration: \n {config_loader}")
    log_handler(f"Loaded data: \n {data_loader}")
