"""
Registry of RPC procedure handlers for POST /rpc/invoke.

Each handler receives a params dict and returns a result object or raises
RpcProcedureError for structured client errors.
"""

from __future__ import annotations

from typing import Any, Awaitable, Callable, Dict, Type

from pydantic import BaseModel, ValidationError

from src.models.rpc_models import (
    AgentRunDetail,
    AgentRunSummary,
    CancelExampleRunParams,
    GetExampleRunStatusParams,
    ListExampleRunsParams,
    RpcError,
    RpcErrorCode,
    StartExampleAgentRunParams,
)
from src.resources.agent_run_service import (
    cancel_example_run,
    get_example_run_status,
    list_example_runs,
    start_example_agent_run,
)

RpcHandler = Callable[[Dict[str, Any]], Awaitable[Any]]


class RpcProcedureError(Exception):
    def __init__(self, error: RpcError) -> None:
        super().__init__(error.message)
        self.error = error


def _validate_params(model: Type[BaseModel], params: Dict[str, Any]) -> BaseModel:
    try:
        return model.model_validate(params)
    except ValidationError as exc:
        raise RpcProcedureError(
            RpcError(
                code=RpcErrorCode.VALIDATION_ERROR,
                message="Invalid procedure parameters",
                details={"errors": exc.errors()},
            )
        ) from exc


async def _ping(_params: Dict[str, Any]) -> Dict[str, str]:
    return {"message": "rpc backend ready"}


async def _list_example_runs(params: Dict[str, Any]) -> list[AgentRunSummary]:
    validated = _validate_params(ListExampleRunsParams, params)
    return await list_example_runs(validated.review_id, validated.limit)


async def _start_example_agent_run(params: Dict[str, Any]) -> AgentRunSummary:
    validated = _validate_params(StartExampleAgentRunParams, params)
    return await start_example_agent_run(validated.review_id, validated.prompt)


async def _get_example_run_status(params: Dict[str, Any]) -> AgentRunDetail:
    validated = _validate_params(GetExampleRunStatusParams, params)
    detail = await get_example_run_status(validated.run_id)
    if detail is None:
        raise RpcProcedureError(
            RpcError(
                code=RpcErrorCode.NOT_FOUND,
                message=f"Run not found: {validated.run_id}",
            )
        )
    return detail


async def _cancel_example_run(params: Dict[str, Any]) -> AgentRunSummary:
    validated = _validate_params(CancelExampleRunParams, params)
    summary = await cancel_example_run(validated.run_id)
    if summary is None:
        raise RpcProcedureError(
            RpcError(
                code=RpcErrorCode.NOT_FOUND,
                message=f"Run not found: {validated.run_id}",
            )
        )
    return summary


PROCEDURE_REGISTRY: Dict[str, RpcHandler] = {
    "ping": _ping,
    "listExampleRuns": _list_example_runs,
    "startExampleAgentRun": _start_example_agent_run,
    "getExampleRunStatus": _get_example_run_status,
    "cancelExampleRun": _cancel_example_run,
}


async def invoke_procedure(method: str, params: Dict[str, Any]) -> Any:
    handler = PROCEDURE_REGISTRY.get(method)
    if handler is None:
        raise RpcProcedureError(
            RpcError(
                code=RpcErrorCode.METHOD_NOT_FOUND,
                message=f"Unknown procedure: {method}",
            )
        )
    return await handler(params)
