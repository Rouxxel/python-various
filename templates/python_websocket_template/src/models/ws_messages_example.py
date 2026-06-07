"""
#############################################################################
### Example WebSocket message models file
###
### @file ws_messages_example.py
### @author Sebastian Russo
### @date 2026
#############################################################################

Template Pydantic models for WebSocket message envelopes, meant to be either
deleted or renamed/extended to fit the current project requirements.

Unlike REST bodies, a WebSocket carries a stream of discrete messages over a
single connection. A common, scalable pattern is a typed envelope:

    *Incoming*  -> what a client is allowed to send over the socket. Validate
                every received frame against this before acting on it, so a
                malformed payload is rejected instead of crashing the handler.
    *Outgoing*  -> what the server sends back. Keeping a single response shape
                (``type`` + ``data``) makes the client easy to write and lets
                you add message kinds later without breaking existing clients.

These mirror the Base/Create/Response split used for REST in
``models_example.py`` - the same discipline, adapted to a message stream.
"""

#Native imports
from typing import Optional

#Third-party imports
from pydantic import BaseModel, Field


class EchoMessageIn(BaseModel):
    """
    Payload a client may send to the echo endpoint.

    Replace these fields with your own. ``Field(...)`` lets you add
    validation/metadata (constraints, description, examples). Validating every
    inbound frame against a model is the WebSocket equivalent of validating a
    REST request body.
    """

    name: str = Field(..., min_length=1, description="Human-readable name.")
    message: str = Field(..., min_length=1, description="Free-text message to echo.")
    contact_email: Optional[str] = Field(
        default=None, description="Optional email; validated when present."
    )


class ChatMessageIn(BaseModel):
    """
    Payload a client may send to the broadcast endpoint.

    The ``username`` identifies the sender so other clients can render who said
    what; the server never trusts a client-supplied identity for anything
    security-sensitive (add authentication for that).
    """

    username: str = Field(..., min_length=1, description="Display name of the sender.")
    text: str = Field(..., min_length=1, description="Message body to broadcast.")


class WsMessageOut(BaseModel):
    """
    Standard server-to-client envelope returned by both example endpoints.

    Keeping one outgoing shape (a ``type`` discriminator plus a free-form
    ``data`` payload) means the client can branch on ``type`` and you can add
    new message kinds later without changing the contract for existing ones.
    """

    type: str = Field(..., description="Message kind, e.g. 'echo', 'chat', 'error'.")
    data: dict = Field(default_factory=dict, description="Message payload.")
