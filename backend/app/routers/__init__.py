# API Routers
from app.routers import templates, tags, categories, analytics, health, sanitizer
from app.routers import merge_fields, code_patterns, layout_partials
from app.routers import dashboard, admin, storage, auth
# V3 Routers
from app.routers import offices, employees, assets, external_listings, checklists, territories
from app.routers import web_crawl

__all__ = [
    # Core
    "templates",
    "tags",
    "categories",
    "analytics",
    "health",
    "sanitizer",
    # V2
    "merge_fields",
    "code_patterns",
    "layout_partials",
    "dashboard",
    "admin",
    "storage",
    "auth",
    # V3
    "offices",
    "employees",
    "assets",
    "external_listings",
    "checklists",
    "territories",
    "web_crawl",
]
