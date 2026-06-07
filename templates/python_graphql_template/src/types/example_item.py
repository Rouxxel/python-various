"""
#############################################################################
### Example Item GraphQL Type
###
### @file example_item.py
### @author Sebastian Russo
### @date 2026
#############################################################################

Strawberry types for the template example entity. Mirrors the Pydantic split in
``src/models/models_example.py`` — copy and rename when adding real entities.
"""

#Native imports
from typing import Optional

#Third-party imports
import strawberry

@strawberry.type
class ExampleItem:
    """Full example item returned by queries and mutations."""

    id: str
    name: str
    description: Optional[str] = None

@strawberry.input
class ExampleItemInput:
    """Payload accepted when creating an example item."""

    name: str
    description: Optional[str] = None
    contact_email: Optional[str] = None
