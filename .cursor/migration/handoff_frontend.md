# Handoff: Frontend Migrator → Deployment Agent

**Date:** 2026-01-16
**Status:** Complete
**Next Agent:** `/migration-deploy`

---

## What Was Done

### 1. Updated next.config.js
**File:** `frontend/next.config.js`

- Removed Azure Blob Storage image patterns (`*.blob.core.windows.net`)
- Added comment explaining template content is now in database
- Kept API rewrites for Railway backend

### 2. Simplified API Config
**File:** `frontend/src/lib/api/config.ts`

- Updated comments to reflect Vercel + Railway as primary deployment
- Kept Azure Container Apps detection as legacy fallback
- No functional changes needed (relative URLs work for both)

---

## Files Changed

| File | Change |
|------|--------|
| `frontend/next.config.js` | Removed `images.remotePatterns` block |
| `frontend/src/lib/api/config.ts` | Updated comments, kept Azure as legacy |

---

## Azure References Status

### Removed
- `images.remotePatterns` with `*.blob.core.windows.net`

### Kept (Legacy Support)
- Azure Container Apps hostname detection in `config.ts`
- This allows the Azure deployment to continue working during transition

---

## No Other Azure References Found

Searched `frontend/src/` for:
- `azure` (case-insensitive)
- `blob.core.windows`

Only references are in `config.ts` as legacy fallback.

---

## Environment Variables for Vercel

| Variable | Value | Notes |
|----------|-------|-------|
| `BACKEND_URL` | Railway backend URL | Required for API rewrites |

Example:
```
BACKEND_URL=https://dokumenthub-production.up.railway.app
```

---

## Local Testing Results

The frontend continues to work with:
- `npm run dev` on localhost:3000
- Backend on localhost:8000 (via docker compose)
- Next.js rewrites proxy API calls correctly

Testing checklist:
- [x] Dashboard loads
- [x] Template list displays
- [x] Template preview works
- [x] Code editor loads content
- [x] Save functionality works
- [x] No console errors
- [x] No Azure-related network requests

---

## Build Verification

```bash
cd frontend
npm run build
```

Expected: Build succeeds with no errors.

---

## Next Agent Should

### 1. Create Railway Project
1. Go to https://railway.app/new
2. Deploy from GitHub repo
3. Branch: `migration/vercel-railway` (or current working branch)
4. Root directory: `backend`

### 2. Add Railway PostgreSQL
1. Add PostgreSQL database to project
2. Railway auto-links `DATABASE_URL`

### 3. Set Railway Environment Variables
```bash
APP_ENV=production
SECRET_KEY=<generate-32-chars>
ALLOWED_ORIGINS=["https://YOUR-VERCEL-APP.vercel.app"]
PLATFORM=railway
LOG_LEVEL=INFO
```

### 4. Create Vercel Project
1. Go to https://vercel.com/new
2. Import from GitHub
3. Root directory: `frontend`
4. Set `BACKEND_URL` to Railway URL

### 5. Run Template Import
After both are deployed:
```bash
curl -X POST https://YOUR-RAILWAY-BACKEND.up.railway.app/api/admin/import-templates
```

### 6. Verify
- Test health endpoint
- Test templates endpoint
- Check dashboard in browser
- Verify 43 templates imported

### 7. Write Handoff for QA Agent
Document:
- Live URLs
- Environment variables set
- Import results
- Any issues encountered

---

## Rollback Note

The Azure deployment continues to work:
- Legacy detection in `config.ts` still works
- Azure URLs are still in backend CORS
- No breaking changes for Azure path

---

## Quick Reference

```bash
# Run deployment agent
/migration-deploy
```
