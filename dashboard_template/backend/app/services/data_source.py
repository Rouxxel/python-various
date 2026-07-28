"""Data source abstraction for mock and live data modes."""

from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path

from app.config import settings
from app.core_specs.configuration.config_loader import config_loader
from app.utils.custom_logger import log_handler
from app.utils.secure_file_io import read_json, set_allowed_root

_BACKEND_DIR = Path(__file__).resolve().parents[2]
_MOCK_DATA_DIR = _BACKEND_DIR / config_loader["defaults"]["mock_data_path"]
_MOCK_FILES = config_loader["mock_data"]

set_allowed_root(_BACKEND_DIR)


class DataSource(ABC):
    """Abstract data source interface."""

    @abstractmethod
    def get_overview(self, from_date: datetime, to_date: datetime) -> dict:
        pass

    @abstractmethod
    def get_users(self, from_date: datetime, to_date: datetime) -> dict:
        pass

    @abstractmethod
    def get_sessions(self, from_date: datetime, to_date: datetime) -> dict:
        pass

    @abstractmethod
    def get_activity(self, from_date: datetime, to_date: datetime) -> dict:
        pass

    @abstractmethod
    def get_infrastructure(self) -> dict:
        pass

    @abstractmethod
    def get_costs(self, from_date: datetime, to_date: datetime) -> dict:
        pass

    @abstractmethod
    def get_ai_metrics(self, from_date: datetime, to_date: datetime) -> dict:
        pass


class MockDataSource(DataSource):
    """Mock data source for development without external services."""

    def _load_mock_json(self, key: str) -> dict:
        filename = _MOCK_FILES[key]
        path = _MOCK_DATA_DIR / filename
        try:
            data = read_json(path, default={"error": f"Mock file not found: {filename}"})
            return data if isinstance(data, dict) else {"data": data}
        except FileNotFoundError:
            log_handler.warning("Mock file missing: %s", path)
            return {"error": f"Mock file not found: {filename}"}
        except Exception as exc:
            log_handler.error("Failed to load mock file %s: %s", path, exc)
            return {"error": str(exc)}

    def get_overview(self, from_date: datetime, to_date: datetime) -> dict:
        return self._load_mock_json("overview")

    def get_users(self, from_date: datetime, to_date: datetime) -> dict:
        return self._load_mock_json("users")

    def get_sessions(self, from_date: datetime, to_date: datetime) -> dict:
        return self._load_mock_json("sessions")

    def get_activity(self, from_date: datetime, to_date: datetime) -> dict:
        return self._load_mock_json("activity")

    def get_infrastructure(self) -> dict:
        return self._load_mock_json("infrastructure")

    def get_costs(self, from_date: datetime, to_date: datetime) -> dict:
        return self._load_mock_json("costs")

    def get_ai_metrics(self, from_date: datetime, to_date: datetime) -> dict:
        return self._load_mock_json("ai_metrics")


class LiveDataSource(DataSource):
    """Live data source that queries actual providers."""

    def __init__(self):
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
    """Return mock or live data source based on ``DASHBOARD_DATA_MODE``."""
    if settings.dashboard_data_mode == "mock":
        return MockDataSource()
    return LiveDataSource()
