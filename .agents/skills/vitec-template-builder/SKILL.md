---
name: vitec-template-builder
description: Build production-ready Vitec Next HTML templates. Handles three operational modes (edit, convert, create new) across five complexity tiers. Use when asked to convert, build, edit, or produce a Vitec template, process a Word document for Vitec Next, or work with flettekoder, vitec-if, or template HTML.
---

# Vitec Template Builder

Build production-ready Vitec Next HTML templates with merge fields, conditional logic, party
loops, and the full template shell.

**Track record:** 11 production templates built, 6/6 validated at 100% pass rate.

## MANDATORY Pre-Read Files

Before ANY build, read these files in order:

1. **LESSONS.md** (this directory) — Every known mistake and its fix. Apply proactively.
   Includes the **Source of Truth Hierarchy** — follow it when sources conflict.
2. **PATTERNS.md** (this directory) — Copy-pasteable reference patterns. Use verbatim.
3. **CHANGELOG.md** (this directory) — Recent changes to the knowledge base. Check for relevant updates.
4. This file (SKILL.md) — Pipeline stages and quick reference.

These four files together form the complete knowledge base for one-shot perfection.

**Maintenance rule:** Any agent that modifies LESSONS.md, PATTERNS.md, SKILL.md, the validator
(`scripts/tools/validate_vitec_template.py`), or the post-processor
(`scripts/tools/post_process_template.py`) MUST append a dated entry to CHANGELOG.md
describing what changed and why.

### Primary References (the actual source of truth)

- **Working reference templates** — `scripts/reference_templates/` and `scripts/golden standard/`
  Verified production templates from Vitec Next that render correctly in PDF.
- **Master template library** — `templates/master/` (249 official templates, scraped 2026-02-23)
  The complete set of Vitec system and Proaktiv custom templates from production.
- **Vitec Stilark** — `docs/vitec-stilark.md`
  The default style system loaded by Vitec Next. Templates inherit these styles.

**Do NOT use** `.planning/vitec-html-ruleset-FULL.md` as the primary authority.
It was generated from the old database (133 Proaktiv-customized templates) and contains
conventions specific to Proaktiv that do not reflect the Vitec standard.

## When to Use

- User provides a Word document (.htm, .docx, .rtf) to convert into a Vitec Next template
- User asks to build, produce, or create a Vitec template
- User asks to edit, update, or fix an existing Vitec template
- User asks to add flettekoder, vitec-if, or vitec-foreach to a template
- User asks about merge field syntax, conditional patterns, or template structure
- User asks to reconcile a Vitec update with customized templates

## STEP 1: Intake Questionnaire (Read NOTHING else first)

Before loading any reference files, ask the user these three questions:

### Question 1: Mode

| Mode | Use when |
|------|----------|
| **A1** | Editing a template currently in production (user-requested change) |
| **A2** | Reconciling a Vitec system update with our customized template |
| **B** | Converting an existing document from Word/old format |
| **C** | Creating a brand new template from scratch |

### Question 2: Tier

| Tier | Type | Examples |
|------|------|----------|
| **T1** | Plain text | SMS templates |
| **T2** | Simple HTML | Email templates, simple notices |
| **T3** | Structured document | Letters, simple agreements |
| **T4** | Complex contract | Kjøpekontrakt, Oppdragsavtale |
| **T5** | Interactive form | Multi-party contracts with dynamic sections |

### Question 3: Scope (Mode A only)

- Which template? (name or ID)
- What change? (A1) / Which Vitec update version? (A2)
- Risk: cosmetic / structural / critical

### Produce Spec Sheet

```
MODE: [A1/A2/B/C]
TIER: [T1-T5]
TEMPLATE: [name]
SCOPE: [description]
RISK: [cosmetic/structural/critical] (Mode A only)
FILES TO READ: [list based on mode + tier]
STAGES TO EXECUTE: [S0-S10 with skips noted]
```

**Wait for user confirmation before proceeding.**

## STEP 2: Launch Analysis Subagents (T3+ Mode B/C)

For T3+ conversions, launch three parallel analysis subagents using the Task tool.
Each agent reads only what it needs and writes its output to `scripts/_analysis/{template_name}/`.

**Prompt templates:** `.planning/phases/11-template-suite/SUBAGENT-PROMPTS.md`
**Output format specs:** `scripts/_analysis/FORMAT_structure.md`, `FORMAT_fields.md`, `FORMAT_logic.md`

### Launch 3 subagents in parallel (single message, 3 Task calls):

| # | Subagent | Model | Reads | Writes |
|---|----------|-------|-------|--------|
| 1 | **Structure Analyzer** | fast | Source document only | `_analysis/{name}/structure.md` |
| 2 | **Field Mapper** | fast | Source + field-registry.md | `_analysis/{name}/fields.md` |
| 3 | **Logic Mapper** | fast | Source + conditional-logic ruleset + VITEC-IF-DEEP-ANALYSIS.md | `_analysis/{name}/logic.md` |

Fill in the `{placeholders}` in each prompt template with the actual file paths and template name.

### After all 3 complete:

1. Read all three analysis outputs
2. Check for `NEED REVIEW` flags — resolve with user before proceeding
3. Check for unmapped fields — resolve with user before proceeding

### For T1/T2 or Mode A:

Skip subagents. The template is simple enough for direct handling:
- T1/T2: Read the source and build directly using patterns from this skill file
- Mode A: Read the existing template from the database, apply the requested change

## STEP 3: Launch Builder Subagent (T3+ Mode B/C)

Launch a single Builder subagent using the Task tool (default model, NOT fast).

The builder reads the 3 analysis outputs + this SKILL.md + source document (for verbatim text).
See the Builder prompt template in `SUBAGENT-PROMPTS.md`.

### After builder completes:

Launch 2 validation subagents in parallel:

| # | Subagent | Model | Purpose |
|---|----------|-------|---------|
| 5 | **Static Validator** | fast | Runs scripts/tools/validate_vitec_template.py |
| 6 | **Content Verifier** | fast | Compares HTML vs source for accuracy |

### Pass/Fail Decision:

- **All pass:** Proceed to STEP 4 (Post-Processing)
- **Validation fails:** Resume the builder subagent with specific failure details
- **Content issues:** Resume the builder subagent with the content verifier's report
- Iterate until both validators pass

### For T1/T2 or Mode A:

Build directly, then proceed to STEP 4 (Post-Processing).

## STEP 4: Post-Processing (MANDATORY — ALL builds)

**This step is NON-NEGOTIABLE.** Run the post-processor on every template before final validation:

```bash
python scripts/tools/post_process_template.py <production_html> --in-place
```

This automatically applies:
- **E1:** Norwegian character → HTML entity encoding
- **E3:** ASCII-ifies Norwegian characters in comments
- **S2:** Removes `proaktiv-theme` class if present

And warns about issues needing manual attention:
- **S1:** Missing outer table wrapper
- **S3:** Wrong title tag level (H5 instead of H1)
- **CB1:** Unicode checkboxes still present
- **MF2:** Bare monetary fields without `$.UD()`
- **V2:** Foreach loops without guards/fallbacks

**If warnings are reported, fix them before proceeding.**

## STEP 5: Final Validation

Run the validator on the post-processed template:

```bash
python scripts/tools/validate_vitec_template.py <production_html> --tier {tier}
```

If any checks fail, fix and re-run. Do NOT skip this step.

## STEP 6: Handoff

Write the handoff summary to `scripts/handoffs/{name}_HANDOFF.md` documenting:
- Spec sheet (mode, tier, template name)
- Production file path and size
- Template stats (sections, merge fields, vitec-if count, foreach count, etc.)
- Validation result
- Fixes applied (both manual and post-processor)
- Potential issues and uncertainties
- Known limitations
- Pipeline execution summary

## STEP 3 (legacy): Direct Pipeline Execution

For cases where subagents are not available or for simple tasks, follow `AGENT-2B-PIPELINE-DESIGN.md`
stages S1-S10 directly. This is the fallback path.

---

## Quick Reference

### Template Shell

```html
<div id="vitecTemplate">
<span vitec-template="resource:Vitec Stilark">&nbsp;</span>
<style type="text/css">
  /* Full CSS block — counters, headings, tables, lists, checkboxes, inserts
     See PRODUCTION-TEMPLATE-PIPELINE.md Section 3 (complete block) + Section 7 (SVG checkbox CSS) */
</style>
<table>
  <tbody>
    <tr>
      <td colspan="100" style="text-align:right">
        <small>
          Meglerforetakets org.nr: <strong>[[meglerkontor.orgnr]]</strong><br />
          Oppdragsnr.:&nbsp;<strong>[[oppdrag.nr]]</strong><br />
          Omsetningsnr.:&nbsp;<strong>[[kontrakt.formidling.nr]]</strong>
        </small>
      </td>
    </tr>
    <tr><td colspan="100">&nbsp;</td></tr>
    <tr>
      <td colspan="100">
        <h1>Template Title Here</h1>
        <!-- All body content inside this cell -->
      </td>
    </tr>
  </tbody>
</table>
</div>
```

**Important:** Do NOT add `class="proaktiv-theme"` to the root div. No reference template uses it.

### Merge Field Syntax

| Syntax | Usage |
|--------|-------|
| `[[field.path]]` | Standard merge field |
| `[[*field.path]]` | Required field (inside vitec-foreach only) |
| `$.UD([[field]])` | Number formatting (thousand separators) — **mandatory for all monetary values** |

### Conditional Logic

```html
<span vitec-if="Model.eiendom.grunntype == &quot;Bolig&quot;">Boligen</span>
```

Escaping: `"` → `&quot;`, `>` → `&gt;`, `<` → `&lt;`, `&&` → `&amp;&amp;`

For Norwegian characters inside condition string values, use unicode escapes:
`ø` → `\xF8`, `å` → `\xE5`, `æ` → `\xE6`, `Ø` → `\xD8`

Example: `vitec-if="Model.oppdrag.hovedtype == &quot;Oppgj\xF8rsoppdrag&quot;"`

### Party Loops (with required guard + fallback)

```html
<div vitec-if="Model.selgere.Count &gt; 0">
  <table class="roles-table">
    <tbody vitec-foreach="selger in Model.selgere">
      <tr><td>[[*selger.navnutenfullmektigogkontaktperson]]</td></tr>
    </tbody>
  </table>
</div>
<div vitec-if="Model.selgere.Count == 0">
  <p>[Mangler selger]</p>
</div>
```

**Every foreach needs BOTH a guard AND a fallback.** No exceptions.

### Checkboxes (SVG Pattern — mandatory)

Never use Unicode characters `&#9744;`/`&#9745;` — they render as "?" in Vitec PDF.

Two distinct patterns depending on who controls the checkbox state:

**Broker-interactive checkboxes** (user toggles in CKEditor):
```html
<label class="btn" contenteditable="false" data-toggle="button">
  <span class="checkbox svg-toggle"></span>
</label>
```

**Data-driven checkboxes** (system sets state via vitec-if — NO `<input>` tag):
```html
<span vitec-if="condition is true">
  <label class="btn active" contenteditable="false" data-toggle="button">
    <span class="checkbox svg-toggle"></span>
  </label>
</span>
<span vitec-if="condition is false">
  <label class="btn" contenteditable="false" data-toggle="button">
    <span class="checkbox svg-toggle"></span>
  </label>
</span>
```

**Key distinction:** Data-driven checkboxes omit `<input type="checkbox" />` because:
- Vitec PDF conversion is flat — form fields don't survive
- Hidden inputs could cause future Stilark conflicts
- The system sets state through vitec-if, not user interaction

The SVG checkbox CSS block must be included in the template `<style>`. See `PRODUCTION-TEMPLATE-PIPELINE.md` Section 7 for the complete CSS.

### Page Break Controls (mandatory for T3+)

Vitec's PDF renderer splits content at arbitrary points unless explicitly controlled.

**CSS rule (required in style block):**
```css
#vitecTemplate .avoid-page-break { page-break-inside: avoid; }
```

**Short sections** (1-4 paragraphs) — add class directly to article:
```html
<article class="avoid-page-break item">
  <h2>HEADING</h2>
  <p>Content...</p>
</article>
```

**Long sections** — wrap heading + key content blocks in internal divs:
```html
<article class="item">
  <div class="avoid-page-break">
    <h2>HEADING</h2>
    <p>First paragraph that must stay with heading...</p>
    <table><!-- table that must stay together --></table>
  </div>
  <p>Remaining content can break naturally...</p>
  <div class="avoid-page-break">
    <p>Another group that should stay together...</p>
  </div>
</article>
```

**Forced page breaks** — use sparingly at major transition points:
```html
<article class="item" style="page-break-before: always;">
```

**Where to apply (golden standard patterns):**
- Heading + first 1-2 paragraphs of each section
- Financial tables (costs-table, roles-table)
- Checkbox groups with their labels
- Bullet/numbered lists
- Signature blocks
- Short sections (entire article)

**Minimum coverage:** At least half the article sections should have page break protection. Golden standard templates use 20-30 wrappers per document.

### Insert Fields (with data-label) — Chromium Fix

```html
<span class="insert-table"><span class="insert" data-label="dato"></span></span>
```

The `data-label` attribute shows placeholder text (e.g., "dato", "beløp") in the CKEditor.
The `.insert-table { display: inline-table }` CSS is the **Chromium-compatible fix** — critical
for correct rendering in both Vitec's Chromium-based editor and PDF output.

**Required CSS** (UNSCOPED — no `#vitecTemplate` prefix):
```css
span.insert:empty { font-size: inherit !important; line-height: inherit !important; display: inline-block; background-color: lightpink; min-width: 2em !important; height: .7em !important; text-align: center; }
span.insert:empty:before { content: attr(data-label); }
span.insert:empty:hover { background-color: #fff; cursor: pointer; }
.insert-table { display: inline-table; }
.insert-table > span, .insert-table > span.insert { display: table-cell; }
```
See PATTERNS.md section 3 for full formatted version.

### Entity Encoding (mandatory)

All Norwegian characters in template text content MUST be HTML entities, never literal UTF-8.
Literal characters cause mojibake in Vitec PDF rendering.

| Character | Entity |
|-----------|--------|
| ø | `&oslash;` |
| å | `&aring;` |
| æ | `&aelig;` |
| Ø | `&Oslash;` |
| Å | `&Aring;` |
| Æ | `&AElig;` |
| § | `&sect;` |
| « | `&laquo;` |
| » | `&raquo;` |
| – | `&ndash;` |
| — | `&mdash;` |
| é | `&eacute;` |

### Source Clue Recognition

| Source Pattern | Action |
|---------------|--------|
| `#field.context¤` | Map to `[[modern.field]]` |
| Wingdings + `q` | → SVG checkbox pattern (see above) |
| `color:red` text | → `vitec-if` branch |
| "Alt 1:" / "Alt 2:" | → `vitec-if` div blocks |
| "Boligen/fritidsboligen" | → `grunntype` condition |
| "1 A" / "1 B" headers | → `eieform` condition |
| `…………` or underlines | → `<span class="insert-table"><span class="insert" data-label="..."></span></span>` |

---

## Utility Scripts

| Script | Usage |
|--------|-------|
| `scripts/tools/validate_vitec_template.py` | `python scripts/tools/validate_vitec_template.py template.html --tier 4` |
| `scripts/tools/post_process_template.py` | `python scripts/tools/post_process_template.py template.html --in-place` |
| `scripts/tools/build_preview.py` | Visual preview with Stilark CSS |
| `scripts/tools/monthly_diff.py` | Monthly release diff: `python scripts/tools/monthly_diff.py` |
| `scripts/tools/mine_template_library.py` | Re-mine library for KB patterns: `python scripts/tools/mine_template_library.py` |
| `scripts/tools/build_template_library.py` | Rebuild master library from export JSON |

## Output Locations

| File | Location |
|------|----------|
| Build script | `scripts/build_{template_name}.py` |
| Production HTML | `scripts/production/{name}_PRODUCTION.html` |
| Handoff summary | `scripts/handoffs/{name}_HANDOFF.md` |
| Snapshot (Mode A) | `scripts/snapshots/{name}_SNAPSHOT.html` |
| PDF artifact (T3-T5) | `scripts/qa_artifacts/{name}_testfletting.pdf` |

## Live Verification (T3-T5, Mode B/C)

**Test system:** `https://proatest.qa.vitecnext.no`
**Credentials:** `VITEC_TEST_USER` / `VITEC_TEST_PASSWORD` in `backend/.env`
**Test property:** Solåsveien 30

Process: Create test template → paste HTML → Testfletting → PDF inspect → download → delete.
See `AGENT-2B-PIPELINE-DESIGN.md` S9 for full 12-step procedure and failure triage.

## Database Access

```sql
-- MCP tool: user-postgres, tool: query
SELECT title, content FROM templates tmpl
JOIN template_tags tt ON tmpl.id = tt.template_id
JOIN tags t ON tt.tag_id = t.id
WHERE t.name = 'Vitec Next'
AND title LIKE '%search_term%'
ORDER BY LENGTH(content) DESC LIMIT 1
```

## Quality Checklist

- [ ] `<div id="vitecTemplate">` wrapper (NO `class="proaktiv-theme"`)
- [ ] `<span vitec-template="resource:Vitec Stilark">&nbsp;</span>`
- [ ] Outer `<table>` body wrapper with `<small>` header info
- [ ] `<h1>` for template title (not `<h5>` or other levels)
- [ ] CSS block includes counters + SVG checkbox + insert field styles (T3+)
- [ ] Counter `::before` uses content-only pattern (no `display`/`width` overrides)
- [ ] Article `padding-left: 20px` matches h2 `margin-left: -20px` (heading/body alignment)
- [ ] All `<article class="item">` with `<h2>` headings (T3+)
- [ ] No legacy `#field¤` syntax remaining
- [ ] All `vitec-if` use `&quot;` for quotes
- [ ] All `vitec-foreach` have collection guards AND fallback placeholders
- [ ] `roles-table` on party tables
- [ ] `costs-table` on financial tables
- [ ] Signature block with signing lines (T3+)
- [ ] `insert-table` + `span.insert` with `data-label` for fill-in fields
- [ ] `.insert-table { display: inline-table }` CSS present (Chromium fix)
- [ ] Article padding `20px`, H2 margin-left `-20px` (production standard)
- [ ] All Norwegian characters are HTML entities (`&oslash;`, `&aring;`, etc.) — NO literal UTF-8
- [ ] No Unicode checkboxes (`&#9744;`/`&#9745;`) — SVG checkboxes only
- [ ] Data-driven checkboxes have NO `<input>` tag — broker-interactive checkboxes may
- [ ] All monetary merge fields wrapped in `$.UD()`
- [ ] Page break CSS rule present: `#vitecTemplate .avoid-page-break { page-break-inside: avoid; }` (T3+)
- [ ] Short sections have `class="avoid-page-break item"` on article (T3+)
- [ ] Long sections have `<div class="avoid-page-break">` around heading + key content (T3+)
- [ ] Signature block has `avoid-page-break` wrapper (T3+)
- [ ] Forced page breaks at natural transition points (T4+)
- [ ] No inline `font-family` or `font-size`
- [ ] Static validation: `scripts/tools/validate_vitec_template.py` all checks PASS
- [ ] Live verification: PASS or data gap documented (T3-T5)
- [ ] PDF artifact saved (T3-T5)
- [ ] Database commit confirmed

## Rules

- Legal text must be **verbatim** from source — never paraphrase
- All merge fields use `[[field.path]]` — no legacy `#field¤`
- All `vitec-if` use HTML entity escaping (`&quot;`, `&gt;`, `&lt;`, `&amp;&amp;`)
- All `vitec-foreach` have guards AND fallbacks
- All Norwegian characters must be HTML entities — never literal UTF-8
- All monetary merge fields must use `$.UD()` wrapper
- All checkboxes must use SVG pattern — never Unicode `&#9744;`/`&#9745;`
- Data-driven checkboxes (vitec-if controlled) must NOT include `<input type="checkbox" />`
- All insert fields must use `insert-table` wrapper with `data-label`
- T3+ templates must have `avoid-page-break` wrappers on headings, tables, and short sections
- T4+ templates should have forced page breaks at major document transitions
- Norwegian characters in `vitec-if` string values use `\xF8`/`\xE5`/`\xE6` escapes
- If a field mapping is unclear, **ask** — don't guess
