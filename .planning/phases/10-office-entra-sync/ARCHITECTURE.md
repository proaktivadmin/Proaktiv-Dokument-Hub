# Office Entra ID Sync - Architecture Document

## System Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                         Proaktiv Dokument Hub                           │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  ┌─────────────┐         ┌─────────────┐         ┌─────────────────┐   │
│  │  Vitec Next │ ──────► │  PostgreSQL │ ◄────── │ Microsoft Graph │   │
│  │  (Primary)  │         │  (Storage)  │         │   (Secondary)   │   │
│  └─────────────┘         └─────────────┘         └─────────────────┘   │
│        │                       │                         │              │
│        │ Scraper               │ SQLAlchemy              │ Graph API   │
│        ▼                       ▼                         ▼              │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                     Office Model                                 │   │
│  │  ┌─────────────────────┐   ┌──────────────────────────────────┐ │   │
│  │  │   Vitec Fields      │   │      Entra Fields (Secondary)    │ │   │
│  │  │   ---------------   │   │   ----------------------------   │ │   │
│  │  │   name              │   │   entra_group_id                 │ │   │
│  │  │   email             │   │   entra_group_name               │ │   │
│  │  │   phone             │   │   entra_group_mail               │ │   │
│  │  │   city              │   │   entra_group_description        │ │   │
│  │  │   ...               │   │   entra_sharepoint_url           │ │   │
│  │  └─────────────────────┘   │   entra_member_count             │ │   │
│  │                            │   entra_mismatch_fields          │ │   │
│  │                            │   entra_last_synced_at           │ │   │
│  │                            └──────────────────────────────────┘ │   │
│  └─────────────────────────────────────────────────────────────────┘   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Data Flow

### Import Flow (Entra → DB)

```
┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│  Microsoft Graph │ ──► │  Import Script   │ ──► │    PostgreSQL    │
│    (Groups API)  │     │  (Python)        │     │  (entra_* cols)  │
└──────────────────┘     └──────────────────┘     └──────────────────┘
        │                        │                        │
        │ GET /groups            │ Match by email         │ UPDATE offices
        │                        │ Compute mismatches     │ SET entra_*
        ▼                        ▼                        ▼
   Unified Groups          Office records           Entra snapshot
```

### Display Flow (DB → UI)

```
┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│    PostgreSQL    │ ──► │   FastAPI        │ ──► │   React UI       │
│  (Office model)  │     │   (Endpoints)    │     │   (Components)   │
└──────────────────┘     └──────────────────┘     └──────────────────┘
        │                        │                        │
        │ All fields             │ JSON response          │ Status bubbles
        │ (vitec + entra)        │                        │ Entra section
        ▼                        ▼                        ▼
   Full office data         API response            Visual indicators
```

---

## Matching Algorithm

### Priority Order

1. **Email Exact Match** (highest confidence)
   ```python
   # Group mail matches office email exactly
   group.mail.lower() == office.email.lower()
   # Example: "bergen@proaktiv.no" == "bergen@proaktiv.no"
   ```

2. **Email Prefix Match** (high confidence)
   ```python
   # Group mail prefix matches office short_code
   group.mail.split('@')[0].lower() == office.short_code.lower()
   # Example: "bergen@proaktiv.no" → "bergen" == "BERG" → no match
   # But: "bergen@proaktiv.no" → "bergen" == "bergen" → match
   ```

3. **Name Contains City** (medium confidence)
   ```python
   # Group displayName contains office city
   office.city.lower() in group.displayName.lower()
   # Example: "Proaktiv Bergen Team" contains "Bergen"
   ```

4. **Name Contains Office Name** (low confidence)
   ```python
   # Group displayName contains office name
   office.name.lower() in group.displayName.lower()
   # Example: "Bergen Eiendom Team" contains "Bergen"
   ```

### Match Resolution

```python
def find_matching_office(group: dict, offices: list[Office]) -> Office | None:
    # 1. Try email exact match
    for office in offices:
        if office.email and group.get('mail'):
            if office.email.lower() == group['mail'].lower():
                return office
    
    # 2. Try email prefix match
    group_prefix = group.get('mail', '').split('@')[0].lower()
    for office in offices:
        if office.email:
            office_prefix = office.email.split('@')[0].lower()
            if office_prefix == group_prefix:
                return office
    
    # 3. Try city match
    for office in offices:
        if office.city:
            if office.city.lower() in group.get('displayName', '').lower():
                return office
    
    # 4. No match found
    return None
```

---

## Mismatch Detection

### Fields to Compare

| Vitec Field | Entra Field | Normalization |
|-------------|-------------|---------------|
| `name` | `displayName` | Case-insensitive, trim |
| `email` | `mail` | Lowercase, trim |
| `description` | `description` | Trim |

### Mismatch Computation

```python
def compute_mismatch_fields(office: Office, group: dict) -> list[str]:
    mismatches = []
    
    def check(field: str, vitec: str | None, entra: str | None) -> None:
        if not vitec or not entra:
            return
        if vitec.strip().lower() != entra.strip().lower():
            mismatches.append(field)
    
    check("name", office.name, group.get("displayName"))
    check("email", office.email, group.get("mail"))
    check("description", office.description, group.get("description"))
    
    return mismatches
```

---

## API Endpoints

### New Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/api/entra-sync/import-offices` | Import M365 Groups |

### Existing Endpoints (Modified)

| Method | Path | Change |
|--------|------|--------|
| `GET` | `/api/offices` | Include `entra_*` fields |
| `GET` | `/api/offices/{id}` | Include `entra_*` fields |

---

## Schema Design

### Pydantic Schemas

```python
# Request
class EntraOfficeImportRequest(BaseModel):
    dry_run: bool = False
    filter_office_id: UUID | None = None

# Response
class EntraOfficeImportResult(BaseModel):
    success: bool
    dry_run: bool
    offices_loaded: int | None
    matched_updated: int | None
    offices_not_matched: int | None
    groups_not_matched: int | None
    error: str | None
```

### Office Response Extension

```python
# Added to OfficeResponse
class OfficeResponse(BaseModel):
    # ... existing fields ...
    
    # Entra ID sync fields (secondary)
    entra_group_id: str | None
    entra_group_name: str | None
    entra_group_mail: str | None
    entra_group_description: str | None
    entra_sharepoint_url: str | None
    entra_member_count: int | None
    entra_mismatch_fields: list[str] | None
    entra_last_synced_at: datetime | None
```

---

## Component Design

### OfficeCard Status Bubbles

```tsx
// Status bubble logic (same pattern as EmployeeCard)
const entraHasData = Boolean(office.entra_group_id);
const mismatchCount = office.entra_mismatch_fields?.length ?? 0;
const entraStatus = !entraHasData ? "missing" : mismatchCount > 0 ? "mismatch" : "match";

// Bubble classes
const bubbleClass = (source: "entra" | "vitec", state: string) => {
  const baseColor = source === "entra" ? "bg-sky-500" : "bg-emerald-500";
  // ... same logic as EmployeeCard
};
```

### Office Detail Entra Section

```tsx
// Similar to Employee Entra section
<section className="border rounded-lg p-4">
  <h3 className="text-sm font-medium text-muted-foreground mb-3">
    Entra ID (sekundær)
  </h3>
  
  {office.entra_group_id ? (
    <dl className="grid grid-cols-2 gap-2 text-sm">
      <dt className="text-muted-foreground">M365 Gruppe</dt>
      <dd>{office.entra_group_name}</dd>
      
      <dt className="text-muted-foreground">Gruppe-ID</dt>
      <dd className="font-mono text-xs">{office.entra_group_id}</dd>
      
      {/* ... more fields */}
    </dl>
  ) : (
    <p className="text-sm text-muted-foreground italic">
      Ikke synkronisert med Entra ID
    </p>
  )}
</section>
```

---

## Error Handling

### Graph API Errors

| Error | Handling |
|-------|----------|
| 401 Unauthorized | Log error, return failure with auth message |
| 403 Forbidden | Check Group.Read.All permission |
| 429 Rate Limited | Implement retry with backoff |
| 5xx Server Error | Log and retry once |

### Matching Errors

| Scenario | Handling |
|----------|----------|
| Multiple groups match one office | Use first match by email priority |
| No groups match | Leave entra_* fields null |
| Office already has entra_group_id | Update with new data |

---

## Security Considerations

1. **Read-Only**: No writes to Entra ID
2. **Credential Storage**: Use environment variables only
3. **Logging**: Never log access tokens or secrets
4. **Rate Limiting**: Respect Graph API throttling

---

## Testing Strategy

### Unit Tests
- Matching algorithm with various input patterns
- Mismatch detection logic

### Integration Tests
- Mock Graph API responses
- Database updates

### Manual Testing
- Dry-run import
- UI visual inspection
- Error scenarios

---

## Future Enhancements (Out of Scope)

1. **Member Sync Validation** - Compare group members with office employees
2. **Write Capabilities** - Add/remove group members (requires approval)
3. **SharePoint Integration** - Link to team document libraries
4. **Automated Sync** - Scheduled background sync
