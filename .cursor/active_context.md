# ACTIVE CONTEXT & ROADMAP

## PROJECT STATUS
- **Phase:** 2.8 (Railway Migration Complete)
- **Current Sprint:** ✅ COMPLETE
- **Architecture:** Document-first, shelf grouping, 4-tab viewer
- **Last Milestone:** ✅ Railway Migration (2026-01-17)
- **Current Milestone:** Production Live on Railway

## V2.8 RAILWAY MIGRATION (2026-01-17)

### Migration Complete ✅
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

### Changes Made
| File | Changes |
|------|---------|
| `backend/requirements.txt` | Removed azure-storage-blob, azure-identity |
| `backend/app/services/__init__.py` | Removed AzureStorageService |
| `backend/app/main.py` | Removed Azure CORS origins |
| `backend/scripts/start-prod.sh` | Simplified for Railway-only |
| `frontend/next.config.js` | Removed Azure Blob image patterns |
| `frontend/src/lib/api/config.ts` | Removed Azure detection logic |
| `.github/workflows/deploy-azure.yml` | DELETED |
| `infrastructure/bicep/` | DELETED |

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
- Fixed dashboard 500 error (endpoint now exists)
- Includes recent uploads list
- Dashboard now uses real backend data

## V2.6 FEATURES (2026-01-15)

### 1. Live Document Preview Thumbnails
- Template cards show **live document previews** instead of static icons
- Uses IntersectionObserver for **lazy loading**
- 15% scale transform fits full document into thumbnail area

### 2. A4 Page Break Visualization
- Toggle button "Vis A4" / "Skjul A4" in preview toolbar
- Shows **red dashed lines** at A4 page boundaries

### 3. Simulator Test Data Persistence
- Default test data **pre-populated** with common fields
- Save/Reset/Clear buttons for test data management
- Test data survives browser refresh

### 4. Code Generator (Flettekoder Page)
- Visual interface for building Vitec code snippets
- Supports: `vitec-if/else`, `vitec-foreach`, inline conditions

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

### Deploy Process
1. Push to `main` branch
2. Railway auto-deploys both services
3. Migrations run automatically via start-prod.sh

## NEXT STEPS (V2.9+)

### Potential Features
- [ ] Custom domain setup (dokumenthub.proaktiv.no)
- [ ] Template versioning UI (view/restore previous versions)
- [ ] Visual builder with TipTap integration
- [ ] Bulk template operations
- [ ] Advanced search and filtering
- [ ] Add more Vitec Logic patterns to snippets.json
