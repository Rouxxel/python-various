"""
#############################################################################
### User GraphQL Type
###
### @file user.py
### @author Sebastian Russo
### @date 2025
#############################################################################

This module defines the User GraphQL type and related input types.
"""

import strawberry
from typing import Optional, List
from datetime import datetime

@strawberry.type
class User:
    """GraphQL User type representing a user in the system."""
    
    id: int
    name: str
    email: str
    age: int
    active: bool
    
    @strawberry.field
    def posts(self) -> List["Post"]:
        """Get all posts by this user."""
        from src.core_specs.data.data_loader import data_loader
        from src.types.post import Post
        
        user_posts = [
            post for post in data_loader["sample_data"]["posts"] 
            if post["author_id"] == self.id
        ]
        
        return [
            Post(
                id=post["id"],
                title=post["title"],
                content=post["content"],
                author_id=post["author_id"],
                published=post["published"],
                created_at=datetime.fromisoformat(post["created_at"].replace('Z', '+00:00'))
            )
            for post in user_posts
        ]

@strawberry.input
class UserInput:
    """Input type for creating a new user."""
    
    name: str
    email: str
    age: int
    active: Optional[bool] = True

@strawberry.input
class UserUpdateInput:
    """Input type for updating an existing user."""
    
    name: Optional[str] = None
    email: Optional[str] = None
    age: Optional[int] = None
    active: Optional[bool] = None