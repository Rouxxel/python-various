"""
#############################################################################
### GraphQL Schema Definition
###
### @file schema.py
### @author Sebastian Russo
### @date 2025
#############################################################################

This module defines the main GraphQL schema combining queries and mutations.
"""

import strawberry
from strawberry.extensions import DisableIntrospection

from src.resolvers.query import Query
from src.resolvers.mutation import Mutation
from src.core_specs.configuration.config_loader import config_loader

_extensions = []
if not config_loader["graphql"]["introspection"]:
    _extensions.append(DisableIntrospection())

# Create the main GraphQL schema
schema = strawberry.Schema(
    query=Query,
    mutation=Mutation,
    extensions=_extensions,
)