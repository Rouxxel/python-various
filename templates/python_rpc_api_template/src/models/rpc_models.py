"""
Pydantic models for RPC-style requests and responses.

Procedure parameters are typed per operation; the invoke gateway accepts a
generic params dict and validates inside each handler.
"""

from __future__ import annotations

from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field


class RpcErrorCode(str, Enum):
    INVALID_REQUEST = "invalid_request"
    METHOD_NOT_FOUND = "method_not_found"
    VALIDATION_ERROR = "validation_error"
    NOT_FOUND = "not_found"
    CONFLICT = "conflict"
    INTERNAL_ERROR = "internal_error"


class RpcError(BaseModel):
    code: RpcErrorCode
    message: str
    details: Optional[Dict[str, Any]] = None


class RpcInvokeRequest(BaseModel):
    """Body for POST /rpc/invoke — dispatches by method name."""

    method: str = Field(..., min_length=1, description="Registered procedure name")
    params: Dict[str, Any] = Field(default_factory=dict)


class RpcInvokeResponse(BaseModel):
    ok: bool
    result: Optional[Any] = None
    error: Optional[RpcError] = None


class AgentRunStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"


class StartExampleAgentRunParams(BaseModel):
    review_id: str = Field(..., min_length=1)
    prompt: str = Field(default="Review this change set.", min_length=1)


class GetExampleRunStatusParams(BaseModel):
    run_id: str = Field(..., min_length=1)


class CancelExampleRunParams(BaseModel):
    run_id: str = Field(..., min_length=1)


class ListExampleRunsParams(BaseModel):
    review_id: Optional[str] = None
    limit: int = Field(default=20, ge=1, le=100)


class AgentRunEvent(BaseModel):
    seq: int
    run_id: str
    type: str
    message: str
    payload: Optional[Dict[str, Any]] = None


class AgentRunSummary(BaseModel):
    run_id: str
    review_id: str
    status: AgentRunStatus
    prompt: str


class AgentRunDetail(AgentRunSummary):
    events: List[AgentRunEvent] = Field(default_factory=list)
