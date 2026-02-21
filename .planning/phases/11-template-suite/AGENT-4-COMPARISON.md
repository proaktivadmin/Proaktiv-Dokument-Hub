# TASK: Comparison Agent — AI-Powered Vitec Template Change Analysis

## Role & Objective

You are the Comparison Agent. You build a feature that lets the project owner understand what changed when Vitec updates a system template, without reading HTML source code.

The workflow: the user pastes updated Vitec source code into the dashboard, the system compares it against the stored copy, and an AI agent returns a plain-language analysis — what changed, what it means practically, whether custom edits conflict, and a clear recommendation (adopt, ignore, partially merge). The user makes the final call.

This is **not a diff tool**. It is an AI-powered change analysis that produces human-readable summaries from structural HTML comparison.

---

## Prerequisites

**Hard gate:** The following must exist before you begin:

- `.planning/vitec-html-ruleset.md` — Agent 1's approved ruleset
- `backend/app/services/template_workflow_service.py` — Agent 3's workflow service (confirms Agent 3 completed)
- The `vitec_source_hash` column must exist on the `templates` table (Agent 3's migration)

If any is missing, STOP and report which prerequisite is not met.

---

## Read First

Before doing anything else, read these files in order:

1. `CLAUDE.md` — Project overview, architecture, conventions
2. `.planning/vitec-html-ruleset.md` — The ruleset. You need Section 2 (CKEditor compatibility), Section 10 (Property Type Patterns), Section 11 (Known Failure Modes), and Section 14 (No-Touch Templates)
3. `.planning/phases/11-template-suite/PLAN.md` — Phase overview
4. `backend/app/models/template.py` — Template model (especially `vitec_source_hash`, `origin`, `content`)
5. `backend/app/services/sanitizer_service.py` — Understand HTML normalization rules
6. `backend/app/services/template_analyzer_service.py` — Understand merge field extraction and template analysis
7. `frontend/src/components/editor/CKEditorSandbox.tsx` — The editor component (Agent 3 built this)
8. `frontend/src/app/templates/[id]/edit/page.tsx` — The editor page (you may add a comparison tab here)
9. `.planning/codebase/DESIGN-SYSTEM.md` — Design tokens for UI

## Database Access

A `user-postgres` MCP tool is available for read-only access to the production database. Use `CallMcpTool` with server `user-postgres` and tool `query` to run SQL queries.

---

## Deliverables

### 1. Structural Diff Service

**File:** `backend/app/services/template_comparison_service.py` (new)

A service that performs structural HTML comparison using BeautifulSoup. This is the foundation layer — it identifies **what** changed at the DOM level before AI interprets **why**.

```python
class TemplateComparisonService:
    async def compare(
        self,
        stored_html: str,
        updated_html: str,
        template_id: UUID | None = None,
    ) -> ComparisonResult:
        """Compare stored template against updated Vitec source."""

    def _structural_diff(self, stored_soup: BeautifulSoup, updated_soup: BeautifulSoup) -> list[StructuralChange]:
        """Identify structural changes between two parsed HTML trees."""

    def _classify_changes(self, changes: list[StructuralChange]) -> ChangeClassification:
        """Categorize changes as cosmetic, structural, or breaking."""

    def _detect_conflicts(self, stored_html: str, original_hash: str | None, changes: list[StructuralChange]) -> list[Conflict]:
        """Identify where Vitec's changes overlap with our customizations."""

    def _compute_hash(self, html: str) -> str:
        """SHA256 hash for content comparison."""
```

**Change classification categories:**

| Category | Description | Example |
|----------|-------------|---------|
| `cosmetic` | Whitespace, attribute order, style reformat | Vitec reindented a table |
| `structural` | Elements added/removed/moved, tag changes | New `vitec-if` condition added |
| `content` | Text content changed | Legal text updated |
| `merge_fields` | Merge field syntax changed | `[[seller.name]]` → `[[selger.fulltNavn]]` |
| `logic` | `vitec-if`/`vitec-foreach` logic changed | New property type branch added |
| `breaking` | Changes that would break our customizations | Section we customized was restructured |

**Conflict detection:**

A "conflict" exists when a Vitec change touches a section that differs between the original Vitec source (tracked via `vitec_source_hash`) and our stored copy. This means we customized something that Vitec also changed.

To detect this, the service needs three versions:
1. **Original Vitec source** — The HTML we started with (stored hash, or reconstructable from version history)
2. **Our current copy** — The stored template content (possibly customized)
3. **Updated Vitec source** — The pasted new source

If `vitec_source_hash` is available, compare updated source against the original hash to see what Vitec changed. Then compare our current copy against the original hash to see what we changed. Overlapping sections = conflicts.

### 2. AI Analysis Service

**File:** `backend/app/services/template_analysis_ai_service.py` (new)

Takes the structural diff output and produces a plain-language analysis using an LLM.

```python
class TemplateAnalysisAIService:
    async def analyze(
        self,
        comparison: ComparisonResult,
        template_title: str,
        template_category: str | None = None,
    ) -> AnalysisReport:
        """Generate human-readable analysis from structural comparison."""

    async def _build_prompt(self, comparison: ComparisonResult, template_title: str) -> str:
        """Build the LLM prompt with structured change data."""
```

**Analysis report structure:**

The AI must produce:

1. **Summary** — 2-3 sentences describing the update at a high level
2. **What Vitec changed** — Bulleted list of changes in plain Norwegian, grouped by category
3. **Impact on our version** — What these changes mean for our customized copy
4. **Conflicts** — Specific sections where our edits and Vitec's changes overlap, with explanation
5. **Recommendation** — One of: `ADOPT` (take their version), `IGNORE` (keep ours), `PARTIAL_MERGE` (take some changes), `REVIEW_REQUIRED` (too complex for automated recommendation)
6. **Suggested actions** — If PARTIAL_MERGE, list which specific changes to adopt and which to keep

**LLM configuration:**

- Support multiple providers: Google Gemini (preferred), OpenAI, or Anthropic
- Add the relevant API key to environment variables (document in CLAUDE.md)
- Temperature: 0.2 (factual, deterministic)
- System prompt should include context about Vitec templates, merge fields, and Norwegian real estate conventions
- The prompt must include the structural diff data, not raw HTML (keep token usage manageable)
- **Fallback:** If no API key is configured, return the structural diff results only (no AI summary) with a message indicating AI analysis is unavailable

### 3. Comparison Schemas

**File:** `backend/app/schemas/template_comparison.py` (new)

```python
class StructuralChange(BaseModel):
    category: Literal["cosmetic", "structural", "content", "merge_fields", "logic", "breaking"]
    element_path: str  # CSS-like path to the changed element
    description: str
    before: str | None
    after: str | None

class Conflict(BaseModel):
    section: str  # Human-readable section description
    our_change: str  # What we modified
    vitec_change: str  # What Vitec modified
    severity: Literal["low", "medium", "high"]

class ChangeClassification(BaseModel):
    cosmetic: int
    structural: int
    content: int
    merge_fields: int
    logic: int
    breaking: int
    total: int

class ComparisonResult(BaseModel):
    changes: list[StructuralChange]
    classification: ChangeClassification
    conflicts: list[Conflict]
    stored_hash: str
    updated_hash: str
    hashes_match: bool  # Quick check: are they identical?

class AnalysisReport(BaseModel):
    summary: str
    changes_by_category: dict[str, list[str]]
    impact: str
    conflicts: list[Conflict]
    recommendation: Literal["ADOPT", "IGNORE", "PARTIAL_MERGE", "REVIEW_REQUIRED"]
    suggested_actions: list[str]
    ai_powered: bool  # False if LLM was unavailable
    raw_comparison: ComparisonResult

class CompareRequest(BaseModel):
    updated_html: str  # The pasted Vitec source
```

### 4. Comparison Endpoints

**File:** `backend/app/routers/templates.py` (modify)

Add these endpoints:

```
POST /api/templates/{template_id}/compare
    Body: CompareRequest (the pasted updated Vitec source)
    Response: AnalysisReport
    Compares the stored template against the pasted source.

POST /api/templates/{template_id}/compare/apply
    Body: { action: "adopt" | "ignore" | "partial", sections_to_adopt?: string[] }
    Response: TemplateContentResponse
    Applies the comparison decision:
    - "adopt": Replace content with updated Vitec source, update vitec_source_hash
    - "ignore": Keep current content, update vitec_source_hash to mark as reviewed
    - "partial": Future — for now, return 501 Not Implemented

POST /api/templates/compare-standalone
    Body: { stored_html: str, updated_html: str, template_title: str }
    Response: AnalysisReport
    Compare two arbitrary HTML strings without a stored template. Useful for ad-hoc analysis.
```

### 5. Comparison UI Component

**File:** `frontend/src/components/editor/TemplateComparison.tsx` (new)

A component that provides the comparison workflow:

**UI layout:**

```
┌─────────────────────────────────────────────────────────────┐
│  Sammenlign med Vitec-oppdatering                       [X] │
│                                                             │
│  ┌─ Lim inn oppdatert Vitec-kode ──────────────────────┐   │
│  │                                                       │   │
│  │   [Textarea — paste updated Vitec source here]        │   │
│  │                                                       │   │
│  └───────────────────────────────────────────────────────┘   │
│                                                             │
│  [ Sammenlign ]                                             │
│                                                             │
│  ┌─ Analyse ────────────────────────────────────────────┐   │
│  │                                                       │   │
│  │  Vitec har oppdatert "Kjøpekontrakt Bruktbolig"       │   │
│  │  med 3 strukturelle og 1 innholdsendring.             │   │
│  │                                                       │   │
│  │  ## Hva Vitec endret                                   │   │
│  │  - Oppdatert juridisk tekst i §3 (innhold)            │   │
│  │  - Ny vitec-if for borettslagsboliger (logikk)        │   │
│  │  - Endret marger i tabellceller (kosmetisk)           │   │
│  │                                                       │   │
│  │  ## Påvirkning på vår versjon                         │   │
│  │  Vi har tilpasset §3 med egne formuleringer. Vitecs   │   │
│  │  endring i dette avsnittet vil overskrive disse.       │   │
│  │                                                       │   │
│  │  ## Konflikter (1)                                     │   │
│  │  ⚠ §3 Overtakelse — vi har endret, Vitec har endret  │   │
│  │                                                       │   │
│  │  ## Anbefaling: DELVIS OVERTAGELSE                    │   │
│  │  Ta den nye borettslags-betingelsen og margjusteringer.│   │
│  │  Behold vår tilpassede §3-tekst.                      │   │
│  │                                                       │   │
│  └───────────────────────────────────────────────────────┘   │
│                                                             │
│  ┌─ Endringsoversikt ───────────────────────────────────┐   │
│  │  Kosmetisk: 2  │  Strukturell: 1  │  Innhold: 1      │   │
│  │  Flettekoder: 0  │  Logikk: 1  │  Kritisk: 0        │   │
│  └───────────────────────────────────────────────────────┘   │
│                                                             │
│  [ Behold vår versjon ]    [ Overta Vitec-versjon ]         │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Component props:**

```typescript
interface TemplateComparisonProps {
  templateId: string;
  currentContent: string;
  templateTitle: string;
  onAdopt: (newContent: string) => void;  // Content was replaced
  onDismiss: () => void;  // User chose to keep current version
}
```

### 6. Integration with Editor Page

**File:** `frontend/src/app/templates/[id]/edit/page.tsx` (modify)

Add a "Sammenlign" button in the editor toolbar and/or as a new tab in the right panel. When clicked, it opens the `TemplateComparison` component.

Only show this button for templates where `origin === 'vitec_system'` — custom templates have no Vitec source to compare against.

### 7. API Client Updates

**File:** `frontend/src/lib/api.ts` (modify)

Add to `templateApi`:

```typescript
compareWithVitec: async (templateId: string, updatedHtml: string): Promise<AnalysisReport>
applyComparison: async (templateId: string, action: 'adopt' | 'ignore'): Promise<ContentResponse>
compareStandalone: async (storedHtml: string, updatedHtml: string, title: string): Promise<AnalysisReport>
```

Add TypeScript interfaces for `AnalysisReport`, `ComparisonResult`, `StructuralChange`, `Conflict`, `ChangeClassification`, `CompareRequest`.

---

## Scope Boundaries

**In scope:**
- Structural HTML diff service
- AI analysis service with LLM integration
- Comparison endpoints
- Comparison UI component
- Integration with the editor page
- API client methods

**Out of scope (do NOT do these):**
- Partial merge UI (complex — return 501 for now, build in a future phase)
- Automatic Vitec template sync (no API available)
- Template deduplication (Agent 5)
- Flettekode editor integration (Agent 6)
- Chrome MCP scraping of Vitec templates
- Modifying the CKEditor sandbox (Agent 3 built it, don't change it)

---

## Section 14 Awareness — No-Touch Templates

The ruleset's Section 14 lists government registration forms that must NEVER be modified. If a user attempts to compare a No-Touch template, the comparison should still work (showing what Vitec changed), but the recommendation must always be `ADOPT` — we never customize these templates, so we always take Vitec's version.

Identify No-Touch templates by checking if the template title matches patterns from Section 14 (e.g., "Skjøte", "Pantedokument", "Grunnboksutskrift", "Konsesjonserklæring", "Seksjoneringsbegjæring").

---

## LLM Provider Configuration

The AI analysis feature requires an LLM API key. Design the service to be provider-agnostic:

- Support a `COMPARISON_LLM_PROVIDER` env var (`google`, `openai`, `anthropic`, or `none`)
- Default provider priority: if `GOOGLE_API_KEY` is set, use Google Gemini; else if `OPENAI_API_KEY` is set, use OpenAI; else if `ANTHROPIC_API_KEY` is set, use Anthropic; else fallback to structural diff only
- **Google Gemini:** Use `google-generativeai` package with `gemini-2.0-flash` model. Add `google-generativeai` to `backend/requirements.txt`.
- **OpenAI:** Use `openai` package with `gpt-4o` model
- **Anthropic:** Use `anthropic` package with `claude-sonnet-4-20250514` model
- If no key is configured, the structural diff still works — only the AI summary is disabled
- The prompt should be in Norwegian for a Norwegian-language output
- Token usage should be logged for cost awareness

---

## Testing

- Compare a real Vitec template against a slightly modified copy (change one paragraph, add a `vitec-if`, reorder an attribute) — verify structural diff catches all three
- Compare identical templates — verify `hashes_match: true` and zero changes
- Compare a No-Touch template — verify recommendation is always `ADOPT`
- Test with AI unavailable (no API key) — verify graceful fallback
- Test the `apply` endpoint with `action: "adopt"` — verify content is replaced and hash is updated
- Run backend linting (`ruff check`) and frontend linting (`npm run lint`)

---

## Rules

- Follow existing code patterns in the codebase (read CLAUDE.md)
- All backend services must be async
- Use Pydantic for all API schemas
- No `any` in TypeScript
- Use design system tokens for all UI work (read `.planning/codebase/DESIGN-SYSTEM.md`)
- Do NOT commit or push — just make the changes
- If anything is unclear, ASK before proceeding

---

## Handoff Summary

When complete, produce a handoff summary in this exact format:

---
**AGENT 4 COMPLETE**

**Files created:**
- [ ] `backend/app/services/template_comparison_service.py`
- [ ] `backend/app/services/template_analysis_ai_service.py`
- [ ] `backend/app/schemas/template_comparison.py`
- [ ] `frontend/src/components/editor/TemplateComparison.tsx`

**Files modified:**
- [ ] `backend/app/routers/templates.py` (added comparison endpoints)
- [ ] `frontend/src/lib/api.ts` (added comparison API methods)
- [ ] `frontend/src/app/templates/[id]/edit/page.tsx` (added Sammenlign button/tab)

**LLM provider configured:** OpenAI / Anthropic / None (fallback only)

**Test results:**
- Structural diff with modified template: Pass/Fail
- Identical template comparison: Pass/Fail
- No-Touch template recommendation: Pass/Fail
- AI-unavailable fallback: Pass/Fail
- Apply adopt action: Pass/Fail
- Linting: Pass/Fail

**Environment variables required:**
- `GOOGLE_API_KEY`, `OPENAI_API_KEY`, or `ANTHROPIC_API_KEY` (optional — structural diff works without)
- `COMPARISON_LLM_PROVIDER` (optional, auto-detected from available keys, priority: google > openai > anthropic)

**Issues encountered:** (list any or "None")

**Ready for Agent 5:** Yes/No
---
