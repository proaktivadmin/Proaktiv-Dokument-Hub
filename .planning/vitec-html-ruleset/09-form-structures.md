## 9. Form-like Structures

### `span.insert` — Editable placeholder fields

The `span.insert` pattern creates inline editable fields that show a placeholder label when empty:

```html
<span class="insert-table">
  <span class="insert" data-label="Skriv inn tekst her"></span>
</span>
```

CSS behaviour:
- When empty: displays with `lightpink` background and shows `data-label` text via `::before` pseudo-element
- When user clicks: background turns white, cursor changes to pointer
- `font-size` and `line-height` inherit from parent (`!important`)
- Minimum width: `2em`

```css
span.insert:empty {
    display: inline-block;
    background-color: lightpink;
    min-width: 2em !important;
    height: .7em !important;
}
span.insert:empty:before {
    content: attr(data-label);
}
```

**Evidence:** Lines 108–125 (CSS), line 6214 (HTML usage).

The `insert-table` wrapper provides inline-table display for proper alignment:
```css
.insert-table {
    display: inline-table;
}
.insert-table > span,
.insert-table > span.insert {
    display: table-cell;
}
```

### `data-label` on `<td>` — Floating field labels

The `data-label` attribute on `<td>` elements creates floating labels above the cell content using CSS `::before`:

```html
<td data-label="Adresse">[[eiendom.gatenavnognr]]</td>
<td data-label="Oppdragsnr.">[[oppdrag.nr]]</td>
```

CSS rules:
```css
#vitecTemplate table td[data-label] {
    padding: 16px 2px 5px 4px;
    position: relative;
}
#vitecTemplate table td[data-label]:before {
    content: attr(data-label);
    text-align: left;
    font-size: 9pt;
    line-height: 8pt;
    display: block;
    position: absolute;
    top: 5px;
}
```

**Evidence:** Lines 93–106 (CSS in Alle-flettekoder), lines 6222–6228 (HTML usage), lines 824–839 (CSS in Sikring footer, `vitec-reference.md`).

Note: The exact CSS values differ slightly between the Alle-flettekoder template (9pt, top: 5px) and the Sikring footer template (7pt, top: 1px). Both patterns are valid — the difference reflects template-specific styling.

### `data-choice` on `<td>` — Floating choice labels

The `data-choice` attribute on `<td>` elements creates floating choice/selection labels **below** the cell content using CSS `::after`. Often used alongside `data-label` for cells that have both a top label and a bottom choice indicator:

```html
<td data-label="Eieform" data-choice="Velg">[[eiendom.eieform]]</td>
```

CSS rules:
```css
#vitecTemplate td[data-choice]:after {
    content: attr(data-choice);
    text-align: center;
    font-size: 7pt;
    line-height: 8pt;
    color: #333;
    display: block;
    position: absolute;
    bottom: 1px;
    left: 0;
    right: 0;
}
#vitecTemplate td[data-choice] {
    padding: 0 2px 14px 2px;
    position: relative;
}
/* Cells with BOTH label and choice text */
#vitecTemplate td[data-label][data-choice] {
    padding: 16px 2px 16px 2px;
    position: relative;
}
```

**(DB evidence: 41 templates including "Skjøte", "Akseptbrev kjøper", "Hjemmelserklæring", "Hjemmelsoverføring")**

### `checkbox-table` class — Checkbox layout tables

A specialized table class for checkbox/radio button layouts, distinct from `form-table`:

```html
<table class="checkbox-table">
  <tbody>
    <tr>
      <td>
        <label class="btn" contenteditable="false" data-toggle="button">
          <span class="checkbox svg-toggle"></span>
        </label>
      </td>
      <td>Option text here</td>
    </tr>
  </tbody>
</table>
```

CSS:
```css
#vitecTemplate .checkbox-table {
    width: 100%;
    margin-left: 10px;
    table-layout: fixed;
    margin-bottom: 8px;
}
#vitecTemplate .checkbox-table td {
    padding-bottom: 5px;
    border: 0px;
}
#vitecTemplate .checkbox-table td:first-child {
    font-weight: 700;
    vertical-align: top;
}
```

Variant `checkbox-table-one-row` is used for single-row checkbox layouts at 86.7% width.

**(DB evidence: "Akseptbrev kjøper uten oppgjørsskjema (e-post)", "Skjøte")**

### `roles-table` — Party listing with trailing-row hiding

The `roles-table` class is used for seller/buyer party listings. Each party gets a `<tbody>` via `vitec-foreach`, and an extra `<tr>` with `&nbsp;` spacer is added after each party. A CSS rule hides the trailing spacer row from the last party:

```css
#vitecTemplate .roles-table tbody:last-child tr:last-child td {
    display: none;
}
```

This prevents an extra blank row after the final party entry. The HTML pattern:

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
    <tr><td colspan="100">&nbsp;</td></tr> <!-- hidden for last party -->
  </tbody>
</table>
```

**(Evidence: Kjøpekontrakt FORBRUKER — both DB and custom versions)**

### `screen-help` — Guided editing sidebar boxes (Legacy pattern — Næring/Aksje)

> **LEGACY PATTERN** — This interactive editing system was used in commercial property (Næring) and share purchase (Aksje) contract templates. These templates have been **removed from future Vitec support and updates** but remain in active use. The pattern is documented here for awareness — evaluate on a case-by-case basis before replicating in new templates.
>
> **Templates using this pattern:**
> - **Kjøpekontrakt Næring** — Commercial property purchase (38 help boxes, Vedlegg 5/6, Bilag 1/2)
> - **Kjøpekontrakt Aksje** — Share purchase with settlement (38+ help boxes, Vedlegg 7 embedded settlement agreement, Bilag 1–6 + Fullmakt)

The `screen-help` system provides colored sidebar guidance boxes that appear alongside contract sections in the CKEditor, allowing users to customize contracts through toggle interactions without directly editing HTML. All guidance boxes are **hidden in PDF output** via `@media print`.

#### Three component types

**1. Information boxes (turquoise)** — Read-only contextual help:

```html
<span class="btn btn-info btn-xs extra-wide right-aligned screen-help screen-help-info"
      contenteditable="false"
      data-help="Pass på at Avtalt Overtakelse er en bankdag.">
  Punkt 3.1: Informasjon
</span>
```

- `.screen-help-info` class adds `pointer-events: none` (non-clickable)
- Font Awesome info icon (`\f05a`) via `::before` pseudo-element
- `data-help` text rendered via `::after` pseudo-element on white background

**2. Toggle boxes (orange when collapsed, green when expanded)** — Click to show/hide alternative text:

```html
<span aria-expanded="false"
      class="btn btn-success btn-xs collapsed extra-wide left-aligned screen-help"
      contenteditable="false"
      data-help="Hvis partene har tatt de forbehold som følger av bud og budaksept..."
      data-target="#hjelp1"
      data-toggle="collapse">
  Ekstra setning til innledningen
</span>
```

- Uses Bootstrap collapse (`data-toggle="collapse"`, `data-target`)
- `.collapsed` state applies orange gradient via CSS
- `data-help` provides instructions for when to use the alternative text
- Font Awesome checkbox icon (`\f14a` unchecked, `\f0c8` collapsed) via `::before`

**3. Collapsible content** — The hidden alternative text that toggles show:

```html
<span aria-expanded="false" class="collapse collapse-span" id="hjelp1" style="height:0px">
  <span style="color:red"><em>Alternativt:</em> Overtakelse skal skje...</span>
</span>
```

- Hidden by default: `.collapse { display: none !important; }`
- Shown when toggled: `.collapse.in { display: block !important; }`
- Alternative text displayed in **red** (`color:red`) to signal it needs review
- Display variants: `collapse-span` (inline), `collapse-list-item` (for `<li>`), `collapse-tbody` (for table rows)

#### CSS architecture

```css
.screen-help {
    position: absolute;
    width: 300px;
    white-space: unset;
    text-align: left;
    font-family: Regular, sans-serif;
}

.screen-help.extra-wide { width: 400px; }
.screen-help.left-aligned { left: -1cm; margin-left: -305px; }
.screen-help.right-aligned { right: -1.2cm; margin-right: -305px; }

.screen-help:after {
    content: attr(data-help);
    display: block;
    background-color: white;
    color: black;
    font-size: 11.5px;
    line-height: 13px;
    padding: 2px;
}

/* Collapsed state: orange gradient */
.screen-help.collapsed {
    background-image: linear-gradient(to bottom, #f0ad4e 0, #eb9316 100%);
    border-color: #e38d13;
}

/* Print: hide all help boxes */
@("@")media print {
    .screen-help { display: none; }
}
```

Note: `@("@")media` is the Razor escape syntax for CSS `@media` — inside Vitec templates, `@` is intercepted by the Razor engine, so `@media` must be escaped as `@("@")media` to produce valid CSS output.

#### Usage pattern in contract templates

The næring contract uses a sequential ID scheme (`hjelp1`, `hjelp2`, ... `hjelp38`) with guidance boxes positioned at each customizable section. The pattern supports:

- **Alternative text** — Pre-written replacement clauses toggled in/out (e.g., "Alternativ tekst til punkt 3.1")
- **Additional clauses** — Extra contractual provisions toggled in (e.g., "Ny bokstav i punkt 4.1")
- **Appended sentences** — Supplementary sentences toggled at the end of existing text (e.g., "Bisetning til punkt 6.3")
- **Conditional sections** — Entire article sections wrapped in `.collapse` (e.g., "Frist for gjennomføring")

#### Multi-target toggling

A single toggle box can control multiple targets using a CSS class instead of an ID:

```html
<!-- Toggle controls two separate elements -->
<span data-target=".hjelp2" data-toggle="collapse">...</span>

<!-- Two separate elements share the class -->
<span class="collapse collapse-span hjelp2" style="height:0px">...</span>
<article class="collapse-span hjelp2 collapse" style="height:0px">...</article>
```

#### Additional patterns from the Næring template

**`table.numbered`** — Auto-numbered table rows using CSS counters that match the section number:

```css
#vitecTemplate table.numbered { counter-reset: row-num; }
#vitecTemplate table.numbered tbody tr { counter-increment: row-num; }
#vitecTemplate table.numbered tr td:first-child:before {
    content: counter(main-counter) "." counter(row-num);
    font-weight: bold;
}
```

This creates rows numbered "2.1", "2.2", "2.3" etc. matching the parent section's `main-counter` value.

**`.witness-table`** — Bordered table for witness signatures with `data-label` floating labels and `header-cell` class for gray background cells.

**Inline list separator pattern** — Comma-separated list items using CSS `:last-child` hiding:

```css
#vitecTemplate .kjoperspant:last-child .separator { display: none; }
```

```html
<span vitec-foreach="pant in Model.oppdrag.kjoperspant">
  <span class="kjoperspant">[[*pant.navn]] (org.nr. [[*pant.panthaverorgnr]])
    <span class="separator">, </span>
  </span>
</span>
```

**Collection-with-fallback pattern** — When a collection may be empty, template shows editable insert fields as fallback. Used extensively in the Aksje template for buyer's bank references:

```html
<span vitec-if="Model.oppdrag.kjoperspant.Count > 0">
  <span vitec-foreach="pant in Model.oppdrag.kjoperspant">
    <span class="kjoperspant">[[*pant.navn]] (org.nr. [[*pant.panthaverorgnr]])
      <span class="separator">,</span>
    </span>
  </span>
</span>
<span vitec-if="Model.oppdrag.kjoperspant.Count == 0">
  <span class="insert-table"><span class="insert" data-label="Kjøpers bank"></span></span>,
  org.nr. <span class="insert-table"><span class="insert" data-label="Orgnr. kjøpers bank"></span></span>
</span>
```

This `Count > 0` / `Count == 0` guard-and-fallback pattern repeats ~10 times throughout the Aksje template (main contract, Oppgjørsavtale, Bilag 1, 2, 4, 5) wherever buyer's bank is referenced.

**Conditional representative name** — Falls back to insert field when company name equals contact name. Applied symmetrically for both seller and buyer:

```html
<span vitec-if="Model.selger.hovedkontakt.navn == Model.selger.firmanavn">
  <span class="insert-table"><span class="insert" data-label="Selgers representant"></span></span>
</span>
<span vitec-if="Model.selger.hovedkontakt.navn != Model.selger.firmanavn">
  [[selger.hovedkontakt.navn]]
</span>

<span vitec-if="Model.kjoper.hovedkontakt.navn == Model.kjoper.firmanavn">
  <span class="insert-table"><span class="insert" data-label="Kjøpers representant"></span></span>
</span>
<span vitec-if="Model.kjoper.hovedkontakt.navn != Model.kjoper.firmanavn">
  [[kjoper.hovedkontakt.navn]]
</span>
```

This pattern appears in every signature block throughout the Aksje template (main contract, Oppgjørsavtale, and all 6 Bilag). When Vitec auto-fills the contact name to equal the company name (indicating no specific contact person is registered), the template shows an editable pink insert field instead.

**Multi-document template** — A single template file contains the main contract plus multiple appendices (Vedlegg 5, Vedlegg 6 with two variants, Bilag 1, Bilag 2), separated by `<div style="page-break-after:always"><span style="display:none">&nbsp;</span></div>`.

**(Evidence: Kjøpekontrakt Næring source code from Vitec Next production — legacy template, removed from future Vitec support. 2026-02-21)**

#### Additional patterns from Kjøpekontrakt Aksje

The share purchase contract template (Kjøpekontrakt ved salg av aksjer) extends the screen-help system with additional patterns not seen in the Næring template:

**Dynamic cross-reference numbering via CSS `aria-expanded` selectors** — When toggle boxes insert/remove numbered sections, cross-references in other toggle labels update automatically using adjacent-sibling CSS selectors keyed on `aria-expanded`:

```css
span[aria-expanded="false"][data-target="\23hjelp31"] + span .is-aria-expanded-hjelp31-hjelp32:before {
    content: "punkt 2.9";
}
span[aria-expanded="true"][data-target="\23hjelp31"] + span .is-aria-expanded-hjelp31-hjelp32:before {
    content: "punkt 2.10";
}
```

`\23` is the CSS Unicode escape for `#`, matching `data-target="#hjelp31"`. This pattern is embedded inside a `<style>` block within a `<td>` cell — an inline `<style>` element, not in the template header. The toggle button and the affected label must be adjacent siblings in the DOM for the `+` combinator to work:

```html
<td>
  <style>/* dynamic cross-ref rules here */</style>
  <span data-target="#hjelp31" data-toggle="collapse" aria-expanded="false">Nytt punkt 2.7</span>
  <span><span class="is-aria-expanded-hjelp31-hjelp32"></span></span>
  <span><span class="is-aria-expanded-hjelp31-hjelp33"></span></span>
</td>
```

**`text-transform: uppercase` for company names** — In Bilag headers (Aksjeeierbok, Generalforsamlingsprotokoll), the company name is forced to uppercase via inline style:

```html
<p style="text-align:center"><strong><span style="text-transform:uppercase">[[aksjeselskap.navn]]</span></strong></p>
```

This ensures legal document headers display company names in block letters regardless of the stored casing.

**Extensive Bilag suite** — The Aksje template contains 6 appendices (Bilag 1–6) plus a Fullmakt og Samtykke page, all within the same template file:
- Bilag 1: Aksjeeierbok (share register at signing) with heftelser/merknader columns
- Bilag 2: Fullmakt til pantsettelse (authorization to mortgage) with witness table
- Bilag 3: Styreprotokoll (board meeting minutes)
- Bilag 4: Melding om aksjeerverv og pantsettelse (notice of share acquisition)
- Bilag 5: Aksjeeierbok (share register at takeover) with updated entries
- Bilag 6: Generalforsamlingsprotokoll (extraordinary general meeting minutes) — includes draft bylaws

**Vedlegg 7 as embedded contract** — The settlement agreement (Oppgjørsavtale) appears as "Vedlegg 7" within the main template, with its own complete section numbering (restarting from 1), its own `<table class="numbered">` auto-numbered action tables, and its own signature blocks. This "contract within a contract" uses the same `main-counter` / `sub-counter` CSS counters as the parent, which restart correctly because the outer `<article>` structure resets counters per section.

**`$.UD()` function** — Number formatting for purchase prices:

```html
NOK $.UD([[kontrakt.kjopesum]])
```

This is a Vitec helper function that formats the merge field value with thousands separators (e.g., "1 500 000"). Used for financial amounts in contracts.

**`insert-checkbox`** — Inline checkbox fields for contract forms:

```css
.insert-checkbox {
    display: inline-table;
    vertical-align: bottom;
    margin: 0 2px;
}
.insert-checkbox > span {
    line-height: 1.1;
    border: solid 1px #000;
    height: 1.1em;
    width: 1.1em;
    max-width: 1.1em;
    overflow: hidden;
    display: table-cell;
    text-align: center;
    white-space: nowrap;
}
```

**`collapse-list-item`** — A collapse variant for `<li>` elements that preserves list formatting:

```css
.collapse.collapse-list-item { display: none !important; }
.collapse.collapse-list-item.in { display: list-item !important; }
```

Used for toggleable list items within `<ol>` numbered lists — when toggled in, the item inherits its counter position from the parent list, so remaining items re-number automatically.

**`collapse-tbody`** — A collapse variant for `<tbody>` elements, used to toggle entire table row groups in `table.numbered` action tables:

```css
.collapse.collapse-tbody.in { display: table-row-group !important; }
```

This enables optional rows to be inserted into numbered action tables while preserving auto-numbering — when toggled in, the `<tbody>` becomes visible with `table-row-group` display (required for correct table rendering), and the `counter-increment: row-num` on `<tr>` elements adjusts numbering automatically.

**`bordered-table`** — Full-border table with `9pt` font size, vertical alignment control:

```css
#vitecTemplate .bordered-table td {
    vertical-align: top;
    border: solid 1px #000;
    font-size: 9pt;
}
#vitecTemplate .bordered-table td div { font-size: 9pt; }
#vitecTemplate .bordered-table th {
    vertical-align: bottom;
    font-size: 9pt;
}
```

Used for structured data tables (e.g., share register / aksjeeierbok) where headers align to bottom and cells align to top.

**`roles-table` last-row hiding** — Hides the trailing spacer row from the last party entry, preventing excess whitespace:

```css
#vitecTemplate .roles-table tbody:last-child tr:last-child td { display: none; }
```

**`a.bookmark` links** — In-document bookmarks styled as black, italic, non-underlined links:

```css
#vitecTemplate a.bookmark { color: #000; font-style: italic; text-decoration: none; }
```

**Separator hiding family** — Three CSS classes use `:last-child .separator { display: none }` to hide trailing separators (commas/slashes) from the last item in a list:

```css
#vitecTemplate .kjoperspant:last-child .separator { display: none; }
#vitecTemplate .kjopers-pant:last-child .separator { display: none; }
#vitecTemplate .matrikkel:last-child .separator { display: none; }
```

- `kjoperspant` / `kjopers-pant` — Buyer's bank list (two naming variants across templates)
- `matrikkel` — Cadastral reference list

**(Evidence: Kjøpekontrakt ved salg av aksjer source code from Vitec Next production — legacy template using Meglerstandard mars 2020 with oppgjørsansvarlig variant. Full source code analysis 2026-02-21)**

### `contenteditable="false"` — Non-editable regions

Prevents CKEditor users from editing specific elements:

```html
<tr contenteditable="false">
  <td class="no-border" colspan="20"><small>GA-5400 B</small></td>
</tr>
```

Used on:
- `<tr>` — entire rows (footer templates with fixed text like form numbers)
- `<label>` — SVG toggle labels (prevents user from accidentally editing the toggle structure)

**Evidence:** `vitec-reference.md` lines 862, 916 (footers); Alle-flettekoder lines 289, 6175–6210 (toggles).

### `data-version` — Version tagging

The `data-version` attribute marks when a feature was introduced in Vitec Next:

```html
<tr data-version="4.0">
  <td colspan="30">Markedsføringsdato</td>
  <td colspan="70">[[oppdrag.tilsalgsdato]]</td>
</tr>
```

CSS displays a coloured badge via `::after`:
```css
#vitecTemplate [data-version]:after {
    content: attr(data-version);
    background-color: rgb(4 98 175 / 0.6);
    border-radius: 3px;
    padding: 1px 4px;
    color: #fff;
    font-size: 13px;
}
```

Version badges can be toggled on/off via a checkbox toggle button (lines 168–205, 273, 289).

**Evidence:** 100 instances in Alle-flettekoder. Used on `<tr>` and `<td>` elements. Version values observed: `2.1`, `3.0`, `4.0`, `4.1`, `4.2`, `4.3`, `4.4`, `5.1`, `5.2`, `5.3`, `23.2`, `23.4`, `25.1`, `25.9`.

---
