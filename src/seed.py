import logging

from sqlalchemy.orm import Session

from src.auth import hash_password
from src.config import settings
from src.database import SessionLocal
from src.models.user import User


logger = logging.getLogger(__name__)


def seed_default_admin_user(db: Session) -> None:
	"""Create the default admin user if it is configured and missing."""
	email = settings.DEFAULT_ADMIN_EMAIL.strip()
	password = settings.DEFAULT_ADMIN_PASSWORD.strip()

	if not email or not password:
		return

	existing_user = db.query(User).filter(User.User_mail == email).first()
	if existing_user:
		return

	admin_user = User(
		User_mail=email,
		User_password=hash_password(password),
		isAdmin=settings.DEFAULT_ADMIN_IS_ADMIN,
	)
	db.add(admin_user)
	db.commit()


def seed_database() -> None:
	"""Run database seeders after migrations have been applied."""
	db = SessionLocal()
	try:
		seed_default_admin_user(db)
		if settings.DEFAULT_ADMIN_EMAIL.strip() and settings.DEFAULT_ADMIN_PASSWORD.strip():
			logger.info("Default admin seed checked for %s", settings.DEFAULT_ADMIN_EMAIL.strip())
	except Exception:
		db.rollback()
		raise
	finally:
		db.close()