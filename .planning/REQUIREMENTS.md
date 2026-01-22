# Requirements: Proaktiv Dokument Hub

**Defined:** 2026-01-20
**Core Value:** Brokers can manage and preview document templates without touching code

## v1 Requirements

Requirements for current milestone. Each maps to roadmap phases.

### Vitec API Integration

- [ ] **VITEC-01**: Backend can connect to Vitec Next API and make authenticated requests
- [ ] **VITEC-02**: Admin can trigger employee sync from Vitec
- [ ] **VITEC-03**: Admin can trigger office sync from Vitec
- [ ] **VITEC-04**: System matches employees by email address
- [ ] **VITEC-05**: Admin sees field-by-field diff for each match
- [ ] **VITEC-06**: Admin can approve/reject each field change individually
- [ ] **VITEC-07**: Sync creates new entries for unmatched Vitec records
- [ ] **VITEC-08**: Sync UI shows summary of changes (new, matched, conflicts)

### Social Media Links

- [ ] **SOCIAL-01**: Office has fields for Instagram, Facebook, Google Business URLs
- [ ] **SOCIAL-02**: Employee has optional social media URL fields
- [ ] **SOCIAL-03**: Office detail page displays social media links
- [ ] **SOCIAL-04**: Featured brokers section shows employees marked for marketing

### Stack Upgrade

- [x] **UPGRADE-01**: Frontend upgraded to Next.js 16 (skipped 15)
- [x] **UPGRADE-02**: Frontend upgraded to React 19
- [x] **UPGRADE-03**: Frontend upgraded to Tailwind 4
- [x] **UPGRADE-04**: TypeScript upgraded to 5.9, all type checks passing
- [x] **UPGRADE-05**: Build succeeds with no TypeScript errors
- [x] **UPGRADE-06**: CI/CD pipeline added (GitHub Actions)
- [x] **UPGRADE-07**: Testing infrastructure (Vitest + Pytest)

### Vercel Migration

- [ ] **VERCEL-01**: Backend CORS updated for Vercel domains
- [ ] **VERCEL-02**: Frontend deployed to Vercel
- [ ] **VERCEL-03**: API rewrites working (frontend → Railway backend)
- [ ] **VERCEL-04**: Authentication works on Vercel deployment
- [ ] **VERCEL-05**: Railway frontend service removed

## v2 Requirements

Deferred to future release. Tracked but not in current roadmap.

### Vitec Extended

- **VITEC-F01**: Template sync from Vitec
- **VITEC-F02**: Property sync with status filters

### Social Media Extended

- **SOCIAL-F01**: Google Business API integration
- **SOCIAL-F02**: Analytics dashboard

## Out of Scope

Explicitly excluded. Documented to prevent scope creep.

| Feature | Reason |
|---------|--------|
| Customer data from Vitec | Privacy/legal — hard boundary, never |
| Social media API integration | Complexity — static links sufficient for now |
| Auto-sync without review | Data quality — manual approval required |
| Multi-tenant support | Single organization (Proaktiv) |
| Mobile app | Web-only admin tool |

## Traceability

Which phases cover which requirements. Updated during roadmap creation.

| Requirement | Phase | Status |
|-------------|-------|--------|
| VITEC-01 | Phase 1 | ✅ Complete |
| VITEC-02 | Phase 1 | ✅ Complete |
| VITEC-03 | Phase 1 | ✅ Complete |
| VITEC-04 | Phase 2 | Pending |
| VITEC-05 | Phase 2 | Pending |
| VITEC-06 | Phase 2 | Pending |
| VITEC-07 | Phase 2 | Pending |
| VITEC-08 | Phase 2 | Pending |
| SOCIAL-01 | Phase 3 | Pending |
| SOCIAL-02 | Phase 3 | Pending |
| SOCIAL-03 | Phase 3 | Pending |
| SOCIAL-04 | Phase 3 | Pending |
| UPGRADE-01 | Phase 4 | ✅ Complete |
| UPGRADE-02 | Phase 4 | ✅ Complete |
| UPGRADE-03 | Phase 4 | ✅ Complete |
| UPGRADE-04 | Phase 4 | ✅ Complete |
| UPGRADE-05 | Phase 4 | ✅ Complete |
| UPGRADE-06 | Phase 4 | ✅ Complete |
| UPGRADE-07 | Phase 4 | ✅ Complete |
| VERCEL-01 | Phase 5 | Pending |
| VERCEL-02 | Phase 5 | Pending |
| VERCEL-03 | Phase 5 | Pending |
| VERCEL-04 | Phase 5 | Pending |
| VERCEL-05 | Phase 5 | Pending |

**Coverage:**
- v1 requirements: 24 total
- Complete: 10 (Phase 1 + Phase 4)
- Pending: 14
- Unmapped: 0 ✓

---
*Requirements defined: 2026-01-20*
*Last updated: 2026-01-22 after Phase 4 completion*
