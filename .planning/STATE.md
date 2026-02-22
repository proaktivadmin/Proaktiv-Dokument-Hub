# Project State

> **This is the single source of truth for project status.**
> See also: `CLAUDE.md` (quick reference), `.cursor/workflow_guide.md` (workflow)

## Project Reference

See: .planning/PROJECT.md (updated 2026-01-23)

**Core value:** Brokers can manage and preview document templates without touching code
**Current focus:** Phase 11 — Template production pipeline + QA testing

## Current Position

Phase: 11 (HTML Template Management & Publishing Suite)
Plan: Subagent-driven template builder pipeline — 3-phase orchestrator with 6 specialized subagents
Status: 9 production templates delivered, subagent pipeline designed and validated, file structure reorganized
Last activity: 2026-02-22 — Template builder sprint complete, preparing for signoff

Progress: [██████░░░░] 60% (9 templates built, pipeline operational, 14 source docs in backlog)

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
Stopped at: Template builder sprint complete — 9 production templates, subagent pipeline, file restructure committed
Resume file: N/A
Next step: Manual QA of production templates via Testfletting, then continue backlog conversion (14 remaining source docs)

### Session Summary (2026-02-22 - Latest)

**V4.1 Template Builder Sprint + Subagent Pipeline (2026-02-22):**

This session delivered the full template builder sprint: 9 production-ready Vitec Next HTML templates, a new subagent pipeline architecture, comprehensive documentation, and a reorganized file structure.

**Commit: `7e1e7ef` — Template builder pipeline with subagent architecture**
- 88 files changed, 26,667 insertions

**Production templates delivered (9):**

| Template | Type | Size |
|----------|------|------|
| Kjopekontrakt prosjekt (leilighet) | Contract | 51 KB |
| Kjopekontrakt prosjekt (enebolig) | Contract | 38 KB |
| Kjopekontrakt prosjekt (profesjonell) | Contract | 51 KB |
| Generalfullmakt | Legal form | 12 KB |
| Leieavtale naeringsbygg | Standard form | 70 KB |
| Leieavtale naeringslokaler | Standard form | 61 KB |
| Meglerstandard eiendom | Standard form | 102 KB |
| Forlengelse av oppdrag | Letter | 8 KB |
| Forlengelse av oppdrag (epost) | Email | 4 KB |

**Subagent pipeline architecture (new):**
- 3-phase orchestrator: Analysis (3 parallel) → Construction (1 sequential) → Validation (2 parallel)
- 6 specialized subagents: Structure Analyzer, Field Mapper, Logic Mapper, Builder, Static Validator, Content Verifier
- Structured output formats for subagent handoffs (`scripts/_analysis/FORMAT_*.md`)
- Prompt templates in `.planning/phases/11-template-suite/SUBAGENT-PROMPTS.md`
- Orchestrator spec in `.planning/phases/11-template-suite/AGENT-2B-TEMPLATE-BUILDER.md`

**File structure reorganization:**
- `scripts/production/` — QA-ready HTML files (grab for testing)
- `scripts/handoffs/` — build summaries per template
- `scripts/tools/` — validator, preview, batch scripts
- `scripts/sources/` — original .htm/.docx files
- `scripts/intermediates/` — raw extractions
- `scripts/_analysis/` — subagent outputs + format templates

**Documentation:**
- Vitec HTML ruleset split into 15 modular files (`.planning/vitec-html-ruleset/`)
- vitec-if deep analysis, field registry, V2 analysis report
- Production template pipeline expanded to 15 sections
- Updated SKILL.md with orchestrator flow and quality checklist
- Golden standard templates added for reference

**Backlog:** 14 unconverted source documents remain in `scripts/converted_html/`

### Session Summary (2026-02-22 - Earlier)

**V4.0 Phase 11 Foundation + Infrastructure Fixes (2026-02-21 to 2026-02-22):**

This session delivered the Phase 11 HTML Template Management & Publishing Suite foundation, a dedicated notifications page, Vitec picture proxy restoration, editor fixes, and a critical CSP fix.

**Commits (oldest first):**

1. **`a790f38` — Phase 11: HTML Template Management & Publishing Suite**
   - 39 files changed, 19,352 insertions
   - Full multi-agent plan: 6 agent specs in `.planning/phases/11-template-suite/`
   - Backend services: `WordConversionService`, `TemplateComparisonService`, `TemplateDedupService`, `TemplateWorkflowService`, `TemplateAnalysisAIService`
   - Frontend pages: `/templates/[id]/edit`, `/templates/dedup`
   - Documentation: `vitec-html-ruleset.md` (4,087 lines), `Alle-flettekoder-25.9.md` (6,493 lines)

2. **`63a5ff7` — RTF support, A3 validation fix, dedup improvements**

3. **`48c7a3b` — Notifications page, Vitec picture proxy, editor fixes**

4. **`ed58bb3` — CSP fix for Monaco Editor and CKEditor CDN**

**Deployed to Vercel:** ✅ Production build successful, all pages rendering

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
| V4.1    | 2026-02-22 | 9 production templates, subagent pipeline, file restructure |
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

### Option A: Manual QA of Production Templates (RECOMMENDED)

9 production templates in `scripts/production/`. For each template:
1. Open in Vitec Next CKEditor (paste HTML)
2. Run Testfletting against a test property
3. Verify PDF rendering: page breaks, checkboxes, conditional sections, merge fields
4. If satisfied, commit to template database

### Option B: Continue Template Backlog

14 unconverted source documents in `scripts/converted_html/`. To convert:
1. Move source to `scripts/sources/`
2. Open new agent session, reference `.agents/skills/vitec-template-builder/SKILL.md`
3. Orchestrator launches subagents automatically
4. Output lands in `scripts/production/`

### Option C: Template Library Inventory Refresh

A Vitec Next export (`vitec-next-export.json`, 247 templates) has metadata but no content.
Needs a content-fetch pass to backfill HTML bodies before library reset.

### Option D: Remaining Infrastructure

- **DB Migration:** `20260221_0001_template_publishing.py` — needs manual apply to Railway
- **WebDAV Employee Photos** — replace base64 with hosted photos
- **Signature Email Deployment** — Send-SignatureEmails.ps1
- **Notifications Page Polish** — approval workflow, batch actions

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
