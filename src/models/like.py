from datetime import datetime, timezone
from sqlalchemy import Column, Integer, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from src.database import Base

def utc_now() -> datetime:
    return datetime.now(timezone.utc)

class Like(Base):
    __tablename__ = "likes"

    user_id = Column(Integer, ForeignKey("users.User_ID"), primary_key=True, nullable=False)
    post_id = Column(Integer, ForeignKey("posts.id"), primary_key=True, nullable=False)
    created_at = Column(DateTime, default=utc_now, nullable=False)

    user = relationship("User", back_populates="likes")
    post = relationship("Post", back_populates="likes")
