"""Data source abstraction for mock and live data modes."""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import Literal

from app.config import settings


class DataSource(ABC):
    """Abstract data source interface."""

    @abstractmethod
    def get_overview(self, from_date: datetime, to_date: datetime) -> dict:
        """Get overview metrics."""
        pass

    @abstractmethod
    def get_users(self, from_date: datetime, to_date: datetime) -> dict:
        """Get user analytics."""
        pass

    @abstractmethod
    def get_sessions(self, from_date: datetime, to_date: datetime) -> dict:
        """Get session analytics."""
        pass

    @abstractmethod
    def get_activity(self, from_date: datetime, to_date: datetime) -> dict:
        """Get activity/events."""
        pass

    @abstractmethod
    def get_infrastructure(self) -> dict:
        """Get infrastructure metrics."""
        pass

    @abstractmethod
    def get_costs(self, from_date: datetime, to_date: datetime) -> dict:
        """Get cost analytics."""
        pass

    @abstractmethod
    def get_ai_metrics(self, from_date: datetime, to_date: datetime) -> dict:
        """Get AI/ML metrics."""
        pass


class MockDataSource(DataSource):
    """Mock data source for development without external services."""

    def __init__(self):
        self._mock_data_dir = None

    def _load_mock_json(self, filename: str) -> dict:
        """Load mock data from JSON file."""
        import json
        from pathlib import Path

        if self._mock_data_dir is None:
            self._mock_data_dir = Path(__file__).parent.parent / "mock_data"

        path = self._mock_data_dir / filename
        if not path.exists():
            return {"error": f"Mock file not found: {filename}"}

        with open(path) as f:
            return json.load(f)

    def get_overview(self, from_date: datetime, to_date: datetime) -> dict:
        return self._load_mock_json("overview.json")

    def get_users(self, from_date: datetime, to_date: datetime) -> dict:
        return self._load_mock_json("users.json")

    def get_sessions(self, from_date: datetime, to_date: datetime) -> dict:
        return self._load_mock_json("sessions.json")

    def get_activity(self, from_date: datetime, to_date: datetime) -> dict:
        return self._load_mock_json("activity.json")

    def get_infrastructure(self) -> dict:
        return self._load_mock_json("infrastructure.json")

    def get_costs(self, from_date: datetime, to_date: datetime) -> dict:
        return self._load_mock_json("costs.json")

    def get_ai_metrics(self, from_date: datetime, to_date: datetime) -> dict:
        return self._load_mock_json("ai_metrics.json")


class LiveDataSource(DataSource):
    """Live data source that queries actual providers."""

    def __init__(self):
        # Import live data builders here to avoid circular imports
        from app.services.live import placeholder_analytics

        self._analytics = placeholder_analytics

    def get_overview(self, from_date: datetime, to_date: datetime) -> dict:
        return self._analytics.build_overview(from_date, to_date)

    def get_users(self, from_date: datetime, to_date: datetime) -> dict:
        return self._analytics.build_users(from_date, to_date)

    def get_sessions(self, from_date: datetime, to_date: datetime) -> dict:
        return self._analytics.build_sessions(from_date, to_date)

    def get_activity(self, from_date: datetime, to_date: datetime) -> dict:
        return self._analytics.build_activity(from_date, to_date)

    def get_infrastructure(self) -> dict:
        return self._analytics.build_infrastructure()

    def get_costs(self, from_date: datetime, to_date: datetime) -> dict:
        return self._analytics.build_costs(from_date, to_date)

    def get_ai_metrics(self, from_date: datetime, to_date: datetime) -> dict:
        return self._analytics.build_ai_metrics(from_date, to_date)


def get_data_source() -> DataSource:
    """Factory function to get the appropriate data source based on settings."""
    if settings.dashboard_data_mode == "mock":
        return MockDataSource()
    else:
        return LiveDataSource()
