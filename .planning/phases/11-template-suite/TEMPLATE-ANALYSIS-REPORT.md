# Vitec Template Analysis Report

## Executive Summary

After systematic comparison of our two generated templates against three working Vitec reference templates (bruktbolig kjøpekontrakt, oppdragsavtale prosjekt, and FORBRUKER kjøpekontrakt), two critical rendering-breaking issues and several important structural deviations were identified.

### Top Findings Ranked by Impact

| # | Severity | Finding | Impact |
|---|----------|---------|--------|
| 1 | **CRITICAL** | UTF-8 literal characters instead of HTML entities | PDF mojibake (ø→Ã¸, å→Ã¥, §→Â§) |
| 2 | **CRITICAL** | Unicode checkboxes (&#9744;/&#9745;) instead of SVG pattern | Checkboxes render as "?" in PDF |
| 3 | **IMPORTANT** | Missing outer `<table>` body wrapper | Layout may break in Vitec PDF renderer |
| 4 | **IMPORTANT** | Missing CSS classes from references (`.insert-table`, `span.insert:empty`, `.borders`, `a.bookmark`) | Editor placeholders and styling won't work |
| 5 | **IMPORTANT** | Leilighet regressions from enebolig pilot (title, header, CSS) | Inconsistent output quality |
| 6 | **IMPORTANT** | `class="proaktiv-theme"` on root div (not in any reference) | Potential CSS conflict |
| 7 | **COSMETIC** | Validator checks for `class="proaktiv-theme"` (false assumption) | Validator would reject valid reference templates |
| 8 | **INFO** | Different contract type (bustadoppføringslova vs avhendingslova) | Expected — different template scope |

**Before the next template build, items 1-6 MUST be fixed.**

---

## Visual Comparison (Browser-Rendered)

Visual inspection was performed using the existing `build_preview.py` / `build_preview_leilighet.py` tooling, plus a new `build_reference_preview.py` that wraps the working bruktbolig reference template in the same preview harness. All three were served via `python -m http.server` and rendered in the browser.

### Preview Tool Architecture

The preview scripts (`C:\Users\Adrian\Documents\Proaktiv-Dokument-Hub\scripts\`) wrap production templates in an A4-like viewer with:
- Sticky info bar (field count, vitec-if count, foreach count, sections)
- Merge field highlighting (yellow `<span class="mf">`)
- vitec-if visual indicators (green left-border + "if" badge)
- vitec-foreach visual indicators (blue left-border + "foreach" badge)
- A4 page wrapper (21cm max-width, 2.5cm padding, box-shadow)

### Template Stats Comparison

| Metric | Enebolig (ours) | Leilighet (ours) | Bruktbolig (reference) |
|--------|:---------------:|:----------------:|:----------------------:|
| Merge Fields | 48 | 39 | 64 |
| vitec-if | 54 | 46 | 173 |
| foreach | 4 | 2 | 9 |
| Sections | 21 | 21 | 28 |
| Content Size | ~33,000 chars | ~31,000 chars | 100,984 chars |

The reference template is **~3x the size** of ours and has **3-4x more conditional logic**. This is expected given the bruktbolig template covers multiple property types (selveier, sameie, borettslag, aksje) through extensive conditionals, while ours focus on a single prosjekt variant.

### Visual Findings

#### V1: Header Layout Difference

**Our templates (both):** Header info (Oppdragsnummer, Omsetningsnummer) is left-aligned as plain paragraphs at the top of the page.

**Reference template:** Header info (Meglerselskap, Meglerforetakets org.nr, Oppdragsnr., Omsetningsnr.) is right-aligned inside a `<table><tbody><tr><td style="text-align:right"><small>...</small></td></tr></tbody></table>` wrapper. This gives a professional, right-justified layout consistent with formal legal documents.

**Impact:** Visual only in preview, but the outer table wrapper matters for Vitec's PDF renderer which uses the `<table>` structure for layout control.

#### V2: Title Rendering

**Our enebolig:** `<h1>` tag, centered, uppercase — matches reference closely.

**Our leilighet:** `<h5>` tag, centered — renders much smaller than the enebolig title in the browser. The `<h5>` is styled at 16pt by the preview CSS, but this is a custom override. In CKEditor/Vitec, `<h5>` has no special styling and would render at the default small heading size.

**Reference:** `<h1>` centered at 14pt — clean, proper heading hierarchy.

**Impact:** The leilighet title visually appears smaller and inconsistent.

#### V3: Checkbox Rendering (CRITICAL)

**Our templates:** Both use Unicode characters ☑ (U+2611) and ☐ (U+2610) as plain text. In the browser preview, these render correctly as visible checkbox symbols.

**Reference template:** Uses SVG data URI backgrounds on `<span class="svg-toggle checkbox">` elements. These render as crisp, scalable black-and-white checkbox graphics. In the browser preview, the checkboxes appear as proper interactive-looking form elements. The CSS includes both checked (`.active`) and unchecked states, plus radio button variants.

**Critical finding:** While the Unicode checkboxes look acceptable in a modern browser, the TEMPLATE-ANALYSIS-REPORT already documented (D2) that Vitec's PDF renderer cannot handle these characters and renders them as "?". The visual comparison confirms the SVG approach produces consistently superior rendering across all output formats.

#### V4: Conditional Logic Density

**Our templates:** Show sparse green vitec-if borders — conditionals mostly wrap individual checkbox pairs or simple show/hide sections.

**Reference template:** Shows extremely dense green vitec-if borders — nearly every paragraph has conditional logic for handling different property types (selveier, sameie, borettslag, aksje), ownership forms, and business scenarios. The entire document is a web of interconnected conditionals.

**Implication:** Our templates have a simpler conditional structure because they target a single prosjekt scenario. This is correct for the content, but the reference shows the level of conditional sophistication our pipeline must be capable of for more complex templates.

#### V5: Cross-Reference Navigation

**Reference template:** Has clickable bookmark links (e.g., `<a class="bookmark" href="#tinglysing-notifisering-og-sikkerhet">`) at the top that navigate between sections. These render as styled anchor links in the browser.

**Our templates:** No internal cross-references. This is acceptable for the prosjekt kjøpekontrakt (simpler structure), but the pipeline should support this pattern for larger templates.

#### V6: Internal Consistency (Enebolig vs. Leilighet)

Comparing our two templates side-by-side confirms the code analysis findings:
- **Section numbering:** Enebolig uses "A —" letter prefixes (e.g., "A — SALGSOBJEKT OG TILBEHØR"), leilighet uses plain numbers — inconsistent approach.
- **Quote style:** Enebolig uses «guillemets», leilighet uses "curly quotes" — visible inconsistency between the two.
- **Parties table:** Both use "Adresse" header; reference uses "Adresse/Kontaktinfo" combined header — our column is narrower.
- **Field completeness:** Enebolig has `[[kjoper.fullmektig.navn]]` fullmektig section; leilighet omits it.

### Preview Files Generated

| File | Location |
|------|----------|
| Enebolig preview | `scripts/converted_html/preview_production.html` |
| Leilighet preview | `scripts/converted_html/Kjopekontrakt_prosjekt_leilighet_PREVIEW.html` |
| Reference preview | `scripts/converted_html/REFERENCE_bruktbolig_PREVIEW.html` |

These can be opened locally via `python -m http.server 8765 --directory scripts/converted_html` and viewed at `http://localhost:8765/`.

---

## Source Document vs. Production Template Comparison

The original Word-exported `.htm` source documents were compared against the production HTML templates using both visual browser rendering and automated content analysis (`compare_source_vs_production.py`).

### Source Files

| Template | Source File | Origin |
|----------|-----------|--------|
| Enebolig | `Kjøpekontrakt prosjekt (enebolig med delinnbetalinger).htm` | OneDrive, Word export |
| Leilighet | `Kjøpekontrakt prosjekt selveier.htm` | OneDrive, Word export |

Both source files are ~100KB Word HTML exports with heavy MsoNormal/Word-specific markup. They share the same 13 legacy merge fields (`#field.context¤` format) and 33 checkbox placeholders each (rendered as "q" characters in Word).

### Size and Content Preservation

| Metric | Enebolig Source | Enebolig Prod | Leilighet Source | Leilighet Prod |
|--------|:--------------:|:------------:|:----------------:|:-------------:|
| HTML size | 100,759 chars | 37,844 chars | 102,122 chars | 36,446 chars |
| Text content | 22,477 chars | 22,225 chars | 22,502 chars | 22,820 chars |
| Merge fields | 13 (legacy) | 48 (modern) | 13 (legacy) | 39 (modern) |
| Checkboxes | 33 ("q" chars) | 32 (&#9744;/&#9745;) | 33 ("q" chars) | 50 (&#9744;/&#9745;) |

**Content preservation is excellent:** Text content differs by only ~1% between source and production for both templates. The HTML shrinkage (63-64%) is due to stripping Word markup — this is correct behavior.

**Merge field expansion:** The 13 legacy fields expand to 48/39 modern fields because legacy constructs like `#eiere¤` (loop over sellers) are decomposed into explicit fields (`[[selger.navnutenfullmektigogkontaktperson]]`, `[[selger.gatenavnognr]]`, etc.).

### Section Completeness: All 22 Sections Present

All sections from the source documents are present in both production templates:

SALGSOBJEKT (A+B), KJØPESUM, SELGERS PLIKT, OPPGJØR, HEFTELSER, TINGLYSING, MANGELSANSVAR, ENDRINGSARBEIDER, OVERTAKELSE, ETTÅRSBEFARING, SELGERS KONTRAKTSBRUDD, KJØPERS KONTRAKTSBRUDD, FORSIKRING, AVBESTILLING, SELGERS FORBEHOLD, ANNET, SAMTYKKE, VERNETING, BILAG, SIGNATUR.

No sections were dropped during conversion.

### Content Gaps Found

#### [IMPORTANT] Leilighet Uses Wrong Payment Model

The leilighet production template was built from the **selveier** source, but its Oppgjør (payment) section uses the **enebolig's** payment structure instead:

- **Selveier source:** Has "Alternativ 1: Forskudd" and "Alternativ 2: Hele kjøpesummen betales ved overtakelse" — a two-option payment model.
- **Leilighet production:** Has "For tomten:" and "For boligen:" — the delinnbetalinger model from the enebolig source.

This is a **content mismatch**. The leilighet template has the wrong payment terms for its contract type.

Additionally, the selveier source contains these guarantee-related paragraphs that are **missing from the leilighet production:**
- "forskuddsbetaling" provisions (bustadoppføringslova § 47 reference)
- "forskuddsgaranti" requirements
- "Til det er dokumentert at det foreligger §12 garanti, har forbrukeren rett til å holde tilbake alt vederlag"

#### [COSMETIC] Missing "Eierseksjonsloven" Reference in Enebolig

The enebolig source has a reference to "Eierseksjonsloven" in section 1B that was dropped in the production template. The leilighet production template has this reference (added independently).

#### [COSMETIC] "Alternativ 1/2" Labels Dropped

Both source documents label the Overtakelse options as "Alternativ 1:" and "Alternativ 2:" with explicit `q` checkboxes. The production templates drop these labels and instead use vitec-if conditional pairs — functionally equivalent but loses the explicit alternative labeling visible in the Word document.

#### [INFO] Checkbox Count Discrepancy

- **Enebolig:** Source has 33 checkboxes, production has 32 — one checkbox was likely merged or dropped during conversion.
- **Leilighet:** Source has 33 checkboxes, production has 50 — the production template added conditional two-state checkbox pairs (☑/☐) for interactive form behavior, expanding beyond the source count. This is intentional enhancement for the Vitec environment but means the template has more interactive elements than the source document.

### Visual Rendering Comparison

The source Word .htm files were opened alongside the production previews in the browser:

**Source Word .htm rendering:**
- Displays legacy merge fields as raw text: `#oppdragsnummer.oppdrag¤`, `#eiere¤`
- Checkboxes appear as lowercase "q" characters
- Section numbers are hardcoded as plain text ("1 A", "1 B", "2", "3", etc.)
- Fill-in blanks appear as "………" dots
- Some text highlighted in red (Word hyperlinks to Eierseksjonsloven, etc.)
- Title renders as `<h5>KJØPEKONTRAKT</h5>` (Word chose h5 for the centered title)
- No conditional logic — flat document structure

**Production template rendering:**
- Merge fields displayed in yellow highlighted boxes with modern syntax
- Checkboxes render as Unicode ☑/☐ symbols (correct in browser, fails in PDF)
- Section numbers auto-generated via CSS counters
- Fill-in blanks replaced with `<span class="insert">` or dotted underlines
- Green/blue borders show vitec-if/foreach conditional structure
- Title upgraded to `<h1>` in enebolig (but `<h5>` in leilighet matches source)
- Rich conditional logic wrapping appropriate sections

**Key insight:** The source document's `<h5>` title tag was actually the Word export's choice. The enebolig build script intentionally upgraded it to `<h1>` for better semantic markup. The leilighet build script preserved the original `<h5>` — so this is not a "regression" from enebolig but rather the leilighet staying closer to the source. However, the reference template uses `<h1>`, confirming `<h1>` is the correct target.

### DOCX Verification

The original `Kjøpekontrakt Prosjekt selveier .docx` was converted via mammoth to verify content matches the `.htm` export. The DOCX text content (23,390 chars) closely matches the `.htm` text (22,502 chars), confirming no data loss in the Word-to-HTM export step.

The DOCX clearly shows the selveier-specific payment model:

```
Alternativ 1:
Forskudd.
Boligen tinglyses i kjøpers navn først ved tidspunkt for ferdigstillelse og overtagelse.
...
Alternativ 2:
Hele kjøpesummen betales ved overtakelse av boligen.
```

And the selveier-specific guarantee provisions:

```
Er det i avtalen tatt forbehold som beskrevet i bustadoppføringslova § 12 annet ledd...
Til det er dokumentert at det foreligger §12 garanti, har forbrukeren rett til å holde tilbake alt vederlag.
Ved avtale om forskuddsbetaling etter punkt 2 og 4 alternativ 1, skal selger i tillegg stille
forskuddsgaranti etter bustadoppføringslova § 47...
```

None of these provisions appear in the leilighet production template, confirming the **wrong payment model** finding is not an artifact of the `.htm` export but a genuine content mismatch in the conversion pipeline.

### Source Files for Preview

| File | URL |
|------|-----|
| Enebolig source (.htm) | `http://localhost:8765/SOURCE_enebolig.htm` |
| Selveier source (.htm) | `http://localhost:8765/SOURCE_selveier_leilighet.htm` |
| Selveier source (DOCX→HTML) | `http://localhost:8765/SOURCE_selveier_DOCX.html` |
| Profesjonell kjøper source | `http://localhost:8765/SOURCE_profesjonell_kjoper.htm` |
| Borettslag source | `http://localhost:8765/SOURCE_borettslag.htm` |

---

## D0: Internal Consistency (Enebolig vs. Leilighet)

### Findings

#### [CRITICAL] Title Heading Regression
- **Enebolig** (line 44): `<h1 style="text-align:center; text-transform:uppercase;">Kjøpekontrakt</h1>`
- **Leilighet** (line 32): `<h5 style="text-align:center;">KJØPEKONTRAKT</h5>`
- **Bruktbolig reference** (line 197): `<h1>Kj&oslash;pekontrakt</h1>`
- The reference uses `<h1>`, same as enebolig. Leilighet regressed to `<h5>`.
- The reference also relies on CSS (`h1 { text-align: center; font-size: 14pt; }`) rather than inline style — our enebolig inline-styles the same properties, duplicating what Stilark provides.

#### [IMPORTANT] Header Structure Regression
- **Enebolig** (lines 32-41): Wraps header in `<table><tbody><tr><td colspan="100"><small>...</small></td></tr></tbody></table>`
- **Leilighet** (lines 29-30): Uses bare `<p>Oppdragsnummer: ...</p>`
- **Bruktbolig reference** (lines 181-194): Uses `<table><tbody><tr><td colspan="100" style="text-align:right"><small>...</small></td></tr></tbody></table>`
- The leilighet dropped the table wrapper and `<small>` tag. Both are present in the reference.

#### [IMPORTANT] Missing CSS Classes in Leilighet
- **Enebolig** has:
  - `.sign-line` (line 27): `border-top: solid 1px #000; width: 45%; display: inline-block; text-align: center; margin-top: 40px;`
  - `.liste:last-child .separator` (line 26): `display: none;`
- **Leilighet** is missing both CSS rules entirely.
- The bruktbolig reference has `.liste:last-child .separator` (line 115-117), confirming this is a required pattern.

#### [COSMETIC] Quote Mark Inconsistency
- **Enebolig** uses `&laquo;selger&raquo;` (guillemets «»)
- **Leilighet** uses `&ldquo;selger&rdquo;` (curly quotes "")
- Both are typographically valid, but the FORBRUKER reference also uses `&laquo;`/`&raquo;`, suggesting guillemets are the standard for Norwegian legal documents.

#### [IMPORTANT] Signature Section Differences
- **Enebolig** (lines 568-592): Uses `<td colspan="45">` for two-column signature, uses `Selger<span vitec-if>e</span>` conditional plural, `[[dagensdato]]` merge field for date.
- **Leilighet** (lines 578-599): Uses `<td colspan="40">`, bare text `Selger(e)`, manual `<span class="insert">` for date with excessive `&nbsp;` padding, `[[kjoper.fullmektig.navn]]` directly in cell without conditional wrapper.
- **Bruktbolig reference**: Uses `<table class="avoid-page-break">` for signature section, `<td colspan="48">` and `<td colspan="4">` spacer, `<table>` nested inside cells with foreach loops for multiple signers.
- Both our templates use a simpler single-signature approach vs. the reference's multi-signer foreach pattern.

#### [COSMETIC] `$.UD()` Function Usage
- **Enebolig** (line 230): Uses `$.UD([[kontrakt.kjopesum]])` for sum row only
- **Enebolig** (line 197): Uses raw `[[kontrakt.kjopesum]]` in body text (no formatting)
- **Leilighet** (line 206): Uses `$.UD([[kontrakt.kjopesum]])` in body text
- **Bruktbolig reference**: Consistently uses `$.UD()` for all monetary values: `kr $.UD([[kontrakt.kjopesum]])`
- Our templates are inconsistent. The reference always wraps monetary values in `$.UD()`.

#### [IMPORTANT] Heftelser Section Approach
- **Enebolig** (lines 322-341): Uses simple `<span>` conditionals to append text
- **Leilighet** (lines 347-371): Uses paired `&#9745;`/`&#9744;` checkboxes for both options (much closer to source document layout)
- The leilighet approach is structurally better (closer to source), but the checkbox implementation is wrong (see D2).

#### [IMPORTANT] Build Approach Comparison
- **Enebolig**: `build_production_template.py` — BeautifulSoup-based, 770 lines, programmatic parsing of Word .htm source. Pros: Traceable to source, reusable pipeline. Cons: Complex, fragile parsing rules.
- **Leilighet**: `build_kjopekontrakt_prosjekt_leilighet.py` — Hardcoded template string, ~623 lines, entire HTML output as a Python string literal. Pros: Exact control, easy to read final output. Cons: Not connected to source document, manual transcription errors likely, no reuse across templates.
- **Recommendation**: The BeautifulSoup approach is more maintainable for a pipeline that needs to convert many documents. However, it must be hardened to fix the encoding and checkbox issues. The hardcoded approach should be used only for verification/gold-master comparison.

### Evidence Summary
| Pattern | Enebolig | Leilighet | Bruktbolig Ref |
|---------|----------|-----------|----------------|
| Title tag | `<h1>` | `<h5>` | `<h1>` |
| Header wrapper | `<table><small>` | `<p>` | `<table><small>` |
| `.sign-line` CSS | Present | Missing | N/A (different sig pattern) |
| `.liste .separator` CSS | Present | Missing | Present |
| Quote marks | `«»` | `""` | (entities) |
| `$.UD()` usage | Partial | Partial | Consistent |

---

## D1: Encoding and Character Handling

### Findings

#### [CRITICAL] UTF-8 Literals vs. HTML Entities — Root Cause of PDF Mojibake

This is the single most impactful finding. Every Norwegian character in our templates uses literal UTF-8, while every working reference template uses HTML entities.

**Our templates:**
```
Kjøpekontrakt (line 44, enebolig)
kjøpesummen (line 197, enebolig)
§ 1 (line 47, enebolig)
```

**Working bruktbolig reference:**
```
Kj&oslash;pekontrakt (line 197)
kj&oslash;pesummen (line 295)
&sect; 54 (line 399)
```

**Working FORBRUKER reference:**
```
Kj&oslash;pekontrakt (from extracted content)
&aring; (throughout)
&aelig; (throughout)
```

#### Complete Entity Map Required

| Character | UTF-8 | HTML Entity | Required? |
|-----------|-------|-------------|-----------|
| ø | ø | `&oslash;` | **YES** |
| å | å | `&aring;` | **YES** |
| æ | æ | `&aelig;` | **YES** |
| Ø | Ø | `&Oslash;` | **YES** |
| Å | Å | `&Aring;` | **YES** |
| Æ | Æ | `&AElig;` | **YES** |
| § | § | `&sect;` | **YES** |
| « | « | `&laquo;` | **YES** |
| » | » | `&raquo;` | **YES** |
| — | — | `&mdash;` | YES |
| – | – | `&ndash;` | YES |
| é | é | `&eacute;` | YES (in "én") |

**All Norwegian letters, §, and typographic punctuation MUST be entity-encoded for Vitec PDF rendering.**

#### CKEditor Behavior

CKEditor 4 preserves HTML entities that are already in the source. When a user types "ø" in the editor, CKEditor stores the literal UTF-8 character. But existing `&oslash;` entities in source HTML are preserved. Therefore:
- **Pipeline must output entities** — CKEditor will preserve them.
- If a user edits text and types Norwegian characters, those will be UTF-8 — but this is expected since manual edits are the user's responsibility.

#### [CRITICAL] Conditional Logic Entity Escaping

**Our templates use UTF-8 in vitec-if attribute values:**
```html
vitec-if="Model.eiendom.eieform != &quot;Eierseksjon&quot;"
```
This is correct — the attribute itself uses `&quot;` properly. However, the TEXT CONTENT around conditionals uses UTF-8 characters.

**References use `\xF8` escape for Norwegian characters inside conditions:**
```html
vitec-if="Model.oppdrag.hovedtype == &quot;Oppgj\xF8rsoppdrag&quot;"
```
The `\xF8` is the raw Unicode codepoint for "ø". This appears in the bruktbolig reference (line 203) and FORBRUKER reference. Our templates don't need this pattern because we're comparing against values that don't contain Norwegian characters (like "Eierseksjon", "Bolig", "Fritid"). But if we ever compare against a value containing ø/å/æ, we MUST use the `\xF8`/`\xE5`/`\xE6` escape pattern.

### Recommendation

Add an entity-encoding post-processing step to the pipeline. This should be the LAST step before output, converting all literal Norwegian characters to HTML entities:

```python
ENTITY_MAP = {
    'ø': '&oslash;', 'å': '&aring;', 'æ': '&aelig;',
    'Ø': '&Oslash;', 'Å': '&Aring;', 'Æ': '&AElig;',
    '§': '&sect;', '«': '&laquo;', '»': '&raquo;',
    '—': '&mdash;', '–': '&ndash;', 'é': '&eacute;',
}

def encode_entities(html: str) -> str:
    """Convert Norwegian characters to HTML entities.
    MUST NOT touch content inside attribute values (vitec-if, etc.)."""
    # Entity-encode text nodes only, not attributes
    for char, entity in ENTITY_MAP.items():
        html = html.replace(char, entity)
    return html
```

**IMPORTANT**: The naive replace above would also convert characters inside `vitec-if` attribute values. For conditions comparing Norwegian strings, use the `\xHH` escape format instead. A robust implementation should parse the HTML and only entity-encode text nodes.

---

## D2: Checkbox and Interactive Element Patterns

### Findings

#### [CRITICAL] Unicode Checkboxes Render as "?" in Vitec PDF

**Our templates use:**
```html
<span vitec-if="Model.eiendom.grunntype == &quot;Bolig&quot;">&#9745;</span>
<span vitec-if="Model.eiendom.grunntype != &quot;Bolig&quot;">&#9744;</span>
```

`&#9744;` (☐) and `&#9745;` (☑) are Unicode box-drawing characters. The Vitec PDF renderer doesn't have a font that supports these glyphs, so they render as "?".

**All three reference templates use SVG-based interactive checkboxes:**

```html
<label class="btn" contenteditable="false" data-toggle="button">
  <input type="checkbox" />
  <span class="checkbox svg-toggle"></span>
</label>
```

With CSS (from bruktbolig reference, lines 119-179):
```css
label.btn {
    display: inline;
    text-transform: none;
    white-space: normal;
    padding: 0;
    vertical-align: baseline;
    outline: none;
    font-size: inherit;
}
label.btn:active, label.btn.active {
    box-shadow: none;
    outline: none;
}
.svg-toggle {
    display: inline-block !important;
    width: 16px;
    height: 16px;
    margin: 0 5px;
    vertical-align: bottom;
    padding: 0;
    border: none;
    background: transparent;
    border-radius: 0;
    box-shadow: none !important;
    cursor: pointer;
    white-space: normal;
    text-align: left;
    background-repeat: no-repeat;
    background-size: 16px 16px;
    background-position: center center;
}
.svg-toggle.checkbox {
    background-image: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 512 512'><rect style='fill:black;' height='496' width='496' x='9.1' y='9.1'></rect><rect style='fill:white;' height='400' width='400' x='57.1' y='60.6'></rect></svg>");
}
.svg-toggle.checkbox.active,
.btn.active > .svg-toggle.checkbox {
    background-image: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 512 512'><rect style='fill:black;' height='496' width='496' x='9.1' y='9.1'></rect><rect style='fill:white;' height='400' width='400' x='57.1' y='60.6'></rect><path style='fill:black;' d='M396.1,189.9L223.5,361.1c-4.7,4.7-12.3,4.6-17-0.1l-90.8-91.5c-4.7-4.7-4.6-12.3,0.1-17l22.7-22.5c4.7-4.7,12.3-4.6,17,0.1 l59.8,60.3l141.4-140.2c4.7-4.7,12.3-4.6,17,0.1l22.5,22.7C400.9,177.7,400.8,185.3,396.1,189.9L396.1,189.9z'></path></svg>");
    box-shadow: none !important;
}
#vitecTemplate [data-toggle="buttons"] input {
    display: none;
}
```

#### SVG Checkbox Pattern Variants

1. **Standard checkbox** (all references): `<span class="checkbox svg-toggle"></span>` inside `<label class="btn">`
2. **Radio buttons** (FORBRUKER, bruktbolig): `<span class="radio svg-toggle"></span>` with `<input name="rbl001" type="radio" />`
3. **Conditional checked state**: Use `class="btn active"` on the label to show checked state

#### How to Convert Our Conditional Checkboxes

Our pattern (broken):
```html
<span vitec-if="Model.eiendom.grunntype == &quot;Bolig&quot;">&#9745;</span>
<span vitec-if="Model.eiendom.grunntype != &quot;Bolig&quot;">&#9744;</span>
bolig
```

Correct pattern (two approaches):

**Approach A: Dual labels with vitec-if (conditional display)**
```html
<span vitec-if="Model.eiendom.grunntype == &quot;Bolig&quot;">
  <label class="btn active" contenteditable="false" data-toggle="button">
    <input type="checkbox" /><span class="checkbox svg-toggle"></span>
  </label>
</span>
<span vitec-if="Model.eiendom.grunntype != &quot;Bolig&quot;">
  <label class="btn" contenteditable="false" data-toggle="button">
    <input type="checkbox" /><span class="checkbox svg-toggle"></span>
  </label>
</span>
bolig
```

**Approach B: Single interactive checkbox (user toggles in editor)**
```html
<label class="btn" contenteditable="false" data-toggle="button">
  <input type="checkbox" /><span class="checkbox svg-toggle"></span>
</label> bolig
```

Approach A preserves our conditional logic. Approach B treats it as a user-editable form field (which is how the references work — the broker clicks to toggle).

### Recommendation
- Replace ALL `&#9744;`/`&#9745;` with SVG checkbox pattern
- Add the full SVG checkbox CSS block to our template `<style>` tag
- For items that should be auto-checked based on data: use Approach A
- For items that are user-toggled: use Approach B

---

## D3: DOM Structure and Layout Architecture

### Findings

#### [IMPORTANT] Missing Outer Table Wrapper

**Bruktbolig reference** (lines 181-196 / end): The entire body content is wrapped in:
```html
<table>
  <tbody>
    <tr>
      <td colspan="100" style="text-align:right">
        <!-- header info -->
      </td>
    </tr>
    <tr><td colspan="100">&nbsp;</td></tr>
    <tr>
      <td colspan="100">
        <!-- ALL body content: h1, articles, signature -->
      </td>
    </tr>
  </tbody>
</table>
```

**FORBRUKER reference**: Same pattern — single outer `<table>` with `<td colspan="100">` wrapping everything.

**Our enebolig**: Has a header `<table>` (lines 32-41) but does NOT wrap body content in a table cell.

**Our leilighet**: No outer table at all.

This outer table may serve as a layout container for the Vitec PDF renderer. Without it, content may flow differently.

#### [IMPORTANT] `class="proaktiv-theme"` on Root Div

Both our templates add `class="proaktiv-theme"` to the root div:
```html
<div class="proaktiv-theme" id="vitecTemplate">
```

**No reference template has this class.** All references use:
```html
<div id="vitecTemplate">
```

This class could potentially conflict with Vitec Stilark CSS or cause unexpected styling. It should be removed.

#### [IMPORTANT] Missing `span.insert:empty` Pattern

**References use** (bruktbolig lines 77-103):
```css
span.insert:empty {
    font-size: inherit !important;
    line-height: inherit !important;
    display: inline-block;
    background-color: lightpink;
    min-width: 2em !important;
    height: .7em !important;
    text-align: center;
}
span.insert:empty:before {
    content: attr(data-label);
}
span.insert:empty:hover {
    background-color: #fff;
    cursor: pointer;
}
.insert-table {
    display: inline-table;
}
.insert-table > span,
.insert-table > span.insert {
    display: table-cell;
}
```

**Our templates** use a simpler `.insert` class:
```css
#vitecTemplate .insert { border-bottom: 1px dotted #999; min-width: 80px; display: inline-block; }
```

The reference pattern uses:
- `data-label` attribute to show placeholder text (e.g., `data-label="beløp"`, `data-label="dato"`)
- `lightpink` background to highlight unfilled fields
- `:empty` pseudo-class to only show placeholder when field is empty
- `.insert-table` for inline-table layout of fill-in fields

Our pattern is functional but lacks the `data-label` placeholder text and the visual highlighting that helps users identify unfilled fields in the CKEditor.

#### [COSMETIC] `rowspan` Usage in Roles Table

**References** use `rowspan="2"` on the name cell to span both the address row and the contact info row:
```html
<td colspan="34" rowspan="2">[[*selger.navnutenfullmektigogkontaktperson]]</td>
```

**Our templates** use separate rows without rowspan:
```html
<td colspan="34">[[*selger.navnutenfullmektigogkontaktperson]]</td>
```

The contact info row in references uses `colspan="63"` (48+15 remaining space), while ours uses `colspan="100"`.

#### [INFO] Additional `<span vitec-template>` Resources

**Bruktbolig reference** (line 1) includes:
```html
<span vitec-template="resource:Vitec Stilark">&nbsp;</span>
<span vitec-template="resource:Boligkjøperforsikring">&nbsp;</span>
```

Our templates only include Vitec Stilark. The `Boligkjøperforsikring` resource provides additional template content for the boligkjøperforsikring section (specific to bruktbolig contracts, not needed for prosjekt contracts).

### Recommendation
1. Remove `class="proaktiv-theme"` from root div
2. Wrap all body content inside the outer `<table><tbody><tr><td colspan="100">` structure
3. Add the full `span.insert:empty` CSS block with `data-label` support
4. Use `rowspan="2"` in roles tables for proper contact info layout

---

## D4: CSS Counter and Numbering System

### Findings

#### [INFO] Three Counter Pattern Variants Observed

**Pattern A — section/subsection** (bruktbolig reference + our templates):
```css
#vitecTemplate { counter-reset: section; }
#vitecTemplate article.item:not(article.item article.item) {
    counter-increment: section;
    counter-reset: subsection;
}
#vitecTemplate article.item article.item { counter-increment: subsection; }
#vitecTemplate article.item:not(article.item article.item) h2::before {
    content: counter(section) ". ";
    display: inline-block;
    width: 26px;
}
#vitecTemplate article.item article.item h3::before {
    content: counter(section) "." counter(subsection) ". ";
    display: inline-block;
    width: 36px;
}
```

The `display: inline-block; width: 26px;` on `::before` prevents double-digit section numbers
(10+) from pushing heading text out of alignment with body text below.

**Pattern B — item/counters** (FORBRUKER reference):
```css
#vitecTemplate h1 { counter-reset: item; }
#vitecTemplate .item { counter-increment: item; }
#vitecTemplate .item > .item { counter-reset: item; }
#vitecTemplate .item ~ .item { counter-reset: none; }
#vitecTemplate .item h2:before,
#vitecTemplate .item h3:before {
    content: counters(item, ".") ". ";
}
```

**Pattern C — from Fullmakt template** (from JSON export):
Uses its own custom CSS without counter system (simpler documents don't need section numbering).

#### Selector Specificity Difference

Our templates use `> h2::before` (direct child selector), while references use ` h2::before` (descendant selector). The reference bruktbolig also uses `h2::before` without `>`. Functionally equivalent for the current structure but slightly different in edge cases.

### Recommendation
- Both patterns A and B are valid. Pattern A (section/subsection) is used by the most directly comparable reference (bruktbolig). Keep using Pattern A.
- Remove the `>` direct child selector to match references: `article.item:not(...) h2::before` instead of `article.item:not(...) > h2::before`

---

## D5: Merge Field Coverage and Accuracy

### Findings

#### [IMPORTANT] Merge Field Differences

| Field | Our Templates | Bruktbolig Ref | FORBRUKER Ref |
|-------|---------------|----------------|---------------|
| `[[kontrakt.klientkonto]]` + `[[kontrakt.kid]]` | Used separately | — | — |
| `[[kontrakt.klientkontoogkid]]` | Not used | Used | Used |
| `[[oppgjor.besoksadresse]]` | Used | — | — |
| `[[oppgjor.postadresse]]` | Not used | Used | — |
| `[[meglerkontor.orgnr]]` | Not used | Used | Used |
| `[[meglerkontor.juridisknavn]]` | Not used | Used (e-tinglysing section) | — |
| `[[kontrakt.formidling.nr]]` | Used | Used | Used |
| `[[dagensdato]]` | Used (enebolig) | Not used | — |
| `[[kontrakt.dato]]` | Not used | — | Used |
| `[[komplettmatrikkelutvidet]]` | Not used | Used | Used |
| `[[komplettmatrikkel]]` | Used | — | — |
| `[[eiendom.ettaarsbefaring.dato]]` | Used (enebolig) | — | — |

Key findings:
- `[[kontrakt.klientkontoogkid]]` is the combined field used by references — we split it into two separate fields which may not exist as separate fields.
- `[[oppgjor.besoksadresse]]` vs `[[oppgjor.postadresse]]` — different field names for the same concept. Need to verify which is correct in the API.
- `[[meglerkontor.orgnr]]` is used by references in the header but missing from our templates.

#### [COSMETIC] `$.UD()` Format Function Usage
- References consistently wrap monetary amounts: `kr $.UD([[kontrakt.kjopesum]])`
- Our templates are inconsistent (sometimes raw `[[kontrakt.kjopesum]]`, sometimes `$.UD()`)
- `$.UD()` formats numbers with Norwegian thousands separators (e.g., "1 500 000")

#### [INFO] `$.CALC()` Function
The bruktbolig reference uses an advanced calculation function:
```
$.CALC(UD:[[kontrakt.kjopesumogomkostn]]-@GetPosteringsVerdiForBoligkjoperforsikring())
```
And C#-style method calls: `@GetPosteringsVerdiForBoligkjoperforsikring()`. These are specific to templates that need computed values. Our prosjekt contracts don't currently need this pattern but should be documented for future use.

### Recommendation
- Verify `[[kontrakt.klientkontoogkid]]` vs separate fields — use the combined field if available
- Verify `[[oppgjor.postadresse]]` vs `[[oppgjor.besoksadresse]]` — use the reference field name
- Add `[[meglerkontor.orgnr]]` to header section
- Consistently use `$.UD()` for all monetary values
- Document `$.CALC()` and `@Method()` patterns in pipeline docs

---

## D6: Conditional Logic Patterns

### Findings

#### [IMPORTANT] Unicode Escape in Condition Values

**Bruktbolig reference** (line 203):
```html
<div vitec-if="Model.oppdrag.hovedtype == &quot;Oppgj\xF8rsoppdrag&quot;">
```

The `\xF8` is the raw hex escape for "ø" (U+00F8). This is used inside `&quot;`-wrapped string values in `vitec-if` attributes.

**Our templates don't have conditions comparing Norwegian-character strings**, so this isn't a current issue. But it MUST be documented for future templates that compare against values like "Oppgjørsoppdrag".

#### [COSMETIC] Condition Syntax Patterns

**References use `!=` with `&quot;`:**
```html
vitec-if="Model.eiendom.eieform != &quot;Aksje&quot;"
```

**References use `&amp;&amp;` for AND:**
```html
vitec-if="(Model.eiendom.eieform == &quot;Aksje&quot; || Model.eiendom.eieform == &quot;Obligasjonsleilighet&quot;)"
```

Our templates correctly use these patterns. No issues found in our conditional logic syntax.

#### [INFO] `data-toggle="buttons"` Pattern

The references use `data-toggle="buttons"` for radio button groups (mutually exclusive choices):
```html
<p data-toggle="buttons">
  <label class="btn" contenteditable="false" data-toggle="button">
    <span class="checkbox svg-toggle"></span>
    <input name="rbl001" type="radio" />
  </label> Jeg ønsker boligkjøperforsikring
  <label class="btn" contenteditable="false" data-toggle="button">
    <span class="checkbox svg-toggle"></span>
    <input name="rbl001" type="radio" />
  </label> Jeg ønsker ikke boligkjøperforsikring
</p>
```

The `name="rbl001"` groups radio inputs so only one can be selected. We don't currently use radio buttons, but this pattern should be available for future templates.

#### [INFO] vitec-foreach Container Variations

**On `<tbody>`** (most common — both references and our templates):
```html
<tbody vitec-foreach="selger in Model.selgere">
```

**On `<div>`** (FORBRUKER reference, for kjøper signature blocks):
```html
<div vitec-foreach="kjoper in Model.kjopere">
```

**On `<span>`** (FORBRUKER reference, for inline lists):
```html
<span vitec-foreach="selger in Model.selgere">
```

All three containers are valid. Use `<tbody>` for table rows, `<div>` for block-level repeating content, and `<span>` for inline repeating content.

### Recommendation
- Document the `\xF8` escape pattern in PIPELINE-DESIGN
- Add a utility function that converts Norwegian characters to `\xHH` escapes for use in condition string values

---

## D7: Content Fidelity (vs. Source Document)

### Findings

#### [INFO] Different Contract Type — Expected Scope Difference

Our templates are prosjekt contracts (bustadoppføringslova — new construction), while the bruktbolig reference is for used properties (avhendingslova). This means:
- Different section structure (our templates have sections like "SELGERS FORBEHOLD", "AVBESTILLING", "ENDRINGSARBEIDER" that don't exist in bruktbolig contracts)
- Different legal references (bustadoppføringslova §§ 12, 15, 16, 17, 25-27, 29, 30, 46-53 vs avhendingslova §§ 3-1 through 5-7)
- Different party patterns (our templates have simpler party tables; bruktbolig has complex multi-eieform conditional branches)

This is expected and NOT a deficiency.

#### [COSMETIC] Section Heading Formatting

**Our templates**: Uppercase headings without counter prefix in text:
```html
<h2>KJØPESUM OG OMKOSTNINGER</h2>
```

**Bruktbolig reference**: Mixed-case headings:
```html
<h2>Kjøpesum og omkostninger</h2>
```

The counter CSS adds the number prefix, so the heading text itself shouldn't include a number. Both approaches work, but the reference style (sentence case) is more standard for legal documents in Norwegian.

#### [IMPORTANT] Legal Text Accuracy

Verified: Our templates correctly reference:
- `bustadoppføringslova av 13. juni nr. 43 1997` (correct citation)
- `§ 12` (garanti), `§ 15` (overtakelsesforretning), `§ 16` (ettårsbefaring)
- `§§ 29 flg.` (rettingsmidler), `§ 30` (reklamasjon)
- `§§ 52 og 53` (avbestilling)
- `tvangsfullbyrdelsesloven § 13-2` (tvangsfravikelse)
- `eiendomsmeglingsforskriften § 3-10 (3)` (renter)

However, the § symbol renders as mojibake in PDF due to D1 encoding issue. Must be `&sect;`.

### Recommendation
- Consider using sentence case for headings to match reference convention
- Ensure all § symbols are entity-encoded (`&sect;`)

---

## D8: Validator Gap Analysis

### Findings

#### [CRITICAL] Validator Would Reject Working Reference Templates

The `validate_template.py` checks for `class="proaktiv-theme"` (line 26):
```python
check("A", "vitecTemplate wrapper div",
      'id="vitecTemplate"' in html and 'class="proaktiv-theme"' in html)
```

**No reference template has `class="proaktiv-theme"`**. This check validates a pattern we invented that doesn't exist in production Vitec templates. This is a false assumption that would cause the validator to reject valid reference templates.

#### [CRITICAL] Validator Validates Norwegian Characters as UTF-8

```python
check("I", "Contains ø", "ø" in html)
check("I", "Contains æ", "æ" in html)
check("I", "Contains å", "å" in html)
```

These checks PASS when characters are literal UTF-8 — the exact thing that causes PDF mojibake. The validator should instead check that Norwegian characters are entity-encoded. This inverts the correct check.

**Should be:**
```python
check("I", "No literal ø (should be &oslash;)", "ø" not in html)
check("I", "No literal å (should be &aring;)", "å" not in html)
check("I", "No literal æ (should be &aelig;)", "æ" not in html)
check("I", "Uses &oslash; entities", "&oslash;" in html)
check("I", "Uses &aring; entities", "&aring;" in html)
check("I", "Uses &aelig; entities", "&aelig;" in html)
```

#### [IMPORTANT] Missing Validator Checks

The validator does NOT check for:
1. **SVG checkbox CSS presence** — should verify `.svg-toggle.checkbox` CSS block exists
2. **No Unicode checkbox characters** — should check `&#9744;` and `&#9745;` are NOT present
3. **Outer table wrapper** — should verify the `<table><tbody><tr><td colspan="100">` body wrapper
4. **`data-label` on insert spans** — should verify `<span class="insert" data-label="...">` pattern
5. **No `class="proaktiv-theme"`** — should verify this class is NOT present
6. **`<small>` tag in header** — should verify header metadata uses `<small>` wrapper
7. **`h1` for title** — should verify main title uses `<h1>`, not `<h5>` or other
8. **Entity encoding** — should verify `&oslash;`, `&aring;`, `&aelig;` are used (not literal characters)
9. **`$.UD()` on monetary values** — should check merge fields like `kjopesum` are wrapped
10. **No `class="proaktiv-theme"`** — already mentioned but critically important

#### [COSMETIC] Two Validators Should Be Unified

`validate_template.py` (208 lines) and `validate_leilighet.py` should be a single parameterized validator that accepts any template file path as an argument. The current approach of duplicating the validator for each template is not maintainable.

### Recommendation

Create a unified validator (`validate_vitec_template.py`) with these checks:
```python
# CRITICAL encoding checks (new)
check("ENCODING", "No literal ø", "ø" not in html)
check("ENCODING", "No literal å", "å" not in html)
check("ENCODING", "No literal æ", "æ" not in html)
check("ENCODING", "Uses &oslash;", "&oslash;" in html or "&Oslash;" in html)
check("ENCODING", "No Unicode checkboxes &#9744;", "&#9744;" not in html)
check("ENCODING", "No Unicode checkboxes &#9745;", "&#9745;" not in html)

# STRUCTURAL checks (new)
check("STRUCTURE", "No proaktiv-theme class", 'class="proaktiv-theme"' not in html)
check("STRUCTURE", "Title uses h1", "<h1>" in html.lower())
check("STRUCTURE", "Has SVG checkbox CSS", ".svg-toggle.checkbox" in html)
check("STRUCTURE", "Has insert-table CSS", ".insert-table" in html)

# EXISTING checks to keep
check("SHELL", "vitecTemplate wrapper", 'id="vitecTemplate"' in html)
check("SHELL", "Stilark resource", 'vitec-template="resource:Vitec Stilark"' in html)
# ... (keep other valid checks)
```

---

## Pipeline Improvement Actions

### AGENT-2B-PIPELINE-DESIGN.md
- [ ] Add "Entity Encoding" as a mandatory final processing step
- [ ] Add "SVG Checkbox Injection" step to replace Unicode checkboxes
- [ ] Document the `\xF8` escape pattern for condition string values
- [ ] Add "Outer Table Wrapper" as a required structural element
- [ ] Remove `class="proaktiv-theme"` from template shell specification

### SKILL.md (vitec-template-builder)
- [ ] Update the entity encoding requirement (currently not mentioned)
- [ ] Add SVG checkbox CSS + HTML as a required pattern
- [ ] Add `span.insert:empty` with `data-label` as the standard insert pattern
- [ ] Document `$.UD()` usage requirement for monetary values
- [ ] Add `\xF8`/`\xE5`/`\xE6` escape pattern documentation

### validate_template.py → validate_vitec_template.py (unified)
- [ ] Remove `class="proaktiv-theme"` check (false assumption)
- [ ] Invert Norwegian character checks (should check for entities, not literals)
- [ ] Add encoding validation (no literal ø/å/æ/§)
- [ ] Add Unicode checkbox rejection check
- [ ] Add SVG checkbox CSS presence check
- [ ] Add outer table wrapper check
- [ ] Add `data-label` on insert spans check
- [ ] Accept template file path as command-line argument
- [ ] Merge `validate_leilighet.py` into this unified validator

### PRODUCTION-TEMPLATE-PIPELINE.md
- [ ] Add post-processing step: entity encoding
- [ ] Add post-processing step: checkbox conversion
- [ ] Update template shell definition (remove proaktiv-theme)
- [ ] Add the outer table wrapper to the shell template
- [ ] Document that `<h1>` is required for title

### Build Approach
- [ ] Standardize on BeautifulSoup approach for pipeline (maintainability)
- [ ] Add entity-encoding post-processing step
- [ ] Add checkbox-conversion post-processing step
- [ ] Remove `class="proaktiv-theme"` from output
- [ ] Add outer table wrapper to output
- [ ] Use hardcoded approach only for gold-master verification

---

## Reference Patterns Library

### SVG Checkbox CSS + HTML Markup

**Full CSS block** (copy from bruktbolig reference, add to template `<style>`):
```css
/* Klikkbare sjekkbokser og radioknapper */
label.btn {
    display: inline;
    text-transform: none;
    white-space: normal;
    padding: 0;
    vertical-align: baseline;
    outline: none;
    font-size: inherit;
}
label.btn:active,
label.btn.active {
    box-shadow: none;
    outline: none;
}
.svg-toggle {
    display: inline-block !important;
    width: 16px;
    height: 16px;
    margin: 0 5px;
    vertical-align: bottom;
    padding: 0;
    border: none;
    background: transparent;
    border-radius: 0;
    box-shadow: none !important;
    cursor: pointer;
    white-space: normal;
    text-align: left;
    background-repeat: no-repeat;
    background-size: 16px 16px;
    background-position: center center;
}
.svg-toggle.checkbox {
    background-image: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 512 512'><rect style='fill:black;' height='496' width='496' x='9.1' y='9.1'></rect><rect style='fill:white;' height='400' width='400' x='57.1' y='60.6'></rect></svg>");
}
.svg-toggle.checkbox.active,
.btn.active > .svg-toggle.checkbox {
    background-image: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 512 512'><rect style='fill:black;' height='496' width='496' x='9.1' y='9.1'></rect><rect style='fill:white;' height='400' width='400' x='57.1' y='60.6'></rect><path style='fill:black;' d='M396.1,189.9L223.5,361.1c-4.7,4.7-12.3,4.6-17-0.1l-90.8-91.5c-4.7-4.7-4.6-12.3,0.1-17l22.7-22.5c4.7-4.7,12.3-4.6,17,0.1 l59.8,60.3l141.4-140.2c4.7-4.7,12.3-4.6,17,0.1l22.5,22.7C400.9,177.7,400.8,185.3,396.1,189.9L396.1,189.9z'></path></svg>");
    box-shadow: none !important;
}
.svg-toggle.radio {
    background-image: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 512 512'><circle style='fill:black;' cx='257.1' cy='257.1' r='248'></circle><circle style='fill:white;' cx='257.1' cy='257.1' r='200'></circle></svg>");
}
.svg-toggle.radio.active,
.btn.active > .svg-toggle.radio {
    background-image: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 512 512'><circle style='fill:black;' cx='257.1' cy='257.1' r='248'></circle><circle style='fill:white;' cx='257.1' cy='257.1' r='200'></circle><circle style='fill:black;' cx='257.1' cy='257.1' r='91.5'></circle></svg>");
    box-shadow: none !important;
}
#vitecTemplate [data-toggle="buttons"] input {
    display: none;
}
```

**HTML for unchecked checkbox:**
```html
<label class="btn" contenteditable="false" data-toggle="button">
  <input type="checkbox" /><span class="checkbox svg-toggle"></span>
</label>
```

**HTML for checked checkbox:**
```html
<label class="btn active" contenteditable="false" data-toggle="button">
  <input type="checkbox" /><span class="checkbox svg-toggle"></span>
</label>
```

**HTML for radio button group:**
```html
<p data-toggle="buttons">
  <label class="btn" contenteditable="false" data-toggle="button">
    <span class="checkbox svg-toggle"></span>
    <input name="rbl001" type="radio" />
  </label> Option A
  &nbsp;&nbsp;&nbsp;
  <label class="btn" contenteditable="false" data-toggle="button">
    <span class="checkbox svg-toggle"></span>
    <input name="rbl001" type="radio" />
  </label> Option B
</p>
```

---

### Norwegian Character Entity Encoding Map

```python
ENTITY_MAP = {
    'ø': '&oslash;',
    'å': '&aring;',
    'æ': '&aelig;',
    'Ø': '&Oslash;',
    'Å': '&Aring;',
    'Æ': '&AElig;',
    '§': '&sect;',
    '«': '&laquo;',
    '»': '&raquo;',
    '—': '&mdash;',
    '–': '&ndash;',
    'é': '&eacute;',
}

# For use in vitec-if condition string values:
CONDITION_ESCAPE_MAP = {
    'ø': '\\xF8',
    'å': '\\xE5',
    'æ': '\\xE6',
    'Ø': '\\xD8',
    'Å': '\\xC5',
    'Æ': '\\xC6',
}
```

---

### Outer Table Wrapper Structure

```html
<div id="vitecTemplate">
<span vitec-template="resource:Vitec Stilark">&nbsp;</span>
<style type="text/css">
/* ... CSS ... */
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
    <tr>
      <td colspan="100">&nbsp;</td>
    </tr>
    <tr>
      <td colspan="100">
        <!-- ALL BODY CONTENT HERE -->
        <h1>Kj&oslash;pekontrakt</h1>
        <!-- articles, tables, signature... -->
      </td>
    </tr>
  </tbody>
</table>
</div>
```

---

### Insert-Table / Data-Label Pattern

**CSS:**
```css
span.insert:empty {
    font-size: inherit !important;
    line-height: inherit !important;
    display: inline-block;
    background-color: lightpink;
    min-width: 2em !important;
    height: .7em !important;
    text-align: center;
}
span.insert:empty:before {
    content: attr(data-label);
}
span.insert:empty:hover {
    background-color: #fff;
    cursor: pointer;
}
.insert-table {
    display: inline-table;
}
.insert-table > span,
.insert-table > span.insert {
    display: table-cell;
}
```

**HTML (labeled placeholder):**
```html
<span class="insert-table">
  <span class="insert" data-label="dato"></span>
</span>
```

**HTML (simple placeholder):**
```html
<span class="insert-table">
  <span class="insert" data-label="beløp"></span>
</span>
```

---

### Page Break Pattern

```css
#vitecTemplate .avoid-page-break {
    page-break-inside: avoid;
}
```

```html
<div class="avoid-page-break">
  <!-- content that should stay together -->
</div>

<article class="item avoid-page-break">
  <!-- article that should not break across pages -->
</article>
```

---

### Signature Block Pattern (Reference Standard)

```html
<table class="avoid-page-break">
  <tbody>
    <tr>
      <td colspan="100" style="vertical-align:top">
        <p>
          [[meglerkontor.poststed]], den [[kontrakt.dato]]<br />
          &nbsp;
        </p>
      </td>
    </tr>
    <tr>
      <td colspan="48" style="vertical-align:top"><strong>Selger</strong></td>
      <td colspan="4">&nbsp;</td>
      <td colspan="48"><strong>Kj&oslash;per</strong></td>
    </tr>
    <tr>
      <td colspan="48" style="vertical-align:top">
        <table vitec-if="Model.selgere.Count &gt; 0">
          <tbody vitec-foreach="selger in Model.selgere">
            <tr>
              <td style="border-bottom:solid 1px #000000; height:40px">&nbsp;</td>
            </tr>
            <tr>
              <td style="vertical-align:bottom">[[*selger.navn]]</td>
            </tr>
          </tbody>
        </table>
      </td>
      <td colspan="4">&nbsp;</td>
      <td colspan="48" style="vertical-align:top">
        <div vitec-if="Model.kjopere.Count &gt; 0">
          <div vitec-foreach="kjoper in Model.kjopere">
            <table>
              <tbody>
                <tr>
                  <td style="border-bottom:solid 1px #000000; height:40px">&nbsp;</td>
                </tr>
                <tr>
                  <td>[[*kjoper.navn]]</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
      </td>
    </tr>
  </tbody>
</table>
```

---

### Counter CSS Pattern (Standard — Pattern A)

```css
#vitecTemplate {
    counter-reset: section;
}
#vitecTemplate article.item:not(article.item article.item) {
    counter-increment: section;
    counter-reset: subsection;
}
#vitecTemplate article.item article.item {
    counter-increment: subsection;
}
#vitecTemplate article.item:not(article.item article.item) h2::before {
    content: counter(section) ". ";
    display: inline-block;
    width: 26px;
}
#vitecTemplate article.item article.item h3::before {
    content: counter(section) "." counter(subsection) ". ";
    display: inline-block;
    width: 36px;
}
#vitecTemplate .avoid-page-break {
    page-break-inside: avoid;
}
#vitecTemplate article {
    padding-left: 26px;
}
#vitecTemplate article article {
    padding-left: 0;
}
#vitecTemplate h1 {
    text-align: center;
    font-size: 14pt;
    margin: 0;
    padding: 0;
}
#vitecTemplate h2 {
    font-size: 11pt;
    margin: 30px 0 0 -26px;
    padding: 0;
}
#vitecTemplate h3 {
    font-size: 10pt;
    margin: 20px 0 0 -10px;
    padding: 0;
}
#vitecTemplate table {
    width: 100%;
    table-layout: fixed;
}
#vitecTemplate table .borders {
    width: 100%;
    table-layout: fixed;
    border-bottom: solid 1px black;
    border-top: solid 1px black;
}
#vitecTemplate ul {
    list-style-type: disc;
    margin-left: 0;
}
#vitecTemplate ul li {
    list-style-position: outside;
    line-height: 20px;
    margin-left: 0;
}
#vitecTemplate .roles-table tbody:last-child tr:last-child td {
    display: none;
}
#vitecTemplate a.bookmark {
    color: #000;
    font-style: italic;
    text-decoration: none;
}
#vitecTemplate .liste:last-child .separator {
    display: none;
}
```

---

### Roles Table Pattern (with rowspan)

```html
<table class="roles-table" vitec-if="Model.selgere.Count &gt; 0">
  <thead>
    <tr>
      <th colspan="34"><strong>Navn</strong></th>
      <th colspan="48"><strong>Adresse/Kontaktinfo</strong></th>
      <th colspan="18"><strong>[[selger.ledetekst_fdato_orgnr]]</strong></th>
    </tr>
  </thead>
  <tbody vitec-foreach="selger in Model.selgere">
    <tr>
      <td colspan="34" rowspan="2">[[*selger.navnutenfullmektigogkontaktperson]]</td>
      <td colspan="48">[[*selger.gatenavnognr]], [[*selger.postnr]] [[*selger.poststed]]</td>
      <td colspan="18">[[*selger.fdato_orgnr]]</td>
    </tr>
    <tr>
      <td colspan="63">
        <span vitec-if="selger.tlf != &quot;&quot;">Tlf: [[*selger.tlf]]</span>
        <span vitec-if="(selger.tlf != &quot;&quot; &amp;&amp; selger.emailadresse != &quot;&quot;)"> / </span>
        <span vitec-if="selger.emailadresse != &quot;&quot;">E-post: [[*selger.emailadresse]]</span>
      </td>
    </tr>
    <tr>
      <td colspan="100">&nbsp;</td>
    </tr>
  </tbody>
</table>
```

---

### Bookmark/Anchor Cross-Reference Pattern

**CSS:**
```css
#vitecTemplate a.bookmark {
    color: #000;
    font-style: italic;
    text-decoration: none;
}
```

**Anchor target:**
```html
<a id="tinglysing-notifisering-og-sikkerhet"></a>
```

**Link:**
```html
<a class="bookmark" href="#tinglysing-notifisering-og-sikkerhet">
  <span vitec-if="(Model.eiendom.eieform == &quot;Selveier&quot; ...)">Tinglysing og Sikkerhet</span>
</a>
```

---

### Inline List Pattern (`.liste` / `.separator`)

**CSS:**
```css
#vitecTemplate .liste:last-child .separator {
    display: none;
}
```

**HTML:**
```html
<span vitec-foreach="selger in Model.selgere">
  <span class="liste">
    [[*selger.navnutenfullmektigogkontaktperson]]
    <span class="separator">, </span>
  </span>
</span>
```

This creates comma-separated inline lists where the last comma is hidden via CSS.
