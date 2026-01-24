# CLAUDE.md

## Project: Vitec Next Admin Hub (Proaktiv Dokument Hub)

A document template management system for Norwegian real estate brokers, integrated with Vitec Next.

---

## Quick Context

| Aspect | Details |
|--------|---------|
| **Phase** | 3.7 (UPN Mismatch Detection) |
| **Stack** | Next.js 16 + React 19 + FastAPI + PostgreSQL (Railway) |
| **UI** | Shadcn/UI + Tailwind CSS 4 + Custom Design Tokens |
| **Hosting** | Vercel (Frontend) + Railway (Backend + PostgreSQL) |
| **Storage** | WebDAV (proaktiv.no/d/) |
| **Auth** | Password + JWT sessions (7-day expiry) |
| **CI/CD** | GitHub Actions (lint, typecheck, test, build) |
| **Monitoring** | Sentry (frontend + backend) |
| **Status** | ✅ Production Live |

---

## Core Concepts

### Document-First Paradigm
- **Preview is PRIMARY**, code is SECONDARY
- Users see rendered documents, not code
- Click elements to inspect underlying HTML (ElementInspector)
- Code editing is a power-user escape hatch, not the default

### Shelf Layout
- Templates displayed as cards in horizontal shelves
- Default grouping: **Channel** (PDF, Email, SMS)
- Filtering **dims** non-matching cards (opacity 0.3), doesn't hide them
- **Live document preview thumbnails** on cards for visual recognition

### Template Viewer Features (V2.6+)
- **A4 Page Break Visualization** - Toggle to see where pages break
- **Simulator Test Data Persistence** - Save default test values to localStorage
- **Quick Test Data Toggle** - Switch between original and processed content
- **Visual Code Generator** - Build Vitec snippets without coding

### Flettekoder (Merge Fields)
- Syntax: `[[field.name]]` or `[[*field.name]]` (with asterisk for required)
- Conditions: `vitec-if="expression"`
- Loops: `vitec-foreach="item in collection"`
- All operations through `MergeFieldService`

### Vitec Integration (V2.9)
- Full reference in `.cursor/vitec-reference.md`
- SanitizerService enforces Vitec Stilark compliance
- Layout partials for headers/footers/signatures
- WebDAV storage for network file access
- Vitec export + import workflow docs in `docs/`

### Authentication (V2.9)
- Simple password-based authentication (single user)
- JWT session tokens with 7-day expiry stored in `session` cookie
- Auth middleware protects all `/api/*` routes
- Login page at `/login`
- Logout button in header
- **Disabled by default** - set `APP_PASSWORD_HASH` to enable
- Generate hash: `python backend/scripts/generate_password_hash.py`

### API Proxy Architecture (Critical)
- Frontend makes API calls to `/api/*` (relative URLs)
- Vercel rewrites `/api/*` → `https://proaktiv-admin.up.railway.app/api/*`
- This keeps session cookies **first-party** (same origin)
- **Never use direct Railway URLs from frontend** - browsers block third-party cookies
- See `frontend/vercel.json` for rewrite rules and `frontend/src/lib/api/config.ts` for URL handling

---

## Key Directories

```
.planning/               # Project planning (source of truth)
├── STATE.md             # Current position and progress
├── ROADMAP.md           # Phase breakdown
├── PROJECT.md           # Requirements and context
├── codebase/            # Technical docs (STACK.md, TESTING.md)
└── phases/              # Active and completed phase plans

.cursor/                 # Agent resources
├── agents/              # Agent prompts (architect, builder)
├── specs/               # Generated specifications
├── commands/            # Slash commands
├── skills/              # Reusable skill modules
└── vitec-reference.md   # Vitec Next API reference

backend/
├── app/
│   ├── models/      # SQLAlchemy models
│   ├── services/    # Business logic (async)
│   │   ├── sanitizer_service.py   # Vitec Stilark compliance
│   │   ├── webdav_service.py      # WebDAV client
│   │   ├── inventory_service.py   # Template sync stats
│   │   └── image_service.py       # Avatar resizing/cropping
│   ├── routers/     # FastAPI endpoints
│   └── schemas/     # Pydantic models

frontend/
├── src/
│   ├── app/         # Next.js pages
│   │   ├── assets/  # Mediefiler page (logos, global assets)
│   │   ├── storage/ # WebDAV browser page
│   │   └── portal/  # Portal skins preview page
│   ├── components/  # React components
│   │   ├── assets/  # Asset gallery, LogoLibrary
│   │   ├── storage/ # Storage browser components
│   │   └── portal/  # Portal mockup components
│   ├── hooks/       # Custom hooks
│   ├── lib/         # API wrapper, utilities
│   │   └── api/config.ts  # resolveApiUrl, resolveAvatarUrl
│   └── types/       # TypeScript interfaces

skins/                    # Vitec portal skin packages
├── proaktiv-bud/         # Budportal skin files
│   ├── PROAKTIV.scss     # Source SCSS
│   ├── PROAKTIV.css      # Compiled CSS
│   ├── PROAKTIV.min.css  # Minified CSS
│   └── PROAKTIV.json     # Portal configuration
├── proaktiv-visning/     # Visningsportal skin files
│   ├── PROAKTIV.scss/css/min.css/json
│   ├── email_*.txt       # Email templates
│   ├── sms_*.txt         # SMS templates
│   └── blacklist.json    # Blocked domains
├── .specs/               # Skin specifications
│   ├── SKIN-SPEC.md      # Design spec document
│   └── QA-REPORT.md      # QA validation report
├── PROAKTIV-bud.zip      # Deployment package
└── PROAKTIV-visning.zip  # Deployment package
```

---

## Patterns to Follow

### Backend
- Business logic in `services/`, never in routers
- All services must be `async`
- Use `Depends()` for dependency injection
- UUID for all primary keys
- JSONB for array/object fields
- Pydantic for all data validation

### Frontend
- Server Components by default
- `"use client"` only when hooks needed
- Use `lib/api.ts` for all API calls
- Prefer Shadcn components over custom
- No `any` in TypeScript
- **Follow `.planning/codebase/DESIGN-SYSTEM.md`** for all UI work

### Component Naming
- Viewer components: `*Frame.tsx` (A4Frame, SMSFrame)
- Library components: `*Library.tsx`, `*Card.tsx`
- Inspector: `ElementInspector.tsx`
- Storage components: `StorageBrowser.tsx`, `ImportToLibraryDialog.tsx`

### Design System (Critical)

**⚠️ BEFORE any frontend work, READ `.planning/codebase/DESIGN-SYSTEM.md`**

- **Use design tokens** — Never hardcode shadows, transitions, colors
- **Cards**: `shadow-card` base, `shadow-card-hover` + `hover:-translate-y-0.5` on hover
- **Selection**: `ring-strong` + `shadow-glow` (bronze accent)
- **Typography**: Serif (`font-serif`) for headings, sans for body
- **Transitions**: Always use `duration-*` and `ease-standard`
- **Colors**: Navy `#272630`, Bronze `#BCAB8A`, Beige `#E9E7DC`
- Rule file: `.cursor/rules/frontend-design.mdc` (auto-applies to frontend files)

---

## Current Status

See `.planning/STATE.md` for full status.

**V3.7 UPN Mismatch Detection (Completed 2026-01-24):**
- ✅ Detect employees with Entra ID UPN different from Vitec Next email
- ✅ `entra_upn` and `entra_upn_mismatch` fields added to Employee model
- ✅ EmployeeCard shows red warning banner for affected employees
- ✅ Detection scripts: `check_upn_mismatch.py` (Python), `Check-UPNMismatch.ps1` (PowerShell)
- ✅ Scripts query Graph API, compare UPN with DB email, update flags
- Note: Currently on QA system; flags persist until production switch

**V3.6 Design System Enhancement (Completed 2026-01-23):**
- ✅ Comprehensive design token system (shadows, transitions, colors)
- ✅ Brand-aligned UI with premium feel
- ✅ Micro-interactions (avatar scale, chevron rotation, shimmer)
- ✅ Consistent card hover patterns across all components
- ✅ Bronze accent for selection states and focus rings
- ✅ Typography hierarchy with serif headings
- Design Guide: `.planning/codebase/DESIGN-SYSTEM.md`

**V3.5 Navigation & Logo Library (Completed 2026-01-23):**
- ✅ Reorganized navigation into **Ressurser** (files/docs) and **Selskap** (HR/org)
- ✅ Added **LogoLibrary** component with Proaktiv logos preview and copy URL
- ✅ Server-side image resizing with `ImageService` for employee avatars
- ✅ New `resolveAvatarUrl()` helper for proper avatar cropping
- ✅ Sub-offices display on office cards and detail pages

**Phase 06: Entra ID Signature Sync (Profile Sync Complete):**
- ✅ Microsoft Graph authentication works
- ✅ Sync employee profiles to Entra ID (jobTitle, department, officeLocation)
- ✅ Photo upload ready (script complete)
- ⏸️ Exchange Online signatures on hold (requires certificate auth)
- QA verified: 2026-01-23 dry-run successful
- Plans: `.planning/phases/06-entra-signature-sync/`
- Commands: `/entra-sync` (usage docs)

**V3.4 Portal Skins Preview (Completed 2026-01-23):**
- ✅ Vitec Budportal and Visningsportal skin packages created
- ✅ PROAKTIV skin with company branding (colors, fonts, privacy URLs)
- ✅ Authentic mockup preview using exact Vitec HTML structure
- ✅ Fullscreen preview mode for accurate representation
- ✅ Voss office mode toggle (financing option enabled)
- ✅ Consent options: Verdivurdering ✓, Budvarsel ✓, Newsletter ✗, Finansiering (Voss only)
- ✅ Navigation: Verktøy → Portal Skins
- Files: `skins/proaktiv-bud/`, `skins/proaktiv-visning/`, `skins/*.zip`
- Preview: `/portal/preview`

**V3.3 API Proxy Fix (Completed 2026-01-23):**
- ✅ Fixed 401 Unauthorized errors on all authenticated API endpoints
- ✅ Frontend now uses relative URLs (`/api/*`) for all API calls
- ✅ Vercel rewrites proxy requests to Railway backend
- ✅ Session cookies now first-party (same-origin), avoiding browser blocking
- ✅ Removed direct Railway URL usage from `frontend/src/lib/api/config.ts`

**V3.2 Stack Upgrade + CI/CD (Completed 2026-01-22):**
- ✅ Next.js 14 → 16.1.4 upgrade
- ✅ React 18 → 19.2.3 upgrade
- ✅ Tailwind CSS 3 → 4.1.18 upgrade
- ✅ TypeScript 5.3 → 5.9.3 upgrade
- ✅ SQLAlchemy 2.0.25 → 2.0.46 upgrade
- ✅ GitHub Actions CI/CD pipeline
  - Frontend: ESLint + TypeScript + Vitest
  - Backend: Ruff + Pyright + Pytest
- ✅ Testing infrastructure
  - Vitest for frontend (4 tests)
  - Pytest + pytest-asyncio for backend (10 tests, 3 xfail)
- ✅ Sentry error tracking (frontend + backend)
- ✅ CVE-2025-29927 security vulnerability fixed

**V3.1 Office & Employee Hub (Completed):**
- ✅ Office management with banner images and employee avatars
- ✅ Employee profile pictures with circular avatars (Radix UI)
- ✅ Office cards with background images from `profile_image_url`
- ✅ Clickable employee avatars on office cards (up to 6) and detail pages (up to 12)
- ✅ Improved color scheme (emerald/sky instead of harsh blues)
- ✅ Banner images on office detail pages with gradient overlays
- ✅ 6 offices and 23 employees imported from proaktiv.no
- ✅ Consistent employee page layout with 256px sidebar
- ✅ Shortened office names (removed "Proaktiv Eiendomsmegling" prefix)
- ✅ **Proaktiv Directory Scraper** - Automated tool to sync offices/employees from proaktiv.no
  - One-command launcher: `run-proaktiv-scraper.bat`
  - PowerShell runner with Local/Railway DB support
  - Bounded crawling with safety limits
  - Upserts offices (by `homepage_url`) and employees (by `email`)
  - Documentation: `docs/proaktiv-directory-sync.md`
  - Command: `/scrape-proaktiv` (see `.cursor/commands/scrape-proaktiv.md`)

**V2.9 Vitec Integration (Completed):**
- ✅ Full Vitec reference documentation
- ✅ Enhanced SanitizerService with Vitec Stilark compliance
- ✅ WebDAV storage integration
- ✅ Storage browser UI
- ✅ Layout partials for headers/footers/signatures
- ✅ Password authentication system
- ✅ Login page with JWT sessions
- ✅ Railway CLI integration
- ✅ Alembic migration auto-repair in start-prod.sh

**V2.8 Railway Migration (Completed):**
- ✅ Migrated from Azure to Railway
- ✅ 44 templates stored in PostgreSQL database
- ✅ 11 categories seeded
- ✅ Backend on Railway, Frontend moved to Vercel
- ✅ Deploys from `main` branch

**V2.6-2.7 Features:**
- ✅ Live document preview thumbnails on template cards
- ✅ A4 page break visualization in document viewer
- ✅ Simulator test data persistence with save/reset/clear
- ✅ Visual code generator for Vitec snippets
- ✅ 4-tab document viewer (Preview, Code, Settings, Simulator)

---

## Agent Pipeline

Execute in order:

1. **Systems Architect** → `.cursor/specs/backend_spec.md`
2. **Frontend Architect** → `.cursor/specs/frontend_spec.md`
3. **Builder** → Implementation

Use `/architect`, `/frontend-architect`, `/builder` commands.

### Entra ID Sync Pipeline (Phase 06)

1. **Script Architect** → `.cursor/specs/entra_sync_spec.md`
2. **Script Builder** → PowerShell implementation
3. **QA** → Test with dry-run

Use `/entra-architect`, `/entra-builder`, `/entra-qa` commands.

---

## Don't

- Use `any` in TypeScript
- Put business logic in routers
- Create components without proper types
- Skip the specs when building
- Use Monaco as the primary view (document preview is primary)
- Hide filtered cards (dim them instead)
- Hardcode colors, shadows, or transitions (use design tokens)
- Use harsh blues for status (use emerald/sky instead)
- Skip hover states on interactive elements
- Use `opacity-50` directly (use `opacity-disabled` token)

---

## Quick Commands

| Command | Purpose |
|---------|---------|
| `/start-dev` | Start Docker environment |
| `/architect` | Run Systems Architect |
| `/frontend-architect` | Run Frontend Architect |
| `/builder` | Run Builder |
| `/status` | Check project status |
| `/scrape-proaktiv` | Run Proaktiv directory scraper |
| `/entra-architect` | Design Entra ID sync script |
| `/entra-builder` | Build Entra ID sync script |
| `/entra-qa` | Test Entra ID sync |
| `/entra-sync` | Run Entra ID sync (usage docs) |

---

## Testing

### Run Tests Locally
```bash
# Frontend
cd frontend
npm run test:run          # Single run
npm run test              # Watch mode

# Backend
cd backend
pytest                    # All tests
pytest -v                 # Verbose
```

### CI/CD Pipeline
Push to `main` triggers GitHub Actions:
1. **Lint Frontend** - ESLint + TypeScript
2. **Lint Backend** - Ruff + Pyright
3. **Test Frontend** - Vitest
4. **Test Backend** - Pytest
5. **Build Frontend** - Next.js production build

---

## Environment

### Local Development
```bash
# Start development
docker compose up -d

# Backend health
curl http://localhost:8000/api/health

# Frontend
http://localhost:3000

# Database
docker compose exec db psql -U postgres -d dokument_hub
```

### Production
- **Frontend (Vercel):** https://proaktiv-dokument-hub.vercel.app
- **Backend (Railway):** https://proaktiv-admin.up.railway.app
- **Deploy:** Push to `main` branch (auto-deploys to both Vercel and Railway)

### Environment Variables (Backend)
| Variable | Value |
|----------|-------|
| `DATABASE_URL` | Railway PostgreSQL **public** URL (use `${{Postgres.DATABASE_PUBLIC_URL}}`) |
| `SECRET_KEY` | Random string (32+ chars) for JWT signing |
| `APP_PASSWORD_HASH` | bcrypt hash - enables auth when set |
| `WEBDAV_URL` | `http://proaktiv.no/d/` |
| `WEBDAV_USERNAME` | (your username) |
| `WEBDAV_PASSWORD` | (your password) |
| `SENTRY_DSN` | Sentry DSN for error tracking (optional) |
| `SENTRY_ENVIRONMENT` | Environment name: `production`, `staging`, etc. |

### Environment Variables (Frontend)
| Variable | Value |
|----------|-------|
| `BACKEND_URL` | `https://proaktiv-admin.up.railway.app` (for Next.js rewrites) |
| `NEXT_PUBLIC_SENTRY_DSN` | Sentry DSN for error tracking (optional) |
| `SENTRY_ORG` | Sentry organization slug (for source maps) |
| `SENTRY_PROJECT` | Sentry project slug (for source maps) |
| `SENTRY_AUTH_TOKEN` | Sentry auth token (for source map upload) |

**IMPORTANT:** Do NOT set `NEXT_PUBLIC_API_URL` in production. The frontend uses relative URLs (`/api/*`) which Vercel rewrites to Railway. This keeps session cookies first-party and avoids third-party cookie blocking.

**IMPORTANT:** The backend's `DATABASE_URL` must use the **public** Postgres URL (`shuttle.proxy.rlwy.net`), not the internal URL (`postgres.railway.internal`). Railway's internal networking between services can be unreliable. Set it to `${{Postgres.DATABASE_PUBLIC_URL}}` in Railway variables.

### Railway CLI (Backend)
```bash
railway link          # Link to backend service
railway variables     # View environment variables
railway redeploy      # Trigger redeploy
railway logs          # View logs
```

### Vercel CLI (Frontend)
```bash
vercel                # Deploy preview
vercel --prod         # Deploy to production
vercel logs           # View logs
```
