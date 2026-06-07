"""
#############################################################################
### Example mutation resolver
###
### @file example_mutation.py
### @author Sebastian Russo
### @date 2026
#############################################################################

Reference mutation resolver for this template. Copy this file (and its matching
``config_file.json`` entry) when adding new mutation fields.

ONLY ONE MUTATION FIELD SHOULD BE IN THIS FILE. Add further mutations in their
own files within this folder to keep resolver groups organized.

Demonstrates:
    - ``config_loader`` for the GraphQL field name
    - Strawberry input types from ``src/types/``
    - ``validators`` for optional input checks
    - ``log_handler`` for structured logging
"""

#Native imports
import uuid

#Third-party imports
import strawberry

#Other files imports
from src.utils.custom_logger import log_handler
from src.core_specs.configuration.config_loader import config_loader
from src.utils.validators import validate_email_format
from src.types.example_item import ExampleItem, ExampleItemInput
from src.resolvers.example_items_store import get_items_store

_cfg = config_loader["endpoints"]["example_endpoint_2"]

@strawberry.type
class CreateExampleItemMutation:
    """Mixin providing the create example item mutation."""

    @strawberry.field(name=_cfg["field_name"])
    def create_example_item(self, input: ExampleItemInput) -> ExampleItem:
        """
        Create a new example item.

        Parameters:
            input (ExampleItemInput): Validated Strawberry input type.

        Returns:
            ExampleItem: The newly created item.
        """
        if input.contact_email is not None:
            validate_email_format(input.contact_email)

        item_id = str(uuid.uuid4())
        item = ExampleItem(
            id=item_id,
            name=input.name,
            description=input.description,
        )
        get_items_store()[item_id] = item

        log_handler.info("Created example item %s via GraphQL", item_id)
        return item
