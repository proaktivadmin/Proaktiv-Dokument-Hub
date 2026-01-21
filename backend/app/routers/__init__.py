# API Routers
# V3 Routers
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
    web_crawl,
)

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
    "sync",
]
