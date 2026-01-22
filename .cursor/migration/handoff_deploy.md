# Handoff: Deployment Agent → QA Agent

**Date:** 2026-01-16
**Status:** ✅ COMPLETE (Historical)
**Next Agent:** N/A - Migration complete

> **Note (2026-01-22):** This is a historical document from the Azure → Railway migration.
> Railway migration is complete. Stack upgraded to Next.js 16 + React 19 + Tailwind 4.
> For current state, see `.planning/STATE.md`.

---

## What Was Done

### 1. Created Deployment Guide
**File:** `.cursor/migration/DEPLOYMENT_GUIDE.md`

Comprehensive step-by-step guide for:
- Railway backend setup
- PostgreSQL database setup
- Vercel frontend setup
- CORS configuration
- Template import
- Verification steps

### 2. Created Railway Configuration
**File:** `backend/railway.json`

Railway-specific deployment config:
- Uses Dockerfile build
- Sets health check path
- Configures restart policy

### 3. Created Vercel Configuration
**File:** `frontend/vercel.json`

Vercel-specific deployment config:
- Next.js framework
- EU region (fra1) for Norway-based users
- API cache headers

---

## Files Created

| File | Purpose |
|------|---------|
| `.cursor/migration/DEPLOYMENT_GUIDE.md` | Step-by-step deployment instructions |
| `backend/railway.json` | Railway deployment config |
| `frontend/vercel.json` | Vercel deployment config |

---

## Manual Steps Required

The deployment requires manual steps on Railway and Vercel dashboards:

### Railway
1. Create project from GitHub
2. Set root directory to `backend`
3. Add PostgreSQL database
4. Set environment variables
5. Deploy and get backend URL

### Vercel
1. Import from GitHub
2. Set root directory to `frontend`
3. Set `BACKEND_URL` environment variable
4. Deploy

### Post-Deployment
1. Update Railway `ALLOWED_ORIGINS` with Vercel URL
2. Run template import: `POST /api/admin/import-templates`

---

## Environment Variables Summary

### Railway (Backend)
```
APP_ENV=production
SECRET_KEY=<generate-random>
ALLOWED_ORIGINS=["https://YOUR-VERCEL-APP.vercel.app"]
PLATFORM=railway
LOG_LEVEL=INFO
DATABASE_URL=<auto-linked-by-railway>
```

### Vercel (Frontend)
```
BACKEND_URL=https://YOUR-RAILWAY-URL.up.railway.app
```

---

## Expected URLs

After deployment, you should have:

| Service | Example URL |
|---------|-------------|
| Backend | `https://dokumenthub-production.up.railway.app` |
| Frontend | `https://proaktiv-dokument-hub.vercel.app` |
| API Docs | `https://dokumenthub-production.up.railway.app/docs` |

---

## QA Agent Should

### 1. Verify Backend Health
```bash
curl https://RAILWAY-URL/api/health
```
Expected: `{"status": "healthy", ...}`

### 2. Verify Template Import
```bash
curl https://RAILWAY-URL/api/admin/template-content-stats
```
Expected: `{"total_templates": 43, "with_content": 43, ...}`

### 3. Test API Endpoints
- `GET /api/templates` - List templates
- `GET /api/dashboard/stats` - Dashboard stats
- `GET /api/categories` - Categories list

### 4. Test Frontend
Open Vercel URL and verify:
- [ ] Dashboard loads without errors
- [ ] Template list shows 43 templates
- [ ] Template preview renders content
- [ ] Code editor shows HTML
- [ ] Save functionality works

### 5. Check Console
- [ ] No CORS errors
- [ ] No 500 errors
- [ ] No missing resource errors

### 6. Approve or Reject

If all tests pass:
- Approve merge to main
- Document any known issues

If tests fail:
- Document failures
- Hand back to appropriate agent for fixes

---

## Rollback Note

Azure deployment remains active:
- `https://dokumenthub-web.greenmushroom-2067e5c8.norwayeast.azurecontainerapps.io`
- Can be used as fallback during transition

---

## Cost Comparison

| Platform | Estimated Monthly Cost |
|----------|------------------------|
| Azure (current) | ~$30-50 |
| Railway + Vercel | $0-10 |

**Savings:** ~$20-40/month

---

## Quick Reference

```bash
# Run QA agent
/migration-qa
```
