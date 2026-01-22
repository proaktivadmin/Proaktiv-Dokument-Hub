# The Proaktiv Ultimate Workflow

This workflow combines the best elements of **Ralph** (Hierarchy), **GSD** (Context-First), and **Agentic Skills** into a unified process for this project.

## 1. Core Philosophy: "Context is King" (from GSD)
**Rule #1:** No code is written until context is understood.
The AI must always know *where* it is in the grand scheme before taking a step. This prevents "context drift" over long sessions.

## 2. The Hierarchy (from Ralph)
We structure work in three distinct layers to manage complexity:

### Level 1: STRATEGY (The "What")
*   **Files:** `.planning/PROJECT.md`, `.planning/ROADMAP.md`, `.planning/REQUIREMENTS.md`
*   **Purpose:** Defines the *Goal*, *Requirements*, and *Architecture*.
*   **Updates:** Only when requirements change or phases are completed.

### Level 2: STATE (The "Now")
*   **File:** `.planning/STATE.md` (project-level), `.cursor/active_context.md` (session-level)
*   **Purpose:** The single source of truth for the *Current Position*.
*   **Contents:**
    *   **Current Phase:** Which roadmap phase are we in?
    *   **Progress:** What percentage complete?
    *   **Recent Changes:** What did we just complete?
*   **Usage:** Read at start of session, update after major completions.

### Level 3: EXECUTION (The "How")
*   **Files:** Source code, Tests, `.planning/phases/*/PLAN.md` files.
*   **Purpose:** The actual implementation.

## 2.1 CI/CD Integration
Before any code changes:
1. Check CI status: `gh run list --limit 3`
2. After changes, verify CI passes
3. All pushes to `main` trigger GitHub Actions

## 3. Agent Personas (from Prompt Engineering)
We use specialized modes (switched via `/commands` or Agentic Mode):
*   **Architect**: Reads Level 1, updates Level 2. (Planning)
*   **Builder**: Reads Level 2, executes Level 3. (Coding)
*   **Debugger**: Reads Level 3, updates Level 2. (Fixing)

## 4. The Workflow Loop

1.  **START SESSION**:
    *   Read `.cursor/active_context.md`.
    *   *Self-Correction:* If stale, read `plans/` and update `active_context.md`.

2.  **PICK TASK**:
    *   Select next item from `active_context.md` checklist.
    *   Break it down into atomic steps if too large (create a mini-checklist).

3.  **EXECUTE**:
    *   Write Code / Run Terminal.
    *   *Checkpoint:* If a step succeeds, mark it `[x]` in `active_context.md`.

4.  **VERIFY**:
    *   Run tests/verification steps.
    *   Update `active_context.md` with results ("Known Issues").

5.  **HANDOFF**:
    *   Summary of what was done.
    *   Clear "Next Steps" for the next agent session.

## 5. Skills & Tools (from Awesome Skills)
When encountering specific domains, look for specialized prompts in `.cursor/skills/` (to be created as needed).
*   Example: `skills/pdf_parsing.md`, `skills/vitec_api.md`.
