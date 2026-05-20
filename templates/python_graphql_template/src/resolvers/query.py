"""
#############################################################################
### GraphQL Query Resolvers
###
### @file query.py
### @author Sebastian Russo
### @date 2025
#############################################################################

This module contains all GraphQL query resolvers.
"""

import strawberry
from typing import List, Optional
from datetime import datetime

from src.types.user import User
from src.types.post import Post
from src.core_specs.data.data_loader import data_loader
from src.utils.custom_logger import log_handler

@strawberry.type
class Query:
    """Root Query type containing all available GraphQL queries."""
    
    @strawberry.field
    def hello(self, name: Optional[str] = None) -> str:
        """Simple hello query for testing."""
        log_handler.debug(f"Hello query called with name: {name}")
        if name:
            return f"Hello, {name}!"
        return "Hello, World!"
    
    @strawberry.field
    def api_info(self) -> str:
        """Get API information."""
        log_handler.debug("API info query called")
        api_info = data_loader["api_info"]
        return f"{api_info['name']} v{api_info['version']} - {api_info['description']}"
    
    @strawberry.field
    def users(self, active_only: Optional[bool] = None) -> List[User]:
        """Get all users, optionally filtered by active status."""
        log_handler.debug(f"Users query called with active_only: {active_only}")
        
        users_data = data_loader["sample_data"]["users"]
        
        if active_only is not None:
            users_data = [user for user in users_data if user["active"] == active_only]
        
        return [
            User(
                id=user["id"],
                name=user["name"],
                email=user["email"],
                age=user["age"],
                active=user["active"]
            )
            for user in users_data
        ]
    
    @strawberry.field
    def user(self, id: int) -> Optional[User]:
        """Get a specific user by ID."""
        log_handler.debug(f"User query called with id: {id}")
        
        users_data = data_loader["sample_data"]["users"]
        user_data = next((user for user in users_data if user["id"] == id), None)
        
        if user_data:
            return User(
                id=user_data["id"],
                name=user_data["name"],
                email=user_data["email"],
                age=user_data["age"],
                active=user_data["active"]
            )
        return None
    
    @strawberry.field
    def posts(self, published_only: Optional[bool] = None) -> List[Post]:
        """Get all posts, optionally filtered by published status."""
        log_handler.debug(f"Posts query called with published_only: {published_only}")
        
        posts_data = data_loader["sample_data"]["posts"]
        
        if published_only is not None:
            posts_data = [post for post in posts_data if post["published"] == published_only]
        
        return [
            Post(
                id=post["id"],
                title=post["title"],
                content=post["content"],
                author_id=post["author_id"],
                published=post["published"],
                created_at=datetime.fromisoformat(post["created_at"].replace('Z', '+00:00'))
            )
            for post in posts_data
        ]
    
    @strawberry.field
    def post(self, id: int) -> Optional[Post]:
        """Get a specific post by ID."""
        log_handler.debug(f"Post query called with id: {id}")
        
        posts_data = data_loader["sample_data"]["posts"]
        post_data = next((post for post in posts_data if post["id"] == id), None)
        
        if post_data:
            return Post(
                id=post_data["id"],
                title=post_data["title"],
                content=post_data["content"],
                author_id=post_data["author_id"],
                published=post_data["published"],
                created_at=datetime.fromisoformat(post_data["created_at"].replace('Z', '+00:00'))
            )
        return None