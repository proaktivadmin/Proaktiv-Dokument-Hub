"""
Proaktiv Dokument Hub - FastAPI Backend

Main application entry point with database integration.
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.config import settings
from app.database import init_db, close_db
from app.middleware.auth import AuthMiddleware
from app.routers import templates, tags, categories, analytics, health, sanitizer
from app.routers import merge_fields, code_patterns, layout_partials, dashboard, admin, storage
from app.routers import auth
# V3 Routers
from app.routers import offices, employees, assets, external_listings, checklists, territories, web_crawl, sync
# Vitec Integration
from app.routers import vitec

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
    # Railway URLs
    "https://blissful-quietude-production.up.railway.app",
    "https://proaktiv-dokument-hub-production.up.railway.app",
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

# Auth middleware (only active if APP_PASSWORD_HASH is set)
app.add_middleware(AuthMiddleware)

# Include routers
app.include_router(auth.router, prefix="/api", tags=["Auth"])
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
app.include_router(storage.router, tags=["Storage"])

# V3 Routers - Office & Employee Hub
app.include_router(offices.router, prefix="/api", tags=["Offices"])
app.include_router(employees.router, prefix="/api", tags=["Employees"])
app.include_router(assets.router, prefix="/api", tags=["Assets"])
app.include_router(external_listings.router, prefix="/api", tags=["External Listings"])
app.include_router(checklists.router, prefix="/api", tags=["Checklists"])
app.include_router(territories.router, prefix="/api", tags=["Territories"])
app.include_router(web_crawl.router, prefix="/api", tags=["Web Crawl"])
app.include_router(vitec.router, prefix="/api", tags=["Vitec"])
app.include_router(sync.router, prefix="/api", tags=["Sync"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs"
    }
