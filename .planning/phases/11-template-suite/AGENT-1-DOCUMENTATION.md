# TASK: Documentation Agent — Produce Vitec HTML Ruleset

## Role & Objective

You are the Documentation Agent. Your sole deliverable is a formal markdown document: `.planning/vitec-html-ruleset.md`. You write no code. You make no changes to the codebase. Your output is the source of truth that every subsequent agent depends on — if your ruleset has gaps or errors, they will propagate through the entire project. Take the time to get this right.

Human approval of your deliverable is required before any other agent begins work.

---

## Read First

Before doing anything else, read these files in order to orient yourself:

1. `CLAUDE.md` — Project overview, architecture, conventions
2. `.planning/STATE.md` — Current project state and recent work
3. `.planning/codebase/ARCHITECTURE.md` — System architecture
4. `.planning/codebase/STACK.md` — Technology stack

Then read these reference files in full:

- `.cursor/vitec-reference.md` — Vitec metadata, document categories, property types, customer relation types, merge field syntax, standard template examples
- `docs/vitec-stilark.md` — The official Vitec Stilark CSS (fresh copy, treat as authoritative). This file contains only the raw Stilark HTML/CSS and should be replaceable with a new copy at any time without losing anything.
- `docs/Alle-flettekoder-25.9.md` — This is both a flettekode reference AND a real working template source. It is 6,494 lines of production HTML containing 118 instances of vitec-if/vitec-foreach, 100 instances of data-label/data-version/contenteditable, and 16 function calls (.Where(), $.UD(), $.BOKST(), $.CALC()). Treat it as primary evidence of valid HTML patterns used in production.
- `docs/vitec-next-export-format.md` — The JSON export format used to pull templates from Vitec Next
- `backend/app/services/sanitizer_service.py` — Existing sanitizer rules. Understand what is already being preserved and stripped. Key: the `PRESERVE_STYLES` list defines which inline CSS properties survive sanitisation.

---

## Source Collection (Do This Before Writing Anything)

You have one source of real template HTML: the templates stored in the Proaktiv Dokument Hub database.

**Important filter: Only analyse templates tagged "Vitec Next".** These are original Vitec system templates scraped from the live system. Do NOT include templates tagged "Kundemal" — those are custom-made or heavily edited by us and do not represent Vitec's standard patterns. The ruleset must be derived from what Vitec considers valid, not from our customisations.

**How to access templates:**

Use the `user-postgres` MCP tool (via `CallMcpTool`) to query the production PostgreSQL database directly. This is a read-only connection to the Railway-hosted database.

To get all Vitec Next tagged templates with their HTML content:

```sql
SELECT tmpl.id, tmpl.title, tmpl.content, tmpl.channel, tmpl.template_type,
       tmpl.file_type, LENGTH(tmpl.content) AS content_length
FROM templates tmpl
JOIN template_tags tt ON tmpl.id = tt.template_id
JOIN tags t ON tt.tag_id = t.id
WHERE t.name = 'Vitec Next'
AND tmpl.content IS NOT NULL AND tmpl.content != ''
ORDER BY LENGTH(tmpl.content) DESC
```

There are 133 templates tagged "Vitec Next" with HTML content. For large templates, you may want to query content individually by ID:

```sql
SELECT title, content FROM templates WHERE id = 'UUID_HERE'
```

The MCP tool server is `user-postgres`, and the tool name is `query`. Pass your SQL as the `sql` argument.

**What to prioritise:** Templates that use `vitec-if`, `vitec-foreach`, tables, images, nested structures, forms with `data-label`, and SVG elements. These represent the complex patterns that are most likely to cause issues during conversion or editing.

**Also use the reference file:** `docs/Alle-flettekoder-25.9.md` is a single template containing nearly every Vitec pattern in one document. It is the single richest source of pattern evidence you have access to.

Do not begin writing the ruleset until you have collected and analysed a representative sample from the database.

---

## What to Investigate

For each pattern you find in the collected templates, document whether it is safe, unsafe, or conditional. Pay particular attention to:

### CKEditor 4 Behaviour

CKEditor 4 is used inside Vitec Next as the template editor. It is known to silently strip or rewrite HTML it considers invalid. Your job is to determine — from evidence, not assumption — which elements, attributes, and structures survive CKEditor intact. Custom attributes like `vitec-if`, `vitec-foreach`, `data-label`, `data-version`, and `contenteditable` are non-standard and CKEditor may strip them unless explicitly allowed. Document exactly which ones are safe and under what conditions.

Also investigate what CKEditor 4 is capable of beyond what Vitec currently uses. There may be supported elements, formatting options, or structural patterns that are valid in CKEditor 4 but simply have not been used in Vitec templates yet. Document these as "unexplored but potentially available" — this gives future agents and the project owner informed options rather than just replicating current limitations.

### Vitec-if and Vitec-foreach

These are the patterns most likely to cause issues when implemented incorrectly. Document:
- The exact safe syntax
- Which HTML elements can safely carry these attributes
- Nesting rules
- Escaping requirements (particularly `&quot;` for string comparisons inside attribute values)
- Known failure modes with concrete examples of what breaks and why

### Table Structures

Tables are complex and CKEditor is opinionated about them. Document:
- Which table patterns are confirmed safe
- Which are known to break
- What CKEditor does when it encounters table structures it does not like
- The `form-table` class pattern and its behaviour

### The Stilark and Template Wrapper

Document the required outer structure every template must have:
- The `#vitecTemplate` wrapper div
- The Stilark resource reference (`<span vitec-template="resource:Vitec Stilark">&nbsp;</span>`)
- A4 dimensions (21cm width, standard margins)
- How the Stilark CSS interacts with inline styles

### Merge Field Syntax

Document:
- `[[field.path]]` syntax rules
- `[[*field.path]]` (required fields with asterisk)
- Nesting constraints
- Use inside attributes vs text nodes
- The `$.UD()`, `$.BOKST()`, `$.CALC()` function wrappers
- Any edge cases found in real templates

### SVG and Image Patterns

Document:
- The base64 SVG checkbox/radio pattern
- Image embedding conventions
- The `figure`/`figcaption` pattern
- Logo and property image patterns
- The `.scaled-image` class pattern

### Form-like Structures

Document:
- `span.insert` elements and their `data-label` attribute
- `data-label` on `td` elements with `::before` pseudo-element patterns
- The `contenteditable="false"` pattern
- The `data-version` attribute and version tagging behaviour

---

## Deliverable Structure

Produce `.planning/vitec-html-ruleset.md` with the following sections:

### 1. Required Template Shell

The exact outer HTML structure every template must follow. Include the `#vitecTemplate` wrapper, Stilark resource reference, and any required meta elements. Provide a complete minimal example.

### 2. CKEditor 4 Compatibility Rules

What CKEditor 4 allows, strips, rewrites, or requires. Organised by element type. Include a clear table distinguishing safe / unsafe / conditional. Include a section on capabilities beyond current Vitec usage.

### 3. Vitec-if Conditional Logic

Full syntax reference with safe patterns, unsafe patterns, nesting rules, escaping rules, and failure mode examples.

### 4. Vitec-foreach Iteration

Full syntax reference including `.Where()`, `.Any()`, `.Take()` filtering patterns, safe container elements, and known edge cases.

### 5. Merge Field Reference

Syntax rules, function wrappers, attribute vs text node usage, and edge cases.

### 6. Table Patterns

Safe table structures, known-breaking patterns, CKEditor table behaviour, and the `form-table` class pattern.

### 7. CSS and Styling Rules

What inline styles survive rendering, which Stilark classes are available and safe, CSS properties to avoid, and the interaction between Stilark and inline styles. Reference the `PRESERVE_STYLES` list from `sanitizer_service.py`.

### 8. SVG, Images, and Media

Base64 SVG patterns, image embedding, the `figure` pattern, and logo/property image conventions.

### 9. Form-like Structures

`span.insert`, `data-label`, `contenteditable`, `data-version` patterns with safe usage examples.

### 10. Property Type Conditional Patterns

The confirmed safe patterns for branching content by property type, ownership type, and assignment type using vitec-if. These are the foundation for the template merging work in Agent 5 (a later phase). Document concrete examples from real templates.

### 11. Known Failure Modes

A dedicated section listing confirmed ways templates break in CKEditor or fail in Vitec rendering, with examples. This is as important as the safe patterns.

### 12. Conversion Checklist

A step-by-step checklist that the Word-to-HTML Conversion Agent (Agent 2) can follow mechanically to validate that a converted template meets all rules before handoff. This checklist must be self-contained — Agent 2 should be able to follow it without needing to read the rest of the ruleset document.

---

## File Organisation

Ensure the following file separation is in place before you finish:

- `docs/vitec-stilark.md` — Vitec Stilark CSS only. No custom content. This file should be replaceable with a fresh Stilark copy at any time without losing anything.
- `.cursor/vitec-reference.md` — Custom reference documentation only (categories, property types, relation types, flettekode syntax, best practices). No Stilark CSS.

Currently, `.cursor/vitec-reference.md` contains a copy of the Stilark CSS starting around line 516 (under "## Vitec Stilark (Base Stylesheet)"). This duplicated content should be removed from the reference file and a pointer added to `docs/vitec-stilark.md` instead. Document this change in your handoff summary.

---

## Scope Boundaries

**In scope:**
- Analysing template HTML patterns from the database
- Documenting CKEditor 4 compatibility rules
- Producing the formal ruleset document
- Separating Stilark from reference documentation

**Out of scope (do NOT do these):**
- Writing any code
- Modifying any backend or frontend files (except the file separation noted above)
- Creating database migrations
- Building UI components
- Scraping Vitec Next via Chrome MCP (not needed — the database templates are sufficient)

---

## QA Before Handoff

Before declaring your work complete, verify:

- Every rule in your document is backed by at least one real template example, either from the database or from `docs/Alle-flettekoder-25.9.md`
- The CKEditor 4 compatibility section covers all non-standard attributes found in collected templates
- The conversion checklist in Section 12 is complete enough that Agent 2 could follow it without needing to read the rest of the document
- The Stilark and reference files are cleanly separated
- No code has been written or modified (beyond the file separation)

---

## Handoff Summary

When complete, produce a handoff summary in this exact format:

---
**AGENT 1 COMPLETE**

**Templates analysed:**
- Database templates (Vitec Next tagged): (count)
- Reference template (Alle-flettekoder): Yes/No

**Key findings not previously documented:**
- (list)

**CKEditor 4 capabilities identified beyond current Vitec usage:**
- (list)

**Patterns found in database templates not covered by existing sanitizer rules:**
- (list)

**File separation:**
- [ ] `docs/vitec-stilark.md` contains only Stilark CSS
- [ ] `.cursor/vitec-reference.md` contains no Stilark CSS (pointer added)
- [ ] Duplicate Stilark content removed from reference file

**Open questions or ambiguities for Agent 2 / Agent 3:**
- (list, or "None")

**Deliverable path:** `.planning/vitec-html-ruleset.md`

**Ready for human review:** Yes/No
---

---

## Rules

- Follow existing project conventions (read CLAUDE.md)
- All analysis must be evidence-based — cite specific templates or line numbers
- Do NOT make assumptions about CKEditor behaviour — derive from observed patterns
- Do NOT write code or modify the codebase (except file separation)
- Do NOT commit or push anything
- If anything is unclear, ASK before proceeding
