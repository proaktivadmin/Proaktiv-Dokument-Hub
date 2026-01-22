# Project State

> **This is the single source of truth for project status.**
> See also: `CLAUDE.md` (quick reference), `.cursor/workflow_guide.md` (workflow)

## Project Reference

See: .planning/PROJECT.md (updated 2026-01-22)

**Core value:** Brokers can manage and preview document templates without touching code
**Current focus:** Phase 2 - Vitec Sync Review UI

## Current Position

Phase: 2 of 5 (Vitec Sync Review UI)
Plan: 0 of 5 in current phase
Status: Ready to plan
Last activity: 2026-01-22 — Phase 4 (Stack Upgrade) completed

Progress: [████░░░░░░] 40% (2 of 5 phases complete)

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
Stopped at: CI pipeline fixed and passing, documentation updated
Resume file: None

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
