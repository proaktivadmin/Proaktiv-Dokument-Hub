# Syncing Changes Between Branches

This guide explains how to keep the migration branch up-to-date with your active development on V2-development.

---

## Branch Overview

| Branch | Purpose | Deployment |
|--------|---------|------------|
| `V2-development` | Active development, new features | Azure Container Apps |
| `migration/vercel-railway` | Migration to simpler stack | Vercel + Railway (future) |
| `main` | Stable production releases | - |

---

## How to Sync Changes from V2-development to Migration Branch

When you have new features or fixes on `V2-development` that you want to bring to the migration branch:

### Step 1: Switch to Migration Branch
```bash
git checkout migration/vercel-railway
```

### Step 2: Merge Latest from V2-development
```bash
git merge V2-development
```

### Step 3: Resolve Any Conflicts
If there are conflicts (files changed in both branches), Git will tell you. Open the conflicting files and choose which changes to keep.

### Step 4: Commit and Push
```bash
git add .
git commit -m "chore: sync with V2-development"
git push origin migration/vercel-railway
```

---

## When to Sync

Sync the migration branch when:
- ✅ You've finished a feature on V2-development and it's stable
- ✅ You've fixed bugs that should carry over
- ✅ Before running the migration agents
- ✅ Before deploying to Vercel + Railway

Don't sync:
- ❌ Half-finished features
- ❌ Experimental code you might revert
- ❌ Azure-specific fixes (migration removes Azure anyway)

---

## Quick Reference Commands

```bash
# See all branches
git branch -a

# Switch to V2-development (daily work)
git checkout V2-development

# Switch to migration branch
git checkout migration/vercel-railway

# Sync migration with latest V2 changes
git checkout migration/vercel-railway
git merge V2-development
git push origin migration/vercel-railway

# Check current branch
git branch --show-current
```

---

## Visual Workflow

```
V2-development:     A───B───C───D───E───F  (your daily work)
                         \       \
                          \       \
migration/vercel-railway:  M───────X───────Y  (sync points)
                           │       │       │
                           │       │       └─ git merge V2-development
                           │       └─ git merge V2-development
                           └─ initial migration setup
```

---

## Starting the Migration

When you're ready to complete the migration to Vercel + Railway:

1. Sync latest changes: `git checkout migration/vercel-railway && git merge V2-development`
2. Run agents in order:
   - `/migration-architect`
   - `/migration-backend`
   - `/migration-frontend`
   - `/migration-deploy`
   - `/migration-qa`
3. After QA approval, the migration branch becomes your new production

---

## Need Help?

If you get stuck:
- **Merge conflicts:** Open the file, look for `<<<<<<<` markers, choose the right code
- **Wrong branch:** `git checkout <branch-name>` to switch
- **Undo a merge:** `git merge --abort` (before committing)
- **See what changed:** `git diff V2-development migration/vercel-railway`
