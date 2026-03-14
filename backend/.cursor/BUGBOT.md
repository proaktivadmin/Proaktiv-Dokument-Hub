# Bugbot — Backend (FastAPI)

Backend-specific rules for PR reviews. See root `.cursor/BUGBOT.md` for project-wide context.

## Critical (blocking)

- **Business logic in services only** — Never in routers. Routers call services via `Depends()`.
- **Service methods must be async** — All service methods should be `async def`.
- **Use `HTTPException`** — Raise with clear `detail` for expected failures.
- **Pydantic for validation** — Request/response schemas in `backend/app/schemas/`.
- **No `postgres.railway.internal`** — Use public Postgres URL (`shuttle.proxy.rlwy.net`).
- **Prefer `flush()` over `commit()`** — Where project pattern expects session auto-commit.

## Patterns

- UUID primary keys for all models
- JSONB for array/object fields
- Timezone-aware timestamps
- `Depends()` for dependency injection
- Config/settings for env vars — never read `os.environ` directly in business logic

## Migrations

- Create migrations in `backend/alembic/versions/`
- Apply manually to Railway — do not rely on deploy to run `alembic upgrade head`
- See `.cursor/rules/database-migrations.mdc`

## Tests

- Backend changes should include or update tests in `backend/tests/`
- Run: `pytest`, `ruff check .`, `pyright`
