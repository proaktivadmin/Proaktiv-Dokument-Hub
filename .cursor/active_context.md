# ACTIVE CONTEXT & ROADMAP
> **Workflow Rule:** Follow `.cursor/workflow_guide.md`. Update this file *before* coding.


## 2026-01-18 (LATEST) — VITEC TEMPLATE UX + DEPLOY STABILITY

### Shipped ✅ (on `main`)
- ✅ **Rebrand**: App name/UX aligned to **Vitec Next Admin Hub** (header + login + metadata)
- ✅ **Templates UX parity**
  - **Origin grouping** in list view (Vitec Next vs Kundemal)
  - **Pagination fixed** (working next/prev; increased `per_page` where appropriate)
  - **Attachments** shown (paperclip count + names) and detail view refetches `/templates/{id}` so it stays accurate
  - **Card view**: larger previews (fewer per row), cleaned overlays, channel badge moved to bottom row
- ✅ **“Kategorisering” fields exposed in Settings UI**
  - `template_type`, `receiver_type`, `receiver`, `extra_receivers`
  - `phases`, `assignment_types`, `ownership_types`, `departments`
  - Wired through: detail sheet + edit dialog + upload + new template
- ✅ **Dashboard**: “Vitec Malbibliotek Status” widget moved above “Nylig opplastet” + “Kategorier” and refetches after uploads
- ✅ **Vitec Next import tooling + docs**
  - Script: `backend/scripts/import_vitec_next_export.py`
  - Docs: `docs/vitec-next-export-format.md`, `docs/vitec-next-mcp-scrape-and-import.md`
- ✅ **Railway frontend build fixes**
  - Treat Vitec receiver values as free-form strings (typing)
  - Tighten status filter typing to `TemplateStatus`

### Known Gaps / Caveats ⚠️
- **Next.js warning**: `next@14.1.0` prints a security advisory warning during build; plan an upgrade window
- **Inventory stats can show 0 Vitec templates** until the Vitec registry is seeded/imported
- **WebDAV**: directory listing still needs server-side `PROPFIND` enabled

### “Next Agent” — Append Below ⬇️
<!-- NEXT_AGENT_NOTES_START -->

### QA PASS (LOCALHOST, 2026-01-18)
- Backend endpoints OK: `/api/health`, `/api/dashboard/stats`, `/api/templates`, `/api/templates/{id}`, `/api/categories`, `/api/merge-fields`, `/api/employees` (empty), `/api/offices`, `/api/assets`, `/api/territories` (empty).
- Backend gaps: `/api/ping` returns 404; `/api/employees/email-group` returns 422 because `/email-group` is shadowed by `/{employee_id}` route.
- Frontend OK: Dashboard loads; Templates list + Hylle view render; Template detail preview loads; Settings dialog shows "Kategorisering" fields; Employees/Offices/Assets/Mottakere pages render empty states.
- Frontend issues:
  - `/territories` shows "Request failed with status code 405" and console logs 405 at `/api/territories/stats`.
  - `/templates?receiver=Selger` shows CORS errors (no `Access-Control-Allow-Origin`) and "Nettverksfeil" banner.
  - Attachments badges include invalid values like `"0, False"` in templates list (data quality from metadata extraction).

### Fixes Started (2026-01-18)
- Plan: add `/api/ping`, add `/api/territories/stats`, move `/employees/email-group` above ID routes, and harden receiver filtering to avoid 500s in local dev.

### Fixes Completed (2026-01-18)
- Added `/api/ping`, `/api/territories/stats`, and reordered `/employees/email-group` to avoid UUID shadowing.
- Receiver filter now returns 200; CORS/UI errors on `/templates?receiver=Selger` cleared.
- `/territories` no longer shows 405 in the UI.
- Template settings update no longer 500s; audit log now serializes settings payload safely.
- Shelf view now loads all pages (shows full 259 templates instead of first 100).

<!-- (leave space for next agent’s updates) -->

<!-- NEXT_AGENT_NOTES_END -->

## PROJECT STATUS
- **Phase:** V3.1 Verification (polish + QA)
- **Current Sprint:** Stabilize templates workflow + verify Company Hub pages
- **Architecture:** Document-first, shelf grouping, 4-tab viewer
- **Deploy:** Railway (frontend + backend), deploys on push to `main`


## V2.9 VITEC INTEGRATION (2026-01-17) - IN PROGRESS

### Completed Today ✅
- ✅ Full Vitec reference documentation (`.cursor/vitec-reference.md`)
- ✅ Enhanced SanitizerService with Vitec Stilark compliance
- ✅ WebDAV storage integration (backend service + API)
- ✅ Storage browser UI with file management
- ✅ Import-to-library functionality from WebDAV
- ✅ Layout partials for headers/footers/signatures
- ✅ Channel-aware layout partial selectors in settings
- ✅ Inventory dashboard widget (sync status with Vitec)
- ✅ Multiple bug fixes for Railway deployment
- ✅ **Password Authentication System** (single-user, JWT sessions)
- ✅ Login page with password protection
- ✅ Auth middleware protecting all API routes
- ✅ Logout button in header
- ✅ Railway CLI integration for deployment management

### Pending Configuration
- ⏳ WebDAV server needs PROPFIND enabled for directory listing
- ⏳ Contact web developer to enable WebDAV protocol support

### New Files Created
| File | Purpose |
|------|---------|
| `backend/app/services/webdav_service.py` | WebDAV client wrapper |
| `backend/app/routers/storage.py` | Storage API endpoints |
| `backend/app/routers/auth.py` | Authentication endpoints (login/logout/status) |
| `backend/app/middleware/auth.py` | JWT session validation middleware |
| `backend/app/services/inventory_service.py` | Vitec template sync stats |
| `backend/scripts/generate_password_hash.py` | CLI tool to generate bcrypt hashes |
| `frontend/src/app/storage/page.tsx` | Storage browser page |
| `frontend/src/app/login/page.tsx` | Password login page |
| `frontend/src/components/storage/` | Storage UI components |
| `frontend/src/components/auth/AuthProvider.tsx` | Auth guard wrapper |
| `frontend/src/lib/api/auth.ts` | Auth API client |
| `frontend/src/hooks/useLayoutPartials.ts` | Layout partials hook |
| `frontend/src/hooks/useInventoryStats.ts` | Inventory stats hook |
| `.cursor/vitec-reference.md` | Full Vitec Next reference |

### Bug Fixes Today
- ✅ Fixed `layoutPartialsApi.list()` call signature in v2 hook
- ✅ Fixed undefined `NEW_RESOURCE_STRING` in SanitizerService
- ✅ Fixed Category/categoryApi exports in API barrel file
- ✅ Improved WebDAV error handling with user-friendly messages

## V2.8 RAILWAY MIGRATION (2026-01-17) ✅

### Migration Complete
- ✅ Backend deployed to Railway (FastAPI + PostgreSQL)
- ✅ Frontend deployed to Railway (Next.js)
- ✅ 44 templates imported to PostgreSQL database
- ✅ 11 categories seeded
- ✅ Azure dependencies completely removed
- ✅ GitHub branches cleaned (main + V2-development)
- ✅ Deploys from `main` branch

### Production URLs
- **Frontend:** https://blissful-quietude-production.up.railway.app
- **Backend:** https://proaktiv-dokument-hub-production.up.railway.app

## V2.7 COMPLETED FEATURES (2026-01-16)

### 1. Template Content Editing API ✅
- `PUT /api/templates/{id}/content` - Save edited HTML content
- Automatic versioning (creates TemplateVersion before save)
- Re-scan merge fields after content update
- Optional HTML sanitization
- Wired to Monaco Editor with Ctrl+S save shortcut

### 2. Template Settings API ✅
- `PUT /api/templates/{id}/settings` - Save Vitec metadata
- `GET /api/templates/{id}/settings` - Retrieve settings
- Support for margins, header/footer, channel, phases, receivers
- Validate layout partial references
- Wired to Settings panel with save button

### 3. Dashboard Stats API ✅
- `GET /api/dashboard/stats` - Returns template counts
- `GET /api/dashboard/inventory` - Vitec sync status
- Dashboard now uses real backend data

## V2 CORE CONCEPTS

### Document-First Paradigm
- Preview is PRIMARY, code is SECONDARY
- Live thumbnails on cards for visual recognition
- Click elements to inspect code (ElementInspector)
- Monaco editor available in "Kode" tab

### Shelf Layout
- Templates grouped in horizontal shelves (wrapped grid)
- Default grouping: Channel (PDF, Email, SMS)
- Filtering dims non-matching cards (doesn't hide)

### Flettekode System
- Merge fields: `[[field.name]]` or `[[*field.name]]` (required)
- Conditions: `vitec-if="expression"`
- Loops: `vitec-foreach="item in collection"`
- Auto-discovery scans existing templates
- Visual code generator for non-coders

### Vitec Integration (V2.9)
- Full Vitec Stilark compliance in sanitizer
- Headers/footers/signatures as layout partials
- WebDAV storage for network file access
- Template inventory tracking vs Vitec registry

## DATABASE STATUS
- **Platform:** Railway PostgreSQL
- **Templates:** 44
- **Categories:** 11
- **Connection:** ✅ Verified

## DEPLOYMENT

### Railway Services
| Service | Branch | Purpose |
|---------|--------|---------|
| proaktiv-dokument-hub | main | Backend (FastAPI) |
| blissful-quietude | main | Frontend (Next.js) |
| PostgreSQL | - | Database |

### Environment Variables (Backend)
| Variable | Purpose |
|----------|---------|
| `DATABASE_URL` | PostgreSQL connection string |
| `SECRET_KEY` | JWT signing key (32+ chars) |
| `APP_PASSWORD_HASH` | bcrypt hash for app password (enables auth) |
| `WEBDAV_URL` | WebDAV server URL (`http://proaktiv.no/d/`) |
| `WEBDAV_USERNAME` | WebDAV login |
| `WEBDAV_PASSWORD` | WebDAV password |

### Environment Variables (Frontend)
| Variable | Purpose |
|----------|---------|
| `BACKEND_URL` | Backend API URL for Next.js rewrites |
| `NEXT_PUBLIC_API_URL` | Backend API URL for client-side calls |

### Deploy Process
1. Push to `main` branch
2. Railway auto-deploys both services
3. Migrations run automatically via start-prod.sh

## NEXT STEPS (V3.1)

### Specs Completed
- ✅ Backend Spec: `.cursor/specs/backend_spec.md` (2026-01-17)
- ✅ Frontend Spec: `.cursor/specs/frontend_spec.md` (2026-01-17)
- ✅ Builder: Implementation complete (2026-01-18)

### V3.0 Verification (Immediate)
1. [ ] **Verify Database**: Ensure all tables created and relations working.
2. [ ] **Verify Seeding**: Run `seed_vitec_categories.py` and check results.
3. [ ] **Verify UI**: Test Office/Employee CRUD manually.
4. [ ] **Territory Map**: Validate postal code sync and map rendering.

### V3.0 Features (Implemented - Ready for QA)
1. [x] Seed 97 Vitec categories with vitec_id
2. [x] Office model + CRUD + UI
3. [x] Employee model + lifecycle + UI  
4. [x] Company Assets with scoping
5. [x] External Listings (third-party tracking)
6. [x] Checklists (onboarding/offboarding)
7. [x] Territory Map (postal code heatmap)
8. [x] System template versioning + defaults
9. [ ] (Deferred) Bulk operations for templates
10. [ ] (Deferred) Template version history UI

### Future Features
- [ ] Custom domain setup (dokumenthub.proaktiv.no)
- [ ] Visual builder with TipTap integration
- [ ] Advanced search and filtering
