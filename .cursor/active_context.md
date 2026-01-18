# ACTIVE CONTEXT & ROADMAP

## 2026-01-18 (LATEST UPDATES) — FRONTEND / UX / NAV

### Shipped Today ✅
- ✅ **Rebrand**: App is now **Vitec Next Admin Hub** (header, login, metadata, backend `APP_NAME`)
- ✅ **Logo**: Lily mark (same as favicon) rendered in `#272630` via CSS mask in header + login
- ✅ **Navigation cleanup**
  - **Dokumenter** dropdown: Maler, Kategorier, Mottakere
  - **Selskap** dropdown: Kontorer, Ansatte, **Filer**, **Markedsområder**
- ✅ **Clickable linking**
  - Categories and receiver types are clickable and deep-link to `/templates` filtered view
  - `/templates` supports `?category=<uuid>` and `?receiver=<name>` with filter chips
- ✅ **Receiver filter support**
  - Backend: `/api/templates?receiver=...` (matches primary + extra receivers, normalizes diacritics)
- ✅ **Edit / New / Upload dialogs**
  - Settings now available from **Rediger** (no need to open template first)
  - “Avanserte innstillinger” in **Ny mal** and **Last opp fil** uses the same settings UI
- ✅ **Categories icon consistency**
  - Removed emojis, standardized to Lucide icons via `frontend/src/lib/category-icons.ts`
- ✅ **Dashboard polish**
  - Cleaner top (removed “Dashboard” heading/description)
  - Neutral palette for cards/icons/tags; “archived” translated to **Arkivert**
- ✅ **Markedsområder page added**: `/territories`
  - Stats + layer toggles + placeholder map (real heatmap pending geometry dataset)
- ✅ **Postal code sync (Bring)**
  - Script added: `backend/scripts/sync_postal_codes.py`
  - Existing endpoint: `POST /api/postal-codes/sync` (yearly manual update)

### Known Gaps / Caveats ⚠️
- **Territory heatmap**: backend currently returns placeholder geometry; real map needs postal-code polygons dataset
- **Local Windows venv**: `pip install -r backend/requirements.txt` may fail if Python version lacks `psycopg2-binary` wheels; easiest is running scripts inside Docker

### “Next Agent” — Append Below ⬇️
<!-- NEXT_AGENT_NOTES_START -->

<!-- (leave space for next agent’s updates) -->

<!-- NEXT_AGENT_NOTES_END -->

## PROJECT STATUS
- **Phase:** 3.0 (Office & Employee Hub)
- **Current Sprint:** V3.0 Full Feature Implementation
- **Architecture:** Document-first, shelf grouping, 4-tab viewer
- **Last Milestone:** ✅ V2.9 Vitec Integration Complete (2026-01-17)
- **Current Milestone:** V3.0 - Office/Employee Hub, Company Assets, Territory Map
- **Agent Pipeline:** ✅ Backend Spec → ✅ Frontend Spec → ⏳ Builder

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

## NEXT STEPS (V3.0)

### Specs Completed
- ✅ Backend Spec: `.cursor/specs/backend_spec.md` (2026-01-17)
- ✅ Frontend Spec: `.cursor/specs/frontend_spec.md` (2026-01-17)
- ⏳ Builder: Ready to start implementation

### V3.0 Features (In Order)
1. [ ] Seed 97 Vitec categories with vitec_id
2. [ ] Office model + CRUD + UI
3. [ ] Employee model + lifecycle + UI  
4. [ ] Company Assets with scoping
5. [ ] External Listings (third-party tracking)
6. [ ] Checklists (onboarding/offboarding)
7. [ ] Territory Map (postal code heatmap)
8. [ ] System template versioning + defaults
9. [ ] Bulk operations for templates
10. [ ] Template version history UI

### Future Features
- [ ] Custom domain setup (dokumenthub.proaktiv.no)
- [ ] Visual builder with TipTap integration
- [ ] Advanced search and filtering
