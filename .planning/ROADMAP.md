# Roadmap: Proaktiv Dokument Hub

## Overview

This roadmap delivers Vitec API integration for employee/office sync, social media link management, and a critical stack upgrade with platform migration. The journey progresses from establishing API connectivity, through building manual review UI for sync operations, adding social media features, upgrading the tech stack to fix CVE-2025-29927, and finally migrating the frontend to Vercel while keeping the backend on Railway.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [x] **Phase 1: Vitec API Connection** - Establish authenticated API connectivity and basic sync triggers
- [x] **Phase 2: Vitec Sync Review UI** - Build field-level diff comparison and manual approval workflow
- [ ] **Phase 3: Social Media Links** - Add social media URL fields to offices and employees
- [x] **Phase 4: Stack Upgrade** - Upgrade Next.js 16, React 19, Tailwind 4, TypeScript 5.9 (fixes CVE-2025-29927)
- [x] **Phase 5: Vercel Migration** - Move frontend to Vercel (completed via manual deployment)
- [x] **Phase 6: Entra ID Signature Sync** - Implementation complete, ready for testing
- [ ] **Phase 7: Office Enhancements** - Region grouping, office merge, SalesScreen integration
- [x] **V3.6: Design System Enhancement** - Comprehensive UI polish with design tokens

## Phase Details

### Phase 1: Vitec API Connection
**Goal**: Admin can connect to Vitec API and trigger employee/office sync operations
**Depends on**: Nothing (first phase)
**Requirements**: VITEC-01, VITEC-02, VITEC-03
**Success Criteria** (what must be TRUE):
  1. Backend successfully authenticates with Vitec Next API
  2. Admin can trigger employee sync and see Vitec employee data fetched
  3. Admin can trigger office sync and see Vitec office data fetched
  4. API errors surface clearly in UI (not silent failures)
**Plans**: 3 plans

Plans:
- [ ] 01-01-PLAN.md - Add Vitec status endpoint and connection verification
- [ ] 01-02-PLAN.md - Improve error feedback and add connection status UI
- [ ] 01-03-PLAN.md - Production verification of complete sync flow

### Phase 2: Vitec Sync Review UI ✅ COMPLETE
**Goal**: Admin can review and approve sync changes field-by-field before committing
**Depends on**: Phase 1
**Requirements**: VITEC-04, VITEC-05, VITEC-06, VITEC-07, VITEC-08
**Success Criteria** (what must be TRUE):
  1. ✅ System matches Vitec employees to local employees by email address
  2. ✅ Admin sees field-by-field diff (old vs new) for each matched record
  3. ✅ Admin can approve or reject individual field changes
  4. ✅ Unmatched Vitec records can be created as new entries
  5. ✅ Sync summary shows counts: new, matched, conflicts
**Completed**: 2026-01-22

**What was delivered:**
- SyncMatchingService: email-based employee matching, vitec_department_id office matching
- SyncPreviewService: field-by-field diff generation with conflict detection
- SyncCommitService: apply approved changes, create new records, batch commits
- Sync page UI: preview cards, diff display, accept/reject controls, commit button
- Employee/office picture sync buttons with proxy URL storage
- Direct sync endpoints for offices and employees (bypasses review for speed)
- Default to showing only active offices/employees with "Vis inaktive" toggle
- Small green/red dot status indicator on office cards
- Avatar images resolved to backend URL (fixes Railway proxy ECONNREFUSED)
- Empty last_name handling for Vitec employees
- Batch database commits to prevent connection timeouts

Plans:
- [x] 02-01: Matching Service (email-based employee matching, office matching)
- [x] 02-02: Diff Generation (field-by-field comparison logic)
- [x] 02-03: Review UI Components (diff display, approve/reject controls)
- [x] 02-04: Sync Commit Logic (apply approved changes, create new records)
- [x] 02-05: Sync Summary Dashboard (change counts, conflict highlights)

### Phase 3: Social Media Links
**Goal**: Offices and employees can display social media links on their profiles
**Depends on**: Nothing (independent of Phases 1-2)
**Requirements**: SOCIAL-01, SOCIAL-02, SOCIAL-03, SOCIAL-04
**Success Criteria** (what must be TRUE):
  1. Office edit form has fields for Instagram, Facebook, Google Business URLs
  2. Employee edit form has optional social media URL fields
  3. Office detail page displays social media links as clickable icons
  4. Featured brokers section shows employees marked for marketing
**Plans**: TBD

Plans:
- [ ] 03-01: Database Schema (social media fields on Office and Employee)
- [ ] 03-02: Office Social UI (edit form fields, detail page display)
- [ ] 03-03: Employee Social UI (edit form, featured broker flag)
- [ ] 03-04: Featured Brokers Section (display on office page)

### Phase 4: Stack Upgrade ✅ COMPLETE
**Goal**: Frontend running on Next.js 16, React 19, Tailwind 4 with no errors
**Depends on**: Nothing (independent, but should complete before Phase 5)
**Requirements**: UPGRADE-01, UPGRADE-02, UPGRADE-03, UPGRADE-04, UPGRADE-05
**Success Criteria** (what must be TRUE):
  1. ✅ Next.js 16 installed and running (CVE-2025-29927 fixed)
  2. ✅ React 19 installed with all components rendering correctly
  3. ✅ Tailwind 4 installed with existing styles preserved
  4. ✅ TypeScript 5.9 with all type checks passing
  5. ✅ Build succeeds with zero TypeScript errors
  6. ✅ CI/CD pipeline added (ESLint, TypeScript, Pyright, Pytest, Vitest)
**Completed**: 2026-01-22

**What was delivered:**
- Next.js 14 → 16.1.4 (skipped 15, went to 16)
- React 18 → 19.2.3
- Tailwind 3 → 4.1.18
- TypeScript 5.3 → 5.9.3
- Added Vitest for frontend testing
- Added Pytest + pytest-asyncio for backend testing
- Added Ruff for Python linting/formatting
- Added Pyright for Python type checking
- Added GitHub Actions CI workflow
- Added Sentry for error tracking (frontend + backend)

### Phase 5: Vercel Migration
**Goal**: Frontend deployed to Vercel with backend remaining on Railway
**Depends on**: Phase 4 ✅
**Requirements**: VERCEL-01, VERCEL-02, VERCEL-03, VERCEL-04, VERCEL-05
**Success Criteria** (what must be TRUE):
  1. Backend CORS accepts requests from Vercel deployment domains
  2. Frontend deployed and accessible on Vercel
  3. API calls from Vercel frontend reach Railway backend successfully
  4. Authentication (login, session, logout) works on Vercel deployment
  5. Railway frontend service deleted after successful migration
**Status**: Ready to start (Phase 4 prerequisite complete)

**Agent Pipeline:**
| Order | Command | Agent | Purpose |
|-------|---------|-------|---------|
| 1 | `/vercel-architect` | Infra Architect | Update CORS, create vercel.json |
| 2 | `/vercel-builder` | Builder | Deploy to Vercel |
| 3 | `/vercel-qa` | QA Master | Full E2E testing |
| 4 | `/vercel-cleanup` | Cleanup | Remove Railway frontend |

Plans:
- [ ] 05-01: CORS Update (add Vercel domains to backend)
- [ ] 05-02: Vercel Config (create vercel.json, update next.config.js)
- [ ] 05-03: Deploy to Vercel (environment variables, initial deploy)
- [ ] 05-04: Verification (full E2E testing)
- [ ] 05-05: Cleanup (remove Railway frontend, update docs)

### Phase 6: Entra ID Signature Sync ✅ IMPLEMENTATION COMPLETE
**Goal**: Sync employee data from PostgreSQL to Microsoft Entra ID with photo and signature support
**Depends on**: Nothing (independent)
**Requirements**: Employee profiles in Entra ID, profile photos, email signatures in Exchange
**Success Criteria** (what must be TRUE):
  1. ✅ PowerShell script syncs employee data to Entra ID
  2. ✅ Profile photos uploaded to Entra ID
  3. ✅ Email signatures pushed to Exchange Online
  4. 🔲 Tested with real Azure credentials
**Status**: Ready for testing
**Completed**: Implementation 2026-01-22

**What was delivered:**
- `Sync-EntraIdEmployees.ps1` - Full PowerShell sync script
- Certificate and client secret authentication
- DryRun mode for safe testing
- HTML/TXT email signature templates
- Backend API endpoints for preview
- Frontend dialogs for individual and batch sync

Plans:
- [x] 06-01 through 06-08: Backend API, service, schemas, frontend components

### Phase 7: Office Enhancements
**Goal**: Add region grouping, office merge, and SalesScreen integration
**Depends on**: Nothing (independent)
**Status**: Ready for implementation

Plans:
- [ ] 07-01: Add region field to offices
- [ ] 07-02: Region filter and grouping UI
- [ ] 07-03: Office merge backend API
- [ ] 07-04: Office merge frontend UI
- [ ] 07-05: SalesScreen fields on Office model
- [ ] 07-06: SalesScreen backend service
- [ ] 07-07: SalesScreen frontend components
- [ ] 07-08: SalesScreen integration with onboarding

### V3.6: Design System Enhancement ✅ COMPLETE
**Goal**: Comprehensive UI polish with brand-aligned design tokens
**Depends on**: Nothing (independent)
**Completed**: 2026-01-23

**What was delivered:**
- Design token system (shadows, transitions, colors)
- 14 base UI components updated
- 5+ feature components enhanced
- 9 micro-interactions added
- Full documentation in `.planning/codebase/DESIGN-SYSTEM.md`

### V3.8-3.9.4: Signature Portal & Notifications ✅ COMPLETE
**Completed**: 2026-01-24 to 2026-02-02
See STATE.md session summaries for details.

### Phase 11: HTML Template Management & Publishing Suite 🔧 IN PROGRESS
**Goal**: Full template lifecycle — import Word/RTF docs, convert to production HTML, validate, QA test, and publish to Vitec Next
**Depends on**: Phase 4 (stack upgrade)
**Status**: 9 production templates delivered, subagent pipeline operational, 14 in backlog
**Plans**: `.planning/phases/11-template-suite/`

**Subagent Pipeline Architecture (V4.1):**

3-phase orchestrator with 6 specialized subagents:

| Phase | Subagents | Model | Purpose |
|-------|-----------|-------|---------|
| 1. Analysis | Structure Analyzer, Field Mapper, Logic Mapper | fast (parallel) | Map document structure, merge fields, vitec-if conditions |
| 2. Construction | Builder | default | Assemble production HTML from analysis outputs |
| 3. Validation | Static Validator, Content Verifier | fast (parallel) | Run 46-54 automated checks + source comparison |

**Key documentation:**
- Builder skill: `.agents/skills/vitec-template-builder/SKILL.md`
- Orchestrator: `.planning/phases/11-template-suite/AGENT-2B-TEMPLATE-BUILDER.md`
- Subagent prompts: `.planning/phases/11-template-suite/SUBAGENT-PROMPTS.md`
- Pipeline reference: `.planning/phases/11-template-suite/PRODUCTION-TEMPLATE-PIPELINE.md`
- Vitec HTML ruleset: `.planning/vitec-html-ruleset/` (15 modular files)

**Production templates delivered (9):**
- Kjopekontrakt prosjekt (leilighet, enebolig, profesjonell)
- Generalfullmakt
- Leieavtale naeringsbygg / naeringslokaler
- Meglerstandard eiendom
- Forlengelse av oppdrag (standard + epost)

**File structure:**
- `scripts/production/` — QA-ready HTML (grab for testing)
- `scripts/handoffs/` — build summaries
- `scripts/tools/` — validator, preview, batch scripts
- `scripts/sources/` — original Word exports
- `scripts/_analysis/` — subagent outputs + format templates

**Remaining work:**
- Manual QA of 9 production templates via Testfletting
- Convert 14 remaining source documents from backlog
- Apply migration `20260221_0001_template_publishing.py` to Railway
- Vitec Next template library inventory refresh (247 templates scraped, content pending)
- Integration of CKEditor sandbox, comparison service, dedup workflow in web UI

### V4.0: Infrastructure & UX Fixes ✅ COMPLETE
**Goal**: Fix Monaco/CKEditor loading, add notifications page, restore Vitec pictures
**Completed**: 2026-02-22

**What was delivered:**
- CSP fix: Added CDN domains to `script-src` for Monaco + CKEditor
- Notifications page: `/notifications` with filters, date grouping, metadata display
- Vitec picture proxy: Re-enabled employee/office picture endpoints
- Picture sync integration: Sync buttons now also fetch pictures
- Editor UX: "Normaliser til Vitec" no longer auto-saves, shows explicit save banner
- CKEditor CDN: Fixed 404 on version 4.25.1 → 4.25.1-lts

---

## Progress

**Execution Order:**
Phases execute in numeric order, with V3.x versions as incremental feature releases.

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Vitec API Connection | 3/3 | Complete | 2026-01-20 |
| 2. Vitec Sync Review UI | 5/5 | Complete | 2026-01-22 |
| 3. Social Media Links | 0/4 | Not started | - |
| 4. Stack Upgrade | 5/5 | Complete | 2026-01-22 |
| 5. Vercel Migration | 5/5 | Complete | 2026-01-23 |
| 6. Entra ID Sync | 8/8 | Ready for Testing | 2026-01-22 |
| 7. Office Enhancements | 0/8 | Not started | - |
| V3.6 Design System | Complete | Complete | 2026-01-23 |
| V3.8-3.9.4 Signatures | Complete | Complete | 2026-02-02 |
| 11. Template Suite | 9 templates + pipeline | In Progress | - |
| V4.0 Infra & UX | Complete | Complete | 2026-02-22 |
| V4.1 Template Sprint | Complete | Complete | 2026-02-22 |

---
*Roadmap created: 2026-01-20*
*Last updated: 2026-02-22 (V4.1 template builder sprint + subagent pipeline)*
