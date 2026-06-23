from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.database import get_db
from src.models.user import User
from src.schemas import Token, UserRegister, AuthLogin
from src.auth import hash_password, verify_password, create_access_token
from src.config import settings

router = APIRouter(prefix="/auth", tags=["auth"])
DB = Annotated[Session, Depends(get_db)]


@router.post("/register", response_model=Token, status_code=201)
def register(user: UserRegister, db: DB):
    """Register a new user and return a token."""
    existing_user = db.query(User).filter(User.User_mail == user.email).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )

    hashed_password = hash_password(user.password)

    db_user = User(
        User_DisplayName=user.displayName,
        User_mail=user.email,
        User_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(db_user.User_ID)}, expires_delta=access_token_expires
    )
    return {"token": access_token}


@router.post("/login", response_model=Token)
def login(credentials: AuthLogin, db: DB):
    """Login endpoint that returns JWT token."""
    user = db.query(User).filter(User.User_mail == credentials.email).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    if not verify_password(credentials.password, user.User_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.User_ID)}, expires_delta=access_token_expires
    )
    return {"token": access_token}
