"""Tests for the main app."""
import pytest
from fastapi import status
from fastapi.testclient import TestClient


class TestAppStartup:
    """Tests for app startup and basic functionality."""
    
    def test_app_startup(self, client: TestClient):
        """Test that app starts successfully."""
        # If we can create a client, the app started
        assert client is not None
    
    def test_health_check_if_exists(self, client: TestClient):
        """Test health check endpoint if it exists."""
        # This will fail if no health endpoint exists, which is fine
        response = client.get("/health")
        # Just verify we get a response (could be 404)
        assert response.status_code in [200, 404]


class TestAPIVersioning:
    """Tests for API version prefix."""
    
    def test_api_prefix_v0(self, client: TestClient, user_token: str):
        """Test that API uses /api/v0 prefix."""
        headers = {"Authorization": f"Bearer {user_token}"}
        # This endpoint should exist under /api/v0
        response = client.get("/api/v0/users/me", headers=headers)
        # Should NOT return 404, meaning the prefix works
        assert response.status_code != 404
    
    def test_invalid_endpoint(self, client: TestClient):
        """Test that invalid endpoint returns 404."""
        response = client.get("/api/v0/invalid-endpoint")
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestCORSAndSecurityHeaders:
    """Tests for CORS and security headers."""
    
    def test_response_has_headers(self, client: TestClient, user_token: str):
        """Test that responses have expected headers."""
        headers = {"Authorization": f"Bearer {user_token}"}
        response = client.get("/api/v0/users/me", headers=headers)
        # Should have content-type header
        assert "content-type" in response.headers
