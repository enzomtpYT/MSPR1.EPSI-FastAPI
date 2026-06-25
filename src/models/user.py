from datetime import datetime, timezone
from sqlalchemy import Column, Integer, String, Float, Table, ForeignKey, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property
from src.database import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)

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
    User_DisplayName = Column(String, nullable=False, server_default="User")
    isAdmin = Column(Boolean, default=False, nullable=False)
    created_at = Column(DateTime, default=utc_now, nullable=False)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)
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
    _profile_picture_url = Column("profile_picture_url", String, nullable=True)

    @hybrid_property
    def profile_picture_url(self) -> str:
        if self._profile_picture_url:
            return self._profile_picture_url
        name = (self.User_DisplayName or "User").replace(" ", "+")
        return f"https://ui-avatars.com/api/?name={name}&background=random"

    @profile_picture_url.setter
    def profile_picture_url(self, value: str | None) -> None:
        self._profile_picture_url = value

    equipment = relationship("Equipment", secondary=user_equipment_association, back_populates="users")
    posts = relationship("Post", back_populates="user", cascade="all, delete-orphan")
    comments = relationship("Comment", back_populates="user", cascade="all, delete-orphan")
    likes = relationship("Like", back_populates="user", cascade="all, delete-orphan")
