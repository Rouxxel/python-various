"""
Health check for the local RPC backend (not a REST resource catalog).
"""

from fastapi import APIRouter, Request

from src.core_specs.configuration.config_loader import config_loader
from src.resources.cache.redis_client import get_redis_status
from src.rpc.rpc_registry import PROCEDURE_REGISTRY
from src.utils.custom_logger import log_handler
from src.utils.limiter import limiter as SlowLimiter

router = APIRouter(
    prefix=config_loader["endpoints"]["root_directory_endpoint"]["endpoint_prefix"],
    tags=[config_loader["endpoints"]["root_directory_endpoint"]["endpoint_tag"]],
)


@router.get(config_loader["endpoints"]["root_directory_endpoint"]["endpoint_route"])
@SlowLimiter.limit(
    f"{config_loader['endpoints']['root_directory_endpoint']['request_limit']}/"
    f"{config_loader['endpoints']['root_directory_endpoint']['unit_of_time_for_limit']}"
)
async def root_endpoint(request: Request):
    log_handler.debug("RPC backend health check")
    return {
        "status": "ok",
        "style": "rpc",
        "message": "Local RPC backend is running",
        "registered_procedures": sorted(PROCEDURE_REGISTRY.keys()),
        "redis": get_redis_status(),
    }
