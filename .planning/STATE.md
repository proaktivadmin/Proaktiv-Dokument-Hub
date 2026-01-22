# Project State

> **This is the single source of truth for project status.**
> See also: `CLAUDE.md` (quick reference), `.cursor/workflow_guide.md` (workflow)

## Project Reference

See: .planning/PROJECT.md (updated 2026-01-22)

**Core value:** Brokers can manage and preview document templates without touching code
**Current focus:** Phase 2 - Vitec Sync Review UI

## Current Position

Phase: 5 of 5 (Vercel Migration)
Plan: 2 of 5 in current phase (05-01, 05-02 complete)
Status: In progress - ready for deployment
Last activity: 2026-01-22 — Plans 05-01 (CORS) and 05-02 (Vercel Config) complete

Progress: [████████░░] 80% (2 of 5 phases complete, Phase 5 in progress)

## Performance Metrics

**Velocity:**
- Total plans completed: 8 (Phase 1: 3, Phase 4: 5)
- Average duration: ~2 hours per plan
- Total execution time: ~16 hours

**By Phase:**

| Phase | Plans | Status | Completed |
|-------|-------|--------|-----------|
| 1. Vitec API Connection | 3/3 | Complete | 2026-01-20 |
| 4. Stack Upgrade | 5/5 | Complete | 2026-01-22 |
| 5. Vercel Migration | 2/5 | In Progress | - |
| 6. Entra ID Signature Sync | 8/8 | Ready for Testing | 2026-01-22 |
| 7. Office Enhancements + SalesScreen | 0/8 | Ready | - |

**Recent Trend:**
- Phase 4 completed rapidly (same day)
- CI/CD pipeline now operational

*Updated after each plan completion*

## Accumulated Context

### Decisions

Decisions are logged in PROJECT.md Key Decisions table.
Recent decisions affecting current work:

- Manual sync review: Prevent bad data overwrites, require case-by-case approval
- Email-based employee matching: Most reliable identifier across systems
- Field-by-field diff: User chooses per-field, not all-or-nothing
- Static social links: No API integration, links rarely change
- Upgrade before migrate: Fix CVE-2025-29927 first, test on one platform
- Vercel for frontend: Better Next.js DX, preview deployments
- Skip Next.js 15, go to 16: Latest stable with React 19 support
- xfail incomplete tests: Don't block CI, track missing features

### Pending Todos

- 3 normalizer service tests marked as xfail (CSS stripping not implemented)

### Blockers/Concerns

None.

## Session Continuity

Last session: 2026-01-22
Stopped at: Phase 5 - Plans 05-01 and 05-02 complete (CORS + Vercel config)
Resume file: `.planning/phases/05-vercel-migration/05-03-PLAN.md`
Next step: Deploy frontend to Vercel using `/vercel-builder`

## Recent Changes (2026-01-22)

### Stack Upgrade Completed
- Next.js 14 → 16.1.4
- React 18 → 19.2.3
- Tailwind 3 → 4.1.18
- TypeScript 5.3 → 5.9.3
- SQLAlchemy 2.0.25 → 2.0.46

### CI/CD Pipeline Added
- GitHub Actions workflow (`.github/workflows/ci.yml`)
- Frontend: ESLint + TypeScript + Vitest
- Backend: Ruff + Pyright + Pytest
- All checks passing on main branch

### Testing Infrastructure
- Vitest configured for frontend
- Pytest + pytest-asyncio for backend
- 14 tests total (11 passing, 3 xfail)

### Structure Cleanup (2026-01-22)
- Archived Azure-related files (migration complete)
- Archived Railway migration docs (complete)
- Archived completed phases (1, 4) to `.planning/phases/_complete/`
- Archived session logs to `docs/_archive/`
- Consolidated context files (removed duplicates)
- Updated workflow guide with new structure

### Phase 06: Entra ID Signature Sync (Implementation Complete - Ready for Testing)
- Completed by `/entra-builder` agent on 2026-01-22
- All planned files created and integrated
- **PowerShell Script:**
  - `backend/scripts/Sync-EntraIdEmployees.ps1` - Full sync script with:
    - Certificate and client secret auth
    - Profile, photo, and signature sync
    - DryRun mode, FilterEmail for testing
    - Rate limiting and retry logic
  - `backend/scripts/templates/email-signature.html` - Proaktiv-branded HTML
  - `backend/scripts/templates/email-signature.txt` - Plain text fallback
  - `run-entra-sync.bat` - Windows launcher
  - `docs/entra-signature-sync.md` - Full documentation
- **Backend API:**
  - `backend/app/schemas/entra_sync.py` - Pydantic schemas
  - `backend/app/services/entra_sync_service.py` - Service layer
  - `backend/app/routers/entra_sync.py` - FastAPI endpoints
  - Config settings added to `backend/app/config.py`
- **Frontend:**
  - Types, API client, hooks in `frontend/src/types/entra-sync.ts`
  - 4 new components: EntraConnectionStatus, SignaturePreviewDialog, EntraSyncDialog, EntraSyncBatchDialog
  - EmployeeCard updated with selection checkbox + Entra menu items
  - EmployeeGrid updated with batch selection mode
  - employees/page.tsx wired up with all dialogs
- **Next step:** Run `/entra-qa` to test with real Azure credentials

### Phase 07: Office Enhancements + SalesScreen (Ready)
- Separated from Phase 06 to allow independent development
- Research complete: See 07-RESEARCH-SALESSCREEN.md
- 8 execution plans (07-01 through 07-08):
  - 07-01: Add region field to offices (DB + API)
  - 07-02: Region filter and grouping in office UI
  - 07-03: Office merge backend API
  - 07-04: Office merge frontend UI
  - 07-05: Add SalesScreen fields to Office model
  - 07-06: SalesScreen backend service and API
  - 07-07: SalesScreen frontend types, hooks, dialogs
  - 07-08: SalesScreen integration with employee UI + onboarding
- Ready for implementation after Phase 06 or in parallel

### Office Regions
Defined regions for geographic grouping:
- Trøndelag (Trondheim area)
- Romerike (Lillestrøm, Lørenskog area)
- Sør-Rogaland (Stavanger, Sandnes, Sola area)
- Vest (Bergen, Voss area)
- Sør (Kristiansand, Skien area)
- Øst (Oslo, Drammen area)
