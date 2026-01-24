"""
Proaktiv Dokument Hub - FastAPI Backend

Main application entry point with database integration.
"""

import json
import logging
import os
from contextlib import asynccontextmanager

import sentry_sdk
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings

# Initialize Sentry for error tracking and performance monitoring
# Only enabled if SENTRY_DSN environment variable is set
if os.environ.get("SENTRY_DSN"):
    sentry_sdk.init(
        dsn=os.environ.get("SENTRY_DSN"),
        # Performance monitoring - capture 10% of transactions in production
        traces_sample_rate=1.0 if settings.DEBUG else 0.1,
        # Environment and release identification
        environment=os.environ.get("SENTRY_ENVIRONMENT", "production"),
        release=f"proaktiv-backend@{settings.APP_VERSION}",
        # Include user info for debugging (disable if privacy concerns)
        send_default_pii=False,
        # Enable profiling for performance analysis (5% of transactions)
        profiles_sample_rate=0.05,
    )
from app.database import close_db, init_db
from app.middleware.auth import AuthMiddleware

# V3 Routers
# Vitec Integration
from app.routers import (
    admin,
    analytics,
    assets,
    auth,
    categories,
    checklists,
    code_patterns,
    dashboard,
    employees,
    entra_sync,
    external_listings,
    health,
    layout_partials,
    merge_fields,
    offices,
    sanitizer,
    storage,
    sync,
    tags,
    templates,
    territories,
    vitec,
    web_crawl,
)

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL), format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
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
    "https://proaktiv-admin.up.railway.app",
    # Vercel URLs
    "https://proaktiv-dokument-hub.vercel.app",
]

# Merge allowed origins
all_origins = list(set(allowed_origins + default_origins))

app.add_middleware(
    CORSMiddleware,
    allow_origins=all_origins,
    allow_origin_regex=r"https://.*\.vercel\.app",  # All Vercel preview URLs
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
app.include_router(entra_sync.router, prefix="/api", tags=["Entra Sync"])


@app.get("/")
async def root():
    """Root endpoint."""
    return {"name": settings.APP_NAME, "version": settings.APP_VERSION, "status": "running", "docs": "/docs"}
