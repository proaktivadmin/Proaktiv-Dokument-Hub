# AGENTS.md

## Project

Vitec Next Admin Hub (Proaktiv Dokument Hub) is a document-first template management system for Norwegian real estate brokers. The stack is Next.js 16 + React 19 on the frontend and FastAPI + PostgreSQL on the backend, deployed via Vercel and Railway.

## First read checklist

Read this file first, then pull in the docs that match the task:

1. Read `.planning/STATE.md` and the relevant phase plan in `.planning/phases/` for active context.
2. For frontend work, read `.planning/codebase/DESIGN-SYSTEM.md` before editing UI.
3. For database work, read `.cursor/rules/database-migrations.mdc` before creating or applying migrations.
4. For Vitec template or merge-field work, read `.cursor/vitec-reference.md` and the relevant docs in `docs/`.
5. If business logic seems unclear or missing, inspect `_legacy_v1` before inventing new behavior.

## Core repo rules

- Keep the monorepo split: `frontend/` and `backend/` are siblings.
- Use strict typing everywhere. No `any` in TypeScript; use full type hints in Python.
- Prefer small, focused changes that follow existing patterns instead of introducing new abstractions.
- Never hardcode secrets or read env vars directly inside business logic; use the existing config/settings layer.
- When creating a new component or endpoint, add a targeted automated test file.

## Architecture guardrails

### Frontend

- Default to Server Components. Use `"use client"` only when hooks or browser APIs are required.
- Use the typed API wrapper in `frontend/src/lib/api.ts` or related API modules; avoid ad hoc `fetch()` calls inside components.
- Use Shadcn/UI patterns before inventing custom primitives.
- Follow the design system tokens. Do not hardcode colors, shadows, or transitions.
- Document preview is primary, code view is secondary.
- For template collections, dim filtered cards instead of hiding them.
- Use component naming conventions already established in the repo:
  - Viewer components: `*Frame.tsx`
  - Library components: `*Library.tsx`, `*Card.tsx`
  - Inspector component: `ElementInspector.tsx`

### Backend

- Business logic belongs in `backend/app/services/`, never in routers.
- Service methods should be async.
- Use FastAPI dependency injection with `Depends()`.
- Raise `HTTPException` with clear details for expected failures.
- Use Pydantic for validation and settings.
- Follow the existing SQLAlchemy patterns: UUID primary keys, JSONB for structured arrays/objects, timezone-aware timestamps, and decimal fields where precision matters.
- Prefer `flush()` over `commit()` where the project pattern expects session auto-commit.

### Vitec and template domain

- All merge-field operations should flow through `MergeFieldService`.
- Merge fields use `[[field.name]]` or `[[*field.name]]`.
- Conditions use `vitec-if`; loops use `vitec-foreach`.
- Keep the document-first editing model intact: preview first, inspector second, raw code as the escape hatch.
- Content saves should preserve versioning behavior and merge-field rescans already established in the template services.

## API and deployment constraints

- Frontend API calls must use relative `/api/*` paths, not direct Railway URLs.
- `frontend/vercel.json` rewrites `/api/*` to Railway so cookies stay first-party.
- Production auth is password + JWT session based and can be disabled when `APP_PASSWORD_HASH` is unset.
- Use the public Railway Postgres URL, never the internal hostname.

## Database migration rules

Railway migrations are not reliable enough to trust during deploy. After creating a migration:

1. Apply it locally.
2. Apply it manually to Railway using the public database URL.
3. Verify the current migration revision explicitly.
4. If Railway still misses the schema change, add a one-off repair script with safe `ALTER TABLE ... ADD COLUMN IF NOT EXISTS` logic.

Do not merge DB changes without handling the manual Railway migration path.

## Key directories

- `.planning/` - plans, roadmap, state, and phase docs
- `.cursor/` - agent prompts, specs, commands, rules, and Vitec reference
- `backend/app/services/` - business logic
- `backend/app/routers/` - FastAPI endpoints
- `backend/app/schemas/` - Pydantic schemas
- `frontend/src/app/` - Next.js app routes
- `frontend/src/components/` - UI and feature components
- `frontend/src/lib/` - API wrappers and utilities
- `skins/` - Vitec portal skins and related assets

## Cursor Cloud specific instructions

- Start local development with `docker compose up -d`.
- Backend health check: `curl http://localhost:8000/api/health`
- Frontend dev URL: `http://localhost:3000`
- For frontend changes, run targeted checks from `frontend/` such as `npm run test:run`, `npm run lint`, or a focused build/test command relevant to the change.
- For backend changes, run targeted checks from `backend/` such as `pytest` on the relevant test module plus any needed lint/type checks.
- Prefer targeted tests over full-suite runs unless the task truly spans the whole app.
- If you start local services for testing, leave them running when you are done unless the task requires cleanup.

## Agent workflow

1. Search for the existing pattern before editing.
2. Read the surrounding files and docs before changing behavior.
3. Make the smallest change that fits the current architecture.
4. Run the narrowest high-signal tests that prove the change works end to end.
5. If behavior, architecture, or workflow changes, update the relevant docs in `.planning/`, `docs/`, or this file.

## Current product context

- The app is production live.
- Phase 11 work centers on HTML template management and publishing.
- Important recent areas include template editing, deduplication, comparison, notifications, signatures, storage, and Vitec integration.
- A pending migration from `backend/alembic` history may still need manual Railway application: `20260221_0001_template_publishing.py`.

## Do not do these

- Do not use `any` in TypeScript.
- Do not put business logic in routers.
- Do not treat Monaco or raw code as the primary template experience.
- Do not hide filtered template cards; dim them instead.
- Do not hardcode design tokens.
- Do not assume Railway deploys applied your migration.
- Do not use `postgres.railway.internal`.
- Do not bypass the API proxy architecture from the frontend.
