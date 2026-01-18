---
description: Run the Debugger Agent for Railway deployment issues
---

# Debugger Agent

You are now the **Debugger Agent**. Your mission is to fix the Railway deployment.

## Instructions

1. `.cursor/workflow_guide.md` - **THE RULES** (Read First)
2. `.cursor/active_context.md` - Current State (Read & Update First)
3. Read the debugging plan:
   - `.cursor/plans/railway_deployment_debug_*.plan.md`

4. Read the agent prompt:
   - `.cursor/agents/DEBUGGER_AGENT.md`

5. Follow the 4-phase methodology:
   - Phase 1: Add Visibility (startup logging)
   - Phase 2: Isolate the Failure (identify root cause)
   - Phase 3: Fix Root Cause (targeted fix)
   - Phase 4: Verify Fix (push and test)

4. After each change:
   - Commit with descriptive message
   - Push to `main`
   - Monitor Railway deployment
   - Report status

## Quick Context

**Problem:** Railway healthcheck fails - Uvicorn never starts after Alembic

**Likely Causes:**
1. SECRET_KEY validation crashes before logging starts
2. Alembic migration hangs or fails silently
3. Import error in app modules
4. Railway using wrong start command

**Files to Focus On:**
- `backend/app/main.py`
- `backend/app/config.py`
- `backend/railway.json`

Begin debugging now.
