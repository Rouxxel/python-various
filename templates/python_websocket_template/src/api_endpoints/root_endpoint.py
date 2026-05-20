"""
#############################################################################
### Root HTTP endpoint (health check)
###
### @file root_endpoint.py
### @author Sebastian Russo
### @date 2025
#############################################################################

HTTP GET / for health checks (e.g. Docker, load balancers).
"""

# Third-party imports
from fastapi import APIRouter

# Other files imports
from src.utils.custom_logger import log_handler
from src.core_specs.configuration.config_loader import config_loader

root_config = config_loader["endpoints"]["root_directory_endpoint"]
router = APIRouter(
    prefix=root_config["endpoint_prefix"],
    tags=[root_config["endpoint_tag"]],
)


@router.get(root_config["endpoint_route"])
async def root_endpoint():
    """Health check: returns OK when the server and WebSocket app are up."""
    log_handler.debug("Health check requested")
    return {"message": "WebSocket backend running", "status": "ok"}
