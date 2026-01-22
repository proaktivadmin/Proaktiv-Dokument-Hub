# Vercel Migration Builder

You are the Builder for Phase 5: Vercel Migration.

## Your Mission

Deploy the frontend to Vercel and configure all environment variables.

## Prerequisites

- Plans 05-01 and 05-02 must be complete (run `/vercel-architect` first)
- CORS changes must be deployed to Railway

## Context Files (Read First)
1. `.planning/phases/05-vercel-migration/HANDOVER.md` - Phase context
2. `.planning/phases/05-vercel-migration/05-03-PLAN.md` - Deployment plan

## Execute Plan

Read and execute `05-03-PLAN.md` (Deploy to Vercel)

## Deployment Steps

### 1. Push CORS changes to Railway
```bash
git push origin main
# Wait for Railway to redeploy backend
```

### 2. Deploy to Vercel (CLI method)
```bash
cd frontend
npx vercel login
npx vercel link
npx vercel --prod
```

### 3. Set Environment Variables
In Vercel Dashboard → Settings → Environment Variables:
- `BACKEND_URL` = `https://proaktiv-dokument-hub-production.up.railway.app`
- `NEXT_PUBLIC_API_URL` = `https://proaktiv-dokument-hub-production.up.railway.app`
- `NEXT_PUBLIC_SENTRY_DSN` = (copy from Railway)

### 4. Trigger Redeploy
After setting env vars, redeploy to pick them up.

## Verification

```bash
curl https://proaktiv-dokument-hub.vercel.app/api/health
```

Should return `{"status": "healthy"}`.

## Success Criteria

- Vercel deployment successful
- All environment variables set
- API proxy working
- Frontend loads without errors

## Handoff

After deployment is working, hand off to `/vercel-qa` for full testing.
