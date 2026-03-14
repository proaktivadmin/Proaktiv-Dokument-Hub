---
description: Direct commit to main. Use only for hotfixes, typos, or urgent config changes.
---

# Commit to Production

Commit directly to `main` and push. Bypasses homelab QA. Use only when the change is trivial or urgent.

## When to Use

- Hotfix (critical bug in production)
- Typo, copy fix, config tweak
- User explicitly requests "commit to production" or "direct to main"

## When NOT to Use

- New features, UI changes, refactors → use `/commit-to-homelab` instead
- Anything that could break production → use homelab QA first

## Execute

1. **Ensure on main:** `git checkout main && git pull origin main`
2. **Commit:** Stage only relevant paths. Use `scripts/tools/commit_intent.ps1` or `git add` + `git commit`.
3. **Push:** `git push origin main`
4. **Report:** Committed and pushed. Vercel + Railway will auto-deploy.

## Rules

- Only for low-risk changes.
- When in doubt, use `/commit-to-homelab` instead.
