from datetime import timedelta
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from src.database import get_db
from src.models.user import User
from src.models.token_blacklist import BlacklistedToken
from src.schemas import Token, UserRegister
from src.auth import hash_password, verify_password, create_access_token, oauth2_scheme
from src.config import settings

router = APIRouter(prefix="/auth", tags=["auth"])
DB = Annotated[Session, Depends(get_db)]


@router.post("/register", response_model=Token, status_code=201)
def register(user: UserRegister, db: DB):
    """Register a new user and return a token."""
    # Check email uniqueness
    if db.query(User).filter(User.User_mail == user.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )

    # Check displayName uniqueness
    if db.query(User).filter(User.User_DisplayName == user.displayName).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This display name is already taken"
        )

    db_user = User(
        User_DisplayName=user.displayName,
        User_mail=user.email,
        User_password=hash_password(user.password)
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    access_token = create_access_token(
        data={"sub": str(db_user.User_ID)},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"token": access_token}


@router.post("/login", response_model=Token)
def login(
    credentials: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: DB,
):
    """OAuth2-compliant login endpoint. `username` field carries the email."""
    user = db.query(User).filter(User.User_mail == credentials.username).first()

    if not user or not verify_password(credentials.password, user.User_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        data={"sub": str(user.User_ID)},
        expires_delta=timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"token": access_token}


@router.post("/logout", status_code=status.HTTP_200_OK)
def logout(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: DB,
):
    """Logout by blacklisting the current token."""
    blacklisted = db.query(BlacklistedToken).filter(BlacklistedToken.token == token).first()
    if blacklisted:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token already blacklisted"
        )
        
    db_token = BlacklistedToken(token=token)
    db.add(db_token)
    db.commit()
    
    return {"detail": "Successfully logged out"}
