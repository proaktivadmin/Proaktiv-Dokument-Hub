# Phase 11: HTML Template Management & Publishing Suite

## Overview

Evolve the existing template storage (261 templates in PostgreSQL) into a comprehensive HTML template management and publishing suite. Includes a Word-to-HTML conversion pipeline, CKEditor 4 validation sandbox, AI-powered Vitec change analysis, template deduplication, and Flettekode editor integration.

**Goal**: Give the project owner full control over the template lifecycle — from authoring and validation through publishing and ongoing maintenance — without needing to read HTML source code or manually diff Vitec updates.

---

## Success Criteria

1. A formal HTML ruleset document derived from real Vitec system templates, reviewed and approved by the project owner
2. A working Word-to-HTML pipeline that produces CKEditor 4-compliant, Vitec-ready HTML
3. A template editing UI with CKEditor 4 sandbox for pre-flight validation
4. A publishing workflow (draft → review → published)
5. A clean library baseline from active Vitec Next templates, with legacy templates archived
6. An AI-powered comparison tool for analyzing Vitec system template updates
7. A deduplication tool for consolidating same-purpose templates using vitec-if logic
8. Flettekode merge field insertion integrated directly into the template editor

---

## Current State

### What Exists

- **261 templates** in PostgreSQL (44 in active use, rest are scraped archive)
- **Template model** with 30+ fields: Vitec metadata, version history (`TemplateVersion`), content hash (SHA256), status (draft/published/archived), layout partials, JSONB fields for phases/receivers/departments
- **Services**: `TemplateService`, `TemplateContentService`, `TemplateSettingsService`, `TemplateAnalyzerService`, `SanitizerService`, `MergeFieldService`
- **Frontend**: Shelf + Table views, multi-mode preview (A4/Email/SMS), `ElementInspector`, `SimulatorPanel`, `FlettekodeLibrary` with search/autocomplete/code generator
- **Merge field registry** with auto-discovery, usage tracking, categorisation
- **WebDAV client** for `proaktiv.no/d/` storage
- **Chrome MCP scraping workflow** for pulling templates from Vitec Next

### What Was Built (Phase 11)

- **Word-to-HTML pipeline** — mammoth + BeautifulSoup post-processing + SanitizerService + 12-item validation checklist (Agent 2)
- **CKEditor 4 sandbox** — Iframe with postMessage API, `allowedContent: true`, validation mode, source toggle (Agent 3)
- **Publishing workflow** — Full state machine (draft/in_review/published/archived) with service, endpoints, and UI badges (Agent 3)
- **Template editor page** — `/templates/{id}/edit` with 60/40 split, CKEditor + tabbed sidebar (Agent 3)
- **Library reset script** — `--dry-run` / `--confirm` to classify 261 templates by origin (Agent 3)
- **Schema extensions** — 10 new columns including `workflow_status`, `origin`, `vitec_source_hash`, `property_types`, `ckeditor_validated` (Agent 3)
- **AI-powered template comparison** — Structural diff (6 change categories) + LLM analysis (Google/OpenAI/Anthropic) with recommendation engine (Agent 4)
- **Template deduplication** — Candidate identification, merge analysis, merge engine with vitec-if generation (Agent 5)
- **Flettekode editor integration** — Merge field panel (3 tabs), inline `[[` autocomplete, WYSIWYG highlighting (Agent 6)
- **Formal HTML ruleset** — 3,208 lines, 14 sections, derived from real Vitec system templates (Agent 1)

---

## Agent Pipeline

Execute agents in sequence. Each agent receives a written plan, works only within its scope, runs its own QA, and delivers a structured handoff summary before the next agent begins.

| # | Agent | Plan File | Deliverables | Status |
|---|-------|-----------|-------------|--------|
| 1 | Documentation Agent | `AGENT-1-DOCUMENTATION.md` | Formal HTML ruleset document (3,208 lines, 14 sections) | **Complete** (Approved) |
| 2 | Conversion Agent | `AGENT-2-CONVERSION.md` | Word-to-HTML pipeline (mammoth + BeautifulSoup + SanitizerService) | **Complete** |
| 2B | **Template Builder Agent** | `AGENT-2B-TEMPLATE-BUILDER.md` | Production-ready Vitec Next HTML templates from source documents | **Active** |
| 3 | Storage & Editor Agent | `AGENT-3-STORAGE-EDITOR.md` | Schema (10 columns), CKEditor sandbox, publishing workflow, library reset | **Complete** |
| 4 | Comparison Agent | `AGENT-4-COMPARISON.md` | AI-powered template change analysis (structural diff + LLM summary) | **Complete** |
| 5 | Merge Agent | `AGENT-5-MERGE.md` | Template deduplication using vitec-if logic (5 groups, 10 templates) | **Complete** |
| 6 | Flettekode Integration Agent | `AGENT-6-FLETTEKODE.md` | Editor merge field integration (panel, autocomplete, highlighting) | **Complete** |

### Agent 2B: Why It Exists

The pilot conversion of "Kjøpekontrakt prosjekt (enebolig med delinnbetalinger)" proved that Agent 2's automated conversion pipeline produces only basic HTML structure. Production-ready Vitec Next templates require domain-specific engineering that a conversion script cannot automate:

- **Merge field mapping:** Legacy `#field.context¤` syntax → modern `[[field.path]]` requires a curated mapping table
- **Conditional logic:** Red text markers, checkbox alternatives, and section variants must be identified in the source and converted to `vitec-if` expressions with proper escaping
- **Party loops:** Flat party listings must be restructured into `vitec-foreach` loops with `roles-table` layout
- **Template shell:** CSS counters, table colspan system, signature blocks, and insert placeholders must be engineered
- **Content accuracy:** Legal text must be verbatim — no AI paraphrasing allowed

Agent 2B uses the knowledge base in `PRODUCTION-TEMPLATE-PIPELINE.md` to replicate this process efficiently across all remaining templates.

### Agent 2B Knowledge Base

The pipeline guide (`PRODUCTION-TEMPLATE-PIPELINE.md`) contains:

1. Source format comparison and recommendations
2. The 6-step conversion pipeline
3. Template style block (CSS counters)
4. Complete field mapping reference (legacy → modern)
5. Conditional pattern library (12 patterns)
6. Party loop patterns (roles-table)
7. Source document clue recognition table
8. Validation script reference
9. Template inventory with effort estimates
10. Step-by-step agent instructions
11. File reference
12. Known issues & edge cases

---

## Timeline & Dependencies

```
[Agent 1: Documentation] ──── HUMAN APPROVAL GATE ────┬── [Agent 2: Conversion]
                                                       │         │
                                                       │   [Agent 2B: Template Builder]  ← REPEATABLE
                                                       │     (runs once per template)
                                                       │
                                                       └── [Agent 3: Storage & Editor]
                                                                     │
                                                       ┌─────────────┼─────────────┐
                                                       │             │             │
                                                [Agent 4:     [Agent 5:     [Agent 6:
                                                Comparison]    Merge]       Flettekode]
```

- Agent 1 has no dependencies and starts immediately
- Agents 2 and 3 can run in parallel after Agent 1's ruleset is approved
- **Agent 2B runs after Agent 2** and is invoked once per template. It uses the pipeline knowledge base to produce production templates.
- Agents 4, 5, and 6 can run in parallel after Agent 3 completes (they depend on the schema extensions and editor UI)

---

## Key Technical Decisions

| Decision | Rationale |
|----------|-----------|
| CKEditor 4 via CDN in iframe | No npm dependency, sandboxed, matches Vitec's actual editor version |
| `mammoth` for docx conversion | Clean semantic HTML output, configurable style mapping, well-maintained |
| Structural diff via `bs4` | Comparing parsed DOM trees gives meaningful change categories vs raw text diff |
| LLM-powered comparison analysis | Plain-language summaries require natural language generation; needs API key config |
| Legacy archive, not migration | The 261 templates get flagged `is_archived_legacy`, not deleted; new baseline from Vitec |
| Only "Vitec Next" tagged templates for ruleset | Original system templates are the authoritative source; "Kundemal" templates may contain non-standard patterns |

---

## Database Access

All agents have read-only access to the production PostgreSQL database via the `user-postgres` MCP tool. Use `CallMcpTool` with server `user-postgres` and tool `query` to run SQL queries.

**Template stats:** 261 total templates — 133 tagged "Vitec Next" (original system templates), 83 tagged "Kundemal" (custom), 45 untagged.

**Key query — Vitec Next templates with content:**

```sql
SELECT tmpl.id, tmpl.title, tmpl.content, tmpl.channel, tmpl.template_type
FROM templates tmpl
JOIN template_tags tt ON tmpl.id = tt.template_id
JOIN tags t ON tt.tag_id = t.id
WHERE t.name = 'Vitec Next'
AND tmpl.content IS NOT NULL AND tmpl.content != ''
ORDER BY LENGTH(tmpl.content) DESC
```

**Note:** The backend API (`https://proaktiv-admin.up.railway.app`) requires authentication. Use the MCP tool for all database reads.

---

## Reference Files

| File | Purpose |
|------|---------|
| `docs/vitec-stilark.md` | Official Vitec Stilark CSS (authoritative, replaceable) |
| `docs/Alle-flettekoder-25.9.md` | Complete flettekode reference template (6,494 lines of production HTML) |
| `.cursor/vitec-reference.md` | Vitec metadata reference (categories, property types, merge fields, best practices) |
| `docs/vitec-next-export-format.md` | JSON export format for Vitec Next templates |
| `docs/vitec-next-mcp-scrape-and-import.md` | Chrome MCP scraping workflow |
| `backend/app/services/sanitizer_service.py` | Existing sanitizer rules |
| `backend/app/services/template_analyzer_service.py` | Template analysis (merge field extraction, conditions, loops) |

---

## Risk Assessment

| Risk | Mitigation |
|------|------------|
| CKEditor 4 CDN becomes unavailable | Pin specific version, consider self-hosting the JS |
| Ruleset misses edge cases | Analyse broad set of "Vitec Next" tagged templates, not just a few |
| mammoth output doesn't match Vitec expectations | Post-processing pipeline with ruleset-based cleanup + SanitizerService pass |
| LLM API costs for comparison feature | Make analysis optional, cache results, allow offline structural diff without LLM |
| Migration fails on Railway | Manual migration application (established pattern, see CLAUDE.md) |
| Agents exceed scope | Each agent has explicit scope boundaries and handoff format |

---

## Future Phase (Out of Scope)

Interactive PDF generation with fillable form fields for customer-facing documents. The data model and template structure must not prevent this from being added later. Specifically, the `property_types` JSONB field and flexible content model should remain extensible.

---

## Notes

- Norwegian UI labels throughout (matching existing patterns)
- All agents must check for linting errors before completion
- No agent may push to remote — commits are done by the orchestrator after review
- The Chrome MCP scraping workflow is documented but not required for Phase 11; it remains available for future library refreshes
