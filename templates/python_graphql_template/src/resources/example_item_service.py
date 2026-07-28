"""
#############################################################################
### Example item service module
###
### @file example_item_service.py
### @date 2026
#############################################################################

Demo service showing optional Redis caching. GraphQL resolvers call this module;
cache operations stay in ``redis_service``, not in resolver methods directly.
"""

#Native imports
from typing import Optional

#Other files imports
from src.types.example_item import ExampleItem
from src.resolvers.example_items_store import get_items_store
from src.resources.cache.redis_service import cache_get, cache_set
from src.utils.custom_logger import log_handler

_CACHE_TTL_SECONDS = 600
_CACHE_KEY_PREFIX = "example_item:"


def _item_to_cache_dict(item: ExampleItem) -> dict:
    return {
        "id": item.id,
        "name": item.name,
        "description": item.description,
    }


def get_example_item_by_id(item_id: str) -> Optional[ExampleItem]:
    """
    Fetch an example item, using Redis as an optional cache layer.

    Returns:
        ExampleItem if found, otherwise None.
    """
    cache_key = f"{_CACHE_KEY_PREFIX}{item_id}"

    cached = cache_get(cache_key)
    if cached is not None:
        log_handler.debug("Cache hit for example item %s", item_id)
        return ExampleItem(**cached)

    item = get_items_store().get(item_id)
    if item is None:
        return None

    cache_set(cache_key, _item_to_cache_dict(item), expiration_seconds=_CACHE_TTL_SECONDS)
    log_handler.debug("Cache miss for example item %s", item_id)
    return item
