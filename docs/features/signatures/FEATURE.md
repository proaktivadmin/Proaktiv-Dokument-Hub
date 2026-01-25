# Email Signature System

**Status:** ✅ Production  
**Version:** V3.9.2  
**Last Updated:** 2026-01-25

---

## Overview

A self-service email signature system for 120+ employees. Admins preview and send personalized signature links from the dashboard. Employees visit their personal page to copy and paste the signature into their email client.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        ADMIN DASHBOARD                               │
│  Employee Detail Page → "Signatur" Tab                              │
│  - Preview signature (with-photo / no-photo)                        │
│  - "Send signatur til ansatt" button                                │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  │ POST /api/signatures/{id}/send
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        RAILWAY BACKEND                               │
│  SignatureService - render_signature()                              │
│  GraphService - send_mail()                                         │
│  Templates: email-signature.html, email-signature-no-photo.html     │
└─────────────────────────────────────────────────────────────────────┘
                                  │
                                  │ Email with personal link
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│                           EMPLOYEE                                   │
│  1. Receives email with link                                         │
│  2. Clicks → /signature/{employee-uuid}                              │
│  3. Selects version (med bilde / uten bilde)                         │
│  4. Clicks "Kopier signatur"                                         │
│  5. Pastes into email client                                         │
└─────────────────────────────────────────────────────────────────────┘
```

---

## API Endpoints

### GET /api/signatures/{employee_id}

Renders a personalized email signature for an employee.

- **Query:** `version=with-photo|no-photo`
- **Auth:** None (public, UUID provides security)
- **Response:** `{ html, text, employee_name, employee_email }`

### POST /api/signatures/{employee_id}/send

Sends signature notification email to employee.

- **Auth:** Required (dashboard session)
- **Response:** `{ success, sent_to, message }`

---

## Template Placeholders

| Placeholder | Source | Notes |
|-------------|--------|-------|
| `{{DisplayName}}` | `employee.full_name` | Required |
| `{{JobTitle}}` | `employee.title` | Optional |
| `{{MobilePhone}}` | `employee.phone` | Formatted as XX XX XX XX |
| `{{MobilePhoneRaw}}` | `employee.phone` | Raw digits for tel: links |
| `{{Email}}` | `employee.email` | Required |
| `{{EmployeePhotoUrl}}` | `employee.profile_image_url` | Falls back to placeholder |
| `{{FacebookUrl}}` | Office → Company default | Social media link |
| `{{InstagramUrl}}` | Office → Company default | Social media link |
| `{{LinkedInUrl}}` | Office → Company default | Social media link |
| `{{OfficeName}}` | `employee.office.name` | Office display name |
| `{{OfficeAddress}}` | `employee.office.street_address` | Street address |
| `{{OfficePostal}}` | Computed | `{postal_code} {city}` |

---

## Photo Integration

### Photo Source

Employee photos are scraped from proaktiv.no and uploaded to WebDAV:
```
https://proaktiv.no/d/photos/employees/{email}.jpg
```

### Photo Resolution Priority

1. `employee.profile_image_url` (if set and not Vitec API path)
2. Fallback: `https://proaktiv.no/assets/logos/lilje_clean_52.png`

### Export Scripts

| Script | Purpose |
|--------|---------|
| `backend/scripts/export_homepage_employee_photos.py` | Crawl proaktiv.no, download employee photos |
| `backend/scripts/export_office_banners.py` | Crawl proaktiv.no, download office banners |

See `docs/features/photo-export/HANDOVER.md` for photo export documentation.

---

## Files

### Backend

| File | Purpose |
|------|---------|
| `backend/app/services/signature_service.py` | Renders personalized HTML signatures |
| `backend/app/services/graph_service.py` | Microsoft Graph API client for sending emails |
| `backend/app/routers/signatures.py` | GET/POST API endpoints |
| `backend/scripts/templates/email-signature.html` | With-photo template |
| `backend/scripts/templates/email-signature-no-photo.html` | No-photo template |
| `backend/scripts/templates/signature-notification-email.html` | Email notification template |

### Frontend

| File | Purpose |
|------|---------|
| `frontend/src/hooks/v3/useSignature.ts` | API hooks for signature fetching/sending |
| `frontend/src/components/employees/SignaturePreview.tsx` | Admin preview component |
| `frontend/src/app/signature/[id]/page.tsx` | Public self-service page |

### Scripts

| File | Purpose |
|------|---------|
| `backend/scripts/Send-SignatureEmails.ps1` | Bulk email sender |
| `run-signature-emails.bat` | Windows launcher |

---

## Usage

### Admin Dashboard

1. Navigate to employee detail page
2. Click "Signatur" tab
3. Preview signature (with-photo / no-photo)
4. Click "Send signatur" to email link to employee

### Employee Self-Service

1. Employee receives email with personal link
2. Clicks link → `/signature/{uuid}`
3. Selects version (med bilde / uten bilde)
4. Clicks "Kopier signatur"
5. Pastes into email client

### Bulk Rollout

```powershell
# Dry run (test without sending)
.\backend\scripts\Send-SignatureEmails.ps1 -DryRun

# Send to specific person (testing)
.\backend\scripts\Send-SignatureEmails.ps1 -FilterEmails "adrian@proaktiv.no"

# Send to all (production)
.\backend\scripts\Send-SignatureEmails.ps1
```

---

## Environment Variables

Required on Railway backend:

| Variable | Value |
|----------|-------|
| `SIGNATURE_SENDER_EMAIL` | `froyland@proaktiv.no` |
| `FRONTEND_URL` | `https://proaktiv-dokument-hub.vercel.app` |

---

## Azure Permissions

Add to Entra app `PROAKTIV-Entra-Sync`:

- **Microsoft Graph** → **Application permissions** → **Mail.Send**
- Grant admin consent

---

## Mobile Support (V3.9.1)

- "Åpne e-post" button for mobile users
- Plain text fallback when HTML clipboard fails
- Keyboard shortcut hints for desktop users
- Support contact section with IT email addresses

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| V3.9.2 | 2026-01-25 | Photo export scripts, `{{EmployeePhotoUrl}}` placeholder |
| V3.9.1 | 2026-01-25 | Mobile support, phone formatting, QA fixes |
| V3.9 | 2026-01-24 | Initial release |

---

## Related Documentation

- `.planning/phases/09-signature-portal/COMPLETED.md` - Phase completion summary
- `.planning/phases/09-signature-portal/SPEC.md` - Technical specification
- `docs/features/photo-export/HANDOVER.md` - Photo export handover
- `docs/entra-signature-sync.md` - Entra ID sync documentation
