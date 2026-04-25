from datetime import date

from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from src.auth import hash_password, create_access_token
from src.models.biometrics_log import BiometricsLog
from src.models.meal_log import MealLog
from src.models.product import Product
from src.models.user import User
from src.models.workout_session import WorkoutSession


def _auth_header_for(user_id: int) -> dict:
    token = create_access_token(data={"sub": str(user_id)})
    return {"Authorization": f"Bearer {token}"}


class TestAnalyticsSummary:
    def test_get_my_summary_requires_auth(self, client: TestClient):
        response = client.get("/api/v0/analytics/me/summary")
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_my_summary_only_my_data(self, client: TestClient, db: Session, test_user: User):
        other_user = User(
            User_mail="other@example.com",
            User_password=hash_password("otherpassword123"),
            isAdmin=False,
        )
        db.add(other_user)
        db.commit()
        db.refresh(other_user)

        p1 = Product(product_name="P1", product_kcal=100.0)
        p2 = Product(product_name="P2", product_kcal=250.0)
        p3 = Product(product_name="P3", product_kcal=500.0)
        db.add_all([p1, p2, p3])
        db.commit()
        db.refresh(p1)
        db.refresh(p2)
        db.refresh(p3)

        db.add_all(
            [
                MealLog(User_ID=test_user.User_ID, Product_ID=p1.Product_ID, Log_Date=date(2026, 3, 10)),
                MealLog(User_ID=test_user.User_ID, Product_ID=p2.Product_ID, Log_Date=date(2026, 3, 11)),
                MealLog(User_ID=other_user.User_ID, Product_ID=p3.Product_ID, Log_Date=date(2026, 3, 12)),
                WorkoutSession(
                    User_ID=test_user.User_ID,
                    Session_Date=date(2026, 3, 10),
                    Session_Duration=30,
                    Session_Type="cardio",
                ),
                WorkoutSession(
                    User_ID=test_user.User_ID,
                    Session_Date=date(2026, 3, 11),
                    Session_Duration=60,
                    Session_Type="strength",
                ),
                WorkoutSession(
                    User_ID=other_user.User_ID,
                    Session_Date=date(2026, 3, 12),
                    Session_Duration=120,
                    Session_Type="other",
                ),
                BiometricsLog(
                    User_ID=test_user.User_ID,
                    Log_Date=date(2026, 3, 10),
                    Weight=80.0,
                    Sleep_Hours=7.0,
                    Heart_Rate=65,
                ),
                BiometricsLog(
                    User_ID=test_user.User_ID,
                    Log_Date=date(2026, 3, 15),
                    Weight=79.0,
                    Sleep_Hours=8.0,
                    Heart_Rate=64,
                ),
                BiometricsLog(
                    User_ID=other_user.User_ID,
                    Log_Date=date(2026, 3, 20),
                    Weight=120.0,
                    Sleep_Hours=4.0,
                    Heart_Rate=90,
                ),
            ]
        )
        db.commit()

        headers = _auth_header_for(test_user.User_ID)
        response = client.get("/api/v0/analytics/me/summary", headers=headers)

        assert response.status_code == status.HTTP_200_OK
        payload = response.json()

        assert payload["user_id"] == test_user.User_ID
        assert payload["meal_logs_count"] == 2
        assert payload["workout_sessions_count"] == 2
        assert payload["biometrics_logs_count"] == 2
        assert payload["total_logged_kcal"] == 350.0
        assert payload["avg_workout_duration_minutes"] == 45.0
        assert payload["avg_sleep_hours"] == 7.5
        assert payload["latest_weight"] == 79.0

    def test_get_my_summary_empty_state(self, client: TestClient, test_user: User):
        headers = _auth_header_for(test_user.User_ID)
        response = client.get("/api/v0/analytics/me/summary", headers=headers)

        assert response.status_code == status.HTTP_200_OK
        payload = response.json()

        assert payload["user_id"] == test_user.User_ID
        assert payload["meal_logs_count"] == 0
        assert payload["workout_sessions_count"] == 0
        assert payload["biometrics_logs_count"] == 0
        assert payload["total_logged_kcal"] == 0.0
        assert payload["avg_workout_duration_minutes"] is None
        assert payload["avg_sleep_hours"] is None
        assert payload["latest_weight"] is None
