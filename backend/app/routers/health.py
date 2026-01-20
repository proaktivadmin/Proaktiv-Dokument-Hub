"""
Health Check Endpoints
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text
from datetime import datetime

from app.config import settings
from app.database import get_db
from app.services.azure_storage_service import get_azure_storage_service
from app.services.vitec_hub_service import VitecHubService

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
    
    # Check Azure Storage
    storage_service = get_azure_storage_service()
    storage_status = "configured" if storage_service.is_configured else "not_configured"
    
    # Check Vitec Hub API configuration
    vitec_hub = VitecHubService()
    vitec_status = "configured" if vitec_hub.is_configured else "not_configured"
    
    return {
        "status": "healthy" if db_status == "connected" else "degraded",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "database": db_status,
            "storage": storage_status,
            "vitec_api": vitec_status,
            "redis": "not_configured"
        },
        "version": settings.APP_VERSION
    }


@router.get("/api/ping")
async def ping():
    """Lightweight ping endpoint for uptime checks."""
    return {"status": "ok", "timestamp": datetime.utcnow().isoformat()}


@router.get("/api/health/azure-storage")
async def azure_storage_check():
    """
    Detailed Azure Storage connection test.
    Returns connection status, account info, and available containers.
    """
    storage_service = get_azure_storage_service()
    result = await storage_service.test_connection()
    
    return {
        "timestamp": datetime.utcnow().isoformat(),
        **result
    }


@router.get("/api/health/ready")
async def readiness_check():
    """Kubernetes readiness probe."""
    return {"status": "ready"}


@router.get("/api/health/live")
async def liveness_check():
    """Kubernetes liveness probe."""
    return {"status": "alive"}

