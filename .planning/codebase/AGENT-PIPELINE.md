# Multi-Agent Pipeline Architecture

> Technical reference for implementing features using phased agent execution.

## Overview

The multi-agent pipeline is a methodology for breaking complex features into discrete, sequentially-executed plans. Each plan is self-contained with explicit context, scope, and success criteria, enabling independent agents to execute without full project knowledge.

## Pipeline Structure

```
.planning/phases/{phase-number}-{feature-name}/
├── HANDOVER.md           # Master prompt + execution order
├── {phase}-RESEARCH.md   # Optional: Background research
├── {phase}-01-PLAN.md    # Wave 1: Foundation
├── {phase}-02-PLAN.md    # Wave 2: Core implementation
├── {phase}-03-PLAN.md    # Wave 3: Integration
├── ...
└── {phase}-NN-PLAN.md    # Wave N: Testing/QA
```

## File Formats

### HANDOVER.md (Master Prompt)

The HANDOVER file provides context that applies to ALL plans in the phase.

```markdown
# Phase XX: Feature Name - HANDOVER

**Created:** YYYY-MM-DD
**Status:** Ready for Implementation

## MASTER PROMPT

You are implementing Phase XX: Feature Name.

**Objective:** High-level goal statement

**Data Flow:**
```
Source → Step 1 → Step 2 → Destination
```

## CONTEXT FILES (READ FIRST)

1. `CLAUDE.md` - Project conventions
2. `file.py` - Relevant existing code
3. ...

## EXECUTION ORDER

### Wave 1: Foundation
1. **XX-01-PLAN.md** - Description

### Wave 2: Implementation
2. **XX-02-PLAN.md** - Description
...

## KEY PATTERNS

### Pattern Name
Code examples and conventions to follow

## COMMANDS

### `/command-01` - Description
```
Execute .planning/phases/XX-feature/XX-01-PLAN.md
Context: Read HANDOVER.md first. Pattern from X.
Return: Execution summary with specific outputs.
```
```

### PLAN.md Files

Each PLAN file is a self-contained task specification.

```markdown
---
phase: XX-feature-name
plan: 01
type: execute | verify
wave: 1
depends_on: []
files_modified:
  - path/to/file.ext
autonomous: true
---

<objective>
Brief objective description.
</objective>

<context>
Read these files first:
- File 1 - Purpose
- File 2 - Purpose
</context>

<tasks>
<task type="auto">
  <name>Task 1: Name</name>
  <files>path/to/file.ext</files>
  <action>
    Detailed instructions with code examples.
  </action>
</task>

<task type="manual">
  <name>Task 2: Manual Step</name>
  <files>-</files>
  <action>
    Instructions for human execution.
  </action>
</task>
</tasks>

<success_criteria>
- Criterion 1
- Criterion 2
</success_criteria>
```

## Agent Command Files

Commands live in `.cursor/commands/` as `.md` files.

```markdown
# /command-name - Brief Description

## Execute

`.planning/phases/XX-feature/XX-01-PLAN.md`

## Context (Read First)

1. `HANDOVER.md` - Master context
2. `file.py` - Relevant pattern

## Objective

Clear statement of what the agent should accomplish.

## Files to Create/Modify

- `path/to/new/file.ext` - Description
- `path/to/existing/file.ext` - What to change

## Key Requirements

- Requirement 1
- Requirement 2

## Return Format

After completing, return this summary:

```
## EXECUTION SUMMARY

**Plan:** XX-01-PLAN.md
**Status:** COMPLETE | PARTIAL | BLOCKED

### Completed Tasks
- [x] Task 1: Description

### Files Created/Modified
- `path/to/file.ext` - Description

### Verification
- [ ] Criterion: PASS/FAIL

### Notes for Review
- Deviations, decisions, issues

### Next Steps
- What next agent should do
```
```

## Execution Flow

### 1. Planning Phase

1. Create phase directory in `.planning/phases/`
2. Write HANDOVER.md with master context
3. Break feature into sequential waves
4. Create PLAN.md for each wave
5. Create command files in `.cursor/commands/`

### 2. Execution Phase

For each wave:

1. **Invoke agent** with command reference: `@.cursor/commands/command-01.md`
2. **Agent reads** HANDOVER.md for context
3. **Agent executes** PLAN.md tasks
4. **Agent returns** structured execution summary
5. **Human reviews** summary for correctness
6. **Proceed to next wave** or fix issues

### 3. Completion Phase

1. Move phase to `.planning/phases/_complete/`
2. Merge command files into archive
3. Create maintenance command for future updates
4. Update project documentation (CLAUDE.md, STATE.md)

## Wave Dependencies

Waves are designed to build on each other:

| Wave | Purpose | Dependencies |
|------|---------|--------------|
| 1 | Database/Model | None |
| 2 | Backend Service | Wave 1 |
| 3 | API Endpoints | Wave 2 |
| 4 | Frontend Types | Wave 3 |
| 5 | Frontend Components | Wave 4 |
| 6 | Integration | Waves 2, 5 |
| 7 | Testing/QA | All previous |

## Best Practices

### Plan Design

- **Single responsibility**: Each plan does one thing well
- **Explicit context**: List all files agent must read
- **Code examples**: Show patterns, don't just describe
- **Success criteria**: Measurable, verifiable outcomes
- **No assumptions**: Agent knows only what's in the plan

### Agent Commands

- **Self-contained**: Include all necessary context
- **Structured output**: Define exact return format
- **Review checkpoints**: Enable human verification
- **Next steps**: Tell agent what comes after

### Error Handling

- **Partial completion**: Agent reports what succeeded
- **Blockers**: Agent identifies dependencies not met
- **Deviations**: Agent documents why plan was modified
- **Human review**: Summary enables quick verification

## Example: 6-Wave Feature Pipeline

```
Wave 1: Database Model + Migration
  └── Creates foundation data structures

Wave 2: Backend Service
  └── Business logic layer
  
Wave 3: API Endpoints
  └── REST interface to service

Wave 4: Frontend Types + API Client
  └── TypeScript types + fetch wrapper

Wave 5: Frontend Components
  └── UI implementation

Wave 6: Testing + QA
  └── Verification and documentation
```

## Maintenance Commands

After completion, create a single maintenance command that:

1. References all relevant code locations
2. Explains the feature architecture
3. Provides patterns for modifications
4. Enables future agents to safely update the feature

Example: `/notification` for sync notification system maintenance.
