"""Test main application module."""
import pytest
from fastapi.testclient import TestClient

from src.main import app


@pytest.fixture
def client() -> TestClient:
    """Create test client."""
    return TestClient(app)


def test_root_endpoint(client: TestClient) -> None:
    """Test root endpoint returns expected response."""
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "General Agent is running"}


def test_health_endpoint(client: TestClient) -> None:
    """Test health check endpoint returns healthy status."""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}
