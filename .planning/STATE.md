# Project State

> **This is the single source of truth for project status.**
> See also: `CLAUDE.md` (quick reference), `.cursor/workflow_guide.md` (workflow)

## Project Reference

See: .planning/PROJECT.md (updated 2026-01-23)

**Core value:** Brokers can manage and preview document templates without touching code
**Current focus:** Phase 06 Testing OR Phase 07 Office Enhancements

## Current Position

Phase: 3.6 (Design System Enhancement)
Plan: V3.6 complete
Status: Production live
Last activity: 2026-01-23 — Design system enhancement, comprehensive UI polish

Progress: [█████████░] 95% (V3.6 design complete, Phase 06 ready for testing)

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
| 6. Entra ID Signature Sync | 8/8 | Ready for Testing | 2026-01-22 |
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

Last session: 2026-01-23
Stopped at: V3.6 Design System Enhancement complete
Resume file: None (ready for new work)
Next step: Continue with Phase 06 Entra ID testing OR Phase 07 Office Enhancements

### Session Summary (2026-01-23 - Latest)
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
| V3.6 | 2026-01-23 | Design system enhancement, UI polish |
| V3.5 | 2026-01-23 | Navigation reorganization, Logo Library |
| V3.4 | 2026-01-23 | Portal skins preview |
| V3.3 | 2026-01-23 | API proxy fix for auth cookies |
| V3.2 | 2026-01-22 | Stack upgrade (Next.js 16, React 19) + CI/CD |
| V3.1 | 2026-01-22 | Office & Employee Hub |

---

## Ready for Next Steps

### Option A: Phase 06 Testing (Entra ID Sync)
- Run `/entra-qa` command
- Test with real Azure credentials
- Verify profile, photo, and signature sync

### Option B: Phase 07 (Office Enhancements)
- 8 execution plans ready
- Region grouping, office merge, SalesScreen
- Can run in parallel with Phase 06 testing

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
