# Project State

> **This is the single source of truth for project status.**
> See also: `CLAUDE.md` (quick reference), `.cursor/workflow_guide.md` (workflow)

## Project Reference

See: .planning/PROJECT.md (updated 2026-01-22)

**Core value:** Brokers can manage and preview document templates without touching code
**Current focus:** Phase 2 - Vitec Sync Review UI

## Current Position

Phase: 3.5 (Navigation Reorganized, Logo Library)
Plan: V3.5 complete
Status: Production live
Last activity: 2026-01-23 — Navigation reorganization, LogoLibrary, avatar resizing

Progress: [█████████░] 90% (V3.5 features complete, Phase 06 ready for testing)

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

Last session: 2026-01-23
Stopped at: V3.5 Navigation & Logo Library complete
Resume file: None (ready for new work)
Next step: Continue with Phase 06 Entra ID testing OR Phase 07 Office Enhancements

### Session Summary (2026-01-23 - Latest)
**Changes:**
1. **Navigation Reorganization:**
   - Ressurser dropdown: Maler, Kategorier, Mediefiler, WebDAV Lagring
   - Selskap dropdown: Kontorer, Ansatte, Markedsområder, Mottakere
   - Verktøy dropdown: Sanitizer, Synkronisering, Portal Skins

2. **Logo Library:**
   - New `LogoLibrary` component at `/assets` → Proaktiv Logoer tab
   - Preview cards with copy URL, download, open in new tab
   - 6 logo assets from proaktiv.no/assets/logos/

3. **Avatar Image Resizing:**
   - Backend `ImageService` for server-side cropping/resizing
   - `/api/vitec/employees/{id}/picture?size=128&crop=top`
   - Frontend `resolveAvatarUrl()` helper
   - All avatar components updated

4. **Office Enhancements:**
   - Sub-offices display on office cards and detail pages
   - Parent-child office hierarchy (`office_type`, `parent_office_id`)
   - Dashboard office tags removed for cleaner UI

5. **Employee Data Cleanup:**
   - `employee_type` field (internal/external/system)
   - Entra sync filters to only internal employees
   - Cleanup script for Vitec as single source of truth

### Previous Session Summary (2026-01-23)
**Issue:** 401 Unauthorized errors on all authenticated API endpoints after login
**Root Cause:** Frontend made direct cross-origin requests to Railway backend. Browsers blocked third-party cookies, so session cookie wasn't sent with API requests.
**Fix:** Modified `frontend/src/lib/api/config.ts` to use relative URLs (`/api/*`) for all API calls. Vercel rewrites proxy these to Railway, making cookies first-party.

## Recent Changes (2026-01-23)

### V3.5 Navigation & Logo Library
**Navigation Reorganization:**
- Renamed "Dokumenter" dropdown to "Ressurser" (files/documents focus)
- Renamed "Selskap" dropdown to include HR/organization items
- Moved Assets from Selskap to Ressurser
- Moved WebDAV Storage from Verktøy to Ressurser
- Moved Mottakere from Dokumenter to Selskap

**New Ressurser menu:**
- Maler → `/templates`
- Kategorier → `/categories`
- Mediefiler → `/assets` (includes Proaktiv Logoer tab)
- WebDAV Lagring → `/storage`

**New Selskap menu:**
- Kontorer → `/offices`
- Ansatte → `/employees`
- Markedsområder → `/territories`
- Mottakere → `/mottakere`

**Logo Library (`/assets` → Proaktiv Logoer tab):**
- New `LogoLibrary` component with preview cards
- Copy URL button with tooltip showing full URL
- Download button for saving logos locally
- Open in new tab button
- 6 logo assets: logo.svg, logo-white.svg, logo-dark.svg, icon.svg, icon-white.svg, favicon.png
- Proper background preview (dark for white logos, checkered for transparent)

**Avatar Image Resizing:**
- New `ImageService` in `backend/app/services/image_service.py`
- Server-side cropping and resizing using Pillow
- `resize_for_avatar(image_data, size, crop_mode)` method
- Crop modes: "top" (faces), "center", "face" (not implemented)
- API endpoint: `/api/vitec/employees/{id}/picture?size=128&crop=top`
- Frontend helper: `resolveAvatarUrl(url, size, crop)` in `lib/api/config.ts`
- All avatar components updated to use proper sizes

**Office Sub-departments:**
- New `office_type` field: main, sub, regional
- New `parent_office_id` foreign key for hierarchy
- Sub-offices displayed on parent office cards
- Sub-offices section on office detail pages
- Offices list excludes sub-offices by default (`include_sub: false`)

**Dashboard Cleanup:**
- Removed office tags section from main dashboard
- Cleaner, more focused layout

**Employee Type System:**
- New `employee_type` field: internal, external, system
- New `external_company` field for contractor details
- Entra sync filters to only sync internal employees
- `should_sync_to_entra` property on Employee model

### V3.4 Portal Skins Preview
- Vitec Budportal and Visningsportal skin packages
- Authentic mockup preview with Proaktiv branding
- Fullscreen preview mode
- Voss office mode toggle

### V3.3 API Proxy Fix (Critical Production Fix)
**Problem:** After login, all API calls returned 401 Unauthorized
**Symptoms:**
- `/api/auth/check` returned 200 OK (public route)
- All other endpoints returned 401 with "Not authenticated"
- Session cookie was set correctly but not sent with API requests

**Root Cause:**
- `frontend/src/lib/api/config.ts` detected Vercel domains and returned direct Railway URL
- API requests went directly to `https://proaktiv-admin.up.railway.app` (cross-origin)
- Browsers treat cross-origin cookies as third-party and block them
- Session cookie wasn't included in requests

**Solution:**
- Modified `getApiBaseUrl()` to always return empty string
- All API calls now use relative URLs (`/api/templates`, `/api/offices`, etc.)
- Vercel's rewrite rules (in `vercel.json`) proxy `/api/*` to Railway
- Requests appear same-origin to browser, cookies are first-party

**Key Files:**
- `frontend/src/lib/api/config.ts` - Removed hostname detection, always use relative URLs
- `frontend/vercel.json` - Contains rewrite rules (already correct)
- `frontend/src/lib/api/auth.ts` - Uses separate axios instance with relative URLs

**Lessons Learned:**
1. Never make direct cross-origin requests when using cookies for auth
2. Always proxy API requests through frontend's domain
3. Vercel build cache can persist old code - use `vercel --prod --force` when debugging

---

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
