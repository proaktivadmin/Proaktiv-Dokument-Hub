# Homelab QA Workflow

**Purpose:** Test changes on homelab before merging to main. Reduces production breakage and supports larger, verified updates.

## Git Structure (Quick Reference)

```
main          ← Production. Vercel + Railway deploy from here.
  ↑
  merge
  ↑
feature/xyz   ← Your branch. Lives on GitHub, gets deployed to homelab for QA.
```

- **main** = what users see in production. Protected; only merge after QA.
- **feature branch** = your work. Push to GitHub → deploy to homelab → QA → merge to main.

## Three-Gate QA Checklist

All homelab commits use three QA gates. See **`docs/qa-checklist-three-gates.md`** for the full checklist.

| Gate | When | Purpose |
|------|------|----------|
| **Gate 1: Pre-Commit** | Before push & deploy | Lint, typecheck, tests, build — catch failures locally |
| **Gate 2: Homelab QA** | After deploy to homelab | Manual testing at http://192.168.77.127:3000 |
| **Gate 3: Production Readiness** | Before merge | CI status, no blockers — ready for main or parent branch |

---

## Full Workflow: Commit to Homelab

When the user says "commit to homelab" or uses `/commit-to-homelab`, execute this sequence:

### Step 1: Ensure you're on a feature branch

```powershell
# If currently on main, create and switch to a feature branch
git checkout -b feature/<short-description>
# Example: feature/reports-filter, feature/fix-login-redirect
```

Use a descriptive branch name. If the user provides one, use it.

### Step 2: Commit changes

Use scoped commits. Stage only relevant paths:

```powershell
pwsh -File scripts/tools/commit_intent.ps1 -Message "feat: <what changed>" -Paths "path1","path2"
# Or: git add <paths> && git commit -m "feat: <message>"
```

### Step 3: Gate 1 — Pre-Commit checks

Run before pushing. See `docs/qa-checklist-three-gates.md` for full list.

- `cd frontend && npm run lint && npx tsc --noEmit && npm run test:run && npm run build`
- `cd backend && ruff check . && pytest`
- Resolve any failures before proceeding.

### Step 4: Rebase onto latest main

Ensures homelab tests your changes on top of current production:

```powershell
git fetch origin main
git rebase origin/main
```

Resolve any conflicts. If rebase is too complex, use `git merge origin/main` instead.

### Step 5: Push branch to GitHub

```powershell
git push -u origin feature/<branch-name>
# If you rebased: git push --force-with-lease origin feature/<branch-name>
```

### Step 6: Deploy to homelab

```powershell
.\scripts\deploy-homelab.ps1 -Branch feature/<branch-name>
```

App URL after deploy: http://192.168.77.127:3000

### Step 7: Gate 2 — Homelab QA

Execute the Homelab QA checklist at http://192.168.77.127:3000. See `docs/qa-checklist-three-gates.md`.

- **Functional:** Backend health, login/logout, core pages, changed-scope flows
- **Console & DevTools:** No errors in Console; no failed/CORS requests in Network
- **Backend logs:** `docker compose logs backend` — no tracebacks
- **Visual inspection:** Use Cursor browser or manual check. Layout, typography, colors, interactive states match design system. Features work and look correct.

### Step 8: Gate 3 — Production Readiness

Before merge. See `docs/qa-checklist-three-gates.md`.

- Gates 1 and 2 passed
- CI status: `gh run list --limit 3`
- No known blockers
- Merge target clear (main or parent feature branch)

### Step 8b: Decision point — ask or suggest

Before merging, **ask or suggest** per `docs/qa-checklist-three-gates.md`:
- Will there be more commits today? Consider staging and batching.
- Multiple branches ready? Merge into parent first, or separately?
- Merge to main now, or into a larger feature set?

### Step 9: Merge to main (only if all gates pass)

```powershell
git checkout main
git merge feature/<branch-name>
git push origin main
```

Production (Vercel + Railway) will auto-deploy from main.

### Step 10: Report outcome

- **GO:** Merged to main. Production will update shortly.
- **NO-GO:** Blocking issues found. Report them and do not merge.

---

## When to Use

| Scenario | Use |
|----------|-----|
| New feature, UI change, refactor | `/commit-to-homelab` |
| Hotfix, typo, config tweak | `/commit-to-production` |
| Unsure | Prefer homelab; use production only for urgent fixes |

---

## Homelab Environment

- **Host:** Proxmox LXC 203 at 192.168.77.10
- **App:** http://192.168.77.127:3000
- **Backend:** http://192.168.77.127:8000
- **Deploy script:** `.\scripts\deploy-homelab.ps1 -Branch <branch>`

Ensure `backend/.env.docker` includes `http://192.168.77.127:3000` in `ALLOWED_ORIGINS` for CORS.
