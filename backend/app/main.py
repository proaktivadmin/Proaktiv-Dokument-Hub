"""
Proaktiv Dokument Hub - FastAPI Backend

Main application entry point with database integration.

Build: 2026-01-16-v2 - Force container restart
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.config import settings
from app.database import init_db, close_db
from app.routers import templates, tags, categories, analytics, health, sanitizer
from app.routers import merge_fields, code_patterns, layout_partials, dashboard, admin

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events."""
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    try:
        await init_db()
    except Exception as e:
        logger.warning(f"Database init check failed: {e}")
    yield
    await close_db()
    logger.info("Shutting down application")


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Centralized Master Template Library API",
    lifespan=lifespan,
)

# CORS Configuration
# Parse allowed origins from environment or use defaults
import json
try:
    allowed_origins = json.loads(settings.ALLOWED_ORIGINS)
except (json.JSONDecodeError, TypeError):
    allowed_origins = ["http://localhost:3000"]

# Add common development and deployment origins
default_origins = [
    "http://localhost:3000",
    "http://localhost:3001",
    "http://frontend:3000",
    "https://dokumenthub.proaktiv.no",
    # Azure Container Apps URLs (legacy)
    "https://dokumenthub-web.greenmushroom-2067e5c8.norwayeast.azurecontainerapps.io",
    "https://dokumenthub-api.greenmushroom-2067e5c8.norwayeast.azurecontainerapps.io",
]

# Merge allowed origins
all_origins = list(set(allowed_origins + default_origins))

app.add_middleware(
    CORSMiddleware,
    allow_origins=all_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health.router)
app.include_router(templates.router, prefix="/api/templates", tags=["Templates"])
app.include_router(tags.router, prefix="/api/tags", tags=["Tags"])
app.include_router(categories.router, prefix="/api/categories", tags=["Categories"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"])
app.include_router(sanitizer.router, tags=["Sanitizer"])

# V2 Routers
app.include_router(merge_fields.router, prefix="/api", tags=["Merge Fields"])
app.include_router(code_patterns.router, prefix="/api", tags=["Code Patterns"])
app.include_router(layout_partials.router, prefix="/api", tags=["Layout Partials"])
app.include_router(dashboard.router, prefix="/api", tags=["Dashboard"])
app.include_router(admin.router, tags=["Admin"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs"
    }
