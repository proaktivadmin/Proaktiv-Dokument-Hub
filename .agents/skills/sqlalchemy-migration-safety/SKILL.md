---
name: sqlalchemy-migration-safety
description: SQLAlchemy and migration safety patterns for this project. Use when changing models, writing Alembic migrations, or applying database updates to Railway.
---

# SQLAlchemy + Migration Safety

## When to Use

- Add or modify SQLAlchemy models
- Create Alembic migrations
- Apply schema changes to Railway
- Diagnose schema drift or missing-column errors

## Core Rules

1. Model changes must ship with migration changes.
2. Use UUID primary keys and JSONB for structured payloads where appropriate.
3. Keep migrations idempotent when possible for recovery scenarios.
4. Never assume Railway deploy ran migrations successfully.
5. Verify migration state after apply.

## Mandatory Railway Flow

1. Create migration locally.
2. Apply locally and verify.
3. Apply to Railway manually using public DB URL.
4. Verify `alembic current` shows head.

## Safety Checklist

- [ ] Migration includes forward path for all model changes.
- [ ] Migration tested locally before remote apply.
- [ ] Railway manual apply completed and verified.
- [ ] Rollback strategy or mitigation is documented.
