# Deploy Gates

Run explicit go/no-go checks before deployment decisions.

## Gate Sequence

1. Run `/verify-gates` and require all changed-scope verifiers to pass.
2. Confirm migrations:
   - Follow `.cursor/rules/database-migrations.mdc`.
   - Verify target DB shows expected Alembic head.
3. Smoke-test critical endpoints:
   - `/api/health`
   - `/api/ping`
   - one core business endpoint for changed scope
4. Confirm no blocker diagnostics in recent changes.
5. Generate token/process audit with `/token-audit`.

## Go / No-Go

**GO** only if:
- Verifier gates pass
- Migration state is correct (if schema changed)
- Smoke tests pass
- No unresolved blocker notes

**NO-GO** if any gate fails.

## Output Format

- Decision: `GO` or `NO-GO`
- Gate results (pass/fail)
- Blocking items with owner
- Required next action
