# Implement (Orchestrated)

Use the orchestrator for multi-step feature execution with architecture, build, and verification gates.

## Execute

1. Read `.cursor/context-registry.md`.
2. Read and execute `.cursor/agents/00_ORCHESTRATOR.md`.

## Notes

- For template-only requests, orchestrator should route to `/process-template-requests`.
- For failures, orchestrator should route to `/debugger` then `/qa`.
- Before any release recommendation, run `/verify-gates`.
- For retrospective and token/process optimization, run `/token-audit`.
