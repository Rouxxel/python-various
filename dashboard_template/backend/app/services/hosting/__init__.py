"""Hosting services package."""

from app.config import settings
from app.services.hosting.base import HostingService
from app.services.hosting.generic import GenericService
from app.services.hosting.railway import RailwayService
from app.services.hosting.render import RenderService


def get_hosting_service() -> HostingService:
    """Factory function to get the appropriate hosting service.

    Returns:
        HostingService instance based on HOSTING_PROVIDER setting
    """
    provider = settings.hosting_provider

    if provider == "render":
        return RenderService()
    elif provider == "railway":
        return RailwayService()
    elif provider == "fly":
        # Fly.io not fully implemented - use generic
        return GenericService()
    elif provider == "custom":
        return GenericService()
    else:
        return GenericService()
