# MASTER HANDOFF DOCUMENT
# Vitec Next Admin Hub - Agent Pipeline Context

**Last Updated:** 2026-01-22

**Important:** Large parts of this document are **historical** (Azure/SQLite era).  
For current production + active roadmap, use `.planning/STATE.md` as source of truth.

---

## 0. TODAY UPDATE (2026-01-22) — STACK UPGRADE + CI/CD PIPELINE

### What changed
- **Stack Upgrade Complete** (Phase 4 of roadmap)
  - Next.js 14 → 16.1.4 (skipped 15, went directly to 16)
  - React 18 → 19.2.3
  - Tailwind CSS 3 → 4.1.18
  - TypeScript 5.3 → 5.9.3
  - SQLAlchemy 2.0.25 → 2.0.46
- **CI/CD Pipeline** via GitHub Actions
  - Frontend: ESLint + TypeScript + Vitest
  - Backend: Ruff + Pyright + Pytest
  - Workflow: `.github/workflows/ci.yml`
  - All checks passing on `main`
- **Testing Infrastructure**
  - Vitest configured (`frontend/vitest.config.ts`)
  - Pytest + pytest-asyncio (`backend/pytest.ini`)
  - 14 tests total (11 passing, 3 xfail)
- **GitHub CLI** installed for CI monitoring
- **Sentry** error tracking (frontend + backend)
- **CVE-2025-29927** security vulnerability fixed

### What to verify
- CI passes on all pushes to `main`
- Production build succeeds on Railway
- No runtime regressions from upgrades

### Roadmap Status
| Phase | Status | Completed |
|-------|--------|-----------|
| 1. Vitec API Connection | ✅ Complete | 2026-01-20 |
| 2. Vitec Sync Review UI | 🔄 In Progress | - |
| 3. Social Media Links | Not started | - |
| 4. Stack Upgrade | ✅ Complete | 2026-01-22 |
| 5. Vercel Migration | Not started | - |

---

## PREVIOUS UPDATE (2026-01-18) — TEMPLATE UX + IMPORT + DEPLOY FIXES

### What changed
- **Rebrand** to **Vitec Next Admin Hub**
  - Header + login + Next.js metadata + backend `APP_NAME`
  - Lily logo rendered in `#272630` (CSS mask using `frontend/public/assets/proaktiv-lily-black.png`)
- **Navigation**
  - “Dokumenter” dropdown: Maler, Kategorier, Mottakere
  - “Selskap” dropdown: Kontorer, Ansatte, Filer, **Markedsområder** (`/territories`)
- **Templates discoverability**
  - Categories + receivers are clickable to filtered templates view
  - Added `/api/templates?receiver=...` backend filter (primary + extra receivers)
- **Settings UX**
  - Settings available directly from **Rediger** dialog
  - “Avanserte innstillinger” in **Ny mal** and **Last opp fil**
- **Dashboard polish**
  - Removed “Dashboard” heading/description
  - Neutral palette for cards/icons/status tags; translate archived → **Arkivert**
- **New pages**
  - `/mottakere` (receiver list)
  - `/territories` (market area overview; map/heatmap placeholder pending geometry dataset)
- **Postal codes sync**
  - Script: `backend/scripts/sync_postal_codes.py`
  - Existing endpoint: `POST /api/postal-codes/sync`

- **Template workflow parity**
  - Attachments exposed in list + detail responses and shown in UI (paperclip count + names)
  - List view grouped by origin (**Vitec Next** vs **Kundemal**) and pagination fixed
  - Settings UI expanded with Vitec “Kategorisering” fields (type/receiver/phases/etc.)
- **Vitec Next import tooling**
  - `backend/scripts/import_vitec_next_export.py`
  - `docs/vitec-next-export-format.md`
  - `docs/vitec-next-mcp-scrape-and-import.md`
- **Railway build fixes**
  - Receiver values treated as free-form strings in typing
  - Status filter typing aligned to `TemplateStatus`

### What to verify tomorrow
- `/territories` loads in prod and is visible under **Selskap**
- Template filtering works from category/receiver links
- “Rediger” dialog saves category + advanced settings as expected

### Next agent — append below
<!-- NEXT_AGENT_NOTES_START -->

### AI Signoff (2026-01-18)
- Pushed `068ec02` to `main`; Railway deploy triggered.
- QA fixes landed: `/api/ping`, `/api/territories/stats`, `/employees/email-group` route ordering, template receiver filter hardening, template settings audit JSON serialization, shelf pagination to load all templates.
- Employee UI now supports role filtering + email group action.
- Integrations note: Vitec Next API + Azure/Microsoft stubs remain present but intentionally inactive.

#### Open Items / Follow-ups
- Employee create/update should persist `system_roles` + `sharepoint_folder_url`.
- Email group button should include status filters.
- Normalize role naming (`daglig leder` vs `daglig_leder`) across FE/BE.
- Remove unused `Badge` import in `frontend/src/components/employees/RoleFilter.tsx`.
- Investigate attachment badges showing values like `"0, False"` (metadata cleanup).

<!-- (leave space for next agent’s updates) -->

<!-- NEXT_AGENT_NOTES_END -->

**Purpose:** Comprehensive context for AI agents working on this project

---

## 1. PROJECT STATE SUMMARY (CURRENT)

### What Works
- Frontend UI loads and renders correctly
- Navigation between pages works
- Template shelf view displays templates and supports filtering/grouping
- Template preview with merge field highlighting
- Code editor (Monaco) in template viewer
- Simulator panel detects variables
- Flettekoder page with 142 merge fields
- Railway deploy pipeline (push to `main` deploys frontend + backend)
- PostgreSQL-backed persistence (Railway)

### What Is Broken
- No known production-blocking issues in current `main` deploy.
- Build warnings:
  - Next.js prints a security advisory warning for `next@14.1.0` (plan upgrade window)

---

## 2. CRITICAL FILES LIST

### Infrastructure (Railway)
| File | Purpose |
|------|---------|
| `docker-compose.yml` | Local dev stack (frontend + backend + db) |
| `backend/railway.json` | Railway backend runtime config |
| `backend/Dockerfile` | Backend container image |
| `frontend/Dockerfile` | Frontend container image |
| `backend/scripts/start.sh` | Container startup script |

### Backend (Agent 1 - Systems Architect)
| File | Purpose |
|------|---------|
| `backend/app/main.py` | FastAPI application entry |
| `backend/app/config.py` | Environment configuration |
| `backend/app/database.py` | Database connection |
| `backend/app/models/` | SQLAlchemy models |
| `backend/app/routers/` | API endpoints |
| `backend/app/services/` | Business logic |
| `backend/app/schemas/` | Pydantic schemas |
| `backend/alembic/` | Database migrations |

### Frontend (Agent 2 - Frontend Architect)
| File | Purpose |
|------|---------|
| `frontend/next.config.js` | Next.js config with API rewrites |
| `frontend/src/lib/api.ts` | API client (uses relative URLs) |
| `frontend/src/app/page.tsx` | Dashboard page |
| `frontend/src/app/templates/page.tsx` | Templates shelf view |
| `frontend/src/components/` | React components |
| `frontend/src/hooks/` | Custom React hooks |
| `frontend/src/types/` | TypeScript interfaces |

### Context Files
| File | Purpose |
|------|---------|
| `CLAUDE.md` | Project quick reference |
| `.cursor/active_context.md` | Current phase and status |
| `.cursorrules` | Coding patterns and rules |

---

## 3. KNOWN ISSUES (CURRENT)

- No known production-blocking issues in the current Railway deploy.
- **Warnings to track:**
  - `next@14.1.0` security advisory warning during build (plan upgrade)
  - WebDAV directory listing requires server-side `PROPFIND` enabled (if WebDAV storage is used)

---

## 4. DEPLOYMENT INFORMATION

### URLs
| Service | URL | Status |
|---------|-----|--------|
| Frontend | https://blissful-quietude-production.up.railway.app | Live |
| Backend | https://proaktiv-dokument-hub-production.up.railway.app | Live |
| API Docs | https://proaktiv-dokument-hub-production.up.railway.app/docs | Live |
| Health | https://proaktiv-dokument-hub-production.up.railway.app/api/health | Live |

### GitHub Repository
- **URL:** https://github.com/Adrian12341234-code/Proaktiv-Dokument-Hub
- **Branch:** `main` (triggers Railway auto-deploy)

---

## 5. GITHUB SECRETS

**Note:** Current production is on Railway. Most GitHub “Azure secrets” below are legacy and can be ignored.

---

## 6. TECH STACK

| Layer | Technology | Version |
|-------|------------|---------|
| Frontend | Next.js | 16.1.4 |
| React | React | 19.2.3 |
| UI Components | Shadcn/UI | Latest |
| Styling | Tailwind CSS | 4.1.18 |
| TypeScript | TypeScript | 5.9.3 |
| Backend | FastAPI | 0.109.0 |
| Database | PostgreSQL (Railway) | 15 |
| ORM | SQLAlchemy | 2.0.46 |
| Migrations | Alembic | 1.13.1 |
| Container | Docker | - |
| Cloud | Railway | - |
| CI/CD | GitHub Actions + Railway | - |
| Monitoring | Sentry | - |
| Testing (FE) | Vitest | 4.0.17 |
| Testing (BE) | Pytest | 8.0.0+ |
| Linting (FE) | ESLint | 9.39.2 |
| Linting (BE) | Ruff + Pyright | Latest |

---

## 7. SUCCESS CRITERIA

The deployment is considered "fixed" when ALL of these pass:

- [ ] Backend `/api/health` returns `{"status": "healthy"}`
- [ ] Frontend loads without any error banners
- [ ] Dashboard shows template counts (not 500 error)
- [ ] Template list populates correctly
- [ ] Upload a new template and verify it persists
- [ ] Restart the container and verify data is still there
- [ ] API docs page loads at `/docs`

---

## 8. AGENT PIPELINE

### Execution Order
1. **Azure DevOps Architect** (`/azure-architect`) → Fixes infrastructure
2. **Systems Architect** (`/architect`) → Backend specifications
3. **Frontend Architect** (`/frontend-architect`) → Frontend specifications  
4. **Builder** (`/builder`) → Implementation
5. **Debugger Mode** → QA verification

### Model Recommendations
| Agent | Model | Reason |
|-------|-------|--------|
| Azure DevOps Architect | Claude Opus 4.5 / o1-pro | Complex infrastructure |
| Systems Architect | Claude Opus 4.5 | Backend architecture |
| Frontend Architect | Claude Sonnet 4 | Fast, good at UI |
| Builder | Claude Sonnet 4 | Fast execution |
| Debugger | Claude Opus 4.5 | Deep debugging |

---

## 9. QUICK COMMANDS

```bash
# Local development
docker compose up -d

# Check backend health
curl http://localhost:8000/api/health

# Run migrations locally
docker compose exec backend alembic upgrade head

# View logs
docker compose logs -f backend

# Deploy to production (Railway auto-deploys on push)
git push origin main
```

---

## 10. NOTES FOR AGENTS

### Do NOT:
- Skip reading context files
- Mark issues as "fixed" without verification
- Remove working code to "simplify"
- Add features not in the spec
- Use `any` type in TypeScript
- Put business logic in routers

### DO:
- Read all context files first
- Test each change before moving on
- Document any new issues discovered
- Ask if something is unclear
- Follow existing code patterns
- Keep solutions simple (single-user app)
