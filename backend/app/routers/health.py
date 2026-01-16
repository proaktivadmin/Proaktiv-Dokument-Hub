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


@router.get("/api/health/db-tables")
async def check_db_tables(db: AsyncSession = Depends(get_db)):
    """Check which tables exist in the database."""
    from app.config import settings
    import os
    
    result = {
        "database_url": settings.DATABASE_URL[:50] if settings.DATABASE_URL else "None",
        "is_sqlite": settings.DATABASE_URL.startswith("sqlite") if settings.DATABASE_URL else False,
        "tables": [],
        "cwd": os.getcwd(),
        "db_file_exists": None,
        "error": None
    }
    
    try:
        if result["is_sqlite"]:
            # Check if SQLite file exists
            db_path = settings.DATABASE_URL.replace("sqlite:///", "")
            result["db_path"] = db_path
            result["db_file_exists"] = os.path.exists(db_path)
            
            # Query SQLite for tables
            tables_result = await db.execute(text("SELECT name FROM sqlite_master WHERE type='table'"))
            result["tables"] = [row[0] for row in tables_result.fetchall()]
        else:
            # PostgreSQL
            tables_result = await db.execute(text("SELECT tablename FROM pg_tables WHERE schemaname = 'public'"))
            result["tables"] = [row[0] for row in tables_result.fetchall()]
    except Exception as e:
        result["error"] = str(e)
        import traceback
        result["traceback"] = traceback.format_exc()
    
    return result
# #endregion

