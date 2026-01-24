# Entra ID Employee Sync - Read-Only Audit

This document describes how to set up and use the Entra ID sync script in read-only audit mode. It compares local employee data with Entra ID and reports changes that would be applied. Writes to Entra ID or Exchange Online are forbidden.

## Read-Only Policy (Writes Forbidden)

- Update-MgUser, Set-MgUserPhotoContent, and Set-MailboxMessageConfiguration are not allowed
- Write mode is blocked unless `ENTRA_ALLOW_WRITES=true` and `-AllowWrites` are explicitly set (future only)

## Prerequisites

### Software Requirements

- **PowerShell 7+** - [Install PowerShell](https://aka.ms/powershell)
- **Python 3.12+** - [Install Python](https://python.org)
- **Microsoft Graph PowerShell SDK 2.0+**
- **Exchange Online Management 3.0+** (optional; write mode only, currently forbidden)

### Install PowerShell Modules

```powershell
# Install Microsoft Graph modules
Install-Module Microsoft.Graph.Authentication -Scope CurrentUser
Install-Module Microsoft.Graph.Users -Scope CurrentUser

# Install Exchange Online module (write mode only; currently forbidden)
Install-Module ExchangeOnlineManagement -Scope CurrentUser
```

### Azure App Registration

You need an Azure App Registration with the following:

1. **API Permissions (Application type)**:
   - `User.Read.All` - Read user profiles
   - Do **NOT** grant `User.ReadWrite.All` or `Exchange.ManageAsApp` until write mode is approved

2. **Authentication**:
   - Certificate (recommended for production)
   - OR Client Secret (for development/testing)

3. **Exchange Online Admin Role**:
   - Not required in read-only mode
   - Only needed if write mode is approved in the future

See `.planning/phases/06-entra-signature-sync/06-01-PLAN.md` for detailed setup instructions.

## Configuration

### Environment Variables

Set these environment variables before running:

| Variable | Description | Required |
|----------|-------------|----------|
| `ENTRA_TENANT_ID` | Azure AD tenant ID (GUID) | Yes |
| `ENTRA_CLIENT_ID` | App registration client ID (GUID) | Yes |
| `ENTRA_CLIENT_SECRET` | Client secret (if not using certificate) | Conditional |
| `ENTRA_CERT_THUMBPRINT` | Certificate thumbprint (if not using secret) | Conditional |
| `ENTRA_ORGANIZATION` | Microsoft 365 domain (e.g., `proaktiv.onmicrosoft.com`) | Yes |
| `DATABASE_URL` | PostgreSQL connection string | No (uses backend/.env) |
| `ENTRA_ALLOW_WRITES` | Enable write mode (future only) | No (must remain unset) |

### Example: Setting Environment Variables

**PowerShell:**
```powershell
$env:ENTRA_TENANT_ID = "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
$env:ENTRA_CLIENT_ID = "yyyyyyyy-yyyy-yyyy-yyyy-yyyyyyyyyyyy"
$env:ENTRA_CLIENT_SECRET = "your-client-secret"
$env:ENTRA_ORGANIZATION = "proaktiv.onmicrosoft.com"
# Do NOT set ENTRA_ALLOW_WRITES in read-only mode
```

**Windows Command Prompt:**
```cmd
set ENTRA_TENANT_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
set ENTRA_CLIENT_ID=yyyyyyyy-yyyy-yyyy-yyyy-yyyyyyyyyyyy
set ENTRA_CLIENT_SECRET=your-client-secret
set ENTRA_ORGANIZATION=proaktiv.onmicrosoft.com
rem Do NOT set ENTRA_ALLOW_WRITES in read-only mode
```

## Usage

### Quick Start (Windows)

```cmd
run-entra-sync.bat
```

### PowerShell Direct

```powershell
# Read-only audit with single user (test mode)
.\backend\scripts\Sync-EntraIdEmployees.ps1 `
    -TenantId "xxx" `
    -ClientId "yyy" `
    -CertificateThumbprint "zzz" `
    -Organization "proaktiv.onmicrosoft.com" `
    -FilterEmail "ola@proaktiv.no" `
    -DryRun

# Profile comparison only (skip photos and signatures)
.\backend\scripts\Sync-EntraIdEmployees.ps1 `
    -TenantId "xxx" `
    -ClientId "yyy" `
    -CertificateThumbprint "zzz" `
    -Organization "proaktiv.onmicrosoft.com" `
    -SkipPhoto `
    -SkipSignature
```

### Entra Import (Read-Only, DB only)

This import reads Entra ID users and stores them as secondary fields on employees.
It never writes to Entra ID.

```powershell
# Full import
py -3.12 .\backend\scripts\import_entra_employees.py

# Dry run (no DB writes)
py -3.12 .\backend\scripts\import_entra_employees.py --dry-run

# Single user
py -3.12 .\backend\scripts\import_entra_employees.py --filter-email "user@proaktiv.no"
```

### UI Trigger (Employees page)

The Employees page includes a **Hent Entra** button in the header.
It calls `/entra-sync/import` and refreshes the list with updated Entra fields.

### Parameters

| Parameter | Description | Default |
|-----------|-------------|---------|
| `-TenantId` | Azure AD tenant ID | Required |
| `-ClientId` | App registration client ID | Required |
| `-CertificateThumbprint` | Certificate thumbprint | Required* |
| `-ClientSecret` | Client secret | Required* |
| `-Organization` | Microsoft 365 domain | Required |
| `-FilterEmail` | Process only this email | All employees |
| `-SkipProfile` | Skip profile updates | False |
| `-SkipPhoto` | Skip photo uploads | False |
| `-SkipSignature` | Skip signature deployment | False |
| `-DryRun` | Force read-only mode | False |
| `-Force` | Skip confirmation prompts | False |
| `-DelayMs` | Delay between API calls | 150 |
| `-LogPath` | Custom log file path | Auto-generated |
| `-AllowWrites` | **FORBIDDEN** unless explicitly approved | False |

*Either `-CertificateThumbprint` or `-ClientSecret` is required.

## Data Flow

```
Vitec Next API
      ↓
Proaktiv Directory Scraper (run-proaktiv-scraper.bat)
      ↓
PostgreSQL Database (employees + offices)
      ↓
Sync-EntraIdEmployees.ps1
      ↓
┌─────────────────────────────┐
│  For each employee:        │
│  1. Find in Entra ID       │
│  2. Compare profile fields │
│  3. Report photo changes   │
│  4. Preview signature      │
└─────────────────────────────┘
      ↓
Microsoft Entra ID + Exchange Online
```

## Entra Import Flow (Read-Only)

```
Microsoft Graph (Entra ID)
      ↓
import_entra_employees.py (GET only)
      ↓
PostgreSQL: employees.entra_* (secondary fields)
      ↓
UI bubbles + Entra panel
```

## Field Mappings

| Local Database | Entra ID Property |
|----------------|-------------------|
| `first_name` | `givenName` |
| `last_name` | `surname` |
| `first_name + last_name` | `displayName` |
| `title` | `jobTitle` |
| `phone` | `mobilePhone` |
| `office.name` | `department` |
| `office.city` | `officeLocation` |
| `office.street_address` | `streetAddress` |
| `office.postal_code` | `postalCode` |
| (constant) | `country` = "NO" |

## Entra Snapshot Fields (Secondary)

Stored on `employees` as read-only Entra snapshots:
- `entra_user_id`, `entra_upn`, `entra_mail`
- `entra_display_name`, `entra_given_name`, `entra_surname`
- `entra_job_title`, `entra_mobile_phone`
- `entra_department`, `entra_office_location`, `entra_street_address`, `entra_postal_code`, `entra_country`
- `entra_account_enabled`
- `entra_mismatch_fields`, `entra_last_synced_at`

Vitec Next remains the primary source of truth; Entra values are secondary.

## Signature Templates

The email signature is built from templates in `backend/scripts/templates/` (read-only mode uses this for preview only; no signatures are deployed):

- `email-signature.html` - HTML signature (for rich email clients)
- `email-signature.txt` - Plain text signature (fallback)

### Template Variables

| Variable | Source |
|----------|--------|
| `{{DisplayName}}` | `first_name + " " + last_name` |
| `{{JobTitle}}` | `title` |
| `{{Email}}` | `email` |
| `{{MobilePhone}}` | `phone` |
| `{{OfficeName}}` | `office.name` |
| `{{OfficeAddress}}` | `office.street_address` |
| `{{OfficePostal}}` | `office.postal_code + " " + office.city` |
| `{{OfficePhone}}` | `office.phone` |
| `{{OfficeEmail}}` | `office.email` |

### Customizing Templates

1. Edit the template files in `backend/scripts/templates/`
2. Use the variables above for dynamic content
3. Keep HTML simple (tables, inline CSS) for email client compatibility
4. Maximum size: 10KB

## Troubleshooting

### Exit Codes

| Code | Meaning | Action |
|------|---------|--------|
| 0 | Success | All users processed |
| 1 | Partial success | Some users skipped/failed |
| 2 | Authentication failure | Check credentials/permissions |
| 3 | Database failure | Check DATABASE_URL |
| 4 | Invalid parameters | Check command line |
| 5 | Missing dependencies | Install required modules |

### Common Issues

#### "User not found in Entra ID"

The email in the database doesn't match any user in Entra ID. Check:
- Is the email correct in the database?
- Does the user exist in Entra ID with this email as UPN or mail property?

#### "Permission denied"

The app registration doesn't have the required permissions. Check:
- API permissions are granted admin consent
- Exchange Administrator role is assigned

#### "Photo upload failed"

The profile image URL may be invalid or the image too large. Check:
- Is the URL accessible?
- Is the image less than 4MB?

#### Signatures not appearing

Expected in read-only mode. Signatures are never deployed until write mode is approved.

### Logs

Logs are saved to `backend/logs/entra-sync-YYYY-MM-DD-HHMMSS.log`

View recent logs:
```powershell
Get-ChildItem backend/logs/entra-sync-*.log | Sort-Object LastWriteTime -Descending | Select-Object -First 5
```

## Security Considerations

1. **Never commit secrets** - Use environment variables or Key Vault
2. **Use certificates in production** - More secure than client secrets
3. **Least privilege** - Read-only permissions until write mode is approved
4. **Audit logging** - All comparisons are logged
5. **Writes disabled** - Write mode is forbidden by policy

## UI Status Indicators

Employee cards and detail pages show:
- **Green bubble** = Vitec (primary source)
- **Blue bubble** = Entra (secondary source)
- Amber ring indicates mismatch between sources

## Related Commands

| Command | Description |
|---------|-------------|
| `/scrape-proaktiv` | Sync offices/employees from proaktiv.no |
| `/entra-architect` | Design Entra ID sync specification |
| `/entra-builder` | Build Entra ID sync implementation |
| `/entra-qa` | Test Entra ID sync |

## See Also

- [Proaktiv Directory Sync](proaktiv-directory-sync.md)
- [06-RESEARCH.md](.planning/phases/06-entra-signature-sync/06-RESEARCH.md)
- [Microsoft Graph API Reference](https://learn.microsoft.com/en-us/graph/api/overview)
- [Exchange Online PowerShell](https://learn.microsoft.com/en-us/powershell/exchange/exchange-online-powershell)
