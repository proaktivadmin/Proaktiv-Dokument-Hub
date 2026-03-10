# Implement (Orchestrated)

Default to single-agent execution.
Use the orchestrator only when escalation triggers are present.

## Escalation Triggers

Use multi-agent orchestration only if one or more are true:

1. Context protection is needed.
2. Subtasks are independent and parallelizable.
3. Specialization/tool-routing needs justify split agents.

## Execute

1. Read `.cursor/context-registry.md`.
2. Select lane:
   - **Single-agent lane** for scoped linear work.
   - **Multi-agent lane** when escalation triggers apply.
3. If multi-agent lane: read and execute `.cursor/agents/00_ORCHESTRATOR.md`.

## Notes

- For template-only requests, orchestrator should route to `/process-template-requests`.
- For failures, orchestrator should route to `/debugger` then `/qa`.
- Before any release recommendation, run `/verify-gates`.
- For retrospective and token/process optimization, run `/token-audit`.
- Report lane used (`single`/`multi`) and escalation reason in final handoff.
