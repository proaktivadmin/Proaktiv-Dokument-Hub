# External Integrations

**Analysis Date:** 2026-01-20

## APIs & External Services

**Vitec Megler Hub:**
- Purpose: Real estate broker platform integration (offices, employees, templates)
- SDK/Client: Custom `VitecHubService` using httpx
- Implementation: `backend/app/services/vitec_hub_service.py`
- Auth: HTTP Basic Auth via Product Login
- Env vars:
  - `VITEC_HUB_BASE_URL` - API endpoint
  - `VITEC_HUB_PRODUCT_LOGIN` - Service account username
  - `VITEC_HUB_ACCESS_KEY` - Service account password
  - `VITEC_ENVIRONMENT` - "qa" or "prod" (derives URL if base not set)
  - `VITEC_INSTALLATION_ID` - Customer installation ID
- Endpoints used:
  - `GET Account/Methods` - List available API methods
  - `GET {installationId}/Departments` - Fetch offices
  - `GET {installationId}/Employees` - Fetch employees

**Microsoft Graph API:**
- Purpose: Teams groups, team membership, email sending via Exchange
- SDK/Client: Custom `MicrosoftGraphClient` using httpx
- Implementation: `backend/app/integrations/microsoft_graph.py`
- Auth: OAuth 2.0 client credentials flow
- Env vars:
  - `MICROSOFT_TENANT_ID` - Azure AD tenant
  - `MICROSOFT_CLIENT_ID` - App registration client ID
  - `MICROSOFT_CLIENT_SECRET` - App registration secret
  - `MICROSOFT_SENDER_EMAIL` - Authorized sender address
- Status: Configured but requires Azure AD app registration

**Firecrawl:**
- Purpose: Web scraping and crawling for external content import
- SDK/Client: `firecrawl-py` (AsyncFirecrawl)
- Implementation: `backend/app/services/firecrawl_service.py`
- Auth: API key
- Env vars:
  - `FIRECRAWL_API_KEY` - API key from Firecrawl
  - `FIRECRAWL_TIMEOUT_MS` - Request timeout (default: 30000)
  - `FIRECRAWL_ONLY_MAIN_CONTENT` - Extract main content only (default: true)
- Features: Markdown/HTML output, metadata extraction, link scraping

**WebDAV Network Storage:**
- Purpose: File storage on network drives (proaktiv.no/d/)
- SDK/Client: Custom `WebDAVService` using httpx with DigestAuth
- Implementation: `backend/app/services/webdav_service.py`
- Auth: HTTP Digest authentication
- Env vars:
  - `WEBDAV_URL` - WebDAV server URL
  - `WEBDAV_USERNAME` - Authentication username
  - `WEBDAV_PASSWORD` - Authentication password
- Operations: PROPFIND, GET, PUT, MKCOL, DELETE, MOVE, COPY
- Status: Currently disabled pending server configuration

## Data Storage

**Primary Database:**
- PostgreSQL 15
- Connection: `DATABASE_URL` environment variable
- Driver: asyncpg (async) / psycopg2 (sync for migrations)
- ORM: SQLAlchemy 2.0 with async sessions
- Implementation: `backend/app/database.py`
- Features:
  - Connection pooling (pool_size=5, max_overflow=10)
  - Async sessions with auto-commit/rollback
  - Supports both PostgreSQL and SQLite

**Development Database:**
- SQLite (aiosqlite driver)
- Auto-creates tables on startup
- No pooling (not needed)

**Database Migrations:**
- Tool: Alembic 1.13.1
- Config: `backend/alembic.ini`
- Scripts: `backend/alembic/`
- Startup command runs `alembic upgrade head`

**File Storage:**
- Template content: Stored in PostgreSQL (migrated from Azure Blob)
- Network storage: WebDAV (proaktiv.no/d/) - optional integration
- Local development: Docker volumes for persistence

**Azure Blob Storage (DEPRECATED):**
- Previously used for template storage
- Env vars still present for rollback compatibility:
  - `AZURE_STORAGE_CONNECTION_STRING`
  - `AZURE_STORAGE_CONTAINER_NAME`
  - `AZURE_CONTAINER_NAME`
  - `AZURE_STORAGE_PREVIEWS_CONTAINER`
- Implementation: `backend/app/services/azure_storage_service.py` (legacy)

**Caching:**
- Redis (optional, not actively used)
- Env var: `REDIS_URL`
- Status: Configuration present but not implemented

## Authentication & Identity

**Primary Auth:**
- Type: Simple password-based (single user)
- Implementation: `backend/app/routers/auth.py`
- Password storage: bcrypt hash in `APP_PASSWORD_HASH` env var
- Session: JWT tokens in httpOnly cookies
- Token config:
  - Algorithm: HS256
  - Signing key: `SECRET_KEY` env var
  - Expiry: 7 days (configurable via `AUTH_SESSION_EXPIRE_DAYS`)

**Auth Middleware:**
- Implementation: `backend/app/middleware/auth.py`
- Activation: Only active when `APP_PASSWORD_HASH` is set
- Protected routes: All `/api/*` except public routes
- Public routes:
  - `/api/auth/login`, `/api/auth/logout`, `/api/auth/status`, `/api/auth/check`
  - `/api/health`, `/health`
  - `/docs`, `/redoc`, `/openapi.json`
  - `/api/sanitize/*` endpoints

**Frontend Auth:**
- Implementation: `frontend/src/lib/api/auth.ts`
- Cookie-based sessions with `withCredentials: true`
- Login page: `/login`
- Logout: Button in header

**Mock Auth (Development):**
- Enabled when `AUTH_ENABLED=false` (default)
- Mock user: `admin@proaktiv.no` / "Admin User"
- Implementation: `backend/app/config.py:get_mock_user()`

## Monitoring & Observability

**Health Check:**
- Endpoint: `GET /api/health`
- Implementation: `backend/app/routers/health.py`
- Docker healthcheck: every 30s, timeout 10s

**Logging:**
- Backend: Python logging module
- Level: Configurable via `LOG_LEVEL` env var
- Format: `%(asctime)s - %(name)s - %(levelname)s - %(message)s`

**Error Tracking:**
- None configured

**Analytics:**
- Internal dashboard stats endpoint
- Implementation: `backend/app/routers/analytics.py`

## CI/CD & Deployment

**Hosting Platform:**
- Railway
- Services: Frontend, Backend, PostgreSQL (addon)

**Deployment:**
- Trigger: Push to `main` branch
- Build: Docker images from Dockerfiles
- No explicit CI pipeline file detected

**Dockerfiles:**
- Frontend: `frontend/Dockerfile` - Multi-stage Node 20 Alpine
- Backend: `backend/Dockerfile` - Python 3.11 slim

**Railway Configuration:**
- Frontend builds from `frontend/Dockerfile`
- Backend builds from `backend/Dockerfile`
- Environment variables set in Railway dashboard

## Environment Configuration

**Required Environment Variables (Production):**
- `DATABASE_URL` - PostgreSQL connection string
- `SECRET_KEY` - JWT signing (32+ chars recommended)
- `APP_PASSWORD_HASH` - bcrypt hash to enable authentication

**Optional Environment Variables:**
- `VITEC_HUB_*` - Vitec integration
- `MICROSOFT_*` - Microsoft Graph integration
- `FIRECRAWL_API_KEY` - Web scraping
- `WEBDAV_*` - Network storage
- `REDIS_URL` - Caching (not used)

**Secrets Management:**
- Railway environment variables (production)
- `.env` files (development, not committed)
- No external secrets manager (Key Vault deprecated)

## Webhooks & Callbacks

**Incoming Webhooks:**
- None detected

**Outgoing Webhooks:**
- None detected

## API Communication Patterns

**Frontend to Backend:**
- HTTP client: Axios
- Base URL: Dynamic via `getApiBaseUrl()` in `frontend/src/lib/api/config.ts`
- Proxy: Next.js rewrites `/api/*` to `BACKEND_URL/api/*`
- Auth: Cookies with `withCredentials: true`

**Backend to External:**
- HTTP client: httpx (async)
- Auth patterns:
  - HTTP Basic (Vitec Hub)
  - OAuth 2.0 client credentials (Microsoft Graph)
  - API key (Firecrawl)
  - HTTP Digest (WebDAV)

**CORS Configuration:**
- Allowed origins include:
  - `http://localhost:3000`, `http://localhost:3001`
  - `https://dokumenthub.proaktiv.no`
  - Railway URLs

---

*Integration audit: 2026-01-20*
