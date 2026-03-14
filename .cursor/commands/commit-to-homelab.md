---
description: Branch → push → homelab deploy → agent QA → merge to main. Use for features and non-urgent changes.
---

# Commit to Homelab

Execute the full homelab QA workflow: create/use feature branch, commit, push, deploy to homelab, run QA, merge to main only if QA passes.

## Required Reading

**Before executing, read:**
- `docs/homelab-qa-workflow.md`
- `docs/qa-checklist-three-gates.md`

## Execute (in order)

1. **Branch:** If on `main`, create `feature/<short-description>`. If user provided a branch name, use it.
2. **Commit:** Stage only relevant paths. Use `scripts/tools/commit_intent.ps1` or `git add` + `git commit`.
3. **Gate 1 — Pre-Commit:** Run checklist from `docs/qa-checklist-three-gates.md` (lint, typecheck, tests, build). Fix failures before proceeding.
4. **Rebase main:** `git fetch origin main && git rebase origin/main` (resolve conflicts if any).
5. **Push:** `git push -u origin feature/<branch>` (use `--force-with-lease` if rebased).
6. **Deploy:** `.\scripts\deploy-homelab.ps1 -Branch feature/<branch>`
7. **Gate 2 — Homelab QA:** Run checklist at http://192.168.77.127:3000. Include console/DevTools, backend logs, and **visual browser inspection** (UI/UX, CSS). See `docs/qa-checklist-three-gates.md`.
8. **Gate 3 — Production Readiness:** Run checklist. CI status, no blockers. See `docs/qa-checklist-three-gates.md`.
9. **Merge (only if all gates pass):** Merge to `main` or to a parent feature branch. `git checkout main && git merge feature/<branch> && git push origin main` (or merge into parent branch if consolidating).
10. **Report:** GO = merged. NO-GO = blocking issues, do not merge.

## Rules

- Never merge to main without all three gates passing.
- Always rebase (or merge) main into the branch before deploying to homelab.
- If QA fails, report blocking issues and stop. Do not merge.

## Decision Points

Before merging, **ask or suggest** per `docs/qa-checklist-three-gates.md`:
- More commits planned today? Consider staging and batching the merge.
- Multiple branches ready? Suggest merging into a parent branch first vs. separate merges.
- Unclear merge target? Ask: main now, or into a larger feature set?

## Mentoring

The user is learning the pipeline. Explain the "why" briefly, suggest best practices, ask before assuming at decision points, and keep the workflow visible.

## Git Structure Reminder

```
main          ← Production. Deploy from here.
  ↑ merge (after QA)
feature/xyz   ← Your branch. Deployed to homelab for testing.
```
