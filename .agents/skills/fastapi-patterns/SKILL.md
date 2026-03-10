---
name: fastapi-patterns
description: FastAPI backend implementation patterns for this project. Use when adding or refactoring routers, services, schemas, dependency injection, and error handling.
---

# FastAPI Patterns

## When to Use

- Add new API endpoints in `backend/app/routers/`
- Add or refactor business logic in `backend/app/services/`
- Add request/response models in `backend/app/schemas/`
- Design API contracts and error handling for backend features

## Core Rules

1. Keep business logic in services, not routers.
2. Routers orchestrate request/response, auth, and dependency wiring only.
3. Use async service methods and async DB paths.
4. Validate all request/response data with Pydantic schemas.
5. Raise explicit HTTP errors with actionable messages.

## Router Pattern

1. Parse and validate input via schema.
2. Inject dependencies with `Depends()`.
3. Call service methods.
4. Map domain errors to stable API responses.

## Service Pattern

1. One service per domain capability.
2. Keep methods cohesive and side effects explicit.
3. Return typed results, not loosely shaped dicts where avoidable.
4. Keep DB operations transactional and predictable.

## Success Checklist

- [ ] Router contains no business logic.
- [ ] Service method contracts are explicit and typed.
- [ ] Request and response schemas are defined.
- [ ] Error paths are covered and predictable.
