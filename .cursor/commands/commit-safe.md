# Commit Safe

Create intentional commits by staging only explicit paths.

## Usage

```powershell
pwsh -File scripts/tools/commit_intent.ps1 `
  -Message "feat: short why-focused message" `
  -Paths "backend/app/services/foo.py","frontend/src/lib/bar.ts"
```

## Dry Run

```powershell
pwsh -File scripts/tools/commit_intent.ps1 `
  -Message "chore: verify stage list" `
  -Paths "path/one","path/two" `
  -DryRun
```

## Rules

- Never use `git add -A` for targeted changes.
- Stage only files relevant to the current scope.
- Verify `git status --short` before final commit.
