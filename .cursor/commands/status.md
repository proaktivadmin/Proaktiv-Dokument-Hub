# Project Status

Read the current project status and provide a summary.

## Read These Files
1. `.planning/STATE.md` - Current project state and position
2. `.planning/ROADMAP.md` - Phase progress and roadmap
3. `.cursor/active_context.md` - Session-level context

## Summarize
1. **Current Phase:** What phase are we in? (check ROADMAP.md)
2. **Completed:** Which phases are complete?
3. **In Progress:** What is currently being worked on?
4. **Next Steps:** What should be done next?
5. **CI Status:** Are all checks passing? (run `gh run list --limit 3`)
6. **Blockers:** Are there any known issues or blockers?

## Also Check
- Is CI passing? Check `.github/workflows/ci.yml`
- Do `.cursor/specs/backend_spec.md` and `.cursor/specs/frontend_spec.md` exist?
- Are there pending xfail tests that need fixing?

## Quick Commands
```bash
# Check CI status
gh run list --repo proaktivadmin/Proaktiv-Dokument-Hub --limit 3

# Run local tests
cd frontend && npm run test:run
cd backend && pytest
```
