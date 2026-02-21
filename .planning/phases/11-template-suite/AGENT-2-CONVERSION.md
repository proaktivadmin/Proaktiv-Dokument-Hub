# TASK: Conversion Agent — Build Word-to-HTML Pipeline

## Role & Objective

You are the Conversion Agent. You build a pipeline that accepts a Word document (.docx) and returns a CKEditor 4-compliant, Vitec Next-ready HTML template — clean and usable without manual intervention. This pipeline will be used heavily during the initial library reset (importing templates that currently exist as Word documents) and less frequently over time.

Your sole source of truth for what constitutes valid output is the ruleset produced by Agent 1: `.planning/vitec-html-ruleset.md`. Do NOT begin work until you have confirmed this file exists and has been reviewed.

---

## Prerequisites

**Hard gate:** `.planning/vitec-html-ruleset.md` must exist and be approved. If it does not exist, STOP and report that Agent 1 has not completed its work.

---

## Read First

Before doing anything else, read these files in order:

1. `CLAUDE.md` — Project overview, architecture, conventions
2. `.planning/vitec-html-ruleset.md` — **The ruleset. Read every section.** Pay special attention to Section 12 (Conversion Checklist) — this is your validation reference.
3. `.planning/phases/11-template-suite/PLAN.md` — Phase overview and your position in the pipeline
4. `backend/app/services/sanitizer_service.py` — Existing sanitizer. Your pipeline must produce output that passes `SanitizerService.validate_structure()` without errors.
5. `backend/app/services/template_content_service.py` — Content saving service. Understand how templates are stored (content hash, versioning, merge field extraction).
6. `backend/app/routers/templates.py` — Existing template endpoints. Understand the upload/create flow.
7. `backend/app/schemas/template_settings.py` — Existing Pydantic schemas for templates.
8. `docs/vitec-stilark.md` — The Vitec Stilark CSS. Your output must be compatible.
9. `.planning/codebase/DESIGN-SYSTEM.md` — Frontend design tokens for any UI components.

## Database Access

A `user-postgres` MCP tool is available for read-only access to the production database. Use `CallMcpTool` with server `user-postgres` and tool `query` to run SQL queries. This is useful for inspecting existing Vitec templates to compare against your conversion output.

Example — fetch a real Vitec template for comparison:

```sql
SELECT title, content FROM templates tmpl
JOIN template_tags tt ON tmpl.id = tt.template_id
JOIN tags t ON tt.tag_id = t.id
WHERE t.name = 'Vitec Next'
ORDER BY LENGTH(content) DESC LIMIT 1
```

---

## Deliverables

### 1. Add `mammoth` dependency

**File:** `backend/requirements.txt` (modify)

Add `mammoth` (latest version) to the requirements. mammoth converts .docx to clean semantic HTML with configurable style mapping. It is the right tool for this job because it produces structured HTML (headings, lists, tables) rather than the visual mess that libreoffice or pandoc produce.

Verify the package exists and note the version you add.

### 2. Create Word Conversion Service

**File:** `backend/app/services/word_conversion_service.py` (new)

The service must:

- Accept raw .docx bytes as input
- Run mammoth conversion with a custom style map that aligns Word styles with Vitec Stilark conventions
- Post-process the mammoth output using BeautifulSoup to enforce the ruleset from `.planning/vitec-html-ruleset.md`
- Run the result through `SanitizerService.sanitize()` for Vitec Stilark compliance
- Extract merge fields from the converted HTML using `TemplateAnalyzerService.extract_merge_fields()`
- Return a structured result with the cleaned HTML, a list of warnings, validation results, and detected merge fields

**Key methods:**

```python
class WordConversionService:
    async def convert(self, docx_bytes: bytes, filename: str = "upload.docx") -> ConversionResult:
        """Convert a .docx file to Vitec-ready HTML."""
        ...

    def _build_style_map(self) -> str:
        """Build mammoth style map aligned with Vitec Stilark."""
        ...

    def _post_process(self, html: str) -> tuple[str, list[str]]:
        """Apply ruleset-based cleanup. Returns (html, warnings)."""
        ...

    def _validate_against_checklist(self, html: str) -> list[ValidationItem]:
        """Run Section 12 conversion checklist. Returns pass/fail for each item."""
        ...
```

**Style map guidance:** mammoth uses a style map to control how Word styles map to HTML elements. For example:
- Word Heading 1 → `<h1>`
- Word Heading 2 → `<h2>`
- Word "Normal" → `<p>`
- Bold → `<strong>`
- Italic → `<em>`
- Word tables → `<table>` with appropriate classes

Consult the ruleset (Section 6: Table Patterns and Section 7: CSS and Styling Rules) to determine which HTML elements and classes to target.

**Post-processing must handle:**
- Wrapping output in the required `#vitecTemplate` shell (Section 1 of ruleset)
- Stripping any styles that violate the Stilark rules (Section 7)
- Ensuring tables match safe patterns (Section 6)
- Adding the Stilark resource reference
- Cleaning up mammoth artifacts (empty paragraphs, unnecessary spans, etc.)
- Preserving any `[[merge.field]]` syntax that may exist in the Word document

### 3. Create Conversion Schemas

**File:** `backend/app/schemas/word_conversion.py` (new)

```python
from pydantic import BaseModel

class ValidationItem(BaseModel):
    rule: str
    passed: bool
    detail: str | None = None

class ConversionResult(BaseModel):
    html: str
    warnings: list[str]
    validation: list[ValidationItem]
    merge_fields_detected: list[str]
    is_valid: bool  # True if all validation items passed
```

### 4. Create Conversion Endpoint

**File:** `backend/app/routers/templates.py` (modify)

Add a new endpoint:

```
POST /api/templates/convert-docx
```

- Accepts multipart file upload (`.docx` only)
- Returns `ConversionResult` with converted HTML, warnings, validation, and detected merge fields
- Does NOT automatically create a template record — the user reviews the output first
- Optional query parameter `?auto_save=true` to create a draft template from the result

**Request:** `multipart/form-data` with field `file` (the .docx file)

**Response:** `ConversionResult` JSON

**Error cases:**
- 400 if file is not .docx
- 422 if mammoth fails to parse the file
- 500 for unexpected errors (with proper logging)

### 5. Create Frontend Conversion Dialog

**File:** `frontend/src/components/templates/WordConversionDialog.tsx` (new)

A dialog component triggered from the templates page that:

- Provides a file upload dropzone accepting .docx files only
- Shows upload progress and conversion status
- Displays the converted HTML in an A4Frame preview (reuse existing `A4Frame` component)
- Shows warnings in an amber alert section
- Shows validation results as a checklist (green check / red X for each item)
- Shows detected merge fields as a list
- Provides a "Save as Draft" button that creates a template record via `POST /api/templates`
- Provides a "Download HTML" button for manual review
- Follows the design system (read `.planning/codebase/DESIGN-SYSTEM.md`)

**UI layout:**

```
┌─────────────────────────────────────────────────┐
│  Konverter Word-dokument                    [X] │
│                                                 │
│  ┌─────────────────────────────────────────┐    │
│  │                                         │    │
│  │   Dra og slipp .docx fil her            │    │
│  │   eller klikk for å velge               │    │
│  │                                         │    │
│  └─────────────────────────────────────────┘    │
│                                                 │
│  ┌─ Forhåndsvisning ──────────────────────┐    │
│  │                                         │    │
│  │   [A4Frame preview of converted HTML]   │    │
│  │                                         │    │
│  └─────────────────────────────────────────┘    │
│                                                 │
│  ┌─ Advarsler (2) ────────────────────────┐    │
│  │ ⚠ Empty paragraph removed at line 34   │    │
│  │ ⚠ Unknown style "CustomHeading" mapped  │    │
│  │   to default <p>                        │    │
│  └─────────────────────────────────────────┘    │
│                                                 │
│  ┌─ Validering ───────────────────────────┐    │
│  │ ✓ vitecTemplate wrapper present         │    │
│  │ ✓ Stilark reference present             │    │
│  │ ✓ No prohibited inline styles           │    │
│  │ ✗ Table missing border-collapse         │    │
│  └─────────────────────────────────────────┘    │
│                                                 │
│  ┌─ Flettekoder funnet (3) ───────────────┐    │
│  │ [[eiendom.adresse]]                     │    │
│  │ [[selger.navn]]                         │    │
│  │ [[meglerkontor.navn]]                   │    │
│  └─────────────────────────────────────────┘    │
│                                                 │
│  [ Last ned HTML ]          [ Lagre som utkast ] │
└─────────────────────────────────────────────────┘
```

### 6. Add Conversion Button to Templates Page

**File:** `frontend/src/app/templates/page.tsx` (modify)

Add a button in the templates page header (near the existing "New Template" button):

```tsx
<Button variant="outline" onClick={() => setShowConversionDialog(true)}>
  <FileUp className="h-4 w-4 mr-2" />
  Importer Word
</Button>
```

### 7. Add API Client Method

**File:** `frontend/src/lib/api.ts` (modify)

Add to `templateApi`:

```typescript
convertDocx: async (file: File): Promise<ConversionResult> => {
  const formData = new FormData();
  formData.append('file', file);
  const response = await api.post('/api/templates/convert-docx', formData);
  return response.data;
}
```

Add the `ConversionResult` type to `frontend/src/types/` or inline in the API file.

---

## Scope Boundaries

**In scope:**
- The conversion service, endpoint, and frontend dialog
- The mammoth dependency
- Post-processing pipeline that enforces the ruleset
- Validation against the Section 12 checklist

**Out of scope (do NOT do these):**
- CKEditor 4 sandbox integration (that is Agent 3's job)
- Schema extensions to the Template model (Agent 3)
- Publishing workflow (Agent 3)
- Library reset / bulk import (Agent 3)
- AI-powered comparison (Agent 4)
- Template deduplication (Agent 5)
- Flettekode editor integration (Agent 6)

---

## Testing

- Convert at least one sample .docx file (create a simple test document with headings, a table, bold/italic text, and a merge field placeholder like `[[eiendom.adresse]]`)
- Verify the output passes `SanitizerService.validate_structure()`
- Verify the output contains the required template shell (Section 1 of ruleset)
- Verify merge fields in the original document are preserved in the output
- Verify the validation checklist correctly reports pass/fail for each item
- Run backend linting (`ruff check`) and frontend linting (`npm run lint`) on modified files

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
**AGENT 2 COMPLETE**

**Files created:**
- [ ] `backend/app/services/word_conversion_service.py`
- [ ] `backend/app/schemas/word_conversion.py`
- [ ] `frontend/src/components/templates/WordConversionDialog.tsx`

**Files modified:**
- [ ] `backend/requirements.txt` (added mammoth)
- [ ] `backend/app/routers/templates.py` (added convert-docx endpoint)
- [ ] `frontend/src/lib/api.ts` (added convertDocx method)
- [ ] `frontend/src/app/templates/page.tsx` (added Importer Word button)

**Endpoint ready:** `POST /api/templates/convert-docx`

**Mammoth version added:** (version)

**Test results:**
- Sample .docx conversion: Pass/Fail
- SanitizerService validation: Pass/Fail
- Merge field preservation: Pass/Fail
- Linting: Pass/Fail

**Ruleset sections referenced:** (list which sections of the ruleset were used)

**Issues encountered:** (list any or "None")

**Ready for Agent 3:** Yes/No
---
