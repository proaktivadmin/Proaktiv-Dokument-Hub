# Project Workflow Guide

**Updated:** 2026-01-22 (after structure cleanup)

## File Structure

### Source of Truth Hierarchy

```
CLAUDE.md                    # Quick reference (read-only summary)
    ↓
.planning/                   # Project planning (single source of truth)
├── STATE.md                 # Current position and progress
├── ROADMAP.md               # Phase breakdown and timeline
├── PROJECT.md               # Requirements and context
├── REQUIREMENTS.md          # Detailed requirement tracking
├── codebase/                # Technical documentation
│   ├── STACK.md             # Technology versions
│   ├── ARCHITECTURE.md      # System design
│   └── TESTING.md           # Test patterns
└── phases/                  # Active phase plans
    ├── 02-*/                # Current phases
    ├── 03-*/                # Future phases
    └── _complete/           # Archived completed phases
```

### Agent Resources

```
.cursor/
├── agents/                  # Agent prompts
│   ├── 01_SYSTEMS_ARCHITECT.md
│   ├── 02_FRONTEND_ARCHITECT.md
│   ├── 03_BUILDER.md
│   ├── DEBUGGER_AGENT.md
│   └── QA_MASTER.md
├── commands/                # Slash commands
├── specs/                   # Generated specifications
├── skills/                  # Reusable skill modules
├── vitec-reference.md       # Vitec Next API reference
└── _archive/                # Historical/obsolete files
```

### Documentation

```
docs/
├── PRD.md                   # Product requirements
├── proaktiv-directory-sync.md  # Scraper documentation
├── vitec-next-*.md          # Vitec integration docs
├── features/                # Feature specifications
└── _archive/                # Historical session logs
```

## Workflow

### 1. Start Session
Read these files in order:
1. `CLAUDE.md` - Quick context
2. `.planning/STATE.md` - Current position
3. `.planning/ROADMAP.md` - What's next

### 2. Before Coding
- Check CI status: `gh run list --limit 3`
- Read relevant phase plan in `.planning/phases/`

### 3. After Changes
- Update `.planning/STATE.md` with progress
- Run tests: `cd frontend && npm run test:run` / `cd backend && pytest`
- Commit and push to trigger CI

### 4. Phase Completion
- Move phase folder to `.planning/phases/_complete/`
- Update `.planning/ROADMAP.md` status
- Update `CLAUDE.md` Current Status section

## Quick Commands

| Command | Purpose |
|---------|---------|
| `gh run list --limit 3` | Check CI status |
| `cd frontend && npm run test:run` | Run frontend tests |
| `cd backend && pytest` | Run backend tests |
| `docker compose up -d` | Start local dev |

## Don't

- Create new context files (use existing `.planning/` structure)
- Put session notes in root (use `.planning/` or `docs/`)
- Skip updating STATE.md after major changes
