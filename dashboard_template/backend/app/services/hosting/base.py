"""Base hosting service interface."""

from abc import ABC, abstractmethod
from typing import Literal


class HostingService(ABC):
    """Abstract base class for hosting provider health checks."""

    @abstractmethod
    async def check_health(self, url: str) -> dict:
        """Check health of hosting service.

        Args:
            url: Service URL to check

        Returns:
            dict with status, response_time, uptime
        """
        pass

    @abstractmethod
    async def wake(self, url: str) -> dict:
        """Wake up sleeping service (for free tier spin-down).

        Args:
            url: Service URL to wake

        Returns:
            dict with status and message
        """
        pass


async def generic_health_check(url: str) -> dict:
    """Generic HTTP health check.

    Args:
        url: Service URL to check

    Returns:
        dict with status, response_time, uptime
    """
    import httpx

    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url)
            response_time = response.elapsed.total_seconds() * 1000

            return {
                "status": "healthy" if response.status_code == 200 else "unhealthy",
                "response_time": response_time,
                "uptime": 99.9,  # Placeholder - would need historical data
                "status_code": response.status_code,
            }
    except Exception as e:
        return {
            "status": "unhealthy",
            "response_time": 0,
            "uptime": 0,
            "error": str(e),
        }


async def generic_wake(url: str) -> dict:
    """Generic wake request (simple HTTP GET).

    Args:
        url: Service URL to wake

    Returns:
        dict with status and message
    """
    import httpx

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(url)
            return {
                "status": "success" if response.status_code == 200 else "failed",
                "message": "Wake request sent",
                "status_code": response.status_code,
            }
    except Exception as e:
        return {
            "status": "failed",
            "message": str(e),
        }
