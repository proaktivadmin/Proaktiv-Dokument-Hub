# Entra ID Employee Sync & Email Signature Deployment

This document describes how to set up and use the Entra ID sync script to:

1. Sync employee profiles from the local database to Microsoft Entra ID
2. Upload profile photos to Entra ID
3. Deploy email signatures to Exchange Online

## Prerequisites

### Software Requirements

- **PowerShell 7+** - [Install PowerShell](https://aka.ms/powershell)
- **Python 3.12+** - [Install Python](https://python.org)
- **Microsoft Graph PowerShell SDK 2.0+**
- **Exchange Online Management 3.0+**

### Install PowerShell Modules

```powershell
# Install Microsoft Graph modules
Install-Module Microsoft.Graph.Authentication -Scope CurrentUser
Install-Module Microsoft.Graph.Users -Scope CurrentUser

# Install Exchange Online module
Install-Module ExchangeOnlineManagement -Scope CurrentUser
```

### Azure App Registration

You need an Azure App Registration with the following:

1. **API Permissions (Application type)**:
   - `User.ReadWrite.All` - Read/write user profiles
   - `Exchange.ManageAsApp` - Manage Exchange Online

2. **Authentication**:
   - Certificate (recommended for production)
   - OR Client Secret (for development/testing)

3. **Exchange Online Admin Role**:
   - The app needs "Exchange Administrator" role in Azure AD
   - OR use Application Access Policy in Exchange Online

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

### Example: Setting Environment Variables

**PowerShell:**
```powershell
$env:ENTRA_TENANT_ID = "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"
$env:ENTRA_CLIENT_ID = "yyyyyyyy-yyyy-yyyy-yyyy-yyyyyyyyyyyy"
$env:ENTRA_CLIENT_SECRET = "your-client-secret"
$env:ENTRA_ORGANIZATION = "proaktiv.onmicrosoft.com"
```

**Windows Command Prompt:**
```cmd
set ENTRA_TENANT_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
set ENTRA_CLIENT_ID=yyyyyyyy-yyyy-yyyy-yyyy-yyyyyyyyyyyy
set ENTRA_CLIENT_SECRET=your-client-secret
set ENTRA_ORGANIZATION=proaktiv.onmicrosoft.com
```

## Usage

### Quick Start (Windows)

```cmd
run-entra-sync.bat --dry-run
```

### PowerShell Direct

```powershell
# Dry run with single user (test mode)
.\backend\scripts\Sync-EntraIdEmployees.ps1 `
    -TenantId "xxx" `
    -ClientId "yyy" `
    -CertificateThumbprint "zzz" `
    -Organization "proaktiv.onmicrosoft.com" `
    -FilterEmail "ola@proaktiv.no" `
    -DryRun

# Full sync (all employees)
.\backend\scripts\Sync-EntraIdEmployees.ps1 `
    -TenantId "xxx" `
    -ClientId "yyy" `
    -CertificateThumbprint "zzz" `
    -Organization "proaktiv.onmicrosoft.com"

# Profile only (skip photos and signatures)
.\backend\scripts\Sync-EntraIdEmployees.ps1 `
    -TenantId "xxx" `
    -ClientId "yyy" `
    -CertificateThumbprint "zzz" `
    -Organization "proaktiv.onmicrosoft.com" `
    -SkipPhoto `
    -SkipSignature
```

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
| `-DryRun` | Preview changes only | False |
| `-Force` | Skip confirmation prompts | False |
| `-DelayMs` | Delay between API calls | 150 |
| `-LogPath` | Custom log file path | Auto-generated |

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
│  2. Update profile         │
│  3. Upload photo           │
│  4. Set email signature    │
└─────────────────────────────┘
      ↓
Microsoft Entra ID + Exchange Online
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

## Signature Templates

The email signature is built from templates in `backend/scripts/templates/`:

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

If roaming signatures are enabled, server-side signatures may be overridden. Check:
- Run `Get-OrganizationConfig | Select PostponeRoamingSignaturesUntilLater`
- If enabled, signatures set by this script will not appear

To disable roaming signatures:
```powershell
Set-OrganizationConfig -PostponeRoamingSignaturesUntilLater $true
```

### Logs

Logs are saved to `backend/logs/entra-sync-YYYY-MM-DD-HHMMSS.log`

View recent logs:
```powershell
Get-ChildItem backend/logs/entra-sync-*.log | Sort-Object LastWriteTime -Descending | Select-Object -First 5
```

## Security Considerations

1. **Never commit secrets** - Use environment variables or Key Vault
2. **Use certificates in production** - More secure than client secrets
3. **Least privilege** - Only grant required permissions
4. **Audit logging** - All changes are logged
5. **Dry run first** - Always preview before live sync

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
