"""
#############################################################################
### Post GraphQL Type
###
### @file post.py
### @author Sebastian Russo
### @date 2025
#############################################################################

This module defines the Post GraphQL type and related input types.
"""

import strawberry
from typing import Optional
from datetime import datetime

@strawberry.type
class Post:
    """GraphQL Post type representing a blog post or article."""
    
    id: int
    title: str
    content: str
    author_id: int
    published: bool
    created_at: datetime
    
    @strawberry.field
    def author(self) -> Optional["User"]:
        """Get the author of this post."""
        from src.core_specs.data.data_loader import data_loader
        from src.types.user import User
        
        users = data_loader["sample_data"]["users"]
        author_data = next((user for user in users if user["id"] == self.author_id), None)
        
        if author_data:
            return User(
                id=author_data["id"],
                name=author_data["name"],
                email=author_data["email"],
                age=author_data["age"],
                active=author_data["active"]
            )
        return None

@strawberry.input
class PostInput:
    """Input type for creating a new post."""
    
    title: str
    content: str
    author_id: int
    published: Optional[bool] = False

@strawberry.input
class PostUpdateInput:
    """Input type for updating an existing post."""
    
    title: Optional[str] = None
    content: Optional[str] = None
    published: Optional[bool] = None