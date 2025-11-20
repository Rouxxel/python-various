"""
#############################################################################
### Validators file
###
### @file validators.py
### @author Sebastian Russo
### @date 2025
#############################################################################

This module contains validation utilities for GraphQL inputs and data.
"""

import re
from typing import Optional
from src.core_specs.configuration.config_loader import config_loader

def validate_email(email: str) -> bool:
    """
    Validates an email address format and allowed providers.
    
    Args:
        email (str): Email address to validate
        
    Returns:
        bool: True if email is valid, False otherwise
    """
    if not email or not isinstance(email, str):
        return False
    
    # Basic email format validation
    email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(email_pattern, email):
        return False
    
    # Check allowed providers and TLDs
    try:
        local_part, domain = email.split('@')
        domain_parts = domain.split('.')
        
        if len(domain_parts) < 2:
            return False
        
        provider = domain_parts[0].lower()
        tld = domain_parts[-1].lower()
        
        allowed_providers = config_loader["email_validation"]["allowed_providers"]
        allowed_tlds = config_loader["email_validation"]["allowed_tlds"]
        
        return provider in allowed_providers and tld in allowed_tlds
    except (ValueError, KeyError):
        return False

def validate_user_input(name: str, email: str, age: int) -> Optional[str]:
    """
    Validates user input data.
    
    Args:
        name (str): User name
        email (str): User email
        age (int): User age
        
    Returns:
        Optional[str]: Error message if validation fails, None if valid
    """
    if not name or len(name.strip()) < 2:
        return "Name must be at least 2 characters long"
    
    if len(name) > 100:
        return "Name must be less than 100 characters"
    
    if not validate_email(email):
        return "Invalid email address or provider not allowed"
    
    if not isinstance(age, int) or age < 0 or age > 150:
        return "Age must be a valid number between 0 and 150"
    
    return None

def validate_post_input(title: str, content: str) -> Optional[str]:
    """
    Validates post input data.
    
    Args:
        title (str): Post title
        content (str): Post content
        
    Returns:
        Optional[str]: Error message if validation fails, None if valid
    """
    if not title or len(title.strip()) < 3:
        return "Title must be at least 3 characters long"
    
    if len(title) > 200:
        return "Title must be less than 200 characters"
    
    if not content or len(content.strip()) < 10:
        return "Content must be at least 10 characters long"
    
    if len(content) > 10000:
        return "Content must be less than 10,000 characters"
    
    return None

def sanitize_string(input_str: str) -> str:
    """
    Sanitizes a string by removing potentially harmful characters.
    
    Args:
        input_str (str): String to sanitize
        
    Returns:
        str: Sanitized string
    """
    if not isinstance(input_str, str):
        return ""
    
    # Remove HTML tags and script content
    import html
    sanitized = html.escape(input_str)
    
    # Remove excessive whitespace
    sanitized = re.sub(r'\s+', ' ', sanitized).strip()
    
    return sanitized