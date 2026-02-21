# TASK: Merge Agent — Template Deduplication & Consolidation

## Role & Objective

You are the Merge Agent. You build a tool that identifies templates serving the same purpose but existing as separate copies for different property types, and consolidates them into single flexible templates using `vitec-if` logic. This reduces maintenance overhead — instead of updating 4 copies of the same contract for different property types, the user updates one template with conditional branches.

This is not a one-time cleanup task. You are building an **ongoing capability** into the suite — a deduplication dashboard that helps identify merge candidates, previews the merged result, and lets the user confirm the merge.

---

## Prerequisites

**Hard gate:** The following must exist before you begin:

- `.planning/vitec-html-ruleset.md` — Agent 1's approved ruleset (you need Section 3, 4, and 10 heavily)
- `backend/app/services/template_workflow_service.py` — Agent 3's workflow service
- The `property_types` JSONB column and `origin` column must exist on the `templates` table (Agent 3's migration)

If any is missing, STOP and report which prerequisite is not met.

---

## Read First

Before doing anything else, read these files in order:

1. `CLAUDE.md` — Project overview, conventions
2. `.planning/vitec-html-ruleset.md` — Focus on:
   - Section 3: Vitec-if Conditional Logic (syntax, escaping, nesting)
   - Section 4: Vitec-foreach Iteration
   - Section 10: Property Type Conditional Patterns (the foundation for merge logic)
   - Section 11: Known Failure Modes (avoid these in merged output)
   - Section 14: No-Touch Templates (NEVER merge government forms)
3. `.planning/phases/11-template-suite/PLAN.md` — Phase overview
4. `backend/app/models/template.py` — Template model (especially `property_types`, `origin`, `content`, `template_type`)
5. `backend/app/services/sanitizer_service.py` — HTML normalization
6. `backend/app/services/template_analyzer_service.py` — Template analysis
7. `.cursor/vitec-reference.md` — Property types, ownership types, assignment types
8. `frontend/src/app/templates/page.tsx` — Templates list page
9. `.planning/codebase/DESIGN-SYSTEM.md` — Design tokens for UI

## Database Access

A `user-postgres` MCP tool is available for read-only access to the production database. Use `CallMcpTool` with server `user-postgres` and tool `query` to run SQL queries.

Useful queries:

```sql
-- Templates grouped by base title (potential duplicates)
SELECT
    REGEXP_REPLACE(title, '\s*(Bruktbolig|Nybygg|Fritid|Tomt|Borettslag|Aksjeleilighet|Obligasjonsleilighet|Næring).*$', '', 'gi') AS base_title,
    COUNT(*) AS count,
    ARRAY_AGG(title ORDER BY title) AS variants
FROM templates
WHERE content IS NOT NULL AND content != ''
GROUP BY base_title
HAVING COUNT(*) > 1
ORDER BY count DESC;

-- Templates with property type in title
SELECT title, template_type, channel
FROM templates
WHERE title ~* '(Bruktbolig|Nybygg|Fritid|Tomt|Borettslag|Aksjeleilighet)'
AND content IS NOT NULL AND content != ''
ORDER BY title;
```

---

## Deliverables

### 1. Deduplication Analysis Service

**File:** `backend/app/services/template_dedup_service.py` (new)

The core service that identifies merge candidates, analyzes their differences, and produces a merged result.

```python
class TemplateDedupService:
    async def find_candidates(self) -> list[MergeCandidateGroup]:
        """Scan the library and identify groups of templates that serve the same purpose."""

    async def analyze_group(self, template_ids: list[UUID]) -> MergeAnalysis:
        """Deep-compare a group of templates to identify shared vs divergent content."""

    async def preview_merge(self, template_ids: list[UUID], primary_id: UUID) -> MergePreview:
        """Generate a preview of the merged template using vitec-if logic."""

    async def execute_merge(self, template_ids: list[UUID], primary_id: UUID, merged_html: str) -> MergeResult:
        """Apply the merge: update primary template, archive the rest."""
```

**Candidate identification strategy:**

1. **Title similarity** — Strip property type suffixes ("Bruktbolig", "Nybygg", "Fritid", "Tomt", "Borettslag") and group by remaining base title
2. **Content similarity** — Compare normalized HTML (strip whitespace, normalize attributes) using sequence matching. Templates with >70% structural similarity are candidates.
3. **Category + receiver matching** — Templates in the same category with the same receiver type are likely candidates
4. **Existing `vitec-if` analysis** — Templates that already contain property type conditions may already be partially merged

**Merge analysis must identify:**

- Sections that are **identical** across all variants (shared content)
- Sections that **differ by property type** (need `vitec-if` wrapping)
- Sections that are **unique to one variant** (may need property type condition or may be custom additions)
- **Merge fields** that differ between variants (e.g., different field paths for different property types)

### 2. Merge Engine

The `preview_merge` method must produce valid HTML that:

1. Uses the primary template as the base structure
2. Wraps differing sections in `vitec-if` conditions based on property type
3. Follows the exact `vitec-if` syntax from Section 3 of the ruleset
4. Uses the property type field path from Section 10 of the ruleset
5. Preserves all existing merge fields, conditions, and loops from the original templates
6. Produces HTML that passes the SanitizerService

**Example merge pattern (from ruleset Section 10):**

```html
<!-- Shared content above -->
<div vitec-if="oppdrag.oppdragstype.key == &quot;Bruktbolig&quot;">
    <!-- Content specific to Bruktbolig -->
</div>
<div vitec-if="oppdrag.oppdragstype.key == &quot;Nybygg&quot;">
    <!-- Content specific to Nybygg -->
</div>
<!-- Shared content below -->
```

**Escaping rules (from ruleset Section 3):**

- String comparisons in `vitec-if` use `&quot;` for quotes
- Norwegian characters: `æ` → `\xE6`, `ø` → `\xF8`, `å` → `\xE5`
- Operators: `==`, `!=`, `&gt;`, `&lt;`, `&gt;=`, `&lt;=`
- Boolean: `&&`, `||`

### 3. Deduplication Schemas

**File:** `backend/app/schemas/template_dedup.py` (new)

```python
class MergeCandidate(BaseModel):
    template_id: UUID
    title: str
    property_type: str | None
    content_length: int
    similarity_score: float  # 0-1, compared to group primary

class MergeCandidateGroup(BaseModel):
    base_title: str
    candidates: list[MergeCandidate]
    category: str | None
    estimated_reduction: int  # How many templates would be eliminated

class ContentSection(BaseModel):
    path: str  # CSS selector path to section
    content_hash: str
    is_shared: bool
    differs_in: list[str]  # Template IDs where this section differs
    preview: str  # First 100 chars of section content

class MergeAnalysis(BaseModel):
    group_title: str
    templates: list[MergeCandidate]
    shared_sections: list[ContentSection]
    divergent_sections: list[ContentSection]
    unique_sections: list[ContentSection]
    merge_complexity: Literal["simple", "moderate", "complex"]
    auto_mergeable: bool  # True if differences are only property-type text
    warnings: list[str]

class MergePreview(BaseModel):
    merged_html: str
    primary_template_id: UUID
    templates_to_archive: list[UUID]
    vitec_if_conditions_added: int
    warnings: list[str]
    validation_passed: bool

class MergeResult(BaseModel):
    primary_template_id: UUID
    archived_template_ids: list[UUID]
    new_version: int
    property_types_covered: list[str]
```

### 4. Deduplication Endpoints

**File:** `backend/app/routers/templates.py` (modify)

Add these endpoints:

```
GET /api/templates/dedup/candidates
    Response: list[MergeCandidateGroup]
    Returns all identified merge candidate groups.

POST /api/templates/dedup/analyze
    Body: { template_ids: list[UUID] }
    Response: MergeAnalysis
    Deep-analyzes a specific group of templates.

POST /api/templates/dedup/preview
    Body: { template_ids: list[UUID], primary_id: UUID }
    Response: MergePreview
    Generates a preview of the merged template.

POST /api/templates/dedup/execute
    Body: { template_ids: list[UUID], primary_id: UUID, merged_html: str }
    Response: MergeResult
    Applies the merge. Updates primary, archives others.
    The merged_html is provided explicitly (from preview, possibly user-edited).
```

### 5. Deduplication Dashboard Component

**File:** `frontend/src/components/editor/DeduplicationDashboard.tsx` (new)

A page-level component that shows merge candidates and guides the user through the merge process.

**UI layout:**

```
┌─────────────────────────────────────────────────────────────────┐
│  Deduplisering                                                   │
│                                                                   │
│  Funnet 5 grupper med mulige duplikater (12 maler totalt)        │
│                                                                   │
│  ┌─ Kjøpekontrakt (4 varianter) ────────────────────────────┐   │
│  │                                                           │   │
│  │  ○ Kjøpekontrakt Bruktbolig    — 87% likhet    [Primary]  │   │
│  │  ○ Kjøpekontrakt Nybygg        — 82% likhet              │   │
│  │  ○ Kjøpekontrakt Fritid        — 79% likhet              │   │
│  │  ○ Kjøpekontrakt Tomt          — 74% likhet              │   │
│  │                                                           │   │
│  │  Kompleksitet: Moderat                                     │   │
│  │  Estimert reduksjon: 3 maler                               │   │
│  │                                                           │   │
│  │  [ Analyser ]                                              │   │
│  │                                                           │   │
│  └───────────────────────────────────────────────────────────┘   │
│                                                                   │
│  ┌─ Oppdragsavtale (3 varianter) ───────────────────────────┐   │
│  │  ...                                                       │   │
│  └───────────────────────────────────────────────────────────┘   │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

**After "Analyser" is clicked:**

```
┌─────────────────────────────────────────────────────────────────┐
│  Kjøpekontrakt — Sammenslåingsanalyse                            │
│                                                        [ Tilbake ]│
│                                                                   │
│  ┌─ Delte seksjoner (12) ───────────────────────────────────┐   │
│  │  ✓ Innledning og parter                                   │   │
│  │  ✓ §1 Eiendommen                                         │   │
│  │  ✓ §2 Kjøpesum                                           │   │
│  │  ...                                                       │   │
│  └───────────────────────────────────────────────────────────┘   │
│                                                                   │
│  ┌─ Avvikende seksjoner (3) ────────────────────────────────┐   │
│  │  ⚡ §4 Overtakelse — ulik tekst per eiendomstype          │   │
│  │  ⚡ §7 Forsikring — kun Bruktbolig og Nybygg              │   │
│  │  ⚡ Vedlegg — ulikt antall vedlegg per type               │   │
│  └───────────────────────────────────────────────────────────┘   │
│                                                                   │
│  Velg primærmal: [ Kjøpekontrakt Bruktbolig ▾ ]                  │
│                                                                   │
│  [ Forhåndsvis sammenslåing ]                                     │
│                                                                   │
│  ┌─ Forhåndsvisning ────────────────────────────────────────┐   │
│  │  [A4Frame preview of merged template]                      │   │
│  │                                                           │   │
│  │  vitec-if betingelser lagt til: 5                         │   │
│  │  Advarsler: Ingen                                         │   │
│  └───────────────────────────────────────────────────────────┘   │
│                                                                   │
│  [ Avbryt ]                          [ Utfør sammenslåing ]       │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

### 6. Deduplication Page

**File:** `frontend/src/app/templates/dedup/page.tsx` (new)

A dedicated page at `/templates/dedup` that hosts the `DeduplicationDashboard`. Add a navigation link from the templates list page.

### 7. API Client Updates

**File:** `frontend/src/lib/api.ts` (modify)

Add to `templateApi`:

```typescript
dedupCandidates: async (): Promise<MergeCandidateGroup[]>
dedupAnalyze: async (templateIds: string[]): Promise<MergeAnalysis>
dedupPreview: async (templateIds: string[], primaryId: string): Promise<MergePreview>
dedupExecute: async (templateIds: string[], primaryId: string, mergedHtml: string): Promise<MergeResult>
```

Add TypeScript interfaces for all dedup types.

---

## Scope Boundaries

**In scope:**
- Deduplication analysis service with candidate identification
- Merge engine that produces valid `vitec-if` conditional templates
- Deduplication endpoints
- Deduplication dashboard UI
- API client methods
- Deduplication page

**Out of scope (do NOT do these):**
- Automatic merging without user confirmation
- AI-powered merge suggestions (structural comparison is sufficient)
- Schema changes (Agent 3 already added `property_types`)
- CKEditor sandbox modifications (Agent 3 built it)
- Flettekode integration (Agent 6)
- Merging No-Touch templates (Section 14 — government forms must never be merged)

---

## Section 14 Awareness — No-Touch Templates

Government registration forms (listed in Section 14 of the ruleset) must NEVER appear as merge candidates. Filter them out in `find_candidates()`. These include:

- Skjøte, Pantedokument, Grunnboksutskrift
- Konsesjonserklæring, Seksjoneringsbegjæring
- Any template with `origin = 'vitec_system'` AND title matching government form patterns

---

## Testing

- Run `find_candidates()` against the database and verify it identifies at least one group (if duplicate titles exist)
- Create two test templates with 80% identical content but different property type sections — verify `analyze_group()` correctly identifies shared vs divergent sections
- Generate a merge preview and verify:
  - The `vitec-if` syntax is correct per Section 3 of the ruleset
  - Property type comparisons use `&quot;` escaping
  - Norwegian characters in property type names are properly escaped
  - The merged HTML passes `SanitizerService.validate_structure()`
- Verify No-Touch templates are excluded from candidates
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
**AGENT 5 COMPLETE**

**Files created:**
- [ ] `backend/app/services/template_dedup_service.py`
- [ ] `backend/app/schemas/template_dedup.py`
- [ ] `frontend/src/components/editor/DeduplicationDashboard.tsx`
- [ ] `frontend/src/app/templates/dedup/page.tsx`

**Files modified:**
- [ ] `backend/app/routers/templates.py` (added dedup endpoints)
- [ ] `frontend/src/lib/api.ts` (added dedup API methods)
- [ ] `frontend/src/app/templates/page.tsx` (added Deduplisering navigation link)

**Merge candidate groups found:** X groups (Y templates total)

**Test results:**
- Candidate identification: Pass/Fail
- Merge analysis (shared/divergent sections): Pass/Fail
- Merge preview (vitec-if syntax correct): Pass/Fail
- Merged HTML passes SanitizerService: Pass/Fail
- No-Touch template exclusion: Pass/Fail
- Linting: Pass/Fail

**vitec-if patterns used in merged output:**
- Property type comparison: `oppdrag.oppdragstype.key == &quot;...&quot;`
- (list any others used)

**Issues encountered:** (list any or "None")

**Ready for Agent 6:** Yes/No
---
