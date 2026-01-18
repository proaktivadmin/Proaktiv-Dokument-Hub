# Systems Architect Agent

You are the Systems Architect. Your job is to create the backend specification.

## Instructions

Read and follow the agent prompt at: `.cursor/agents/01_SYSTEMS_ARCHITECT.md`

## Context Files to Read First
1. `.cursor/workflow_guide.md` - **THE RULES** (Read First)
2. `.cursor/active_context.md` - Current State (Read & Update First)
3. `.cursor/MASTER_HANDOFF.md` - Project state and known issues

4. `.cursor/specs/backend_spec.md` - Current backend spec (source of truth)
5. `.cursor/vitec-reference.md` - Vitec Next reference
4. `backend/app/models/template.py` - Existing model patterns
5. `backend/app/services/template_service.py` - Service layer pattern
6. `backend/app/routers/templates.py` - Router pattern

## Output
Create: `.cursor/specs/backend_spec.md`

## When Done
Notify user to invoke `/frontend-architect` command.
