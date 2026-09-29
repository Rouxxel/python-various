"""
Unified RPC gateway: POST /rpc/invoke with { method, params }.
"""

from typing import Any

from fastapi import APIRouter, Request
from pydantic import BaseModel

from src.core_specs.configuration.config_loader import config_loader
from src.models.rpc_models import RpcInvokeRequest, RpcInvokeResponse
from src.rpc.rpc_registry import RpcProcedureError, invoke_procedure
from src.utils.custom_logger import log_handler
from src.utils.limiter import limiter as SlowLimiter

_cfg = config_loader["endpoints"]["rpc_invoke_procedure"]

router = APIRouter(
    prefix=_cfg["endpoint_prefix"],
    tags=[_cfg["endpoint_tag"]],
)


def _to_jsonable(value: Any) -> Any:
    if isinstance(value, BaseModel):
        return value.model_dump()
    if isinstance(value, list):
        return [_to_jsonable(item) for item in value]
    return value


@router.post(_cfg["endpoint_route"])
@SlowLimiter.limit(f"{_cfg['request_limit']}/{_cfg['unit_of_time_for_limit']}")
async def invoke_rpc_procedure(
    request: Request,
    body: RpcInvokeRequest,
) -> RpcInvokeResponse:
    log_handler.debug("RPC invoke: %s", body.method)
    try:
        result = await invoke_procedure(body.method, body.params)
        return RpcInvokeResponse(ok=True, result=_to_jsonable(result))
    except RpcProcedureError as exc:
        return RpcInvokeResponse(ok=False, error=exc.error)
