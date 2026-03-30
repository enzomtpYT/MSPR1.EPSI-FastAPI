from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.database import get_db
from src.models.workout_session import WorkoutSession
from src.models.user import User
from src.schemas import WorkoutSessionCreate, WorkoutSessionRead
from src.auth import get_current_user

router = APIRouter(prefix="/workout-sessions", tags=["workout-sessions"])
DB = Annotated[Session, Depends(get_db)]
CurrentUser = Annotated[User, Depends(get_current_user)]


@router.post("/", response_model=WorkoutSessionRead, status_code=201)
def create_session(session: WorkoutSessionCreate, db: DB, current_user: CurrentUser):
    db_session = WorkoutSession(**session.model_dump(), User_ID=current_user.User_ID)
    db.add(db_session)
    db.commit()
    db.refresh(db_session)
    return db_session


@router.get("/", response_model=list[WorkoutSessionRead])
def get_sessions(db: DB, current_user: CurrentUser, skip: int = 0, limit: int = 100):
    return db.query(WorkoutSession).filter(WorkoutSession.User_ID == current_user.User_ID).offset(skip).limit(limit).all()


@router.get("/{session_id}", response_model=WorkoutSessionRead)
def get_session(session_id: int, db: DB, current_user: CurrentUser):
    session = db.query(WorkoutSession).filter(
        WorkoutSession.Session_ID == session_id,
        WorkoutSession.User_ID == current_user.User_ID
    ).first()
    if not session:
        raise HTTPException(404, "Workout session not found")
    return session


@router.put("/{session_id}", response_model=WorkoutSessionRead)
def update_session(session_id: int, payload: WorkoutSessionCreate, db: DB, current_user: CurrentUser):
    session = db.query(WorkoutSession).filter(
        WorkoutSession.Session_ID == session_id,
        WorkoutSession.User_ID == current_user.User_ID
    ).first()
    if not session:
        raise HTTPException(404, "Workout session not found")
    for key, value in payload.model_dump().items():
        setattr(session, key, value)
    db.commit()
    db.refresh(session)
    return session


@router.delete("/{session_id}", status_code=204)
def delete_session(session_id: int, db: DB, current_user: CurrentUser):
    session = db.query(WorkoutSession).filter(
        WorkoutSession.Session_ID == session_id,
        WorkoutSession.User_ID == current_user.User_ID
    ).first()
    if not session:
        raise HTTPException(404, "Workout session not found")
    db.delete(session)
    db.commit()
