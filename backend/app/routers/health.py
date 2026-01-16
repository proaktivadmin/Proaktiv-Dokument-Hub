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
    
    return {
        "status": "healthy" if db_status == "connected" else "degraded",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "database": db_status,
            "storage": storage_status,
            "vitec_api": "not_configured",
            "redis": "not_configured"
        },
        "version": settings.APP_VERSION
    }


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


# #region agent log
@router.get("/api/health/debug-logs")
async def get_debug_logs():
    """Get debug logs for Azure deployment debugging."""
    import os
    log_path = "/app/.cursor/debug.log"
    logs = []
    try:
        if os.path.exists(log_path):
            with open(log_path, "r") as f:
                import json
                for line in f:
                    try:
                        logs.append(json.loads(line.strip()))
                    except:
                        logs.append({"raw": line.strip()})
        return {"logs": logs, "log_path": log_path, "exists": os.path.exists(log_path)}
    except Exception as e:
        return {"error": str(e), "log_path": log_path}
# #endregion

