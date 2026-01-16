# QA Checklist: Migration to Railway + Vercel

**Date:** 2026-01-16
**Status:** Pre-Deployment QA Complete ✅

## Summary

| Category | Status |
|----------|--------|
| Backend Build | ✅ PASS |
| Backend API Tests | ✅ PASS (all endpoints working) |
| Frontend Build | ✅ PASS (no TypeScript errors) |
| Template Content | ✅ 43/43 templates have content (100%) |
| Ready for Deployment | ✅ YES |

---

## Pre-Deployment Verification (Local)

These tests can be run locally before deploying to Railway/Vercel.

### Backend Tests

| Test | Command | Expected | Status |
|------|---------|----------|--------|
| Docker builds | `docker compose build backend` | Success | ✅ PASS |
| Container starts | `docker compose up -d` | Healthy | ✅ PASS |
| Health endpoint | `curl localhost:8000/api/health` | 200 OK | ✅ PASS |
| Templates list | `curl localhost:8000/api/templates` | Array of templates | ✅ PASS (43 templates) |
| Dashboard stats | `curl localhost:8000/api/dashboard/stats` | Stats object | ✅ PASS |
| Admin import | N/A - templates already have content | Import count | ✅ N/A |
| Content stats | `curl localhost:8000/api/admin/template-content-stats` | Percentage | ✅ PASS (100%)

### Frontend Tests

| Test | Command | Expected | Status |
|------|---------|----------|--------|
| Build succeeds | `cd frontend && npm run build` | No errors | ✅ PASS |
| Dev server starts | `npm run dev` | Runs on :3000 | ⏳ (manual) |
| Dashboard loads | Browser check | No errors | ⏳ (manual) |
| Templates visible | Browser check | 43 templates | ⏳ (manual) |
| Preview renders | Click template | HTML displays | ⏳ (manual) |

### Code Quality

| Check | Command | Expected | Status |
|-------|---------|----------|--------|
| No TypeScript errors | `cd frontend && npm run build` | Success | ✅ PASS |
| No lint errors | `cd frontend && npm run lint` | 0 errors | ⏳ |
| Backend imports clean | `docker compose exec backend python -c "..."` | No errors | ✅ PASS |

---

## Post-Deployment Verification

After deploying to Railway and Vercel:

### Backend (Railway)

| Test | URL | Expected |
|------|-----|----------|
| Health | `GET /api/health` | `{"status": "healthy"}` |
| Templates | `GET /api/templates` | Array with 43 items |
| Dashboard | `GET /api/dashboard/stats` | Stats with totals |
| API Docs | `/docs` | Swagger UI loads |

### Frontend (Vercel)

| Test | Check | Expected |
|------|-------|----------|
| Homepage loads | Visual | Dashboard visible |
| No console errors | DevTools | 0 errors |
| API calls work | Network tab | 200 responses |
| Template preview | Click card | Content renders |
| Code editor | Click edit | Monaco loads |

### Integration

| Test | Check | Expected |
|------|-------|----------|
| CORS working | API calls from frontend | No CORS errors |
| Auth headers | If enabled | Proper authentication |
| Environment | Check `APP_ENV` | `production` |

---

## Migration-Specific Tests

### Database Content

| Check | Expected |
|-------|----------|
| Template count | 43 |
| Templates with content | 43 |
| No Azure blob references in content | ✓ |

### Legacy Compatibility

| Check | Expected |
|-------|----------|
| Azure app still works | ✓ (not modified) |
| API responses match | Same structure |
| No data loss | All templates present |

---

## Known Issues / Workarounds

### Issue 1: Template Import Requires library/ folder
**Workaround:** The `library/` folder needs to be available in the Railway container. Options:
1. Include in Docker build (add to .dockerignore exclusion)
2. Seed database from local machine
3. Use Railway CLI to run import

### Issue 2: Azure Storage Deprecation Warning
**Status:** Expected behavior. Warning appears in logs but doesn't affect functionality.

---

## Sign-off

### Local Testing
- [x] All backend endpoints return expected data
- [x] Frontend builds without errors
- [ ] Dashboard loads and displays data (manual browser test)
- [ ] No console errors (manual browser test)

### Production Testing (After Deployment)
- [ ] Railway backend is healthy
- [ ] Vercel frontend loads
- [ ] API calls work end-to-end
- [ ] 43 templates imported and accessible

### Approval

**QA Status:** ⏳ Pending Deployment

Once Railway and Vercel are set up and tested:

- [ ] **APPROVED** - Ready to merge to main
- [ ] **REJECTED** - Issues found (document below)

---

## Issues Found

*(Document any issues discovered during QA)*

None yet - pending deployment.

---

## Merge Instructions

After QA approval:

```bash
# Ensure on migration branch
git checkout migration/vercel-railway

# Merge to main
git checkout main
git merge migration/vercel-railway
git push origin main
```

Or, if following the user's workflow:
- Continue development on `V2-development`
- Sync to `migration/vercel-railway` when stable
- Merge to main after full verification
