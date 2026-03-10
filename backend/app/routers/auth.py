"""
Authentication Router

Multi-user password-based authentication.
Users are defined in APP_USERS_JSON (preferred) or the legacy APP_PASSWORD_HASH.
"""

import json
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


def get_auth_cookie_settings() -> dict[str, str | bool]:
    """Return cookie settings for local vs production environments."""
    env = (settings.APP_ENV or "").lower()
    is_dev = env in ("development", "dev", "local") or settings.DEBUG
    if is_dev:
        return {"secure": False, "samesite": "lax"}
    return {"secure": True, "samesite": "none"}


def get_users() -> list[dict] | None:
    """
    Return the configured user list, or None if auth is disabled.

    Priority: APP_USERS_JSON > APP_PASSWORD_HASH (legacy).
    Returns None when neither is configured (auth disabled).
    """
    if settings.APP_USERS_JSON:
        try:
            users = json.loads(settings.APP_USERS_JSON)
            if isinstance(users, list):
                return users
        except (json.JSONDecodeError, ValueError):
            return None
    if settings.APP_PASSWORD_HASH:
        # Legacy single-user mode — email not required for login
        return [{"email": None, "password_hash": settings.APP_PASSWORD_HASH}]
    return None


def is_auth_enabled() -> bool:
    """Return True when authentication is configured."""
    return get_users() is not None


class LoginRequest(BaseModel):
    email: str
    password: str


class AuthStatus(BaseModel):
    authenticated: bool
    email: str | None = None
    expires_at: datetime | None = None


def create_session_token(email: str | None = None, expires_delta: timedelta | None = None) -> str:
    """Create a JWT session token, optionally embedding the user's email."""
    if expires_delta is None:
        expires_delta = timedelta(days=settings.AUTH_SESSION_EXPIRE_DAYS)

    expire = datetime.now(UTC) + expires_delta
    to_encode: dict = {"exp": expire, "iat": datetime.now(UTC), "type": "session"}
    if email:
        to_encode["sub"] = email
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=ALGORITHM)


def verify_session_token(token: str) -> dict | None:
    """Verify a JWT session token. Returns the payload or None."""
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


def find_user(email: str, password: str) -> dict | None:
    """
    Look up a user by email and verify their password.
    Returns the user dict on success, None on failure.
    """
    users = get_users()
    if not users:
        return None

    for user in users:
        user_email = user.get("email")
        # Legacy mode: single user with no email requirement
        if user_email is None:
            if verify_password(password, user.get("password_hash", "")):
                return user
        elif user_email.lower() == email.lower():
            if verify_password(password, user.get("password_hash", "")):
                return user
    return None


@router.post("/login")
async def login(login_request: LoginRequest, response: Response):
    """
    Authenticate with email + password.
    Sets an httpOnly cookie with the session token.
    """
    if not is_auth_enabled():
        raise HTTPException(
            status_code=503,
            detail="Authentication not configured. Set APP_USERS_JSON environment variable.",
        )

    user = find_user(login_request.email, login_request.password)
    if not user:
        raise HTTPException(status_code=401, detail="Feil e-post eller passord")

    email = user.get("email")
    token = create_session_token(email=email)

    expires = datetime.now(UTC) + timedelta(days=settings.AUTH_SESSION_EXPIRE_DAYS)
    cookie_settings = get_auth_cookie_settings()
    response.set_cookie(
        key="session",
        value=token,
        httponly=True,
        secure=cookie_settings["secure"],
        samesite=cookie_settings["samesite"],
        expires=expires.strftime("%a, %d %b %Y %H:%M:%S GMT"),
        path="/",
    )

    return {"success": True, "message": "Logged in successfully", "expires_at": expires.isoformat()}


@router.post("/logout")
async def logout(response: Response):
    """Log out by clearing the session cookie."""
    cookie_settings = get_auth_cookie_settings()
    response.delete_cookie(
        key="session",
        httponly=True,
        secure=cookie_settings["secure"],
        samesite=cookie_settings["samesite"],
        path="/",
    )
    return {"success": True, "message": "Logged out successfully"}


@router.get("/status", response_model=AuthStatus)
async def auth_status(request: Request):
    """Check if the current session is authenticated."""
    if not is_auth_enabled():
        return AuthStatus(authenticated=True)

    token = request.cookies.get("session")
    if not token:
        return AuthStatus(authenticated=False)

    payload = verify_session_token(token)
    if not payload:
        return AuthStatus(authenticated=False)

    expires_at = datetime.fromtimestamp(payload["exp"], tz=UTC)
    email = payload.get("sub")
    return AuthStatus(authenticated=True, email=email, expires_at=expires_at)


@router.get("/check")
async def auth_check(request: Request):
    """
    Quick authentication check — returns 200 if authenticated, 401 if not.
    Used by the frontend to validate session on page load.
    """
    if not is_auth_enabled():
        return {"authenticated": True, "auth_required": False}

    token = request.cookies.get("session")
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")

    payload = verify_session_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid or expired session")

    return {"authenticated": True, "auth_required": True, "email": payload.get("sub")}
