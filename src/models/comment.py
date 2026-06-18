from datetime import datetime, timezone
from sqlalchemy import Column, Integer, ForeignKey, DateTime, Text
from sqlalchemy.orm import relationship
from src.database import Base

def utc_now() -> datetime:
    return datetime.now(timezone.utc)

class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.User_ID"), nullable=False)
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=utc_now, nullable=False)

    user = relationship("User", back_populates="comments")
    post = relationship("Post", back_populates="comments")
