# Cursor Bugbot Setup

Bugbot reviews pull requests and flags bugs, security issues, and code quality problems. See [cursor.com/docs/bugbot](https://cursor.com/docs/bugbot).

## Project configuration (done)

Project-specific rules are in `.cursor/BUGBOT.md` files:

- `.cursor/BUGBOT.md` — Project-wide (always included)
- `backend/.cursor/BUGBOT.md` — Included when reviewing backend files
- `frontend/.cursor/BUGBOT.md` — Included when reviewing frontend files

Bugbot reads these automatically when reviewing PRs.

## Dashboard setup (you must do)

### 1. Connect GitHub

1. Go to [cursor.com/dashboard](https://cursor.com/dashboard?tab=integrations)
2. Open the **Integrations** tab
3. Click **Connect GitHub** (or **Manage Connections** if already connected)
4. Complete the GitHub installation flow

### 2. Enable Bugbot on this repo

1. In the dashboard, go to the **Bugbot** tab or your installations list
2. Enable Bugbot for `proaktivadmin/Proaktiv-Dokument-Hub` (or your repo)

### 3. Optional: Personal settings

- **Run only when mentioned** — Comment `cursor review` or `bugbot run` on a PR to trigger a review
- **Run only once per PR** — Skip reviews on subsequent commits
- **Enable reviews on draft PRs** — Include draft PRs in automatic reviews (Teams)

## Manual trigger

Comment on any PR:

```
cursor review
```

or

```
bugbot run
```

For verbose output:

```
cursor review verbose=true
```

## Autofix

Bugbot can spawn a Cloud Agent to fix issues. Configure in the [Bugbot dashboard](https://cursor.com/dashboard?tab=bugbot):

- **Off** — Use manual "Fix in Cursor" or "Fix in Web" links
- **Create New Branch** (recommended) — Push fixes to a new branch
- **Commit to Existing Branch** — Push fixes to the PR branch (max 3 attempts)

## Workflow integration

With the homelab QA workflow:

1. Open a PR from your feature branch
2. Bugbot runs automatically (or when you comment `cursor review`)
3. Address any bugs before Gate 3 (production readiness)
4. Merge when all gates pass
