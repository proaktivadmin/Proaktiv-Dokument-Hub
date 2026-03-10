# Builder Agent Prompt: Fix Leilighet Production Template

## Task

Fix the "Kjøpekontrakt prosjekt (leilighet med delinnbetalinger)" production template to pass
all quality checks identified in the analysis report. Validate with the unified validator,
then deliver a finished production HTML file and a handoff summary document.

## Context

A deep analysis compared our generated templates against three working Vitec reference templates,
including both code-level and **visual browser-rendered comparison**. The analysis found:
- **2 critical rendering-breaking issues** (PDF mojibake from literal UTF-8, Unicode checkboxes as "?")
- **Several important structural deviations** (missing CSS heading rules, incomplete style block)
- **A content mismatch** (wrong payment model — enebolig's instead of selveier's)
- **Visual inconsistencies** (missing fullmektig section, wrong column headers, incomplete base CSS)
The full report is at `.planning/phases/11-template-suite/TEMPLATE-ANALYSIS-REPORT.md`.

The pipeline documents have been updated with corrected rules. You must follow them.

## Files to Read (in order)

### 1. Pipeline documents (rules and patterns)
Read these FIRST — they contain the corrected rules:

1. `.planning/phases/11-template-suite/AGENT-2B-PIPELINE-DESIGN.md` — Pipeline design with Rules 1-6
2. `.planning/phases/11-template-suite/PRODUCTION-TEMPLATE-PIPELINE.md` — Knowledge base with Section 7 (Reference Patterns Library)
3. `.agents/skills/vitec-template-builder/SKILL.md` — Quick reference for entity encoding, SVG checkboxes, insert patterns

### 2. Analysis report (what went wrong)
4. `.planning/phases/11-template-suite/TEMPLATE-ANALYSIS-REPORT.md` — Full findings and evidence

### 3. Primary reference template (gold standard)
5. `C:\Users\Adrian\Downloads\kjøpekontrakt bruktbolig html.html` — Working Vitec production contract

### 4. Current leilighet template (to be fixed)
6. `C:\Users\Adrian\Documents\Proaktiv-Dokument-Hub\scripts\converted_html\Kjopekontrakt_prosjekt_leilighet_PRODUCTION.html`
   (Read from this location. Your fixed version will be written to the workspace — see Deliverables.)

### 5. Current leilighet build script (to be fixed)
7. `C:\Users\Adrian\Documents\Proaktiv-Dokument-Hub\scripts\build_kjopekontrakt_prosjekt_leilighet.py`
   (Read from this location. Your fixed version will be written to the workspace — see Deliverables.)

### 6. Enebolig pilot (for consistency reference)
8. `scripts/converted_html/Kjopekontrakt_prosjekt_enebolig_PRODUCTION.html` — Our pilot template (better structure than leilighet)

### 7. Word source document
9. `C:\Users\Adrian\Downloads\8966142_3.htm` — Original Word-exported HTML for this template

## Spec Sheet

```
MODE: B (Convert/Migrate — fixing a failed conversion)
TIER: T4 (Complex contract)
TEMPLATE: Kjøpekontrakt prosjekt (leilighet med delinnbetalinger)
SCOPE: Fix all critical and important issues from analysis report
RISK: N/A (Mode B)
```

## Required Fixes (ordered by severity)

### CRITICAL — Must fix for PDF rendering

#### Fix 1: Entity Encoding (Analysis D1)
Replace ALL literal Norwegian characters in template text content with HTML entities.

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

This must be done as a post-processing step on ALL text content. Merge field paths
(`[[field.path]]`) use ASCII and are not affected.

**Implementation:** In the build script, add entity encoding as the final step before writing
the output file. Use a simple character replacement on the final HTML string. Be careful NOT to
encode characters inside `vitec-if` and `vitec-foreach` attribute values — those use `\xHH`
escape format for Norwegian characters (e.g., `\xF8` for ø). A simple string replacement on
the full HTML is safe because our attribute values currently don't contain literal Norwegian
characters.

#### Fix 2: SVG Checkboxes (Analysis D2)
Replace ALL Unicode checkbox characters (`&#9744;`/`&#9745;`) with the SVG checkbox pattern.

**Unchecked:**
```html
<label class="btn" contenteditable="false" data-toggle="button">
  <input type="checkbox" /><span class="checkbox svg-toggle"></span>
</label>
```

**Checked (active):**
```html
<label class="btn active" contenteditable="false" data-toggle="button">
  <input type="checkbox" /><span class="checkbox svg-toggle"></span>
</label>
```

**Conditional auto-check (most checkbox instances in our template):**
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

Add the SVG checkbox CSS block to the template `<style>`. The complete CSS is in
`PRODUCTION-TEMPLATE-PIPELINE.md` Section 7.

### IMPORTANT — Must fix for structural correctness

#### Fix 3: Remove `class="proaktiv-theme"` (Analysis D0/D3)
Change `<div class="proaktiv-theme" id="vitecTemplate">` to `<div id="vitecTemplate">`.
No reference template uses this class.

#### Fix 4: Fix title from `<h5>` to `<h1>` (Analysis D0)
Change `<h5 style="text-align:center;">KJØPEKONTRAKT</h5>` to `<h1>Kj&oslash;pekontrakt</h1>`.
Match the reference template pattern. The Stilark CSS handles the centering.

#### Fix 5: Add outer `<table>` body wrapper (Analysis D0/D3)
Wrap the template body in the outer table pattern. See `PRODUCTION-TEMPLATE-PIPELINE.md`
Section 7 "Outer Table Body Wrapper" for the exact HTML.

The header should include:
- Meglerforetakets org.nr: `[[meglerkontor.orgnr]]`
- Oppdragsnr.: `[[oppdrag.nr]]`
- Omsetningsnr.: `[[kontrakt.formidling.nr]]`

#### Fix 6: Add missing CSS classes (Analysis D0)
Add to the `<style>` block:
- `span.insert:empty::before` (placeholder text from `data-label`)
- `.insert-table` (inline-table display)
- `.liste .separator` (inline list with separator hiding)
- `.sign-line` (signature line styling) — if used

Get the exact CSS from `PRODUCTION-TEMPLATE-PIPELINE.md` Section 7.

#### Fix 7: Insert field pattern (Analysis D4)
Update `<span class="insert">&nbsp;</span>` instances to use the `insert-table` wrapper and
`data-label` attribute:
```html
<span class="insert-table"><span class="insert" data-label="dato"></span></span>
```

Choose appropriate `data-label` values: `"dato"`, `"bel&oslash;p"`, `"tekst"`, `"klokkeslett"`,
`"adresse"`.

#### Fix 8: Wrap monetary fields in `$.UD()` (Analysis D0)
All monetary merge fields must use `$.UD()` for thousand-separator formatting:
- `[[kontrakt.kjopesum]]` → `$.UD([[kontrakt.kjopesum]])`
- `[[kontrakt.totaleomkostninger]]` → `$.UD([[kontrakt.totaleomkostninger]])`
- `[[kontrakt.kjopesumogomkostn]]` → `$.UD([[kontrakt.kjopesumogomkostn]])`
- `[[kostnad.belop]]` → `$.UD([[kostnad.belop]])` (inside foreach)
- `[[eiendom.fellesutgifter]]` → `$.UD([[eiendom.fellesutgifter]])`
- Any other numeric/monetary values

#### Fix 9: Quote mark consistency (Analysis D0)
Standardize to guillemets (`&laquo;`/`&raquo;`) throughout, matching the reference templates
and Norwegian legal document convention. Replace `&ldquo;`/`&rdquo;` with `&laquo;`/`&raquo;`.

#### Fix 10: Signature block improvements (Analysis D0)
- Fix colspan from `40` to `45` (matching enebolig and closer to reference)
- Add conditional plural: `Selger<span vitec-if="Model.selgere.Count &gt; 1">e</span>`
- Replace manual `<span class="insert">` date with `[[dagensdato]]` merge field
- If possible, use `vitec-foreach` loops for multi-party signatures (matching reference pattern)

### CONTENT — Must fix for legal accuracy

#### Fix 11: Wrong Payment Model (Analysis: Source Document Comparison)

**This is a content mismatch, not a structural issue.** The leilighet production template
currently uses the **enebolig's** "delinnbetalinger" payment structure in its Oppgj&oslash;r
(Section 4) with "For tomten:" and "For boligen:" subsections.

However, the actual selveier source document (`8966142_3.htm` / `Kj&oslash;pekontrakt Prosjekt
selveier .docx`) has a different two-option payment model:

- **Alternativ 1: Forskudd** — Boligen tinglyses i kj&oslash;pers navn f&oslash;rst ved
  tidspunkt for ferdigstillelse og overtagelse
- **Alternativ 2: Hele kj&oslash;pesummen betales ved overtakelse av boligen**

Additionally, the following guarantee provisions from the selveier source are **missing** from
the current leilighet template:
- `bustadoppf&oslash;ringslova &sect; 47` forskuddsgaranti requirements
- `&sect; 12` garanti provisions specific to the selveier variant
- "Til det er dokumentert at det foreligger &sect;12 garanti, har forbrukeren rett til &aring;
  holde tilbake alt vederlag"

**Action:** Compare the source document (`C:\Users\Adrian\Downloads\8966142_3.htm`) against
the current Oppgj&oslash;r section. Replace the enebolig delinnbetalinger model with the
correct selveier two-alternative payment model, and add the missing guarantee paragraphs.
Use `vitec-if` to branch between Alternativ 1 and Alternativ 2.

**Important:** The legal text must be taken **verbatim** from the source document. Do not
paraphrase or summarize legal provisions.

### VISUAL — Must fix for consistency with reference (Analysis: Visual Comparison)

#### Fix 12: Missing fullmektig section (Visual V6)
The enebolig template has a `[[kjoper.fullmektig.navn]]` fullmektig (representative) section,
but the leilighet omits it. Add the fullmektig conditional block matching the enebolig pattern:

```html
<p vitec-if="Model.kjoper.fullmektig.navn != &quot;&quot;">
  Kj&oslash;per er representert ved fullmektig [[kjoper.fullmektig.navn]]
</p>
```

#### Fix 13: Complete heading and base CSS from reference (Visual V2, Analysis D4)
The template `<style>` block must include the full heading CSS from the bruktbolig reference,
not just the counter system. Add these rules:

```css
#vitecTemplate h1 { text-align: center; font-size: 14pt; margin: 0; padding: 0; }
#vitecTemplate h2 { font-size: 11pt; margin: 30px 0 0 -26px; padding: 0; }
#vitecTemplate h3 { font-size: 10pt; margin: 20px 0 0 -10px; padding: 0; }
#vitecTemplate table { width: 100%; table-layout: fixed; }
#vitecTemplate ul { list-style-type: disc; margin-left: 0; }
#vitecTemplate ul li { list-style-position: outside; line-height: 20px; margin-left: 0; }
#vitecTemplate a.bookmark { color: #000; font-style: italic; text-decoration: none; }
```

The `h1` centering is important because we removed the inline `style="text-align:center"` in
Fix 4 — the CSS rule handles centering instead, matching the reference approach.

#### Fix 14: Roles table column header (Visual V6)
Change the "Adresse" column header to "Adresse/Kontaktinfo" matching the reference pattern:
```html
<th colspan="48"><strong>Adresse/Kontaktinfo</strong></th>
```

And use `rowspan="2"` on the name cell to span both address and contact rows (see
`PRODUCTION-TEMPLATE-PIPELINE.md` Section 7, Roles Table with rowspan).

## Build Process

1. **Update the build script** (`build_kjopekontrakt_prosjekt_leilighet.py`) with all fixes above
2. **Run the build script** to generate the updated production HTML
3. **Run the unified validator:**
   ```
   python scripts/validate_vitec_template.py scripts/converted_html/Kjopekontrakt_prosjekt_leilighet_PRODUCTION.html --tier 4
   ```
4. **Fix any validation failures** — iterate until all checks PASS
5. **Write the handoff summary** (see "Deliverables" below)

**Do NOT** upload to Vitec Next, run live verification, or commit to the database.
Your job ends when the production HTML passes validation and the handoff summary is written.

## Deliverables

All output files must be written **inside the project workspace**.

| File | Path (relative to workspace root) |
|------|-----------------------------------|
| Updated build script | `scripts/build_kjopekontrakt_prosjekt_leilighet.py` |
| Production HTML | `scripts/converted_html/Kjopekontrakt_prosjekt_leilighet_PRODUCTION.html` |
| Handoff summary | `scripts/converted_html/Kjopekontrakt_prosjekt_leilighet_HANDOFF.md` |

### Handoff Summary Format

Write the handoff summary as a Markdown file at the path above. It must contain:

```markdown
# Handoff: Kjøpekontrakt prosjekt (leilighet)

## Spec
- **Mode:** B (Convert/Migrate)
- **Tier:** T4 (Complex contract)
- **Template:** Kjøpekontrakt prosjekt (leilighet med delinnbetalinger)

## Production File
- **Path:** `scripts/converted_html/Kjopekontrakt_prosjekt_leilighet_PRODUCTION.html`
- **Size:** [X chars]
- **Build script:** `scripts/build_kjopekontrakt_prosjekt_leilighet.py`

## Template Stats
- Sections: [count]
- Merge fields: [count] — [list all field paths]
- vitec-if conditions: [count]
- vitec-foreach loops: [count] — [list each "item in Collection"]
- Insert fields: [count]
- SVG checkboxes: [count]

## Validation Result
- Validator: `validate_vitec_template.py --tier 4`
- Result: [X/Y PASS, Z FAIL]
- [Paste the full validator output here]

## Fixes Applied
[List each fix applied with a one-line summary of what changed]

## Potential Issues & Uncertainties
[List anything the builder is uncertain about, e.g.:]
- Field mappings that were guessed rather than confirmed
- Legal text sections where the source was ambiguous
- Sections where the enebolig pilot was used as reference because the source didn't cover it
- Merge field paths that couldn't be verified against the field registry
- Any structural choices that differ from the bruktbolig reference and why

## Content Notes
[Anything relevant about the template content:]
- Which source document sections were used verbatim
- Which sections were adapted from the enebolig pilot
- Payment model details (Alternativ 1 vs 2)
- Guarantee provisions included

## Known Limitations
[Anything that can't be fixed at build time:]
- Patterns that may behave differently in CKEditor vs static HTML
- Merge fields that depend on property data availability
- Conditional branches that can't be tested without specific property types

## Recommendations
[Suggestions for the next step — analysis agent or human review:]
- Sections that should be carefully reviewed
- Recommended test properties for live verification (when done later)
- Any follow-up work needed
```

## Validation Target

All checks in `validate_vitec_template.py --tier 4` must PASS, specifically:
- `[A] No proaktiv-theme class` — PASS
- `[A] Outer table body wrapper` — PASS
- `[A] H1 title element` — PASS
- `[A] H1 CSS styling in style block` — PASS
- `[A] H2 CSS styling with negative margin` — PASS
- `[H] No Unicode checkboxes` — PASS
- `[H] SVG checkbox CSS present` — PASS
- `[H] Insert fields have data-label` — PASS
- `[H] Insert fields use insert-table wrapper` — PASS
- `[I] Norwegian chars are HTML entities` — PASS
- `[I] HTML entities present` — PASS
- `[J] Monetary fields use $.UD()` — PASS

## Important Rules

- Legal text must be **verbatim** from the source document — never paraphrase
- All Norwegian characters in text content must be HTML entities — never literal UTF-8
- All checkboxes must use the SVG pattern — never Unicode &#9744;/&#9745;
- All monetary merge fields must use `$.UD()` wrapper
- All `vitec-if` expressions must use `&quot;` for quotes, `&gt;` for greater-than
- All `vitec-foreach` loops must have both a `Count > 0` guard AND a `Count == 0` fallback
- All insert fields must use `insert-table` wrapper with `data-label`
- If a field mapping is unclear, flag it in the handoff summary under "Potential Issues" — don't guess silently
- **Do NOT** attempt to upload, test in Vitec Next, or commit to the database
