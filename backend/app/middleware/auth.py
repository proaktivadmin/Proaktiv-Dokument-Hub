"""
Authentication Middleware

Protects API routes by requiring a valid session token.
"""

from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse

from app.config import get_settings
from app.routers.auth import verify_session_token


# Routes that don't require authentication
PUBLIC_ROUTES = [
    "/api/auth/login",
    "/api/auth/logout",
    "/api/auth/status",
    "/api/auth/check",
    "/api/health",
    "/health",
    "/docs",
    "/redoc",
    "/openapi.json",
    "/",
    # Sanitizer endpoints - stateless HTML transformation, no sensitive data
    "/api/sanitize/preview",
    "/api/sanitize/validate",
    "/api/sanitize/strip-styles",
]

# CORS headers to add to 401 responses
CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",  # Will be overridden by main CORS for valid requests
    "Access-Control-Allow-Credentials": "true",
    "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS, PATCH",
    "Access-Control-Allow-Headers": "Content-Type, Authorization, Cookie",
}


class AuthMiddleware(BaseHTTPMiddleware):
    """
    Middleware that checks for valid session token on protected routes.
    
    - Allows public routes without authentication
    - If APP_PASSWORD_HASH is not set, allows all requests (auth disabled)
    - Protected routes require a valid session cookie
    - Allows OPTIONS requests for CORS preflight
    """
    
    async def dispatch(self, request: Request, call_next):
        settings = get_settings()
        
        # Always allow OPTIONS requests (CORS preflight)
        if request.method == "OPTIONS":
            return await call_next(request)
        
        # If auth is not configured, allow all requests
        if not settings.APP_PASSWORD_HASH:
            return await call_next(request)
        
        # Check if this is a public route
        path = request.url.path
        
        # Allow public routes
        for public_route in PUBLIC_ROUTES:
            if path == public_route or path.startswith(public_route + "/"):
                return await call_next(request)
        
        # Allow non-API routes (static files, etc.)
        if not path.startswith("/api"):
            return await call_next(request)
        
        # Get origin for CORS headers
        origin = request.headers.get("origin", "*")
        cors_headers = {
            "Access-Control-Allow-Origin": origin,
            "Access-Control-Allow-Credentials": "true",
        }
        
        # Check for session token
        token = request.cookies.get("session")
        if not token:
            return JSONResponse(
                status_code=401,
                content={"detail": "Not authenticated"},
                headers=cors_headers
            )
        
        # Verify token
        payload = verify_session_token(token)
        if not payload:
            return JSONResponse(
                status_code=401,
                content={"detail": "Invalid or expired session"},
                headers=cors_headers
            )
        
        # Token is valid, continue
        return await call_next(request)
