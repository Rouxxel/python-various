"""
#############################################################################
### Redis pub/sub service module
###
### @file redis_pubsub_service.py
### @date 2026
#############################################################################

Optional Redis pub/sub for cross-instance WebSocket broadcasts.
Each process publishes messages; a background listener delivers them to
local connections only.
"""

#Native imports
import asyncio
import json
import os
import threading
from typing import Awaitable, Callable, Optional

#Other files imports
from src.resources.cache.redis_client import REDIS_ENABLED, redis_client
from src.utils.custom_logger import log_handler

BROADCAST_CHANNEL = os.getenv("REDIS_WS_BROADCAST_CHANNEL", "ws:broadcast")

_listener_thread: Optional[threading.Thread] = None
_stop_event = threading.Event()


def is_pubsub_available() -> bool:
    """Return True when Redis pub/sub can be used for broadcasts."""
    return REDIS_ENABLED and redis_client is not None


def publish_broadcast(message: dict) -> bool:
    """
    Publish a JSON message to the shared broadcast channel.

    Returns:
        True if published successfully, False otherwise.
    """
    if redis_client is None:
        return False
    try:
        redis_client.publish(BROADCAST_CHANNEL, json.dumps(message))
        return True
    except Exception as exc:
        log_handler.warning("Redis publish failed: %s", exc)
        return False


def start_broadcast_listener(
    loop: asyncio.AbstractEventLoop,
    on_message: Callable[[dict], Awaitable[None]],
) -> None:
    """
    Start a daemon thread that forwards pub/sub messages to the event loop.

    Parameters:
        loop: The running asyncio event loop (from FastAPI lifespan).
        on_message: Async callback invoked for each decoded broadcast payload.
    """
    global _listener_thread

    if not is_pubsub_available():
        log_handler.info(
            "Redis pub/sub listener not started (Redis disabled or unavailable)"
        )
        return

    def _run() -> None:
        pubsub = redis_client.pubsub(ignore_subscribe_messages=True)
        pubsub.subscribe(BROADCAST_CHANNEL)
        log_handler.info("Redis pub/sub listening on channel %s", BROADCAST_CHANNEL)

        while not _stop_event.is_set():
            message = pubsub.get_message(timeout=1.0)
            if not message or message.get("type") != "message":
                continue
            try:
                payload = json.loads(message["data"])
                future = asyncio.run_coroutine_threadsafe(on_message(payload), loop)
                future.result(timeout=5)
            except Exception as exc:
                log_handler.warning("Failed to deliver pub/sub message: %s", exc)

        pubsub.unsubscribe(BROADCAST_CHANNEL)
        pubsub.close()
        log_handler.info("Redis pub/sub listener stopped")

    _stop_event.clear()
    _listener_thread = threading.Thread(
        target=_run, daemon=True, name="redis-ws-pubsub"
    )
    _listener_thread.start()


def stop_broadcast_listener() -> None:
    """Signal the pub/sub listener thread to stop and wait briefly."""
    global _listener_thread

    _stop_event.set()
    if _listener_thread is not None and _listener_thread.is_alive():
        _listener_thread.join(timeout=5)
    _listener_thread = None
