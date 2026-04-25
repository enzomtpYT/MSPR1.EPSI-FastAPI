import csv
from datetime import date, datetime
from io import StringIO
from typing import Annotated, Any

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from src.auth import get_current_user
from src.database import get_db
from src.models.biometrics_log import BiometricsLog
from src.models.equipment import Equipment
from src.models.meal_log import MealLog
from src.models.product import Product
from src.models.user import User
from src.models.workout_session import WorkoutSession

router = APIRouter(prefix="/exports", tags=["exports"])
DB = Annotated[Session, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]


def ensure_admin(current_user: User) -> None:
    if not current_user.isAdmin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can export data",
        )


def _format_csv_value(value: Any) -> Any:
    if value is None:
        return ""
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    return value


def csv_response(filename: str, columns: list[str], rows: list[tuple[Any, ...]]) -> Response:
    buffer = StringIO()
    writer = csv.writer(buffer)
    writer.writerow(columns)

    for row in rows:
        writer.writerow([_format_csv_value(value) for value in row])

    return Response(
        content=buffer.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@router.get("/users.csv")
def export_users_csv(db: DB, current_user: CurrentUser):
    ensure_admin(current_user)
    rows = (
        db.query(
            User.User_ID,
            User.User_mail,
            User.isAdmin,
            User.User_Subscription,
            User.User_age,
            User.User_weight,
            User.User_Height,
            User.User_gender,
            User.User_Goals,
            User.User_Allergies,
            User.User_Dietary_Preferences,
            User.User_Budget_Level,
            User.User_Injuries,
            User.created_at,
            User.updated_at,
        )
        .order_by(User.User_ID.asc())
        .all()
    )

    columns = [
        "User_ID",
        "User_mail",
        "isAdmin",
        "User_Subscription",
        "User_age",
        "User_weight",
        "User_Height",
        "User_gender",
        "User_Goals",
        "User_Allergies",
        "User_Dietary_Preferences",
        "User_Budget_Level",
        "User_Injuries",
        "created_at",
        "updated_at",
    ]
    return csv_response("users.csv", columns, rows)


@router.get("/products.csv")
def export_products_csv(db: DB, current_user: CurrentUser):
    ensure_admin(current_user)
    rows = (
        db.query(
            Product.Product_ID,
            Product.product_name,
            Product.product_kcal,
            Product.product_protein,
            Product.product_carbs,
            Product.product_fat,
            Product.product_fiber,
            Product.product_sugar,
            Product.product_sodium,
            Product.product_chol,
            Product.Product_Diet_Tags,
            Product.Product_Price_Category,
            Product.created_at,
            Product.updated_at,
        )
        .order_by(Product.Product_ID.asc())
        .all()
    )

    columns = [
        "Product_ID",
        "product_name",
        "product_kcal",
        "product_protein",
        "product_carbs",
        "product_fat",
        "product_fiber",
        "product_sugar",
        "product_sodium",
        "product_chol",
        "Product_Diet_Tags",
        "Product_Price_Category",
        "created_at",
        "updated_at",
    ]
    return csv_response("products.csv", columns, rows)


@router.get("/equipment.csv")
def export_equipment_csv(db: DB, current_user: CurrentUser):
    ensure_admin(current_user)
    rows = (
        db.query(
            Equipment.Equipment_ID,
            Equipment.Equipment_Name,
            Equipment.Equipment_Category,
            Equipment.Equipment_Location,
            Equipment.created_at,
            Equipment.updated_at,
        )
        .order_by(Equipment.Equipment_ID.asc())
        .all()
    )

    columns = [
        "Equipment_ID",
        "Equipment_Name",
        "Equipment_Category",
        "Equipment_Location",
        "created_at",
        "updated_at",
    ]
    return csv_response("equipment.csv", columns, rows)


@router.get("/meal-logs.csv")
def export_meal_logs_csv(db: DB, current_user: CurrentUser):
    ensure_admin(current_user)
    rows = (
        db.query(
            MealLog.Log_ID,
            MealLog.User_ID,
            MealLog.Product_ID,
            MealLog.Log_Date,
            MealLog.created_at,
            MealLog.updated_at,
        )
        .order_by(MealLog.Log_ID.asc())
        .all()
    )

    columns = [
        "Log_ID",
        "User_ID",
        "Product_ID",
        "Log_Date",
        "created_at",
        "updated_at",
    ]
    return csv_response("meal-logs.csv", columns, rows)


@router.get("/workout-sessions.csv")
def export_workout_sessions_csv(db: DB, current_user: CurrentUser):
    ensure_admin(current_user)
    rows = (
        db.query(
            WorkoutSession.Session_ID,
            WorkoutSession.User_ID,
            WorkoutSession.Session_Date,
            WorkoutSession.Session_MaxBpm,
            WorkoutSession.Session_AvgBpm,
            WorkoutSession.Session_RestingBpm,
            WorkoutSession.Session_Duration,
            WorkoutSession.Session_Type,
            WorkoutSession.User_Feedback_Score,
            WorkoutSession.created_at,
            WorkoutSession.updated_at,
        )
        .order_by(WorkoutSession.Session_ID.asc())
        .all()
    )

    columns = [
        "Session_ID",
        "User_ID",
        "Session_Date",
        "Session_MaxBpm",
        "Session_AvgBpm",
        "Session_RestingBpm",
        "Session_Duration",
        "Session_Type",
        "User_Feedback_Score",
        "created_at",
        "updated_at",
    ]
    return csv_response("workout-sessions.csv", columns, rows)


@router.get("/biometrics-logs.csv")
def export_biometrics_logs_csv(db: DB, current_user: CurrentUser):
    ensure_admin(current_user)
    rows = (
        db.query(
            BiometricsLog.Log_ID,
            BiometricsLog.User_ID,
            BiometricsLog.Log_Date,
            BiometricsLog.Weight,
            BiometricsLog.Sleep_Hours,
            BiometricsLog.Heart_Rate,
            BiometricsLog.created_at,
            BiometricsLog.updated_at,
        )
        .order_by(BiometricsLog.Log_ID.asc())
        .all()
    )

    columns = [
        "Log_ID",
        "User_ID",
        "Log_Date",
        "Weight",
        "Sleep_Hours",
        "Heart_Rate",
        "created_at",
        "updated_at",
    ]
    return csv_response("biometrics-logs.csv", columns, rows)
