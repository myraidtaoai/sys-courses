"""Tests for API endpoints."""

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    """Create test client."""
    from src.backend.main import app
    return TestClient(app)


def test_root_endpoint(client):
    """Test root endpoint returns welcome message."""
    response = client.get("/")
    assert response.status_code == 200
    assert "Poetry AI Assistant" in response.json()["message"]


def test_health_endpoint(client):
    """Test health endpoint returns status."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_chat_endpoint_requires_query(client):
    """Test chat endpoint validates input."""
    response = client.post("/chat", json={})
    assert response.status_code == 422  # Validation error


def test_classify_endpoint_requires_text(client):
    """Test classify endpoint validates input."""
    response = client.post("/classify", json={})
    assert response.status_code == 422  # Validation error
