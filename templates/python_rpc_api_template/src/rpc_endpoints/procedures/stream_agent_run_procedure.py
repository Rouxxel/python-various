"""
Server-Sent Events stream for long agent runs: GET /rpc/streamExampleAgentRun
"""

import json
from typing import AsyncIterator

from fastapi import APIRouter, HTTPException, Query, Request
from starlette.responses import StreamingResponse

from src.core_specs.configuration.config_loader import config_loader
from src.resources.agent_run_service import get_example_run_status, subscribe_example_run_events
from src.utils.custom_logger import log_handler
from src.utils.limiter import limiter as SlowLimiter

_cfg = config_loader["endpoints"]["rpc_stream_agent_run_procedure"]

router = APIRouter(
    prefix=_cfg["endpoint_prefix"],
    tags=[_cfg["endpoint_tag"]],
)


async def _event_stream(run_id: str, after_seq: int) -> AsyncIterator[str]:
    try:
        event_iter = subscribe_example_run_events(run_id, after_seq=after_seq)
    except KeyError:
        yield 'data: {"error":"Run not found"}\n\n'
        return

    async for event in event_iter:
        payload = json.dumps(event.model_dump(), ensure_ascii=False)
        yield f"data: {payload}\n\n"


@router.get(_cfg["endpoint_route"])
@SlowLimiter.limit(f"{_cfg['request_limit']}/{_cfg['unit_of_time_for_limit']}")
async def stream_example_agent_run(
    request: Request,
    run_id: str = Query(..., min_length=1),
    after_seq: int = Query(default=0, ge=0),
):
    log_handler.debug("Streaming run %s after seq %s", run_id, after_seq)
    if await get_example_run_status(run_id) is None:
        raise HTTPException(status_code=404, detail="Run not found")

    return StreamingResponse(
        _event_stream(run_id, after_seq),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
