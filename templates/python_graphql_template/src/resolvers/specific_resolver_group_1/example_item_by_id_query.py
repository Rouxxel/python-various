"""
#############################################################################
### Example item by ID query resolver
###
### @file example_item_by_id_query.py
### @author Sebastian Russo
### @date 2026
#############################################################################

Reference query resolver demonstrating optional Redis caching via the service
layer. Resolvers must not import ``redis_client`` directly.
"""

#Native imports
from typing import Optional

#Third-party imports
import strawberry

#Other files imports
from src.utils.custom_logger import log_handler
from src.core_specs.configuration.config_loader import config_loader
from src.types.example_item import ExampleItem
from src.resources.example_item_service import get_example_item_by_id

_cfg = config_loader["endpoints"]["example_endpoint_3"]


@strawberry.type
class ExampleItemByIdQuery:
    """Mixin providing the example item by ID query (optional Redis cache)."""

    @strawberry.field(name=_cfg["field_name"])
    def example_item(self, id: str) -> Optional[ExampleItem]:
        """
        Get a single example item by ID.

        Parameters:
            id (str): Unique item identifier.

        Returns:
            ExampleItem | None: The item if found.
        """
        log_handler.debug("example_item query for id=%s", id)
        return get_example_item_by_id(id)
