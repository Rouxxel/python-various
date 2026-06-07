"""
#############################################################################
### Example WebSocket endpoint - structured echo
###
### @file example_echo_ws.py
### @author Sebastian Russo
### @date 2026
#############################################################################

Reference WebSocket handler for this template. Copy this file (and its matching
``config_file.json`` entry) when adding new WebSocket endpoint groups.

ONLY ONE WEBSOCKET ENDPOINT SHOULD BE IN THIS FILE. For other endpoints they
should be in their own file but within this same folder, in order to have a
more organized code in folders and not a single endless file.

Demonstrates:
    - ``config_loader`` for prefix, tag, and the WebSocket route path
    - Pydantic models to validate every inbound message frame (``src/models/``)
    - ``validators`` for input checks (optional ``contact_email``)
    - ``data_loader`` for static reference data
    - ``log_handler`` for structured logging
    - A single typed outgoing envelope (``WsMessageOut``) for every reply

Unlike a REST route, a WebSocket handler runs a receive loop for the lifetime
of the connection. The pattern below - accept, loop while validating each
frame, and always handle ``WebSocketDisconnect`` - is what you copy for new
endpoints.
"""

#Native imports
import json

#Third-party imports
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from pydantic import ValidationError

#Other files imports
from src.utils.custom_logger import log_handler
from src.core_specs.configuration.config_loader import config_loader
from src.core_specs.data.data_loader import data_loader
from src.utils.validators import validate_email_format
from src.models.ws_messages_example import EchoMessageIn, WsMessageOut

"""WS ROUTER-----------------------------------------------------------"""
router = APIRouter(
    prefix=config_loader["endpoints"]["example_ws_endpoint_1"]["endpoint_prefix"],
    tags=[config_loader["endpoints"]["example_ws_endpoint_1"]["endpoint_tag"]],
)

"""ENDPOINTS-----------------------------------------------------------"""
@router.websocket(config_loader["endpoints"]["example_ws_endpoint_1"]["ws_route"])
async def example_echo_ws(websocket: WebSocket):
    """
    Structured echo endpoint.

    Each inbound frame is expected to be JSON matching ``EchoMessageIn``. The
    handler validates it, optionally checks ``contact_email``, and replies with
    a typed ``WsMessageOut`` envelope. Invalid frames get an ``error`` envelope
    rather than tearing the connection down.

    Parameters:
        websocket (WebSocket): The incoming client connection.
    """
    await websocket.accept()
    log_handler.info(
        "Echo client connected (supported languages: %s)",
        data_loader.get("languages", []),
    )

    try:
        while True:
            raw = await websocket.receive_text()
            log_handler.debug("Echo received raw frame: %s", raw)

            #Parse + validate the inbound frame against the Pydantic model.
            try:
                payload = EchoMessageIn(**json.loads(raw))
            except (json.JSONDecodeError, ValidationError) as exc:
                error = WsMessageOut(type="error", data={"detail": str(exc)})
                await websocket.send_json(error.model_dump())
                continue

            #Optional field check using the shared validators helper.
            if payload.contact_email is not None:
                try:
                    validate_email_format(payload.contact_email)
                except Exception as exc:  # pylint: disable=broad-except
                    error = WsMessageOut(
                        type="error", data={"detail": f"invalid email: {exc}"}
                    )
                    await websocket.send_json(error.model_dump())
                    continue

            response = WsMessageOut(
                type="echo",
                data={"name": payload.name, "message": payload.message},
            )
            await websocket.send_json(response.model_dump())
    except WebSocketDisconnect:
        log_handler.info("Echo client disconnected")
