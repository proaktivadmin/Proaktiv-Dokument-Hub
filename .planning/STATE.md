# Project State

> **This is the single source of truth for project status.**
> See also: `CLAUDE.md` (quick reference), `.cursor/workflow_guide.md` (workflow)

## Project Reference

See: .planning/PROJECT.md (updated 2026-01-23)

**Core value:** Brokers can manage and preview document templates without touching code
**Current focus:** Phase 06 Testing OR Phase 07 Office Enhancements

## Current Position

Phase: 3.9.1 (Signature Portal Enhancements)
Plan: V3.9.1 QA + Mobile Fixes
Status: Deployed to production
Last activity: 2026-01-25 — Mobile compatibility, phone formatting, QA testing

Progress: [██████████] 100% (V3.9.1 enhancements complete)

## Performance Metrics

**Velocity:**
- Total plans completed: 8 (Phase 1: 3, Phase 4: 5)
- Average duration: ~2 hours per plan
- Total execution time: ~16 hours

**By Phase:**

| Phase | Plans | Status | Completed |
|-------|-------|--------|-----------|
| 1. Vitec API Connection | 3/3 | Complete | 2026-01-20 |
| 4. Stack Upgrade | 5/5 | Complete | 2026-01-22 |
| 5. Vercel Migration | 2/5 | In Progress | - |
| 6. Entra ID Signature Sync | 8/8 | Profile Sync ✅ / Exchange ⏸️ | 2026-01-24 |
| 7. Office Enhancements + SalesScreen | 0/8 | Ready | - |

**Recent Trend:**
- Phase 4 completed rapidly (same day)
- CI/CD pipeline now operational

*Updated after each plan completion*

## Accumulated Context

### Decisions

Decisions are logged in PROJECT.md Key Decisions table.
Recent decisions affecting current work:

- Manual sync review: Prevent bad data overwrites, require case-by-case approval
- Email-based employee matching: Most reliable identifier across systems
- Field-by-field diff: User chooses per-field, not all-or-nothing
- Static social links: No API integration, links rarely change
- Upgrade before migrate: Fix CVE-2025-29927 first, test on one platform
- Vercel for frontend: Better Next.js DX, preview deployments
- Skip Next.js 15, go to 16: Latest stable with React 19 support
- xfail incomplete tests: Don't block CI, track missing features

### Pending Todos

- 3 normalizer service tests marked as xfail (CSS stripping not implemented)

### Blockers/Concerns

None.

## Session Continuity

Last session: 2026-01-25
Stopped at: V3.9.2 Photo export scripts complete
Resume file: `docs/features/photo-export/HANDOVER.md`
Next step: Upload photos to WebDAV, update database records, verify signature rendering

### Session Summary (2026-01-25 - Latest)
**V3.9.2 Photo Export for Signatures (In Progress):**
- ✅ Created `export_homepage_employee_photos.py` - crawls proaktiv.no, downloads employee photos
- ✅ Created `export_office_banners.py` - crawls proaktiv.no, downloads office banners
- ✅ Fixed og:image extraction in `sync_proaktiv_directory.py` for profile photos
- ✅ Updated `email-signature.html` template with `{{EmployeePhotoUrl}}` placeholder
- ✅ Updated `signature_service.py` with `_resolve_employee_photo_url()` method
- ✅ Added external link to proaktiv.no profile on EmployeeCard component
- ✅ Generated photo mapping files (manifest.json, CSV maps)
- ⏳ Pending: Manual WebDAV upload of `photos/employees/` and `photos/offices/`
- ⏳ Pending: Database update scripts for `profile_image_url` fields
- Handover: `docs/features/photo-export/HANDOVER.md`

**Output Files Generated:**
- `C:\Users\Adrian\Documents\ProaktivPhotos\webdav-upload\photos\employees\` (~100 photos)
- `C:\Users\Adrian\Documents\ProaktivPhotos\webdav-upload\photos\offices\` (21 banners)

**V3.9.1 Signature Portal Enhancements (Completed earlier today):**
- ✅ Mobile compatibility: "Åpne e-post" button, plain text fallback
- ✅ Norwegian phone formatting: `XX XX XX XX` display format
- ✅ Keyboard shortcut hints for desktop users (Ctrl/⌘+C, Ctrl/⌘+M)
- ✅ Support contact section with IT email addresses
- ✅ Toast messages now indicate copy format (HTML vs text)
- ✅ QA testing plan created (5 stages), Stages 1-2 executed with fixes
- ✅ Deployment verification and Vercel cache fix
- Session log: `.planning/phases/09-signature-portal/SESSION-2026-01-25.md`

**Pending Work (for Next Agent):**
- ⏳ WebDAV upload: Upload photos to `proaktiv.no/d/photos/employees/` and `photos/offices/`
- ⏳ Database update: Set `profile_image_url` from CSV mapping files
- ⏳ QA testing: Stages 3-5 pending (email clients, mobile, edge cases)
- ⏳ Transport rule signatures: Agent 3-4 pending (POC test, docs)

### Session Summary (2026-01-24)
**V3.9 Self-Service Signature Portal (Completed 2026-01-24):**
- ✅ Backend SignatureService renders personalized HTML signatures (with-photo/no-photo)
- ✅ Backend GraphService sends notification emails via Microsoft Graph API
- ✅ GET /api/signatures/{id} endpoint (public, returns HTML/text)
- ✅ POST /api/signatures/{id}/send endpoint (sends signature link email)
- ✅ Frontend SignaturePreview component on employee detail page (Signatur tab)
- ✅ Public /signature/{id} page for employees to copy signatures
- ✅ Copy-to-clipboard with HTML formatting for email clients
- ✅ Instructions accordion for Outlook, Gmail, Apple Mail
- ✅ PowerShell bulk sender script (Send-SignatureEmails.ps1)
- Plans: `.planning/phases/09-signature-portal/`
- Commit: `4241eb8`

**V3.8 Sync Notification System (Completed 2026-01-24):**
- ✅ Notification bell dropdown in header
- ✅ Unread count badge with polling (30s)
- ✅ Notification types: employee/office added/updated/removed, UPN mismatch, sync error
- ✅ Click to navigate to related entity
- ✅ Mark as read, mark all read, clear all actions
- ✅ Integration with employee and office sync services
- Plans: `.planning/phases/08-sync-notifications/`

**V3.7 UPN Mismatch Detection:**

1. **Problem Identified:**
   - Employees with Entra ID UPN different from Vitec Next email fail SSO login
   - Validation error occurs when UPN != email in Vitec Next

2. **Solution Implemented:**
   - Added `entra_upn` field to Employee model (stores Entra UPN)
   - Added `entra_upn_mismatch` boolean flag (true when UPN != email)
   - Database migration: `20260124_0001_add_entra_upn_fields.py`
   - Frontend EmployeeCard shows red warning for affected employees

3. **Detection Scripts:**
   - `backend/scripts/check_upn_mismatch.py` - Python script
   - `backend/scripts/Check-UPNMismatch.ps1` - PowerShell alternative
   - Scripts query Entra ID via Graph API, compare with DB, update flags

4. **Note:**
   - Connected to QA system, not production
   - Flagged employees persist until production switch

### Previous Session (2026-01-23)
**V3.6 Design System Enhancement:**

1. **Design Token System:**
   - Shadow tokens: soft, medium, elevated, glow, card, card-hover
   - Transition tokens: fast (150ms), normal (200ms), slow (300ms), ease-standard
   - State tokens: opacity-disabled, ring-strong
   - All tokens in CSS variables and Tailwind config

2. **Base UI Component Updates (14 components):**
   - button, card, dialog, dropdown-menu, input, select, textarea
   - checkbox, skeleton, badge, sheet, tabs, toast
   - Consistent focus rings, disabled states, transitions

3. **Feature Component Enhancements:**
   - Header: Scroll shadow effect
   - OfficeCard, EmployeeCard, TemplateCard, AssetCard: Unified hover pattern
   - FeaturedBrokers: Avatar hover scale
   - Dashboard: Stat cards with shadows, quick access cards with lift

4. **Micro-interactions Added:**
   - Skeleton shimmer animation (motion-safe)
   - Avatar hover scale (hover:scale-105)
   - Dropdown chevron rotation (group-data-[state=open]:rotate-180)
   - Focus ring transitions
   - Button press feedback (active:scale-[0.98])

5. **Documentation Created:**
   - `.planning/codebase/DESIGN-SYSTEM.md` - Full design guide
   - Brand colors, typography, spacing, shadow system
   - Component patterns and golden rules

### Previous Session (2026-01-23)
**V3.5 Navigation & Logo Library:**
- Navigation reorganization (Ressurser, Selskap, Verktøy)
- LogoLibrary component with preview cards
- Avatar image resizing with ImageService
- Sub-offices display on cards
- Employee type system for Entra sync filtering
- API proxy fix (relative URLs for first-party cookies)

---

## Key Documentation

| Document | Purpose |
|----------|---------|
| `CLAUDE.md` | Quick reference for AI agents |
| `.planning/STATE.md` | This file - current status |
| `.planning/PROJECT.md` | Requirements and context |
| `.planning/ROADMAP.md` | Phase breakdown |
| `.planning/codebase/DESIGN-SYSTEM.md` | **Frontend design guidelines** |
| `.planning/codebase/STACK.md` | Technology stack details |

---

## Version History

| Version | Date | Key Changes |
|---------|------|-------------|
| V3.9.1 | 2026-01-25 | Signature mobile compatibility, phone formatting, QA fixes |
| V3.9 | 2026-01-24 | Self-service signature portal with 6-agent pipeline |
| V3.8 | 2026-01-24 | Sync notification system + QA tests |
| V3.7 | 2026-01-24 | UPN mismatch detection for Entra ID SSO |
| V3.6 | 2026-01-23 | Design system enhancement, UI polish |
| V3.5 | 2026-01-23 | Navigation reorganization, Logo Library |
| V3.4 | 2026-01-23 | Portal skins preview |
| V3.3 | 2026-01-23 | API proxy fix for auth cookies |
| V3.2 | 2026-01-22 | Stack upgrade (Next.js 16, React 19) + CI/CD |
| V3.1 | 2026-01-22 | Office & Employee Hub |

---

## Ready for Next Steps

### Option A: WebDAV Employee Photos (RECOMMENDED)
Replace Vitec API base64 images with WebDAV-hosted photos for faster loading.

```powershell
# 1. Upload photos to WebDAV
cd backend
python scripts/upload_employee_photos.py --photos-dir "C:\Users\Adrian\Documents\ProaktivPhotos\webdav-upload" --dry-run

# 2. Update database URLs
python scripts/update_photo_urls_webdav.py --dry-run   # Preview
python scripts/update_photo_urls_webdav.py             # Apply
```

**Scripts ready:** `upload_employee_photos.py`, `update_photo_urls_webdav.py`  
**Photos downloaded:** 184 in `C:\Users\Adrian\Documents\ProaktivPhotos\webdav-upload\`

### Option B: Complete Signature QA
- QA plan: `.cursor/plans/signature_qa_testing_01ae0f96.plan.md`
- Stage 3: Email client rendering (Outlook, Gmail, Apple Mail)
- Stage 4: Mobile device testing
- Stage 5: Edge cases and error states

### Option C: Deploy Signature Emails
- Set environment variables (SIGNATURE_SENDER_EMAIL, FRONTEND_URL)
- Add Mail.Send permission in Azure Portal
- Run `.\backend\scripts\Send-SignatureEmails.ps1 -DryRun` to test
- Run `.\backend\scripts\Send-SignatureEmails.ps1` for full rollout

### Option D: Phase 07 (Office Enhancements)
- 8 execution plans ready
- Region grouping, office merge, SalesScreen
- Can run in parallel with other work

---

## Office Regions Reference

| Region | Areas |
|--------|-------|
| Trøndelag | Trondheim |
| Romerike | Lillestrøm, Lørenskog |
| Sør-Rogaland | Stavanger, Sandnes, Sola |
| Vest | Bergen, Voss |
| Sør | Kristiansand, Skien |
| Øst | Oslo, Drammen |
