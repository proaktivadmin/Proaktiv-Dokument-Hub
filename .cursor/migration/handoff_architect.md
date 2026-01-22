# Handoff: Migration Architect → Backend Migrator

**Date:** 2026-01-16
**Status:** ✅ COMPLETE (Historical)
**Next Agent:** N/A - Migration complete

> **Note (2026-01-22):** This is a historical document from the Azure → Railway migration.
> Railway migration is complete. For current state, see `.planning/STATE.md`.

---

## What Was Done

1. Analyzed all Azure dependencies in the codebase
2. Found 31 files with Azure/blob references
3. Discovered that **key infrastructure already exists**:
   - Template model has `content` column
   - `TemplateContentService` exists
   - Cross-database type adapters work
4. Created full migration specification

---

## Key Discovery: Less Work Than Expected

The V2.7 bug fixes already added most of what we need:

| Component | Status | Notes |
|-----------|--------|-------|
| `Template.content` column | ✅ EXISTS | Already in model |
| `TemplateContentService` | ✅ EXISTS | Has save/versioning |
| Database type adapters | ✅ EXISTS | GUID, JSONType |
| Import endpoint | ❌ NEEDED | Create in admin.py |

---

## Files That Need Changes

### Backend (Your Tasks)

1. **`backend/app/config.py`**
   - Comment out `AZURE_STORAGE_*` variables
   - Add `PLATFORM: str = "railway"` for environment detection
   - Keep commented code for potential rollback

2. **`backend/app/routers/admin.py`** (CREATE NEW)
   - Add `POST /api/admin/import-templates` endpoint
   - Reads from `library/` folder
   - Populates `content` column for templates where it's NULL

3. **`backend/app/services/azure_storage_service.py`**
   - Add deprecation warning at top
   - Don't delete (needed for rollback)

4. **`backend/app/main.py`**
   - Include new admin router

5. **`backend/app/services/__init__.py`**
   - Keep azure_storage_service export (deprecated but compatible)

### Files to Leave Alone
- `backend/app/models/template.py` - Already has content column
- `backend/app/services/template_content_service.py` - Already complete
- `backend/app/routers/templates.py` - Already uses database content

---

## Import Endpoint Specification

Create `backend/app/routers/admin.py`:

```python
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pathlib import Path
import logging

from app.database import get_db
from app.models.template import Template

router = APIRouter(prefix="/api/admin", tags=["admin"])
logger = logging.getLogger(__name__)

@router.post("/import-templates")
async def import_templates_from_library(
    db: AsyncSession = Depends(get_db)
) -> dict:
    """
    One-time import: Read HTML files from library/ and store in database.
    Only imports templates where content is currently NULL.
    """
    library_path = Path("library")
    imported = 0
    skipped = 0
    errors = []
    
    # Get templates without content
    result = await db.execute(
        select(Template).where(Template.content.is_(None))
    )
    templates = result.scalars().all()
    
    for template in templates:
        try:
            # Try to find matching file
            file_path = find_template_file(library_path, template.file_name)
            if file_path and file_path.exists():
                template.content = file_path.read_text(encoding='utf-8')
                imported += 1
                logger.info(f"Imported: {template.file_name}")
            else:
                skipped += 1
                logger.warning(f"File not found: {template.file_name}")
        except Exception as e:
            errors.append(f"{template.file_name}: {str(e)}")
    
    await db.commit()
    
    return {
        "imported": imported,
        "skipped": skipped,
        "errors": errors,
        "total_templates": len(templates)
    }

def find_template_file(library_path: Path, file_name: str) -> Path | None:
    """Find template file, searching subdirectories."""
    # Direct match
    direct = library_path / file_name
    if direct.exists():
        return direct
    
    # Search subdirectories
    for path in library_path.rglob(file_name):
        return path
    
    # Try with .html extension
    if not file_name.endswith('.html'):
        return find_template_file(library_path, f"{file_name}.html")
    
    return None
```

---

## Environment Variables for Railway

When you test locally, these will be used:

```bash
# Already in docker-compose.yml
DATABASE_URL=postgresql://postgres:postgres@db:5432/dokument_hub

# Add to .env for testing
PLATFORM=railway
```

---

## Testing Checklist

Before handing off to Frontend Migrator:

1. [ ] Run `docker compose up -d`
2. [ ] Run migrations: `docker compose exec backend alembic upgrade head`
3. [ ] Test health: `curl http://localhost:8000/api/health`
4. [ ] Test import: `curl -X POST http://localhost:8000/api/admin/import-templates`
5. [ ] Verify templates have content: `curl http://localhost:8000/api/templates | jq '.[0].content | length'`

---

## Blockers or Concerns

### None Critical

The migration is straightforward because:
1. Content column already exists
2. TemplateContentService already works
3. We're just removing Azure, not adding new functionality

### Minor Concern: Azure Blob URLs
- `azure_blob_url` column is NOT NULL in schema
- Templates created during migration need a placeholder value
- Suggest: Use `"database://content"` as placeholder for new templates

---

## What NOT to Do

1. ❌ Don't delete `azure_storage_service.py` - needed for rollback
2. ❌ Don't remove `azure_blob_url` column - historical reference
3. ❌ Don't modify template_content_service.py - already complete
4. ❌ Don't change database models - content column exists

---

## Next Agent Should

1. Create `backend/app/routers/admin.py` with import endpoint
2. Update `backend/app/main.py` to include admin router
3. Comment out Azure config in `config.py`
4. Add deprecation warning to `azure_storage_service.py`
5. Test locally with docker compose
6. Write handoff for Frontend Migrator

---

## Quick Reference

```bash
# Switch to migration branch (if not already)
git checkout migration/vercel-railway

# Sync latest from V2-development first
git merge V2-development

# Start local dev
docker compose up -d

# Run backend migrator agent
/migration-backend
```
