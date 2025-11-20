"""
#############################################################################
### Request limiter file
###
### @file request_limiter.py
### @Sebastian Russo
### @date: 2025
#############################################################################

This module contains a method to handle when a user exceeds the x number of 
allowed requests per x minutes/seconds for GraphQL endpoints
"""

from fastapi import Request
from fastapi.responses import JSONResponse
from slowapi.errors import RateLimitExceeded

from src.utils.custom_logger import log_handler

async def rate_limit_handler(request: Request, exc: RateLimitExceeded):
    """
    Handles GraphQL requests that exceed the allowed rate limit.

    This function is triggered when a client sends too many GraphQL requests within a given 
    time frame, as defined by the rate limiting middleware.

    Parameters:
    request (Request): The incoming HTTP request that triggered the exception.
    exc (RateLimitExceeded): The exception instance containing rate limit details.

    Returns:
    JSONResponse: A 429 Too Many Requests response with a GraphQL-compatible error format.
    """
    log_handler.warning(f"GraphQL rate limit exceeded for IP: {request.client.host}")
    return JSONResponse(
        status_code=429,
        content={
            "errors": [{
                "message": "Request rate limit exceeded. Please try again later.",
                "extensions": {
                    "code": "RATE_LIMITED"
                }
            }]
        },
    )