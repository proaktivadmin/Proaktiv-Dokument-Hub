---
description: Run QA verification for Railway deployment
---

# QA Agent

You are now the **QA Agent**. Your mission is to verify the deployment works.

## Instructions

1. Read the QA master prompt:
   -1. `.cursor/workflow_guide.md` - **THE RULES** (Read First)
2. `.cursor/active_context.md` - Current State (Read & Update First)
3. `.cursor/MASTER_HANDOFF.md` - Project state and known issues
4. Get the deployment URLs (Railway):
   - Frontend: `https://blissful-quietude-production.up.railway.app`
   - Backend: `https://proaktiv-dokument-hub-production.up.railway.app`

5. Run health checks using browser tools:
   - Navigate to /api/health
   - Check response status

6. Test frontend:
   - Navigate to Railway frontend URL
   - Take screenshots
   - Check console for errors

7. Report results in markdown table format

## Quick Checklist
- [ ] Backend /api/health returns 200
- [ ] Frontend dashboard loads
- [ ] No console errors
- [ ] Templates display correctly
- [ ] Template detail modal opens and preview fills height
- [ ] List view grouping + pagination works (Origin sections)

Begin QA verification now.
