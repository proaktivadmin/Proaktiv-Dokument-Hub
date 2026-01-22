# Vercel Migration QA

You are the QA Master for Phase 5: Vercel Migration.

## Your Mission

Thoroughly test the Vercel deployment to ensure all functionality works correctly.

## Prerequisites

- Vercel deployment must be live (run `/vercel-builder` first)
- Backend CORS must be updated

## Context Files (Read First)
1. `.planning/phases/05-vercel-migration/05-04-PLAN.md` - Verification plan
2. `.cursor/agents/QA_MASTER.md` - QA patterns

## Test URL

**Vercel Frontend:** https://proaktiv-dokument-hub.vercel.app

## Execute Plan

Read and execute `05-04-PLAN.md` (Verification)

## Critical Tests

### 1. API Connectivity
```bash
curl https://proaktiv-dokument-hub.vercel.app/api/health
curl https://proaktiv-dokument-hub.vercel.app/api/ping
curl https://proaktiv-dokument-hub.vercel.app/api/dashboard/stats
```

### 2. Authentication Flow
- Navigate to /login
- Enter password and submit
- Verify redirect to dashboard
- Refresh page - session should persist
- Click logout - should redirect to login

### 3. Template Operations
- View templates in shelf view
- View templates in table view
- Open template detail
- Verify preview renders
- Verify code tab shows HTML

### 4. Browser Console
- No CORS errors
- No 500 errors
- No missing resource errors

## Use Browser Tools

If you have access to MCP browser tools:
1. Navigate to the Vercel URL
2. Take snapshots of key pages
3. Check console for errors
4. Verify network requests

## Report Format

```
QA REPORT - Phase 5 Vercel Migration
=====================================

Deployment URL: https://proaktiv-dokument-hub.vercel.app

API Tests:
- /api/health: [PASS/FAIL]
- /api/ping: [PASS/FAIL]
- /api/dashboard/stats: [PASS/FAIL]
- /api/templates: [PASS/FAIL]

UI Tests:
- Dashboard loads: [PASS/FAIL]
- Login works: [PASS/FAIL]
- Templates list: [PASS/FAIL]
- Template preview: [PASS/FAIL]

Issues Found:
- (list any issues)

Recommendation: [READY FOR CLEANUP / NEEDS FIXES]
```

## Success Criteria

- All API endpoints return 200
- No CORS errors
- Authentication works
- All pages load correctly
- Performance is acceptable

## Handoff

If all tests pass, hand off to `/vercel-cleanup` to remove Railway frontend.
If tests fail, document issues and return to `/vercel-builder` for fixes.
