# AGENT-2B Pipeline Design — Vitec Next Template Build Pipeline

## Purpose

This document is the **authoritative specification** for the template build pipeline. It defines
how templates enter the pipeline, how they are classified, how they are built, how they are
validated, how they are verified against the live Vitec system, and how they are committed to the
database. Every decision is explicit. The building agent follows this document — it does not make
judgment calls.

**Companion documents:**
- `PRODUCTION-TEMPLATE-PIPELINE.md` — Knowledge base (field mappings, patterns, CSS, source clues)
- `AGENT-2B-TEMPLATE-BUILDER.md` — Agent task specification (process steps, output format)
- `.agents/skills/vitec-template-builder/SKILL.md` — Agent skill (quick reference, invocation trigger)
- `.planning/POST-REVIEW-ADDITIONS.md` — Review items incorporated into this document

---

## S0 — Intake Questionnaire

Every pipeline run begins with a structured intake. The agent asks the user these questions
before reading any reference files, loading any context, or writing any code.

### Question 1: Operational Mode

| Mode | Description | When to use |
|------|-------------|-------------|
| **A1** | Edit/Update (user-requested change) | User asks to modify a template that is currently in production |
| **A2** | Edit/Update (Vitec reconciliation) | A Vitec system update changed a base template and we need to reconcile with our customizations |
| **B** | Convert/Migrate | An existing document from a different format (Word, old system) needs to become a Vitec Next template |
| **C** | Create New | A brand new template needs to be built to fill a new need, using our ruleset and existing templates as structural reference |

### Question 2: Complexity Tier

| Tier | Type | Examples | Section J checks | Live Verification |
|------|------|----------|-------------------|-------------------|
| **T1** | Plain text | SMS templates | Skip | Skip |
| **T2** | Simple HTML | Email templates, simple notices | Skip | Skip |
| **T3** | Structured document | Letters, simple agreements | Run | Run |
| **T4** | Complex contract | Kjøpekontrakt, Oppdragsavtale | Run | Run |
| **T5** | Interactive form | Multi-party contracts with dynamic sections | Run | Run |

### Question 3: Scope (Mode A only)

For Mode A (Edit/Update), the agent asks:
- Which template? (name or ID)
- What is the specific change requested? (A1) / Which Vitec update version? (A2)
- Risk classification: **cosmetic** (text/label changes), **structural** (section reordering,
  new conditions), or **critical** (party loops, merge field changes, conditional logic changes)

### Spec Sheet

After the questionnaire, the agent produces a spec sheet and presents it for user confirmation:

```
MODE: [A1/A2/B/C]
TIER: [T1-T5]
TEMPLATE: [name]
SCOPE: [description of work]
RISK: [cosmetic/structural/critical] (Mode A only)
FILES TO READ: [list based on mode + tier]
STAGES TO EXECUTE: [S1-S10 (builder scope), S11-S12 handled separately]
```

The agent does NOT proceed until the user confirms the spec sheet.

### Context Loading (Two-Phase)

**Phase 1 (before spec sheet):** Only the questionnaire section of the SKILL.md is read. No
reference files, no ruleset, no field registry.

**Phase 2 (after spec sheet confirmation):** Load context based on confirmed mode + tier:

| Context | T1 | T2 | T3 | T4 | T5 | Mode A |
|---------|----|----|----|----|----|---------| 
| `PRODUCTION-TEMPLATE-PIPELINE.md` | - | Sections 2,4 | Full | Full | Full | Sections 4,5,6 |
| Ruleset section files (see below) | 00 only | 00,01 | 00,01,04,06 | 00,01,04,06,07,10 | All | By scope |
| `field-registry.md` | - | Relevant group | Relevant groups | Full | Full | Changed fields |
| `Alle-flettekoder-25.9.md` | - | - | On demand | On demand | On demand | On demand |
| Existing template (DB query) | - | - | If variant | If variant | If variant | Always |

---

## S1 — Source Analysis

### Mode B/C

Read the source document (`.htm`, `.docx`, or `.rtf`). Produce a **Source Analysis Report**:

- Total sections/articles identified
- All legacy merge fields found (`#field.context¤`)
- All Wingdings checkboxes (`font-family:Wingdings` + `q`)
- All red text conditional markers (`color:red`)
- All alternative sections (1A/1B, Alt 1/Alt 2)
- All tables and their purposes (content, party listing, cost, layout)
- Signature block location and structure

### Mode A

Read the current production template from the database. Produce a **Change Impact Report**:

- Current merge field inventory (count and list)
- Current vitec-if condition inventory
- Current vitec-foreach loop inventory
- Specific elements affected by the requested change
- Risk assessment: which existing functionality could be affected

**Mode A safety:** Before any edit, save the current template as a snapshot:
```
scripts/snapshots/{template_name}_SNAPSHOT_{timestamp}.html
```

---

## S2 — Field Mapping

### Mode B/C

For every legacy merge field found in S1:

1. Look up in `PRODUCTION-TEMPLATE-PIPELINE.md` Section 4
2. If not found, search `field-registry.md`
3. If still not found, search `Alle-flettekoder-25.9.md`
4. If still not found, query the database for similar templates
5. If still unmapped, flag for user confirmation — do NOT guess

### Mode A

Only map fields that are part of the change scope. Do not touch fields outside scope.

---

## S3 — Structural Planning

### Mode B/C

Before building, decide:

- Which sections become numbered `<article class="item">` elements
- Which alternative sections need `vitec-if` branching (Section 5 patterns)
- Which party listings need `vitec-foreach` loops (Section 6 patterns)
- Which tables are `roles-table`, `costs-table`, or layout
- Which checkboxes become auto-checked (SVG checkbox with `vitec-if` for active/inactive state)

### Mode A

Structural planning is limited to the change scope. The agent documents:
- Which elements will be modified
- Which elements are adjacent and must not be affected
- Whether the change requires new conditions, loops, or fields

### Construction Rules (All Modes)

**Rule 1: Every collection must have a guard AND a fallback.**

No `vitec-foreach` loop may exist without both:
1. A `vitec-if="{collection}.Count > 0"` wrapper on the parent element
2. A sibling `vitec-if="{collection}.Count == 0"` element containing a Norwegian
   placeholder in the format `[Mangler {rolle}]`

This applies to all party collections (`selgere`, `kjopere`, `fullmektiger`, `advokater`, etc.)
and all dynamic lists.

```html
<!-- CORRECT — guarded with fallback -->
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

<!-- WRONG — will crash if collection is empty -->
<tbody vitec-foreach="selger in Model.selgere">
  <tr><td>[[*selger.navnutenfullmektigogkontaktperson]]</td></tr>
</tbody>
```

A template that crashes on missing data is **incomplete** regardless of how correct the HTML
structure is. This is a hard rule, not a suggestion.

**Rule 2: All legal text must be verbatim from the source document.** No paraphrasing.

**Rule 3: All vitec-if expressions must use HTML entity escaping.** See
`PRODUCTION-TEMPLATE-PIPELINE.md` Section 5 for the escaping table.

**Rule 4: All merge fields inside vitec-foreach must use the asterisk prefix** (`[[*field]]`).

**Rule 5: All Norwegian characters in template text content must be HTML entities.**

Never use literal UTF-8 Norwegian characters in the template HTML. Vitec's PDF renderer
does not handle UTF-8 correctly and produces mojibake (`Ã¸`, `Ã¥`, `Â§`).

| Character | Entity | Character | Entity |
|-----------|--------|-----------|--------|
| ø | `&oslash;` | Ø | `&Oslash;` |
| å | `&aring;` | Å | `&Aring;` |
| æ | `&aelig;` | Æ | `&AElig;` |
| § | `&sect;` | « | `&laquo;` |
| » | `&raquo;` | – | `&ndash;` |
| — | `&mdash;` | é | `&eacute;` |

This applies to ALL text content in the template — legal text, labels, headings, placeholders.
Merge field paths (`[[field.path]]`) are NOT affected — they use ASCII identifiers.

**Rule 6: All checkboxes must use the SVG checkbox pattern.**

Never use Unicode characters `&#9744;`/`&#9745;` for checkboxes. They render as "?" in
Vitec PDF output. The standard Vitec pattern uses `label.btn` + `span.checkbox.svg-toggle`
with SVG data URIs defined in CSS.

```html
<!-- Unchecked -->
<label class="btn" contenteditable="false" data-toggle="button">
  <input type="checkbox" /><span class="checkbox svg-toggle"></span>
</label>

<!-- Checked (active) -->
<label class="btn active" contenteditable="false" data-toggle="button">
  <input type="checkbox" /><span class="checkbox svg-toggle"></span>
</label>
```

For conditional auto-check (data-driven checkboxes), wrap in paired `vitec-if` blocks:
```html
<span vitec-if="condition is true">
  <label class="btn active" contenteditable="false" data-toggle="button">
    <input type="checkbox" /><span class="checkbox svg-toggle"></span>
  </label>
</span>
<span vitec-if="condition is false">
  <label class="btn" contenteditable="false" data-toggle="button">
    <input type="checkbox" /><span class="checkbox svg-toggle"></span>
  </label>
</span>
```

The required SVG checkbox CSS block is in `PRODUCTION-TEMPLATE-PIPELINE.md` Section 7.
Include it in the template `<style>` alongside the counter CSS.

---

## S4 — Template Shell

Wrap content in the Vitec template shell:

1. `<div id="vitecTemplate">` — NO `class="proaktiv-theme"` (no reference template uses it)
2. `<span vitec-template="resource:Vitec Stilark">&nbsp;</span>`
3. `<style>` block with **complete CSS** from `PRODUCTION-TEMPLATE-PIPELINE.md` Section 3:
   - CSS counters (section/subsection dual-counter)
   - Heading styles (h1 centered 14pt, h2 11pt with negative margin, h3 10pt)
   - Table base styles (`width:100%; table-layout:fixed`) and `.borders` class
   - `roles-table`, `costs-table`, `insert` field CSS
   - `ul`/`li` list styles, `a.bookmark`, `.liste .separator`
   - SVG checkbox CSS (from Section 7)
   - Insert field CSS (from Section 7)
4. Outer `<table>` body wrapper with header info row:
   ```html
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
   ```
5. `<h1>` for the template title (not `<h5>` or other levels)
6. Sections as `<article class="item">` with `<h2>` headings
7. 100-unit colspan system for table layouts
8. `roles-table` and `costs-table` CSS classes
9. `avoid-page-break` on signature section
10. `insert-table` + `span.insert` with `data-label` for user fill-in fields

For Mode A, this stage is skipped — the shell already exists.

---

## S5 — Template Construction

### Mode B/C

Create a Python build script at `scripts/build_{template_name}.py` that generates the template.
The script approach is preferred because it is version-controllable, reviewable section by
section, and re-runnable after modifications.

Output: `scripts/production/{template_name}_PRODUCTION.html`

**Mandatory post-processing:** As the final step of the build script, run entity encoding
on all text content. Replace every literal Norwegian character with its HTML entity equivalent
(Rule 5). This must happen AFTER all content is assembled, so no literal characters can
slip through from any source (legal text, labels, headings).

### Mode A

Apply the change directly to the template HTML. Changes must be surgical — modify only the
elements in scope. The agent must not reformat, re-indent, or restructure content outside the
change scope.

**If the existing template contains literal Norwegian characters**, convert them to entities
as part of the change. This is a non-breaking correctness fix and is always in scope.

---

## S6 — Static Validation

Run the unified validator:

```bash
python scripts/tools/validate_vitec_template.py scripts/production/{name}_PRODUCTION.html --tier {N}
```

For Mode A with a snapshot:

```bash
python scripts/tools/validate_vitec_template.py scripts/production/{name}_PRODUCTION.html --tier {N} --compare-snapshot scripts/snapshots/{name}_SNAPSHOT.html
```

### Validation Check Groups

| Group | Checks | T1/T2 | T3+ |
|-------|--------|-------|-----|
| A. Template Shell | 5 | Run | Run |
| B. Table Structure | 3 | Run | Run |
| C. Inline Styles | 2 | Run | Run |
| D. Merge Fields | 3 | Run | Run |
| E. Conditional Logic | 3 | Run | Run |
| F. Iteration (guards + fallbacks) | 2 + 2N (N = foreach count) | Run | Run |
| G. Images | 1 | Run | Run |
| H. Form Elements | 1 | Run | Run |
| I. Text and Formatting | 5 | Run | Run |
| J. Contract-Specific | 8 | **Skip** | Run |
| K. Final Validation | 4 | Run | Run |
| SNAPSHOT (Mode A only) | 4 | Run | Run |

**Gate:** All checks must PASS. Any FAIL blocks progression to S7.

Fix failures before proceeding. If a failure is a false positive for the template type (e.g.
"Has vitec-foreach loops" for a simple letter that genuinely has no loops), document the
exception in the handoff report.

---

## S7 — Visual Preview

Generate a visual preview:

```bash
python scripts/tools/build_preview.py
```

(Update the source path in the script)

Open the preview HTML in a browser and verify:
- Section numbering renders correctly
- Tables are properly structured
- Merge fields are visible (highlighted in preview)
- Conditions and loops are annotated
- Signature block is at the bottom

---

## S8 — Content Verification

If the original PDF or source document is available, compare section by section:

- All sections present and in correct order
- All legal text is verbatim (no paraphrasing)
- All fill-in blanks converted to `span.insert`
- All checkboxes converted to auto-check or static
- No content accidentally omitted

For Mode A: verify that only the intended change was applied and no other content was affected.
Use the `--compare-snapshot` output from S6 to confirm.

---

## S10 — Builder Handoff

The builder agent's final stage is to deliver the production HTML and a handoff summary.
The builder does **NOT** upload to Vitec Next, run live verification, or commit to the database.
Those are separate downstream steps handled by other agents or the user.

### Builder Deliverables

| File | Path (relative to workspace root) |
|------|-----------------------------------|
| Build script | `scripts/build_{name}.py` (Mode B/C) |
| Production HTML | `scripts/production/{name}_PRODUCTION.html` |
| Handoff summary | `scripts/handoffs/{name}_HANDOFF.md` |

### Handoff Summary Contents

The handoff `.md` file must contain:

1. **Spec** — Mode, Tier, Template name, Scope
2. **Production File** — Path, size, build script path
3. **Template Stats** — Section count, merge field count + list, vitec-if count,
   vitec-foreach count + list, insert field count, SVG checkbox count
4. **Validation Result** — Full output of `validate_vitec_template.py --tier N`
5. **Fixes Applied** — One-line summary per fix
6. **Potential Issues & Uncertainties** — Guessed field mappings, ambiguous legal text,
   sections adapted from other templates, unverified merge field paths, structural choices
   that differ from the reference
7. **Content Notes** — Source document sections used, payment model details, guarantee provisions
8. **Known Limitations** — CKEditor behavior differences, data availability dependencies,
   untestable conditional branches
9. **Recommendations** — Sections to review, suggested test properties, follow-up work

### What Happens After Builder Handoff

The handoff summary and production HTML are reviewed by:
- **Analysis agent** — Runs structural comparison, validates against reference templates
- **Human review** — Reads handoff notes, checks flagged uncertainties
- **Live verification** (S11) — Separate step, done manually or by a dedicated QA agent
- **Database commit** — Done after live verification passes

---

## S11 — Live Verification (Separate from Builder)

> This stage is NOT part of the builder agent's scope. It is documented here for the
> overall pipeline reference.

**Skip conditions:**
- T1/T2 templates (static validation is sufficient)
- Mode A templates (already live in Vitec)

### Environment

- **Test system URL:** `https://proatest.qa.vitecnext.no` (from `VITEC_TEST_URL` in `backend/.env`)
- **Auth:** Chrome session via MCP browser (`cursor-ide-browser`)
- **Default test property:** Solåsveien 30

### Process (12 steps)

```
Step 1:  Navigate to VITEC_TEST_URL
Step 2:  Handle auth (login if needed)
Step 3:  Navigate to Document Templates
Step 4:  Create a new blank template named "[TEST] {template_name}_VERIFY"
Step 5:  Open the HTML source editor, paste the full production HTML
Step 6:  Save the template
Step 7:  Click the "Testfletting" button
Step 8:  Confirm "Solåsveien 30" is loaded as the OBJEKT
Step 9:  Observe the result (see Failure Triage below)
Step 10: Click the magnifying glass icon → visual PDF inspection
Step 11: Download the PDF → save to scripts/qa_artifacts/{template_name}_testfletting.pdf
Step 12: Delete the [TEST] template to keep the QA system clean
```

### Failure Triage (3 types)

| Type | Indicator | Action |
|------|-----------|--------|
| **Type 1: Template code failure** | Structural crash, blank document | Export saved-back HTML, diff against input, return to builder |
| **Type 2: Unguarded collection** | Null reference, missing section | Add guard + fallback, return to builder |
| **Type 3: Data gap** | Template correct, test property lacks entity | Flag in notes — NOT a template bug |

---

## S12 — Database Commit (Separate from Builder)

> This stage is NOT part of the builder agent's scope.

**New template (Mode B/C):**
```
POST /api/templates
Content-Type: multipart/form-data
Fields: file (HTML), title, description, status, auto_sanitize
```

**Update existing (Mode A):**
```
PUT /api/templates/{template_id}/content
Body: { "content": "<html>" }
```

| Condition | Status |
|-----------|--------|
| All stages pass including S11 | `published` |
| S11 Type 3 data gap | `pending_live_verification` |
| S11 unreachable | `pending_live_verification` |

---

## Mode A — Edit/Update Safety Protocol

### A1: User-Requested Change

1. Save pre-edit snapshot
2. Classify change risk (cosmetic / structural / critical)
3. Apply change surgically — modify ONLY the elements in scope
4. Run validator with `--compare-snapshot` to detect regressions
5. The snapshot comparison checks:
   - No merge fields lost
   - No vitec-if conditions lost
   - No vitec-foreach loops lost
   - Article count unchanged or increased

### A2: Vitec Update Reconciliation

When Vitec releases a system update that modifies a base template we've customized:

1. Obtain three versions:
   - **Original:** The Vitec template before our customization (from git history or snapshots)
   - **Ours:** Our current customized version (from database)
   - **Theirs:** The new Vitec version (from the Vitec system)
2. Use `TemplateComparisonService` to produce structural diffs:
   - Original → Ours (our changes)
   - Original → Theirs (Vitec's changes)
3. Merge non-conflicting changes automatically
4. Flag conflicts for user review

**Escape hatch:** If the three-way merge produces more than 40% conflicting elements,
the templates are "too diverged" for merging. Present the user with options:
- Proceed with manual conflict resolution (may take longer than rebuilding)
- Reclassify as Mode C (build new template using the new Vitec version as source)
- Keep our version and ignore the Vitec update

---

## Token Optimization Strategy

### Ruleset Section Files

The `vitec-html-ruleset.md` (4,087 lines) is split into section files under
`.planning/vitec-html-ruleset/`:

```
00-preamble.md
01-template-shell.md
02-images-svg.md
03-text-formatting.md
04-tables.md
05-inline-styles.md
06-merge-fields.md
07-conditional-logic.md
08-form-elements.md
09-iteration.md
10-ckeditor-acf.md
11-failure-modes.md
12-conversion-checklist.md
13-appendix-stilark.md
14-no-touch-templates.md
```

The original file is renamed to `vitec-html-ruleset-FULL.md` as an archive. Agents load only
the section files relevant to their current tier and mode (see S0 Context Loading table).

### Field Registry

A structured `field-registry.md` (~200 lines) is extracted from `Alle-flettekoder-25.9.md`
(6,494 lines). This registry contains:
- Field path
- Display name (Norwegian)
- Data type
- Typical usage context (contract/letter/email)
- Notes (required field, formatting functions, collection membership)

The full `Alle-flettekoder-25.9.md` is only loaded on demand when a field is not found in the
registry.

### Expected Token Savings

| File | Before | After | Saving |
|------|--------|-------|--------|
| `vitec-html-ruleset.md` | ~15,000 tokens (full) | ~2,000–6,000 tokens (relevant sections) | 60–87% |
| `Alle-flettekoder-25.9.md` | ~25,000 tokens (full) | ~800 tokens (registry) | 97% |
| Total per agent run | ~45,000 tokens baseline | ~5,000–10,000 tokens | 78–89% |

---

## Pipeline Architecture

```
S0  → Intake Questionnaire (Mode + Tier + Scope)
       ↓
S1  → Source Analysis (or Change Impact Report for Mode A)
       ↓
S2  → Field Mapping
       ↓
S3  → Structural Planning + Construction Rules
       ↓
S4  → Template Shell (skip for Mode A)
       ↓
S5  → Template Construction
       ↓
S6  → Static Validation (validate_vitec_template.py --tier N)
       ↓
S7  → Visual Preview
       ↓
S8  → Content Verification
       ↓
S10 → Builder Handoff (production HTML + handoff .md)
       ↓ ════════════ BUILDER SCOPE ENDS HERE ════════════
S11 → Live Verification [separate step, not builder's job]
       ↓
S12 → Database Commit [separate step, not builder's job]
```

---

## Future Opportunity: PDF Thumbnail as Dashboard Cover

Out of scope for the current pipeline. Flagged for a future phase.

The Testfletting-generated PDF (saved in `scripts/qa_artifacts/`) is a more accurate
representation of the template than the current `build_preview.py` output, because it is
rendered by Vitec's actual engine. A future enhancement could:

1. Extract a thumbnail from page 1 of the Testfletting PDF (e.g. via `pdf2image`)
2. Store the thumbnail and link it to the template record as `preview_url`
3. The `preview_url` field already exists on the Template model — no schema change required

The current pipeline saves the PDF artifact to `scripts/qa_artifacts/` specifically so it is
available for this extraction when the feature is implemented.
