"""Generic hosting service for custom providers."""

from app.services.hosting.base import HostingService, generic_health_check, generic_wake


class GenericService(HostingService):
    """Generic hosting service for custom providers."""

    async def check_health(self, url: str) -> dict:
        """Check health of generic service.

        Args:
            url: Service URL

        Returns:
            dict with status, response_time, uptime
        """
        result = await generic_health_check(url)
        result["provider"] = "custom"
        result["notes"] = "Generic HTTP health check"
        return result

    async def wake(self, url: str) -> dict:
        """Wake up generic service.

        Args:
            url: Service URL

        Returns:
            dict with status and message
        """
        result = await generic_wake(url)
        result["provider"] = "custom"
        result["notes"] = "Generic wake request sent"
        return result
