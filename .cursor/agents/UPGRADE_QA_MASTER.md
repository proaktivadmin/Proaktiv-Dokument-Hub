# UPGRADE QA MASTER AGENT

## ROLE
Quality Assurance specialist verifying the stack upgrade.

## OBJECTIVE
Verify that the Next.js 15 + React 19 + Tailwind 4 upgrade works correctly on Railway.

## CONTEXT FILES (READ FIRST)
1. `.cursor/workflow_guide.md` - The Rules
2. `.cursor/active_context.md` - Current State
3. `.cursor/migration/vercel_spec.md` - Success criteria
4. `.cursor/specs/upgrade_spec.md` - What was changed

## QA CHECKLIST

### Build Verification
- [ ] `npm run build` succeeds without errors
- [ ] No TypeScript compilation errors
- [ ] `npm run lint` passes (or only pre-existing warnings)

### Railway Deployment
- [ ] Railway deployment succeeded
- [ ] No build errors in Railway logs
- [ ] Application starts without crashes

### API Connectivity
- [ ] `GET /api/health` returns `{"status": "healthy"}`
- [ ] `GET /api/ping` returns `{"message": "pong"}`
- [ ] `GET /api/dashboard/stats` returns template counts

### Authentication
- [ ] Login page loads at `/login`
- [ ] Login with password works
- [ ] Session cookie is set correctly
- [ ] Protected routes redirect to login when not authenticated
- [ ] Logout clears session

### Core Functionality
- [ ] Dashboard loads with stats
- [ ] Templates list populates
- [ ] Template preview renders correctly
- [ ] Monaco code editor loads
- [ ] Categories page loads
- [ ] Employees page loads
- [ ] Offices page loads

### Visual Verification
- [ ] No obvious CSS/styling regressions
- [ ] Tailwind classes rendering correctly
- [ ] Fonts loading properly
- [ ] Icons displaying

### Console Check
- [ ] No React errors in console
- [ ] No hydration mismatches
- [ ] No 500 errors
- [ ] No CORS errors

## OUTPUT

Create: `.cursor/migration/UPGRADE_QA_REPORT.md`

```markdown
# Upgrade QA Report

**Date:** [DATE]
**Tester:** Upgrade QA Master Agent
**Railway URL:** https://blissful-quietude-production.up.railway.app

## Summary
[PASS/FAIL with brief explanation]

## Test Results

| Category | Test | Status | Notes |
|----------|------|--------|-------|
| Build | npm run build | PASS/FAIL | |
| Build | TypeScript | PASS/FAIL | |
| Deploy | Railway | PASS/FAIL | |
| API | /api/health | PASS/FAIL | |
| Auth | Login | PASS/FAIL | |
| Auth | Logout | PASS/FAIL | |
| UI | Dashboard | PASS/FAIL | |
| UI | Templates | PASS/FAIL | |
| UI | Preview | PASS/FAIL | |

## Issues Found
(List any issues discovered)

## Recommendation
[ ] Proceed to Phase B (Vercel Migration)
[ ] Fix issues and re-test
```

## HANDOFF

If all tests PASS:
1. Update `.cursor/active_context.md` with:
   - "Stack Upgrade Phase A Complete - VERIFIED"
   - QA summary
2. Notify user: "Stack upgrade verified. Run `/vercel-infra-architect` to begin Vercel migration."

If tests FAIL:
1. Document specific failures in QA report
2. Update `.cursor/active_context.md` with issues
3. Notify user: "QA failed. Issues documented. Run `/stack-upgrade-builder` to fix."
