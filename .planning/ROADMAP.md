# Roadmap: Proaktiv Dokument Hub

## Overview

This roadmap delivers Vitec API integration for employee/office sync, social media link management, and a critical stack upgrade with platform migration. The journey progresses from establishing API connectivity, through building manual review UI for sync operations, adding social media features, upgrading the tech stack to fix CVE-2025-29927, and finally migrating the frontend to Vercel while keeping the backend on Railway.

## Phases

**Phase Numbering:**
- Integer phases (1, 2, 3): Planned milestone work
- Decimal phases (2.1, 2.2): Urgent insertions (marked with INSERTED)

Decimal phases appear between their surrounding integers in numeric order.

- [ ] **Phase 1: Vitec API Connection** - Establish authenticated API connectivity and basic sync triggers
- [ ] **Phase 2: Vitec Sync Review UI** - Build field-level diff comparison and manual approval workflow
- [ ] **Phase 3: Social Media Links** - Add social media URL fields to offices and employees
- [ ] **Phase 4: Stack Upgrade** - Upgrade Next.js 15, React 19, Tailwind 4 (fixes CVE-2025-29927)
- [ ] **Phase 5: Vercel Migration** - Move frontend to Vercel, update backend CORS, cleanup Railway

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
**Plans**: TBD

Plans:
- [ ] 01-01: Vitec API Service (authentication, client setup)
- [ ] 01-02: Sync Trigger Endpoints (employee sync, office sync routes)
- [ ] 01-03: Admin Sync UI (buttons, loading states, basic results display)

### Phase 2: Vitec Sync Review UI
**Goal**: Admin can review and approve sync changes field-by-field before committing
**Depends on**: Phase 1
**Requirements**: VITEC-04, VITEC-05, VITEC-06, VITEC-07, VITEC-08
**Success Criteria** (what must be TRUE):
  1. System matches Vitec employees to local employees by email address
  2. Admin sees field-by-field diff (old vs new) for each matched record
  3. Admin can approve or reject individual field changes
  4. Unmatched Vitec records can be created as new entries
  5. Sync summary shows counts: new, matched, conflicts
**Plans**: TBD

Plans:
- [ ] 02-01: Matching Service (email-based employee matching, office matching)
- [ ] 02-02: Diff Generation (field-by-field comparison logic)
- [ ] 02-03: Review UI Components (diff display, approve/reject controls)
- [ ] 02-04: Sync Commit Logic (apply approved changes, create new records)
- [ ] 02-05: Sync Summary Dashboard (change counts, conflict highlights)

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

### Phase 4: Stack Upgrade
**Goal**: Frontend running on Next.js 15, React 19, Tailwind 4 with no errors
**Depends on**: Nothing (independent, but should complete before Phase 5)
**Requirements**: UPGRADE-01, UPGRADE-02, UPGRADE-03, UPGRADE-04, UPGRADE-05
**Success Criteria** (what must be TRUE):
  1. Next.js 15 installed and running (CVE-2025-29927 fixed)
  2. React 19 installed with all components rendering correctly
  3. Tailwind 4 installed with existing styles preserved
  4. All async request APIs (cookies, headers, params) properly awaited
  5. Build succeeds with zero TypeScript errors
**Plans**: TBD

Plans:
- [ ] 04-01: Next.js 15 Upgrade (dependencies, config changes)
- [ ] 04-02: React 19 Upgrade (dependency update, component fixes)
- [ ] 04-03: Tailwind 4 Upgrade (config migration, style verification)
- [ ] 04-04: Async API Migration (cookies/headers/params await patterns)
- [ ] 04-05: Build Verification (TypeScript errors, runtime testing)

### Phase 5: Vercel Migration
**Goal**: Frontend deployed to Vercel with backend remaining on Railway
**Depends on**: Phase 4
**Requirements**: VERCEL-01, VERCEL-02, VERCEL-03, VERCEL-04, VERCEL-05
**Success Criteria** (what must be TRUE):
  1. Backend CORS accepts requests from Vercel deployment domains
  2. Frontend deployed and accessible on Vercel
  3. API calls from Vercel frontend reach Railway backend successfully
  4. Authentication (login, session, logout) works on Vercel deployment
  5. Railway frontend service deleted after successful migration
**Plans**: TBD

Plans:
- [ ] 05-01: Backend CORS Update (add Vercel domains)
- [ ] 05-02: Vercel Deployment Setup (project creation, env vars)
- [ ] 05-03: API Rewrite Configuration (frontend to backend routing)
- [ ] 05-04: Auth Testing (login flow verification on Vercel)
- [ ] 05-05: Railway Cleanup (remove frontend service)

## Progress

**Execution Order:**
Phases execute in numeric order: 1 -> 2 -> 3 -> 4 -> 5
(Note: Phases 3 and 4 could run in parallel as they are independent)

| Phase | Plans Complete | Status | Completed |
|-------|----------------|--------|-----------|
| 1. Vitec API Connection | 0/3 | Not started | - |
| 2. Vitec Sync Review UI | 0/5 | Not started | - |
| 3. Social Media Links | 0/4 | Not started | - |
| 4. Stack Upgrade | 0/5 | Not started | - |
| 5. Vercel Migration | 0/5 | Not started | - |

---
*Roadmap created: 2026-01-20*
*Last updated: 2026-01-20*
