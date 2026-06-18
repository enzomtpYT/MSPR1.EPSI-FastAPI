from datetime import datetime, timezone
import enum
from sqlalchemy import Column, Integer, String, Text, ForeignKey, DateTime, Enum, JSON
from sqlalchemy.orm import relationship
from src.database import Base

def utc_now() -> datetime:
    return datetime.now(timezone.utc)

class MediaType(str, enum.Enum):
    image = "image"
    video = "video"
    none = "none"

class Post(Base):
    __tablename__ = "posts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.User_ID"), nullable=False)
    content = Column(String(500), nullable=True)
    media_type = Column(Enum(MediaType), default=MediaType.none, nullable=False)
    media_urls = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=utc_now, nullable=False)
    updated_at = Column(DateTime, default=utc_now, onupdate=utc_now, nullable=False)

    user = relationship("User", back_populates="posts")
    comments = relationship("Comment", back_populates="post", cascade="all, delete-orphan")
    likes = relationship("Like", back_populates="post", cascade="all, delete-orphan")
