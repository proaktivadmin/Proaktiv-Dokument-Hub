# Phase 10: Office Entra ID Sync

## Overview

Extend the existing Entra ID sync functionality to fetch and display Microsoft 365 Group data for offices. This is a **read-only audit** feature that matches M365 Groups to local offices and shows sync status in the UI.

**Goal**: Provide visibility into office Microsoft 365 Group association and identify data mismatches between Vitec (primary source) and Entra ID (secondary source).

---

## Success Criteria

1. ✅ Fetch M365 Groups from Microsoft Graph API
2. ✅ Match groups to local offices by email/name patterns
3. ✅ Store Entra data in secondary `entra_*` columns (never overwrite Vitec data)
4. ✅ Display Entra status bubbles on OfficeCard (like EmployeeCard)
5. ✅ Show "Entra ID (sekundær)" section on office detail page
6. ✅ Add "Hent Entra" button to offices page

---

## Phase Dependencies

| Dependency | Status | Notes |
|------------|--------|-------|
| Phase 06: Employee Entra Sync | ✅ Complete | Pattern reference |
| `Group.Read.All` permission | ⏸️ Required | Must be granted in Azure |
| PostgreSQL migrations | ⚠️ Manual | Apply to Railway manually |

---

## Agent Pipeline

Execute agents in sequence. Each agent delivers specific outputs before handover.

| # | Agent | File | Deliverables |
|---|-------|------|--------------|
| 1 | Schema Architect | `office-entra-sync-01-schema.md` | Alembic migration, model updates, Pydantic schemas |
| 2 | Graph API Specialist | `office-entra-sync-02-graph.md` | Import script with group fetching and matching |
| 3 | Backend API Builder | `office-entra-sync-03-api.md` | Service methods, router endpoints |
| 4 | Frontend Integrator | `office-entra-sync-04-frontend.md` | UI components, Entra status bubbles |
| 5 | QA & Documentation | `office-entra-sync-05-qa.md` | Testing, docs, handover |

---

## Timeline (Relative Order)

```
[Agent 1: Schema] → [Agent 2: Graph] → [Agent 3: API] → [Agent 4: Frontend] → [Agent 5: QA]
       ↓                   ↓                  ↓                 ↓                  ↓
   Migration         Import Script       Endpoints         UI Updates          Tests
```

---

## Key Decisions

### 1. Matching Strategy
Groups will be matched to offices using:
1. **Email match**: Group mail → Office email (e.g., `bergen@proaktiv.no`)
2. **Name match**: Group displayName contains office name or city
3. **Manual override**: `entra_group_id` can be set manually if auto-match fails

### 2. Read-Only Policy
- Entra ID is **never modified** by this feature
- All data flows: Entra → Local DB (read-only)
- Entra fields are secondary; Vitec data is always the source of truth

### 3. Visual Indicators
Follow the EmployeeCard pattern:
- **Green bubble**: Vitec data (primary source)
- **Blue bubble**: Entra data (secondary source)
- **Amber ring**: Mismatch detected
- **Faded bubble**: No sync data

---

## Graph API Details

### Required Permission
```
Group.Read.All (Application)
```

### Endpoint
```
GET /groups?$filter=groupTypes/any(c:c eq 'Unified')
&$select=id,displayName,mail,description,createdDateTime
```

### Optional: SharePoint Site
```
GET /groups/{id}/sites/root
```

---

## Database Schema Changes

### New Office Columns

| Column | Type | Description |
|--------|------|-------------|
| `entra_group_id` | `String(64)` | M365 Group object ID |
| `entra_group_name` | `String(255)` | Group display name |
| `entra_group_mail` | `String(255)` | Group email address |
| `entra_group_description` | `Text` | Group description |
| `entra_sharepoint_url` | `Text` | SharePoint site URL |
| `entra_member_count` | `Integer` | Group member count |
| `entra_mismatch_fields` | `JSONB` | Array of mismatched field names |
| `entra_last_synced_at` | `DateTime(tz)` | Last sync timestamp |

---

## Files to Create/Modify

### Backend
- `backend/alembic/versions/YYYYMMDD_add_office_entra_columns.py` (NEW)
- `backend/app/models/office.py` (MODIFY - add entra columns)
- `backend/app/schemas/office.py` (MODIFY - add entra fields)
- `backend/app/schemas/entra_sync.py` (MODIFY - add office schemas)
- `backend/scripts/import_entra_offices.py` (NEW)
- `backend/app/services/entra_sync_service.py` (MODIFY - add office methods)
- `backend/app/routers/entra_sync.py` (MODIFY - add office endpoints)

### Frontend
- `frontend/src/types/v3.ts` (MODIFY - add entra fields to Office)
- `frontend/src/types/entra-sync.ts` (MODIFY - add office types)
- `frontend/src/components/offices/OfficeCard.tsx` (MODIFY - add status bubbles)
- `frontend/src/app/offices/[id]/page.tsx` (MODIFY - add Entra section)
- `frontend/src/app/offices/page.tsx` (MODIFY - add Hent Entra button)
- `frontend/src/lib/api/entra-sync.ts` (MODIFY - add office methods)

---

## Risk Assessment

| Risk | Mitigation |
|------|------------|
| Group.Read.All not granted | Document permission requirements, test in dry-run |
| Migration fails on Railway | Manual migration application (see CLAUDE.md) |
| Wrong group matched | Use email-first matching, allow manual override |
| Too many groups | Paginate results, filter by domain |

---

## Rollback Plan

1. Remove migration: `alembic downgrade -1`
2. Revert code changes
3. Redeploy

---

## Notes

- Norwegian UI labels (e.g., "Hent Entra", "M365 Gruppe", "Synkronisert")
- Follow existing patterns from Employee Entra sync
- All agents must check for linting errors before completion
