"""Railway-specific hosting service."""

from app.services.hosting.base import HostingService, generic_health_check, generic_wake


class RailwayService(HostingService):
    """Railway hosting service."""

    async def check_health(self, url: str) -> dict:
        """Check health of Railway service.

        Args:
            url: Railway service URL

        Returns:
            dict with status, response_time, uptime
        """
        result = await generic_health_check(url)
        result["provider"] = "railway"
        result["notes"] = "Railway health check via HTTP GET"
        return result

    async def wake(self, url: str) -> dict:
        """Wake up Railway service.

        Args:
            url: Railway service URL

        Returns:
            dict with status and message
        """
        result = await generic_wake(url)
        result["provider"] = "railway"
        result["notes"] = "Railway wake request sent"
        return result
