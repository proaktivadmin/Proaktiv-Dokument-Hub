# Phase 2: Vitec Sync Review UI - Research

**Researched:** 2026-01-20
**Domain:** Sync Review Workflow with Field-Level Diff
**Confidence:** HIGH

## Summary

Phase 2 builds a manual review workflow for Vitec sync operations. Instead of auto-syncing data (Phase 1), users will preview incoming changes, see field-by-field diffs, and approve/reject changes individually before committing.

**Primary recommendation:** Build a sync preview system with session-based state storage, allowing users to review diffs and selectively approve changes before any database writes occur.

## Standard Stack

The established libraries/tools for this domain:

### Core (Already in Codebase)
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| FastAPI | 0.100+ | API framework | Existing backend framework |
| Pydantic | 2.x | Data validation | Existing schema pattern |
| SQLAlchemy | 2.x | Database ORM | Existing async pattern |
| React | 18.x | Frontend framework | Existing UI framework |
| Shadcn/UI | - | Component library | Existing component pattern |

### Supporting (Already in Codebase)
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| Tanstack Query | - | Data fetching | Already used for API calls |
| Zustand | 4.x | State management | Already in dependencies |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| DB session storage | Redis | Redis adds infrastructure; DB is sufficient for admin tool |
| Real-time updates | WebSockets | Unnecessary - single user reviewing |
| File-based diff | Custom diff | Build custom - domain-specific field matching needed |

**Installation:**
No new packages needed - all dependencies already exist.

## Architecture Patterns

### Existing Project Structure (Follow This)
```
backend/
├── app/
│   ├── services/
│   │   ├── sync_preview_service.py   # NEW - Preview generation
│   │   └── sync_matching_service.py  # NEW - Record matching
│   ├── routers/
│   │   └── sync.py                   # NEW - Preview/commit endpoints
│   ├── schemas/
│   │   └── sync.py                   # NEW - Diff/preview schemas
│   └── models/
│       └── sync_session.py           # NEW - Session storage

frontend/
├── src/
│   ├── app/
│   │   └── sync/
│   │       └── page.tsx              # NEW - Sync review page
│   ├── components/
│   │   └── sync/
│   │       ├── SyncPreview.tsx       # NEW - Main preview component
│   │       ├── RecordDiffCard.tsx    # NEW - Single record diff
│   │       └── FieldDiffRow.tsx      # NEW - Field comparison
│   └── lib/api/
│       └── sync.ts                   # NEW - Sync preview API
```

### Pattern 1: Preview Before Commit
**What:** Generate preview of changes without writing to DB
**When to use:** Any bulk import/sync operation requiring review
**Example:**
```python
class SyncPreviewService:
    async def generate_preview(self, db: AsyncSession) -> SyncPreview:
        """Fetch Vitec data, match to local, generate diffs."""
        vitec_offices = await self.hub.get_departments(install_id)
        vitec_employees = await self.hub.get_employees(install_id)
        
        office_diffs = await self._match_and_diff_offices(db, vitec_offices)
        employee_diffs = await self._match_and_diff_employees(db, vitec_employees)
        
        return SyncPreview(offices=office_diffs, employees=employee_diffs)
```

### Pattern 2: Session-Based State
**What:** Store preview data in DB session for later commit
**When to use:** Multi-step workflows where user reviews before commit
**Example:**
```python
class SyncSession(Base):
    id: UUID
    preview_data: dict  # JSONB - stores full preview
    decisions: dict     # JSONB - stores approve/reject per field
    created_at: datetime
    expires_at: datetime
    status: str  # pending, committed, expired, cancelled
```

### Pattern 3: Field-Level Diff
**What:** Compare each field individually with clear approve/reject
**When to use:** When user needs granular control over changes
**Example:**
```python
class FieldDiff(BaseModel):
    field_name: str
    local_value: Any
    vitec_value: Any
    has_conflict: bool  # Both have different non-null values
    decision: Optional[Literal["accept", "reject"]]  # User's choice
```

### Anti-Patterns to Avoid
- **Auto-overwriting data:** Never write Vitec data without user approval
- **All-or-nothing sync:** Allow per-field decisions, not just per-record
- **Lost sessions:** Store session in DB, not memory/Redis

## Don't Hand-Roll

Problems that already have solutions in the codebase:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Vitec API calls | New client | VitecHubService | Already handles auth, errors |
| Field mapping | New mappers | _map_department_payload(), _map_employee_payload() | Already normalize data |
| Record lookup | New queries | get_by_organization_number(), get_by_email() | Already exist |
| Toast notifications | Custom alerts | useToast() from shadcn | Existing pattern |

## Common Pitfalls

### Pitfall 1: Session Expiry Without Warning
**What goes wrong:** User leaves review open, comes back, session expired, work lost
**Why it happens:** No visibility of session expiry
**How to avoid:** Show time remaining, auto-save decisions to session
**Warning signs:** User complaints about lost work

### Pitfall 2: Matching False Positives
**What goes wrong:** Wrong records matched, user approves thinking it's correct
**Why it happens:** Fuzzy matching too aggressive
**How to avoid:** Show match confidence, highlight low-confidence matches
**Warning signs:** Duplicate records after sync

### Pitfall 3: Large Preview Payload
**What goes wrong:** Preview takes forever, browser slows down
**Why it happens:** Loading all 125 employees at once
**How to avoid:** Paginate preview, show summary first
**Warning signs:** Spinner never stops, browser unresponsive

### Pitfall 4: Partial Commit Confusion
**What goes wrong:** User commits some records, forgets others pending
**Why it happens:** No clear indication of what's committed vs pending
**How to avoid:** Clear status badges, commit confirmation shows counts
**Warning signs:** "I thought I synced everyone"

## Data Models

### SyncPreview Schema
```python
class FieldDiff(BaseModel):
    field_name: str
    local_value: Any
    vitec_value: Any
    has_conflict: bool
    decision: Optional[Literal["accept", "reject"]] = None

class RecordDiff(BaseModel):
    match_type: Literal["new", "matched", "not_in_vitec"]
    local_id: Optional[UUID]
    vitec_id: Optional[str]
    display_name: str  # For UI display
    fields: List[FieldDiff]
    match_confidence: float  # 0.0 - 1.0
    match_method: Optional[str]  # "org_number", "email", "name"

class SyncPreview(BaseModel):
    session_id: UUID
    created_at: datetime
    expires_at: datetime
    offices: List[RecordDiff]
    employees: List[RecordDiff]
    summary: SyncSummary

class SyncSummary(BaseModel):
    offices_new: int
    offices_matched: int
    offices_not_in_vitec: int
    employees_new: int
    employees_matched: int
    employees_not_in_vitec: int
    employees_missing_office: int
```

### API Endpoints
```
POST /api/sync/preview
  - Fetches Vitec data, generates preview
  - Creates sync session in DB
  - Returns: SyncPreview

GET /api/sync/sessions/{session_id}
  - Returns stored preview with current decisions

PATCH /api/sync/sessions/{session_id}/decisions
  - Body: { record_type, record_id, field_name, decision }
  - Updates decision for a field

POST /api/sync/sessions/{session_id}/commit
  - Applies all accepted changes
  - Creates new records for accepted "new" items
  - Returns: SyncResult

DELETE /api/sync/sessions/{session_id}
  - Cancels sync session
```

## Matching Strategy

### Offices
| Priority | Match By | Confidence |
|----------|----------|------------|
| 1 | organization_number | 1.0 |
| 2 | vitec_department_id | 1.0 |
| 3 | name (exact) | 0.9 |
| 4 | name (fuzzy 85%) | 0.7 |

### Employees
| Priority | Match By | Confidence |
|----------|----------|------------|
| 1 | vitec_employee_id | 1.0 |
| 2 | email (case-insensitive) | 0.95 |
| 3 | first_name + last_name + office | 0.8 |

## Plan Breakdown

| Plan | Focus | Key Deliverables |
|------|-------|------------------|
| 02-01 | Matching Service | Match algorithms, RecordDiff model, confidence scoring |
| 02-02 | Preview Endpoint | SyncSession model, preview generation, session storage |
| 02-03 | Commit Endpoint | Apply approved changes, reject handling, audit log |
| 02-04 | Review UI | Diff components, approve/reject controls, summary |
| 02-05 | Polish | Bulk actions, session expiry, error handling |

## Open Questions

1. **Session expiry duration** - 24 hours reasonable?
   - Recommendation: 24 hours, with warning after 1 hour

2. **Records not in Vitec** - Show local-only records?
   - Recommendation: Yes, show as "not_in_vitec" for awareness, no action needed

3. **Bulk approve thresholds** - Allow "approve all" for high-confidence matches?
   - Recommendation: Yes, but only for confidence >= 0.9

## Sources

### Primary (HIGH confidence)
- `backend/app/services/office_service.py` - Existing match/upsert logic
- `backend/app/services/employee_service.py` - Existing match/upsert logic
- `backend/app/services/vitec_hub_service.py` - API client
- `.planning/REQUIREMENTS.md` - VITEC-04 through VITEC-08

### Secondary (MEDIUM confidence)
- `.planning/PROJECT.md` - "Manual sync review" constraint
- Phase 1 research - Field mapping, error handling patterns

## Metadata

**Confidence breakdown:**
- Architecture: HIGH - Follows existing patterns, clear requirements
- Matching: HIGH - Based on existing upsert logic
- UI: MEDIUM - New components, but follows Shadcn patterns

**Research date:** 2026-01-20
**Valid until:** 60 days (stable)
