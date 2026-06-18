import pytest
from fastapi.testclient import TestClient

from src.test.conftest import get_auth_header

def test_create_post(client: TestClient, user_token: str):
    response = client.post(
        "/api/v0/posts/",
        json={"content": "Hello world", "media_type": "none"},
        headers=get_auth_header(user_token)
    )
    assert response.status_code == 201
    data = response.json()
    assert data["content"] == "Hello world"
    assert data["media_type"] == "none"
    assert data["likes_count"] == 0
    assert "id" in data

def test_get_feed(client: TestClient, user_token: str):
    # Create a post first
    client.post(
        "/api/v0/posts/",
        json={"content": "Feed post"},
        headers=get_auth_header(user_token)
    )
    
    response = client.get("/api/v0/posts/feed", headers=get_auth_header(user_token))
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["content"] == "Feed post"

def test_like_post(client: TestClient, user_token: str):
    post_response = client.post(
        "/api/v0/posts/",
        json={"content": "To be liked"},
        headers=get_auth_header(user_token)
    )
    post_id = post_response.json()["id"]

    # Like the post
    like_response = client.post(
        f"/api/v0/posts/{post_id}/like",
        headers=get_auth_header(user_token)
    )
    assert like_response.status_code == 201

    # Cannot like again
    like_again = client.post(
        f"/api/v0/posts/{post_id}/like",
        headers=get_auth_header(user_token)
    )
    assert like_again.status_code == 400

    # Check likes_count in feed
    feed_response = client.get("/api/v0/posts/feed?sort=popular", headers=get_auth_header(user_token))
    data = feed_response.json()
    assert any(p["id"] == post_id and p["likes_count"] == 1 for p in data)

    # Unlike the post
    unlike_response = client.delete(
        f"/api/v0/posts/{post_id}/like",
        headers=get_auth_header(user_token)
    )
    assert unlike_response.status_code == 204

def test_comments(client: TestClient, user_token: str):
    post_response = client.post(
        "/api/v0/posts/",
        json={"content": "To be commented"},
        headers=get_auth_header(user_token)
    )
    post_id = post_response.json()["id"]

    # Add comment
    comment_response = client.post(
        f"/api/v0/posts/{post_id}/comments",
        json={"content": "Nice post!"},
        headers=get_auth_header(user_token)
    )
    assert comment_response.status_code == 201
    assert comment_response.json()["content"] == "Nice post!"

    # Get comments
    get_comments = client.get(
        f"/api/v0/posts/{post_id}/comments",
        headers=get_auth_header(user_token)
    )
    assert get_comments.status_code == 200
    assert len(get_comments.json()) == 1
    assert get_comments.json()[0]["content"] == "Nice post!"
