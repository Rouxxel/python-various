"""
#############################################################################
### WebSocket root endpoint
###
### @file ws_root.py
### @author Sebastian Russo
### @date 2025
#############################################################################

Main WebSocket endpoint: accept connections, receive/send messages, handle disconnect.
"""

# Third-party imports
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

# Other files imports
from src.utils.custom_logger import log_handler
from src.core_specs.configuration.config_loader import config_loader

ws_config = config_loader["endpoints"]["websocket_endpoint"]
router = APIRouter(prefix=ws_config["endpoint_prefix"], tags=[ws_config["endpoint_tag"]])


@router.websocket(ws_config["ws_route"])
async def websocket_root(websocket: WebSocket):
    """
    WebSocket endpoint: accept client, echo messages, log disconnect.
    """
    await websocket.accept()
    log_handler.info("WebSocket client connected")
    try:
        while True:
            data = await websocket.receive_text()
            log_handler.debug(f"WebSocket received: {data}")
            await websocket.send_text(f"Echo: {data}")
    except WebSocketDisconnect:
        log_handler.info("WebSocket client disconnected")
