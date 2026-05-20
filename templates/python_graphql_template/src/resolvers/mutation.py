"""
#############################################################################
### GraphQL Mutation Resolvers
###
### @file mutation.py
### @author Sebastian Russo
### @date 2025
#############################################################################

This module contains all GraphQL mutation resolvers.
"""

import strawberry
from typing import Optional
from datetime import datetime

from src.types.user import User, UserInput, UserUpdateInput
from src.types.post import Post, PostInput, PostUpdateInput
from src.core_specs.data.data_loader import data_loader
from src.utils.custom_logger import log_handler

@strawberry.type
class Mutation:
    """Root Mutation type containing all available GraphQL mutations."""
    
    @strawberry.field
    def create_user(self, input: UserInput) -> User:
        """Create a new user."""
        log_handler.info(f"Creating new user: {input.name}")
        
        # In a real application, you would save to a database
        # For this template, we'll simulate by creating a new user object
        users_data = data_loader["sample_data"]["users"]
        new_id = max(user["id"] for user in users_data) + 1 if users_data else 1
        
        new_user = User(
            id=new_id,
            name=input.name,
            email=input.email,
            age=input.age,
            active=input.active
        )
        
        log_handler.info(f"User created with ID: {new_id}")
        return new_user
    
    @strawberry.field
    def update_user(self, id: int, input: UserUpdateInput) -> Optional[User]:
        """Update an existing user."""
        log_handler.info(f"Updating user with ID: {id}")
        
        # In a real application, you would update in a database
        # For this template, we'll simulate the update
        users_data = data_loader["sample_data"]["users"]
        user_data = next((user for user in users_data if user["id"] == id), None)
        
        if not user_data:
            log_handler.warning(f"User with ID {id} not found")
            return None
        
        # Update fields if provided
        if input.name is not None:
            user_data["name"] = input.name
        if input.email is not None:
            user_data["email"] = input.email
        if input.age is not None:
            user_data["age"] = input.age
        if input.active is not None:
            user_data["active"] = input.active
        
        updated_user = User(
            id=user_data["id"],
            name=user_data["name"],
            email=user_data["email"],
            age=user_data["age"],
            active=user_data["active"]
        )
        
        log_handler.info(f"User {id} updated successfully")
        return updated_user
    
    @strawberry.field
    def delete_user(self, id: int) -> bool:
        """Delete a user."""
        log_handler.info(f"Deleting user with ID: {id}")
        
        # In a real application, you would delete from a database
        # For this template, we'll simulate the deletion
        users_data = data_loader["sample_data"]["users"]
        user_exists = any(user["id"] == id for user in users_data)
        
        if user_exists:
            log_handler.info(f"User {id} deleted successfully")
            return True
        else:
            log_handler.warning(f"User with ID {id} not found")
            return False
    
    @strawberry.field
    def create_post(self, input: PostInput) -> Post:
        """Create a new post."""
        log_handler.info(f"Creating new post: {input.title}")
        
        # In a real application, you would save to a database
        posts_data = data_loader["sample_data"]["posts"]
        new_id = max(post["id"] for post in posts_data) + 1 if posts_data else 1
        
        new_post = Post(
            id=new_id,
            title=input.title,
            content=input.content,
            author_id=input.author_id,
            published=input.published,
            created_at=datetime.now()
        )
        
        log_handler.info(f"Post created with ID: {new_id}")
        return new_post
    
    @strawberry.field
    def update_post(self, id: int, input: PostUpdateInput) -> Optional[Post]:
        """Update an existing post."""
        log_handler.info(f"Updating post with ID: {id}")
        
        # In a real application, you would update in a database
        posts_data = data_loader["sample_data"]["posts"]
        post_data = next((post for post in posts_data if post["id"] == id), None)
        
        if not post_data:
            log_handler.warning(f"Post with ID {id} not found")
            return None
        
        # Update fields if provided
        if input.title is not None:
            post_data["title"] = input.title
        if input.content is not None:
            post_data["content"] = input.content
        if input.published is not None:
            post_data["published"] = input.published
        
        updated_post = Post(
            id=post_data["id"],
            title=post_data["title"],
            content=post_data["content"],
            author_id=post_data["author_id"],
            published=post_data["published"],
            created_at=datetime.fromisoformat(post_data["created_at"].replace('Z', '+00:00'))
        )
        
        log_handler.info(f"Post {id} updated successfully")
        return updated_post
    
    @strawberry.field
    def delete_post(self, id: int) -> bool:
        """Delete a post."""
        log_handler.info(f"Deleting post with ID: {id}")
        
        # In a real application, you would delete from a database
        posts_data = data_loader["sample_data"]["posts"]
        post_exists = any(post["id"] == id for post in posts_data)
        
        if post_exists:
            log_handler.info(f"Post {id} deleted successfully")
            return True
        else:
            log_handler.warning(f"Post with ID {id} not found")
            return False