# CLAUDE.md

## Project: Proaktiv Dokument Hub V2.9

A document template management system for Norwegian real estate brokers, integrated with Vitec Next.

---

## Quick Context

| Aspect | Details |
|--------|---------|
| **Phase** | 2.9 (Vitec Integration) |
| **Stack** | Next.js 14 + FastAPI + PostgreSQL (Railway) |
| **UI** | Shadcn/UI + Tailwind CSS |
| **Hosting** | Railway (Frontend + Backend + PostgreSQL) |
| **Storage** | WebDAV (proaktiv.no/d/) |
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

---

## Key Directories

```
.cursor/
├── agents/          # Agent prompts (architect, builder)
├── specs/           # Agent output specs
├── plans/           # Project plans and blueprints
├── commands/        # Slash commands
├── vitec-reference.md  # Full Vitec Next reference
└── active_context.md

backend/
├── app/
│   ├── models/      # SQLAlchemy models
│   ├── services/    # Business logic (async)
│   │   ├── sanitizer_service.py   # Vitec Stilark compliance
│   │   ├── webdav_service.py      # WebDAV client
│   │   └── inventory_service.py   # Template sync stats
│   ├── routers/     # FastAPI endpoints
│   └── schemas/     # Pydantic models

frontend/
├── src/
│   ├── app/         # Next.js pages
│   │   └── storage/ # WebDAV browser page
│   ├── components/  # React components
│   │   └── storage/ # Storage browser components
│   ├── hooks/       # Custom hooks
│   ├── lib/         # API wrapper, utilities
│   └── types/       # TypeScript interfaces
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

### Component Naming
- Viewer components: `*Frame.tsx` (A4Frame, SMSFrame)
- Library components: `*Library.tsx`, `*Card.tsx`
- Inspector: `ElementInspector.tsx`
- Storage components: `StorageBrowser.tsx`, `ImportToLibraryDialog.tsx`

---

## Current Status

See `.cursor/active_context.md` for full status.

**V2.9 Vitec Integration (In Progress):**
- ✅ Full Vitec reference documentation
- ✅ Enhanced SanitizerService with Vitec Stilark compliance
- ✅ WebDAV storage integration
- ✅ Storage browser UI
- ✅ Layout partials for headers/footers/signatures
- ⏳ WebDAV configuration pending (needs `/d/` path)

**V2.8 Railway Migration (Completed):**
- ✅ Migrated from Azure to Railway
- ✅ 44 templates stored in PostgreSQL database
- ✅ 11 categories seeded
- ✅ Frontend and Backend on Railway
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

---

## Don't

- Use `any` in TypeScript
- Put business logic in routers
- Create components without proper types
- Skip the specs when building
- Use Monaco as the primary view (document preview is primary)
- Hide filtered cards (dim them instead)

---

## Quick Commands

| Command | Purpose |
|---------|---------|
| `/start-dev` | Start Docker environment |
| `/architect` | Run Systems Architect |
| `/frontend-architect` | Run Frontend Architect |
| `/builder` | Run Builder |
| `/status` | Check project status |

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

### Production (Railway)
- **Frontend:** https://blissful-quietude-production.up.railway.app
- **Backend:** https://proaktiv-dokument-hub-production.up.railway.app
- **Deploy:** Push to `main` branch

### Environment Variables (Backend)
| Variable | Value |
|----------|-------|
| `DATABASE_URL` | Railway PostgreSQL connection |
| `WEBDAV_URL` | `http://proaktiv.no/d/` |
| `WEBDAV_USERNAME` | (your username) |
| `WEBDAV_PASSWORD` | (your password) |
