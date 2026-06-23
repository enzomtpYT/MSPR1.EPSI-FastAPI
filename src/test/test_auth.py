import pytest
from fastapi.testclient import TestClient

from src.test.conftest import get_auth_header

def test_auth_register(client: TestClient):
    response = client.post(
        "/api/v0/auth/register",
        json={
            "displayName": "TestUser",
            "email": "testauth@example.com",
            "password": "password123"
        }
    )
    assert response.status_code == 201
    assert "token" in response.json()

def test_auth_register_duplicate_email(client: TestClient):
    client.post(
        "/api/v0/auth/register",
        json={
            "displayName": "User1",
            "email": "dup@example.com",
            "password": "password123"
        }
    )
    response = client.post(
        "/api/v0/auth/register",
        json={
            "displayName": "User2",
            "email": "dup@example.com",
            "password": "password123"
        }
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "User with this email already exists"

def test_auth_register_duplicate_displayname(client: TestClient):
    client.post(
        "/api/v0/auth/register",
        json={
            "displayName": "UniqueName",
            "email": "unique1@example.com",
            "password": "password123"
        }
    )
    response = client.post(
        "/api/v0/auth/register",
        json={
            "displayName": "UniqueName",
            "email": "unique2@example.com",
            "password": "password123"
        }
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "This display name is already taken"

def test_auth_login_success(client: TestClient):
    client.post(
        "/api/v0/auth/register",
        json={
            "displayName": "LoginUser",
            "email": "loginuser@example.com",
            "password": "password123"
        }
    )
    response = client.post(
        "/api/v0/auth/login",
        data={
            "username": "loginuser@example.com",
            "password": "password123"
        }
    )
    assert response.status_code == 200
    assert "token" in response.json()

def test_auth_login_fail(client: TestClient):
    response = client.post(
        "/api/v0/auth/login",
        data={
            "username": "wrong@example.com",
            "password": "password123"
        }
    )
    assert response.status_code == 401

def test_auth_logout(client: TestClient):
    response = client.post("/api/v0/auth/logout")
    assert response.status_code == 200
    assert response.json()["message"] == "Successfully logged out"
