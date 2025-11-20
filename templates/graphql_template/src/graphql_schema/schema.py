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
from src.resolvers.query import Query
from src.resolvers.mutation import Mutation

# Create the main GraphQL schema
schema = strawberry.Schema(
    query=Query,
    mutation=Mutation,
    # Enable introspection for development (disable in production if needed)
    # introspection=True,
    # Add extensions for better development experience
    extensions=[
        # Add query complexity analysis
        # strawberry.extensions.QueryDepthLimiter(max_depth=10),
    ]
)