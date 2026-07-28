"""Tests for HTTP API routes."""

from datetime import datetime, timedelta

import pytest
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/api/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    assert body["data_mode"] == "mock"
    assert "providers" in body


def test_config_features():
    response = client.get("/api/config/features")
    assert response.status_code == 200
    body = response.json()
    assert body["data_mode"] == "mock"
    assert "supabase" in body["features"]


def test_overview_mock():
    to_date = datetime.utcnow().date()
    from_date = to_date - timedelta(days=30)
    response = client.get(
        f"/api/overview?from_date={from_date}&to_date={to_date}"
    )
    assert response.status_code == 200
    body = response.json()
    assert "total_users" in body
    assert response.headers.get("X-Data-Mode") == "mock"


@pytest.mark.parametrize(
    "path",
    [
        "/api/users",
        "/api/sessions",
        "/api/activity",
        "/api/ai",
        "/api/costs",
    ],
)
def test_dated_endpoints(path):
    to_date = datetime.utcnow().date()
    from_date = to_date - timedelta(days=7)
    response = client.get(f"{path}?from_date={from_date}&to_date={to_date}")
    assert response.status_code == 200


def test_infrastructure_mock():
    response = client.get("/api/infrastructure")
    assert response.status_code == 200
    body = response.json()
    assert "host_health" in body
    assert "database" in body


def test_wake_host_disabled_by_default():
    response = client.post("/api/infrastructure/wake-host")
    assert response.status_code == 200
    assert response.json()["status"] == "disabled"
