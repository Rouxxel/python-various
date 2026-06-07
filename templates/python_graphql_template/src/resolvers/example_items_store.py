"""
In-memory store shared by the example query and mutation resolvers.
Replace with a database layer in production.
"""

#Native imports
from typing import Dict

#Other files imports
from src.types.example_item import ExampleItem

_items_store: Dict[str, ExampleItem] = {}


def get_items_store() -> Dict[str, ExampleItem]:
    return _items_store
