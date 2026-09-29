"""
In-memory example agent runs for the RPC template.

Replace with your real agent orchestration; keep the same return shapes so
procedure handlers stay thin.
"""

from __future__ import annotations

import asyncio
import uuid
from collections import deque
from dataclasses import dataclass, field
from typing import AsyncIterator, Deque, Dict, List, Optional

from src.models.rpc_models import (
    AgentRunDetail,
    AgentRunEvent,
    AgentRunStatus,
    AgentRunSummary,
)
from src.utils.custom_logger import log_handler

_RUNS: Dict[str, "AgentRunState"] = {}
_LOCK = asyncio.Lock()


@dataclass
class AgentRunState:
    summary: AgentRunSummary
    events: Deque[AgentRunEvent] = field(default_factory=deque)
    subscribers: List[asyncio.Queue[AgentRunEvent]] = field(default_factory=list)
    task: Optional[asyncio.Task[None]] = None
    cancel_requested: bool = False
    _seq: int = 0

    def append_event(self, event_type: str, message: str, payload: Optional[dict] = None) -> AgentRunEvent:
        self._seq += 1
        event = AgentRunEvent(
            seq=self._seq,
            run_id=self.summary.run_id,
            type=event_type,
            message=message,
            payload=payload,
        )
        self.events.append(event)
        for queue in list(self.subscribers):
            queue.put_nowait(event)
        return event


async def _simulate_agent_run(state: AgentRunState) -> None:
    try:
        state.summary.status = AgentRunStatus.RUNNING
        state.append_event("status", "Run started")

        steps = [
            ("plan", "Planning review steps"),
            ("fetch", "Loading diff context"),
            ("analyze", "Running agent analysis"),
            ("summarize", "Writing summary"),
        ]
        for step_type, step_message in steps:
            if state.cancel_requested:
                state.summary.status = AgentRunStatus.CANCELLED
                state.append_event("cancelled", "Run cancelled by client")
                return
            state.append_event(step_type, step_message)
            await asyncio.sleep(0.8)

        state.summary.status = AgentRunStatus.COMPLETED
        state.append_event(
            "completed",
            "Run finished",
            payload={"verdict": "needs_changes", "confidence": 0.82},
        )
    except asyncio.CancelledError:
        state.summary.status = AgentRunStatus.CANCELLED
        state.append_event("cancelled", "Run task cancelled")
        raise
    except Exception as exc:  # pragma: no cover - template demo guard
        log_handler.exception("Agent run failed: %s", exc)
        state.summary.status = AgentRunStatus.FAILED
        state.append_event("error", str(exc))


async def start_example_agent_run(review_id: str, prompt: str) -> AgentRunSummary:
    run_id = str(uuid.uuid4())
    summary = AgentRunSummary(
        run_id=run_id,
        review_id=review_id,
        status=AgentRunStatus.PENDING,
        prompt=prompt,
    )
    state = AgentRunState(summary=summary)

    async with _LOCK:
        _RUNS[run_id] = state

    state.task = asyncio.create_task(_simulate_agent_run(state))
    log_handler.info("Started example agent run %s for review %s", run_id, review_id)
    return summary


async def list_example_runs(review_id: Optional[str], limit: int) -> List[AgentRunSummary]:
    async with _LOCK:
        runs = list(_RUNS.values())

    if review_id:
        runs = [state for state in runs if state.summary.review_id == review_id]

    runs.sort(key=lambda state: state.summary.run_id, reverse=True)
    return [state.summary for state in runs[:limit]]


async def get_example_run_status(run_id: str) -> Optional[AgentRunDetail]:
    async with _LOCK:
        state = _RUNS.get(run_id)
        if state is None:
            return None

    return AgentRunDetail(
        **state.summary.model_dump(),
        events=list(state.events),
    )


async def cancel_example_run(run_id: str) -> Optional[AgentRunSummary]:
    async with _LOCK:
        state = _RUNS.get(run_id)
        if state is None:
            return None

    if state.summary.status in (AgentRunStatus.COMPLETED, AgentRunStatus.FAILED, AgentRunStatus.CANCELLED):
        return state.summary

    state.cancel_requested = True
    if state.task and not state.task.done():
        state.task.cancel()
    return state.summary


async def subscribe_example_run_events(
    run_id: str,
    after_seq: int = 0,
) -> AsyncIterator[AgentRunEvent]:
    async with _LOCK:
        state = _RUNS.get(run_id)
        if state is None:
            raise KeyError(run_id)

        queue: asyncio.Queue[AgentRunEvent] = asyncio.Queue()
        state.subscribers.append(queue)

    last_seq = after_seq
    try:
        for event in state.events:
            if event.seq > last_seq:
                last_seq = event.seq
                yield event

        while state.summary.status in (AgentRunStatus.PENDING, AgentRunStatus.RUNNING):
            event = await queue.get()
            if event.seq > last_seq:
                last_seq = event.seq
                yield event
    finally:
        if queue in state.subscribers:
            state.subscribers.remove(queue)
