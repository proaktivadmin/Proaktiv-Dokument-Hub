# TASK: Storage & Editor Agent — Schema, CKEditor Sandbox, Publishing Workflow, Library Reset

## Role & Objective

You are the Storage & Editor Agent. You refactor the existing template database schema, build an in-browser template editing experience with a CKEditor 4 sandbox for live preview and pre-flight validation, implement a publishing workflow (draft → review → published), and perform the clean library reset — marking the legacy 261-file collection as archived and establishing the active Vitec Next templates as the production baseline.

This is the foundational agent for the entire editing suite. Agents 4, 5, and 6 all build on top of the schema and UI you create.

---

## Prerequisites

**Hard gate:** The following must exist before you begin:

- `.planning/vitec-html-ruleset.md` — Agent 1's approved ruleset (read in full)
- `backend/app/services/word_conversion_service.py` — Agent 2's conversion service must exist (confirms Agent 2 completed)

If either is missing, STOP and report which prerequisite is not met.

---

## Read First

Before doing anything else, read these files in order:

1. `CLAUDE.md` — Project overview, architecture, conventions, **especially the Database Migrations section**
2. `.planning/vitec-html-ruleset.md` — The ruleset. You need Section 1 (Template Shell), Section 2 (CKEditor 4 Compatibility), Section 7 (CSS/Styling), and Section 13 (Vitec Next Admin Interface)
3. `.planning/phases/11-template-suite/PLAN.md` — Phase overview and your position in the pipeline
4. `.planning/codebase/DESIGN-SYSTEM.md` — Design tokens for all UI work
5. `backend/app/models/template.py` — Current Template and TemplateVersion models
6. `backend/app/services/template_content_service.py` — How content is saved today (versioning, hashing)
7. `backend/app/services/sanitizer_service.py` — SanitizerService rules
8. `backend/app/routers/templates.py` — Existing template endpoints
9. `backend/app/schemas/template_settings.py` — Existing Pydantic schemas
10. `frontend/src/app/templates/page.tsx` — Templates list page
11. `frontend/src/app/templates/[id]/page.tsx` — Template detail/viewer page
12. `frontend/src/components/viewer/DocumentViewer.tsx` — Main viewer container
13. `frontend/src/components/templates/TemplatePreview.tsx` — Preview component with A4Frame
14. `frontend/src/lib/api.ts` — Template API methods

## Database Access

A `user-postgres` MCP tool is available for read-only access to the production database. Use `CallMcpTool` with server `user-postgres` and tool `query` to run SQL queries.

Useful queries:

```sql
-- Template status distribution
SELECT status, COUNT(*) FROM templates GROUP BY status;

-- Templates by tag
SELECT t.name AS tag, COUNT(*) FROM tags t
JOIN template_tags tt ON t.id = tt.tag_id
GROUP BY t.name ORDER BY COUNT(*) DESC;

-- Templates with content (non-empty HTML)
SELECT COUNT(*) FROM templates WHERE content IS NOT NULL AND content != '';
```

---

## Deliverables

### 1. Schema Extensions — Alembic Migration

**File:** `backend/alembic/versions/YYYYMMDD_XXXX_template_publishing.py` (new)

Extend the `templates` table with:

| Column | Type | Default | Purpose |
|--------|------|---------|---------|
| `workflow_status` | `VARCHAR(20)` | `'draft'` | Publishing workflow: `draft`, `in_review`, `published`, `archived` |
| `reviewed_at` | `TIMESTAMP` | `NULL` | When the template was last reviewed |
| `reviewed_by` | `VARCHAR(100)` | `NULL` | Who reviewed (user identifier) |
| `published_version` | `INTEGER` | `NULL` | Which version number is the current published version |
| `is_archived_legacy` | `BOOLEAN` | `FALSE` | Flag for the legacy 261-template collection |
| `origin` | `VARCHAR(30)` | `NULL` | Where this template came from: `vitec_system`, `custom`, `word_import`, `manual` |
| `vitec_source_hash` | `VARCHAR(64)` | `NULL` | SHA256 of the original Vitec system template content (for comparison feature in Agent 4) |
| `ckeditor_validated` | `BOOLEAN` | `FALSE` | Whether the content has been validated through the CKEditor sandbox |
| `ckeditor_validated_at` | `TIMESTAMP` | `NULL` | When CKEditor validation last ran |
| `property_types` | `JSONB` | `NULL` | Array of property types this template applies to (for deduplication in Agent 5) |

**Important:** The existing `status` field (draft/published/archived) conflicts with the new `workflow_status`. Handle this carefully:

- Keep `status` as-is for backward compatibility
- `workflow_status` is the new canonical field for the publishing workflow
- Add a comment explaining the distinction: `status` is the legacy field, `workflow_status` is the publishing pipeline state
- When Agent 3's UI is complete, `workflow_status` should be the field displayed and modified

**Migration rules:**
- Use `ADD COLUMN IF NOT EXISTS` for safety
- Follow the CLAUDE.md pattern: apply locally first, then manually apply to Railway
- In the migration's `upgrade()`, also run: `UPDATE templates SET workflow_status = status` to sync existing values
- Do NOT drop or rename the existing `status` column

### 2. Update Template Model

**File:** `backend/app/models/template.py` (modify)

Add the new columns to the SQLAlchemy model, matching the migration above.

### 3. Publishing Workflow Service

**File:** `backend/app/services/template_workflow_service.py` (new)

Manages the publishing lifecycle:

```python
class TemplateWorkflowService:
    async def submit_for_review(self, template_id: UUID) -> Template:
        """Move draft → in_review. Validates content is non-empty."""

    async def approve_and_publish(self, template_id: UUID, reviewer: str) -> Template:
        """Move in_review → published. Sets published_version, reviewed_at, reviewed_by."""

    async def reject_review(self, template_id: UUID, reviewer: str, reason: str) -> Template:
        """Move in_review → draft. Adds rejection reason to version notes."""

    async def unpublish(self, template_id: UUID) -> Template:
        """Move published → draft. Clears published_version."""

    async def archive(self, template_id: UUID) -> Template:
        """Move any state → archived."""

    async def get_workflow_history(self, template_id: UUID) -> list[WorkflowEvent]:
        """Return version history entries related to workflow transitions."""
```

State machine rules:
- `draft` → `in_review` (requires non-empty content)
- `in_review` → `published` (sets `published_version` to current `version`)
- `in_review` → `draft` (rejection)
- `published` → `draft` (unpublish — content remains, version increments)
- Any state → `archived`
- `archived` → `draft` (restore)

### 4. Publishing Workflow Schemas

**File:** `backend/app/schemas/template_workflow.py` (new)

```python
class WorkflowTransition(BaseModel):
    action: Literal["submit", "approve", "reject", "unpublish", "archive", "restore"]
    reviewer: str | None = None
    reason: str | None = None

class WorkflowEvent(BaseModel):
    timestamp: datetime
    from_status: str
    to_status: str
    actor: str | None
    notes: str | None

class WorkflowStatusResponse(BaseModel):
    template_id: UUID
    workflow_status: str
    published_version: int | None
    reviewed_at: datetime | None
    reviewed_by: str | None
    ckeditor_validated: bool
    ckeditor_validated_at: datetime | None
```

### 5. Publishing Workflow Endpoints

**File:** `backend/app/routers/templates.py` (modify)

Add these endpoints:

```
POST /api/templates/{template_id}/workflow
    Body: WorkflowTransition
    Response: WorkflowStatusResponse
    Handles all state transitions via the action field.

GET /api/templates/{template_id}/workflow
    Response: WorkflowStatusResponse
    Returns current workflow state.

GET /api/templates/{template_id}/workflow/history
    Response: list[WorkflowEvent]
    Returns workflow transition history.
```

### 6. CKEditor 4 Sandbox Component

**File:** `frontend/src/components/editor/CKEditorSandbox.tsx` (new)

Embed CKEditor 4 in an iframe loaded from CDN. This provides:

- A sandboxed editor that behaves identically to the one inside Vitec Next
- Pre-flight validation: load HTML into the editor, let CKEditor parse it, then extract the result — any differences reveal what CKEditor would strip or modify
- A live WYSIWYG editing surface for power users

**Architecture:**

```
┌─ Parent React Component ─────────────────────────────────────┐
│                                                               │
│  ┌─ iframe (sandbox) ──────────────────────────────────────┐ │
│  │  CKEditor 4 CDN loaded                                   │ │
│  │  CKEDITOR.replace('editor', { allowedContent: true })     │ │
│  │  postMessage API for communication                        │ │
│  └──────────────────────────────────────────────────────────┘ │
│                                                               │
│  Props:                                                       │
│  - content: string (HTML to load)                            │
│  - onChange: (html: string) => void                           │
│  - onValidation: (result: ValidationResult) => void           │
│  - readOnly?: boolean (default false)                        │
│  - mode?: 'edit' | 'validate' (default 'edit')               │
│                                                               │
│  Methods (via ref):                                           │
│  - getContent(): string                                       │
│  - setContent(html: string): void                            │
│  - validate(): ValidationResult                               │
│  - switchToSource(): void                                     │
│  - switchToWysiwyg(): void                                    │
└───────────────────────────────────────────────────────────────┘
```

**CKEditor 4 CDN:** `https://cdn.ckeditor.com/4.25.1/full-all/ckeditor.js` (pin version to match what Vitec uses — check Section 13 of ruleset for toolbar configuration)

**iframe communication:**

The parent and iframe communicate via `postMessage`:

| Direction | Message | Purpose |
|-----------|---------|---------|
| Parent → iframe | `{ type: 'setContent', html: '...' }` | Load HTML into editor |
| Parent → iframe | `{ type: 'getContent' }` | Request current HTML |
| Parent → iframe | `{ type: 'validate' }` | Run validation and return result |
| Parent → iframe | `{ type: 'setMode', mode: 'source' }` | Switch to source view |
| iframe → Parent | `{ type: 'contentChanged', html: '...' }` | Content was modified |
| iframe → Parent | `{ type: 'contentReady', html: '...' }` | Initial load complete (content after CKEditor parse) |
| iframe → Parent | `{ type: 'validationResult', result: {...} }` | Validation complete |

**CKEditor 4 config:**

Set `allowedContent: true` to enable Advanced Content Filter (ACF) in permissive mode. This prevents CKEditor from stripping custom attributes like `vitec-if`, `vitec-foreach`, `data-label`, `data-version`, `contenteditable`. This is critical and must be verified.

Additionally configure the `extraAllowedContent` with the specific attributes from Section 2 of the ruleset as a safety net.

**Validation mode:**

When `mode="validate"`:
1. Load HTML into CKEditor
2. Wait for `contentReady`
3. Compare input HTML with CKEditor's output HTML
4. Report what CKEditor changed (stripped, rewrote, or added)
5. Return a structured `ValidationResult`

```typescript
interface CKEditorValidationResult {
  isClean: boolean;  // true if CKEditor made no changes
  changes: CKEditorChange[];
  inputLength: number;
  outputLength: number;
}

interface CKEditorChange {
  type: 'stripped' | 'rewritten' | 'added';
  description: string;
  original: string;
  modified: string;
}
```

### 7. Template Editor Page

**File:** `frontend/src/app/templates/[id]/edit/page.tsx` (new)

A full editor page that combines:

- **Left panel (60%)**: CKEditorSandbox in edit mode
- **Right panel (40%)**: Tabbed panel with:
  - **Forhåndsvisning** — A4Frame preview (existing component) updated in real-time as editor content changes
  - **Validering** — Validation results from CKEditor sandbox + SanitizerService
  - **Innstillinger** — Template settings (reuse existing TemplateSettingsPanel)
  - **Historikk** — Version history with diff capability

**Header toolbar:**
- Back to template viewer
- Save button (saves content via `PUT /api/templates/{id}/content`)
- Publish workflow buttons (contextual based on `workflow_status`):
  - When draft: "Send til gjennomgang"
  - When in_review: "Godkjenn og publiser" / "Avvis"
  - When published: "Avpubliser"
- CKEditor validation button ("Valider i CKEditor")
- Toggle: WYSIWYG ↔ Source view

**URL:** `/templates/{id}/edit`

Add a navigation link from the existing template detail page (`/templates/{id}`) to the edit page.

### 8. Workflow Status UI on Template Cards & List

**File:** `frontend/src/components/templates/TemplateCard.tsx` (modify)
**File:** `frontend/src/app/templates/page.tsx` (modify)

Update the template list and cards to show `workflow_status` with appropriate styling:

| Status | Norwegian | Badge Color | Icon |
|--------|-----------|-------------|------|
| `draft` | Utkast | Muted/gray | Pencil |
| `in_review` | Til godkjenning | Amber/yellow | Eye |
| `published` | Publisert | Green | CheckCircle |
| `archived` | Arkivert | Slate | Archive |

Add filter option for `workflow_status` alongside the existing filters.

For legacy archived templates (`is_archived_legacy = true`), show a distinct "Arv" badge so users can visually distinguish archived-by-user from archived-by-reset.

### 9. Library Reset Script

**File:** `backend/scripts/library_reset.py` (new)

A one-time script (not an endpoint) that performs the library reset:

1. Query all templates currently in the database
2. For templates tagged "Vitec Next" with content:
   - Set `origin = 'vitec_system'`
   - Set `workflow_status = 'published'` (they are known-good templates)
   - Compute and store `vitec_source_hash` (SHA256 of current content)
3. For templates tagged "Kundemal":
   - Set `origin = 'custom'`
   - Keep their current `workflow_status` (or set to `draft` if empty)
4. For all remaining templates (the legacy bulk):
   - Set `is_archived_legacy = TRUE`
   - Set `workflow_status = 'archived'`
   - Set `origin = 'vitec_system'` or `'custom'` based on heuristics (if content matches Vitec patterns → vitec_system, otherwise → custom)
5. Log a summary: X templates published, Y archived as legacy, Z marked custom

**Safeguards:**
- `--dry-run` flag (default behavior) that shows what would change without modifying data
- `--confirm` flag to actually apply changes
- Print a before/after summary
- The script must be idempotent (safe to run multiple times)

### 10. API Client Updates

**File:** `frontend/src/lib/api.ts` (modify)

Add to `templateApi`:

```typescript
// Workflow
transitionWorkflow: async (templateId: string, body: WorkflowTransition): Promise<WorkflowStatusResponse>
getWorkflowStatus: async (templateId: string): Promise<WorkflowStatusResponse>
getWorkflowHistory: async (templateId: string): Promise<WorkflowEvent[]>

// Content (if not already present)
saveContent: async (templateId: string, content: string, changeNotes?: string, autoSanitize?: boolean): Promise<ContentResponse>
```

Add corresponding TypeScript interfaces for `WorkflowTransition`, `WorkflowStatusResponse`, `WorkflowEvent`.

---

## Scope Boundaries

**In scope:**
- Schema extensions (migration + model)
- Publishing workflow (service, endpoints, UI)
- CKEditor 4 sandbox component
- Template editor page
- Library reset script
- Workflow status display on template cards/list
- API client updates for workflow endpoints

**Out of scope (do NOT do these):**
- Word-to-HTML conversion (Agent 2 — already done)
- AI-powered template comparison (Agent 4)
- Template deduplication/merging (Agent 5)
- Flettekode integration into editor (Agent 6)
- CKEditor toolbar customization beyond ACF config (keep CKEditor's default full toolbar)
- Automatic sync with Vitec Next (no API available)

---

## Testing

- Create and apply the migration locally (`alembic upgrade head`)
- Test each workflow transition: draft → in_review → published, in_review → draft (reject), published → draft (unpublish), any → archived
- Load a real Vitec template (from database) into the CKEditor sandbox and verify:
  - `vitec-if` attributes survive
  - `vitec-foreach` attributes survive
  - `data-label`, `data-version`, `contenteditable` survive
  - Table structures are preserved
  - The validation result correctly reports CKEditor's changes (if any)
- Run the library reset script in `--dry-run` mode and verify the counts match expectations
- Run backend linting (`ruff check`) and frontend linting (`npm run lint`)

---

## CKEditor 4 Critical Notes

From Section 2 of the ruleset and Section 13:

1. **`allowedContent: true` is mandatory** — Without this, CKEditor strips all custom attributes
2. **The CDN version must be the "full-all" package** — It includes all plugins
3. **Test with real templates, not synthetic HTML** — Edge cases only surface with real content
4. **CKEditor normalizes whitespace** — It will reformat your HTML. The validation must distinguish "safe reformatting" from "destructive changes"
5. **Source mode is critical** — Users need to switch to source view for `vitec-if` and `vitec-foreach` editing. The toolbar must include the Source button.

---

## Database Migration Warning

⚠️ Follow the CLAUDE.md migration protocol:

1. Create migration with Alembic
2. Apply locally: `cd backend && alembic upgrade head`
3. Apply to Railway manually:
   ```powershell
   $env:DATABASE_URL = "postgresql://postgres:PASSWORD@shuttle.proxy.rlwy.net:51557/railway"
   cd backend
   python -m alembic upgrade head
   ```
4. Verify: `python -m alembic current` should show your version as `(head)`

If the migration fails silently on Railway, create a fallback script using `ALTER TABLE ... ADD COLUMN IF NOT EXISTS`.

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
**AGENT 3 COMPLETE**

**Files created:**
- [ ] `backend/alembic/versions/YYYYMMDD_XXXX_template_publishing.py`
- [ ] `backend/app/services/template_workflow_service.py`
- [ ] `backend/app/schemas/template_workflow.py`
- [ ] `backend/scripts/library_reset.py`
- [ ] `frontend/src/components/editor/CKEditorSandbox.tsx`
- [ ] `frontend/src/app/templates/[id]/edit/page.tsx`

**Files modified:**
- [ ] `backend/app/models/template.py` (added new columns)
- [ ] `backend/app/routers/templates.py` (added workflow endpoints)
- [ ] `frontend/src/lib/api.ts` (added workflow API methods)
- [ ] `frontend/src/components/templates/TemplateCard.tsx` (workflow status badge)
- [ ] `frontend/src/app/templates/page.tsx` (workflow filter, edit link)

**Migration applied locally:** Yes/No
**Migration applied to Railway:** (Not done — orchestrator will handle)

**CKEditor 4 validation test results:**
- `vitec-if` attributes preserved: Yes/No
- `vitec-foreach` attributes preserved: Yes/No
- `data-label` / `data-version` preserved: Yes/No
- `contenteditable` preserved: Yes/No
- Table structures preserved: Yes/No
- Custom Stilark classes preserved: Yes/No

**Library reset dry-run results:**
- Templates marked as published (Vitec Next): X
- Templates marked as archived legacy: X
- Templates marked as custom: X

**Workflow transitions tested:**
- draft → in_review: Pass/Fail
- in_review → published: Pass/Fail
- in_review → draft (reject): Pass/Fail
- published → draft (unpublish): Pass/Fail
- any → archived: Pass/Fail

**Linting:** Pass/Fail

**Issues encountered:** (list any or "None")

**Schema additions ready for Agents 4, 5, 6:**
- `vitec_source_hash` — Agent 4 uses this for comparison baseline
- `property_types` — Agent 5 uses this for deduplication grouping
- `ckeditor_validated` — Agent 4 can reference validation state
- `origin` — Agent 5 uses this to identify merge candidates

**Ready for Agents 4, 5, 6:** Yes/No
---
