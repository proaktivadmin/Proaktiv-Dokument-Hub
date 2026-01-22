# Phase 06: Entra ID Employee Sync & Signature Push - RESEARCH

**Created:** 2026-01-22
**Status:** Research Complete

---

## Overview

This phase implements a 2-way sync between the local PostgreSQL database (sourced from Vitec Next) and Microsoft Entra ID, plus email signature deployment to Exchange Online.

**Data Flow:**
```
Vitec Next → Proaktiv Scraper → PostgreSQL → Sync Script → Entra ID + Exchange Online
```

---

## Microsoft Graph API Capabilities

### User Profile Updates

**Endpoint:** `PATCH https://graph.microsoft.com/v1.0/users/{id}`

**Updatable Properties:**

| Property | Type | Description |
|----------|------|-------------|
| `givenName` | String | First name |
| `surname` | String | Last name |
| `displayName` | String | Full display name |
| `jobTitle` | String | Job title |
| `mobilePhone` | String | Mobile phone number |
| `businessPhones` | String[] | Office phone (only one allowed) |
| `department` | String | Department name |
| `officeLocation` | String | Office location/city |
| `streetAddress` | String | Street address |
| `city` | String | City |
| `postalCode` | String | Postal code |
| `country` | String | Country (e.g., "NO") |

**PowerShell Command:**
```powershell
Update-MgUser -UserId $userId -BodyParameter @{
    givenName = "Ola"
    surname = "Nordmann"
    displayName = "Ola Nordmann"
    jobTitle = "Eiendomsmegler"
    mobilePhone = "+47 999 88 777"
    department = "Stavanger"
    officeLocation = "Stavanger"
}
```

### Profile Photo Upload

**Endpoint:** `PUT https://graph.microsoft.com/v1.0/users/{id}/photo/$value`

**Constraints:**
- Maximum size: 4 MB
- Supported formats: JPEG, PNG, GIF
- Syncs to Exchange Online (one-time, not auto-updating)

**PowerShell Command:**
```powershell
Set-MgUserPhotoContent -UserId $userId -InFile "C:\temp\photo.jpg"
```

---

## Exchange Online Signature Management

### Set-MailboxMessageConfiguration

**Key Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `-Identity` | String | User email or mailbox ID |
| `-SignatureHtml` | String | HTML signature content |
| `-SignatureText` | String | Plain text signature |
| `-AutoAddSignature` | Boolean | Auto-add to new messages |
| `-AutoAddSignatureOnReply` | Boolean | Auto-add to replies |
| `-AutoAddSignatureOnMobile` | Boolean | Auto-add on mobile |
| `-SignatureTextOnMobile` | String | Mobile-specific signature |

**Example:**
```powershell
Set-MailboxMessageConfiguration -Identity "ola@proaktiv.no" `
    -SignatureHtml $htmlSignature `
    -AutoAddSignature $true `
    -AutoAddSignatureOnReply $true
```

### Roaming Signatures Consideration

**Important:** If Outlook Roaming Signatures is enabled in the tenant, `Set-MailboxMessageConfiguration` will NOT work for signature management.

**Check Status:**
```powershell
Get-OrganizationConfig | Select-Object PostponeRoamingSignaturesUntilLater
```

**Disable Roaming Signatures (if needed):**
```powershell
Set-OrganizationConfig -PostponeRoamingSignaturesUntilLater $true
```

This allows PowerShell-managed signatures to work until Microsoft provides an admin API for roaming signatures.

---

## Required Permissions

### Azure App Registration Permissions

| Permission | Type | Purpose |
|------------|------|---------|
| `User.ReadWrite.All` | Application | Update user profiles |
| `User.Read.All` | Application | Read user list for matching |
| `Exchange.ManageAsApp` | Application | Manage Exchange Online settings |

### Exchange Online Roles

The app's service principal needs one of these roles:
- **Exchange Administrator** - Full Exchange access
- **Exchange Recipient Administrator** - Mailbox management only (sufficient for signatures)

### Granting Exchange Permissions

```powershell
# Connect to Exchange Online
Connect-ExchangeOnline

# Get the service principal
$servicePrincipal = Get-MgServicePrincipal -Filter "displayName eq 'Proaktiv Entra Sync'"

# Assign Exchange role
New-ManagementRoleAssignment -Role "Exchange Recipient Administrator" `
    -App $servicePrincipal.AppId `
    -Name "Proaktiv Entra Sync - Exchange"
```

---

## Data Mapping: Local DB → Entra ID

| Local DB Field | Table | Entra ID Property |
|----------------|-------|-------------------|
| `first_name` | employees | `givenName` |
| `last_name` | employees | `surname` |
| `first_name + last_name` | employees | `displayName` |
| `title` | employees | `jobTitle` |
| `phone` | employees | `mobilePhone` |
| `email` | employees | (lookup key - UPN match) |
| `profile_image_url` | employees | User photo (download & upload) |
| `name` | offices | `department` |
| `city` | offices | `officeLocation` |
| `street_address` | offices | `streetAddress` |
| `postal_code` | offices | `postalCode` |

### Signature Template Variables

| Variable | Source | Example |
|----------|--------|---------|
| `{{DisplayName}}` | `first_name + last_name` | "Ola Nordmann" |
| `{{JobTitle}}` | `title` | "Eiendomsmegler" |
| `{{Email}}` | `email` | "ola@proaktiv.no" |
| `{{MobilePhone}}` | `phone` | "+47 999 88 777" |
| `{{OfficeName}}` | `office.name` | "Stavanger" |
| `{{OfficeAddress}}` | `office.street_address` | "Lagårdsveien 78" |
| `{{OfficePostal}}` | `office.postal_code + office.city` | "4010 Stavanger" |
| `{{OfficePhone}}` | `office.phone` | "+47 51 50 10 00" |

---

## Database Query

```sql
SELECT 
    e.email,
    e.first_name,
    e.last_name,
    e.title,
    e.phone,
    e.profile_image_url,
    o.name AS office_name,
    o.city,
    o.street_address,
    o.postal_code,
    o.phone AS office_phone,
    o.email AS office_email
FROM employees e
JOIN offices o ON e.office_id = o.id
WHERE e.status = 'active' 
  AND e.email IS NOT NULL
ORDER BY o.name, e.last_name;
```

---

## Authentication Options

### Option 1: Certificate (Recommended for Production)

```powershell
$params = @{
    TenantId = $TenantId
    ClientId = $ClientId
    CertificateThumbprint = $CertThumbprint
}
Connect-MgGraph @params
Connect-ExchangeOnline -CertificateThumbprint $CertThumbprint -AppId $ClientId -Organization "proaktiv.onmicrosoft.com"
```

**Advantages:**
- No secrets to rotate
- More secure than client secrets
- Longer validity (1-2 years)

### Option 2: Client Secret (Simpler Setup)

```powershell
$secureSecret = ConvertTo-SecureString $ClientSecret -AsPlainText -Force
$credential = New-Object System.Management.Automation.PSCredential($ClientId, $secureSecret)

Connect-MgGraph -TenantId $TenantId -ClientSecretCredential $credential
```

**Disadvantages:**
- Secret must be rotated regularly
- Secret can be leaked if not handled carefully

---

## Rate Limiting

Microsoft Graph API has throttling limits:

| Resource | Limit |
|----------|-------|
| Per app per tenant | 10,000 requests per 10 minutes |
| Per user per app | 10,000 requests per 10 minutes |

**Mitigation:**
- Add 100-200ms delay between requests
- Implement exponential backoff on 429 errors
- Batch requests where possible (Graph supports batching)

---

## Error Handling

| Error | Cause | Resolution |
|-------|-------|------------|
| 401 Unauthorized | Invalid/expired token | Re-authenticate |
| 403 Forbidden | Missing permissions | Check app permissions, admin consent |
| 404 Not Found | User doesn't exist in Entra ID | Skip user, log warning |
| 429 Too Many Requests | Rate limited | Wait and retry with backoff |
| 503 Service Unavailable | Microsoft service issue | Retry with backoff |

---

## Security Considerations

1. **Never commit secrets** - Use environment variables or Key Vault
2. **Use certificate auth** - Preferred over client secrets
3. **Least privilege** - Only request necessary permissions
4. **Audit logging** - Log all changes for compliance
5. **Dry-run mode** - Always test before production runs
6. **Filter by email** - Test with single user first

---

## Dependencies

### PowerShell Modules

```powershell
# Microsoft Graph
Install-Module Microsoft.Graph -Scope CurrentUser

# Exchange Online
Install-Module ExchangeOnlineManagement -Scope CurrentUser

# PostgreSQL connectivity (optional - can use Python bridge)
# Npgsql requires .NET assembly loading
```

### Alternative: Python Bridge for Database

Instead of Npgsql, use a Python script to export employees to JSON:

```powershell
# Export from database via Python
py -3.12 -c "
from app.models.employee import Employee
from app.models.office import Office
from app.database import get_db
import json

# Query and export to JSON
"
```

---

## References

- [Update user - Microsoft Graph](https://learn.microsoft.com/en-us/graph/api/user-update?view=graph-rest-1.0)
- [Update profilePhoto - Microsoft Graph](https://learn.microsoft.com/en-us/graph/api/profilephoto-update?view=graph-rest-1.0)
- [Set-MailboxMessageConfiguration](https://learn.microsoft.com/en-us/powershell/module/exchangepowershell/set-mailboxmessageconfiguration?view=exchange-ps)
- [Microsoft Graph PowerShell SDK](https://learn.microsoft.com/en-us/powershell/microsoftgraph/overview)
- [Exchange Online PowerShell](https://learn.microsoft.com/en-us/powershell/exchange/exchange-online-powershell)
