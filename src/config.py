import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")


class Settings:
	def __init__(self) -> None:
		self.DATABASE_URL = os.getenv(
			"DATABASE_URL",
			"postgresql://postgres:postgres@localhost:5432/mspr_db",
		)
		self.SECRET_KEY = os.getenv(
			"SECRET_KEY", "your-secret-key-change-this-in-production"
		)
		self.ALGORITHM = os.getenv("ALGORITHM", "HS256")
		self.ACCESS_TOKEN_EXPIRE_MINUTES = int(
			os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30")
		)
		self.DEFAULT_ADMIN_EMAIL = os.getenv("DEFAULT_ADMIN_EMAIL", "")
		self.DEFAULT_ADMIN_PASSWORD = os.getenv("DEFAULT_ADMIN_PASSWORD", "")
		self.DEFAULT_ADMIN_IS_ADMIN = os.getenv("DEFAULT_ADMIN_IS_ADMIN", "true").lower() in (
			"1",
			"true",
			"yes",
			"on",
		)


settings = Settings()

# Backward-compatible aliases
DATABASE_URL = settings.DATABASE_URL
SECRET_KEY = settings.SECRET_KEY
ALGORITHM = settings.ALGORITHM
ACCESS_TOKEN_EXPIRE_MINUTES = settings.ACCESS_TOKEN_EXPIRE_MINUTES
