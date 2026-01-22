# Vercel Migration Cleanup

You are the Cleanup Agent for Phase 5: Vercel Migration.

## Your Mission

Remove the Railway frontend service and update all documentation to reflect the completed migration.

## Prerequisites

- QA must have passed (run `/vercel-qa` first)
- All functionality verified on Vercel

## Context Files (Read First)
1. `.planning/phases/05-vercel-migration/05-05-PLAN.md` - Cleanup plan

## Execute Plan

Read and execute `05-05-PLAN.md` (Cleanup)

## Tasks

### 1. Verify One More Time
```bash
curl https://proaktiv-dokument-hub.vercel.app/api/health
```
Must return healthy before proceeding.

### 2. Remove Railway Frontend

**DANGER ZONE - Only proceed if QA passed!**

Via Railway CLI:
```bash
railway service delete blissful-quietude
```

Or via Dashboard:
1. Go to https://railway.app/dashboard
2. Select the project
3. Click on frontend service
4. Settings → Danger Zone → Delete

### 3. Update Documentation

Update these files:
- `CLAUDE.md` - Production URLs section
- `.planning/STATE.md` - Phase completion
- `.planning/ROADMAP.md` - Mark Phase 5 complete
- `.planning/REQUIREMENTS.md` - Mark VERCEL-* complete

### 4. Update GitHub Description
```bash
gh repo edit proaktivadmin/Proaktiv-Dokument-Hub --description "Document template management for Norwegian real estate brokers. Next.js 16 (Vercel) + FastAPI (Railway) + PostgreSQL."
```

### 5. Archive Phase 5
```powershell
Move-Item ".planning\phases\05-vercel-migration" ".planning\phases\_complete\"
```

### 6. Commit and Push
```bash
git add -A
git commit -m "docs: complete Phase 5 Vercel migration"
git push origin main
```

## Success Criteria

- Railway shows only backend + database
- Documentation updated
- GitHub description updated
- Phase archived

## Final Architecture

```
┌─────────────────┐     ┌─────────────────────────────────┐
│     Vercel      │     │            Railway              │
│  ┌───────────┐  │     │  ┌─────────────┐  ┌──────────┐ │
│  │ Frontend  │  │────▶│  │   Backend   │──│ Postgres │ │
│  │ (Next.js) │  │     │  │  (FastAPI)  │  │    DB    │ │
│  └───────────┘  │     │  └─────────────┘  └──────────┘ │
└─────────────────┘     └─────────────────────────────────┘
```

## Phase 5 Complete! 🎉

Congratulations! The project is now running on the optimal architecture:
- **Vercel** for Next.js frontend (best-in-class Next.js hosting)
- **Railway** for FastAPI backend + PostgreSQL (reliable, simple)
