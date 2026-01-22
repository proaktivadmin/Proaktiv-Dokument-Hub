# Phase 5: Vercel Migration - Research

**Created:** 2026-01-22
**Status:** Research Complete
**Goal:** Migrate frontend from Railway to Vercel while keeping backend on Railway

---

## Why Vercel?

| Benefit | Details |
|---------|---------|
| **Native Next.js support** | Vercel created Next.js, best-in-class optimization |
| **Preview deployments** | Every PR gets a preview URL |
| **Edge functions** | Faster cold starts than Railway |
| **Analytics** | Built-in Web Vitals tracking |
| **Image optimization** | Automatic via next/image |
| **Cost** | Free tier is generous for this use case |

---

## Current Architecture

```
┌─────────────────────────────────────────────────────────┐
│                      Railway                            │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────┐ │
│  │    Frontend     │  │     Backend     │  │ Postgres│ │
│  │   (Next.js)     │──│   (FastAPI)     │──│   DB    │ │
│  │ blissful-...    │  │ proaktiv-...    │  │         │ │
│  └─────────────────┘  └─────────────────┘  └─────────┘ │
└─────────────────────────────────────────────────────────┘
```

## Target Architecture

```
┌─────────────────┐     ┌─────────────────────────────────┐
│     Vercel      │     │            Railway              │
│  ┌───────────┐  │     │  ┌─────────────┐  ┌──────────┐ │
│  │ Frontend  │  │────▶│  │   Backend   │──│ Postgres │ │
│  │ (Next.js) │  │     │  │  (FastAPI)  │  │    DB    │ │
│  └───────────┘  │     │  └─────────────┘  └──────────┘ │
└─────────────────┘     └─────────────────────────────────┘
```

---

## Migration Steps Overview

### 1. Prepare Backend (Railway)
- Update CORS to allow Vercel domains
- Verify all environment variables are set
- Test API health endpoint

### 2. Deploy to Vercel
- Connect GitHub repository
- Set root directory to `frontend/`
- Configure environment variables
- Set up API rewrites in `vercel.json`

### 3. Verify & Test
- Test all API calls work
- Verify authentication flows
- Check image loading
- Test preview deployments

### 4. Cleanup Railway
- Remove frontend service from Railway
- Update documentation
- Update DNS if custom domain

---

## Environment Variables

### Vercel Frontend
| Variable | Value |
|----------|-------|
| `BACKEND_URL` | `https://proaktiv-dokument-hub-production.up.railway.app` |
| `NEXT_PUBLIC_API_URL` | `https://proaktiv-dokument-hub-production.up.railway.app` |
| `NEXT_PUBLIC_SENTRY_DSN` | (existing Sentry DSN) |

### Railway Backend (Update)
| Variable | Change |
|----------|--------|
| `ALLOWED_ORIGINS` | Add Vercel domains |

---

## CORS Configuration

Backend needs to accept requests from:
- `https://*.vercel.app` (preview deployments)
- `https://proaktiv-dokument-hub.vercel.app` (production)
- Custom domain if configured

```python
# backend/app/main.py
ALLOWED_ORIGINS = [
    "https://proaktiv-dokument-hub.vercel.app",
    "https://*.vercel.app",  # Preview deployments
    # Keep Railway URL during transition
    "https://blissful-quietude-production.up.railway.app",
]
```

---

## API Rewrites

```json
// frontend/vercel.json
{
  "rewrites": [
    {
      "source": "/api/:path*",
      "destination": "https://proaktiv-dokument-hub-production.up.railway.app/api/:path*"
    }
  ]
}
```

---

## Risk Assessment

| Risk | Mitigation |
|------|------------|
| CORS issues | Test with preview deployment first |
| Auth breaks | Verify JWT cookies work cross-origin |
| Image loading | External images already configured |
| Cold starts | Edge runtime for critical routes |
| Rollback needed | Keep Railway frontend until verified |

---

## Rollback Plan

If Vercel deployment fails:
1. Railway frontend is still running
2. No DNS changes until verified
3. Can revert by pointing traffic back to Railway

---

## Success Criteria

- [ ] Vercel deployment builds successfully
- [ ] All API endpoints work
- [ ] Authentication works (login/logout)
- [ ] Images load correctly
- [ ] Preview deployments work for PRs
- [ ] Performance is equal or better
- [ ] Railway frontend can be removed
