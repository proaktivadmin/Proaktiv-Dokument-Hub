# Azure DevOps Specification

**Project:** Proaktiv Dokument Hub V2.6  
**Created:** 2026-01-15  
**Agent:** Azure DevOps Architect  
**Status:** Ready for Review

---

## Table of Contents

1. [Executive Summary](#1-executive-summary)
2. [Root Cause Analysis](#2-root-cause-analysis)
3. [Database Strategy Decision](#3-database-strategy-decision)
4. [Missing API Endpoints](#4-missing-api-endpoints)
5. [Infrastructure Fixes](#5-infrastructure-fixes)
6. [Container Startup Script](#6-container-startup-script)
7. [Verification Checklist](#7-verification-checklist)
8. [Implementation Order](#8-implementation-order)

---

## 1. Executive Summary

### Current State

The Proaktiv Dokument Hub is deployed to Azure Container Apps with the following status:

| Component | Status | Issue |
|-----------|--------|-------|
| Frontend Container | ✅ Running | Works correctly |
| Backend Container | ⚠️ Partial | Missing endpoints, ephemeral DB |
| Azure Blob Storage | ✅ Working | 43 templates stored |
| Database | ❌ Ephemeral | Data lost on restart |
| CI/CD Pipeline | ✅ Working | Builds and deploys |

### Key Issues to Fix

1. **Missing `/api/dashboard/stats` endpoint** - Frontend calls `/api/analytics/dashboard` but displays a 500 error due to empty database
2. **Ephemeral SQLite database** - All data lost when container restarts
3. **No automatic database initialization** - Tables created but no seed data
4. **Migration job runs AFTER deploy** - But `az containerapp exec` doesn't work reliably

### Recommendation

**Keep SQLite** but add automatic seeding on startup. The database schema and templates are already working. We just need to ensure tables are created and seeded automatically.

---

## 2. Root Cause Analysis

### Issue 1: Dashboard 500 Error

**Symptom:** Frontend shows "Request failed with status code 500" on the dashboard.

**Frontend Expectation:**
```typescript
// frontend/src/lib/api.ts line 65
const { data } = await api.get<DashboardStats>("/analytics/dashboard");
```

**Backend Implementation:**
```python
# backend/app/routers/analytics.py line 20
@router.get("/dashboard")
async def get_dashboard_stats(db: AsyncSession = Depends(get_db)):
```

**Actual API Path:** `/api/analytics/dashboard` ✅ (Router is registered with prefix `/api/analytics`)

**Root Cause:** The endpoint EXISTS but returns 500 because the `AuditLog` table query fails:
```python
downloads_query = (
    select(func.count(AuditLog.id))
    .where(AuditLog.action == "downloaded")
    .where(AuditLog.timestamp >= thirty_days_ago)
)
```

The `AuditLog` model may not have the table created, or the query fails on an empty/non-existent table.

**Evidence:** 
- API docs at `/docs` shows the endpoint exists
- `/api/health` returns healthy
- Dashboard request returns 500 (internal server error, not 404)

### Issue 2: Ephemeral Database

**Current Config (main.bicep line 124-125):**
```bicep
name: 'DATABASE_URL'
value: 'sqlite:///./app.db'
```

**Problem:** SQLite file stored in container filesystem at `/app/app.db`. Container filesystem is ephemeral - data is lost when:
- Container restarts
- New deployment occurs
- Container scales (though we use 1 replica)

**Current Mitigation (database.py lines 149-161):**
```python
# For SQLite (ephemeral), automatically create all tables on startup
if is_sqlite(settings.DATABASE_URL):
    logger.info("SQLite detected - creating tables if they don't exist...")
    async with async_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
```

This creates tables, but does NOT seed data. Templates show because they're fetched from Azure Blob Storage (which IS persistent).

### Issue 3: No Seed Data on Startup

**Current Dockerfile (line 44):**
```dockerfile
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Problem:** Starts uvicorn directly without:
1. Running database migrations
2. Seeding initial categories, tags, merge fields
3. The existing `start.sh` waits for PostgreSQL but is NOT used

**Impact:**
- Categories list is empty → Dashboard shows no categories
- Tags list is empty → Templates can't have tags
- Merge fields empty → Flettekoder page shows no data from DB (but 142 fields shown from discovery)

### Issue 4: Previous Volume Mount Failure

**Historical Error:**
```
MountVolume.Setup failed for volume "database-volume": mount failed: exit status 32
```

**Root Cause:** Azure Files storage must be linked to Container Apps Environment BEFORE mounting. The Bicep template didn't define the storage link.

**Current State:** Volume mount was removed to get containers running. This is acceptable for a single-user app if we seed data on startup.

---

## 3. Database Strategy Decision

### Option Analysis

| Option | Pros | Cons | Cost | Recommendation |
|--------|------|------|------|----------------|
| **A. SQLite + Auto-Seed** | Simple, no infra changes, fast | Data loss on restart | $0 | ✅ **RECOMMENDED** |
| B. SQLite + Azure Files | Persistent, no code changes | Volume mount complexity, slow I/O | ~$5/mo | Not worth complexity |
| C. Azure PostgreSQL | Fully managed, reliable | Cost, requires connection string changes | ~$15/mo | Overkill for single user |
| D. SQLite + Blob Backup | Creative, mostly persistent | Complex, possible data loss window | ~$1/mo | Over-engineered |

### Decision: Option A - SQLite with Auto-Seeding

**Rationale:**
1. This is a **single-user internal tool** - reliability requirements are moderate
2. Templates are stored in **Azure Blob Storage** which IS persistent
3. The only DB data that matters is:
   - Categories (static, can be seeded)
   - Tags (static, can be seeded)
   - Merge fields (static, can be seeded)
   - Template metadata (synced from blob storage)
   - Audit logs (nice-to-have, not critical)
4. Cost is zero
5. Minimal code changes required

**Trade-off Accepted:** Audit log history is lost on restart. This is acceptable for an internal tool.

---

## 4. Missing API Endpoints

### Endpoint Status Matrix

| Endpoint | Frontend Expects | Backend Status | Fix Required |
|----------|-----------------|----------------|--------------|
| `/api/analytics/dashboard` | ✅ Called | ✅ Exists | Fix query error |
| `/api/categories` | ✅ Called | ✅ Exists | Seed data |
| `/api/templates` | ✅ Called | ✅ Works | None |
| `/api/templates/{id}/content` | ✅ Called | ✅ Works | None |
| `/api/templates/{id}/download` | ✅ Called | ✅ Works | None |
| `/api/health` | ✅ Called | ✅ Works | None |
| `/api/merge-fields` | ✅ Called | ✅ Exists | Seed data |

### Fix Required: analytics.py

The dashboard endpoint needs to handle empty/non-existent audit logs gracefully:

```python
# Current code fails if AuditLog table is empty or missing
downloads_query = (
    select(func.count(AuditLog.id))
    .where(AuditLog.action == "downloaded")
    .where(AuditLog.timestamp >= thirty_days_ago)
)
downloads = await db.scalar(downloads_query) or 0  # Already handles None
```

The issue is likely that the `AuditLog` model isn't being imported in `database.py:init_db()`. Let me check:

```python
# backend/app/database.py line 147
from app.models import template, category, tag  # noqa: F401
# MISSING: audit_log import!
```

**Root Cause Confirmed:** `AuditLog` table is NOT created because the model isn't imported during `Base.metadata.create_all()`.

---

## 5. Infrastructure Fixes

### 5.1 Bicep Template Updates

The current `main.bicep` is mostly correct. Only minor improvements needed:

```bicep
// Add startup command that runs seeding
env: [
  // ... existing env vars ...
  {
    name: 'RUN_SEED'
    value: 'true'  // Flag to trigger seeding on startup
  }
]
```

**Full Updated main.bicep:** No changes required - the Bicep is fine.

### 5.2 Backend Dockerfile Update

Update `backend/Dockerfile` to use the startup script:

```dockerfile
# Current (line 44):
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

# New:
CMD ["./scripts/start-prod.sh"]
```

### 5.3 New Startup Script for Production

Create `backend/scripts/start-prod.sh`:

```bash
#!/bin/bash
set -e

echo "🚀 Starting Proaktiv Dokument Hub Backend..."

# Skip PostgreSQL wait in SQLite mode
if [[ "$DATABASE_URL" == sqlite* ]]; then
    echo "📦 SQLite mode detected"
else
    echo "⏳ Waiting for database..."
    while ! nc -z ${DB_HOST:-db} ${DB_PORT:-5432}; do
        sleep 1
    done
    echo "✅ Database is ready!"
fi

# Initialize database (creates tables for SQLite)
echo "📦 Initializing database..."
cd /app
python -c "
import asyncio
from app.database import init_db
asyncio.run(init_db())
print('✅ Database initialized!')
"

# Seed data if RUN_SEED is true or database is empty
echo "🌱 Checking if seeding is needed..."
python -c "
import asyncio
import sys
sys.path.insert(0, '/app')

async def check_and_seed():
    from app.database import async_session_factory
    from sqlalchemy import select, func
    from app.models.category import Category
    
    async with async_session_factory() as db:
        count = await db.scalar(select(func.count(Category.id)))
        if count == 0:
            print('Database is empty, seeding...')
            # Import and run seed functions
            from scripts.seed_data import seed_tags, seed_categories
            await seed_tags(db)
            await seed_categories(db)
            await db.commit()
            print('✅ Seed data created!')
        else:
            print(f'✅ Database already has {count} categories, skipping seed.')

asyncio.run(check_and_seed())
"

# Start the application
echo "🌐 Starting FastAPI server..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 "$@"
```

---

## 6. Container Startup Script

### Final Startup Sequence

```
┌─────────────────────────────────────────────────────────────┐
│                  CONTAINER STARTUP                          │
├─────────────────────────────────────────────────────────────┤
│  1. Check database type (SQLite vs PostgreSQL)              │
│     - If PostgreSQL: Wait for connection                    │
│     - If SQLite: Skip wait                                  │
├─────────────────────────────────────────────────────────────┤
│  2. Initialize database                                     │
│     - For SQLite: Create tables via Base.metadata.create_all│
│     - For PostgreSQL: Tables should exist from migrations   │
├─────────────────────────────────────────────────────────────┤
│  3. Check if database is empty                              │
│     - Count categories                                      │
│     - If 0: Run seed scripts                                │
│     - If >0: Skip seeding                                   │
├─────────────────────────────────────────────────────────────┤
│  4. Start FastAPI (uvicorn)                                 │
│     - Host: 0.0.0.0                                         │
│     - Port: 8000                                            │
└─────────────────────────────────────────────────────────────┘
```

---

## 7. Verification Checklist

After implementing fixes, verify each item:

### Pre-Deployment Checks

- [ ] `backend/scripts/start-prod.sh` exists and is executable
- [ ] `backend/Dockerfile` uses `start-prod.sh` as CMD
- [ ] `backend/app/database.py` imports `audit_log` model
- [ ] All models are registered with SQLAlchemy Base
- [ ] Seed data scripts work locally

### Post-Deployment Checks

- [ ] **Backend Health:** `curl https://dokumenthub-api.../api/health` returns `{"status": "healthy"}`
- [ ] **Database Status:** Health check shows `"database": "connected"`
- [ ] **Storage Status:** Health check shows `"storage": "configured"`
- [ ] **Dashboard API:** `curl https://dokumenthub-api.../api/analytics/dashboard` returns JSON (not 500)
- [ ] **Categories API:** `curl https://dokumenthub-api.../api/categories` returns categories list
- [ ] **Templates API:** `curl https://dokumenthub-api.../api/templates` returns 43 templates
- [ ] **Frontend Loads:** No error banner on dashboard
- [ ] **Template Preview:** Click any template → preview renders correctly
- [ ] **Flettekoder Page:** Shows merge fields
- [ ] **API Docs:** `https://dokumenthub-api.../docs` loads Swagger UI

### Persistence Test (Optional)

Since we chose SQLite (ephemeral), this will fail by design:
- [ ] Restart container → Data should be re-seeded automatically
- [ ] Verify templates still load (they come from blob storage)

---

## 8. Implementation Order

### Step 1: Fix Model Imports (5 mins)

Edit `backend/app/database.py`:

```python
# Line 147: Add audit_log import
from app.models import template, category, tag, audit_log  # noqa: F401
```

Also ensure all V2 models are imported:
```python
from app.models import (
    template,
    category,
    tag,
    audit_log,
    merge_field,     # V2
    code_pattern,    # V2
    layout_partial,  # V2
)
```

### Step 2: Create Production Startup Script (10 mins)

Create `backend/scripts/start-prod.sh` with the content from Section 5.3.

Make it executable:
```bash
chmod +x backend/scripts/start-prod.sh
```

### Step 3: Update Dockerfile (2 mins)

Edit `backend/Dockerfile` line 44:

```dockerfile
# From:
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

# To:
CMD ["./scripts/start-prod.sh"]
```

### Step 4: Test Locally (10 mins)

```bash
# Build and run backend container
docker compose build backend
docker compose up -d backend

# Check logs
docker compose logs -f backend

# Test endpoints
curl http://localhost:8000/api/health
curl http://localhost:8000/api/analytics/dashboard
curl http://localhost:8000/api/categories
```

### Step 5: Deploy to Azure (5 mins)

```bash
git add .
git commit -m "fix(azure): auto-seed database and fix model imports

- Add production startup script with auto-seeding
- Import all models in database.py for table creation
- Switch Dockerfile to use start-prod.sh
- Seed categories, tags on empty database

Fixes dashboard 500 error and empty categories."

git push origin V2-development
```

### Step 6: Verify Deployment (5 mins)

Run the verification checklist from Section 7.

---

## 9. Files to Modify

| File | Action | Changes |
|------|--------|---------|
| `backend/app/database.py` | Edit | Add missing model imports (lines 147-148) |
| `backend/scripts/start-prod.sh` | Create | Production startup script with seeding |
| `backend/Dockerfile` | Edit | Change CMD to use start-prod.sh |

### No Changes Required

- `infrastructure/bicep/main.bicep` - Already correct
- `.github/workflows/deploy-azure.yml` - Already correct (can remove migrate job)
- `frontend/*` - No changes needed

---

## 10. Risk Assessment

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| Seeding script fails | Low | Medium | Test locally first |
| Tables not created | Low | High | Database already creates tables on init |
| AuditLog query still fails | Low | Low | Already handles empty result |
| Container won't start | Low | High | Fallback: revert CMD change |

---

## 11. Rollback Plan

If deployment fails:

1. **Revert Dockerfile CMD:**
   ```dockerfile
   CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
   ```

2. **Push revert:**
   ```bash
   git revert HEAD
   git push origin V2-development
   ```

3. **Container will restart with old configuration**

---

## Approval Required

Please review this specification and confirm:

1. ✅ **Database Strategy:** SQLite with auto-seeding is acceptable
2. ✅ **Trade-off:** Audit log history loss on restart is acceptable
3. ✅ **Implementation Order:** The 6-step plan is approved

Once approved, proceed with `/builder` to implement these changes, or I can implement them now.

---

## Next Steps

After implementing these Azure fixes:

1. **Run `/architect`** - Review backend specifications for any additional endpoints
2. **Run `/frontend-architect`** - Verify frontend is complete
3. **Run `/builder`** - Implement any remaining features

The Azure infrastructure is fundamentally sound. These are minor fixes to ensure a complete startup sequence.
