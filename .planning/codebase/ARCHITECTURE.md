# Architecture

**Analysis Date:** 2026-01-20

## Pattern Overview

**Overall:** Three-tier client-server architecture with REST API

**Key Characteristics:**
- Next.js 14 frontend (React Server Components) with App Router
- FastAPI async Python backend with service layer pattern
- PostgreSQL database with SQLAlchemy ORM (async)
- Clear separation: routers handle HTTP, services handle business logic
- JWT-based session authentication (optional, disabled by default)

## Layers

**Presentation Layer (Frontend):**
- Purpose: User interface and client-side state management
- Location: `frontend/src/`
- Contains: React components, custom hooks, API clients
- Depends on: Backend REST API
- Used by: End users via browser

**API Layer (Routers):**
- Purpose: HTTP request handling, validation, response formatting
- Location: `backend/app/routers/`
- Contains: FastAPI route handlers with Pydantic validation
- Depends on: Services, Schemas
- Used by: Frontend API clients

**Business Logic Layer (Services):**
- Purpose: Core business rules and data operations
- Location: `backend/app/services/`
- Contains: Async service classes with static methods
- Depends on: Models, Database session
- Used by: Routers exclusively

**Data Access Layer (Models):**
- Purpose: Database schema and ORM mappings
- Location: `backend/app/models/`
- Contains: SQLAlchemy ORM models with relationships
- Depends on: SQLAlchemy Base
- Used by: Services

**Schema Layer (DTOs):**
- Purpose: Request/response validation and serialization
- Location: `backend/app/schemas/`
- Contains: Pydantic models for API contracts
- Depends on: Nothing
- Used by: Routers, Services

## Data Flow

**Template CRUD Flow:**

1. Frontend component calls API client (`frontend/src/lib/api.ts`)
2. Axios sends HTTP request to `/api/templates/*`
3. FastAPI router (`backend/app/routers/templates.py`) validates input
4. Router calls service method (`backend/app/services/template_service.py`)
5. Service performs database operations via SQLAlchemy
6. Response flows back: Service -> Router -> Axios -> Component

**State Management:**
- Server state: React hooks with SWR/custom fetching patterns
- Client state: React useState/useContext (no Redux/Zustand)
- Form state: Controlled components
- Auth state: Context provider (`AuthProvider`) with session cookie

**Database Session Flow:**
```
Request -> get_db() dependency -> AsyncSession
    -> Service operations (flush on success)
    -> Automatic commit on request completion
    -> Rollback on exception
    -> Session close
```

## Key Abstractions

**Template:**
- Purpose: Document templates with metadata, content, versioning
- Examples: `backend/app/models/template.py`, `frontend/src/types/index.ts`
- Pattern: Rich domain model with relationships (tags, categories, versions)

**Office/Employee (V3):**
- Purpose: Company organizational structure
- Examples: `backend/app/models/office.py`, `backend/app/models/employee.py`
- Pattern: Hierarchical with Office -> Employee relationship

**API Client:**
- Purpose: Type-safe HTTP communication
- Examples: `frontend/src/lib/api.ts`, `frontend/src/lib/api/*.ts`
- Pattern: Function-based clients with error handling, grouped by domain

**Service:**
- Purpose: Encapsulate business logic
- Examples: `backend/app/services/template_service.py`
- Pattern: Static async methods, accepts db session as first argument

## Entry Points

**Backend:**
- Location: `backend/app/main.py`
- Triggers: Uvicorn server startup
- Responsibilities: FastAPI app creation, middleware setup, router registration, lifespan events (DB init/close)

**Frontend:**
- Location: `frontend/src/app/layout.tsx`
- Triggers: Next.js app initialization
- Responsibilities: Root layout, font loading, AuthProvider wrapper

**API Routes:**
- Location: `backend/app/routers/*.py`
- Triggers: HTTP requests to `/api/*`
- Responsibilities: Request validation, service orchestration, response formatting

**Pages:**
- Location: `frontend/src/app/**/page.tsx`
- Triggers: URL navigation
- Responsibilities: Page rendering, data fetching, layout composition

## Error Handling

**Strategy:** Centralized error handling with specific HTTP status codes

**Backend Patterns:**
- HTTPException for expected errors (404, 400, 422)
- Automatic 500 for unhandled exceptions
- Logging via Python logging module
- Database rollback on exceptions (handled by `get_db()`)

**Frontend Patterns:**
- `handleError()` function in API clients
- AxiosError inspection for detailed messages
- User-friendly Norwegian error messages
- Console logging for debugging

## Cross-Cutting Concerns

**Logging:**
- Backend: Python `logging` module configured in `main.py`
- Frontend: Console logging in development
- Log level configurable via `LOG_LEVEL` env var

**Validation:**
- Backend: Pydantic models in `schemas/` validate all input
- Frontend: TypeScript types provide compile-time checking
- Database: SQLAlchemy constraints for data integrity

**Authentication:**
- JWT session tokens stored in HTTP-only cookies
- Middleware checks `session` cookie on protected routes
- Optional: disabled when `APP_PASSWORD_HASH` not set
- Public routes explicitly allowlisted in `backend/app/middleware/auth.py`

**CORS:**
- Configured in `backend/app/main.py`
- Allows localhost:3000, Railway URLs, production domain
- Credentials enabled for cookie-based auth

**Database Transactions:**
- Automatic transaction per request via `get_db()` dependency
- Flush after operations, commit on success, rollback on error
- No manual transaction management in services

---

*Architecture analysis: 2026-01-20*
