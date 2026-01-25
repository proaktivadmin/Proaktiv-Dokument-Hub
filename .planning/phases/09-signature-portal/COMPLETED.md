# Phase 09: Self-Service Signature Portal

**Status:** ✅ Completed  
**Completed:** 2026-01-24 (V3.9 Core), 2026-01-25 (V3.9.1 Enhancements)  
**Commit:** `4241eb8` (V3.9), latest `main` (V3.9.1)

---

## Summary

A self-service email signature system for 120+ employees. Admins preview and send personalized signature links from the dashboard. Employees visit their personal page to copy and paste the signature into their email client.

---

## V3.9.1 Mobile & UX Enhancements (2026-01-25)

| Feature | Description |
|---------|-------------|
| **Mobile Compatibility** | "Åpne e-post" button opens mailto: link on mobile devices |
| **Plain Text Fallback** | Mobile browsers get text copy when HTML clipboard unavailable |
| **Phone Formatting** | Norwegian format `XX XX XX XX` for display, E.164 for `tel:` links |
| **Keyboard Shortcuts** | Desktop hints: Ctrl/⌘+C (copy), Ctrl/⌘+M (email) |
| **Support Contact** | IT contact section: it@proaktiv.no, froyland@proaktiv.no |
| **Toast Clarity** | Messages indicate HTML vs text copy format |

**Session Log:** `.planning/phases/09-signature-portal/SESSION-2026-01-25.md`

---

## Photo Integration (2026-01-25)

The signature template now supports dynamic employee photos via `{{EmployeePhotoUrl}}` placeholder.

**Photo Source:** Employee photos are scraped from proaktiv.no and uploaded to WebDAV at:
```
https://proaktiv.no/d/photos/employees/{email}.jpg
```

**Related Scripts:**
| Script | Purpose |
|--------|---------|
| `backend/scripts/export_homepage_employee_photos.py` | Crawl proaktiv.no, download employee photos |
| `backend/scripts/export_office_banners.py` | Crawl proaktiv.no, download office banners |

**Photo Resolution Priority in SignatureService:**
1. `employee.profile_image_url` (if not empty and not Vitec API path)
2. Fallback: `https://proaktiv.no/assets/logos/lilje_clean_52.png`

See: `docs/features/photo-export/HANDOVER.md` for full photo export documentation.

---

## Deliverables

### Backend

| File | Purpose |
|------|---------|
| `backend/app/services/signature_service.py` | Renders personalized HTML signatures |
| `backend/app/services/graph_service.py` | Microsoft Graph API client for sending emails |
| `backend/app/routers/signatures.py` | GET/POST API endpoints |
| `backend/scripts/templates/email-signature-no-photo.html` | No-photo signature variant |
| `backend/scripts/templates/signature-notification-email.html` | Email template for notifications |

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
| `run-signature-emails.bat` | Launcher script |

---

## API Endpoints

### GET /api/signatures/{employee_id}

Returns personalized HTML signature.

- **Query:** `version=with-photo|no-photo`
- **Auth:** None (public, UUID provides security)
- **Response:** `{ html, text, employee_name, employee_email }`

### POST /api/signatures/{employee_id}/send

Sends signature notification email to employee.

- **Auth:** Required (dashboard session)
- **Response:** `{ success, sent_to, message }`

---

## Environment Variables

Required on Railway backend:

```
SIGNATURE_SENDER_EMAIL=froyland@proaktiv.no
FRONTEND_URL=https://proaktiv-dokument-hub.vercel.app
```

---

## Azure Permissions

Add to Entra app `PROAKTIV-Entra-Sync`:

- **Microsoft Graph** → **Application permissions** → **Mail.Send**
- Grant admin consent

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

## Agent Pipeline

This feature was built using a 6-agent pipeline:

| Agent | Scope | Files |
|-------|-------|-------|
| 1 | Backend signature service + router | signature_service.py, signatures.py |
| 2 | Backend graph service + send endpoint | graph_service.py, notification template |
| 3 | Frontend hooks + SignaturePreview | useSignature.ts, SignaturePreview.tsx |
| 4 | Employee page tab integration | page.tsx modification |
| 5 | Public signature page | /signature/[id]/page.tsx |
| 6 | PowerShell bulk sender | Send-SignatureEmails.ps1 |

See `.planning/codebase/AGENT-PIPELINE.md` for reusable pipeline documentation.

---

## QA Testing

A comprehensive 5-stage QA testing plan was created:

**Plan File:** `.cursor/plans/signature_qa_testing_01ae0f96.plan.md`

| Stage | Description | Status |
|-------|-------------|--------|
| 1 | Signature Page UI Compatibility | ✅ Passed with fixes |
| 2 | Copy/Paste Functionality | ✅ Passed with fixes |
| 3 | Email Client Rendering | ⏳ Pending |
| 4 | Mobile Device Testing | ⏳ Pending |
| 5 | Edge Cases and Error States | ⏳ Pending |

**Test Clients:** Outlook (New/Classic), Gmail, Apple Mail, Thunderbird

---

## Pending Work

### WebDAV Photo Migration (High Priority)

Replace Vitec API base64 images with WebDAV-hosted photos.

**Scripts Ready:**
- `backend/scripts/upload_employee_photos.py` - Upload to WebDAV
- `backend/scripts/update_photo_urls_webdav.py` - Update database URLs

**Photos Downloaded:** 184 in `C:\Users\Adrian\Documents\ProaktivPhotos\webdav-upload\`

**Commands:**
```powershell
# Upload photos
cd backend
python scripts/upload_employee_photos.py --photos-dir "C:\Users\Adrian\Documents\ProaktivPhotos\webdav-upload" --dry-run

# Update database
python scripts/update_photo_urls_webdav.py --dry-run
python scripts/update_photo_urls_webdav.py
```

### Bulk Email Rollout

Send signature links to all employees:

```powershell
.\backend\scripts\Send-SignatureEmails.ps1 -DryRun      # Test
.\backend\scripts\Send-SignatureEmails.ps1              # Production
```
