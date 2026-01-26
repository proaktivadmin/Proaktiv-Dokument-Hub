# Phase 09: Self-Service Signature Portal

**Status:** ✅ Completed  
**Completed:** 2026-01-24 (V3.9 Core), 2026-01-26 (V3.9.3 Cross-Client Polish)  
**Latest Commit:** See `main` branch

---

## Summary

A self-service email signature system for 120+ employees. Admins preview and send personalized signature links from the dashboard. Employees visit their personal page to copy and paste the signature into their email client.

---

## V3.9.3 Cross-Client Polish & Branding (2026-01-26)

| Feature | Description |
|---------|-------------|
| **Photo Cropping Fix** | Uses `object-fit:cover` with `object-position:center top` for proper 80x96 portrait cropping |
| **Outlook Classic Alignment** | Changed MSO table from `align="center"` to `align="left"` for proper left alignment |
| **Apple Mail Support** | Added `a[x-apple-data-detectors]` CSS to prevent blue link styling |
| **Mac Outlook Support** | Font smoothing with `-webkit-font-smoothing:antialiased` |
| **Gmail Compatibility** | Enhanced dark mode protection with `u + .body` selectors |
| **Black Link Colors** | Aggressive link color override with `<span>` wrappers for all clients |
| **Name Nowrap** | Added `white-space:nowrap` to prevent name wrapping in narrow layouts |
| **Logo from WebDAV** | Public signature page now uses `proaktiv.no/assets/logos/proaktiv_sort.png` |
| **Branding Updates** | "Proaktiv Administrasjonen" for contact, "Adrian Frøyland, IT Ansvarlig" for errors |
| **Improved UX Copy** | Clear instructions about using copy button, not manual selection |

---

## V3.9.2 Photo Export (2026-01-25)

| Feature | Description |
|---------|-------------|
| **Photo Export Scripts** | `export_homepage_employee_photos.py`, `export_office_banners.py` |
| **Template Photo Support** | `{{EmployeePhotoUrl}}` placeholder in signature templates |
| **WebDAV Photo URLs** | Photos hosted at `proaktiv.no/d/photos/employees/{email}.jpg` |

---

## V3.9.1 Mobile & UX Enhancements (2026-01-25)

| Feature | Description |
|---------|-------------|
| **Mobile Compatibility** | "Åpne e-post" button opens mailto: link on mobile devices |
| **Plain Text Fallback** | Mobile browsers get text copy when HTML clipboard unavailable |
| **Phone Formatting** | Norwegian format `XX XX XX XX` for display, E.164 for `tel:` links |
| **Keyboard Shortcuts** | Desktop hints: Ctrl/⌘+C (copy), Ctrl/⌘+M (email) |
| **Support Contact** | IT contact section with email link |
| **Toast Clarity** | Messages indicate HTML vs text copy format |

---

## Deliverables

### Backend

| File | Purpose |
|------|---------|
| `backend/app/services/signature_service.py` | Renders personalized HTML signatures |
| `backend/app/services/graph_service.py` | Microsoft Graph API client for sending emails |
| `backend/app/routers/signatures.py` | GET/POST API endpoints |
| `backend/scripts/templates/email-signature.html` | With-photo signature (Outlook/Gmail/Apple Mail compatible) |
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

## Email Client Compatibility

| Client | Status | Notes |
|--------|--------|-------|
| **Outlook Classic (Windows)** | ✅ Verified | VML for photo cropping, MSO conditional styles |
| **Outlook New (Windows)** | ✅ Verified | Standard HTML with dark mode protection |
| **Outlook for Mac** | ✅ Supported | WebKit font smoothing, standard link styling |
| **Outlook.com** | ✅ Supported | `[data-ogsc]` dark mode protection |
| **Gmail (Web/App)** | ✅ Supported | `u + .body` dark mode protection |
| **Apple Mail (macOS)** | ✅ Supported | `x-apple-data-detectors` link override |
| **iOS Mail** | ✅ Supported | Light mode meta tags, Apple-specific CSS |

---

## Template Features

### Photo Handling
- **Dimensions:** 80×96px (5:6 portrait ratio)
- **Cropping:** `object-fit:cover; object-position:center top`
- **Outlook:** VML `v:rect` with `v:fill type="frame"` for proper cropping
- **Fallback:** Uses placeholder lily icon if no photo

### Link Color Protection
- Inline `color:#000000 !important` on all `<a>` tags
- `<span>` wrapper with explicit color for extra specificity
- MSO-specific styles in `<style>` block for Outlook
- `a[x-apple-data-detectors]` rule for Apple Mail

### Dark Mode Protection
- `<meta name="color-scheme" content="light">`
- `<meta name="x-apple-color-scheme" content="light">`
- `.dark-mode-bg` and `.dark-mode-text` classes with `!important`
- Client-specific selectors for Outlook.com and Gmail

---

## Social Media Link Priority

**Current behavior:** Office → Company default

The signature service resolves social media URLs in this order:
1. Office-level URLs (if office has `facebook_url`, `instagram_url`, `linkedin_url`)
2. Company default URLs (fallback)

**Note:** Employee-level social links are stored in the database but not used in signatures yet. This is planned as a future feature where employees can add personal links below the email line.

---

## Environment Variables

Required on Railway backend:

```
SIGNATURE_SENDER_EMAIL=froyland@proaktiv.no
FRONTEND_URL=https://proaktiv-dokument-hub.vercel.app
```

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
| `{{EmployeeUrl}}` | Employee proaktiv.no profile | From `homepage_url` |
| `{{FacebookUrl}}` | Office → Company default | Social media link |
| `{{InstagramUrl}}` | Office → Company default | Social media link |
| `{{LinkedInUrl}}` | Office → Company default | Social media link |
| `{{OfficeName}}` | `employee.office.name` | Office display name |
| `{{OfficeAddress}}` | `employee.office.street_address` | Street address |
| `{{OfficePostal}}` | Computed | `{postal_code} {city}` |

---

## Documentation

| Document | Path |
|----------|------|
| Email template spec | `docs/features/signatures/EMAIL-SIGNATURE-SPEC.md` |
| Handover document | `.planning/phases/09-signature-portal/HANDOVER.md` |
| Agent command | `.cursor/commands/signature.md` |
| QA plan | `.cursor/plans/signature_qa_testing_01ae0f96.plan.md` |
| Project reference | `CLAUDE.md` |

---

## Pending Work

### QA Testing Stages 3-5

| Stage | Description | Status |
|-------|-------------|--------|
| 3 | Email Client Rendering | ⏳ Pending |
| 4 | Mobile Device Testing | ⏳ Pending |
| 5 | Edge Cases and Error States | ⏳ Pending |

### Bulk Email Rollout

Send signature links to all employees after final approval.

### Future: Employee Social Links

Allow employees to add personal social media links below the email line.
