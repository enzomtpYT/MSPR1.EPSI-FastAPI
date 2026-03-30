"""Test configuration and fixtures."""
import os
from datetime import timedelta
from typing import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

from src.app import app
from src.auth import create_access_token
from src.config import settings
from src.database import Base, get_db
from src.models.user import User
from src.models.product import Product

# Use SQLite in-memory database for tests (thread-safe)
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
    echo=False,
)

# Enable foreign key support for SQLite
@event.listens_for(engine, "connect")
def set_sqlite_pragma(dbapi_conn, connection_record):
    cursor = dbapi_conn.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db() -> Generator[Session, None, None]:
    """Create a fresh database for each test."""
    Base.metadata.create_all(bind=engine)
    db_session = TestingSessionLocal()
    try:
        yield db_session
    finally:
        db_session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db: Session) -> Generator[TestClient, None, None]:
    """Create a test client with test database."""
    
    def override_get_db():
        try:
            yield db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as test_client:
        yield test_client
    
    app.dependency_overrides.clear()


@pytest.fixture
def test_user(db: Session) -> User:
    """Create a test user."""
    from src.auth import hash_password
    
    user = User(
        User_mail="testuser@example.com",
        User_password=hash_password("testpassword123"),
        isAdmin=False,
        User_age=25,
        User_weight=70.0,
        User_Height=175.0,
        User_gender="M",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def admin_user(db: Session) -> User:
    """Create a test admin user."""
    from src.auth import hash_password
    
    user = User(
        User_mail="admin@example.com",
        User_password=hash_password("adminpassword123"),
        isAdmin=True,
        User_age=30,
        User_weight=75.0,
        User_Height=180.0,
        User_gender="M",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def test_product(db: Session) -> Product:
    """Create a test product."""
    product = Product(
        product_name="Test Product",
        product_kcal=100.0,
        product_protein=20.0,
        product_carbs=30.0,
        product_fat=5.0,
    )
    db.add(product)
    db.commit()
    db.refresh(product)
    return product


@pytest.fixture
def user_token(test_user: User) -> str:
    """Generate a valid JWT token for test_user."""
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return create_access_token(
        data={"sub": str(test_user.User_ID)},
        expires_delta=access_token_expires
    )


@pytest.fixture
def admin_token(admin_user: User) -> str:
    """Generate a valid JWT token for admin_user."""
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    return create_access_token(
        data={"sub": str(admin_user.User_ID)},
        expires_delta=access_token_expires
    )


def get_auth_header(token: str) -> dict:
    """Helper to create authorization header."""
    return {"Authorization": f"Bearer {token}"}
