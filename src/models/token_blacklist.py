from sqlalchemy import Column, Integer, String, DateTime
from src.database import Base
from datetime import datetime, timezone

def utc_now() -> datetime:
    return datetime.now(timezone.utc)

class BlacklistedToken(Base):
    __tablename__ = "blacklisted_tokens"

    id = Column(Integer, primary_key=True, index=True)
    token = Column(String, unique=True, index=True, nullable=False)
    blacklisted_on = Column(DateTime, default=utc_now, nullable=False)
