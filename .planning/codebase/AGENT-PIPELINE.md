# Multi-Agent Pipeline Pattern

> Technical reference for orchestrating parallel agent workflows in Cursor.

---

## Overview

The agent pipeline pattern enables complex features to be built by multiple specialized agents working in sequence, with a human orchestrator managing handoffs and final integration.

**Key Benefits:**
- Parallel workstreams where dependencies allow
- Clear scope boundaries prevent agents from overreaching
- Structured handoffs ensure nothing is missed
- Single commit at the end maintains clean git history
- Human QA between stages catches issues early

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                      ORCHESTRATOR (Human)                        │
│  - Creates specification document                                │
│  - Designs agent pipeline with dependencies                      │
│  - Triggers agents in sequence                                   │
│  - Reviews handover summaries                                    │
│  - Runs linters and fixes issues                                 │
│  - Commits and pushes final result                               │
└─────────────────────────────────────────────────────────────────┘
         │                    │                    │
         ▼                    ▼                    ▼
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│   Agent 1   │      │   Agent 2   │      │   Agent 3   │
│  (Backend)  │ ───► │  (Backend)  │      │  (Frontend) │
│             │      │  Depends:1  │      │  Depends:1  │
└─────────────┘      └─────────────┘      └─────────────┘
                            │                    │
                            ▼                    ▼
                     ┌─────────────┐      ┌─────────────┐
                     │   Agent 4   │      │   Agent 5   │
                     │  (Frontend) │      │  (Frontend) │
                     │  Depends:3  │      │  Depends:3  │
                     └─────────────┘      └─────────────┘
```

---

## Pipeline Components

### 1. Specification Document

Create a single source of truth that all agents reference:

```
.planning/phases/{phase-name}/SPEC.md
```

**Contents:**
- Architecture diagram (ASCII)
- API endpoint definitions with request/response schemas
- Template placeholders and data sources
- Files to create (with exact paths)
- Files to modify (with specific changes)
- Environment variables needed
- External permissions required
- Agent assignment table with dependencies
- Success criteria

### 2. Agent Assignment Table

Map work to agents with explicit dependencies:

| Agent | Scope | Dependencies | Files |
|-------|-------|--------------|-------|
| 1 | Backend service + router | None | service.py, router.py |
| 2 | Backend external API | Agent 1 | graph_service.py |
| 3 | Frontend hooks + component | Agent 1, 2 | hook.ts, Component.tsx |
| 4 | Page integration | Agent 3 | page.tsx |
| 5 | Public page | Agent 1, 3 | public/page.tsx |
| 6 | Scripts/automation | Agent 1, 2 | script.ps1 |

**Parallel execution:** Agents with no dependencies (or same dependencies) can run in parallel.

### 3. Agent Command Structure

Each agent receives a structured prompt stored in `.cursor/commands/`:

```markdown
# {Feature} - Agent {N}: {Description}

You are building {feature context}. {One sentence scope}.

## READ SPEC FIRST
- .planning/phases/{phase}/SPEC.md (full technical specification)

## READ THESE FILES (mandatory)
- {file1} - {why}
- {file2} - {why}
- {file3} - {why}

## DELIVERABLES

### 1. {Deliverable Name}
File: {exact/path/to/file.ext}

{Detailed requirements with code examples if helpful}

### 2. {Deliverable Name}
...

## RULES
- {Constraint 1}
- {Constraint 2}
- DO NOT commit or push any code
- ASK for clarification if anything is unclear

## HANDOVER FORMAT
When complete, respond with:

**AGENT {N} COMPLETE**

Files created:
- {file1}
- {file2}

{Key endpoint/component/feature ready}

Issues: (list any or "None")
```

---

## Agent Prompt Best Practices

### DO

1. **Reference the spec first** - Every agent should read SPEC.md before starting
2. **List exact file paths** - No ambiguity about where files go
3. **Provide code examples** - Show expected patterns, not just describe them
4. **Explicit dependencies** - "Just created by Agent 1" makes sequencing clear
5. **Structured handover** - Consistent format makes orchestration easy
6. **No commit rule** - Agents should never commit; orchestrator handles this
7. **Ask-first rule** - Agents should ask rather than assume

### DON'T

1. **Don't give full context** - Agents don't need project history, just their scope
2. **Don't allow scope creep** - "Minimal changes only" prevents over-engineering
3. **Don't skip file reads** - Mandatory reads ensure agents understand patterns
4. **Don't use vague deliverables** - "Create a service" → "Create signature_service.py with async render_signature() method"

---

## Handover Protocol

### Agent → Orchestrator

Each agent returns a structured summary:

```
**AGENT {N} COMPLETE**

Files created:
- backend/app/services/example_service.py
- backend/app/routers/example.py

Files modified:
- backend/app/main.py

Endpoint ready: GET /api/example/{id}

Issues: None
```

### Orchestrator Actions

After each handover:

1. **Verify files exist** - Quick check that deliverables were created
2. **Run linters** - Catch issues before next agent starts
3. **Fix lint errors** - Don't let them accumulate
4. **Trigger next agent** - Only if dependencies are satisfied

---

## Parallel Execution Strategy

### Dependency Graph

```
Agent 1 ──┬──► Agent 2 ──► Agent 4
          │
          └──► Agent 3 ──► Agent 5
                      │
                      └──► Agent 6
```

**Parallel groups:**
- Group 1: Agent 1 (no deps)
- Group 2: Agent 2, Agent 3 (both depend on 1)
- Group 3: Agent 4, Agent 5, Agent 6 (depend on 2 or 3)

### Execution Timeline

```
Time    Agent 1    Agent 2    Agent 3    Agent 4    Agent 5    Agent 6
────────────────────────────────────────────────────────────────────────
T0      [START]
T1      [DONE]     [START]    [START]
T2                 [DONE]     [DONE]     [START]    [START]    [START]
T3                                       [DONE]     [DONE]     [DONE]
T4      [ORCHESTRATOR: Lint, Fix, Commit, Push]
```

---

## Post-Pipeline Checklist

After all agents complete:

- [ ] Verify all files created/modified
- [ ] Run frontend linter: `npm run lint`
- [ ] Run backend linter: `ruff check backend/`
- [ ] Fix any lint errors introduced by agents
- [ ] Test locally if possible
- [ ] Stage only relevant files (avoid unrelated changes)
- [ ] Single commit with comprehensive message
- [ ] Push to remote

---

## Commit Message Template

```
feat({scope}): {Short description}

Backend:
- {Backend change 1}
- {Backend change 2}

Frontend:
- {Frontend change 1}
- {Frontend change 2}

Scripts:
- {Script change 1}

{Phase} planning docs included.
```

---

## Example: Signature Portal Pipeline

**Feature:** Self-service email signature portal  
**Agents:** 6  
**Duration:** ~3-4 hours

| Agent | Scope | Time |
|-------|-------|------|
| 1 | SignatureService + GET endpoint | 20 min |
| 2 | GraphService + POST send endpoint | 25 min |
| 3 | useSignature hook + SignaturePreview | 30 min |
| 4 | Employee page tab integration | 10 min |
| 5 | Public /signature/[id] page | 25 min |
| 6 | PowerShell bulk sender | 20 min |
| QA | Lint fixes, testing, commit | 30 min |

**Key learnings:**
- Agents 2 and 3 can run in parallel after Agent 1
- Agents 4, 5, 6 can all run in parallel after their dependencies
- Lint fixes are usually minor (unused variables, HTML entities)
- Single commit keeps git history clean

---

## Troubleshooting

### Agent Creates Wrong Files

**Solution:** Be explicit about file paths in the prompt. Include the full path from project root.

### Agent Scope Creep

**Solution:** Add explicit constraints: "Minimal changes only - just add the tab" or "Do NOT modify other files."

### Agent Makes Bad Assumptions

**Solution:** Add "ASK for clarification if anything is unclear" and list mandatory files to read first.

### Lint Errors After Agent

**Solution:** Run linters after each agent, not just at the end. Fix immediately before context is lost.

### Agent Commits Code

**Solution:** Every prompt must include: "DO NOT commit or push any code."

---

## Template Files

Store reusable templates in:

```
.planning/templates/
├── agent-prompt-template.md
├── spec-template.md
└── handover-template.md
```

Reference these when creating new pipelines to maintain consistency.
