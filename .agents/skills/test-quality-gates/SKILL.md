---
name: test-quality-gates
description: Verification and quality-gate workflow for backend and frontend changes. Use when implementing features, reviewing fixes, or preparing QA handoff.
---

# Test Quality Gates

## When to Use

- After backend or frontend code changes
- Before QA handoff
- During bug fixes where regressions are likely
- When validating completion claims

## Gate Sequence

1. Spec Gate: ensure implementation matches approved spec.
2. Backend Gate: run backend tests/checks for changed scope.
3. Frontend Gate: run frontend type/tests for changed scope.
4. Integration Gate: verify key user path wiring.
5. QA Gate: final functional validation and reporting.

## Reporting Format

- Scope tested
- Checks run
- Pass/fail counts
- Blocking issues
- Risk notes and deferred items

## Success Checklist

- [ ] All relevant checks executed (or justified if skipped).
- [ ] Failures triaged with owner and next action.
- [ ] Clear go/no-go recommendation for QA/deploy.
