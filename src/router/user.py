from typing import Annotated
from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from src.database import get_db
from src.models.user import User
from src.schemas import UserCreate, UserRead, UserLogin, Token
from src.auth import hash_password, verify_password, create_access_token, get_current_user
from src.config import settings

router = APIRouter(prefix="/users", tags=["users"])
DB = Annotated[Session, Depends(get_db)]


@router.post("/", response_model=UserRead, status_code=201)
def create_user(user: UserCreate, db: DB):
    """Create a new user with hashed password."""
    # Check if user already exists
    existing_user = db.query(User).filter(User.User_mail == user.User_mail).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this email already exists"
        )
    
    # Hash the password
    hashed_password = hash_password(user.User_password)
    
    # Create user with hashed password
    user_data = user.model_dump()
    user_data["User_password"] = hashed_password
    
    db_user = User(**user_data)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@router.post("/login", response_model=Token)
def login(credentials: UserLogin, db: DB):
    """Login endpoint that returns JWT token."""
    user = db.query(User).filter(User.User_mail == credentials.User_mail).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    if not verify_password(credentials.User_password, user.User_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.User_ID)}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/", response_model=list[UserRead])
def get_users(
    db: DB,
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(get_current_user),
):
    """Get all users (admin only)."""
    if not current_user.isAdmin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admins can list all users"
        )
    return db.query(User).offset(skip).limit(limit).all()


@router.get("/me", response_model=UserRead)
def get_current_user_profile(current_user: User = Depends(get_current_user)):
    """Get current authenticated user profile."""
    return current_user


@router.get("/{user_id}", response_model=UserRead)
def get_user(
    user_id: int,
    db: DB,
    current_user: User = Depends(get_current_user),
):
    """Get a specific user by ID (admin or self only)."""
    # Allow users to view their own profile or admins to view any profile
    if current_user.User_ID != user_id and not current_user.isAdmin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this user"
        )
    
    user = db.query(User).filter(User.User_ID == user_id).first()
    if not user:
        raise HTTPException(404, "User not found")
    return user


@router.put("/{user_id}", response_model=UserRead)
def update_user(
    user_id: int,
    payload: UserCreate,
    db: DB,
    current_user: User = Depends(get_current_user),
):
    """Update a user (self or admin only)."""
    # Verify that user is updating their own profile or is an admin
    if current_user.User_ID != user_id and not current_user.isAdmin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this user"
        )
    
    user = db.query(User).filter(User.User_ID == user_id).first()
    if not user:
        raise HTTPException(404, "User not found")
    
    # Hash password if provided
    update_data = payload.model_dump()
    if update_data.get("User_password"):
        update_data["User_password"] = hash_password(update_data["User_password"])
    
    for key, value in update_data.items():
        setattr(user, key, value)
    
    db.commit()
    db.refresh(user)
    return user


@router.delete("/{user_id}", status_code=204)
def delete_user(user_id: int, db: DB, current_user: User = Depends(get_current_user)):
    """Delete a user (self or admin only)."""
    # Verify that user is deleting their own profile or is an admin
    if current_user.User_ID != user_id and not current_user.isAdmin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to delete this user"
        )
    
    user = db.query(User).filter(User.User_ID == user_id).first()
    if not user:
        raise HTTPException(404, "User not found")
    db.delete(user)
    db.commit()
