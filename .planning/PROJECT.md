# Proaktiv Dokument Hub

## What This Is

A document template management system for Norwegian real estate brokers, integrated with Vitec Next. Brokers manage document templates (contracts, listings, emails, SMS) with live preview, merge field support, and organizational structure (offices, employees). Production live on Railway.

## Core Value

**Brokers can manage and preview document templates without touching code.** The document preview is primary — code editing is the escape hatch, not the default.

## Requirements

### Validated

*Shipped and working in production.*

- ✓ Template CRUD with live preview — existing
- ✓ Template categorization and tagging — existing
- ✓ Merge field syntax support (`[[field.name]]`, `vitec-if`, `vitec-foreach`) — existing
- ✓ Monaco code editor for power users — existing
- ✓ A4 page break visualization — existing
- ✓ Simulator with test data persistence — existing
- ✓ Visual code generator for Vitec snippets — existing
- ✓ Office management with banner images — existing (V3.1)
- ✓ Employee profiles with avatars — existing (V3.1)
- ✓ Office-employee relationships — existing (V3.1)
- ✓ JWT session authentication — existing
- ✓ WebDAV storage integration — existing
- ✓ Storage browser UI — existing

### Active

*Current scope — building toward these.*

**Milestone 1: Vitec API Integration**
- [x] Vitec API connection verified and working
- [ ] Employee sync from Vitec with manual review UI
- [ ] Office sync from Vitec with manual review UI
- [ ] Field-by-field diff comparison for sync conflicts
- [ ] Email-based matching for employees
- [ ] Template sync from Vitec (future)
- [ ] Property sync with status filters (future)

**Milestone 2: Social Media Links**
- [ ] Social media URL fields on offices (Instagram, Facebook, Google Business)
- [ ] Featured broker accounts with personal social links
- [ ] Social links displayed on office detail pages

**Milestone 3: Stack Upgrade + Vercel Migration**
- [x] Next.js 14 → 16 upgrade (fixes CVE-2025-29927)
- [x] React 18 → 19 upgrade
- [x] Tailwind 3 → 4 upgrade
- [x] TypeScript 5.3 → 5.9 upgrade
- [x] CI/CD pipeline with testing (GitHub Actions)
- [x] Sentry error tracking (frontend + backend)
- [ ] Frontend migrated from Railway to Vercel
- [ ] Backend remains on Railway with updated CORS

### Out of Scope

*Explicit boundaries — not building these.*

- Social media API integration — Static links only, no OAuth/metrics pulling
- Customer data from Vitec — Hard boundary, never
- Real-time collaboration — Single-user admin tool
- Mobile app — Web-only for now
- Multi-tenant — Single organization (Proaktiv)

## Context

**Current State:**
- V3.6 complete with Design System Enhancement
- 6 offices, 23 employees in database (from proaktiv.no)
- 44 templates across 11 categories
- Production live on Vercel (frontend) + Railway (backend + PostgreSQL)
- CI/CD pipeline operational (GitHub Actions)
- Full testing infrastructure (Vitest + Pytest)
- Comprehensive design token system implemented

**Stack Versions (as of 2026-01-23):**
- Next.js 16.1.4, React 19.2.3, Tailwind 4.1.18
- TypeScript 5.9.3
- FastAPI 0.109.0, SQLAlchemy 2.0.46
- Sentry error tracking enabled
- Custom design tokens (shadows, transitions, colors)

**Vitec Integration:**
- API credentials configured in `.env` and Railway variables
- Test request successful (200 OK via Bruno)
- Vitec env vars already in backend config (`VITEC_*`)
- Employee count expected to increase to ~125 after sync
- Some duplicate offices to clean up

**Existing Plans:**
- Social media spec exists (oversized — simplified to static links)
- Stack upgrade complete — CVE-2025-29927 fixed
- Vercel migration pending (Phase 5)

## Constraints

- **Platform**: Railway backend (unchanged), Vercel frontend (after migration)
- **Auth**: Single-user password auth, no multi-user needed
- **Language**: Norwegian UI, Norwegian real estate domain
- **Data**: No customer data from Vitec — ever
- **Sync**: Manual review for all data sync operations — no auto-overwrite

## Key Decisions

| Decision | Rationale | Outcome |
|----------|-----------|---------|
| Manual sync review | Prevent bad data overwrites, case-by-case control | — Pending |
| Email-based employee matching | Most reliable identifier across systems | — Pending |
| Field-by-field diff | User can choose per-field, not all-or-nothing | — Pending |
| Static social links (no API) | Simpler, links rarely change, defer API complexity | — Pending |
| Upgrade before migrate | Fix security vulnerability first, test on one platform | ✅ Done |
| Skip Next.js 15, go to 16 | Latest stable with React 19 support, better compatibility | ✅ Done |
| Vercel for frontend | Better Next.js DX, preview deployments, keep backend on Railway | — Pending |
| xfail incomplete tests | Don't block CI, track features that need implementation | ✅ Done |
| Lenient Pyright config | Disable strict type checks for pre-existing issues | ✅ Done |
| Design token system | Centralized shadows, transitions, colors for consistency | ✅ Done |
| Bronze for accents | Use bronze instead of blue for selection/focus states | ✅ Done |
| Serif for headings | Premium feel with Playfair Display for headings | ✅ Done |

---
*Last updated: 2026-01-23 after V3.6 Design System Enhancement*
