# Phase 06: Entra ID Employee Sync & Signature Push - HANDOVER

**Created:** 2026-01-22
**Status:** Implementation Complete (Ready for Testing)
**Completed:** 2026-01-22

---

## MASTER PROMPT

You are implementing Phase 06: Entra ID Employee Sync & Signature Push.

**Objective:** Create a PowerShell tool that syncs employee data from the local PostgreSQL database (sourced from Vitec Next) to Microsoft Entra ID, and deploys email signatures to Exchange Online.

**Data Flow:**
```
Vitec Next → Proaktiv Scraper → PostgreSQL → This Script → Entra ID + Exchange Online
```

---

## CONTEXT FILES (READ FIRST)

1. `.planning/phases/06-entra-signature-sync/06-RESEARCH.md` - API research and data mappings
2. `backend/app/models/employee.py` - Employee model structure
3. `backend/app/models/office.py` - Office model structure
4. `backend/scripts/run_proaktiv_directory_sync.ps1` - Pattern to follow for PowerShell scripts

---

## EXECUTION ORDER

### Wave 1: Prerequisites
1. **06-01-PLAN.md** - Azure App Registration and setup documentation

### Wave 2: PowerShell Implementation (parallel)
2. **06-02-PLAN.md** - Main PowerShell sync script
3. **06-03-PLAN.md** - HTML signature template
4. **06-05-PLAN.md** - Backend API endpoints

### Wave 3: Frontend Foundation
5. **06-06-PLAN.md** - Frontend types, API client, hooks

### Wave 4: Frontend Components
6. **06-07-PLAN.md** - UI components (dialogs, previews)

### Wave 5: Integration
7. **06-08-PLAN.md** - Integrate into employees page with batch operations

### Wave 6: Testing
8. **06-04-PLAN.md** - Test scenarios and validation (PowerShell)

---

## KEY PATTERNS

### PowerShell Script Pattern (from run_proaktiv_directory_sync.ps1)

```powershell
<#
.SYNOPSIS
  Brief description.

.DESCRIPTION
  Full description with examples.

.EXAMPLE
  Example usage.
#>

[CmdletBinding()]
param(
  [ValidateSet("option1", "option2")]
  [string]$Param1 = "default",
  
  [switch]$DryRun,
  [switch]$Force
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

function Private-Function { }

try {
  # Main logic
}
finally {
  # Cleanup
}
```

### Database Query via Python Bridge

```powershell
$pythonScript = @"
import sys
sys.path.insert(0, '.')
from app.database import SessionLocal
from app.models.employee import Employee
from app.models.office import Office
import json

db = SessionLocal()
employees = db.query(Employee).filter(Employee.status == 'active').all()
result = [{'email': e.email, 'first_name': e.first_name, ...} for e in employees]
print(json.dumps(result))
db.close()
"@

$json = & py -3.12 -c $pythonScript
$employees = $json | ConvertFrom-Json
```

### Microsoft Graph Authentication

```powershell
# Certificate auth (preferred)
Connect-MgGraph -TenantId $TenantId -ClientId $ClientId -CertificateThumbprint $CertThumbprint

# Client secret auth
$secureSecret = ConvertTo-SecureString $ClientSecret -AsPlainText -Force
$credential = New-Object PSCredential($ClientId, $secureSecret)
Connect-MgGraph -TenantId $TenantId -ClientSecretCredential $credential
```

### Exchange Online Authentication

```powershell
# Certificate auth
Connect-ExchangeOnline -CertificateThumbprint $CertThumbprint -AppId $ClientId -Organization "proaktiv.onmicrosoft.com"
```

---

## DATA MAPPINGS

| Local DB | Entra ID |
|----------|----------|
| `first_name` | `givenName` |
| `last_name` | `surname` |
| `first_name + last_name` | `displayName` |
| `title` | `jobTitle` |
| `phone` | `mobilePhone` |
| `email` | (lookup key) |
| `profile_image_url` | User photo |
| `office.name` | `department` |
| `office.city` | `officeLocation` |

---

## CONSTRAINTS

1. **Safety First**
   - Always support `-DryRun` mode
   - Always support `-FilterEmail` for single-user testing
   - Never commit secrets to git
   - Use environment variables for sensitive data

2. **Rate Limiting**
   - Add delay between API calls (100-200ms minimum)
   - Implement retry with exponential backoff for 429 errors
   - Log all API calls for debugging

3. **Error Handling**
   - Continue on single-user failures (don't abort entire run)
   - Log all errors with context
   - Generate summary report at end

4. **Roaming Signatures**
   - Check if enabled before signature push
   - Warn user if roaming signatures will override

---

## TESTING CHECKLIST

### PowerShell Script (run `/entra-qa`)
- [ ] Database connectivity works (local)
- [ ] Database connectivity works (Railway)
- [ ] Microsoft Graph authentication works
- [ ] Exchange Online authentication works
- [ ] Single user profile sync works
- [ ] Single user photo upload works
- [ ] Single user signature push works
- [ ] Dry-run mode shows accurate preview
- [ ] Rate limiting prevents throttling
- [ ] Error handling continues on failure
- [ ] Summary report generated

### Frontend UI
- [ ] EntraConnectionStatus shows correct state
- [ ] Signature preview dialog renders HTML
- [ ] Single employee sync from dropdown works
- [ ] Batch selection mode activates
- [ ] Batch sync dialog shows progress
- [ ] Success/error toasts display

---

## COMMON PITFALLS

1. **Roaming Signatures Enabled**
   - Signatures set via PowerShell won't appear if roaming signatures are enabled
   - Solution: Disable with `Set-OrganizationConfig -PostponeRoamingSignaturesUntilLater $true`

2. **User Not Found in Entra ID**
   - Email in database may not match UPN in Entra ID
   - Solution: Try matching by mail property, not just UPN

3. **Photo Upload Fails**
   - Photo URL may be invalid or return 404
   - Solution: Validate URL before download, skip on failure

4. **Permission Denied**
   - Missing admin consent or Exchange role
   - Solution: Re-check Azure Portal permissions

5. **Rate Limiting (429)**
   - Too many requests too fast
   - Solution: Add delay, implement exponential backoff

---

## FILES CREATED

### PowerShell Scripts (Wave 2) ✅
| File | Description | Status |
|------|-------------|--------|
| `backend/scripts/Sync-EntraIdEmployees.ps1` | Main sync script | ✅ |
| `backend/scripts/templates/email-signature.html` | HTML signature template | ✅ |
| `backend/scripts/templates/email-signature.txt` | Plain text signature | ✅ |
| `run-entra-sync.bat` | Windows launcher | ✅ |
| `docs/entra-signature-sync.md` | User documentation | ✅ |

### Backend API (Wave 2) ✅
| File | Description | Status |
|------|-------------|--------|
| `backend/app/schemas/entra_sync.py` | Pydantic schemas | ✅ |
| `backend/app/services/entra_sync_service.py` | Business logic | ✅ |
| `backend/app/routers/entra_sync.py` | FastAPI endpoints | ✅ |
| `backend/app/config.py` | Entra ID settings added | ✅ |
| `backend/app/main.py` | Router registered | ✅ |

### Frontend (Waves 3-5) ✅
| File | Description | Status |
|------|-------------|--------|
| `frontend/src/types/entra-sync.ts` | TypeScript interfaces | ✅ |
| `frontend/src/lib/api/entra-sync.ts` | API client | ✅ |
| `frontend/src/hooks/useEntraSync.ts` | React hook | ✅ |
| `frontend/src/components/employees/EntraConnectionStatus.tsx` | Status indicator | ✅ |
| `frontend/src/components/employees/SignaturePreviewDialog.tsx` | Signature preview | ✅ |
| `frontend/src/components/employees/EntraSyncDialog.tsx` | Single sync dialog | ✅ |
| `frontend/src/components/employees/EntraSyncBatchDialog.tsx` | Batch sync dialog | ✅ |
| `frontend/src/components/employees/EmployeeCard.tsx` | Selection + Entra menu | ✅ |
| `frontend/src/components/employees/EmployeeGrid.tsx` | Batch selection mode | ✅ |
| `frontend/src/app/employees/page.tsx` | Dialogs wired up | ✅ |
| `frontend/src/components/ui/progress.tsx` | Progress component added | ✅ |

---

## COMPLETION CRITERIA

Phase 06 is complete when:
1. All files created and working
2. Test scenarios in 06-04-PLAN.md pass
3. Documentation complete
4. At least one real user synced successfully (PowerShell)
5. Frontend UI works end-to-end:
   - Single employee sync from card dropdown
   - Batch sync from multi-select
   - Signature preview renders correctly
   - Success/error toasts display
6. HANDOVER.md updated with "COMPLETED" status

---

## RELATED PHASES

**Phase 07: Office Enhancements & SalesScreen** (separate development cycle)
- Office regions
- Office merge tool
- SalesScreen employee sync
- See: `.planning/phases/07-office-enhancements/`
