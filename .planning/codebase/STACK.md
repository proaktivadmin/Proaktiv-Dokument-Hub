# Technology Stack

**Analysis Date:** 2026-01-20

## Languages

**Primary:**
- TypeScript 5.3.3 - Frontend (Next.js, React components)
- Python 3.11 - Backend (FastAPI)

**Secondary:**
- SQL - Database queries and migrations (via SQLAlchemy/Alembic)

## Runtime

**Frontend:**
- Node.js 20 (Alpine in Docker)
- Package Manager: npm
- Lockfile: `frontend/package-lock.json` (present)

**Backend:**
- Python 3.11 (slim in Docker)
- Package Manager: pip
- Requirements: `backend/requirements.txt`

## Frameworks

**Frontend Core:**
- Next.js 14.1.0 - React framework with App Router
- React 18.2.0 - UI library
- React DOM 18.2.0 - DOM rendering

**Frontend UI:**
- Tailwind CSS 3.4.1 - Utility-first CSS
- Shadcn/UI - Component library (Radix UI primitives)
- Radix UI - Headless UI components (@radix-ui/react-*)
- Lucide React 0.312.0 - Icon library
- tailwindcss-animate 1.0.7 - Animation utilities

**Backend Core:**
- FastAPI 0.109.0 - Async Python web framework
- Uvicorn 0.27.0 - ASGI server
- Pydantic 2.5.3 - Data validation
- Pydantic Settings 2.1.0 - Configuration management

**Database:**
- SQLAlchemy 2.0.25 - ORM with async support
- Asyncpg 0.29.0 - PostgreSQL async driver
- Psycopg2-binary 2.9.9 - PostgreSQL sync driver
- Aiosqlite 0.19.0 - SQLite async driver (dev/fallback)
- Alembic 1.13.1 - Database migrations

**Testing:**
- ESLint 8.56.0 - JavaScript/TypeScript linting
- eslint-config-next 14.1.0 - Next.js ESLint config

**Build/Dev:**
- PostCSS 8.4.33 - CSS processing
- Autoprefixer 10.4.17 - CSS vendor prefixing
- Docker / Docker Compose - Containerization

## Key Dependencies

**Frontend Critical:**
- axios 1.6.5 - HTTP client for API calls
- zustand 4.4.7 - State management
- zod 3.22.4 - Schema validation
- react-hook-form 7.49.3 - Form handling
- @hookform/resolvers 3.3.4 - Zod integration for forms
- @monaco-editor/react 4.7.0 - Code editor for template editing
- react-dropzone 14.2.3 - File upload drag-and-drop
- date-fns 3.2.0 - Date utilities

**Frontend UI Primitives (Shadcn/Radix):**
- @radix-ui/react-dialog 1.0.5
- @radix-ui/react-dropdown-menu 2.0.6
- @radix-ui/react-select 2.0.0
- @radix-ui/react-tabs 1.1.13
- @radix-ui/react-toast 1.1.5
- @radix-ui/react-alert-dialog 1.1.15
- @radix-ui/react-checkbox 1.0.4
- @radix-ui/react-scroll-area 1.2.10
- @radix-ui/react-separator 1.1.8
- class-variance-authority 0.7.0
- clsx 2.1.0
- tailwind-merge 2.2.0

**Backend Critical:**
- httpx 0.26.0 - Async HTTP client
- python-jose[cryptography] 3.3.0 - JWT handling
- bcrypt 4.1.2 - Password hashing
- python-multipart 0.0.6 - File uploads
- beautifulsoup4 4.12.3 - HTML parsing
- lxml 5.1.0 - XML/HTML processing
- firecrawl-py 4.11.1 - Web scraping

**Utilities:**
- python-dateutil 2.8.2 - Date utilities

## Configuration

**Frontend Configuration Files:**
- `frontend/next.config.js` - Next.js config with API rewrites
- `frontend/tailwind.config.ts` - Tailwind with Shadcn theme
- `frontend/postcss.config.js` - PostCSS plugins
- `frontend/tsconfig.json` - TypeScript config (strict mode, path aliases)

**Backend Configuration Files:**
- `backend/app/config.py` - Pydantic settings with env validation
- `backend/alembic.ini` - Database migration config
- `backend/.env` - Environment variables (local)

**Environment Variables (Backend):**
- `DATABASE_URL` - PostgreSQL connection string
- `SECRET_KEY` - JWT signing key (required in production)
- `APP_PASSWORD_HASH` - bcrypt hash to enable auth
- `AUTH_SESSION_EXPIRE_DAYS` - Session duration (default: 7)
- `WEBDAV_URL`, `WEBDAV_USERNAME`, `WEBDAV_PASSWORD` - WebDAV storage
- `VITEC_*` - Vitec API integration settings
- `MICROSOFT_*` - Microsoft Graph API settings
- `FIRECRAWL_API_KEY` - Web scraping service

**Environment Variables (Frontend):**
- `NEXT_PUBLIC_API_URL` - Backend URL (optional, uses rewrites)
- `BACKEND_URL` - Backend URL for Next.js rewrites

**TypeScript Path Aliases:**
- `@/*` maps to `./src/*`

## Build Configuration

**Frontend Build:**
- Output: standalone (for containerization)
- API proxying via Next.js rewrites to BACKEND_URL

**Backend Build:**
- Docker multi-stage not used (single-stage Python build)
- Non-root user (appuser) in container
- Health check endpoint at `/api/health`

## Platform Requirements

**Development:**
- Docker and Docker Compose
- Node.js 20+ (if running frontend outside Docker)
- Python 3.11+ (if running backend outside Docker)
- PostgreSQL 15 (via Docker or external)

**Production:**
- Railway platform (current deployment)
- PostgreSQL database (Railway addon)
- Environment variables configured in Railway

**Docker Services:**
- `db` - PostgreSQL 15 Alpine (port 5432)
- `backend` - FastAPI on Uvicorn (port 8000)
- `frontend` - Next.js (port 3000)

**Production URLs:**
- Frontend: `https://blissful-quietude-production.up.railway.app`
- Backend: `https://proaktiv-dokument-hub-production.up.railway.app`

---

*Stack analysis: 2026-01-20*
