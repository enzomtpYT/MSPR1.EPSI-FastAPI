from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from src.auth import get_current_user
from src.database import get_db
from src.models.biometrics_log import BiometricsLog
from src.models.meal_log import MealLog
from src.models.product import Product
from src.models.user import User
from src.models.workout_session import WorkoutSession
from src.schemas import UserAnalyticsSummary

router = APIRouter(prefix="/analytics", tags=["analytics"])
DB = Annotated[Session, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.get("/me/summary", response_model=UserAnalyticsSummary)
def get_my_analytics_summary(db: DB, current_user: CurrentUser):
    meal_logs_count = (
        db.query(func.count(MealLog.Log_ID))
        .filter(MealLog.User_ID == current_user.User_ID)
        .scalar()
        or 0
    )

    workout_sessions_count = (
        db.query(func.count(WorkoutSession.Session_ID))
        .filter(WorkoutSession.User_ID == current_user.User_ID)
        .scalar()
        or 0
    )

    biometrics_logs_count = (
        db.query(func.count(BiometricsLog.Log_ID))
        .filter(BiometricsLog.User_ID == current_user.User_ID)
        .scalar()
        or 0
    )

    total_logged_kcal = (
        db.query(func.coalesce(func.sum(Product.product_kcal), 0.0))
        .join(MealLog, MealLog.Product_ID == Product.Product_ID)
        .filter(MealLog.User_ID == current_user.User_ID)
        .scalar()
        or 0.0
    )

    avg_workout_duration_minutes = (
        db.query(func.avg(WorkoutSession.Session_Duration))
        .filter(WorkoutSession.User_ID == current_user.User_ID)
        .scalar()
    )

    avg_sleep_hours = (
        db.query(func.avg(BiometricsLog.Sleep_Hours))
        .filter(BiometricsLog.User_ID == current_user.User_ID)
        .scalar()
    )

    latest_weight_row = (
        db.query(BiometricsLog.Weight)
        .filter(BiometricsLog.User_ID == current_user.User_ID)
        .order_by(BiometricsLog.Log_Date.desc(), BiometricsLog.Log_ID.desc())
        .first()
    )
    latest_weight = latest_weight_row[0] if latest_weight_row else None

    return UserAnalyticsSummary(
        user_id=current_user.User_ID,
        meal_logs_count=int(meal_logs_count),
        workout_sessions_count=int(workout_sessions_count),
        biometrics_logs_count=int(biometrics_logs_count),
        total_logged_kcal=float(total_logged_kcal),
        avg_workout_duration_minutes=(
            float(avg_workout_duration_minutes)
            if avg_workout_duration_minutes is not None
            else None
        ),
        avg_sleep_hours=float(avg_sleep_hours) if avg_sleep_hours is not None else None,
        latest_weight=float(latest_weight) if latest_weight is not None else None,
    )
