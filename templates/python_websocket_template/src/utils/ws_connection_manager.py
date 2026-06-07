"""
#############################################################################
### WebSocket connection manager file
###
### @file ws_connection_manager.py
### @author Sebastian Russo
### @date 2026
#############################################################################

Shared helper for tracking active WebSocket connections and broadcasting
messages to all of them.

A single ``ConnectionManager`` instance is created at import time (just like
the shared ``limiter`` in the REST template) so every endpoint that needs to
fan a message out to all connected clients reuses the same registry. Import
``connection_manager`` wherever you need it; do NOT instantiate your own.

For a single-process deployment the in-memory ``set`` below is enough. If you
run multiple workers/replicas, connections live in different processes and an
in-memory set will not reach them - back broadcasts with Redis pub/sub (or a
similar message broker) instead.
"""

#Native imports
from typing import List

#Third-party imports
from fastapi import WebSocket

#Other files imports
from src.utils.custom_logger import log_handler


class ConnectionManager:
    """
    Tracks active WebSocket connections and broadcasts messages to them.

    Methods:
        connect: Accept a socket and register it.
        disconnect: Remove a socket from the registry.
        send_personal: Send JSON to one specific client.
        broadcast: Send JSON to every connected client.
    """

    def __init__(self) -> None:
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> None:
        """
        Accept the handshake and register the connection.

        Parameters:
            websocket (WebSocket): The incoming connection to accept.
        """
        await websocket.accept()
        self.active_connections.append(websocket)
        log_handler.info(
            "WebSocket connected (%d active)", len(self.active_connections)
        )

    def disconnect(self, websocket: WebSocket) -> None:
        """
        Remove a connection from the registry (call on disconnect).

        Parameters:
            websocket (WebSocket): The connection to drop.
        """
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
        log_handler.info(
            "WebSocket disconnected (%d active)", len(self.active_connections)
        )

    async def send_personal(self, message: dict, websocket: WebSocket) -> None:
        """
        Send a JSON message to a single client.

        Parameters:
            message (dict): JSON-serializable payload.
            websocket (WebSocket): Target connection.
        """
        await websocket.send_json(message)

    async def broadcast(self, message: dict) -> None:
        """
        Send a JSON message to every connected client.

        Dead connections that raise on send are dropped so one stale socket
        cannot block delivery to the rest.

        Parameters:
            message (dict): JSON-serializable payload to fan out.
        """
        stale: List[WebSocket] = []
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except Exception:  # pylint: disable=broad-except
                stale.append(connection)

        for connection in stale:
            self.disconnect(connection)


"""VARIABLES-----------------------------------------------------------"""
#Single shared instance reused by every endpoint; import this, do not re-create.
connection_manager = ConnectionManager()
