"""
Explicit action endpoint: POST /rpc/startExampleAgentRun

Same handler as the invoke registry; useful for UI clients that prefer one URL
per operation instead of a single /invoke gateway.
"""

from fastapi import APIRouter, Request

from src.core_specs.configuration.config_loader import config_loader
from src.models.rpc_models import AgentRunSummary, StartExampleAgentRunParams
from src.rpc.rpc_registry import RpcProcedureError, invoke_procedure
from src.utils.custom_logger import log_handler
from src.utils.limiter import limiter as SlowLimiter

_cfg = config_loader["endpoints"]["rpc_start_agent_run_procedure"]

router = APIRouter(
    prefix=_cfg["endpoint_prefix"],
    tags=[_cfg["endpoint_tag"]],
)


@router.post(_cfg["endpoint_route"], response_model=AgentRunSummary)
@SlowLimiter.limit(f"{_cfg['request_limit']}/{_cfg['unit_of_time_for_limit']}")
async def start_example_agent_run(
    request: Request,
    body: StartExampleAgentRunParams,
) -> AgentRunSummary:
    log_handler.info("Explicit startExampleAgentRun for review %s", body.review_id)
    try:
        result = await invoke_procedure(
            "startExampleAgentRun",
            body.model_dump(),
        )
        return result
    except RpcProcedureError as exc:
        from fastapi import HTTPException

        raise HTTPException(status_code=400, detail=exc.error.model_dump()) from exc
