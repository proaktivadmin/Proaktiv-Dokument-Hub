---
name: vitec-template-builder
description: Build production-ready Vitec Next HTML templates from Word-exported source documents. Converts legacy merge fields, adds vitec-if conditionals, vitec-foreach loops, CSS counters, and the full template shell. Use when asked to convert, build, or produce a Vitec template, process a Word document for Vitec Next, or work with flettekoder, vitec-if, or template HTML.
---

# Vitec Template Builder

Build production-ready Vitec Next HTML templates from Word-exported `.htm` source files.

This is NOT a simple conversion — it is domain-specific template engineering that maps legacy merge fields, builds conditional logic, constructs party loops, and wraps content in the Vitec template shell.

## When to Use

- User provides a Word document (.htm, .docx, .rtf) to convert into a Vitec Next template
- User asks to build, produce, or create a Vitec template
- User asks to add flettekoder, vitec-if, or vitec-foreach to a template
- User asks to fix, refine, or improve an existing Vitec template
- User asks about merge field syntax, conditional patterns, or template structure

## Read First (Required)

Before starting any template work, read these files **in this order**:

1. `.planning/phases/11-template-suite/PRODUCTION-TEMPLATE-PIPELINE.md` — **Primary reference.** Contains the complete pipeline (6 steps), field mapping table, conditional pattern library, party loop patterns, source clue recognition, and quality checklist.
2. `.planning/vitec-html-ruleset.md` — Sections 1 (Shell), 6 (Tables), 10 (Conditionals), 12 (Validation Checklist)
3. `.cursor/Alle-flettekoder-25.9.md` — Complete merge field reference (6,494 lines). Search when you encounter an unmapped field.

For the full agent task specification: `.planning/phases/11-template-suite/AGENT-2B-TEMPLATE-BUILDER.md`

## Quick Reference

### Source Format

**Always use "Web Page, Filtered (*.htm)"** exported from Word. This preserves tables, headings, Wingdings checkboxes, and red text markers that other formats lose.

If a `.docx` is provided, recommend re-saving as filtered `.htm` for best results. If that's not possible, use `mammoth` but expect to lose checkbox and color markers.

### Template Shell

Every template must have this outer structure:

```html
<div class="proaktiv-theme" id="vitecTemplate">
<span vitec-template="resource:Vitec Stilark">&nbsp;</span>
<style type="text/css">
  /* CSS counters — see PRODUCTION-TEMPLATE-PIPELINE.md Section 3 */
</style>
<!-- Template content here -->
</div>
```

### Merge Field Syntax

| Syntax | Usage |
|--------|-------|
| `[[field.path]]` | Standard merge field |
| `[[*field.path]]` | Required field (inside vitec-foreach only) |
| `$.UD([[field]])` | Number formatting (thousand separators) |

Legacy `#field.context¤` must be mapped to modern `[[field.path]]` using the mapping table in PRODUCTION-TEMPLATE-PIPELINE.md Section 4.

### Conditional Logic

```html
<span vitec-if="Model.eiendom.grunntype == &quot;Bolig&quot;">Boligen</span>
```

Escaping rules:
- `"` → `&quot;`
- `>` → `&gt;`
- `<` → `&lt;`
- `&&` → `&amp;&amp;`

Full pattern library in PRODUCTION-TEMPLATE-PIPELINE.md Section 5.

### Party Loops

```html
<table class="roles-table" vitec-if="Model.selgere.Count &gt; 0">
<tbody vitec-foreach="selger in Model.selgere">
  <tr><td>[[*selger.navnutenfullmektigogkontaktperson]]</td></tr>
</tbody>
</table>
```

Every `vitec-foreach` needs a collection guard on its parent.

### Source Clue Recognition

| Source Pattern | Meaning | Action |
|---------------|---------|--------|
| `#field.context¤` | Legacy merge field | Map to `[[modern.field]]` |
| Wingdings + `q` | Empty checkbox | → `&#9744;` or auto-check pattern |
| `color:red` text | Conditional alternative | → `vitec-if` branch |
| "Alt 1:" / "Alt 2:" | Explicit alternatives | → `vitec-if` div blocks |
| "Boligen/fritidsboligen" | Property type switch | → `grunntype` condition |
| "1 A" / "1 B" headers | Ownership form switch | → `eieform` condition |
| `…………` or underlines | Fill-in blank | → `<span class="insert">&nbsp;</span>` |

## Workflow

### Building a New Template

```
Task Progress:
- [ ] Step 1: Read source .htm file, produce source analysis
- [ ] Step 2: Map all legacy merge fields to modern syntax
- [ ] Step 3: Identify and build vitec-if conditional branches
- [ ] Step 4: Build vitec-foreach party loops
- [ ] Step 5: Wrap in template shell with CSS counters
- [ ] Step 6: Run 39-point validation (target: 39/39 PASS)
- [ ] Step 7: Generate preview, verify content against original
```

**Step 1: Source Analysis**
Read the `.htm` file. Document: section count, legacy fields found, checkboxes, red text markers, alternative sections, tables, signature blocks.

**Step 2: Field Mapping**
Look up each legacy field in PRODUCTION-TEMPLATE-PIPELINE.md Section 4. For unmapped fields, search `.cursor/Alle-flettekoder-25.9.md`.

**Step 3: Conditionals**
Match source patterns to the conditional pattern library (Section 5). Build `vitec-if` with proper HTML entity escaping.

**Step 4: Party Loops**
Replace flat party listings with `vitec-foreach` using the roles-table pattern (Section 6). Add collection guards.

**Step 5: Template Shell**
Wrap in `#vitecTemplate` div, add Stilark reference, add CSS counter style block, convert sections to `<article class="item">`.

**Step 6: Validate**
Run `scripts/validate_template.py` (update `TEMPLATE` path). Fix failures until 39/39.

**Step 7: Preview & Verify**
Run `scripts/build_preview.py` to generate visual preview. Compare against original PDF section by section.

### Refining an Existing Template

1. Read the template HTML
2. Identify issues (missing fields, broken conditions, incorrect escaping)
3. Apply fixes referencing the pattern library
4. Re-validate

### Reusing the Pilot for Kjøpekontrakt Variants

For templates sharing ~85% structure with the pilot:
1. Start from `scripts/build_production_template.py`
2. Diff source against pilot source to identify differences
3. Modify only differing sections
4. Re-validate

## Database Access

Query production templates for reference:

```sql
-- MCP tool: user-postgres, tool: query
SELECT title, content FROM templates tmpl
JOIN template_tags tt ON tmpl.id = tt.template_id
JOIN tags t ON tt.tag_id = t.id
WHERE t.name = 'Vitec Next'
AND title LIKE '%search_term%'
ORDER BY LENGTH(content) DESC LIMIT 1
```

## Utility Scripts

| Script | Purpose | Usage |
|--------|---------|-------|
| `scripts/validate_template.py` | 39-point validation | `python scripts/validate_template.py` |
| `scripts/build_preview.py` | Visual preview with Stilark CSS | `python scripts/build_preview.py` |
| `scripts/build_production_template.py` | Pilot template builder (reference) | `python scripts/build_production_template.py` |

## Output Files

| File | Location |
|------|----------|
| Build script | `scripts/build_[template_name].py` |
| Production HTML | `scripts/converted_html/[name]_PRODUCTION.html` |
| Preview HTML | `scripts/converted_html/[name]_PREVIEW.html` |

## Quality Checklist (Quick)

- [ ] `<div class="proaktiv-theme" id="vitecTemplate">` wrapper
- [ ] `<span vitec-template="resource:Vitec Stilark">&nbsp;</span>`
- [ ] CSS counter style block
- [ ] All `<article class="item">` with `<h2>` headings
- [ ] No legacy `#field¤` syntax remaining
- [ ] All `vitec-if` use `&quot;` for quotes
- [ ] All `vitec-foreach` have collection guards
- [ ] `roles-table` on party tables
- [ ] `costs-table` on financial tables
- [ ] Signature block with signing lines
- [ ] `span.insert` for user fill-in fields
- [ ] Norwegian characters (æ, ø, å) preserved
- [ ] No inline `font-family` or `font-size`
- [ ] UTF-8 encoding, no Windows-1252 artifacts
- [ ] Validation: 39/39 PASS

## Rules

- Legal text must be **verbatim** from source — never paraphrase
- All merge fields use `[[field.path]]` — no legacy `#field¤`
- All `vitec-if` use HTML entity escaping
- All `vitec-foreach` have collection guards
- UTF-8 only
- Norwegian characters preserved, never transliterated
- If a field mapping is unclear, **ask** — don't guess
