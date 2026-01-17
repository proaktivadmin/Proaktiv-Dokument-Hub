# ACTIVE CONTEXT & ROADMAP

## PROJECT STATUS
- **Phase:** 2.9 (Vitec Integration)
- **Current Sprint:** V2.9 - Vitec Integration & WebDAV Storage
- **Architecture:** Document-first, shelf grouping, 4-tab viewer
- **Last Milestone:** ✅ Railway Migration (2026-01-17)
- **Current Milestone:** Vitec Integration & WebDAV Storage

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

### Pending Configuration
- ⏳ WebDAV URL needs `/d/` path: `http://proaktiv.no/d/`
- ⏳ Waiting for Railway redeploy with correct WebDAV config

### New Files Created
| File | Purpose |
|------|---------|
| `backend/app/services/webdav_service.py` | WebDAV client wrapper |
| `backend/app/routers/storage.py` | Storage API endpoints |
| `backend/app/services/inventory_service.py` | Vitec template sync stats |
| `frontend/src/app/storage/page.tsx` | Storage browser page |
| `frontend/src/components/storage/` | Storage UI components |
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
| `WEBDAV_URL` | WebDAV server URL (`http://proaktiv.no/d/`) |
| `WEBDAV_USERNAME` | WebDAV login |
| `WEBDAV_PASSWORD` | WebDAV password |

### Deploy Process
1. Push to `main` branch
2. Railway auto-deploys both services
3. Migrations run automatically via start-prod.sh

## NEXT STEPS (V2.9+)

### Immediate
- [ ] Verify WebDAV connection with correct URL path
- [ ] Test storage browser functionality
- [ ] Seed Vitec merge fields to database

### Future Features
- [ ] Custom domain setup (dokumenthub.proaktiv.no)
- [ ] Template versioning UI (view/restore previous versions)
- [ ] Visual builder with TipTap integration
- [ ] Bulk template operations
- [ ] Advanced search and filtering
