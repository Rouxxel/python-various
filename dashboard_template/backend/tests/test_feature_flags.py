"""Tests for feature flag functionality."""

import pytest
from unittest.mock import patch

from app.config import Settings


def test_feature_flags_default_values():
    """Test that feature flags have safe default values."""
    settings = Settings()
    
    # External API features should default to off
    assert settings.feature_vercel is False
    assert settings.feature_host_health is False
    assert settings.feature_storage_metrics is False
    assert settings.feature_costs_module is False
    
    # Supabase can default to true for live mode
    assert settings.feature_supabase is True
    
    # Test/prod switch should be enabled by default
    assert settings.feature_test_prod_switch is True


def test_data_mode_default():
    """Test that data mode defaults to mock."""
    settings = Settings()
    assert settings.dashboard_data_mode == "mock"


def test_hosting_provider_default():
    """Test that hosting provider defaults to none."""
    settings = Settings()
    assert settings.hosting_provider == "none"


@patch.dict("os.environ", {"FEATURE_VERCEL": "true", "FEATURE_COSTS_MODULE": "true"})
def test_feature_flags_from_env():
    """Test that feature flags can be set from environment."""
    settings = Settings()
    
    assert settings.feature_vercel is True
    assert settings.feature_costs_module is True


@patch.dict("os.environ", {"DASHBOARD_DATA_MODE": "live"})
def test_data_mode_from_env():
    """Test that data mode can be set from environment."""
    settings = Settings()
    assert settings.dashboard_data_mode == "live"


@patch.dict("os.environ", {"HOSTING_PROVIDER": "render"})
def test_hosting_provider_from_env():
    """Test that hosting provider can be set from environment."""
    settings = Settings()
    assert settings.hosting_provider == "render"


def test_generic_api_urls():
    """Test that generic API URLs are available."""
    settings = Settings()
    
    assert hasattr(settings, "main_api_url_test")
    assert hasattr(settings, "main_api_url_prod")
