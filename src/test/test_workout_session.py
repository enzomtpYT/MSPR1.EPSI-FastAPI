"""Tests for workout session endpoints."""

from datetime import date

from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from src.auth import create_access_token, hash_password
from src.models.user import User
from src.models.workout_session import WorkoutSession


class TestWorkoutSessionEndpoints:
    """Tests for workout session CRUD and ownership rules."""

    def test_create_workout_session_success(self, client: TestClient, test_user: User, user_token: str):
        headers = {"Authorization": f"Bearer {user_token}"}
        response = client.post(
            "/api/v0/workout-sessions/",
            json={
                "User_ID": 99999,
                "Session_Date": "2026-03-30",
                "Session_Duration": 45,
                "Session_Type": "cardio",
            },
            headers=headers,
        )

        assert response.status_code == status.HTTP_201_CREATED
        payload = response.json()
        assert payload["User_ID"] == test_user.User_ID
        assert payload["Session_Duration"] == 45

    def test_create_workout_session_unauthorized(self, client: TestClient):
        response = client.post(
            "/api/v0/workout-sessions/",
            json={
                "User_ID": 1,
                "Session_Date": "2026-03-30",
                "Session_Duration": 30,
                "Session_Type": "strength",
            },
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_sessions_returns_only_current_user_data(
        self,
        client: TestClient,
        db: Session,
        test_user: User,
        user_token: str,
    ):
        other_user = User(
            User_mail="workout-other@example.com",
            User_password=hash_password("otherpassword123"),
            isAdmin=False,
        )
        db.add(other_user)
        db.commit()

        own_session = WorkoutSession(
            User_ID=test_user.User_ID,
            Session_Date=date(2026, 3, 1),
            Session_Duration=35,
            Session_Type="cardio",
        )
        other_session = WorkoutSession(
            User_ID=other_user.User_ID,
            Session_Date=date(2026, 3, 2),
            Session_Duration=60,
            Session_Type="strength",
        )
        db.add_all([own_session, other_session])
        db.commit()

        headers = {"Authorization": f"Bearer {user_token}"}
        response = client.get("/api/v0/workout-sessions/", headers=headers)

        assert response.status_code == status.HTTP_200_OK
        returned_ids = [item["Session_ID"] for item in response.json()]
        assert own_session.Session_ID in returned_ids
        assert other_session.Session_ID not in returned_ids

    def test_get_session_not_found_for_other_user(
        self,
        client: TestClient,
        db: Session,
        test_user: User,
        user_token: str,
    ):
        other_user = User(
            User_mail="workout-owner@example.com",
            User_password=hash_password("ownerpassword123"),
            isAdmin=False,
        )
        db.add(other_user)
        db.commit()
        db.refresh(other_user)

        other_session = WorkoutSession(
            User_ID=other_user.User_ID,
            Session_Date=date(2026, 3, 7),
            Session_Duration=50,
            Session_Type="mobility",
        )
        db.add(other_session)
        db.commit()
        db.refresh(other_session)

        token = create_access_token(data={"sub": str(test_user.User_ID)})
        headers = {"Authorization": f"Bearer {token}"}
        response = client.get(
            f"/api/v0/workout-sessions/{other_session.Session_ID}",
            headers=headers,
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "Workout session not found" in response.json()["detail"]

    def test_update_and_delete_workout_session(
        self,
        client: TestClient,
        db: Session,
        test_user: User,
        user_token: str,
    ):
        session = WorkoutSession(
            User_ID=test_user.User_ID,
            Session_Date=date(2026, 3, 12),
            Session_Duration=40,
            Session_Type="run",
        )
        db.add(session)
        db.commit()
        db.refresh(session)

        headers = {"Authorization": f"Bearer {user_token}"}

        update_response = client.put(
            f"/api/v0/workout-sessions/{session.Session_ID}",
            json={
                "User_ID": test_user.User_ID,
                "Session_Date": "2026-03-13",
                "Session_Duration": 55,
                "Session_Type": "cycling",
            },
            headers=headers,
        )
        assert update_response.status_code == status.HTTP_200_OK
        assert update_response.json()["Session_Duration"] == 55

        delete_response = client.delete(
            f"/api/v0/workout-sessions/{session.Session_ID}",
            headers=headers,
        )
        assert delete_response.status_code == status.HTTP_204_NO_CONTENT

        get_response = client.get(
            f"/api/v0/workout-sessions/{session.Session_ID}",
            headers=headers,
        )
        assert get_response.status_code == status.HTTP_404_NOT_FOUND
