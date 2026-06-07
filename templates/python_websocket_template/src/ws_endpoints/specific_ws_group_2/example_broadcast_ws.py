"""
#############################################################################
### Example WebSocket endpoint - broadcast / chat room
###
### @file example_broadcast_ws.py
### @author Sebastian Russo
### @date 2026
#############################################################################

Reference WebSocket handler for this template. Copy this file (and its matching
``config_file.json`` entry) when adding new WebSocket endpoint groups.

ONLY ONE WEBSOCKET ENDPOINT SHOULD BE IN THIS FILE. For other endpoints they
should be in their own file but within this same folder, in order to have a
more organized code in folders and not a single endless file.

Demonstrates the multi-connection pattern that ``example_echo_ws.py`` does not:
    - ``connection_manager`` (shared ``ConnectionManager``) to track every live
      client and fan a single message out to all of them
    - Pydantic models to validate inbound frames (``ChatMessageIn``)
    - A single typed outgoing envelope (``WsMessageOut``) for every reply
    - ``config_loader`` for prefix, tag, and the WebSocket route path
    - ``log_handler`` for structured logging

This is the canonical chat-room shape: register on connect, broadcast each
valid message to everyone, and always unregister in a ``finally`` so a dropped
client cannot leak into the registry.
"""

#Native imports
import json

#Third-party imports
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import ValidationError

#Other files imports
from src.utils.custom_logger import log_handler
from src.core_specs.configuration.config_loader import config_loader
from src.utils.ws_connection_manager import connection_manager
from src.models.ws_messages_example import ChatMessageIn, WsMessageOut

"""WS ROUTER-----------------------------------------------------------"""
router = APIRouter(
    prefix=config_loader["endpoints"]["example_ws_endpoint_2"]["endpoint_prefix"],
    tags=[config_loader["endpoints"]["example_ws_endpoint_2"]["endpoint_tag"]],
)

"""ENDPOINTS-----------------------------------------------------------"""
@router.websocket(config_loader["endpoints"]["example_ws_endpoint_2"]["ws_route"])
async def example_broadcast_ws(websocket: WebSocket):
    """
    Broadcast endpoint (simple chat room).

    Every connected client is registered with the shared ``connection_manager``.
    Each valid inbound ``ChatMessageIn`` is wrapped in a ``WsMessageOut`` and
    sent to all connected clients. Invalid frames get an ``error`` envelope sent
    only to the offending client.

    Parameters:
        websocket (WebSocket): The incoming client connection.
    """
    await connection_manager.connect(websocket)
    try:
        while True:
            raw = await websocket.receive_text()
            log_handler.debug("Broadcast received raw frame: %s", raw)

            #Parse + validate the inbound frame against the Pydantic model.
            try:
                payload = ChatMessageIn(**json.loads(raw))
            except (json.JSONDecodeError, ValidationError) as exc:
                error = WsMessageOut(type="error", data={"detail": str(exc)})
                await connection_manager.send_personal(error.model_dump(), websocket)
                continue

            message = WsMessageOut(
                type="chat",
                data={"username": payload.username, "text": payload.text},
            )
            await connection_manager.broadcast(message.model_dump())
    except WebSocketDisconnect:
        connection_manager.disconnect(websocket)
        #Let the remaining clients know someone left.
        await connection_manager.broadcast(
            WsMessageOut(type="system", data={"detail": "a client disconnected"}).model_dump()
        )
