from datetime import datetime, timedelta
from typing import Optional, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
import structlog

from app.config import get_settings
from app.database import get_db
from app.models.user import User
from app.core.exceptions import AuthenticationError

logger = structlog.get_logger(__name__)

settings = get_settings()

SECRET_KEY = settings.secret_key
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
security = HTTPBearer()


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hash a password."""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """
    Create a JWT access token.
    
    Args:
        data: Data to encode in the token
        expires_delta: Optional expiration time delta
        
    Returns:
        Encoded JWT token
    """
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire, "iat": datetime.utcnow()})
    
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    
    logger.info("access_token_created", subject=data.get("sub"), expires_at=expire.isoformat())
    
    return encoded_jwt


def decode_access_token(token: str) -> dict:
    """
    Decode and verify a JWT token.
    
    Args:
        token: JWT token string
        
    Returns:
        Decoded token payload
        
    Raises:
        AuthenticationError: If token is invalid or expired
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError as e:
        logger.warning("token_decode_failed", error=str(e))
        raise AuthenticationError("Invalid or expired token")


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> User:
    """
    Get the current authenticated user from JWT token.
    
    Args:
        credentials: HTTP authorization credentials
        db: Database session
        
    Returns:
        Current user object
        
    Raises:
        AuthenticationError: If authentication fails
    """
    token = credentials.credentials
    
    try:
        payload = decode_access_token(token)
        email: str = payload.get("sub")
        
        if email is None:
            raise AuthenticationError("Invalid token payload")
            
    except JWTError:
        raise AuthenticationError("Could not validate credentials")
    
    user = db.query(User).filter(User.email == email).first()
    
    if user is None:
        raise AuthenticationError("User not found")
    
    if not user.is_active:
        raise AuthenticationError("User account is inactive")
    
    logger.debug("user_authenticated", user_id=user.id, email=user.email)
    
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user),
) -> User:
    """Get current active user."""
    if not current_user.is_active:
        raise AuthenticationError("Inactive user")
    return current_user


async def get_current_superuser(
    current_user: User = Depends(get_current_user),
) -> User:
    """Get current superuser."""
    if not current_user.is_superuser:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user


def authenticate_user(db: Session, email: str, password: str) -> Optional[User]:
    """
    Authenticate a user by email and password.
    
    Args:
        db: Database session
        email: User email
        password: Plain text password
        
    Returns:
        User object if authentication succeeds, None otherwise
    """
    user = db.query(User).filter(User.email == email).first()
    
    if not user:
        logger.warning("authentication_failed", email=email, reason="user_not_found")
        return None
    
    if not verify_password(password, user.hashed_password):
        logger.warning("authentication_failed", email=email, reason="invalid_password")
        return None
    
    logger.info("user_authenticated", user_id=user.id, email=email)
    
    return user
