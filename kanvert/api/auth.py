"""
Authentication API endpoints for user management.
"""

from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr
from jose import jwt
import secrets
import structlog
import json
from ..config.settings import get_settings
from ..core.database import get_database, fetch_one, insert_record, update_record

router = APIRouter(prefix="/auth", tags=["authentication"])
security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
settings = get_settings()
logger = structlog.get_logger(__name__)


class SubscriptionTier:
    FREE = "FREE"
    PROFESSIONAL = "PROFESSIONAL"
    ENTERPRISE = "ENTERPRISE"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str
    remember_me: bool = False


class LoginResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int
    user: dict


class RegisterRequest(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    password: str
    terms_accepted: bool
    newsletter_subscription: bool = False


class PasswordResetRequest(BaseModel):
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    email: EmailStr
    token: str
    new_password: str


class TokenValidation(BaseModel):
    valid: bool
    user_id: Optional[str] = None


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Generate password hash."""
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Create JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt


def decode_access_token(token: str) -> dict:
    """Decode and validate JWT token."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except jwt.PyJWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Get current authenticated user from SQLite database."""
    token = credentials.credentials
    payload = decode_access_token(token)
    user_id: str = payload.get("sub")
    email: str = payload.get("email")
    
    if user_id is None or email is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )
    
    # Find user in database
    user_data = await fetch_one(
        "SELECT id, email, name, subscription, created_at, last_login, email_verified FROM users WHERE id = ? AND email = ?",
        (user_id, email)
    )
    
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    return user_data


@router.post("/register", response_model=LoginResponse)
async def register(request: RegisterRequest):
    """Register a new user account using SQLite database."""
    logger.info("Registration attempt", email=request.email)
    
    if not request.terms_accepted:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Terms and conditions must be accepted"
        )
    
    # Check if user already exists
    existing_user = await fetch_one("SELECT id FROM users WHERE email = ?", (request.email,))
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered"
        )
    
    # Create new user
    user_id = secrets.token_urlsafe(16)
    api_key = f"kv_{secrets.token_urlsafe(32)}"
    
    user_data = {
        "id": user_id,
        "email": request.email,
        "name": f"{request.first_name} {request.last_name}",
        "first_name": request.first_name,
        "last_name": request.last_name,
        "password_hash": get_password_hash(request.password),
        "subscription": SubscriptionTier.FREE,
        "api_key": api_key,
        "email_verified": False,
        "newsletter_subscription": request.newsletter_subscription,
    }
    
    # Insert user into database
    await insert_record("users", user_data)
    
    logger.info("User registered successfully", user_id=user_id, email=request.email)
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user_id, "email": request.email}, expires_delta=access_token_expires
    )
    
    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        user={
            "id": user_id,
            "email": request.email,
            "name": f"{request.first_name} {request.last_name}",
            "subscription": SubscriptionTier.FREE,
            "api_key": api_key
        }
    )


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest):
    """Authenticate user and return access token using SQLite database."""
    logger.info("Login attempt", email=request.email)
    
    # Check if user exists and get user data
    user_data = await fetch_one(
        "SELECT id, email, name, password_hash, subscription, api_key FROM users WHERE email = ?",
        (request.email,)
    )
    
    if not user_data:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Verify password
    if not verify_password(request.password, user_data["password_hash"]):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    
    # Update last login
    await update_record("users", user_data["id"], {"last_login": datetime.utcnow().isoformat()})
    
    logger.info("User logged in successfully", user_id=user_data["id"], email=request.email)
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    if request.remember_me:
        access_token_expires = timedelta(days=30)  # Extended for remember me
    
    access_token = create_access_token(
        data={"sub": user_data["id"], "email": request.email}, 
        expires_delta=access_token_expires
    )
    
    return LoginResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=int(access_token_expires.total_seconds()),
        user={
            "id": user_data["id"],
            "email": user_data["email"],
            "name": user_data["name"],
            "subscription": user_data["subscription"],
            "api_key": user_data["api_key"]
        }
    )


@router.get("/me")
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """Get current user information."""
    # Return user info without sensitive data
    return {
        "id": current_user["id"],
        "email": current_user["email"],
        "name": current_user["name"],
        "subscription": current_user["subscription"],
        "created_at": current_user["created_at"],
        "last_login": current_user["last_login"],
        "email_verified": current_user["email_verified"]
    }


@router.post("/validate-token", response_model=TokenValidation)
async def validate_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Validate JWT token."""
    try:
        token = credentials.credentials
        payload = decode_access_token(token)
        user_id = payload.get("sub")
        
        if not user_id:
            return TokenValidation(valid=False)
        
        return TokenValidation(valid=True, user_id=user_id)
    except HTTPException:
        return TokenValidation(valid=False)


@router.post("/refresh-api-key")
async def refresh_api_key(current_user: dict = Depends(get_current_user)):
    """Generate new API key for user."""
    new_api_key = f"kv_{secrets.token_urlsafe(32)}"
    
    # Update in database
    await update_record("users", current_user["id"], {"api_key": new_api_key})
    
    logger.info("API key refreshed", user_id=current_user["id"])
    
    return {"api_key": new_api_key}


@router.get("/debug/users")
async def debug_list_users():
    """Debug endpoint to list all registered users (development only)."""
    if not settings.debug:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Not found"
        )
    
    # Get all users from database
    users = await fetch_all(
        "SELECT id, email, name, subscription, created_at, email_verified FROM users ORDER BY created_at DESC"
    )
    
    return {"users": users, "total": len(users)}