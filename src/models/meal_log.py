from datetime import datetime
from sqlalchemy import Column, Integer, Date, ForeignKey, DateTime
from src.database import Base

class MealLog(Base):
    __tablename__ = "meal_logs"

    Log_ID = Column(Integer, primary_key=True, index=True)
    User_ID = Column(Integer, ForeignKey("users.User_ID"))
    Product_ID = Column(Integer, ForeignKey("products.Product_ID"))
    Log_Date = Column(Date)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
