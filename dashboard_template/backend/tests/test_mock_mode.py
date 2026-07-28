"""Tests for mock mode functionality."""

import pytest
from datetime import datetime

from app.services.data_source import MockDataSource


@pytest.fixture
def mock_data_source():
    """Create a MockDataSource instance."""
    return MockDataSource()


def test_overview_mock_data(mock_data_source):
    """Test that overview returns mock data."""
    from_date = datetime(2024, 1, 1)
    to_date = datetime(2024, 1, 31)
    
    result = mock_data_source.get_overview(from_date, to_date)
    
    assert "total_users" in result
    assert "active_users" in result
    assert "growth_rate" in result
    assert "revenue" in result
    assert "metrics" in result
    assert "charts" in result


def test_users_mock_data(mock_data_source):
    """Test that users returns mock data."""
    from_date = datetime(2024, 1, 1)
    to_date = datetime(2024, 1, 31)
    
    result = mock_data_source.get_users(from_date, to_date)
    
    assert "total_users" in result
    assert "new_users" in result
    assert "active_users" in result
    assert "retention_rate" in result
    assert "metrics" in result
    assert "charts" in result
    assert "table" in result


def test_sessions_mock_data(mock_data_source):
    """Test that sessions returns mock data."""
    from_date = datetime(2024, 1, 1)
    to_date = datetime(2024, 1, 31)
    
    result = mock_data_source.get_sessions(from_date, to_date)
    
    assert "total_sessions" in result
    assert "avg_duration" in result
    assert "metrics" in result
    assert "charts" in result
    assert "table" in result


def test_activity_mock_data(mock_data_source):
    """Test that activity returns mock data."""
    from_date = datetime(2024, 1, 1)
    to_date = datetime(2024, 1, 31)
    
    result = mock_data_source.get_activity(from_date, to_date)
    
    assert "total_events" in result
    assert "events_by_type" in result
    assert "timeline" in result
    assert "table" in result


def test_infrastructure_mock_data(mock_data_source):
    """Test that infrastructure returns mock data."""
    result = mock_data_source.get_infrastructure()
    
    assert "host_health" in result
    assert "deployments" in result
    assert "storage" in result
    assert "database" in result
    assert "notes" in result


def test_costs_mock_data(mock_data_source):
    """Test that costs returns mock data."""
    from_date = datetime(2024, 1, 1)
    to_date = datetime(2024, 1, 31)
    
    result = mock_data_source.get_costs(from_date, to_date)
    
    assert "total_cost" in result
    assert "cost_by_category" in result
    assert "unit_economics" in result
    assert "projections" in result
    assert "notes" in result


def test_ai_metrics_mock_data(mock_data_source):
    """Test that AI metrics returns mock data."""
    from_date = datetime(2024, 1, 1)
    to_date = datetime(2024, 1, 31)
    
    result = mock_data_source.get_ai_metrics(from_date, to_date)
    
    assert "total_generations" in result
    assert "success_rate" in result
    assert "avg_latency" in result
    assert "token_usage" in result
    assert "charts" in result
    assert "notes" in result
