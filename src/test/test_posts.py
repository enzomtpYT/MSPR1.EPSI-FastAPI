import pytest
from fastapi.testclient import TestClient

from src.test.conftest import get_auth_header

def test_create_post(client: TestClient, user_token: str):
    response = client.post(
        "/api/v0/posts/",
        data={"content": "Hello world", "mediaType": "none"},
        headers=get_auth_header(user_token)
    )
    assert response.status_code == 201
    data = response.json()
    assert data["text"] == "Hello world"
    assert data["mediaType"] == "none"
    assert data["likesCount"] == 0
    assert "id" in data

def test_get_posts(client: TestClient, user_token: str):
    client.post(
        "/api/v0/posts/",
        data={"content": "Feed post", "mediaType": "none"},
        headers=get_auth_header(user_token)
    )
    response = client.get("/api/v0/posts/", headers=get_auth_header(user_token))
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert data[0]["text"] == "Feed post"

def test_like_post_and_get_likes(client: TestClient, user_token: str):
    post_response = client.post(
        "/api/v0/posts/",
        data={"content": "To be liked", "mediaType": "none"},
        headers=get_auth_header(user_token)
    )
    post_id = post_response.json()["id"]

    # Toggle like on
    like_response = client.post(
        f"/api/v0/posts/{post_id}/like",
        headers=get_auth_header(user_token)
    )
    assert like_response.status_code == 200
    assert like_response.json()["isLiked"] is True
    assert like_response.json()["likesCount"] == 1

    # Get likes
    likes_list = client.get(
        f"/api/v0/posts/{post_id}/likes",
        headers=get_auth_header(user_token)
    )
    assert likes_list.status_code == 200
    assert len(likes_list.json()) == 1

    # Toggle like off
    unlike_response = client.post(
        f"/api/v0/posts/{post_id}/like",
        headers=get_auth_header(user_token)
    )
    assert unlike_response.status_code == 200
    assert unlike_response.json()["isLiked"] is False
    assert unlike_response.json()["likesCount"] == 0

def test_comments_and_delete(client: TestClient, user_token: str):
    post_response = client.post(
        "/api/v0/posts/",
        data={"content": "To be commented", "mediaType": "none"},
        headers=get_auth_header(user_token)
    )
    post_id = post_response.json()["id"]

    # Add comment
    comment_response = client.post(
        f"/api/v0/posts/{post_id}/comments",
        json={"text": "Nice post!"},
        headers=get_auth_header(user_token)
    )
    assert comment_response.status_code == 201
    comment_id = comment_response.json()["id"]

    # Get comments
    get_comments = client.get(
        f"/api/v0/posts/{post_id}/comments?sort=desc",
        headers=get_auth_header(user_token)
    )
    assert get_comments.status_code == 200
    assert len(get_comments.json()) == 1
    assert get_comments.json()[0]["text"] == "Nice post!"

    # Delete comment
    delete_response = client.delete(
        f"/api/v0/posts/{post_id}/comments/{comment_id}",
        headers=get_auth_header(user_token)
    )
    assert delete_response.status_code == 204

    # Verify deleted
    get_comments_after = client.get(
        f"/api/v0/posts/{post_id}/comments",
        headers=get_auth_header(user_token)
    )
    assert len(get_comments_after.json()) == 0

def test_delete_post(client: TestClient, user_token: str):
    post_response = client.post(
        "/api/v0/posts/",
        data={"content": "To be deleted", "mediaType": "none"},
        headers=get_auth_header(user_token)
    )
    post_id = post_response.json()["id"]

    delete_response = client.delete(
        f"/api/v0/posts/{post_id}",
        headers=get_auth_header(user_token)
    )
    assert delete_response.status_code == 204

def test_delete_post_unauthorized(client: TestClient, user_token: str):
    # User 1 creates a post
    post_response = client.post(
        "/api/v0/posts/",
        data={"content": "To be deleted by unauthorized", "mediaType": "none"},
        headers=get_auth_header(user_token)
    )
    post_id = post_response.json()["id"]

    # User 2 registers and tries to delete it
    register_res = client.post(
        "/api/v0/auth/register",
        json={"displayName": "Hacker", "email": "hacker@example.com", "password": "pass"}
    )
    hacker_token = register_res.json()["token"]

    delete_response = client.delete(
        f"/api/v0/posts/{post_id}",
        headers=get_auth_header(hacker_token)
    )
    assert delete_response.status_code == 403

def test_delete_comment_unauthorized(client: TestClient, user_token: str):
    # User 1 creates a post and a comment
    post_response = client.post(
        "/api/v0/posts/",
        data={"content": "Commented post", "mediaType": "none"},
        headers=get_auth_header(user_token)
    )
    post_id = post_response.json()["id"]
    
    comment_response = client.post(
        f"/api/v0/posts/{post_id}/comments",
        json={"text": "User 1 comment"},
        headers=get_auth_header(user_token)
    )
    comment_id = comment_response.json()["id"]

    # User 2 registers and tries to delete User 1's comment
    register_res = client.post(
        "/api/v0/auth/register",
        json={"displayName": "Hacker2", "email": "hacker2@example.com", "password": "pass"}
    )
    hacker_token = register_res.json()["token"]

    delete_response = client.delete(
        f"/api/v0/posts/{post_id}/comments/{comment_id}",
        headers=get_auth_header(hacker_token)
    )
    assert delete_response.status_code == 403
