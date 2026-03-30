from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, Table, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from src.database import Base

user_equipment_association = Table(
    'user_equipment',
    Base.metadata,
    Column('User_ID', Integer, ForeignKey('users.User_ID'), primary_key=True),
    Column('Equipment_ID', Integer, ForeignKey('equipment.Equipment_ID'), primary_key=True)
)

class User(Base):
    __tablename__ = "users"

    User_ID = Column(Integer, primary_key=True, index=True)
    User_mail = Column(String, unique=True, index=True)
    User_password = Column(String)
    isAdmin = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    User_Subscription = Column(String, nullable=True)
    User_age = Column(Integer, nullable=True)
    User_weight = Column(Float, nullable=True)
    User_Height = Column(Float, nullable=True)
    User_gender = Column(String, nullable=True)
    User_Goals = Column(String, nullable=True)
    User_Allergies = Column(String, nullable=True)
    User_Dietary_Preferences = Column(String, nullable=True)
    User_Budget_Level = Column(String, nullable=True)
    User_Injuries = Column(String, nullable=True)

    equipment = relationship("Equipment", secondary=user_equipment_association, back_populates="users")
