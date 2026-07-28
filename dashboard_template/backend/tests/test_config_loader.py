"""Tests for JSON configuration loader."""

from app.core_specs.configuration.config_loader import config_loader


def test_config_loader_has_required_sections():
    assert "logging" in config_loader
    assert "network" in config_loader
    assert "app" in config_loader
    assert "endpoints" in config_loader
    assert "mock_data" in config_loader


def test_config_loader_api_prefix():
    assert config_loader["app"]["api_prefix"] == "/api"


def test_config_loader_overview_endpoint():
    overview = config_loader["endpoints"]["overview"]
    assert overview["router_prefix"] == "/overview"
