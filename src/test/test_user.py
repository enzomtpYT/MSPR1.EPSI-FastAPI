"""Tests for user endpoints."""
import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from src.models.user import User


class TestUserCreate:
    """Tests for user creation endpoint."""
    
    def test_create_user_success(self, client: TestClient):
        """Test successful user creation."""
        response = client.post(
            "/api/v0/users/",
            json={
                "User_mail": "newuser@example.com",
                "User_password": "securepassword123",
                "User_age": 25,
                "User_weight": 70.0,
                "User_Height": 175.0,
                "User_gender": "M",
            },
        )
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["User_mail"] == "newuser@example.com"
        assert data["isAdmin"] is False
        assert "User_ID" in data
        assert "created_at" in data
    
    def test_create_user_duplicate_email(self, client: TestClient, test_user: User):
        """Test creating user with duplicate email fails."""
        response = client.post(
            "/api/v0/users/",
            json={
                "User_mail": test_user.User_mail,
                "User_password": "differentpassword123",
                "User_age": 30,
            },
        )
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "already exists" in response.json()["detail"]
    
    def test_create_user_missing_email(self, client: TestClient):
        """Test creating user without email fails."""
        response = client.post(
            "/api/v0/users/",
            json={
                "User_password": "securepassword123",
            },
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    
    def test_create_user_missing_password(self, client: TestClient):
        """Test creating user without password fails."""
        response = client.post(
            "/api/v0/users/",
            json={
                "User_mail": "newuser@example.com",
            },
        )
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY


class TestUserLogin:
    """Tests for user login endpoint."""
    
    def test_login_success(self, client: TestClient, test_user: User):
        """Test successful login."""
        response = client.post(
            "/api/v0/users/login",
            json={
                "User_mail": "testuser@example.com",
                "User_password": "testpassword123",
            },
        )
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
    
    def test_login_invalid_email(self, client: TestClient):
        """Test login with non-existent email fails."""
        response = client.post(
            "/api/v0/users/login",
            json={
                "User_mail": "nonexistent@example.com",
                "User_password": "anypassword",
            },
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Invalid email or password" in response.json()["detail"]
    
    def test_login_invalid_password(self, client: TestClient, test_user: User):
        """Test login with wrong password fails."""
        response = client.post(
            "/api/v0/users/login",
            json={
                "User_mail": "testuser@example.com",
                "User_password": "wrongpassword",
            },
        )
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "Invalid email or password" in response.json()["detail"]


class TestGetUsers:
    """Tests for getting users endpoint."""
    
    def test_get_users_unauthorized(self, client: TestClient):
        """Test getting users without authentication fails."""
        response = client.get("/api/v0/users/")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
    
    def test_get_users_non_admin(self, client: TestClient, user_token: str):
        """Test regular user cannot list all users."""
        headers = {"Authorization": f"Bearer {user_token}"}
        response = client.get("/api/v0/users/", headers=headers)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "Only admins can list all users" in response.json()["detail"]
    
    def test_get_users_admin(self, client: TestClient, admin_token: str, admin_user: User, test_user: User):
        """Test admin can list all users."""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = client.get("/api/v0/users/", headers=headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) >= 2
        emails = [user["User_mail"] for user in data]
        assert test_user.User_mail in emails
        assert admin_user.User_mail in emails


class TestGetCurrentUser:
    """Tests for getting current user profile."""
    
    def test_get_current_user_success(self, client: TestClient, user_token: str, test_user: User):
        """Test getting current user profile."""
        headers = {"Authorization": f"Bearer {user_token}"}
        response = client.get("/api/v0/users/me", headers=headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["User_mail"] == test_user.User_mail
        assert data["User_ID"] == test_user.User_ID
    
    def test_get_current_user_unauthorized(self, client: TestClient):
        """Test getting current user without token fails."""
        response = client.get("/api/v0/users/me")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestGetUserById:
    """Tests for getting user by ID endpoint."""
    
    def test_get_user_self(self, client: TestClient, user_token: str, test_user: User):
        """Test user can view their own profile."""
        headers = {"Authorization": f"Bearer {user_token}"}
        response = client.get(f"/api/v0/users/{test_user.User_ID}", headers=headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["User_ID"] == test_user.User_ID
    
    def test_get_user_other_unauthorized(self, client: TestClient, user_token: str, admin_user: User):
        """Test user cannot view another user's profile."""
        headers = {"Authorization": f"Bearer {user_token}"}
        response = client.get(f"/api/v0/users/{admin_user.User_ID}", headers=headers)
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "Not authorized to view this user" in response.json()["detail"]
    
    def test_get_user_admin_can_view_any(self, client: TestClient, admin_token: str, test_user: User):
        """Test admin can view any user's profile."""
        headers = {"Authorization": f"Bearer {admin_token}"}
        response = client.get(f"/api/v0/users/{test_user.User_ID}", headers=headers)
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["User_ID"] == test_user.User_ID
