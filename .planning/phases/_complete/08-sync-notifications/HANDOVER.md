# Phase 08: Sync Notification System - HANDOVER

**Created:** 2026-01-24
**Status:** Ready for Implementation
**Phase:** 08-sync-notifications

---

## MASTER PROMPT

You are implementing Phase 08: Sync Notification System.

**Objective:** Create a notification bell dropdown in the dashboard header that alerts users to sync events (new entries, removals, updates, mismatches) for employees and offices.

**Data Flow:**
```
Sync Services → NotificationService → PostgreSQL → REST API → Frontend Dropdown
```

**Architecture:**
```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend                                 │
│  Header.tsx → NotificationDropdown → NotificationItem            │
│       ↓                                                          │
│  useNotifications hook → notifications API client                │
└─────────────────────────────────────────────────────────────────┘
                              ↓ GET/PATCH/POST
┌─────────────────────────────────────────────────────────────────┐
│                         Backend                                  │
│  /api/notifications/* → NotificationService → Notification Model │
│                                                                  │
│  employee_service.py ──┐                                         │
│  office_service.py ────┼→ NotificationService.create()           │
└─────────────────────────────────────────────────────────────────┘
                              ↓
                    ┌─────────────────┐
                    │   PostgreSQL    │
                    │  notifications  │
                    └─────────────────┘
```

---

## CONTEXT FILES (READ FIRST)

1. `CLAUDE.md` - Project conventions, stack, patterns
2. `.planning/codebase/DESIGN-SYSTEM.md` - Frontend design tokens and patterns
3. `backend/app/models/audit_log.py` - Similar model pattern to follow
4. `backend/app/models/employee.py` - Entity model pattern
5. `frontend/src/components/layout/Header.tsx` - Where notification bell goes
6. `frontend/src/components/ui/dropdown-menu.tsx` - Dropdown pattern to use

---

## NOTIFICATION TYPES

| Type | Entity | Severity | Trigger |
|------|--------|----------|---------|
| `employee_added` | employee | info | New employee synced |
| `employee_removed` | employee | warning | Employee deleted/deactivated |
| `employee_updated` | employee | info | Employee fields changed |
| `office_added` | office | info | New office synced |
| `office_removed` | office | warning | Office deleted |
| `office_updated` | office | info | Office fields changed |
| `upn_mismatch` | employee | error | Entra UPN differs from email |
| `sync_error` | sync | error | Sync operation failed |

---

## API ENDPOINTS

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/notifications` | GET | List notifications (pagination, filters) |
| `/api/notifications/{id}/read` | PATCH | Mark single notification read |
| `/api/notifications/read-all` | POST | Mark all as read |
| `/api/notifications/{id}` | DELETE | Delete notification |
| `/api/notifications/clear` | POST | Clear all notifications |
| `/api/notifications/unread-count` | GET | Get unread count |

---

## EXECUTION ORDER

### Wave 1: Database Foundation
1. **08-01-PLAN.md** - Notification model + Alembic migration
   - Create `notification.py` model
   - Create Alembic migration
   - Apply migration to Railway

### Wave 2: Backend Service Layer
2. **08-02-PLAN.md** - NotificationService + REST endpoints
   - Create `notification_service.py`
   - Create `notification.py` schemas
   - Create `notifications.py` router
   - Register router in main.py

### Wave 3: Frontend Foundation
3. **08-03-PLAN.md** - TypeScript types + API client + hook
   - Create `notification.ts` types
   - Create `notifications.ts` API client
   - Create `use-notifications.ts` hook

### Wave 4: Frontend UI
4. **08-04-PLAN.md** - Notification dropdown components
   - Create `NotificationDropdown.tsx`
   - Create `NotificationItem.tsx`
   - Integrate into `Header.tsx`

### Wave 5: Integration
5. **08-05-PLAN.md** - Hook into sync services
   - Modify `employee_service.py` to emit notifications
   - Modify `office_service.py` to emit notifications
   - Test notification generation

### Wave 6: Testing & QA
6. **08-06-PLAN.md** - Verification and testing
   - Backend API tests
   - Frontend component tests
   - End-to-end verification

---

## KEY PATTERNS

### Backend Model Pattern (from audit_log.py)

```python
from sqlalchemy import DateTime, Index, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func
from app.models.base import GUID, Base, JSONType

class Notification(Base):
    __tablename__ = "notifications"
    
    id: Mapped[uuid.UUID] = mapped_column(GUID, primary_key=True, default=lambda: str(uuid.uuid4()))
    # ... fields with proper typing
    
    __table_args__ = (
        Index("idx_notifications_unread", "is_read"),
        # ... other indexes
    )
```

### Frontend Dropdown Pattern (from Header.tsx)

```tsx
<DropdownMenu>
  <DropdownMenuTrigger asChild>
    <button className="...">
      <Bell className="h-4 w-4" />
      {unreadCount > 0 && <Badge>...</Badge>}
    </button>
  </DropdownMenuTrigger>
  <DropdownMenuContent align="end" className="w-80 bg-white">
    {/* Notification items */}
  </DropdownMenuContent>
</DropdownMenu>
```

### Design Tokens (from DESIGN-SYSTEM.md)

- Shadows: `shadow-card`, `shadow-elevated`
- Transitions: `duration-fast`, `duration-normal`, `ease-standard`
- Colors: Navy `#272630`, Bronze `#BCAB8A`, Beige `#E9E7DC`
- Severity colors: `text-emerald-600` (info), `text-amber-600` (warning), `text-red-600` (error)

---

## AGENT RETURN FORMAT

After completing a plan, return this summary for copy/paste review:

```
## EXECUTION SUMMARY

**Plan:** 08-XX-PLAN.md
**Status:** COMPLETE | PARTIAL | BLOCKED
**Duration:** ~X minutes

### Completed Tasks
- [x] Task 1: Description
- [x] Task 2: Description

### Files Created/Modified
- `path/to/file.ext` - Description of changes

### Verification
- [ ] Criteria 1: PASS/FAIL
- [ ] Criteria 2: PASS/FAIL

### Notes for Review
- Any deviations from plan
- Decisions made
- Issues encountered

### Next Steps
- What the next agent should do
```

---

## COMMANDS

Execute plans with these commands (copy full command including context):

### `/notify-01` - Database Model + Migration

```
Execute .planning/phases/08-sync-notifications/08-01-PLAN.md

Context: Read HANDOVER.md first. Follow patterns from backend/app/models/audit_log.py.

Return: Execution summary with migration version and Railway apply status.
```

### `/notify-02` - Backend Service + Endpoints

```
Execute .planning/phases/08-sync-notifications/08-02-PLAN.md

Context: Read HANDOVER.md first. Notification model exists. Follow patterns from backend/app/services/employee_service.py and backend/app/routers/employees.py.

Return: Execution summary with endpoint list and test results.
```

### `/notify-03` - Frontend Types + API Client

```
Execute .planning/phases/08-sync-notifications/08-03-PLAN.md

Context: Read HANDOVER.md first. Backend API is ready. Follow patterns from frontend/src/types/employee.ts and frontend/src/lib/api/employees.ts.

Return: Execution summary with TypeScript types and hook signature.
```

### `/notify-04` - Frontend Components

```
Execute .planning/phases/08-sync-notifications/08-04-PLAN.md

Context: Read HANDOVER.md first. API client and hook are ready. Follow patterns from Header.tsx dropdowns and DESIGN-SYSTEM.md.

Return: Execution summary with component list and visual description.
```

### `/notify-05` - Sync Integration

```
Execute .planning/phases/08-sync-notifications/08-05-PLAN.md

Context: Read HANDOVER.md first. NotificationService is ready. Modify sync methods to call NotificationService.create().

Return: Execution summary with integration points and test sync results.
```

### `/notify-06` - Testing & QA

```
Execute .planning/phases/08-sync-notifications/08-06-PLAN.md

Context: Read HANDOVER.md first. Full system is implemented. Run tests and verify end-to-end flow.

Return: Execution summary with test results and QA checklist.
```
