# Codebase Concerns

**Analysis Date:** 2026-01-20

## Tech Debt

**Deprecated Azure Storage Service:**
- Issue: `AzureStorageService` is fully deprecated but still imported and instantiated
- Files: `backend/app/services/azure_storage_service.py`, `backend/app/routers/templates.py:17`
- Impact: Dead code adds confusion, template router imports unused service
- Fix approach: Remove service file and all imports; keep only if rollback mechanism is actually needed

**Mock Authentication in Production Code:**
- Issue: `get_mock_user()` returns hardcoded admin user regardless of actual auth state
- Files: `backend/app/config.py:165-178`, `backend/app/routers/templates.py:123-125`, `backend/app/routers/storage.py:24-26`
- Impact: Audit logs show "admin@proaktiv.no" for all actions; no real user tracking
- Fix approach: Replace mock user with actual session user extraction from JWT payload

**Debug Logging in Production:**
- Issue: Extensive debug logging hardcoded in alembic migrations with absolute Windows paths
- Files: `backend/alembic/env.py:26-40`
- Impact: Debug logs written to hardcoded Windows path; fails on Linux/production
- Fix approach: Remove debug logging from env.py or make path configurable

**Legacy V1 Directory:**
- Issue: `_legacy_v1/` directory contains old code that should be removed
- Files: `_legacy_v1/library/`
- Impact: Repository bloat, potential confusion
- Fix approach: Archive externally if needed, remove from repo

**Console Logging Throughout Frontend:**
- Issue: 65+ console.log/console.error calls scattered across production code
- Files: `frontend/src/lib/api.ts`, `frontend/src/hooks/*.ts`, multiple components
- Impact: Noise in browser console; potential information leakage
- Fix approach: Use structured logging service or remove debug statements

## Known Bugs

**WebDAV Integration Disabled:**
- Symptoms: Storage browser shows "WebDAV not configured" even when credentials set
- Files: `backend/app/services/webdav_service.py:9-11`
- Trigger: Code comment indicates PROPFIND not enabled on proaktiv.no server
- Workaround: Feature is documented as disabled pending server config

**TODO: Category Support Missing:**
- Symptoms: Grouping by category defaults to "Alle" for all templates
- Files: `frontend/src/hooks/v2/useGroupedTemplates.ts:71`
- Trigger: Any template grouping operation
- Workaround: None - feature incomplete

**TODO: Azure SAS URL Generation Incomplete:**
- Symptoms: Download URL generation may fail
- Files: `backend/app/routers/templates.py:451`
- Trigger: Requesting template download URL
- Workaround: Templates stored in database now, may not affect current flow

**TODO: Auth User Missing in External Listings:**
- Symptoms: `verified_by` always shows "system" instead of actual user
- Files: `backend/app/routers/external_listings.py:160`
- Trigger: Verifying external listings
- Workaround: None - always records "system"

## Security Considerations

**XSS via dangerouslySetInnerHTML:**
- Risk: Template content rendered directly via `dangerouslySetInnerHTML` without sanitization
- Files: `frontend/src/components/viewer/DocumentViewer.tsx:169,188`, `frontend/src/components/templates/TemplateSettingsPanel.tsx:706`
- Current mitigation: Content comes from database (trusted source); sanitizer service exists for Vitec compliance
- Recommendations: Apply HTML sanitization before rendering; use DOMPurify or similar on client

**Debug Endpoint in Storage Router:**
- Risk: `/api/storage/debug` endpoint exposes raw WebDAV responses including potential server details
- Files: `backend/app/routers/storage.py:138-200`
- Current mitigation: Requires authentication when auth enabled
- Recommendations: Remove or restrict to development environment only

**No Rate Limiting:**
- Risk: API endpoints lack rate limiting; vulnerable to abuse
- Files: All routers in `backend/app/routers/`
- Current mitigation: None detected
- Recommendations: Add FastAPI-Limiter or similar middleware; critical for login endpoint

**CORS Wildcard in Auth Middleware:**
- Risk: 401 responses include `Access-Control-Allow-Origin: *` as fallback
- Files: `backend/app/middleware/auth.py:36`
- Current mitigation: Overridden by main CORS for valid requests
- Recommendations: Remove wildcard fallback; use configured origins only

**Single Password Auth:**
- Risk: Single shared password for all users; no user differentiation
- Files: `backend/app/routers/auth.py`
- Current mitigation: Password is bcrypt hashed; sessions are JWT with expiry
- Recommendations: Acceptable for single-user admin tool; document limitation

## Performance Bottlenecks

**Eager Loading All Relationships:**
- Problem: Template queries use `lazy="selectin"` loading all relationships by default
- Files: `backend/app/models/template.py:166-185`
- Cause: Tags, categories, and versions loaded even when not needed
- Improvement path: Use explicit `selectinload` only when relationships needed; default to `lazy="raise"`

**Large Frontend Components:**
- Problem: Several components exceed 500 lines with complex state management
- Files: `frontend/src/components/templates/TemplateSettingsPanel.tsx` (715 lines), `frontend/src/app/templates/page.tsx` (645 lines), `frontend/src/components/templates/TemplateDetailSheet.tsx` (618 lines)
- Cause: Feature accumulation without refactoring
- Improvement path: Extract sub-components; use custom hooks for state logic

**Large Backend Files:**
- Problem: Router and service files grown too large
- Files: `backend/app/routers/templates.py` (615 lines), `backend/app/routers/storage.py` (607 lines), `backend/app/services/employee_service.py` (557 lines)
- Cause: All template operations in single file
- Improvement path: Split by operation type (CRUD, analysis, content)

**SQLite JSON Filtering Fallback:**
- Problem: Receiver filter falls back to in-memory filtering for SQLite
- Files: `backend/app/services/template_service.py:109-137`
- Cause: SQLite JSON containment unreliable
- Improvement path: Document PostgreSQL requirement; remove SQLite support if not needed

## Fragile Areas

**Template Content Service:**
- Files: `backend/app/services/template_content_service.py`
- Why fragile: Handles multiple content types (HTML, DOCX, PDF) with different code paths
- Safe modification: Add tests for each content type before changes
- Test coverage: None detected

**Vitec Normalizer Service:**
- Files: `backend/app/services/vitec_normalizer_service.py`
- Why fragile: Complex HTML/CSS parsing with many edge cases for Vitec compliance
- Safe modification: Use existing tests as baseline; add tests for new edge cases
- Test coverage: Has unit tests at `backend/tests/test_vitec_normalizer_service.py`

**Microsoft Graph Integration:**
- Files: `backend/app/integrations/microsoft_graph.py`
- Why fragile: External API dependency; placeholder credentials in production config
- Safe modification: Mock all external calls; test failure scenarios
- Test coverage: None detected

## Scaling Limits

**In-Memory Template Filtering:**
- Current capacity: Works for ~100s of templates
- Limit: Large template libraries will slow significantly with receiver filtering on SQLite
- Scaling path: Enforce PostgreSQL; add database indexes for receiver queries

**Single-Instance WebDAV Client:**
- Current capacity: Singleton pattern limits concurrent operations
- Limit: May bottleneck under high load
- Scaling path: Pool WebDAV connections; add retry/circuit breaker

## Dependencies at Risk

**Next.js Security Vulnerability:**
- Risk: `package-lock.json` notes security vulnerability requiring upgrade
- Files: `frontend/package-lock.json:6037`
- Impact: Security vulnerability in Next.js
- Migration plan: Upgrade to patched Next.js version (see https://nextjs.org/blog/security-update-2025-12-11)

**Deprecated npm Packages:**
- Risk: ESLint and related packages deprecated
- Files: `frontend/package-lock.json:213,243,4068`
- Impact: May stop receiving updates
- Migration plan: Migrate to newer ESLint config format

## Missing Critical Features

**No Automated Testing:**
- Problem: Only 2 test files found in backend; none in frontend
- Files: `backend/tests/test_vitec_normalizer_service.py`, `backend/tests/test_vitec_hub_sync_endpoints.py`
- Blocks: Safe refactoring; confident deployments
- Priority: High

**No Error Boundary in Frontend:**
- Problem: React errors may crash entire app
- Files: Frontend lacks ErrorBoundary component
- Blocks: Graceful error handling for users
- Priority: Medium

**No Health Check for WebDAV:**
- Problem: WebDAV status only checked on-demand
- Files: `backend/app/services/webdav_service.py`
- Blocks: Proactive monitoring of storage integration
- Priority: Low (feature disabled)

## Test Coverage Gaps

**Frontend - No Tests:**
- What's not tested: All React components, hooks, API clients
- Files: Entire `frontend/src/` directory
- Risk: UI regressions undetected
- Priority: High

**Backend Services - Minimal Coverage:**
- What's not tested: Most services except VitecNormalizerService
- Files: `backend/app/services/template_service.py`, `backend/app/services/employee_service.py`, all other services
- Risk: Business logic regressions undetected
- Priority: High

**Authentication Flow:**
- What's not tested: Login, logout, session validation, middleware
- Files: `backend/app/routers/auth.py`, `backend/app/middleware/auth.py`
- Risk: Auth bypass or session issues undetected
- Priority: High

**API Endpoints:**
- What's not tested: All FastAPI routers
- Files: `backend/app/routers/*.py`
- Risk: API contract changes break clients
- Priority: Medium

---

*Concerns audit: 2026-01-20*
