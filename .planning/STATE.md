# Project State

> **This is the single source of truth for project status.**
> See also: `CLAUDE.md` (quick reference), `.cursor/workflow_guide.md` (workflow)

## Project Reference

See: .planning/PROJECT.md (updated 2026-01-23)

**Core value:** Brokers can manage and preview document templates without touching code
**Current focus:** Phase 06 Testing OR Phase 07 Office Enhancements

## Current Position

Phase: 11 (HTML Template Management & Publishing Suite)
Plan: Multi-agent template suite — documentation, conversion, editor, comparison, dedup, flettekode
Status: Phase 11 foundation committed + notifications page + CSP fix deployed to Vercel
Last activity: 2026-02-22 — Template suite, notifications page, Vitec picture proxy, CSP fix

Progress: [███░░░░░░░] 30% (Phase 11 foundation laid, agents 1-6 planned, partial implementation)

## Performance Metrics

**Velocity:**

- Total plans completed: 8 (Phase 1: 3, Phase 4: 5)
- Average duration: ~2 hours per plan
- Total execution time: ~16 hours

**By Phase:**

| Phase                                | Plans | Status                        | Completed  |
| ------------------------------------ | ----- | ----------------------------- | ---------- |
| 1. Vitec API Connection              | 3/3   | Complete                      | 2026-01-20 |
| 4. Stack Upgrade                     | 5/5   | Complete                      | 2026-01-22 |
| 5. Vercel Migration                  | 2/5   | In Progress                   | -          |
| 6. Entra ID Signature Sync           | 8/8   | Profile Sync ✅ / Exchange ⏸️ | 2026-01-24 |
| 7. Office Enhancements + SalesScreen | 0/8   | Ready                         | -          |

**Recent Trend:**

- Phase 4 completed rapidly (same day)
- CI/CD pipeline now operational

_Updated after each plan completion_

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

Last session: 2026-02-22
Stopped at: Phase 11 foundation committed, CSP fix deployed, Monaco Editor working
Resume file: N/A
Next step: Execute Phase 11 agents (start with Agent 1: Documentation, then Agent 2: Conversion pipeline)

### Session Summary (2026-02-22 - Latest)

**V4.0 Phase 11 Foundation + Infrastructure Fixes (2026-02-21 to 2026-02-22):**

This session delivered the Phase 11 HTML Template Management & Publishing Suite foundation, a dedicated notifications page, Vitec picture proxy restoration, editor fixes, and a critical CSP fix.

**Commits in this session (oldest first):**

1. **`a790f38` — Phase 11: HTML Template Management & Publishing Suite**
   - 39 files changed, 19,352 insertions
   - Full multi-agent plan: 6 agent specs in `.planning/phases/11-template-suite/`
   - Backend services: `WordConversionService` (DOCX/RTF→HTML), `TemplateComparisonService`, `TemplateDedupService`, `TemplateWorkflowService`, `TemplateAnalysisAIService`
   - Backend schemas: `template_comparison.py`, `template_dedup.py`, `template_workflow.py`, `word_conversion.py`
   - Backend migration: `20260221_0001_template_publishing.py` (adds publishing fields to templates)
   - Frontend pages: `/templates/[id]/edit` (full editor), `/templates/dedup` (deduplication dashboard)
   - Frontend components: `CKEditorSandbox`, `DeduplicationDashboard`, `MergeFieldAutocomplete`, `MergeFieldHighlighter`, `MergeFieldPanel`, `TemplateComparison`, `WordConversionDialog`
   - Extended `lib/api.ts` with template workflow, comparison, dedup, and word conversion endpoints
   - Documentation: `vitec-html-ruleset.md` (4,087 lines), `docs/Alle-flettekoder-25.9.md` (6,493 lines), `docs/vitec-stilark.md`
   - Library reset script: `backend/scripts/library_reset.py`

2. **`63a5ff7` — RTF support, A3 validation fix, dedup improvements**
   - Added RTF-to-HTML conversion via `striprtf` library
   - Fixed A3 page size validation (was incorrectly flagging valid templates)
   - Improved deduplication detection with better similarity scoring

3. **`48c7a3b` — Notifications page, Vitec picture proxy, editor fixes**
   - **New `/notifications` page** (556 lines): Filterable by type/severity/read status, date-grouped, expandable metadata, mark-as-read/delete/clear-all actions
   - **Vitec picture proxy re-enabled**: `GET /api/vitec/employees/{id}/picture` and `GET /api/vitec/departments/{id}/picture` — proxies images from Vitec Hub API with resize/crop and caching
   - **Picture sync integration**: Office and employee sync buttons now also trigger picture sync from Vitec Hub
   - **CKEditor CDN fix**: Updated URL from `4.25.1` to `4.25.1-lts` (old URL 404'd)
   - **"Normaliser til Vitec" save workflow**: No longer auto-saves; shows persistent unsaved-changes banner with explicit save button
   - **Office banner fallback**: `onError` handler on `<img>` falls back to colored background
   - **NotificationDropdown**: Added "Se alle varsler (N)" link to notification page

4. **`ed58bb3` — CSP fix for Monaco Editor and CKEditor CDN**
   - Added `https://cdn.jsdelivr.net` and `https://cdn.ckeditor.com` to `script-src` in both `next.config.js` and `vercel.json`
   - Added `'unsafe-eval'` for Monaco Editor's dynamic execution
   - Added CDN domains to `style-src`, `font-src`, and `connect-src` as needed
   - **Root cause of "Loading editor..." bug**: CSP blocked external scripts from loading

**Deployed to Vercel:** ✅ Production build successful, all pages rendering
**Monaco Editor:** ✅ Now loading properly (CSP fix resolved the blocking)

### Session Summary (2026-02-02 - Previous)

**V3.9.4 Signature Page Self-Service Enhancements (Completed):**

Self-service editing on the public `/signature/{id}` page so employees can customize their signature without IT involvement.

Key changes:
- ✅ **Editable fields**: Name, title, phone, email, office + 4 social links (Facebook, Instagram, LinkedIn, homepage)
- ✅ **Edit-toggle UX**: Read-only by default, "Rediger" button switches to edit mode with Save/Cancel/Reset
- ✅ **Signature overrides table**: `signature_overrides` — stores edits separately from synced employee data
- ✅ **Override rendering**: `SignatureService._render_template()` applies overrides when present, falls back to synced values
- ✅ **Platform setup instructions**: OS-aware filter (Windows/Mac, iPhone/Android), 8 email clients covered
- ✅ **Auto-detect OS**: `navigator.userAgent` detection on first visit, persisted in localStorage
- ✅ **Photo hyperlink**: Employee photo in signature HTML wrapped in `<a href>` to homepage URL
- ✅ **Photo upload backend**: Endpoint built, WebDAV path convention matches existing photos
- ✅ **DB fallback**: Base64 storage in `metadata_json` when WebDAV unavailable
- ⏸️ **Photo upload frontend**: Hidden pending WebDAV integration testing
- ✅ **WebDAV credentials**: Configured on Railway (`WEBDAV_URL`, `WEBDAV_USERNAME`, `WEBDAV_PASSWORD`)
- ✅ Removed non-functional iOS Mail deep link button
- ✅ Restored Adrian's profile photo URL after test upload broke it

New files:
- `frontend/src/components/signature/SignatureEditForm.tsx`
- `frontend/src/components/signature/SetupInstructions.tsx`
- `frontend/src/components/signature/SignaturePhotoUpload.tsx` (hidden)
- `frontend/src/hooks/v3/useSignatureOverrides.ts`
- `frontend/src/hooks/v3/useSignaturePhotoUpload.ts`
- `backend/app/models/signature_override.py`
- `backend/app/services/signature_override_service.py`
- `backend/app/schemas/signature_override.py`
- `backend/alembic/versions/20260201_0001_add_signature_overrides.py`

CI notes:
- Fixed ruff import sorting (`File` before `UploadFile`)
- Fixed ruff format (line wrapping in model/service)
- Fixed React 19 strict hooks: no `setState` in `useEffect`, no ref access during render
- Solution: on-demand field population via callback in click handler

Known limitation:
- Outlook iOS inflates signature font sizes ~125% when pasting (platform bug, no HTML fix)

### Session Summary (2026-02-01)

**V3.9.3 Signature Template Production Hardening (Completed):**

Complete rewrite of both with-photo and no-photo email signature templates for cross-platform compatibility and reply-chain resilience.

Key changes:
- ✅ Single unified table layout (no MSO/non-MSO conditional branching for structure)
- ✅ All inline styles, removed all media queries (stripped in reply chains)
- ✅ 7-layer blue hyperlink defense in `<style>` block
- ✅ `<font color="#000000">` wrapping on phone/email links (Outlook Classic fix)
- ✅ `format-detection` meta tags (telephone, date, address, email = no)
- ✅ `&zwnj;` zero-width non-joiners in org number to break iOS auto-detection
- ✅ Explicit Google Maps `<a href>` for office address with full query string
- ✅ `width:100%` + `max-width` outer table for iOS Mail fill
- ✅ MSO conditional wrapper for fixed width on Outlook Classic
- ✅ Dark mode prevention removed (natural inversion across all clients)
- ✅ No-photo template fully aligned with production with-photo version

QA Results:
- Outlook Classic (dark mode): Perfect — black text inverts to white naturally
- Outlook New (desktop): Perfect layout, known Microsoft bug on link color
- iOS Mail (light + dark): Correct layout, phone link shows blue (acceptable)
- Reply chains: Signature survives intact on all tested clients
- Org number: No longer auto-linked as phone number

Known Limitation:
- Outlook New injects `color: rgb(0, 120, 212) !important` on links — Microsoft bug, no HTML fix

Files modified:
- `backend/scripts/templates/email-signature.html` (complete rewrite)
- `backend/scripts/templates/email-signature-no-photo.html` (aligned to match)
- `backend/app/services/signature_service.py` (added `{{OfficeMapUrl}}` variable)

**Pending Work (for Next Agent):**

- ⏳ WebDAV upload: Upload photos to `proaktiv.no/d/photos/employees/` and `photos/offices/`
- ⏳ Database update: Set `profile_image_url` from CSV mapping files
- ⏳ Deploy signature emails to employees via `Send-SignatureEmails.ps1`
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

| Document                              | Purpose                        |
| ------------------------------------- | ------------------------------ |
| `CLAUDE.md`                           | Quick reference for AI agents  |
| `.planning/STATE.md`                  | This file - current status     |
| `.planning/PROJECT.md`                | Requirements and context       |
| `.planning/ROADMAP.md`                | Phase breakdown                |
| `.planning/codebase/DESIGN-SYSTEM.md` | **Frontend design guidelines** |
| `.planning/codebase/STACK.md`         | Technology stack details       |

---

## Version History

| Version | Date       | Key Changes                                                |
| ------- | ---------- | ---------------------------------------------------------- |
| V4.0    | 2026-02-22 | Phase 11 Template Suite foundation, notifications page, CSP fix |
| V3.9.4  | 2026-02-02 | Signature self-service editing, setup instructions, photo link |
| V3.9.3  | 2026-02-01 | Signature template hardening, reply-chain resilience, Maps link |
| V3.11   | 2026-01-28 | Territory seeding (1732), dashboard 500 fixes, office sync |
| V3.9.1  | 2026-01-25 | Signature mobile compatibility, phone formatting, QA fixes |
| V3.9    | 2026-01-24 | Self-service signature portal with 6-agent pipeline        |
| V3.8    | 2026-01-24 | Sync notification system + QA tests                        |
| V3.7    | 2026-01-24 | UPN mismatch detection for Entra ID SSO                    |
| V3.6    | 2026-01-23 | Design system enhancement, UI polish                       |
| V3.5    | 2026-01-23 | Navigation reorganization, Logo Library                    |
| V3.4    | 2026-01-23 | Portal skins preview                                       |
| V3.3    | 2026-01-23 | API proxy fix for auth cookies                             |
| V3.2    | 2026-01-22 | Stack upgrade (Next.js 16, React 19) + CI/CD               |
| V3.1    | 2026-01-22 | Office & Employee Hub                                      |

---

## Ready for Next Steps

### Option A: Execute Phase 11 Agents (RECOMMENDED)

Phase 11 foundation is committed. Execute agents in order:

| Agent | Name | Purpose | Status |
|-------|------|---------|--------|
| 1 | Documentation | Vitec HTML ruleset validation, Flettekode reference | ✅ Docs written |
| 2 | Conversion | Word/RTF → HTML pipeline (mammoth + striprtf) | ✅ Backend built, needs testing |
| 3 | Storage & Editor | CKEditor 4 sandbox, template workflow, publishing | ✅ Components built, needs integration |
| 4 | Comparison | AI-powered template diff analysis | ✅ Service built, needs frontend wiring |
| 5 | Merge/Dedup | Duplicate template consolidation | ✅ Service + dashboard built |
| 6 | Flettekode | Merge field autocomplete & validation | ✅ Components built, needs editor integration |

**Next action:** Run Agent 1 documentation validation, then Agent 2 conversion pipeline testing.

**Plans:** `.planning/phases/11-template-suite/PLAN.md` (master plan), `AGENT-*.md` (per-agent specs)

**DB Migration:** `20260221_0001_template_publishing.py` — **needs manual apply to Railway!**

```powershell
$env:DATABASE_URL = "postgresql://postgres:PASSWORD@shuttle.proxy.rlwy.net:51557/railway"
cd backend
python -m alembic upgrade head
python -m alembic current  # Verify
```

### Option B: Notifications Page Polish

The `/notifications` page is live but could benefit from:
- Sync approval/rejection workflow (approve/deny changes from notification detail)
- Email notification preferences
- Batch actions on filtered notifications

### Option C: WebDAV Employee Photos

Replace Vitec API base64 images with WebDAV-hosted photos for faster loading.

```powershell
cd backend
python scripts/upload_employee_photos.py --photos-dir "C:\Users\Adrian\Documents\ProaktivPhotos\webdav-upload" --dry-run
python scripts/update_photo_urls_webdav.py --dry-run
```

### Option D: Deploy Signature Emails

- Set environment variables (SIGNATURE_SENDER_EMAIL, FRONTEND_URL)
- Add Mail.Send permission in Azure Portal
- Run `.\backend\scripts\Send-SignatureEmails.ps1 -DryRun` to test

### Option E: Phase 07 (Office Enhancements)

- 8 execution plans ready
- Region grouping, office merge, SalesScreen
- Can run in parallel with other work

---

## Office Regions Reference

| Region       | Areas                    |
| ------------ | ------------------------ |
| Trøndelag    | Trondheim                |
| Romerike     | Lillestrøm, Lørenskog    |
| Sør-Rogaland | Stavanger, Sandnes, Sola |
| Vest         | Bergen, Voss             |
| Sør          | Kristiansand, Skien      |
| Øst          | Oslo, Drammen            |
