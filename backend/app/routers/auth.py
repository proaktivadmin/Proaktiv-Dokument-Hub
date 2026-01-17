"""
Authentication Router

Simple password-based authentication for single-user access.
"""

from datetime import datetime, timedelta, timezone
from typing import Optional

import bcrypt
from fastapi import APIRouter, HTTPException, Response, Request, Depends
from jose import jwt, JWTError
from pydantic import BaseModel

from app.config import get_settings

router = APIRouter(prefix="/auth", tags=["auth"])
settings = get_settings()

# JWT Configuration
ALGORITHM = "HS256"


class LoginRequest(BaseModel):
    password: str


class AuthStatus(BaseModel):
    authenticated: bool
    expires_at: Optional[datetime] = None


def create_session_token(expires_delta: Optional[timedelta] = None) -> str:
    """Create a JWT session token."""
    if expires_delta is None:
        expires_delta = timedelta(days=settings.AUTH_SESSION_EXPIRE_DAYS)
    
    expire = datetime.now(timezone.utc) + expires_delta
    to_encode = {
        "exp": expire,
        "iat": datetime.now(timezone.utc),
        "type": "session"
    }
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)


def verify_session_token(token: str) -> Optional[dict]:
    """Verify a JWT session token."""
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[ALGORITHM])
        if payload.get("type") != "session":
            return None
        return payload
    except JWTError:
        return None


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a bcrypt hash."""
    try:
        return bcrypt.checkpw(
            plain_password.encode('utf-8'),
            hashed_password.encode('utf-8')
        )
    except Exception:
        return False


@router.get("/debug-config")
async def debug_config():
    """
    Debug endpoint to check auth configuration.
    Remove this after debugging!
    """
    import os
    fresh_settings = get_settings()
    
    # Get all env vars that contain "APP" or "PASSWORD" or "HASH" (for debugging)
    relevant_env_vars = {
        k: (v[:20] + "..." if len(v) > 20 else v) 
        for k, v in os.environ.items() 
        if any(x in k.upper() for x in ["APP", "PASSWORD", "HASH", "AUTH"])
    }
    
    # List all env var NAMES (not values) to see what's available
    all_env_var_names = sorted([k for k in os.environ.keys()])
    
    return {
        "module_level_hash_set": bool(settings.APP_PASSWORD_HASH),
        "module_level_hash_length": len(settings.APP_PASSWORD_HASH) if settings.APP_PASSWORD_HASH else 0,
        "fresh_settings_hash_set": bool(fresh_settings.APP_PASSWORD_HASH),
        "fresh_settings_hash_length": len(fresh_settings.APP_PASSWORD_HASH) if fresh_settings.APP_PASSWORD_HASH else 0,
        "env_var_set": bool(os.environ.get("APP_PASSWORD_HASH")),
        "env_var_length": len(os.environ.get("APP_PASSWORD_HASH", "")),
        "env_var_starts_with": os.environ.get("APP_PASSWORD_HASH", "")[:10] if os.environ.get("APP_PASSWORD_HASH") else None,
        "relevant_env_vars": relevant_env_vars,
        "all_env_var_names": all_env_var_names,
    }


@router.post("/login")
async def login(login_request: LoginRequest, response: Response):
    """
    Authenticate with the app password.
    
    Sets an httpOnly cookie with the session token.
    """
    # Check if auth is configured
    if not settings.APP_PASSWORD_HASH:
        raise HTTPException(
            status_code=503,
            detail="Authentication not configured. Set APP_PASSWORD_HASH environment variable."
        )
    
    # Verify password
    if not verify_password(login_request.password, settings.APP_PASSWORD_HASH):
        raise HTTPException(
            status_code=401,
            detail="Incorrect password"
        )
    
    # Create session token
    token = create_session_token()
    
    # Set cookie - use samesite="none" for cross-origin requests between Railway services
    expires = datetime.now(timezone.utc) + timedelta(days=settings.AUTH_SESSION_EXPIRE_DAYS)
    response.set_cookie(
        key="session",
        value=token,
        httponly=True,
        secure=True,  # Required for samesite="none"
        samesite="none",  # Allow cross-origin (frontend/backend on different domains)
        expires=expires.strftime("%a, %d %b %Y %H:%M:%S GMT"),
        path="/"
    )
    
    return {
        "success": True,
        "message": "Logged in successfully",
        "expires_at": expires.isoformat()
    }


@router.post("/logout")
async def logout(response: Response):
    """
    Log out by clearing the session cookie.
    """
    response.delete_cookie(
        key="session",
        httponly=True,
        secure=True,
        samesite="none",
        path="/"
    )
    return {"success": True, "message": "Logged out successfully"}


@router.get("/status", response_model=AuthStatus)
async def auth_status(request: Request):
    """
    Check if the current session is authenticated.
    """
    # If auth is not configured, always return authenticated
    if not settings.APP_PASSWORD_HASH:
        return AuthStatus(authenticated=True)
    
    token = request.cookies.get("session")
    if not token:
        return AuthStatus(authenticated=False)
    
    payload = verify_session_token(token)
    if not payload:
        return AuthStatus(authenticated=False)
    
    expires_at = datetime.fromtimestamp(payload["exp"], tz=timezone.utc)
    return AuthStatus(authenticated=True, expires_at=expires_at)


@router.get("/check")
async def auth_check(request: Request):
    """
    Quick authentication check - returns 200 if authenticated, 401 if not.
    Used by the frontend to validate session on page load.
    """
    # If auth is not configured, always allow
    if not settings.APP_PASSWORD_HASH:
        return {"authenticated": True, "auth_required": False}
    
    token = request.cookies.get("session")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    
    payload = verify_session_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired session")
    
    return {"authenticated": True, "auth_required": True}
