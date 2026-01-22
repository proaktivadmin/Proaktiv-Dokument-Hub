# Phase 2: Vitec Sync Review UI - Agent Handover

**Created:** 2026-01-20
**Purpose:** Complete context for a fresh agent to implement the Vitec Sync Review UI

---

## MASTER PROMPT

You are implementing Phase 2 of the Proaktiv Dokument Hub project: **Vitec Sync Review UI**. This feature allows users to preview incoming Vitec data, see field-by-field differences, and approve/reject changes before committing to the database.

### Your Mission

Build a manual review workflow for Vitec sync operations with these core features:
1. **Preview endpoint** - Fetch Vitec data, match to local records, generate field-level diffs
2. **Session storage** - Store preview in database for later review/commit
3. **Decision tracking** - User can accept/reject individual fields
4. **Commit endpoint** - Apply only approved changes
5. **Frontend UI** - Review interface with diff display and approve/reject controls

### Execution Order

Execute plans in sequence. Each plan builds on the previous:

| Plan | Focus | Files |
|------|-------|-------|
| **02-01** | Matching Service | `schemas/sync.py`, `services/sync_matching_service.py` |
| **02-02** | Preview Endpoint | `models/sync_session.py`, `services/sync_preview_service.py`, `routers/sync.py` |
| **02-03** | Commit Endpoint | `services/sync_commit_service.py`, update `routers/sync.py` |
| **02-04** | Frontend Review UI | `app/sync/page.tsx`, components in `components/sync/` |
| **02-05** | Polish | Bulk actions, session timer, header nav, error handling |

### Plan Files Location
`.planning/phases/02-vitec-sync-review-ui/02-01-PLAN.md` through `02-05-PLAN.md`

---

## PROJECT CONTEXT

### Stack (Updated 2026-01-22)
- **Backend:** FastAPI 0.109 + SQLAlchemy 2.0.46 (async) + Pydantic 2.x + PostgreSQL
- **Frontend:** Next.js 16 + React 19 + Shadcn/UI + Tailwind CSS 4 + TypeScript 5.9
- **Testing:** Vitest (frontend) + Pytest (backend)
- **CI/CD:** GitHub Actions (lint, typecheck, test, build)
- **Deployment:** Railway (backend + DB + frontend)

### Key Patterns

**Backend:**
- Business logic in `services/`, never in routers
- All services must be `async`
- Use `Depends()` for dependency injection
- UUID for all primary keys, JSONB for arrays/objects
- Pydantic for all validation

**Frontend:**
- Server Components by default, `"use client"` only when hooks needed
- Use `lib/api/*.ts` for API calls
- Shadcn components over custom
- No `any` in TypeScript

---

## MATCHING STRATEGY

### Offices - Match Priority
| Priority | Match By | Confidence |
|----------|----------|------------|
| 1 | organization_number | 1.0 |
| 2 | vitec_department_id | 1.0 |
| 3 | name (exact) | 0.9 |
| 4 | name (fuzzy 85%) | 0.7 |

### Employees - Match Priority
| Priority | Match By | Confidence |
|----------|----------|------------|
| 1 | vitec_employee_id | 1.0 |
| 2 | email (case-insensitive) | 0.95 |
| 3 | first_name + last_name + office_id | 0.8 |

---

## API ENDPOINTS TO CREATE

```
POST   /api/sync/preview              -> SyncPreview (creates session)
GET    /api/sync/sessions/{id}        -> SyncPreview (get current state)
PATCH  /api/sync/sessions/{id}/decisions -> {success: bool}
POST   /api/sync/sessions/{id}/commit -> SyncCommitResult
DELETE /api/sync/sessions/{id}        -> {success: bool}
```

---

## EXISTING CODE TO REUSE

### VitecHubService (backend/app/services/vitec_hub_service.py)
```python
hub = VitecHubService()
departments = await hub.get_departments(installation_id)
employees = await hub.get_employees(installation_id)
```

### Existing Mapping Functions
```python
# backend/app/services/office_service.py
payload = OfficeService._map_department_payload(raw_dept)

# backend/app/services/employee_service.py  
payload = EmployeeService._map_employee_payload(raw_employee)
```

### Existing Lookup Functions
```python
await OfficeService.get_by_organization_number(db, org_number)
await OfficeService.get_by_vitec_department_id(db, dept_id)
await EmployeeService.get_by_vitec_employee_id(db, vitec_id)
await EmployeeService.get_by_email(db, email)
```

---

## FIELD LABELS (Norwegian)

```python
FIELD_LABELS = {
    "name": "Markedsnavn",
    "legal_name": "Juridisk navn",
    "organization_number": "Org.nr",
    "email": "Epost",
    "phone": "Telefon",
    "street_address": "Adresse",
    "postal_code": "Postnr",
    "city": "Sted",
    "first_name": "Fornavn",
    "last_name": "Etternavn",
    "title": "Tittel",
    "system_roles": "Roller",
}
```

---

## TESTING CHECKLIST

**Plan 02-01:** Schemas and matching service exist, exports added
**Plan 02-02:** POST /api/sync/preview works, session stored in DB
**Plan 02-03:** PATCH decisions works, POST commit applies only accepted
**Plan 02-04:** /sync page loads, diffs display, accept/reject buttons work
**Plan 02-05:** Bulk actions, timer, header link, error handling

---

## COMMON PITFALLS

1. Auto-write freely - Commit changes without asking for approval
2. Don't recreate VitecHubService - Use existing service
3. Don't skip session storage - Must persist for multi-step workflow
4. Don't forget expires_at - Sessions expire after 24 hours
5. Don't hardcode installation_id - Use settings.VITEC_INSTALLATION_ID

---

## START COMMAND

Read and execute `.planning/phases/02-vitec-sync-review-ui/02-01-PLAN.md` first.
After completing all tasks, commit and move to next plan.

Also read:
- `02-RESEARCH.md` for full data models and architecture
- `CLAUDE.md` for project conventions
