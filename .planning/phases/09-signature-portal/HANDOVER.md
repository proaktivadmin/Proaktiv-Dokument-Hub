# Signature Portal - Agent Handover

**Handover Date:** 2026-01-25  
**Previous Agent:** Claude Opus 4.5  
**Feature Status:** V3.9.2 (Photo Export Complete, WebDAV Upload Pending)

---

## Quick Context

The Self-Service Signature Portal allows 120+ employees to copy their personalized email signature from a web page and paste it into their email client. Admins can preview and send signature links from the dashboard.

**Production URLs:**
- Public signature page: `https://proaktiv-dokument-hub.vercel.app/signature/{employee_id}`
- Admin preview: Employee detail page → "Signatur" tab
- API: `GET /api/signatures/{id}`, `POST /api/signatures/{id}/send`

---

## What's Complete

### V3.9 Core (2026-01-24)
- ✅ Backend SignatureService with HTML template rendering
- ✅ GraphService for email notifications via Microsoft Graph
- ✅ Public `/signature/[id]` page with copy-to-clipboard
- ✅ Admin SignaturePreview component in employee detail page
- ✅ PowerShell bulk sender script

### V3.9.1 Enhancements (2026-01-25 Morning)
- ✅ Mobile compatibility ("Åpne e-post" button, text fallback)
- ✅ Norwegian phone formatting (`XX XX XX XX`)
- ✅ Keyboard shortcut hints (Ctrl/⌘+C, Ctrl/⌘+M)
- ✅ Support contact section
- ✅ Toast messages indicate copy format
- ✅ QA Stages 1-2 passed with fixes applied

### V3.9.2 Photo Export (2026-01-25 Afternoon)
- ✅ Created `export_homepage_employee_photos.py` - crawls proaktiv.no, downloads employee photos
- ✅ Created `export_office_banners.py` - crawls proaktiv.no, downloads office banners
- ✅ Fixed og:image extraction in `sync_proaktiv_directory.py` for profile photos
- ✅ Updated `email-signature.html` template with `{{EmployeePhotoUrl}}` placeholder
- ✅ Updated `signature_service.py` with `_resolve_employee_photo_url()` method
- ✅ Added external link to proaktiv.no profile on EmployeeCard component
- ✅ ~100 employee photos + 21 office banners exported locally
- ⏳ Pending: Manual WebDAV upload
- ⏳ Pending: Database URL update scripts

---

## What's Pending

### Priority 1: WebDAV Photo Upload + Database Update

**Goal:** Upload exported photos to WebDAV and update database URLs.

**Current State (UPDATED):**
- ✅ Photos exported to `C:\Users\Adrian\Documents\ProaktivPhotos\webdav-upload\`
  - `photos/employees/` - ~100 employee photos named `{email}.jpg`
  - `photos/offices/` - 21 office banners named `{office_slug}.jpg`
- ✅ Mapping files generated: `employee_photo_map.csv`, `office_banner_map.csv`
- ⏳ **Manual WebDAV upload required** (proaktiv.no/d is live, be careful!)
- ⏳ **Database update scripts needed**

**Handover Documentation:** `docs/features/photo-export/HANDOVER.md`

**Steps to Complete:**
1. **Manual WebDAV Upload** (user must do this carefully):
   ```
   Local: C:\Users\Adrian\Documents\ProaktivPhotos\webdav-upload\photos\
   Target: proaktiv.no/d/photos/
     └── employees/   # Employee photos
     └── offices/     # Office banners
   ```

2. **Create Database Update Scripts** using mapping files:
   ```python
   # For employees:
   UPDATE employees SET profile_image_url = 'https://proaktiv.no/d/photos/employees/{email}.jpg'
   WHERE email = '{email}';
   
   # For offices:
   UPDATE offices SET banner_image_url = 'https://proaktiv.no/d/photos/offices/{slug}.jpg'
   WHERE homepage_url = '{homepage_url}';
   ```

3. **Verify Signature Rendering** with new photo URLs

**Impact:** Dashboard and signature pages will load employee photos much faster.

---

### Priority 2: QA Testing Stages 3-5

**Plan File:** `.cursor/plans/signature_qa_testing_01ae0f96.plan.md`

| Stage | Description | What to Test |
|-------|-------------|--------------|
| 3 | Email Client Rendering | Paste signature into Outlook, Gmail, Apple Mail, verify formatting |
| 4 | Mobile Device Testing | Test on actual iOS/Android devices |
| 5 | Edge Cases | Invalid IDs, slow network, missing data, special characters |

**How to Run:**
1. Read the plan file for detailed checklists
2. Use browser tools to test at different viewports
3. Send test emails to verify signature rendering
4. Document findings in the plan file or create QA report

---

### Priority 3: Bulk Email Rollout

**Goal:** Send signature links to all 120+ employees.

**Prerequisites:**
- Set `SIGNATURE_SENDER_EMAIL` env var on Railway
- Set `FRONTEND_URL` env var on Railway
- Add `Mail.Send` permission in Azure Portal for `PROAKTIV-Entra-Sync` app

**Commands:**
```powershell
# Test with dry run
.\backend\scripts\Send-SignatureEmails.ps1 -DryRun

# Test with single employee
.\backend\scripts\Send-SignatureEmails.ps1 -FilterEmails "froyland@proaktiv.no"

# Full rollout
.\backend\scripts\Send-SignatureEmails.ps1
```

---

## Key Files Reference

### Backend
| File | Purpose |
|------|---------|
| `backend/app/services/signature_service.py` | Template rendering, placeholders |
| `backend/app/services/graph_service.py` | Microsoft Graph API, email sending |
| `backend/app/routers/signatures.py` | API endpoints |
| `backend/scripts/templates/email-signature.html` | With-photo template |
| `backend/scripts/templates/email-signature-no-photo.html` | No-photo template |

### Frontend
| File | Purpose |
|------|---------|
| `frontend/src/app/signature/[id]/page.tsx` | Public self-service page |
| `frontend/src/components/employees/SignaturePreview.tsx` | Admin preview component |
| `frontend/src/hooks/v3/useSignature.ts` | API hooks |

### Scripts
| File | Purpose |
|------|---------|
| `backend/scripts/Send-SignatureEmails.ps1` | Bulk email sender |
| `backend/scripts/export_homepage_employee_photos.py` | Crawl proaktiv.no, export employee photos |
| `backend/scripts/export_office_banners.py` | Crawl proaktiv.no, export office banners |
| `backend/scripts/upload_employee_photos.py` | WebDAV photo upload (legacy) |
| `backend/scripts/update_photo_urls_webdav.py` | DB URL update (legacy) |

---

## Template Placeholders

| Placeholder | Source | Format |
|-------------|--------|--------|
| `{{DisplayName}}` | `employee.full_name` | "John Doe" |
| `{{JobTitle}}` | `employee.title` | "Eiendomsmegler MNEF" |
| `{{MobilePhone}}` | `employee.phone` | "12 34 56 78" (formatted) |
| `{{MobilePhoneRaw}}` | `employee.phone` | "+4712345678" (E.164) |
| `{{Email}}` | `employee.email` | "john@proaktiv.no" |
| `{{EmployeePhotoUrl}}` | `employee.profile_image_url` | URL or placeholder |
| `{{OfficeName}}` | `employee.office.name` | "Småstrandgaten" |
| `{{OfficeAddress}}` | `employee.office.street_address` | "Småstrandgaten 3" |
| `{{OfficePostal}}` | Computed | "5014 Bergen" |

---

## Known Issues

1. **34 employees missing photos** - No images on proaktiv.no
2. **Mobile HTML copy not supported** - Falls back to plain text (by design)
3. **Transport rule signatures on hold** - Requires certificate auth for Exchange Online

---

## Documentation

| Document | Path |
|----------|------|
| Session log | `.planning/phases/09-signature-portal/SESSION-2026-01-25.md` |
| Feature spec | `.planning/phases/09-signature-portal/SPEC.md` |
| Completion summary | `.planning/phases/09-signature-portal/COMPLETED.md` |
| **Photo export handover** | `docs/features/photo-export/HANDOVER.md` |
| **Signature feature docs** | `docs/features/signatures/FEATURE.md` |
| QA plan | `.cursor/plans/signature_qa_testing_01ae0f96.plan.md` |
| Project reference | `CLAUDE.md` |

---

## Next Agent Instructions

1. **Start by reading** `.planning/STATE.md` for current project status
2. **Read photo export handover** `docs/features/photo-export/HANDOVER.md` for detailed context
3. **Help user with WebDAV upload** - Photos are ready locally, need careful upload to live server
4. **Create DB update scripts** - Use CSV mapping files to update `profile_image_url` fields
5. **Verify signature rendering** - Check that photos load correctly in signature previews
6. **QA testing optional** - Nice to complete but not blocking
7. **Bulk rollout ready** when user approves

**Key Change from Previous Session:**
The photo export scripts now use email-based naming (`{email}.jpg`) instead of slug-based, matching the recommended architecture. The signature template is already updated to use `{{EmployeePhotoUrl}}` which resolves from `employee.profile_image_url`.

Good luck!
