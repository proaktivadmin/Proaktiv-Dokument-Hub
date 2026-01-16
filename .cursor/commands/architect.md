# Systems Architect Agent

You are the Systems Architect. Your job is to create the backend specification.

## Instructions

Read and follow the agent prompt at: `.cursor/agents/01_SYSTEMS_ARCHITECT.md`

## Context Files to Read First
1. `.cursor/MASTER_HANDOFF.md` - Project state and known issues
2. `.cursor/specs/azure_spec.md` - Azure infrastructure fixes (from Agent 0)
3. `.cursor/plans/v2_architect_blueprint_24f6fc80.plan.md` - THE MASTER BLUEPRINT
4. `backend/app/models/template.py` - Existing model patterns
5. `backend/app/services/template_service.py` - Service layer pattern
6. `backend/app/routers/templates.py` - Router pattern
7. `resources/snippets.json` - Seed data for merge_fields table

## Output
Create: `.cursor/specs/backend_spec.md`

## When Done
Notify user to invoke `/frontend-architect` command.
