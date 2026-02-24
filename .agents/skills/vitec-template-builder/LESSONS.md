# Lessons Learned Registry

Structured catalog of every mistake discovered during template builds, with the exact fix applied.
The builder agent MUST read this file before starting any build and apply all relevant lessons proactively.

**Last updated:** 2026-02-24 (empirically validated against 234/249 production templates + 3 transcript audits)

---

## SOURCE OF TRUTH HIERARCHY

When sources conflict, follow this priority order:

1. **Working reference templates** (gold standard) — `scripts/reference_templates/` and `scripts/golden standard/`
   These are verified production templates from Vitec Next that render correctly in PDF.
2. **Master template library** — `templates/master/` (249 official templates scraped 2026-02-23)
   The complete set of Vitec system templates and Proaktiv custom templates from production.
3. **V2 Analysis Report** — `.planning/phases/11-template-suite/V2-ANALYSIS-REPORT.md`
   Side-by-side CSS/HTML comparison against the bruktbolig gold standard.
4. **VITEC-IF Deep Analysis** — `.planning/phases/11-template-suite/VITEC-IF-DEEP-ANALYSIS.md`
   366 conditions analyzed from 3 reference templates.
5. **This file (LESSONS.md)** and **PATTERNS.md** — Distilled from the above sources.
6. **vitec-html-ruleset-FULL.md** — `.planning/vitec-html-ruleset-FULL.md`
   Comprehensive reference (4,101 lines), BUT was written based on the old database collection
   of 133 Proaktiv-customized templates. Some rules reflect Proaktiv conventions, not Vitec
   standards. Where it conflicts with the working reference templates, the references win.

**Known conflict:** The ruleset says `class="proaktiv-theme"` is mandatory (all 133 DB templates
had it). The working reference templates do NOT use it. The 249 scraped Vitec system templates
also do not use it. **Do NOT add `proaktiv-theme`** — it was a Proaktiv custom convention,
not a Vitec standard.

---

## ENCODING (Category E)

### E1: UTF-8 Literals Cause Mojibake in PDF
- **Severity:** CRITICAL
- **Discovered:** Leilighet build (first live test)
- **Symptom:** ø renders as Ã¸, å as Ã¥, § as Â§ in Vitec PDF output
- **Root cause:** Template had literal UTF-8 characters. CKEditor/Vitec PDF renderer expects HTML entities.
- **Fix:** ALL Norwegian characters in text content must be HTML entities, never literal UTF-8.
- **Entity map:**
  - ø → `&oslash;` | å → `&aring;` | æ → `&aelig;`
  - Ø → `&Oslash;` | Å → `&Aring;` | Æ → `&AElig;`
  - § → `&sect;` | « → `&laquo;` | » → `&raquo;`
  - – → `&ndash;` | — → `&mdash;` | é → `&eacute;`
- **Applies to:** ALL templates, ALL tiers
- **Automation:** `post_process_template.py` handles this automatically as final step

### E2: Norwegian Characters in vitec-if Use Unicode Escapes
- **Severity:** IMPORTANT
- **Discovered:** Analysis report comparison with reference templates
- **Symptom:** Condition string comparisons fail silently
- **Root cause:** vitec-if attribute values need unicode escapes, not HTML entities
- **Fix:** Inside `vitec-if="..."` string comparisons:
  - ø → `\xF8` | å → `\xE5` | æ → `\xE6`
  - Ø → `\xD8` | Å → `\xC5` | Æ → `\xC6`
- **Example:** `vitec-if="Model.oppdrag.hovedtype == &quot;Oppgj\xF8rsoppdrag&quot;"`
- **Applies to:** Any template with Norwegian text in condition values

### E3: Norwegian Characters in Comments/CSS
- **Severity:** COSMETIC
- **Discovered:** Landbrukseiendom (validator flagged literal chars in CSS comments)
- **Fix:** Use ASCII equivalents in CSS/HTML comments (e.g. "Kjopekontrakt" not "Kjøpekontrakt")
- **Applies to:** ALL templates

### E4: Word HTM Exports Use Windows-1252 Encoding
- **Severity:** IMPORTANT
- **Discovered:** Transcript mining (prosjekt leilighet/enebolig Word conversion)
- **Symptom:** Python scripts fail with `UnicodeDecodeError` or produce mojibake when reading Word-exported `.htm` files
- **Root cause:** Word saves `.htm` files in Windows-1252 (Latin-1) encoding, not UTF-8
- **Fix:** Scripts that read Word HTM exports must use `encoding='latin-1'` or `encoding='cp1252'`, or a try/fallback pattern:
  ```python
  try:
      content = open(path, 'r', encoding='utf-8').read()
  except UnicodeDecodeError:
      content = open(path, 'r', encoding='latin-1').read()
  ```
- **Applies to:** ALL Word-sourced template conversions (Mode B pipeline)

### E5: CSS Attribute Selectors Use Different Unicode Escape Syntax
- **Severity:** IMPORTANT
- **Discovered:** Transcript mining (oppdragsavtale prosjekt CSS analysis)
- **Symptom:** CSS attribute selector with `\xF8` (vitec-if syntax) doesn't match
- **Root cause:** CSS and vitec-if use different unicode escape syntaxes for Norwegian characters
- **Fix:** Context-dependent escaping:
  - **vitec-if attributes:** `\xF8` (hex escape) → e.g., `Oppgj\xF8rsoppdrag`
  - **CSS selectors:** `\00f8` (CSS unicode escape) → e.g., `[data-type="Oppgj\00f8rsoppdrag"]`
  - These are NOT interchangeable
- **Applies to:** Templates with CSS-driven conditional display via `data-type` attributes

### E6: Lambda Arrow `=>` Must Be HTML-Encoded in Vitec Attributes
- **Severity:** CRITICAL
- **Discovered:** Transcript mining (database analysis of 133 templates)
- **Symptom:** LINQ expressions in vitec-foreach silently fail or cause parse errors
- **Root cause:** The `>` in `=>` is interpreted as HTML, breaking the attribute value
- **Fix:** Encode `=>` as `=&gt;` inside vitec-if and vitec-foreach attribute values:
  - Wrong: `vitec-foreach="x in Model.collection.Where(x => x.type == 'A')"`
  - Correct: `vitec-foreach="x in Model.collection.Where(x =&gt; x.type == &quot;A&quot;)"`
- **Applies to:** T4+ templates using LINQ expressions in vitec attributes

---

## CHECKBOXES (Category CB)

### CB1: Unicode Checkboxes Render as "?" in PDF
- **Severity:** CRITICAL
- **Discovered:** Leilighet build (first live test)
- **Symptom:** `&#9744;` and `&#9745;` render as question marks in Vitec PDF
- **Root cause:** Vitec PDF renderer doesn't support Unicode checkbox characters
- **Fix:** Use SVG-based checkbox pattern exclusively (see PATTERNS.md)
- **Applies to:** ALL templates with checkboxes (T3+)

### CB2: Double Checkbox Rendering
- **Severity:** IMPORTANT
- **Discovered:** Næringsbygg build
- **Symptom:** Two checkboxes appear where one expected
- **Root cause:** CSS selector mismatch: `data-toggle="button"` (singular) vs `data-toggle="buttons"` (plural)
- **Fix:** Use `data-toggle="buttons"` (plural) on the parent container, or use the simple pattern without `<input>` for data-driven checkboxes
- **Applies to:** Templates with interactive checkbox groups

### CB3: Data-Driven vs Broker-Interactive Distinction
- **Severity:** IMPORTANT
- **Discovered:** Analysis report, V2 Analysis (P0-3)
- **Fix:** Data-driven checkboxes (controlled by vitec-if) must NOT have `<input type="checkbox">`. Standalone broker-interactive checkboxes also have NO `<input>`. Only radio groups use `<input type="radio" name="groupName">` AFTER the span (not before).
- **Applies to:** ALL templates with checkboxes

### CB4: SVG ViewBox Must Be 512x512
- **Severity:** BLOCKING (P0)
- **Discovered:** V2 Analysis Report (P0-1)
- **Symptom:** Our checkboxes looked "web-modern" while reference looked like traditional legal forms
- **Root cause:** Used viewBox `0 0 16 16` with thin strokes. Reference uses `0 0 512 512` with filled rects.
- **Fix:** Use the EXACT SVG data URIs from PATTERNS.md section 4. Do not create custom SVGs.
- **Applies to:** ALL templates with checkboxes

### CB5: Checkbox CSS Must Have All 12 Reset Properties
- **Severity:** BLOCKING (P0)
- **Discovered:** V2 Analysis Report (P0-2)
- **Fix:** The checkbox CSS must include ALL properties from the reference to properly reset Bootstrap-derived styles loaded by the Stilark. Missing properties cause: shifted positioning (`vertical-align`), inherited padding (`padding: 0`), blue focus glow (`outline: none`), wrong cursor (`cursor: pointer`).
- **Applies to:** ALL templates with checkboxes

### CB6: Radio Button SVG Pattern
- **Severity:** INFO
- **Discovered:** V2 Analysis Report (appendix)
- **Fix:** For radio-style mutual exclusion (Alternativ A/B), use:
  - `.svg-toggle.radio` class (circular SVG, not square)
  - `<input type="radio" name="groupName">` AFTER the span
  - `data-toggle="buttons"` on the parent `<p>` or container
- **Applies to:** Templates with radio-style alternatives

### CB7: Checkbox Count Parity Between Source and Output
- **Severity:** IMPORTANT
- **Discovered:** Transcript mining (enebolig vs leilighet builds)
- **Symptom:** Missing or duplicate checkboxes in production template vs Word source
- **Root cause:** Word sources use "q" characters as checkbox placeholders. During conversion, counts can drift due to merging, splitting, or adding conditional pairs.
- **Fix:** Track checkbox count from source to output. Word "q" chars → SVG checkboxes. Log and justify every delta in the handoff document:
  - Source had 33 "q" checkboxes
  - Output has 32 (one merged) or 50 (conditional pairs expanded) — document WHY
  - Unexpected count changes signal a conversion error
- **Applies to:** ALL Mode B conversions from Word source

---

## STRUCTURE (Category S)

### S1: Missing Outer Table Wrapper
- **Severity:** IMPORTANT
- **Discovered:** Leilighet regression (had it in enebolig, lost it)
- **Symptom:** Layout may shift in Vitec PDF renderer
- **Fix:** ALL body content must be inside `<table><tbody><tr><td colspan="100">...</td></tr></tbody></table>`
- **Applies to:** ALL templates

### S2: proaktiv-theme Class Not Used
- **Severity:** IMPORTANT
- **Discovered:** Analysis report (no reference template uses it)
- **Fix:** Do NOT add `class="proaktiv-theme"` to the root `<div id="vitecTemplate">`. It can conflict with Vitec Stilark.
- **Applies to:** ALL templates
- **Empirical:** Confirmed: 0 of 234 analyzed templates use proaktiv-theme (mining report 2026-02-24)

### S3: Title Must Be H1, Not H5
- **Severity:** IMPORTANT
- **Discovered:** Leilighet regression from enebolig
- **Fix:** Template title must use `<h1>`, never `<h5>` or other levels
- **Applies to:** ALL templates

### S4: H2 Negative Margin Pattern
- **Severity:** COSMETIC
- **Discovered:** Landbrukseiendom (validator check)
- **Fix:** CSS must include `#vitecTemplate h2 { margin: 30px 0 0 -20px; }` to align headings with the left edge while article content has `padding-left: 20px`. See S8 for the corrected values.
- **Applies to:** T3+ templates with article sections

### S5: CSS Selector Specificity — Scoped vs Unscoped (CRITICAL)
- **Severity:** IMPORTANT
- **Discovered:** V2 Analysis Report (P2-1), Landbrukseiendom
- **Root cause:** The Vitec Stilark loads Bootstrap-derived styles globally. Checkbox and insert-field CSS must compete at the correct specificity level.
- **Fix:** Match the reference scoping pattern exactly:
  - **UNSCOPED** (no `#vitecTemplate` prefix): `label.btn`, `.svg-toggle`, `.svg-toggle.checkbox`, `span.insert:empty`, `.insert-table`
  - **SCOPED** (with `#vitecTemplate` prefix): `.avoid-page-break`, `article`, `h1/h2/h3`, `table`, `.roles-table`, `a.bookmark`, `.liste`
- **Why:** Over-scoping raises specificity, which may override Stilark rules we want to keep. Under-scoping lets Stilark override our rules. The reference templates got this balance right.
- **Applies to:** ALL templates

### S6: Two Separate Style Blocks
- **Severity:** COSMETIC (but recommended)
- **Discovered:** V2 Analysis Report (P3-1)
- **Fix:** Use TWO `<style>` blocks, not one:
  1. First block: Template-specific CSS (counters, headings, tables, inserts)
  2. Second block: Checkbox/radiobutton CSS (prefixed with `/* Klikkbare sjekkbokser og radioknapper */`)
- **Why:** This matches how Vitec organizes its templates and makes surgical CSS updates easier.
- **Applies to:** ALL T3+ templates

### S7: roles-table — Only the Hide-Last-Row Rule
- **Severity:** MINOR
- **Discovered:** V2 Analysis Report (P2-2)
- **Fix:** The reference template only defines one `.roles-table` rule:
  ```css
  #vitecTemplate .roles-table tbody:last-child tr:last-child td { display: none; }
  ```
  Our extra rules (th padding, border-bottom, td padding) come from the Stilark already. Adding them risks overriding Stilark defaults inconsistently with other Vitec templates.
- **Applies to:** T3+ templates with roles-table

### S8: Article Padding is 20px (Not 26px)
- **Severity:** IMPORTANT
- **Discovered:** Production comparison (Bruktbolig + FORBRUKER, 2026-02-23)
- **Symptom:** Section numbering and heading alignment slightly off from production
- **Root cause:** PATTERNS.md previously used 26px from an earlier reference. Both production
  templates use `padding-left: 20px` and `margin: 30px 0 0 -20px` on h2.
- **Fix:** Use exactly:
  ```css
  #vitecTemplate article { padding-left: 20px; }
  #vitecTemplate h2 { margin: 30px 0 0 -20px; }
  ```
- **Applies to:** ALL T3+ templates
- **Empirical:** Confirmed: 7 of 8 templates with article padding use 20px; only 1 uses 26px (mining report 2026-02-24)

### S9: Counter ::before — No display/width Properties
- **Severity:** IMPORTANT
- **Discovered:** Production comparison (Bruktbolig + FORBRUKER, 2026-02-23)
- **Root cause:** PATTERNS.md had `display: inline-block; width: 26px;` on h2/h3 `::before`.
  Production templates only set `content:` — no display or width.
- **Fix:** Counter pseudo-elements should ONLY have the `content:` property:
  ```css
  #vitecTemplate article.item:not(article.item article.item) h2::before {
      content: counter(section) ". ";
  }
  #vitecTemplate article.item article.item h3::before {
      content: counter(section) "." counter(subsection) ". ";
  }
  ```
  Note the trailing period+space in h3 content: `". "` (not just `" "`).
- **Applies to:** ALL T3+ templates with article counters
- **Empirical:** Confirmed: Only 1 of 234 templates has display/width on ::before (mining report 2026-02-24)

### S10: Chromium insert-table Fix (CRITICAL)
- **Severity:** CRITICAL
- **Discovered:** Chromium rendering issue in Vitec Next editor (2026-02-23)
- **Symptom:** Insert fields (pink placeholders) break layout or don't render in Chromium
- **Root cause:** Chromium needs `display: inline-table` on the wrapper and `display: table-cell`
  on children for correct inline rendering of insert field placeholder spans.
- **Fix:** The insert-table CSS block is now the production standard:
  ```css
  .insert-table {
      display: inline-table;
  }
  .insert-table > span,
  .insert-table > span.insert {
      display: table-cell;
  }
  ```
  These selectors MUST be UNSCOPED (no `#vitecTemplate` prefix).
  This pattern is confirmed in both Bruktbolig and FORBRUKER production templates.
- **Applies to:** ALL templates with insert fields
- **Empirical:** Present in 99 of 234 templates (42%) — standard for all templates with insert fields (mining report 2026-02-24)

### S11: .borders Table Class
- **Severity:** INFO
- **Discovered:** Production comparison (Bruktbolig + FORBRUKER, 2026-02-23)
- **Fix:** Production CSS includes a `.borders` class scoped under `#vitecTemplate table`:
  ```css
  #vitecTemplate table .borders {
      width: 100%;
      table-layout: fixed;
      border-bottom: solid 1px black;
      border-top: solid 1px black;
  }
  ```
  Include this in the core CSS block for templates that use bordered table sections.
- **Applies to:** T3+ templates with bordered tables

### S12: .liste Rule — Only the Last-Child Separator
- **Severity:** MINOR
- **Discovered:** Production comparison (Bruktbolig + FORBRUKER, 2026-02-23)
- **Root cause:** PATTERNS.md had 4 `.liste` rules. Production only uses one.
- **Fix:** Only include:
  ```css
  #vitecTemplate .liste:last-child .separator { display: none; }
  ```
  Do NOT add `.liste { display: inline; }`, `.liste .separator { display: inline; }`,
  or `.liste .separator:first-child { display: none; }` — the Stilark handles these.
- **Applies to:** Templates with inline comma-separated lists

### S13: H2 Margin Has Two Valid Patterns
- **Severity:** INFO
- **Discovered:** Library mining report (2026-02-24)
- **Fix:** Two equally common H2 margin patterns exist in production:
  - `margin: 30px 0 0 -20px` — 7 templates (matches article padding 20px, recommended for new builds)
  - `margin: 25px 0 0 -1em` — 7 templates (older pattern)
  Use `30px 0 0 -20px` as the standard for new builds (consistent with S8's 20px article padding).
- **Applies to:** T3+ templates with article sections
- **Empirical:** Both patterns at 7/234 templates each (mining report 2026-02-24)

### S14: H1 Font Size Varies by Template Type
- **Severity:** INFO
- **Discovered:** Library mining report (2026-02-24)
- **Fix:** H1 font size is template-dependent, not universal:
  - `14pt` — 20 templates (most common, contracts/kjøpekontrakt)
  - `18pt` — 15 templates (forms/letters)
  - Other sizes (`22pt`, `16px`, `12pt`, `1.5em`, `16pt`) — 11 templates
  Default to `14pt` for contracts. Check reference templates for the specific template type.
- **Applies to:** ALL templates
- **Empirical:** Font size distribution from 46 templates with explicit h1 styling (mining report 2026-02-24)

### S15: Only Use Standard Vitec CSS Classes
- **Severity:** IMPORTANT
- **Discovered:** Transcript mining (prosjekt leilighet build)
- **Symptom:** Custom CSS class may be silently ignored or conflict with Stilark
- **Root cause:** Builder invented `.costs-table` which doesn't exist in any reference template
- **Fix:** Only use CSS classes known to exist in production templates: `.borders`, `.roles-table`,
  `.insert-table`, `.insert-textbox`, `.insert-textarea`, `.liste`, `.sign-field`,
  `.avoid-page-break`, `.nummerert-liste`, `.checkbox-table`, `.bordered-table`,
  `.collapse-tbody`, `.info-table`, `.sumlinje`, `.delsumlinje`.
  Do not invent new class names — the Stilark and Vitec renderer may not support them.
- **Applies to:** ALL templates

### S16: vitec-foreach Valid on `<div>`, Not Just `<tbody>`
- **Severity:** INFO
- **Discovered:** Transcript mining (bruktbolig reference analysis)
- **Fix:** The foreach container element is flexible:
  - `<tbody>` — for table row loops (most common)
  - `<div>` — for block-level content loops (party info, addresses)
  The element type should match the content structure being looped.
- **Applies to:** ALL templates with foreach loops

### S17: Three Insert Field CSS Variants
- **Severity:** INFO
- **Discovered:** Transcript mining (oppdragsavtale + kjøpetilbud analysis)
- **Fix:** Production templates use three distinct insert field variants:
  - `insert-table` — `display: inline-table` — standard merge field containers (most common)
  - `insert-textbox` — `display: inline-table`, fixed-width, `border-bottom` — inline input fields
  - `insert-textbox.small` — narrower variant (`width: 7em`)
  - `insert-textarea` — `display: table; width: 100%; height: 3em` — multiline with border
  Only `insert-table` is required in all templates. The others appear in form-type templates.
- **Applies to:** Form/agreement templates (T2+)

### S18: `data-choice` Attribute for Floating Choice Labels
- **Severity:** INFO
- **Discovered:** Transcript mining (database analysis, 41/133 templates)
- **Fix:** `data-choice` on `<td>` creates floating choice labels BELOW cell content via CSS
  `::after` pseudo-element. Used alongside `data-label` (which creates labels ABOVE):
  ```html
  <td data-label="Type" data-choice="Selveier">
  ```
- **Applies to:** Form templates with structured data entry cells (Skjøte, Akseptbrev)

### S19: `@functions` C# Blocks Live in Separate Support Templates
- **Severity:** CRITICAL
- **Discovered:** Transcript mining (bruktbolig custom template architecture)
- **Root cause:** Custom C# method definitions cannot be embedded inline in contract templates
- **Fix:** Place `@functions` blocks in a separate system template file and reference via:
  ```html
  <span vitec-template="resource:SupportTemplateName">&nbsp;</span>
  ```
  The main template calls methods with `@MethodName()` in vitec-if or inline text.
  Example: "Boligkjøperforsikring" support template with `@GetPosteringsVerdi...()` methods.
- **Applies to:** Custom templates requiring computed values or complex business logic

### S20: Combined vitec-if + vitec-foreach on Same Element
- **Severity:** INFO
- **Discovered:** Transcript mining (Alle-flettekoder analysis)
- **Fix:** A single element can carry BOTH `vitec-if` and `vitec-foreach` attributes simultaneously.
  The condition is evaluated first; if true, the foreach iterates:
  ```html
  <tbody vitec-if="Model.collection.Count &gt; 0" vitec-foreach="item in Model.collection">
  ```
  This is valid shorthand for the guard+foreach pattern. However, the two-element pattern
  (separate guard `<div>` wrapping the foreach element) is more readable and preferred.
- **Applies to:** ALL templates with foreach loops

### S21: System Templates Use Custom CSS IDs for Scoping
- **Severity:** INFO
- **Discovered:** Transcript mining (system footer/resource template analysis)
- **Fix:** System templates (Avsender, Mottaker, Bunntekst) use custom CSS IDs for scoping:
  `#Avsender`, `#Mottaker`, `#bunntekstTabell`. They do NOT use `#vitecTemplate`.
  This prevents style conflicts between the main template and injected system components.
- **Applies to:** When creating system/resource templates (not regular document templates)

### S22: Multiple Resource Template Spans Can Coexist
- **Severity:** INFO
- **Discovered:** Transcript mining (custom bruktbolig with support template)
- **Fix:** Templates can reference multiple system resources via separate spans:
  ```html
  <span vitec-template="resource:Vitec Stilark">&nbsp;</span>
  <span vitec-template="resource:Boligkjøperforsikring">&nbsp;</span>
  ```
  Each resource is loaded independently. Use for templates needing Stilark + custom function libraries.
  Note: ` Avsender` and ` Mottaker` resources have a leading space in their names (see MF8).
- **Applies to:** Custom templates with computed values or shared partials

---

## MERGE FIELDS (Category MF)

### MF1: Collection Path Errors
- **Severity:** CRITICAL
- **Discovered:** Landbrukseiendom
- **Symptom:** Foreach loop produces no output
- **Root cause:** Used `Model.kjoperskostnader.poster` instead of `Model.kjoperskostnader.alleposter`
- **Fix:** Always verify collection paths against the field registry. Common correct paths:
  - `Model.selgere` (sellers)
  - `Model.kjopere` (buyers)
  - `Model.hjemmelshavere` (title holders)
  - `Model.kjoperskostnader.alleposter` (buyer costs)
  - `Model.selgerskostnader.alleposter` (seller costs)
- **Applies to:** T3+ templates with foreach loops
- **Empirical:** Confirmed: `alleposter` is the standard (7-13 templates), `.poster` used rarely (1-6 templates) (mining report 2026-02-24)

### MF2: Monetary Fields Need $.UD() Wrapper
- **Severity:** IMPORTANT
- **Discovered:** Analysis report
- **Fix:** ALL monetary merge fields must use `$.UD([[field]])` for thousand-separator formatting. Common monetary fields: `kontrakt.kjopesum`, `kostnad.belop`, `kontrakt.totaleomkostninger`, `eiendom.fellesutgifter`
- **Applies to:** ALL templates with monetary values

### MF3: Safe Fallback Pattern (Triple-Span)
- **Severity:** IMPORTANT
- **Discovered:** Landbrukseiendom (evolved from earlier builds)
- **Fix:** Critical fields should use the triple-span guard pattern:
  ```html
  <span vitec-if="Model.field != &quot;&quot; &amp;&amp; Model.field != &quot;Mangler data&quot;">[[field]]</span>
  <span vitec-if="Model.field == &quot;&quot;"><span class="insert-table"><span class="insert" data-label="placeholder"></span></span></span>
  <span vitec-if="Model.field == &quot;Mangler data&quot;"><span class="insert-table"><span class="insert" data-label="placeholder"></span></span></span>
  ```
- **Applies to:** T3+ templates for critical header/preamble fields

### MF4: "Mangler data" Sentinel Checks
- **Severity:** IMPORTANT
- **Discovered:** VITEC-IF Deep Analysis (Finding 5)
- **Symptom:** Conditional sections show "Mangler data" placeholder text in PDF
- **Root cause:** Vitec sets empty fields to the string "Mangler data" rather than null/empty
- **Fix:** For critical data fields (matrikkel, dates, amounts), use:
  ```html
  vitec-if="Model.SomeField != &quot;Mangler data&quot;"
  ```
  Standard empty checks (`!= ''`) do NOT catch this. Use the sentinel check whenever
  Vitec explicitly marks missing data (vs fields that are simply empty/null).
  The triple-span pattern in MF3 already handles this — use it for important fields.
- **Applies to:** T3+ templates, especially property data sections
- **Empirical:** Confirmed: Used in 53 of 234 templates (23%) (mining report 2026-02-24)

### MF5: Entity-Level vs Property-Level Field Access
- **Severity:** IMPORTANT
- **Discovered:** VITEC-IF Deep Analysis (Finding 3)
- **Fix:** Vitec uses two field access patterns — understand when to use each:
  - **Entity-level**: `Model.Property.LandArea` — Direct path through the property entity
  - **Property-level**: `Model.CondoAssociation.Name` — Through a sub-entity association
  - **Collection**: `Model.Owners` — For `vitec-foreach` iteration
  Mixing these patterns (e.g., treating a collection as a single entity) causes render failures.
- **Applies to:** ALL templates

### MF6: vitec-if Negation Patterns
- **Severity:** INFO
- **Discovered:** VITEC-IF Deep Analysis (Finding 4), corrected by library mining (2026-02-24)
- **Fix:** Both `!` prefix and `!(expression)` grouping work in Vitec. The `not` keyword is NOT used in any production template (0 of 234). Use one of:
  - `vitec-if="!Model.Field.Method()"` — negate a method call
  - `vitec-if="!(expression || expression)"` — negate a grouped expression
  - `vitec-if="Model.Field != &quot;&quot;"` — inequality check (most common pattern)
  - `vitec-if="Model.Field == &quot;&quot;"` — empty string check
  - `vitec-if="Model.Field == &quot;false&quot;"` — explicit false check
  Do NOT use `vitec-if="not Model.Field"` — this keyword appears in 0 production templates.
- **Applies to:** ALL templates with conditional logic
- **Empirical:** 5 templates use `!` negation successfully; 0 templates use `not` keyword (mining report 2026-02-24)

### MF7: Most Common Field Paths
- **Severity:** INFO
- **Discovered:** Library mining report (2026-02-24)
- **Fix:** Quick reference for the most frequently used fields:
  - **Top entity:** `eiendom.kommunenavn` (151 templates), `eiendom.gatenavnognr` (148)
  - **Top collection:** `selger.navnutenfullmektigogkontaktperson` (64 in foreach), `selger.navn` (61 in foreach)
  - **Top monetary:** `kontrakt.kjopesum` (40 with `$.UD()`), `pant.belop` (19)
  - **Most common foreach:** `selger in Model.selgere` (138), `kjoper in Model.kjopere` (82)
  - **Default data-label:** `"Sett inn tekst her..."` (79 templates)
- **Applies to:** ALL templates (reference guide)

### MF8: Vitec Template Resources
- **Severity:** INFO
- **Discovered:** Library mining report (2026-02-24)
- **Fix:** Embedded resources used via `vitec-template="resource:NAME"`:
  - `Vitec Stilark` — 194/234 templates (83%, required for all standard templates)
  - ` Avsender` — 108 templates (46%, note leading space is intentional)
  - ` Mottaker` — 104 templates (44%, note leading space is intentional)
  - ` SMS-signatur` — 11 templates (SMS templates only)
  - `Boligkjøperforsikring` — 2 templates
  The leading space in ` Avsender` and ` Mottaker` is how Vitec stores these resources.
- **Applies to:** ALL templates using resource includes

### MF9: Loop Variable Fields Omit `Model.` Prefix
- **Severity:** CRITICAL
- **Discovered:** Transcript mining (database analysis of 133 templates)
- **Symptom:** vitec-if inside foreach silently fails or checks wrong field
- **Root cause:** Inside `vitec-foreach` loops, the loop variable is already scoped — adding `Model.` looks up the top-level entity instead of the current loop item
- **Fix:** Inside foreach loops, use the bare loop variable:
  - Wrong: `vitec-if="Model.selger.tlf != &quot;&quot;"` (inside `foreach selger in Model.selgere`)
  - Correct: `vitec-if="selger.tlf != &quot;&quot;"`
  The `Model.` prefix is only for top-level fields outside loops.
- **Applies to:** ALL templates with foreach loops containing conditionals

### MF10: "Mangler data" as Branching Trigger, Not Just Hide-Guard
- **Severity:** IMPORTANT
- **Discovered:** Transcript mining (forbruker golden standard analysis)
- **Root cause:** MF4 documents hiding content when "Mangler data" appears. But production templates also use it to BRANCH to alternative content.
- **Fix:** Use `== "Mangler data"` to trigger fallback display logic, not just hiding:
  ```html
  <div vitec-if="Model.hjemmelshaver.navn != &quot;Mangler data&quot;">
    [[hjemmelshaver.navn]]
  </div>
  <div vitec-if="Model.hjemmelshaver.navn == &quot;Mangler data&quot;">
    [[*selger.navnutenfullmektigogkontaktperson]]  <!-- fallback to seller name -->
  </div>
  ```
  This is a different usage pattern from the simple hide-guard in MF4.
- **Applies to:** T3+ templates with data fallback chains

### MF11: `Model.dokumentoutput` Discriminates PDF vs Email Rendering
- **Severity:** INFO
- **Discovered:** Transcript mining (Avsender/Mottaker resource template analysis)
- **Fix:** The system field `Model.dokumentoutput` returns `"pdf"` or `"email"` and controls
  output-channel conditional rendering. Resource templates use this to produce completely
  different HTML structures per channel:
  ```html
  <div vitec-if="Model.dokumentoutput == &quot;pdf&quot;">
    <table id="Avsender"><!-- PDF layout with page-break protection --></table>
  </div>
  <div vitec-if="Model.dokumentoutput == &quot;email&quot;">
    <div style="font-family:Calibri"><!-- Email layout --></div>
  </div>
  ```
- **Applies to:** Templates that render differently for PDF vs email output

### MF12: Contact Field Separators Need Compound vitec-if
- **Severity:** IMPORTANT
- **Discovered:** Transcript mining (prosjekt leilighet build)
- **Symptom:** Stray "/" separator appears when one contact field is empty
- **Root cause:** Separator between "Mob: X / E-post: Y" only checks one field, not both
- **Fix:** The "/" separator between adjacent contact fields must check BOTH fields:
  ```html
  <span vitec-if="selger.tlf != &quot;&quot; &amp;&amp; selger.emailadresse != &quot;&quot;"> / </span>
  ```
  For critical fields, also add `!= "Mangler data"` checks on both sides.
- **Applies to:** T3+ templates with inline contact information

---

## CONTENT FIDELITY (Category CF)

### CF1: Wrong Content Variant Mixed In
- **Severity:** CRITICAL
- **Discovered:** Leilighet build
- **Symptom:** Leilighet template had enebolig payment model (delinnbetalinger instead of Alternativ 1/2)
- **Root cause:** Builder copied structure from enebolig pilot without adapting to selveier source
- **Fix:** ALWAYS read the actual source document for the specific template. Never copy content from a different variant.
- **Applies to:** ALL Mode B builds

### CF2: Missing Legal Provisions
- **Severity:** IMPORTANT
- **Discovered:** Leilighet build (§12/§47 provisions)
- **Fix:** When converting, cross-check the source document's legal references against the output. Look for `§` references, "bustadoppføringslova", "avhendingslova" etc. and verify all are present.
- **Applies to:** T4/T5 contract templates

### CF3: Standard Clause Placeholders
- **Severity:** INFO
- **Discovered:** Landbrukseiendom
- **Fix:** Source documents may reference standard Vitec clauses (`#standard_*¤`). These are system-injected blocks that can't be replicated in template HTML. Use descriptive placeholders like `[Ektefellesamtykke-klausul innsettes her]` and note the limitation in the handoff.
- **Applies to:** T4+ templates with standard clause references

### CF4: Word "q" Characters Are Checkbox Placeholders
- **Severity:** IMPORTANT
- **Discovered:** Transcript mining (enebolig/leilighet Word conversion)
- **Symptom:** Literal "q" characters or bullet list items appear where checkboxes should be
- **Root cause:** Original Word documents use "q" characters (via Wingdings font) as checkbox proxies.
  Via mammoth DOCX conversion, these appear as plain "q" or bullet items (`• bolig`).
- **Fix:** During Mode B conversion, recognize both forms and map to SVG checkbox HTML:
  - Word source: `q bolig` or `• bolig` → `<label class="btn"><span class="checkbox svg-toggle"></span></label> bolig`
  - Track count parity (see CB7)
- **Applies to:** ALL Word-sourced template conversions

---

## VITEC-IF SYNTAX (Category VIF)

### VIF1: Implicit Boolean — No `== true` Required
- **Severity:** INFO
- **Discovered:** Transcript mining (database analysis, multiple templates)
- **Fix:** Boolean properties can be used directly in vitec-if without explicit comparison:
  - `vitec-if="Model.selger.ergift"` — works (no need for `== &quot;true&quot;`)
  - `vitec-if="selger.ergift"` — also works inside foreach loops
  This is a common pattern for boolean flags like `ergift`, `harfullmektig`, etc.
- **Applies to:** ALL templates with boolean field conditionals

### VIF2: `.ToString().Length` for ID Type Detection
- **Severity:** INFO
- **Discovered:** Transcript mining (database analysis, line 29 findings)
- **Fix:** `.ToString().Length` is a valid method chain in vitec-if for string length checks:
  ```html
  vitec-if="kjoper.idnummer.ToString().Length == 11"
  ```
  Used to distinguish personal IDs (11 digits) from organization IDs (9 digits) to show
  different labels ("Fødselsnummer" vs "Org.nr.").
- **Applies to:** Templates with party identification sections

### VIF3: Chained LINQ `.Where().Take()` in vitec-foreach
- **Severity:** INFO
- **Discovered:** Transcript mining (database analysis, 5 distinct chaining patterns found)
- **Fix:** Multiple LINQ methods can be chained in vitec-foreach values:
  ```html
  vitec-foreach="x in Model.collection.Where(x =&gt; x.type == &quot;A&quot;).Take(5)"
  ```
  Remember: `=>` must be encoded as `=&gt;` (see E6). Common chains:
  - `.Where().Take()` — filter + limit
  - `.Where().OrderBy()` — filter + sort
  - `.Where().Count()` — filter + count (in vitec-if)
- **Applies to:** T4+ templates with complex data filtering

### VIF4: vitec-if Safe on Additional HTML Elements
- **Severity:** INFO
- **Discovered:** Transcript mining (database analysis + FORBRUKER custom template)
- **Fix:** Beyond `<div>`, `<span>`, `<table>`, `<tr>`, `<td>`, these elements are also
  confirmed safe for vitec-if attributes:
  - `<p>` — paragraph (common in SMS templates)
  - `<article>` — section container (confirmed in FORBRUKER)
  - `<li>` — list item
  - `<ol>` — ordered list
  - `<tbody>` — table body (for combined if+foreach, see S20)
- **Applies to:** ALL templates

### VIF5: Custom Method Calls — `@` Prefix Rules
- **Severity:** IMPORTANT
- **Discovered:** Transcript mining (bruktbolig custom template with support template)
- **Fix:** The `@` prefix for custom method calls depends on context:
  - **vitec-foreach:** NO `@` prefix — `vitec-foreach="item in GetMethodName()"`
  - **vitec-if:** YES `@` prefix — `vitec-if="@GetMethodName() != &quot;0&quot;"`
  - **Inline text:** YES `@` prefix — `$.UD(@GetMethodValue())`
  - Wrong: `vitec-foreach="item in @GetMethod()"` or `vitec-if="GetMethod() != 0"`
- **Applies to:** Custom templates using `@functions` support templates (see S19)

### VIF6: `$.CALC()` Supports Mixed Operands
- **Severity:** INFO
- **Discovered:** Transcript mining (bruktbolig custom cost calculation)
- **Fix:** `$.CALC()` expressions can mix merge field values and method return values:
  ```html
  $.CALC(UD:[[kontrakt.kjopesumogomkostn]]-@GetPosteringsVerdiForBoligkjoperforsikring())
  ```
  The `UD:` prefix formats the result with thousand separators. Supported operators: `+`, `-`, `*`, `/`.
- **Applies to:** Custom templates with computed financial values

---

## VALIDATION (Category V)

### V1: Validator False Positives
- **Severity:** COSMETIC
- **Discovered:** Analysis report
- **Known false assumptions in validator:**
  - Checks for `proaktiv-theme` class (no reference uses it)
  - Some tier-specific checks may not apply to all contract types
- **Fix:** When validator reports failures, check against this list before attempting fixes

### V2: Foreach Guards Must Check Count
- **Severity:** IMPORTANT
- **Discovered:** Multiple builds
- **Fix:** Every `vitec-foreach="item in collection"` MUST have:
  1. Guard: `vitec-if="Model.collection.Count &gt; 0"` wrapping the foreach
  2. Fallback: `vitec-if="Model.collection.Count == 0"` with `[Mangler ...]` text
- **Applies to:** ALL templates with foreach loops
- **Empirical:** Confirmed: 111 of 234 templates (47%) use .Count guards (mining report 2026-02-24)

### V3: Validator Check Count Is Dynamic
- **Severity:** INFO
- **Discovered:** Transcript mining (validator testing sessions)
- **Fix:** The validator reports N checks where N = 35 static + (number of foreach loops) dynamic.
  A template with 4 foreach loops runs 39 checks; with 9 loops it runs 44 checks.
  Do not treat the check count as a fixed number — it scales with template complexity.
- **Applies to:** Validator output interpretation

---

## PIPELINE PROCESS (Category PP)

### PP1: Entity Encoding Must Be Last Step
- **Severity:** CRITICAL
- **Discovered:** Multiple builds
- **Fix:** Entity encoding must happen AFTER all content is finalized. If you encode first, then edit content, new text may have literal characters. Run `post_process_template.py` as the absolute final step.
- **Applies to:** ALL templates

### PP2: Manual Variant Deletion Required
- **Severity:** INFO
- **Discovered:** Næringsbygg, næringslokaler, meglerstandard
- **Fix:** Some templates have variants (Brukt/Nytt, Vedlegg 6A/6B/6C) where the broker must manually delete the inapplicable variant in CKEditor. This is a known Vitec limitation (no runtime variant selection). Document the deletion instructions in the handoff.
- **Applies to:** Templates with mutually exclusive variants

### PP3: Always Produce a Handoff Document
- **Severity:** IMPORTANT
- **Fix:** Every build must produce a handoff at `scripts/handoffs/{name}_HANDOFF.md` documenting: spec, stats, validation result, fixes applied, potential issues, known limitations. This is the learning record.
- **Applies to:** ALL builds

### PP4: Pipeline Reference Docs Must Be Validated Against Golden Standards
- **Severity:** CRITICAL
- **Discovered:** Transcript mining (leilighet v2 build used wrong SVGs from pipeline doc)
- **Symptom:** Builder faithfully reproduces incorrect patterns because the reference doc was wrong
- **Root cause:** `PRODUCTION-TEMPLATE-PIPELINE.md` contained incorrect SVG checkbox data URIs
  (`viewBox 0 0 16 16` with rounded `rx="2" ry="2"`) instead of the golden standard's
  `viewBox 0 0 512 512` with filled rect and sharp corners
- **Fix:** Pipeline documentation (PRODUCTION-TEMPLATE-PIPELINE.md, SUBAGENT-PROMPTS.md) must be
  periodically validated against golden standard templates. When a builder produces incorrect
  output, check whether the pipeline doc itself is the source of the error.
- **Applies to:** Pipeline maintenance

### PP5: Builder Agents Must Verify Source File Identity
- **Severity:** IMPORTANT
- **Discovered:** Transcript mining (leilighet build used enebolig source file by mistake)
- **Symptom:** Output template has wrong content variant
- **Root cause:** Builder agent claimed to have inspected the selveier source but had actually
  read the enebolig source. The analysis agent caught this during review.
- **Fix:** Builder agents must explicitly quote the source file path AND verify distinctive content
  markers (e.g., "Alternativ 1" vs "For tomten") to confirm they're reading the correct source.
  Include a source verification step in the build pipeline.
- **Applies to:** ALL Mode B builds

### PP6: Headers/Footers Assigned via Admin UI, Not Template HTML
- **Severity:** IMPORTANT
- **Discovered:** Transcript mining (Vitec Next admin UI analysis)
- **Root cause:** Headers and footers are NOT referenced from within document template HTML
- **Fix:** Headers and footers are selected per-template via dropdown selectors in Vitec Next's
  "PDF-INNSTILLINGER" admin panel. Options include "Ingen" (none), "Vitec Bunntekst Kontrakt",
  "Vitec Bunntekst Oppdragsavtale", etc. Do not attempt to embed header/footer references
  in the template HTML — they are deployment configuration, not template content.
- **Applies to:** Template deployment process

### PP7: Kartverket Protected Templates — Never Modify
- **Severity:** CRITICAL
- **Discovered:** Transcript mining (user instruction about tinglysing form protection)
- **Fix:** Tinglysing forms from Kartverket have a 4-tier protection classification:
  - **Tier 1 (NEVER modify):** 8 core forms — Skjøte, Pantedokument (sikring), Hjemmelserklæring,
    Hjemmelsoverføring, Grønt/Rødt/Blått skjema, Begjæring (Tvangssalg)
  - **Tier 2 (protected):** 2 system footers with form numbers
  - **Tier 3 (protected):** 5 attachments to Kartverket forms
  - **Tier 4 (editable):** 9 cover letters that can be customized
  Modifying Tier 1-3 templates will cause Kartverket to reject the tinglysing submission.
- **Applies to:** Template management and sync operations

---

## How to Use This Registry

1. **Before building:** Read all entries in categories E, CB, S, MF, VIF relevant to the target tier
2. **During building:** Apply all fixes proactively (don't wait for validation to catch them)
3. **After building:** Run `post_process_template.py` which automates E1, E3, CB1, S1, S2
4. **After validation:** Cross-check failures against V1 (false positives)
5. **After deploy:** Add any new lessons to this file

**Category index:** E (Encoding), CB (Checkboxes), S (Structure), MF (Merge Fields),
VIF (vitec-if Syntax), CF (Content Fidelity), V (Validation), PP (Pipeline Process)

---

## OPEN INVESTIGATIONS

Unresolved questions flagged during transcript mining and library analysis (2026-02-24).
These need testfletting verification or dedicated investigation before being codified as lessons.

### OI-1: `selger.mobiltlf` vs `selger.tlf` — When to Use Which
- **Source:** User flagged during transcript mining
- **Question:** Inside `vitec-foreach="selger in Model.selgere"`, is `selger.mobiltlf` a valid field? When should it be used vs `selger.tlf`?
- **Risk:** Using the wrong field silently renders empty or "Mangler data"
- **Next step:** Test both fields via Testfletting on a template with known seller data

### OI-2: `besoksadresse` vs `postadresse` for Party Address Fields
- **Source:** Flagged in transcript 1 as open question
- **Question:** For party entities (selger, kjoper), when should `besoksadresse` be used vs `postadresse` vs `gatenavnognr`?
- **Risk:** Wrong address field shows old/wrong address for parties with different visit/postal addresses
- **Next step:** Cross-reference with `Alle_flettekoder_25.9` field registry

### OI-3: CKEditor 4 CSS Parser Limitations
- **Source:** Multiple transcript references to CSS being "rejected" or modified by CKEditor
- **Question:** What CSS properties/selectors does CKEditor 4 strip, modify, or reject when saving?
- **Risk:** Builder agents produce valid CSS that CKEditor silently corrupts on save
- **Next step:** Build a test matrix — paste CSS blocks into CKEditor source view, save, compare output
