from datetime import datetime
from sqlalchemy import Column, Integer, Float, Date, ForeignKey, DateTime
from src.database import Base

class BiometricsLog(Base):
    __tablename__ = "biometrics_logs"

    Log_ID = Column(Integer, primary_key=True, index=True)
    User_ID = Column(Integer, ForeignKey("users.User_ID"))
    Log_Date = Column(Date)
    Weight = Column(Float, nullable=True)
    Sleep_Hours = Column(Float, nullable=True)
    Heart_Rate = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
