from datetime import datetime, timezone
from sqlalchemy import Column, Integer, Float, Date, String, ForeignKey, DateTime
from src.database import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)

class WorkoutSession(Base):
    __tablename__ = "workout_sessions"

    Session_ID = Column(Integer, primary_key=True, index=True)
    User_ID = Column(Integer, ForeignKey("users.User_ID"))
    Session_Date = Column(Date)
    Session_MaxBpm = Column(Integer, nullable=True)
    Session_AvgBpm = Column(Integer, nullable=True)
    Session_RestingBpm = Column(Integer, nullable=True)
    Session_Duration = Column(Integer, nullable=True)
    Session_Type = Column(String, nullable=True)
    User_Feedback_Score = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=utc_now, nullable=False)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)
