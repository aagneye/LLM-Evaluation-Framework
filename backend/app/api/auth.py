from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
import structlog

from app.database import get_db
from app.models.user import User
from app.schemas.user_schema import UserCreate, UserLogin, UserResponse, Token
from app.core.security import (
    authenticate_user,
    create_access_token,
    get_password_hash,
    get_current_active_user,
    ACCESS_TOKEN_EXPIRE_MINUTES,
)
from app.core.exceptions import AuthenticationError, ValidationError

logger = structlog.get_logger(__name__)

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Register a new user.
    
    Args:
        user_data: User registration data
        db: Database session
        
    Returns:
        Created user object
        
    Raises:
        ValidationError: If email already exists
    """
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    
    if existing_user:
        logger.warning("registration_failed", email=user_data.email, reason="email_exists")
        raise ValidationError("Email already registered")
    
    hashed_password = get_password_hash(user_data.password)
    
    new_user = User(
        email=user_data.email,
        hashed_password=hashed_password,
        full_name=user_data.full_name,
        is_active=True,
        is_superuser=False,
    )
    
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    logger.info("user_registered", user_id=new_user.id, email=new_user.email)
    
    return new_user


@router.post("/login", response_model=Token)
def login(credentials: UserLogin, db: Session = Depends(get_db)):
    """
    Login and get access token.
    
    Args:
        credentials: Login credentials
        db: Database session
        
    Returns:
        JWT access token
        
    Raises:
        AuthenticationError: If credentials are invalid
    """
    user = authenticate_user(db, credentials.email, credentials.password)
    
    if not user:
        raise AuthenticationError("Incorrect email or password")
    
    if not user.is_active:
        raise AuthenticationError("User account is inactive")
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=access_token_expires
    )
    
    logger.info("user_logged_in", user_id=user.id, email=user.email)
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_active_user)):
    """
    Get current user information.
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        User information
    """
    return current_user
