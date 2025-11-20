"""
#############################################################################
### Main GraphQL API file
###
### @file main.py
### @author Sebastian Russo
### @date 2025
#############################################################################

This module initializes the FastAPI backend with GraphQL support for development.
It sets up the GraphQL endpoint, custom logger, rate limiter, and loads environment variables.
"""

# Native imports
import os
from contextlib import asynccontextmanager

# Third-party imports
import uvicorn
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from strawberry.fastapi import GraphQLRouter
from slowapi.errors import RateLimitExceeded
from dotenv import load_dotenv
load_dotenv()

# Other files imports
from src.utils.request_limiter import rate_limit_handler
from src.utils.custom_logger import log_handler
from src.utils.limiter import limiter
from src.graphql_schema.schema import schema

# Configuration imports
from src.core_specs.configuration.config_loader import config_loader
from src.core_specs.data.data_loader import data_loader

"""API APP-----------------------------------------------------------"""
# Lifespan event manager (startup and shutdown)
@asynccontextmanager
async def lifespan(app: FastAPI):
    port = config_loader["network"]["server_port"]
    log_handler.info(f"GraphQL API Template server starting on port {port}")
    log_handler.info(f"GraphQL endpoint available at: http://localhost:{port}{config_loader['graphql']['endpoint']}")
    if config_loader["graphql"]["graphiql"]:
        log_handler.info(f"GraphiQL interface available at: http://localhost:{port}{config_loader['graphql']['endpoint']}")
    yield
    log_handler.info("GraphQL API Template server shutting down")

# Create FastAPI app
app = FastAPI(
    lifespan=lifespan,
    title=os.getenv("API_TITLE", "GraphQL API Template"),
    version=os.getenv("API_VERSION", "1.0.0"),
    description=os.getenv("API_DESCRIPTION", "A template for building GraphQL APIs with FastAPI and Strawberry")
)

"""VARIOUS-----------------------------------------------------------"""
# Setup rate limiter
app.state.limiter = limiter

# Add global exception handler for rate limits
app.add_exception_handler(RateLimitExceeded, rate_limit_handler)

"""GraphQL Setup-----------------------------------------------------------"""
# Create GraphQL router with rate limiting
graphql_app = GraphQLRouter(
    schema,
    graphiql=config_loader["graphql"]["graphiql"],
    introspection=config_loader["graphql"]["introspection"]
)

# Add rate limiting to GraphQL endpoint
@app.middleware("http")
async def add_graphql_rate_limiting(request: Request, call_next):
    """Add rate limiting to GraphQL requests."""
    if request.url.path == config_loader["graphql"]["endpoint"]:
        # Apply rate limiting to GraphQL endpoint
        rate_limit = f"{config_loader['graphql']['request_limit']}/{config_loader['graphql']['unit_of_time_for_limit']}"
        try:
            await limiter.limit(rate_limit)(request)
        except RateLimitExceeded as e:
            return await rate_limit_handler(request, e)
    
    response = await call_next(request)
    return response

# Include GraphQL router
app.include_router(graphql_app, prefix=config_loader["graphql"]["endpoint"])

"""Health Check Endpoint-----------------------------------------------------------"""
@app.get(config_loader["endpoints"]["health_check"]["endpoint_route"])
@limiter.limit(
    f"{config_loader['endpoints']['health_check']['request_limit']}/"
    f"{config_loader['endpoints']['health_check']['unit_of_time_for_limit']}"
)
async def health_check(request: Request):
    """
    Health check endpoint to verify that the GraphQL API is operational.
    
    Returns:
        dict: A JSON response indicating that the API is running.
    """
    log_handler.debug("Health check endpoint called")
    return {
        "status": "healthy",
        "message": "GraphQL API Template is running",
        "graphql_endpoint": config_loader["graphql"]["endpoint"],
        "graphiql_available": config_loader["graphql"]["graphiql"]
    }

"""Start server-----------------------------------------------------------"""
if __name__ == "__main__":
    port = config_loader["network"]["server_port"]
    
    uvicorn.run(
        config_loader["network"]["uvicorn_app_reference"],
        host=config_loader["network"]["host"],
        port=config_loader["network"]["server_port"],
        reload=config_loader["network"]["reload"],
        workers=config_loader["network"]["workers"],
        proxy_headers=config_loader["network"]["proxy_headers"]
    )
    
    log_handler.info(f"Loaded configuration: \n {config_loader}")
    log_handler.info(f"Loaded data: \n {data_loader}")
    # GraphQL endpoint available at: http://127.0.0.1:8000/graphql
    # GraphiQL interface available at: http://127.0.0.1:8000/graphql