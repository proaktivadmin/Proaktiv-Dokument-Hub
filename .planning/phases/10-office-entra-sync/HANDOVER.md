# Phase 10: Office Entra ID Sync - Handover

## Completion Status

| Task | Status | Notes |
|------|--------|-------|
| Database migration | ✅ Complete | 8 columns added to offices table |
| Office model update | ✅ Complete | Entra fields in SQLAlchemy model |
| Pydantic schemas | ✅ Complete | Request/response schemas for import |
| Import script | ✅ Complete | CLI with dry-run, filter, fetch-details |
| Service method | ✅ Complete | `import_entra_offices()` in EntraSyncService |
| API endpoint | ✅ Complete | POST `/api/entra-sync/import-offices` |
| Frontend types | ✅ Complete | TypeScript interfaces for Office + Import |
| API client | ✅ Complete | `entraSyncApi.importOffices()` |
| OfficeCard status bubbles | ✅ Complete | Green (Vitec) + Blue (Entra) bubbles |
| Office detail Entra section | ✅ Complete | Shows M365 Group data |
| "Hent Entra" button | ✅ Complete | On offices list page |
| Backend tests | ✅ Complete | 2 tests passing |
| QA verification | ✅ Complete | All linting/typecheck passes |

---

## Files Created/Modified

### Backend - New Files

| File | Description |
|------|-------------|
| `backend/alembic/versions/20260124_0004_add_office_entra_columns.py` | Alembic migration adding 8 entra columns |
| `backend/scripts/import_entra_offices.py` | CLI script for importing M365 Groups |
| `backend/tests/test_entra_sync_office_import.py` | Unit tests for import endpoint |

### Backend - Modified Files

| File | Changes |
|------|---------|
| `backend/app/models/office.py` | Added 8 `entra_*` columns and index |
| `backend/app/schemas/office.py` | Added entra fields to `OfficeResponse` |
| `backend/app/schemas/entra_sync.py` | Added `EntraOfficeImportRequest/Result` schemas |
| `backend/app/services/entra_sync_service.py` | Added `import_entra_offices()` method |
| `backend/app/routers/entra_sync.py` | Added `POST /import-offices` endpoint |

### Frontend - Modified Files

| File | Changes |
|------|---------|
| `frontend/src/types/v3/index.ts` | Added 8 entra fields to `Office` interface |
| `frontend/src/types/entra-sync.ts` | Added `EntraOfficeImportRequest/Result` types |
| `frontend/src/lib/api/entra-sync.ts` | Added `importOffices()` API method |
| `frontend/src/components/offices/OfficeCard.tsx` | Added Vitec/Entra status bubbles |
| `frontend/src/components/offices/OfficeGrid.tsx` | Added "Hent Entra" button |
| `frontend/src/app/offices/page.tsx` | Added Entra import handler |
| `frontend/src/app/offices/[id]/page.tsx` | Added "Entra ID (sekundær)" section |

---

## Database Schema

### New Columns in `offices` Table

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

### Index

- `idx_offices_entra_group_id` on `entra_group_id`

---

## Usage

### Run Office Entra Import

**From CLI:**
```bash
cd backend
export DATABASE_URL="..."
export ENTRA_TENANT_ID="..."
export ENTRA_CLIENT_ID="..."
export ENTRA_CLIENT_SECRET="..."

# Dry run (preview only)
python scripts/import_entra_offices.py --dry-run

# Actual import
python scripts/import_entra_offices.py

# With additional details (member count, SharePoint URL)
python scripts/import_entra_offices.py --fetch-details

# JSON output for scripting
python scripts/import_entra_offices.py --json
```

**From API:**
```bash
curl -X POST http://localhost:8000/api/entra-sync/import-offices \
  -H "Content-Type: application/json" \
  -d '{"dry_run": false}'
```

**From UI:**
1. Navigate to `/offices`
2. Click "Hent Entra" button
3. Wait for toast notification with results

---

## Required Permissions

The Entra app registration needs:
- `Group.Read.All` (Application permission)

For SharePoint URLs and member counts with `--fetch-details`:
- `Sites.Read.All` (Application permission) - for SharePoint
- No additional permissions for member count (uses /members/$count)

---

## Matching Algorithm

Groups are matched to offices using priority order:

1. **Email exact match** (highest confidence)
   - `group.mail.lower() == office.email.lower()`

2. **Email prefix match**
   - `group.mail.split('@')[0] == office.email.split('@')[0]`

3. **City name in group name**
   - `office.city.lower() in group.displayName.lower()`

4. **Office name in group name**
   - `office.name.lower() in group.displayName.lower()`

---

## Visual Indicators

Following the EmployeeCard pattern:

| Bubble | Color | Meaning |
|--------|-------|---------|
| Green | `bg-emerald-500` | Vitec data (primary source) |
| Blue | `bg-sky-500` | Entra data (secondary source) |
| Amber ring | `ring-amber-500` | Mismatch detected |
| Faded | `opacity-30` | No sync data |

---

## Known Limitations

1. **Matching is heuristic** - Based on email/name patterns; may need manual override for edge cases
2. **SharePoint/member count are optional** - Require `--fetch-details` flag (slower due to additional API calls)
3. **Read-only** - No writes to Entra ID; data flows one-way (Entra → DB)
4. **No scheduled sync** - Must be triggered manually via UI or CLI

---

## Future Enhancements (Out of Scope)

1. **Member sync validation** - Compare group members with office employees
2. **Manual group ID override** - Allow setting `entra_group_id` manually in UI
3. **Scheduled background sync** - Cron job for periodic updates
4. **Write capabilities** - Add/remove group members (requires additional permissions)

---

## QA Results

| Check | Result |
|-------|--------|
| Backend ruff lint | ✅ PASS (All checks passed) |
| Backend pyright | ✅ PASS (0 errors) |
| Frontend ESLint | ✅ PASS (0 errors, 28 warnings - all pre-existing) |
| Frontend TypeScript | ✅ PASS (no errors) |
| Office model columns | ✅ PASS (8 entra columns verified) |
| Backend tests | ✅ PASS (2/2 tests) |

---

## Railway Migration Reminder

**IMPORTANT**: The migration must be applied to Railway manually. Railway's deployment does NOT reliably run migrations.

```powershell
# Use the PUBLIC database URL (not internal!)
$env:DATABASE_URL = "postgresql://postgres:PASSWORD@shuttle.proxy.rlwy.net:51557/railway"
cd backend
python -m alembic upgrade head
python -m alembic current  # Verify: should show 20260124_0004 (head)
```

If migration fails or columns don't appear, use the fallback script:
```sql
ALTER TABLE offices ADD COLUMN IF NOT EXISTS entra_group_id VARCHAR(64);
ALTER TABLE offices ADD COLUMN IF NOT EXISTS entra_group_name VARCHAR(255);
ALTER TABLE offices ADD COLUMN IF NOT EXISTS entra_group_mail VARCHAR(255);
ALTER TABLE offices ADD COLUMN IF NOT EXISTS entra_group_description TEXT;
ALTER TABLE offices ADD COLUMN IF NOT EXISTS entra_sharepoint_url TEXT;
ALTER TABLE offices ADD COLUMN IF NOT EXISTS entra_member_count INTEGER;
ALTER TABLE offices ADD COLUMN IF NOT EXISTS entra_mismatch_fields JSONB NOT NULL DEFAULT '[]';
ALTER TABLE offices ADD COLUMN IF NOT EXISTS entra_last_synced_at TIMESTAMPTZ;
CREATE INDEX IF NOT EXISTS idx_offices_entra_group_id ON offices(entra_group_id);
```

---

## Completion Summary

Phase 10 (Office Entra ID Sync) is complete and ready for production deployment.

**Key Features Delivered:**
- Fetch M365 Groups from Microsoft Graph API
- Match groups to offices by email/name patterns
- Store Entra data in secondary columns (Vitec remains primary source)
- Visual status bubbles on OfficeCard (green=Vitec, blue=Entra)
- "Entra ID (sekundær)" section on office detail page
- "Hent Entra" button for triggering imports
- Norwegian UI labels throughout

**Ready for Production:** YES

---

*Completed: 2026-01-24*
