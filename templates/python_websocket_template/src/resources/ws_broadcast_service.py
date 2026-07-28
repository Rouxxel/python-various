"""
#############################################################################
### WebSocket broadcast service module
###
### @file ws_broadcast_service.py
### @date 2026
#############################################################################

Fan-out helper for WebSocket messages. Endpoints call this module instead of
using Redis directly or calling ``connection_manager.broadcast`` for room-wide
delivery across replicas.
"""

#Other files imports
from src.resources.cache.redis_pubsub_service import is_pubsub_available, publish_broadcast
from src.utils.custom_logger import log_handler
from src.utils.ws_connection_manager import connection_manager


async def broadcast(message: dict) -> None:
    """
    Deliver a JSON message to all connected clients.

    When Redis pub/sub is available, publishes to the shared channel and each
    process (including this one) delivers to its local sockets via the listener.
    Otherwise falls back to in-process delivery only.
    """
    if is_pubsub_available():
        if publish_broadcast(message):
            return
        log_handler.warning("Redis publish failed; falling back to local broadcast")

    await connection_manager.broadcast_local(message)


async def deliver_local_broadcast(message: dict) -> None:
    """Deliver a message to every socket on this process (pub/sub callback)."""
    await connection_manager.broadcast_local(message)
