# Codebase Structure

**Analysis Date:** 2026-01-20

## Directory Layout

```
Proaktiv-Dokument-Hub/
├── .claude/              # Claude Code settings
├── .cursor/              # Cursor IDE settings, agents, specs, plans
├── .planning/            # GSD planning artifacts
│   └── codebase/         # Codebase analysis documents
├── .github/              # GitHub workflows
├── backend/              # FastAPI Python backend
│   ├── app/              # Application code
│   ├── alembic/          # Database migrations
│   ├── scripts/          # Utility scripts (seeding, imports)
│   ├── tests/            # Backend tests
│   ├── Dockerfile        # Production container
│   └── requirements.txt  # Python dependencies
├── frontend/             # Next.js React frontend
│   ├── src/              # Application source
│   ├── public/           # Static assets
│   ├── Dockerfile        # Production container
│   └── package.json      # Node dependencies
├── api/                  # API documentation/exports
├── data/                 # Data files (templates, imports)
├── docs/                 # Feature documentation
├── library/              # Template library files
├── _legacy_v1/           # Archived v1 code (not in use)
├── docker-compose.yml    # Local development stack
├── CLAUDE.md             # Project instructions for AI
└── README.md             # Project documentation
```

## Directory Purposes

**backend/app/:**
- Purpose: FastAPI application code
- Contains: Main app, config, database setup
- Key files: `main.py`, `config.py`, `database.py`

**backend/app/routers/:**
- Purpose: HTTP endpoint handlers
- Contains: Router modules grouped by domain
- Key files: `templates.py`, `offices.py`, `employees.py`, `auth.py`

**backend/app/services/:**
- Purpose: Business logic layer
- Contains: Service classes with async methods
- Key files: `template_service.py`, `office_service.py`, `sanitizer_service.py`

**backend/app/models/:**
- Purpose: SQLAlchemy ORM definitions
- Contains: Database models with relationships
- Key files: `template.py`, `office.py`, `employee.py`, `base.py`

**backend/app/schemas/:**
- Purpose: Pydantic validation models
- Contains: Request/response DTOs
- Key files: `template.py`, `office.py`, `employee.py`

**backend/app/middleware/:**
- Purpose: Request interceptors
- Contains: Authentication middleware
- Key files: `auth.py`

**backend/alembic/versions/:**
- Purpose: Database migration scripts
- Contains: Versioned schema changes
- Key files: Timestamped migration files (`20251213_*.py`, etc.)

**frontend/src/app/:**
- Purpose: Next.js pages and layouts
- Contains: Route-based page components
- Key files: `page.tsx` (dashboard), `layout.tsx` (root layout)

**frontend/src/components/:**
- Purpose: React UI components
- Contains: Reusable components grouped by domain
- Key files: `ui/*.tsx` (Shadcn), `templates/*.tsx`, `shelf/*.tsx`

**frontend/src/hooks/:**
- Purpose: Custom React hooks
- Contains: Data fetching and state hooks
- Key files: `useCategories.ts`, `useDashboard.ts`, `v2/*.ts`, `v3/*.ts`

**frontend/src/lib/:**
- Purpose: Utility libraries and API clients
- Contains: API wrappers, helpers
- Key files: `api.ts`, `api/*.ts`, `utils.ts`

**frontend/src/types/:**
- Purpose: TypeScript type definitions
- Contains: Shared interfaces and types
- Key files: `index.ts`, `v2.ts`, `v3.ts`

## Key File Locations

**Entry Points:**
- `backend/app/main.py`: FastAPI app initialization
- `frontend/src/app/layout.tsx`: Next.js root layout
- `frontend/src/app/page.tsx`: Dashboard home page

**Configuration:**
- `backend/app/config.py`: Backend settings (Pydantic)
- `frontend/src/lib/api/config.ts`: API client configuration
- `docker-compose.yml`: Local development services
- `backend/alembic/alembic.ini`: Migration settings

**Core Business Logic:**
- `backend/app/services/template_service.py`: Template CRUD
- `backend/app/services/sanitizer_service.py`: HTML sanitization for Vitec
- `backend/app/services/office_service.py`: Office management
- `backend/app/services/employee_service.py`: Employee management

**API Clients:**
- `frontend/src/lib/api.ts`: Main API client (templates, categories)
- `frontend/src/lib/api/index.ts`: API barrel export
- `frontend/src/lib/api/offices.ts`: Office API
- `frontend/src/lib/api/employees.ts`: Employee API

**Database Models:**
- `backend/app/models/base.py`: Base model with cross-DB types
- `backend/app/models/template.py`: Template + TemplateVersion
- `backend/app/models/office.py`: Office entity
- `backend/app/models/employee.py`: Employee entity

**Testing:**
- `backend/tests/`: Backend test files
- `backend/tests/test_vitec_normalizer_service.py`: Service tests

## Naming Conventions

**Files:**
- Backend Python: `snake_case.py`
- Frontend TypeScript: `kebab-case.ts` or `PascalCase.tsx` for components
- Config files: lowercase with dots (`.env`, `next.config.ts`)

**Components:**
- Page components: `page.tsx` (Next.js convention)
- UI components: `PascalCase.tsx` (e.g., `Button.tsx`)
- Hooks: `useCamelCase.ts` (e.g., `useCategories.ts`)

**Backend:**
- Routers: `plural_noun.py` (e.g., `templates.py`, `offices.py`)
- Services: `noun_service.py` (e.g., `template_service.py`)
- Models: `singular_noun.py` (e.g., `template.py`, `office.py`)
- Schemas: Match model names (e.g., `template.py`)

**Database:**
- Tables: `plural_snake_case` (e.g., `templates`, `offices`)
- Columns: `snake_case` (e.g., `created_at`, `file_name`)
- Junction tables: `singular_singular` (e.g., `template_tags`)

## Where to Add New Code

**New API Endpoint:**
- Router: `backend/app/routers/{domain}.py`
- Service: `backend/app/services/{domain}_service.py`
- Schema: `backend/app/schemas/{domain}.py`
- Register in: `backend/app/main.py` (include_router)

**New Database Table:**
- Model: `backend/app/models/{entity}.py`
- Migration: Run `alembic revision --autogenerate -m "description"`
- Import in: `backend/app/models/__init__.py`

**New Frontend Page:**
- Page: `frontend/src/app/{route}/page.tsx`
- Dynamic: `frontend/src/app/{route}/[param]/page.tsx`

**New React Component:**
- Domain-specific: `frontend/src/components/{domain}/{ComponentName}.tsx`
- Shared UI: `frontend/src/components/ui/{component}.tsx` (Shadcn style)
- Add barrel export: `frontend/src/components/{domain}/index.ts`

**New Custom Hook:**
- Location: `frontend/src/hooks/{useHookName}.ts`
- V2 features: `frontend/src/hooks/v2/{useHookName}.ts`
- V3 features: `frontend/src/hooks/v3/{useHookName}.ts`

**New API Client:**
- Location: `frontend/src/lib/api/{domain}.ts`
- Export from: `frontend/src/lib/api/index.ts`

**New TypeScript Type:**
- Core types: `frontend/src/types/index.ts`
- V2 types: `frontend/src/types/v2.ts` or `frontend/src/types/v2/{domain}.ts`
- V3 types: `frontend/src/types/v3.ts`

**Utilities:**
- Backend: `backend/app/utils/{util_name}.py`
- Frontend: `frontend/src/lib/{util_name}.ts`

## Special Directories

**.cursor/:**
- Purpose: Cursor IDE configuration, AI agent prompts
- Generated: Partially (agents are manual)
- Committed: Yes

**.planning/:**
- Purpose: GSD planning and analysis documents
- Generated: Yes (by GSD commands)
- Committed: Yes

**_legacy_v1/:**
- Purpose: Archived code from v1
- Generated: No
- Committed: Yes (for reference)

**backend/.venv/ and frontend/node_modules/:**
- Purpose: Language dependencies
- Generated: Yes
- Committed: No (in .gitignore)

**frontend/.next/:**
- Purpose: Next.js build output
- Generated: Yes
- Committed: No (in .gitignore)

**backend/alembic/versions/:**
- Purpose: Database migration history
- Generated: Yes (by alembic)
- Committed: Yes (required for deployments)

---

*Structure analysis: 2026-01-20*
