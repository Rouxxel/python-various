"""
#############################################################################
### Example room service module
###
### @file example_room_service.py
### @date 2026
#############################################################################

Demo service for the broadcast WebSocket: optional Redis cache for the last
room message. Handlers call this module; cache operations stay in redis_service.
"""

#Native imports
from typing import Optional

#Other files imports
from src.resources.cache.redis_service import cache_get, cache_set

_ROOM_CACHE_KEY = "ws:room:default:last_message"
_ROOM_CACHE_TTL_SECONDS = 3600


def cache_last_room_message(message: dict) -> None:
    """Store the most recent chat message for late-joining clients."""
    cache_set(_ROOM_CACHE_KEY, message, expiration_seconds=_ROOM_CACHE_TTL_SECONDS)


def get_cached_last_room_message() -> Optional[dict]:
    """Return the cached last message, or None if unavailable."""
    cached = cache_get(_ROOM_CACHE_KEY)
    return cached if isinstance(cached, dict) else None
