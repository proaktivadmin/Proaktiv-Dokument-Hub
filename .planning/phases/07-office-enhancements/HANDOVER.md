# Phase 07: Office Enhancements & SalesScreen - HANDOVER

**Created:** 2026-01-22
**Status:** Ready for Implementation

---

## MASTER PROMPT

You are implementing Phase 07: Office Enhancements & SalesScreen Integration.

**Objective:** Add office region grouping, office merge tool, and SalesScreen employee sync.

**Features:**
1. **Office Regions** - Geographic grouping (Trøndelag, Romerike, Sør-Rogaland, Vest, Sør, Øst)
2. **Office Merge** - Combine duplicate offices, move employees/assets
3. **SalesScreen Sync** - Push employee data to SalesScreen for offices with active agreements

---

## CONTEXT FILES (READ FIRST)

1. `07-RESEARCH-SALESSCREEN.md` - SalesScreen API research
2. `backend/app/models/office.py` - Office model structure
3. `backend/app/models/employee.py` - Employee model structure
4. `frontend/src/components/offices/OfficeGrid.tsx` - Current office grid

---

## EXECUTION ORDER

### Wave 1: Database Schema (parallel)
1. **07-01-PLAN.md** - Add region field to offices
2. **07-05-PLAN.md** - Add SalesScreen fields to offices

### Wave 2: Backend APIs (parallel)
3. **07-02-PLAN.md** - Region filter and grouping UI
4. **07-03-PLAN.md** - Office merge backend API
5. **07-06-PLAN.md** - SalesScreen backend service

### Wave 3: Frontend Components
6. **07-04-PLAN.md** - Office merge frontend UI
7. **07-07-PLAN.md** - SalesScreen frontend types, hooks, dialogs

### Wave 4: Integration
8. **07-08-PLAN.md** - SalesScreen integration with employee UI + onboarding

---

## KEY PATTERNS

### Office Regions

```python
VALID_REGIONS = [
    "Trøndelag",    # Trondheim area
    "Romerike",     # Lillestrøm, Lørenskog
    "Sør-Rogaland", # Stavanger, Sandnes, Sola
    "Vest",         # Bergen, Voss
    "Sør",          # Kristiansand, Skien
    "Øst"           # Oslo, Drammen
]
```

### Office Merge Flow

```
1. User selects target office (to keep)
2. User selects source offices (duplicates)
3. System moves all employees to target
4. System moves all assets to target
5. Optionally copy missing fields from sources
6. Deactivate or delete source offices
```

### SalesScreen Sync Flow

```
1. Check if office has salesscreen_enabled = True
2. If not, show error message
3. If yes, call SalesScreen API to create/update user
4. Optionally upload profile photo
5. Log result and show success/error
```

---

## DATA MAPPINGS

### SalesScreen User Mapping

| Our Database | SalesScreen |
|--------------|-------------|
| `first_name` | `firstName` |
| `last_name` | `lastName` |
| `email` | `email` (unique key) |
| `title` | `title` |
| `phone` | `phone` |
| `profile_image_url` | User photo |
| `office.salesscreen_team_id` | `teamId` |

---

## FILES TO CREATE

### Database Migrations
| File | Description |
|------|-------------|
| `backend/alembic/versions/YYYYMMDD_add_office_region.py` | Region column |
| `backend/alembic/versions/YYYYMMDD_add_salesscreen_fields.py` | SalesScreen columns |

### Backend
| File | Description |
|------|-------------|
| `backend/app/schemas/salesscreen.py` | Pydantic schemas |
| `backend/app/services/salesscreen_service.py` | SalesScreen API client |
| `backend/app/routers/salesscreen.py` | FastAPI endpoints |

### Frontend
| File | Description |
|------|-------------|
| `frontend/src/types/salesscreen.ts` | TypeScript interfaces |
| `frontend/src/lib/api/salesscreen.ts` | API client |
| `frontend/src/hooks/useSalesScreen.ts` | React hook |
| `frontend/src/components/offices/OfficeMergeDialog.tsx` | Merge UI |
| `frontend/src/components/employees/SalesScreenSyncDialog.tsx` | Sync dialog |
| `frontend/src/components/employees/SalesScreenBatchDialog.tsx` | Batch sync |
| `frontend/src/components/employees/OnboardingChecklist.tsx` | Onboarding steps |

---

## CONSTRAINTS

1. **SalesScreen API Not Yet Available**
   - Implement with mock API client
   - Will be updated when credentials are obtained
   - Contact SalesScreen for API access

2. **Office-Level Control**
   - Only sync employees from offices with `salesscreen_enabled = True`
   - Show clear error if office not enabled

3. **Merge Safety**
   - Always preview before merge
   - Transaction rollback on error
   - Log all merge operations

---

## TESTING CHECKLIST

### Office Regions
- [ ] Region column exists in database
- [ ] API filters by region
- [ ] Region dropdown in office grid
- [ ] Region badge on office cards
- [ ] Region field in office form

### Office Merge
- [ ] Preview shows accurate counts
- [ ] Employees moved correctly
- [ ] Assets moved correctly
- [ ] Sources deactivated/deleted
- [ ] Transaction rollback on error

### SalesScreen
- [ ] Status endpoint returns connection info
- [ ] Preview shows sync changes
- [ ] Single employee sync works
- [ ] Batch sync works
- [ ] Disabled offices show error
- [ ] Onboarding checklist includes step

---

## COMPLETION CRITERIA

Phase 07 is complete when:
1. All database migrations run successfully
2. Region filter and grouping work in UI
3. Office merge tool works end-to-end
4. SalesScreen mock integration works
5. Onboarding checklist includes SalesScreen step
6. HANDOVER.md updated with "COMPLETED" status
