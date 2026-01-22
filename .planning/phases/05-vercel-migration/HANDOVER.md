# Phase 5: Vercel Migration - Agent Handover

**Created:** 2026-01-22
**Status:** Ready to Start
**Prerequisites:** Phase 4 ✅ Complete (Stack Upgrade)

---

## MASTER PROMPT

You are implementing Phase 5 of the Proaktiv Dokument Hub project: **Vercel Migration**. This moves the frontend from Railway to Vercel while keeping the backend on Railway.

### Your Mission

1. Update backend CORS for Vercel domains
2. Configure `vercel.json` with API rewrites
3. Deploy frontend to Vercel
4. Verify all functionality works
5. Remove Railway frontend service

### Stack (Current)
- **Backend:** FastAPI 0.109 + SQLAlchemy 2.0.46 + PostgreSQL (Railway)
- **Frontend:** Next.js 16 + React 19 + Tailwind 4 + TypeScript 5.9
- **CI/CD:** GitHub Actions (lint, typecheck, test, build)

---

## AGENT PIPELINE

Execute these agents in sequence:

| Order | Agent | Command | Purpose |
|-------|-------|---------|---------|
| 1 | Infra Architect | `/vercel-architect` | Update CORS, create vercel.json |
| 2 | Builder | `/vercel-builder` | Deploy to Vercel, configure env vars |
| 3 | QA Master | `/vercel-qa` | Test all functionality |
| 4 | Cleanup | `/vercel-cleanup` | Remove Railway frontend |

---

## PLAN FILES

| Plan | Focus | Files |
|------|-------|-------|
| **05-01** | CORS Update | `backend/app/main.py`, `backend/app/config.py` |
| **05-02** | Vercel Config | `frontend/vercel.json`, `frontend/next.config.js` |
| **05-03** | Deployment | Vercel dashboard, environment variables |
| **05-04** | Verification | Full E2E testing |
| **05-05** | Cleanup | Railway dashboard, documentation |

---

## KEY URLS

| Service | Current URL |
|---------|-------------|
| Frontend (Railway) | https://blissful-quietude-production.up.railway.app |
| Backend (Railway) | https://proaktiv-dokument-hub-production.up.railway.app |
| Frontend (Vercel) | https://proaktiv-dokument-hub.vercel.app (after deploy) |

---

## ENVIRONMENT VARIABLES

### Vercel (to set)
```
BACKEND_URL=https://proaktiv-dokument-hub-production.up.railway.app
NEXT_PUBLIC_API_URL=https://proaktiv-dokument-hub-production.up.railway.app
NEXT_PUBLIC_SENTRY_DSN=(copy from Railway)
```

### Railway Backend (to update)
```
ALLOWED_ORIGINS=["https://proaktiv-dokument-hub.vercel.app","https://*.vercel.app","https://blissful-quietude-production.up.railway.app"]
```

---

## TESTING CHECKLIST

After each plan:
- [ ] Backend health check passes
- [ ] Frontend loads without errors
- [ ] Login/logout works
- [ ] Templates list loads
- [ ] Template preview renders
- [ ] No CORS errors in console

---

## COMMON PITFALLS

1. **CORS wildcard**: Vercel preview URLs need `*.vercel.app` pattern
2. **Cookie domain**: JWT auth may need `SameSite=None; Secure`
3. **API rewrites**: Must match exact path patterns
4. **Build timeout**: Next.js builds may timeout on free tier
5. **Environment scope**: Vercel env vars have production/preview/development scopes

---

## START COMMAND

Read and execute `.planning/phases/05-vercel-migration/05-01-PLAN.md` first.
Auto-write and commit after each plan without asking for approval.
