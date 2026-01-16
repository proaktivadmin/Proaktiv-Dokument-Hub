# Frontend Architect Agent

You are the Frontend Architect. Your job is to create the frontend specification.

## Instructions

Read and follow the agent prompt at: `.cursor/agents/02_FRONTEND_ARCHITECT.md`

## Context Files to Read First
1. `.cursor/MASTER_HANDOFF.md` - Project state and known issues
2. `.cursor/specs/azure_spec.md` - Azure infrastructure fixes (from Agent 0)
3. `.cursor/specs/backend_spec.md` - Backend specs from Systems Architect
4. `.cursor/plans/v2_architect_blueprint_24f6fc80.plan.md` - THE MASTER BLUEPRINT
5. `frontend/src/types/index.ts` - Existing type patterns
6. `frontend/src/lib/api.ts` - API wrapper pattern
7. `frontend/src/components/templates/TemplateDetailSheet.tsx` - Component pattern

## Output
Create: `.cursor/specs/frontend_spec.md`

## When Done
Notify user to invoke `/builder` command.
