# Phase 1: Vitec API Connection - Research

**Researched:** 2026-01-20
**Domain:** Vitec Megler Hub API Integration
**Confidence:** HIGH

## Summary

Research confirms that Phase 1 is **already substantially implemented**. The codebase contains:

1. A complete `VitecHubService` class with authenticated API calls using HTTP Basic Auth
2. Sync methods in `OfficeService.sync_from_hub()` and `EmployeeService.sync_from_hub()`
3. Router endpoints at `POST /api/offices/sync` and `POST /api/employees/sync`
4. Pydantic schemas for sync results (`OfficeSyncResult`, `EmployeeSyncResult`)
5. Database models with `vitec_department_id` (Office) and `vitec_employee_id` (Employee)
6. Environment configuration for all Vitec Hub credentials

The remaining work is primarily **verification, UI integration, and error handling improvements** rather than building from scratch.

**Primary recommendation:** Focus planning on verifying existing implementation works in production, adding admin UI triggers with clear feedback, and ensuring error states surface properly.

## Standard Stack

The established libraries/tools for this domain:

### Core (Already in Codebase)
| Library | Version | Purpose | Why Standard |
|---------|---------|---------|--------------|
| httpx | async | HTTP client for Vitec API | Already used in VitecHubService, supports BasicAuth |
| FastAPI | 0.100+ | API framework | Existing backend framework |
| Pydantic | 2.x | Data validation | Existing schema pattern |
| SQLAlchemy | 2.x | Database ORM | Existing async pattern |

### Supporting (Already in Codebase)
| Library | Version | Purpose | When to Use |
|---------|---------|---------|-------------|
| python-dotenv | - | Environment config | Loading VITEC_* credentials |
| pydantic-settings | - | Settings validation | Config.py pattern |

### Alternatives Considered
| Instead of | Could Use | Tradeoff |
|------------|-----------|----------|
| httpx | aiohttp | httpx already in codebase, has better BasicAuth support |
| Sync endpoints | Background tasks | Current sync is fast enough, no need for Celery/background |

**Installation:**
No new packages needed - all dependencies already exist.

## Architecture Patterns

### Existing Project Structure (Follow This)
```
backend/
├── app/
│   ├── config.py          # VITEC_* settings already here
│   ├── services/
│   │   ├── vitec_hub_service.py   # EXISTS - API client
│   │   ├── office_service.py      # EXISTS - sync_from_hub()
│   │   └── employee_service.py    # EXISTS - sync_from_hub()
│   ├── routers/
│   │   ├── offices.py     # EXISTS - POST /offices/sync
│   │   └── employees.py   # EXISTS - POST /employees/sync
│   ├── schemas/
│   │   ├── office.py      # EXISTS - OfficeSyncResult
│   │   └── employee.py    # EXISTS - EmployeeSyncResult
│   └── models/
│       ├── office.py      # EXISTS - vitec_department_id
│       └── employee.py    # EXISTS - vitec_employee_id
```

### Pattern 1: Service Layer for External APIs (Established)
**What:** All Vitec API calls go through VitecHubService
**When to use:** Any external API integration
**Example:**
```python
# Source: backend/app/services/vitec_hub_service.py (existing)
class VitecHubService:
    """Client for Vitec Hub API using Product Login."""

    def __init__(self, *, base_url=None, product_login=None, access_key=None):
        self._base_url = base_url or settings.VITEC_HUB_BASE_URL or self._derive_base_url()
        self._product_login = product_login or settings.VITEC_HUB_PRODUCT_LOGIN
        self._access_key = access_key or settings.VITEC_HUB_ACCESS_KEY

    async def _request(self, method: str, path: str) -> Any:
        async with httpx.AsyncClient(
            auth=self._get_auth(),
            timeout=30.0,
            headers={"Accept": "application/json"},
        ) as client:
            response = await client.request(method, url)
        # Error handling for 401, 403, 429...
```

### Pattern 2: Sync Results Schema (Established)
**What:** Sync operations return structured result with counts
**When to use:** Any bulk import/sync operation
**Example:**
```python
# Source: backend/app/schemas/office.py (existing)
class OfficeSyncResult(BaseModel):
    total: int      # Records fetched from Vitec
    synced: int     # Created + Updated
    created: int    # New records
    updated: int    # Modified records
    skipped: int    # Unchanged records
```

### Pattern 3: Upsert with Multiple Match Keys (Established)
**What:** Match by Vitec ID first, then email, then name
**When to use:** Syncing entities that may exist locally without Vitec ID
**Example:**
```python
# Source: backend/app/services/employee_service.py (existing)
async def upsert_from_hub(db, payload, office):
    existing = None
    vitec_employee_id = payload.get("vitec_employee_id")
    if vitec_employee_id:
        existing = await EmployeeService.get_by_vitec_employee_id(db, vitec_employee_id)
    if not existing and payload.get("email"):
        existing = await EmployeeService.get_by_email(db, payload["email"])
    # ... fallback to name match
```

### Anti-Patterns to Avoid
- **Putting API logic in routers:** Business logic belongs in services, routers just call services
- **Hardcoded credentials:** All credentials via settings, never in code
- **Silent sync failures:** Always surface errors to caller with detail

## Don't Hand-Roll

Problems that already have solutions in the codebase:

| Problem | Don't Build | Use Instead | Why |
|---------|-------------|-------------|-----|
| Vitec API client | New HTTP client | VitecHubService | Already handles auth, errors, retries |
| Office sync | New sync logic | OfficeService.sync_from_hub() | Already maps fields, handles upsert |
| Employee sync | New sync logic | EmployeeService.sync_from_hub() | Already maps fields, handles office matching |
| Sync result format | New schema | OfficeSyncResult/EmployeeSyncResult | Consistent response format |
| Vitec ID storage | New columns | vitec_department_id, vitec_employee_id | Already in models with indexes |

**Key insight:** The implementation exists. Planning should focus on verification, UI, and error handling improvements.

## Common Pitfalls

### Pitfall 1: Missing Installation ID
**What goes wrong:** Sync fails with 500 error "VITEC_INSTALLATION_ID is not configured"
**Why it happens:** User tested API with Bruno manually specifying installation_id, forgot to set env var
**How to avoid:** Verify VITEC_INSTALLATION_ID is set in Railway environment variables
**Warning signs:** Sync endpoint returns 500 immediately

### Pitfall 2: Office Sync Before Employee Sync
**What goes wrong:** Employees with missing_office > 0 because their department doesn't exist locally
**Why it happens:** Employee sync runs before offices are synced
**How to avoid:** Always sync offices first, then employees
**Warning signs:** EmployeeSyncResult shows high missing_office count

### Pitfall 3: API Rate Limiting (429)
**What goes wrong:** Vitec Hub returns 429 Too Many Requests
**Why it happens:** Too many rapid sync attempts
**How to avoid:** VitecHubService already handles 429 with Retry-After header
**Warning signs:** 429 error with retry_after in detail message

### Pitfall 4: Email Matching Edge Cases
**What goes wrong:** Duplicate employees created when email differs between systems
**Why it happens:** Email-based matching fails when Vitec has different email
**How to avoid:** Ensure vitec_employee_id is populated on first sync
**Warning signs:** Duplicate employee names appearing after sync

### Pitfall 5: Frontend Error Handling
**What goes wrong:** User clicks sync, sees spinner forever, no error message
**Why it happens:** Frontend doesn't handle backend error responses
**How to avoid:** Frontend must catch and display error.response.data.detail
**Warning signs:** No UI feedback on sync failure

## Code Examples

Verified patterns from existing codebase:

### Vitec Hub API Request (Already Working)
```python
# Source: backend/app/services/vitec_hub_service.py
async def get_employees(self, installation_id: str) -> list[dict[str, Any]]:
    """Fetch employees for a specific installation."""
    data = await self._request("GET", f"{installation_id}/Employees")
    return list(data or [])

async def get_departments(self, installation_id: str) -> list[dict[str, Any]]:
    """Fetch offices (departments) for a specific installation."""
    data = await self._request("GET", f"{installation_id}/Departments")
    return list(data or [])
```

### Sync Endpoint Pattern (Already Working)
```python
# Source: backend/app/routers/offices.py
@router.post("/sync", response_model=OfficeSyncResult)
async def sync_offices(db: AsyncSession = Depends(get_db)):
    """Sync offices from Vitec Hub (Departments endpoint)."""
    result = await OfficeService.sync_from_hub(db)
    return OfficeSyncResult(**result)
```

### Field Mapping Pattern (Already Working)
```python
# Source: backend/app/services/office_service.py
@staticmethod
def _map_department_payload(raw: dict) -> dict:
    name = raw.get("marketName") or raw.get("name") or raw.get("legalName") or "Vitec Office"
    return {
        "vitec_department_id": raw.get("departmentId"),
        "department_number": raw.get("departmentNumber"),
        "name": OfficeService._normalize_text(name),
        "email": OfficeService._normalize_text(raw.get("email")),
        "phone": OfficeService._normalize_text(raw.get("phone")),
        # ... more fields
    }
```

### Error Response Pattern (Already Working)
```python
# Source: backend/app/services/vitec_hub_service.py
if response.status_code == 401:
    raise HTTPException(status_code=401, detail="Vitec Hub unauthorized.")
if response.status_code == 403:
    raise HTTPException(status_code=403, detail="Vitec Hub forbidden.")
if response.status_code == 429:
    retry_after = response.headers.get("Retry-After")
    detail = "Vitec Hub rate limit reached."
    if retry_after:
        detail = f"{detail} Retry after {retry_after} seconds."
    raise HTTPException(status_code=429, detail=detail)
```

## State of the Art

| Old Approach | Current Approach | When Changed | Impact |
|--------------|------------------|--------------|--------|
| Separate Office/Employee models | Vitec ID columns added | 2026-01-19 migration | Can link Hub data |
| No sync functionality | Full sync endpoints | Recent | Complete sync flow |

**Deprecated/outdated:**
- None identified - implementation is current

## Vitec Hub API Reference

Based on codebase analysis and .cursor/vitec-reference.md:

### Available Endpoints (Confirmed Working)
| Endpoint | Method | Returns | Notes |
|----------|--------|---------|-------|
| `Account/Methods` | GET | Available functions | For verifying permissions |
| `{installation_id}/Departments` | GET | Office/department list | Maps to Office model |
| `{installation_id}/Employees` | GET | Employee list | Maps to Employee model |

### Authentication
- **Type:** HTTP Basic Auth (Product Login)
- **Credentials:** VITEC_HUB_PRODUCT_LOGIN + VITEC_HUB_ACCESS_KEY
- **Base URLs:**
  - Production: `https://hub.megler.vitec.net`
  - QA/Test: `https://hub.qa.vitecnext.no`

### Department Response Fields (Used in Mapping)
| Vitec Field | Maps To | Notes |
|-------------|---------|-------|
| departmentId | vitec_department_id | Primary match key |
| departmentNumber | short_code generation | Fallback for short_code |
| marketName | name | Primary name source |
| name | name | Secondary name source |
| legalName | name | Tertiary name source |
| email | email | Direct map |
| phone | phone | Direct map |
| streetAddress | street_address | Direct map |
| postalCode | postal_code | Direct map |
| city | city | Direct map |
| webPublish | is_active | Boolean flag |
| aboutDepartment | description | Direct map |

### Employee Response Fields (Used in Mapping)
| Vitec Field | Maps To | Notes |
|-------------|---------|-------|
| employeeId | vitec_employee_id | Primary match key |
| departmentId | office_id (via lookup) | Links to Office |
| name | first_name, last_name | Split by space |
| email | email | Secondary match key |
| title | title | Direct map |
| mobilePhone | phone | Primary phone source |
| workPhone | phone | Fallback phone source |
| employeePositions | system_roles | Mapped via role_map |
| employeeActive | status | Boolean to active/inactive |
| aboutMe | description | Direct map |

## Open Questions

Things that couldn't be fully resolved:

1. **Rate Limit Behavior**
   - What we know: VitecHubService handles 429 with Retry-After
   - What's unclear: What are the actual rate limits?
   - Recommendation: Test with production data, monitor for 429s

2. **Full Employee Position Mapping**
   - What we know: 10 position types mapped (1-10)
   - What's unclear: Are there additional position types in production?
   - Recommendation: Log unmapped position types during sync

3. **Credential Validation in Railway**
   - What we know: User tested with Bruno and got 200 OK
   - What's unclear: Are the same credentials in Railway environment?
   - Recommendation: First task should verify credentials via /api health check

## Sources

### Primary (HIGH confidence)
- `backend/app/services/vitec_hub_service.py` - Complete API client implementation
- `backend/app/services/office_service.py` - Office sync implementation
- `backend/app/services/employee_service.py` - Employee sync implementation
- `backend/app/routers/offices.py` - Office sync endpoint
- `backend/app/routers/employees.py` - Employee sync endpoint
- `backend/app/config.py` - Environment variable definitions
- `backend/tests/test_vitec_hub_sync_endpoints.py` - Existing tests

### Secondary (MEDIUM confidence)
- `.cursor/vitec-reference.md` - Vitec Next documentation reference
- User context: "tested Vitec API with Bruno and got 200 OK"

### Tertiary (LOW confidence)
- None - all findings verified against codebase

## Metadata

**Confidence breakdown:**
- Standard stack: HIGH - All dependencies already in requirements.txt
- Architecture: HIGH - Implementation exists and follows established patterns
- Pitfalls: HIGH - Based on actual code analysis and common integration issues

**Research date:** 2026-01-20
**Valid until:** 60 days (stable - API and implementation complete)

## Implementation Status Summary

### Already Done (Backend)
- [x] VitecHubService with BasicAuth
- [x] get_departments() and get_employees() methods
- [x] OfficeService.sync_from_hub() with upsert logic
- [x] EmployeeService.sync_from_hub() with upsert logic
- [x] POST /api/offices/sync endpoint
- [x] POST /api/employees/sync endpoint
- [x] OfficeSyncResult and EmployeeSyncResult schemas
- [x] vitec_department_id and vitec_employee_id columns
- [x] Error handling for 401, 403, 429
- [x] Unit tests for sync endpoints

### Needs Verification
- [ ] VITEC_INSTALLATION_ID in Railway environment
- [ ] Production API credentials work
- [ ] Sync returns expected data

### Needs Implementation (Frontend)
- [ ] Admin UI page with sync buttons
- [ ] Loading states during sync
- [ ] Success/error toast notifications
- [ ] Display sync result counts
- [ ] Connection status indicator

### Needs Implementation (Polish)
- [ ] Logging for sync operations
- [ ] Consider dry-run mode for preview
