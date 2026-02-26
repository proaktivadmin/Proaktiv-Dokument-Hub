# Verify Gates

Run a standard verification gate sequence before QA or deploy decisions.

## Execute

1. Read `.cursor/context-registry.md`.
2. Run `.cursor/agents/06_SPEC_VERIFIER.md` when specs changed.
3. Run `.cursor/agents/07_BACKEND_VERIFIER.md` when backend changed.
4. Run `.cursor/agents/08_FRONTEND_VERIFIER.md` when frontend changed.
5. Run `.cursor/agents/QA_MASTER.md` for final release readiness.

## Output Format

- Scope verified
- Checks run
- Pass/fail counts
- Blocking issues
- Go/no-go recommendation

## Rules

- Do not skip verifier steps for changed areas.
- If any verifier reports blocking failures, stop and route back to builder/debugger.
