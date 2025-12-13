"""
Health Check Endpoints
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from datetime import datetime

from app.config import settings
from app.database import get_db

router = APIRouter()


@router.get("/api/health")
async def health_check(db: AsyncSession = Depends(get_db)):
    """
    Health check endpoint.
    Returns status of the application and connected services.
    """
    # Check database
    db_status = "connected"
    try:
        await db.execute(text("SELECT 1"))
    except Exception:
        db_status = "disconnected"
    
    return {
        "status": "healthy" if db_status == "connected" else "degraded",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "database": db_status,
            "storage": "mock" if not settings.AZURE_STORAGE_CONNECTION_STRING else "connected",
            "vitec_api": "not_configured",
            "redis": "not_configured"
        },
        "version": settings.APP_VERSION
    }


@router.get("/api/health/ready")
async def readiness_check():
    """Kubernetes readiness probe."""
    return {"status": "ready"}


@router.get("/api/health/live")
async def liveness_check():
    """Kubernetes liveness probe."""
    return {"status": "alive"}

