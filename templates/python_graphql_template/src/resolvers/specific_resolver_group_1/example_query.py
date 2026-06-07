"""
#############################################################################
### Example query resolver
###
### @file example_query.py
### @author Sebastian Russo
### @date 2026
#############################################################################

Reference query resolver for this template. Copy this file (and its matching
``config_file.json`` entry) when adding new query fields.

ONLY ONE QUERY FIELD SHOULD BE IN THIS FILE. Add further queries in their own
files within this folder to keep resolver groups organized.

Demonstrates:
    - ``config_loader`` for the GraphQL field name
    - Strawberry types from ``src/types/``
    - ``data_loader`` for static reference data
    - ``log_handler`` for structured logging
"""

#Native imports
from typing import List

#Third-party imports
import strawberry

#Other files imports
from src.utils.custom_logger import log_handler
from src.core_specs.configuration.config_loader import config_loader
from src.core_specs.data.data_loader import data_loader
from src.types.example_item import ExampleItem
from src.resolvers.example_items_store import get_items_store

_cfg = config_loader["endpoints"]["example_endpoint_1"]

@strawberry.type
class ExampleItemsQuery:
    """Mixin providing the example items list query."""

    @strawberry.field(name=_cfg["field_name"])
    def example_items(self) -> List[ExampleItem]:
        """
        List all example items.

        Returns:
            list[ExampleItem]: All stored example items.
        """
        log_handler.debug(
            "example_items query (supported languages: %s)",
            data_loader.get("languages", []),
        )
        return list(get_items_store().values())
