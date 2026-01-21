"""
Authentication Router

Simple password-based authentication for single-user access.
"""

from datetime import UTC, datetime, timedelta

import bcrypt
from fastapi import APIRouter, HTTPException, Request, Response
from jose import JWTError, jwt
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
    expires_at: datetime | None = None


def create_session_token(expires_delta: timedelta | None = None) -> str:
    """Create a JWT session token."""
    if expires_delta is None:
        expires_delta = timedelta(days=settings.AUTH_SESSION_EXPIRE_DAYS)

    expire = datetime.now(UTC) + expires_delta
    to_encode = {"exp": expire, "iat": datetime.now(UTC), "type": "session"}
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)


def verify_session_token(token: str) -> dict | None:
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
        return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))
    except Exception:
        return False


@router.post("/login")
async def login(login_request: LoginRequest, response: Response):
    """
    Authenticate with the app password.

    Sets an httpOnly cookie with the session token.
    """
    # Check if auth is configured
    if not settings.APP_PASSWORD_HASH:
        raise HTTPException(
            status_code=503, detail="Authentication not configured. Set APP_PASSWORD_HASH environment variable."
        )

    # Verify password
    if not verify_password(login_request.password, settings.APP_PASSWORD_HASH):
        raise HTTPException(status_code=401, detail="Incorrect password")

    # Create session token
    token = create_session_token()

    # Set cookie - use samesite="none" for cross-origin requests between Railway services
    expires = datetime.now(UTC) + timedelta(days=settings.AUTH_SESSION_EXPIRE_DAYS)
    response.set_cookie(
        key="session",
        value=token,
        httponly=True,
        secure=True,  # Required for samesite="none"
        samesite="none",  # Allow cross-origin (frontend/backend on different domains)
        expires=expires.strftime("%a, %d %b %Y %H:%M:%S GMT"),
        path="/",
    )

    return {"success": True, "message": "Logged in successfully", "expires_at": expires.isoformat()}


@router.post("/logout")
async def logout(response: Response):
    """
    Log out by clearing the session cookie.
    """
    response.delete_cookie(key="session", httponly=True, secure=True, samesite="none", path="/")
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

    expires_at = datetime.fromtimestamp(payload["exp"], tz=UTC)
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
