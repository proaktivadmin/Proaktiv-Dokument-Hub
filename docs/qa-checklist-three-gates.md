# Three-Gate QA Checklist

Three checkpoints before code reaches production. Use for `/commit-to-homelab` and any branch → homelab → merge workflow.

---

## Gate 1: Pre-Commit (Before Deploy to Homelab)

**When:** After committing to the feature branch, before pushing and deploying.

**Purpose:** Catch build/test failures locally so homelab receives a viable build.

| Check | Command / Action | Pass |
|-------|------------------|------|
| Frontend lint | `cd frontend && npm run lint` | |
| Frontend typecheck | `cd frontend && npx tsc --noEmit` | |
| Frontend tests | `cd frontend && npm run test:run` | |
| Backend lint | `cd backend && ruff check .` | |
| Backend typecheck | `cd backend && pyright` | |
| Backend tests | `cd backend && pytest` | |
| Frontend build | `cd frontend && npm run build` | |
| Branch rebased on main | `git fetch origin main && git rebase origin/main` | |
| No unintended changes | `git status` — only intended paths staged/committed | |

**GO:** All checks pass. Proceed to push and deploy.

**NO-GO:** Fix failures before deploying to homelab.

---

## Gate 2: Homelab QA (Testing on Homelab)

**When:** After deploy to homelab. App running at http://192.168.77.127:3000

**Purpose:** Verify behavior and appearance in a production-like environment. Features must both **work** and **look** correct.

### Functional checks

| Check | Action | Pass |
|-------|--------|------|
| Deploy succeeded | `.\scripts\deploy-homelab.ps1 -Branch <branch>` completed | |
| Backend health | `curl http://192.168.77.127:8000/api/health` | |
| Login / logout | Manual: log in, navigate, log out | |
| Core pages load | Dashboard, templates, reports (as relevant) | |
| Changed-scope flows | Exercise new/modified features | |
| Critical paths (scope-dependent) | See QA_MASTER or phase plan | |

### Console & DevTools

| Check | Action | Pass |
|-------|--------|------|
| Console errors | Browser DevTools → Console. No red errors or uncaught exceptions | |
| Console warnings | Note any warnings; triage if relevant to changed scope | |
| Network tab | No failed requests (4xx/5xx). No CORS errors. API calls return expected status | |
| Backend logs | `docker compose logs backend` — no tracebacks or repeated errors | |

### Visual & UI/UX inspection

Use Cursor IDE browser MCP (`browser_navigate`, `browser_snapshot`) when available, or manual inspection. Verify features **look** as intended.

| Check | Action | Pass |
|-------|--------|------|
| Layout & spacing | Elements align correctly; no overflow or cut-off content | |
| Typography | Fonts, sizes, weights match design system (`.planning/codebase/DESIGN-SYSTEM.md`) | |
| Colors & contrast | Navy, bronze, beige used correctly; text readable | |
| Interactive states | Hover, focus, disabled states work and look correct | |
| Responsive behavior | Key breakpoints (if applicable) — no broken layouts | |
| Changed UI components | New or modified components match spec and design tokens | |

**Homelab URL:** http://192.168.77.127:3000

**GO:** All checks pass. Proceed to Gate 3.

**NO-GO:** Fix issues, redeploy if needed, re-run Gate 2.

---

## Gate 3: Production Readiness (Before Merge)

**When:** After Gate 2 passes. Before merging to `main` or into a larger feature branch.

**Purpose:** Confirm the branch is safe to merge and deploy to production.

| Check | Action | Pass |
|-------|--------|------|
| Gate 1 passed | Pre-commit checks completed | |
| Gate 2 passed | Homelab QA completed | |
| CI status | `gh run list --limit 3` — latest run green | |
| No known blockers | No unresolved critical bugs | |
| Migration state (if DB changed) | Migrations applied per `.cursor/rules/database-migrations.mdc` | |
| Merge target clear | Merge to `main` or to feature branch `X` | |

**GO:** Merge to target. Production (or parent branch) will receive the changes.

**NO-GO:** Resolve blockers before merge.

---

## Workflow Integration

```
Gate 1 (Pre-Commit)     Gate 2 (Homelab QA)      Gate 3 (Production Readiness)
       │                         │                            │
       ▼                         ▼                            ▼
  Commit + rebase  →  Push + deploy  →  Test on homelab  →  Merge to main
       │                         │                            │
   Run checks              Run checklist                 Run checklist
   before push             at 192.168.77.127               before merge
```

| Step | Gate |
|------|------|
| Before push to branch | Gate 1 |
| After deploy, before merge | Gate 2 |
| Before merge to main (or parent branch) | Gate 3 |

---

## Decision Points: Ask or Suggest

At key moments, agents should **ask the user** or **suggest** the best option. Do not assume — clarify when it affects workflow.

### Before merging to main

| Situation | Agent action |
|-----------|--------------|
| More commits planned today | **Ask:** "Will there be more commits today? If so, we can stage this branch and wait to merge everything together for a single production deploy." |
| Multiple feature branches ready | **Suggest:** "You have `feature/A` and `feature/B` both passing QA. Prefer merging both into a parent branch first, then merge that to main? Or merge each to main separately?" |
| Unclear merge target | **Ask:** "Merge to `main` now, or into a larger feature branch (e.g. `feature/reports-suite`) for a combined release later?" |
| Urgent vs. batched deploy | **Ask:** "Merge now for immediate production, or batch with other changes for a single deploy?" |

### Before pushing / deploying

| Situation | Agent action |
|-----------|--------------|
| Unstaged changes | **Ask:** "There are unstaged changes. Include them in this commit, or leave for a later commit?" |
| Scope unclear | **Suggest:** "This touches X and Y. Consider splitting into two branches for clearer review, or keep as one if they're tightly coupled." |

### Guiding principle

When in doubt, **ask**. The user prefers a clean, structured workflow and relies on agents to coach them. Suggest the professional best practice and explain why, then let the user decide.

---

## Agent Mentoring & Coaching

The user is learning the code-building pipeline. Agents should:

1. **Explain the "why"** — Briefly state why a step matters (e.g. "Rebasing ensures homelab tests against current production").
2. **Suggest best practices** — Propose the cleanest option and offer alternatives when relevant.
3. **Ask before assuming** — At decision points (merge now vs. wait, batch vs. single), ask or suggest rather than auto-proceeding.
4. **Keep workflow visible** — Summarize where we are in the pipeline (e.g. "Gate 2 complete; next: Gate 3 and merge decision").
5. **Coach, don't lecture** — Short, actionable guidance. Point to docs for detail.

---

## Merge Targets

- **Direct to main:** Use Gate 3 after Gate 2. Merge when all three gates pass.
- **Into larger feature set:** Same. Gate 3 confirms readiness to merge into the parent feature branch; that branch will later go through the same flow before merging to main.
