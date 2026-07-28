"""Render-specific hosting service."""

from app.services.hosting.base import HostingService, generic_health_check, generic_wake


class RenderService(HostingService):
    """Render hosting service with free tier spin-down handling."""

    async def check_health(self, url: str) -> dict:
        """Check health of Render service.

        Render free tier spins down after 15 minutes of inactivity.
        First request after spin-down may take 30-60 seconds.

        Args:
            url: Render service URL

        Returns:
            dict with status, response_time, uptime
        """
        result = await generic_health_check(url)
        result["provider"] = "render"
        result["notes"] = "Free tier spins down after 15 minutes of inactivity"
        return result

    async def wake(self, url: str) -> dict:
        """Wake up Render service.

        Args:
            url: Render service URL

        Returns:
            dict with status and message
        """
        result = await generic_wake(url)
        result["provider"] = "render"
        result["notes"] = "May take 30-60 seconds for service to wake up"
        return result
