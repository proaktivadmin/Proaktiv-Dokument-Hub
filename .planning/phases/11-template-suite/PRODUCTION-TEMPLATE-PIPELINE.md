# Production Template Pipeline — Knowledge Base

## Overview

This document captures everything learned from the pilot conversion of "Kjøpekontrakt prosjekt (enebolig med delinnbetalinger)" — a 9-page, 20-section Norwegian real estate contract — from a Word document into a production-ready Vitec Next HTML template.

**Key insight:** Simple Word-to-HTML conversion (mammoth, pandoc, etc.) produces templates that are structurally incomplete. Production-ready Vitec Next templates require **domain-specific engineering**: mapping legacy merge fields to modern syntax, building conditional logic branches from implied alternatives, constructing `vitec-foreach` loops from flat party listings, and wrapping everything in the Vitec template shell with CSS counters and proper table layouts. This is an agent-level task, not a script.

---

## 1. Source Format Comparison

We tested four export formats from the same Word document:

| Format | Method | Size | Structure Preservation | Verdict |
|--------|--------|------|----------------------|---------|
| **.htm** (Web Page, Filtered) | Word → Save As → "Web Page, Filtered (*.htm)" | 95 KB | Tables, headings, Wingdings checkboxes, red text markers, page sections | **Best** |
| **.docx** (via mammoth) | Native .docx processed by `mammoth` Python library | 47 KB → 26K HTML | Tables, headings, checkboxes become `<li>` bullets, red text lost | Acceptable |
| **.mht** (Web Archive) | Word → Save As → "Single File Web Page (*.mht)" | 222 KB | Same as .htm but wrapped in MIME encoding with Office XML bloat | Worst |
| **.pdf** (via text extraction) | Print/export to PDF | 47 KB | Plain text only, all structure lost | Reference only |

### Recommendation

**Always use "Web Page, Filtered (*.htm)"** from Word. This format:
- Strips Office-specific VML/XML that the unfiltered format keeps
- Preserves table structure with actual `<table>` elements
- Preserves headings as `<h1>`-`<h5>`
- Preserves Wingdings checkbox characters (identifiable by `font-family:Wingdings` + `q` character)
- Preserves red text markers (identifiable by `color:red` in inline styles)
- Preserves page sections as `<div class=WordSection*>`
- Uses `windows-1252` encoding (must be re-encoded to UTF-8)

### How to Save from Word

1. Open the document in Microsoft Word
2. File → Save As
3. Change "Save as type" to **"Web Page, Filtered (*.htm, *.html)"**
4. Important: Choose "Filtered" — NOT "Web Page" (which keeps full Office XML)
5. Close the file in Word before the agent reads it (Word locks open files)

---

## 2. Pipeline Steps

The conversion pipeline has 6 sequential steps. Each step builds on the output of the previous one.

### Step 1: Clean Word Markup

**Input:** Raw `.htm` file (windows-1252 encoded)
**Output:** Clean structural HTML (UTF-8)

Operations:
1. Re-encode from `windows-1252` to UTF-8
2. Strip all Word CSS classes (`MsoNormal`, `MsoHeader`, `MsoBodyText`, `MsoNoSpacing`, `MsoListParagraph`, `MsoQuote`, `MsoFooter`, `Hengende1`, `Stil1`, etc.)
3. Remove all `lang` attributes (`lang=NO-BOK`, `lang=NO-NYN`, `lang=EN-GB`)
4. Strip Word-specific style properties (`mso-*`, `font-family`, `font-size`, `line-height`, `font:7.0pt`)
5. Keep structural styles only: `text-align`, `vertical-align`, `border*`, `padding`, `width`, `page-break-*`, `border-collapse`
6. Unwrap all `<span>` elements (Word wraps every text fragment in spans with style attributes)
7. Unwrap `<a name="...">` bookmarks (Word internal anchors)
8. Remove `<div class=WordSection*>` wrappers (keep content)
9. Remove page break `<br clear=all style='page-break-before:always'>` elements
10. Remove empty `<b>` tags between WordSections
11. Remove empty `<p>` and `&nbsp;`-only `<p>` elements
12. Remove empty `<u>` tags (Word decoration artifacts)

**What to preserve:** `<h1>`-`<h5>`, `<table>`, `<tr>`, `<td>`, `<th>`, `<b>`/`<strong>`, `<i>`/`<em>`, `<p>`, `<u>` (with content), `<ol>`/`<ul>`/`<li>`

### Step 2: Map Legacy Merge Fields

**Input:** Cleaned HTML with legacy `#field.context¤` syntax
**Output:** HTML with modern `[[field.name]]` syntax

Legacy Vitec merge fields use `#fieldname.context¤` syntax. Modern Vitec Next uses `[[field.path]]` with `[[*field.path]]` for required fields inside foreach loops.

See **Section 4: Complete Field Mapping Reference** below for the full mapping table.

Operations:
1. Direct string replacements for known field mappings
2. Remove layout artifacts (`#flettblankeeiere¤`)
3. Replace party listing fields with foreach loop placeholders (handled in Step 4)
4. Add new fields from the Flettekoder 25.9 reference that weren't in the original

### Step 3: Add vitec-if Conditional Branches

**Input:** HTML with modern merge fields
**Output:** HTML with `vitec-if` attributes on elements

Source document clues for conditionals:
- **Red text** (`color:red` in source) = alternative wording that depends on a condition
- **Wingdings checkboxes** (`font-family:Wingdings` + `q`) = mutually exclusive options
- **"Alt 1" / "Alt 2"** labels = explicitly marked alternatives
- **"Bolig/fritidsbolig"** slash separations = property type conditional
- **Section 1A vs 1B** = ownership form conditional (selveiet vs. sameie)

See **Section 5: Conditional Pattern Library** below for all patterns.

### Step 4: Build vitec-foreach Party Loops

**Input:** HTML with flat party listings
**Output:** HTML with `vitec-foreach` on `<tbody>` elements

Legacy templates list parties (selger/kjøper) as flat text blocks with fields like `#eiere¤`, `#forsteeier¤`, `#kunadresse.kontakter¤`. Modern templates use `vitec-foreach` loops with the `roles-table` pattern.

See **Section 6: Party Loop Patterns** below.

### Step 5: Wrap in Vitec Template Shell

**Input:** HTML content with fields, conditions, and loops
**Output:** Complete template with shell, counters, and structure

Operations:
1. Wrap everything in `<div id="vitecTemplate">` — NO `class="proaktiv-theme"`
2. Add Stilark reference: `<span vitec-template="resource:Vitec Stilark">&nbsp;</span>`
3. Add `<style>` block with CSS counters + SVG checkbox CSS + insert field CSS (see Section 3 and 7)
4. Add outer `<table>` body wrapper with `<small>` header info (org.nr, oppdragsnr, omsetningsnr)
5. Use `<h1>` for the template title
6. Wrap numbered contract sections in `<article class="item">` with `<h2>` headings
7. Convert layout tables to 100-unit colspan system
8. Add `roles-table` and `costs-table` CSS classes
9. Add page break controls: `avoid-page-break` class on short sections (article), `<div class="avoid-page-break">` around headings + key content in long sections, forced page breaks at major transitions, signature always wrapped
10. Convert signature block to `border-bottom: solid 1px #000` signing lines
11. Add `insert-table` + `span.insert` with `data-label` for user fill-in fields
12. **Entity encoding** — Replace ALL literal Norwegian characters with HTML entities (mandatory final step)

### Step 6: Validate

**Input:** Complete template
**Output:** Validation report (pass/fail per checklist item)

Run the automated validator `scripts/tools/validate_vitec_template.py` (61 checks).
The old 14-point checklist from `.planning/vitec-html-ruleset.md` is supplementary only
(based on 133 Proaktiv-customized templates, not the official Vitec standard).
Validation sections:
- A. Template Shell (3 checks)
- B. Table Structure (6 checks)
- C. Inline Styles (4 checks)
- D. Merge Fields (5 checks)
- E. Conditional Logic (8 checks)
- F. Iteration (6 checks)
- G. Images and SVG (5 checks)
- H. Form Elements (6 checks)
- I. Text and Formatting (6 checks)
- J. Contract-Specific (12 checks)
- K. Final Validation (6 checks)

Also verify:
- All Norwegian characters are HTML entities (`&oslash;`, `&aring;`, etc.) — NO literal UTF-8
- No Unicode checkboxes (`&#9744;`/`&#9745;`) — SVG checkboxes only
- All monetary merge fields wrapped in `$.UD()`
- No legacy `#field.context¤` syntax remaining
- Outer `<table>` body wrapper present with `<h1>` title

---

## 3. Template Style Block

Every contract template needs this CSS counter pattern in a `<style>` block:

```css
/* Counter system */
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

/* Heading styles — 26px indent accommodates double-digit section numbers (10+) */
#vitecTemplate h1 { text-align: center; font-size: 14pt; margin: 0; padding: 0; }
#vitecTemplate h2 { font-size: 11pt; margin: 30px 0 0 -26px; padding: 0; }
#vitecTemplate h3 { font-size: 10pt; margin: 20px 0 0 -10px; padding: 0; }

/* Article/section layout — padding must match h2 negative margin for alignment */
#vitecTemplate article { padding-left: 26px; }
#vitecTemplate article article { padding-left: 0; }
#vitecTemplate .avoid-page-break { page-break-inside: avoid; }

/* Table base styles */
#vitecTemplate table { width: 100%; table-layout: fixed; }
#vitecTemplate table .borders {
  width: 100%; table-layout: fixed;
  border-bottom: solid 1px black; border-top: solid 1px black;
}

/* Roles table */
#vitecTemplate .roles-table { width: 100%; table-layout: fixed; border-collapse: collapse; }
#vitecTemplate .roles-table th { text-align: left; padding: 4px 6px; border-bottom: 1px solid #000; }
#vitecTemplate .roles-table td { padding: 4px 6px; vertical-align: top; }
#vitecTemplate .roles-table tbody:last-child tr:last-child td { display: none; }

/* Costs table */
#vitecTemplate .costs-table { width: 100%; table-layout: fixed; border-collapse: collapse; }
#vitecTemplate .costs-table td { padding: 2px 6px; vertical-align: top; }
#vitecTemplate .costs-table tr.sum-row td { border-top: 1px solid #000; font-weight: bold; }

/* Lists */
#vitecTemplate ul { list-style-type: disc; margin-left: 0; }
#vitecTemplate ul li { list-style-position: outside; line-height: 20px; margin-left: 0; }
#vitecTemplate .liste:last-child .separator { display: none; }

/* Bookmark cross-references */
#vitecTemplate a.bookmark { color: #000; font-style: italic; text-decoration: none; }
```

This uses the **Chromium-safe dual-counter pattern** (not `counters(item, ".")` which breaks in Chrome PDF rendering). The heading styles, table base, list, bookmark, and separator classes are all taken from the bruktbolig reference template.

---

## 4. Complete Field Mapping Reference

### Direct Replacements (Legacy → Modern)

| Legacy Field | Modern Field | Notes |
|-------------|-------------|-------|
| `#oppdragsnummer.oppdrag¤` | `[[oppdrag.nr]]` | Assignment number |
| `#omsetningsnummer.oppdrag¤` | `[[kontrakt.formidling.nr]]` | Transaction number |
| `#salgssum.oppdrag¤` | `[[kontrakt.kjopesum]]` | Purchase price |
| `#klientkonto.avdelinger¤` | `[[kontrakt.klientkonto]]` | Client account number |
| `#betalingsmerknadkjoper.oppdrag¤` | `[[kontrakt.kid]]` | Payment reference (KID) |
| `#standard_kontaktoppgjor¤` | Oppgjørsavdeling block (see below) | Settlement office contact block |
| `#fullmaktsinnehavereb_kjoper¤` | `[[kjoper.fullmektig.navn]]` | Buyer's representative |
| `#flettblankeeiere¤` | (remove) | Layout artifact, no content |

### Party Fields (Replaced by vitec-foreach Loops)

| Legacy Field | Modern Equivalent | Context |
|-------------|-------------------|---------|
| `#eiere¤` | `vitec-foreach="selger in Model.selgere"` | Seller listing |
| `#forsteeier¤` | `[[*selger.navnutenfullmektigogkontaktperson]]` | Inside selger foreach |
| `#nyeeiere¤` | `vitec-foreach="kjoper in Model.kjopere"` | Buyer listing |
| `#forstenyeier¤` | `[[*kjoper.navnutenfullmektigogkontaktperson]]` | Inside kjoper foreach |
| `#kunadresse.kontakter¤` | `[[*selger.gatenavnognr]], [[*selger.postnr]] [[*selger.poststed]]` | Address fields inside foreach |
| `#mobil.kontakter¤` | `[[*selger.tlf]]` / `[[*kjoper.tlf]]` | Phone inside foreach |
| `#email.kontakter¤` | `[[*selger.emailadresse]]` / `[[*kjoper.emailadresse]]` | Email inside foreach |

### Oppgjørsavdeling Block (Replaces `#standard_kontaktoppgjor¤`)

```html
<table style="width:100%; table-layout:fixed;">
<tbody>
<tr><td colspan="100">[[oppgjor.kontornavn]]</td></tr>
<tr><td colspan="100">[[oppgjor.besoksadresse]], [[oppgjor.besokspostnr]] [[oppgjor.besokspoststed]]</td></tr>
<tr><td colspan="50">Tlf: [[oppgjor.kontortlf]]</td><td colspan="50">E-post: [[oppgjor.kontorepost]]</td></tr>
</tbody>
</table>
```

### Additional Fields to Add (Not in Source Documents)

These fields should be added based on the template's purpose, even if they weren't in the original Word document:

| Field | Used In | Purpose |
|-------|---------|---------|
| `[[kontrakt.kjopesumibokstaver]]` | Kjøpesum section | Price in words |
| `[[kontrakt.kjopesumogomkostn]]` | Kjøpesum section | Total incl. costs |
| `[[kontrakt.totaleomkostninger]]` | Omkostninger section | Sum of costs |
| `[[kontrakt.overtagelse.dato]]` | Overtakelse section | Handover date |
| `[[kontrakt.dato]]` | Header/signatur | Contract date |
| `[[dagensdato]]` | Signatur | Today's date |
| `[[komplettmatrikkel]]` | Salgsobjekt section | Full cadastral reference |
| `[[eiendom.kommunenavn]]` | Salgsobjekt section | Municipality name |
| `[[eiendom.tomtetype]]` | Salgsobjekt section | Plot type (eiertomt/festetomt) |
| `[[eiendom.eieform]]` | Section 1A/1B switch | Ownership form (Eierseksjon etc.) |
| `[[eiendom.grunntype]]` | Bolig/fritid switch | Property base type |
| `[[eiendom.leilighetsnr]]` | Sameie section | Apartment number |
| `[[eiendom.fellesutgifter]]` | Sameie section | Monthly common costs |
| `[[eiendom.heftelserogrettigheter]]` | Heftelser section | Encumbrances text |
| `[[meglerkontor.navn]]` | Various | Brokerage firm name |
| `[[meglerkontor.orgnr]]` | Various | Org number |
| `[[ansvarligmegler.navn]]` | Various | Responsible broker |
| `[[oppdrag.prosjekt.antallenheter]]` | Prosjekt section | Number of units |
| `[[selger.ledetekst_fdato_orgnr]]` | Roles table header | Dynamic column header "Fødselsdato"/"Org.nr" |
| `[[kjoper.ledetekst_fdato_orgnr]]` | Roles table header | Same for buyer |
| `[[*selger.fdato_orgnr]]` | Roles table | Birth date or org number |
| `[[*kjoper.fdato_orgnr]]` | Roles table | Birth date or org number |
| `$.UD([[kontrakt.kjopesum]])` | Price formatting | Format number with thousand separators |

### Collections Available for vitec-foreach

| Collection | Loop Variable | Common Inner Fields |
|-----------|---------------|-------------------|
| `Model.selgere` | `selger` | `navn`, `navnutenfullmektigogkontaktperson`, `gatenavnognr`, `postnr`, `poststed`, `fdato_orgnr`, `tlf`, `emailadresse`, `fullmektig.navn`, `ledetekst_fdato_orgnr` |
| `Model.kjopere` | `kjoper` | Same as selgere |
| `Model.hjemmelshavere` | `hjemmelshaver` | `navn`, `fdato_orgnr` |
| `Model.kjoperskostnader.poster` | `kostnad` | `beskrivelse`, `belop` |
| `Model.heftelser` | `heftelse` | `type`, `beskrivelse`, `belop` |

---

## 5. Conditional Pattern Library

### Escaping Rules for vitec-if Expressions

| Character | HTML Escape | Example |
|-----------|------------|---------|
| `"` (quote) | `&quot;` | `vitec-if="Model.eiendom.eieform == &quot;Eierseksjon&quot;"` |
| `>` (greater than) | `&gt;` | `vitec-if="Model.selgere.Count &gt; 1"` |
| `<` (less than) | `&lt;` | `vitec-if="Model.verdi &lt; 1000000"` |
| `&&` (logical AND) | `&amp;&amp;` | `vitec-if="(selger.tlf != &quot;&quot; &amp;&amp; selger.emailadresse != &quot;&quot;)"` |
| `=>` (lambda arrow) | `=&gt;` | `.Where(x =&gt; x.type == ...)` |
| `æ`, `ø`, `å` | `\xE6`, `\xF8`, `\xE5` | In string comparisons only |

### Pattern: Property Type Switch (Bolig vs. Fritid)

```html
<span vitec-if="Model.eiendom.grunntype == &quot;Bolig&quot;">Boligen</span>
<span vitec-if="Model.eiendom.grunntype == &quot;Fritid&quot;">Fritidsboligen</span>
```

### Pattern: Ownership Form Switch (1A Selveiet vs. 1B Sameie)

```html
<div vitec-if="Model.eiendom.eieform != &quot;Eierseksjon&quot;">
  <!-- Section 1A: Selveiet content -->
</div>
<div vitec-if="Model.eiendom.eieform == &quot;Eierseksjon&quot;">
  <!-- Section 1B: Sameie/eierseksjon content -->
</div>
```

### Pattern: Dynamic Checkbox (Auto-Checked Based on Data)

Uses the SVG checkbox pattern. `&#9744;`/`&#9745;` render as "?" in Vitec PDF — never use them.

```html
<p>
  <span vitec-if="Model.eiendom.tomtetype == &quot;eiertomt&quot;">
    <label class="btn active" contenteditable="false" data-toggle="button">
      <input type="checkbox" /><span class="checkbox svg-toggle"></span>
    </label>
  </span>
  <span vitec-if="Model.eiendom.tomtetype != &quot;eiertomt&quot;">
    <label class="btn" contenteditable="false" data-toggle="button">
      <input type="checkbox" /><span class="checkbox svg-toggle"></span>
    </label>
  </span>
  eiet
</p>
```

See **Section 7: Reference Patterns Library** for the SVG checkbox CSS.

### Pattern: Overtakelse Alternatives (Date Known vs. TBD)

```html
<div vitec-if="Model.kontrakt.overtagelse.dato != &quot;Mangler data&quot;">
  <p>Overtas den <strong>[[kontrakt.overtagelse.dato]]</strong></p>
</div>
<div vitec-if="Model.kontrakt.overtagelse.dato == &quot;Mangler data&quot;">
  <p>Forventet ferdigstillelse er <span class="insert">&nbsp;</span></p>
</div>
```

### Pattern: Conditional Text When Field Has Value

```html
<p>Eiendommen overdras fri for pengeheftelser<span vitec-if="Model.eiendom.heftelserogrettigheter != &quot;&quot;">, med unntak for:</span></p>
<p vitec-if="Model.eiendom.heftelserogrettigheter != &quot;&quot;">[[eiendom.heftelserogrettigheter]]</p>
```

### Pattern: Pluralization (Selger vs. Selgere)

```html
<p>Selger<span vitec-if="Model.selgere.Count &gt; 1">e</span></p>
```

### Pattern: Project Forbehold (Multiple Independent Conditions)

```html
<p vitec-if="Model.oppdrag.prosjekt.erutbyggersforbeholdsalgsgrad == true">
  <label class="btn active" contenteditable="false" data-toggle="button">
    <input type="checkbox" /><span class="checkbox svg-toggle"></span>
  </label> Salgsgrad
</p>
<p vitec-if="Model.oppdrag.prosjekt.erutbyggersforbeholdigangsettelse == true">
  <label class="btn active" contenteditable="false" data-toggle="button">
    <input type="checkbox" /><span class="checkbox svg-toggle"></span>
  </label> Igangsettelsestillatelse
</p>
<p vitec-if="Model.oppdrag.prosjekt.erutbyggersforbeholdbyggelaan == true">
  <label class="btn active" contenteditable="false" data-toggle="button">
    <input type="checkbox" /><span class="checkbox svg-toggle"></span>
  </label> Byggel&aring;n
</p>
```

### Pattern: Fullmektig (Representative, Show Only If Present)

```html
<p vitec-if="Model.selger.fullmektig.navn != &quot;&quot;">
  Selger er representert ved fullmektig [[selger.fullmektig.navn]]
</p>
```

### Pattern: Conditional Phone/Email Display with Separator

```html
<span vitec-if="selger.tlf != &quot;&quot;">Mob: [[*selger.tlf]]</span>
<span vitec-if="(selger.tlf != &quot;&quot; &amp;&amp; selger.emailadresse != &quot;&quot;)"> / </span>
<span vitec-if="selger.emailadresse != &quot;&quot;">E-post: [[*selger.emailadresse]]</span>
```

Note: Inside a `vitec-foreach`, conditions reference the loop variable directly (no `Model.` prefix).

---

## 6. Party Loop Patterns

### Selger Roles Table

```html
<table class="roles-table" vitec-if="Model.selgere.Count &gt; 0">
<thead>
<tr>
  <th colspan="34"><strong>Navn</strong></th>
  <th colspan="48"><strong>Adresse</strong></th>
  <th colspan="18"><strong>[[selger.ledetekst_fdato_orgnr]]</strong></th>
</tr>
</thead>
<tbody vitec-foreach="selger in Model.selgere">
<tr>
  <td colspan="34">[[*selger.navnutenfullmektigogkontaktperson]]</td>
  <td colspan="48">[[*selger.gatenavnognr]], [[*selger.postnr]] [[*selger.poststed]]</td>
  <td colspan="18">[[*selger.fdato_orgnr]]</td>
</tr>
<tr>
  <td colspan="100">
    <span vitec-if="selger.tlf != &quot;&quot;">Mob: [[*selger.tlf]]</span>
    <span vitec-if="(selger.tlf != &quot;&quot; &amp;&amp; selger.emailadresse != &quot;&quot;)"> / </span>
    <span vitec-if="selger.emailadresse != &quot;&quot;">E-post: [[*selger.emailadresse]]</span>
  </td>
</tr>
<tr><td colspan="100">&nbsp;</td></tr>
</tbody>
</table>
```

Same pattern for `Model.kjopere` with `kjoper` as loop variable.

### Collection Guard Rule

Every `vitec-foreach` **must** have a collection guard on its parent element:

```html
<table vitec-if="Model.selgere.Count &gt; 0">
  <tbody vitec-foreach="selger in Model.selgere">
```

---

## 7. Reference Patterns Library

Copy-pasteable CSS and HTML patterns from working Vitec production templates. These patterns are
verified against the PDF renderer and CKEditor 4 ACF.

### SVG Checkbox CSS (include in template `<style>`)

```css
#vitecTemplate label.btn {
  display: inline-block;
  cursor: default;
  -webkit-user-select: none;
  -moz-user-select: none;
  user-select: none;
}
#vitecTemplate label.btn input[type="checkbox"] {
  display: none;
}
#vitecTemplate .svg-toggle.checkbox {
  display: inline-block;
  width: 16px;
  height: 16px;
  vertical-align: text-bottom;
  background-image: url("data:image/svg+xml,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20viewBox%3D%220%200%2016%2016%22%3E%3Crect%20width%3D%2215%22%20height%3D%2215%22%20x%3D%22.5%22%20y%3D%22.5%22%20fill%3D%22%23fff%22%20stroke%3D%22%23000%22%20rx%3D%222%22%20ry%3D%222%22%2F%3E%3C%2Fsvg%3E");
  background-size: contain;
  background-repeat: no-repeat;
}
#vitecTemplate label.btn.active .svg-toggle.checkbox {
  background-image: url("data:image/svg+xml,%3Csvg%20xmlns%3D%22http%3A%2F%2Fwww.w3.org%2F2000%2Fsvg%22%20viewBox%3D%220%200%2016%2016%22%3E%3Crect%20width%3D%2215%22%20height%3D%2215%22%20x%3D%22.5%22%20y%3D%22.5%22%20fill%3D%22%23fff%22%20stroke%3D%22%23000%22%20rx%3D%222%22%20ry%3D%222%22%2F%3E%3Cpath%20fill%3D%22%23000%22%20d%3D%22M12.207%204.793a1%201%200%200%201%200%201.414l-5%205a1%201%200%200%201-1.414%200l-2-2a1%201%200%200%201%201.414-1.414L6.5%209.086l4.293-4.293a1%201%200%200%201%201.414%200z%22%2F%3E%3C%2Fsvg%3E");
}
```

### Insert Field CSS (include in template `<style>`)

```css
#vitecTemplate .insert {
  border-bottom: 1px dotted #999;
  min-width: 80px;
  display: inline-block;
}
#vitecTemplate span.insert:empty::before {
  content: attr(data-label);
  color: #999;
  font-style: italic;
}
#vitecTemplate .insert-table {
  display: inline-table;
}
```

### Insert Field HTML Pattern

```html
<span class="insert-table"><span class="insert" data-label="dato"></span></span>
```

Common `data-label` values: `"dato"`, `"bel&oslash;p"`, `"tekst"`, `"klokkeslett"`, `"adresse"`.

### Entity Encoding Map

All Norwegian characters in template text content must use these entities:

| Character | Entity | Character | Entity |
|-----------|--------|-----------|--------|
| &oslash; | `&oslash;` | &Oslash; | `&Oslash;` |
| &aring; | `&aring;` | &Aring; | `&Aring;` |
| &aelig; | `&aelig;` | &AElig; | `&AElig;` |
| &sect; | `&sect;` | &laquo; | `&laquo;` |
| &raquo; | `&raquo;` | &ndash; | `&ndash;` |
| &mdash; | `&mdash;` | &eacute; | `&eacute;` |

### Outer Table Body Wrapper

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
        <h1>Template Title</h1>
        <!-- All body content -->
      </td>
    </tr>
  </tbody>
</table>
```

### Signature Block Pattern

```html
<div class="avoid-page-break">
  <article class="item">
    <h2>Underskrift</h2>
    <table style="width:100%; table-layout:fixed;">
      <tbody>
        <tr>
          <td colspan="45" style="border-bottom: solid 1px #000; padding-top:40px;">&nbsp;</td>
          <td colspan="10">&nbsp;</td>
          <td colspan="45" style="border-bottom: solid 1px #000; padding-top:40px;">&nbsp;</td>
        </tr>
        <tr>
          <td colspan="45"><em>Selger</em></td>
          <td colspan="10">&nbsp;</td>
          <td colspan="45"><em>Kj&oslash;per</em></td>
        </tr>
      </tbody>
    </table>
  </article>
</div>
```

For multi-party signatures, use `vitec-foreach` loops to generate one signing line per party.

### Page Break Controls (T3+ mandatory)

**CSS rule (already in the complete CSS block above):**
```css
#vitecTemplate .avoid-page-break { page-break-inside: avoid; }
```

**Short sections** — add class directly to `<article>`:
```html
<article class="avoid-page-break item">
```

**Long sections** — wrap heading + key content in internal divs:
```html
<article class="item">
  <div class="avoid-page-break">
    <h2>HEADING</h2>
    <p>First paragraph...</p>
    <table><!-- keep table with heading --></table>
  </div>
  <!-- remaining content flows naturally -->
</article>
```

**Forced page break** — sparingly at major transitions:
```html
<article class="item" style="page-break-before: always;">
```

**Coverage targets (from golden standard analysis):**
- Minimum 20 `avoid-page-break` wrappers for T4 contracts
- At least half the article sections should be protected
- 1-2 forced page breaks at natural document transitions
- Financial tables, checkbox groups, and bullet lists must stay together
- Signature block always wrapped

**Where to apply:**
| Element | Action |
|---------|--------|
| Section heading + first 1-2 paragraphs | `<div class="avoid-page-break">` |
| Short section (1-4 paragraphs) | `<article class="avoid-page-break item">` |
| Financial table (costs-table) | `<div class="avoid-page-break">` around table |
| Checkbox group with labels | `<div class="avoid-page-break">` |
| Bullet/numbered lists | `<div class="avoid-page-break">` |
| Signature block | `<div class="avoid-page-break" style="page-break-before: always;">` |
| Major section transition (Overtakelse) | `style="page-break-before: always;"` on article |

**Validator check:** `scripts/tools/validate_vitec_template.py` Section L reports page break coverage.

### Roles Table with rowspan

```html
<table class="roles-table" style="width:100%; table-layout:fixed;">
  <thead>
    <tr>
      <th colspan="34"><strong>Navn</strong></th>
      <th colspan="48"><strong>Adresse</strong></th>
      <th colspan="18"><strong>[[selger.ledetekst_fdato_orgnr]]</strong></th>
    </tr>
  </thead>
  <tbody vitec-foreach="selger in Model.selgere">
    <tr>
      <td colspan="34" rowspan="2">[[*selger.navnutenfullmektigogkontaktperson]]</td>
      <td colspan="48">[[*selger.gatenavnognr]], [[*selger.postnr]] [[*selger.poststed]]</td>
      <td colspan="18" rowspan="2">[[*selger.fdato_orgnr]]</td>
    </tr>
    <tr>
      <td colspan="48">
        <span vitec-if="selger.tlf != &quot;&quot;">Mob: [[*selger.tlf]]</span>
        <span vitec-if="(selger.tlf != &quot;&quot; &amp;&amp; selger.emailadresse != &quot;&quot;)"> / </span>
        <span vitec-if="selger.emailadresse != &quot;&quot;">E-post: [[*selger.emailadresse]]</span>
      </td>
    </tr>
    <tr><td colspan="100">&nbsp;</td></tr>
  </tbody>
</table>
```

### Inline List with Separator

```html
<span class="liste">
  <span class="separator">, </span>
  <!-- repeated items -->
</span>
```

CSS for inline list:
```css
#vitecTemplate .liste { display: inline; }
#vitecTemplate .liste .separator { display: inline; }
#vitecTemplate .liste .separator:first-child { display: none; }
```

### Bookmark / Anchor Pattern

```html
<a name="seksjon_5" id="seksjon_5"></a>
```

Used for internal document cross-references.

---

## 8. Source Document Clue Recognition

When reading a source `.htm` or `.docx`, look for these patterns to identify what needs conversion:

| Source Pattern | What It Means | Action |
|---------------|---------------|--------|
| `#fieldname.context¤` | Legacy merge field | Map to `[[modern.field]]` |
| `font-family:Wingdings` + `q` character | Empty checkbox | Convert to SVG checkbox pattern (Section 7) |
| `color:red` in text | Conditional alternative | Create `vitec-if` branch |
| `fra/<u>med</u>` or slash-separated alternatives | Choose-one option | Create `vitec-if` with SVG checkbox |
| "Alt 1:" / "Alt 2:" labels | Explicit alternatives | Create `vitec-if` div blocks |
| "Boligen/fritidsboligen" | Property type conditional | Use `grunntype` condition |
| "1 A" / "1 B" section headers | Ownership form alternatives | Use `eieform` condition |
| `background:yellow` | Placeholder/example value | Replace with merge field or `insert-table` + `span.insert` |
| `…………` or `........................` | Fill-in blank | Replace with `<span class="insert-table"><span class="insert" data-label="..."></span></span>` |
| `<div class=WordSection*>` | Page break in Word | Remove wrapper, content becomes continuous |
| `<br clear=all style='page-break-before:always'>` | Explicit page break | Remove |

---

## 9. Validation Script

A unified validation script exists at `scripts/tools/validate_vitec_template.py`. Run it after every
template build:

```bash
python scripts/tools/validate_vitec_template.py scripts/production/MyTemplate_PRODUCTION.html --tier 4
```

Options:
- `--tier {1-5}` — Complexity tier. Section J (contract-specific) checks are skipped for T1/T2.
- `--compare-snapshot snapshot.html` — Mode A regression comparison against a pre-edit baseline.

Target: **All checks PASS** before any template is considered production-ready.

See `AGENT-2B-PIPELINE-DESIGN.md` for the full pipeline including Live Verification (S9).

---

## 10. Template Inventory

### Pilot Template (Complete)

| Template | Source | Status | Sections | Fields | Conditions | Loops | Validation |
|----------|--------|--------|----------|--------|------------|-------|------------|
| Kjøpekontrakt prosjekt (enebolig med delinnbetalinger) | `.htm` | **Done** | 20 | 48 | 54 | 4 | 39/39 |

### Remaining Templates (From `maler vi må få produsert/`)

These are the templates that still need production conversion. Based on the pilot, here are effort estimates and structural notes:

| # | Template | Type | Est. Effort | Shares Structure With |
|---|----------|------|-------------|----------------------|
| 1 | Kjøpekontrakt prosjekt (leilighet) | Kjøpekontrakt | 20 min | Pilot (~85% shared) |
| 2 | Kjøpekontrakt prosjekt (rekkehus) | Kjøpekontrakt | 20 min | Pilot (~85% shared) |
| 3 | Kjøpekontrakt prosjekt (fritidsbolig) | Kjøpekontrakt | 20 min | Pilot (~85% shared) |
| 4 | Kjøpekontrakt forbruker selveier | Kjøpekontrakt | 30 min | Pilot (~70% shared) |
| 5 | Kjøpekontrakt forbruker eierseksjon | Kjøpekontrakt | 30 min | Pilot (~70% shared) |
| 6 | Meglerstandard oppdragsavtale bolig | Oppdragsavtale | 60 min | New structure |
| 7 | Meglerstandard oppdragsavtale næring | Oppdragsavtale | 60 min | #6 (~80% shared) |
| 8 | Meglerstandard oppdragsavtale nybygg | Oppdragsavtale | 60 min | #6 (~80% shared) |
| 9 | Oppdragsavtale prosjekt | Oppdragsavtale | 45 min | #6 (~60% shared) |
| 10 | E-takst oppdragsavtale | Oppdragsavtale | 30 min | #6 (~50% shared) |
| 11 | Leieavtale bolig | Leieavtale | 60 min | New structure |
| 12 | Leieavtale næring | Leieavtale | 60 min | #11 (~70% shared) |
| 13 | Leieavtale korttid | Leieavtale | 45 min | #11 (~60% shared) |

**Recommended execution order:**
1. Kjøpekontrakt variants (2-5) — reuse pilot structure, swap differing clauses
2. Oppdragsavtale group (6-10) — new structure, then clone+modify
3. Leieavtale group (11-13) — new structure, then clone+modify

---

## 11. Agent Instructions for Template Conversion

### Pre-Requisites

Before starting any template conversion:

1. Read `CLAUDE.md` for project context (includes Template Source of Truth hierarchy)
2. Read builder knowledge base: `.agents/skills/vitec-template-builder/LESSONS.md`, `PATTERNS.md`, `SKILL.md`
3. Read this document (`PRODUCTION-TEMPLATE-PIPELINE.md`) in full
4. Have the source `.htm` file saved from Word (Web Page, Filtered format)
5. Have the original PDF for content verification

### Step-by-Step Process

1. **Read the source `.htm` file** — Scan all sections, identify:
   - Total number of sections/articles
   - All legacy merge fields (`#field.context¤` patterns)
   - Checkboxes (Wingdings `q`)
   - Red text alternatives
   - Alternative sections (1A/1B, Alt 1/Alt 2)
   - Tables and their purpose
   - Signature blocks

2. **Check the field mapping** — For each legacy field found, look up the modern equivalent in Section 4 of this document. If a field isn't in the mapping, check `.cursor/Alle-flettekoder-25.9.md` for the correct path.

3. **Build the template** — Either:
   - (a) Start from the pilot template and modify for the variant (for Kjøpekontrakt variants)
   - (b) Build from scratch following the 6-step pipeline (for new template types)

4. **Run validation** — Use `scripts/tools/validate_vitec_template.py template.html --tier N`. Target all checks PASS.

5. **Build preview** — Use `scripts/tools/build_preview.py` to generate a visual preview. Open in browser to verify rendering.

6. **Compare against PDF** — Section by section, verify:
   - All sections present
   - All legal text accurate (verbatim from source)
   - All merge fields properly placed
   - All conditionals correctly branched
   - Norwegian characters preserved

### Quality Checklist (Quick Reference)

- [ ] `<div id="vitecTemplate">` wrapper (NO `class="proaktiv-theme"`)
- [ ] `<span vitec-template="resource:Vitec Stilark">&nbsp;</span>` present
- [ ] CSS block with counters + SVG checkbox + insert field styles
- [ ] Counter `::before` uses `display: inline-block; width: 26px;` (double-digit alignment)
- [ ] Article `padding-left: 26px` matches h2 `margin-left: -26px`
- [ ] Outer `<table>` body wrapper with `<small>` header info
- [ ] `<h1>` for template title
- [ ] All `<article class="item">` with `<h2>` headings
- [ ] All legacy `#field¤` syntax replaced
- [ ] All `vitec-if` use `&quot;` for quotes, `&gt;` for `>`
- [ ] All `vitec-foreach` have collection guards AND fallback placeholders
- [ ] `roles-table` class on party tables
- [ ] `costs-table` class on financial tables
- [ ] Signature block with `border-bottom: solid 1px #000`
- [ ] `insert-table` + `span.insert` with `data-label` for fill-in fields
- [ ] `avoid-page-break` on signature section and all short sections (T3+)
- [ ] `avoid-page-break` divs around headings + key content in long sections (T3+)
- [ ] Forced page breaks at major transition points (T4+)
- [ ] Page break coverage: min 20 wrappers for T4, validator Section L PASS
- [ ] All Norwegian characters are HTML entities — NO literal UTF-8
- [ ] No Unicode checkboxes — SVG checkboxes only
- [ ] Data-driven checkboxes have NO `<input>` tag (system sets state via vitec-if)
- [ ] All monetary merge fields wrapped in `$.UD()`
- [ ] No inline `font-family` or `font-size`
- [ ] Static validation: `scripts/tools/validate_vitec_template.py` all checks PASS

### Hard Rules (Non-Negotiable)

- Legal text must be **verbatim** from the source document — never paraphrase
- All Norwegian characters in text content must be HTML entities — never literal UTF-8
- All checkboxes must use the SVG pattern — never Unicode &#9744;/&#9745;
- All monetary merge fields must use `$.UD()` wrapper
- All `vitec-if` expressions must use `&quot;` for quotes, `&gt;` for greater-than
- All `vitec-foreach` loops must have both a `Count > 0` guard AND a `Count == 0` fallback
- All insert fields must use `insert-table` wrapper with `data-label`
- If a field mapping is unclear, flag it in the handoff summary under "Potential Issues" — don't guess silently
- **Do NOT** attempt to upload, test in Vitec Next, or commit to the database

---

## 12. Handoff Summary Format

Every completed template build must produce a handoff summary Markdown file alongside the
production HTML. Place it at `scripts/handoffs/<TemplateName>_HANDOFF.md`.

```markdown
# Handoff: [Template Name]

## Spec
- **Mode:** [A/B/C] ([Edit/Convert/Create])
- **Tier:** [T1-T5] ([Description])
- **Template:** [Full template name]

## Production File
- **Path:** `scripts/production/<TemplateName>_PRODUCTION.html`
- **Size:** [X chars]
- **Build script:** `scripts/build_<template_name>.py`

## Template Stats
- Sections: [count]
- Merge fields: [count] — [list all field paths]
- vitec-if conditions: [count]
- vitec-foreach loops: [count] — [list each "item in Collection"]
- Insert fields: [count]
- SVG checkboxes: [count]

## Validation Result
- Validator: `scripts/tools/validate_vitec_template.py --tier [N]`
- Result: [X/Y PASS, Z FAIL]
- [Paste the full validator output here]

## Fixes Applied
[List each fix applied with a one-line summary of what changed]

## Potential Issues & Uncertainties
[List anything the builder is uncertain about, e.g.:]
- Field mappings that were guessed rather than confirmed
- Legal text sections where the source was ambiguous
- Sections where another template was used as reference because the source didn't cover it
- Merge field paths that couldn't be verified against the field registry
- Any structural choices that differ from the reference and why

## Content Notes
[Anything relevant about the template content:]
- Which source document sections were used verbatim
- Which sections were adapted from another template
- Payment model details (if applicable)
- Guarantee provisions included (if applicable)

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

---

## 13. Files Reference

| File | Purpose |
|------|---------|
| `scripts/build_production_template.py` | Builds the pilot Kjøpekontrakt template |
| `scripts/tools/build_preview.py` | Generates visual preview with Stilark CSS |
| `scripts/tools/validate_vitec_template.py` | Unified static validation (`python scripts/tools/validate_vitec_template.py template.html --tier N`) |
| `scripts/sources/` | Source .htm files (UTF-8 copies) |
| `scripts/production/` | Output production HTML templates |
| `scripts/handoffs/` | Handoff summary markdown files |
| `scripts/reference_templates/` | Working Vitec reference templates for pattern comparison |
| `scripts/snapshots/` | Pre-edit snapshots for Mode A regression comparison |
| `scripts/qa_artifacts/` | Testfletting PDF downloads from Live Verification |
| `.planning/vitec-html-ruleset/` | HTML ruleset (supplementary — based on old Proaktiv DB, not authoritative) |
| `.planning/field-registry.md` | Structured merge field registry (668 fields) |
| `.cursor/Alle-flettekoder-25.9.md` | Complete merge field reference (6,494 lines) |
| `docs/vitec-stilark.md` | Vitec Stilark CSS |
| `AGENT-2B-PIPELINE-DESIGN.md` | Pipeline design (stages S0-S10, modes, tiers) |
| `AGENT-2B-TEMPLATE-BUILDER.md` | Agent task specification |

---

## 14. Known Issues & Edge Cases

1. **Console encoding:** Norwegian characters (ø, å, æ) may display as `?` in PowerShell console output. This is a console display issue, not a file encoding problem. Verify by reading the actual file bytes.

2. **File locking:** Word locks `.htm` files while open. The agent will get `IOException` when trying to read. User must close the file in Word first.

3. **Wingdings in .docx:** When mammoth processes .docx files, Wingdings checkboxes become plain `<li>` bullet items, losing the checkbox semantics. The .htm format preserves them.

4. **Red text in .docx:** mammoth strips color styles, so red-text conditional markers are invisible in .docx conversion. The .htm format preserves `color:red` inline styles.

5. **Empty collections:** Some vitec-foreach collections may be empty in certain contexts. Always add a collection guard (`vitec-if="Model.collection.Count &gt; 0"`) on the table/container.

6. **"Mangler data" sentinel:** Vitec Next returns the string `"Mangler data"` for fields that have no value. This is different from an empty string. Use `!= &quot;Mangler data&quot;` for date fields that might not be set.

7. **Field paths with asterisk:** Inside a `vitec-foreach` loop, all merge fields referencing the loop variable must use `[[*variable.field]]` (with asterisk) to indicate they are required within the loop context.

---

## 15. Subagent Architecture (T3+ Mode B/C)

For complex templates (T3+), the build process uses an orchestrator + specialized subagents
to improve accuracy and reduce per-agent context load.

### Architecture Overview

```
User drops source file
        │
   ORCHESTRATOR (main agent)
        │
        ├── S0: Intake (Mode/Tier/Scope)
        │
        ├── Phase 1: ANALYSIS (3 parallel subagents, fast model)
        │   ├── Structure Analyzer → _analysis/{name}/structure.md
        │   ├── Field Mapper       → _analysis/{name}/fields.md
        │   └── Logic Mapper       → _analysis/{name}/logic.md
        │
        ├── Quality Gate: check for NEED REVIEW flags
        │
        ├── Phase 2: CONSTRUCTION (1 subagent, default model)
        │   └── Builder → build script + production HTML
        │
        ├── Phase 3: VALIDATION (2 parallel subagents, fast model)
        │   ├── Static Validator → validation report
        │   └── Content Verifier → content accuracy report
        │
        ├── Pass/Fail Decision
        │   ├── PASS → Handoff summary
        │   └── FAIL → Resume builder with specific fixes
        │
        └── Handoff
```

### Why Subagents?

The single-agent approach loads ~15,000+ lines of context (source document, pipeline docs,
ruleset sections, field registry, reference templates) into one agent. This causes:

- **Attention dilution** — content errors (wrong payment model), pattern errors (wrong CSS),
  missed conditional logic
- **Sequential bottleneck** — field mapping, structure analysis, and logic planning are
  independent tasks that can run in parallel
- **No built-in validation loop** — issues only found after manual human review

The subagent approach gives each agent a narrow, focused task with only the context it needs.

### Token Efficiency

| Agent              | Context Lines | Model  | Cost   |
|--------------------|---------------|--------|--------|
| Structure Analyzer | ~1,500        | fast   | 1/10x  |
| Field Mapper       | ~2,200        | fast   | 1/10x  |
| Logic Mapper       | ~2,000        | fast   | 1/10x  |
| Builder            | ~1,200        | default| 1x     |
| Static Validator   | ~800          | fast   | 1/10x  |
| Content Verifier   | ~2,500        | fast   | 1/10x  |
| Orchestrator       | ~500          | —      | —      |

The expensive default model processes ~1,200 lines of pre-analyzed content instead of
~15,000 lines of raw references. The fast models handle mechanical analysis and validation.

### Files

| File | Purpose |
|------|---------|
| `SUBAGENT-PROMPTS.md` | Complete prompt templates with {placeholders} |
| `scripts/_analysis/FORMAT_structure.md` | Output format for Structure Analyzer |
| `scripts/_analysis/FORMAT_fields.md` | Output format for Field Mapper |
| `scripts/_analysis/FORMAT_logic.md` | Output format for Logic Mapper |
| `scripts/_analysis/{template_name}/` | Per-template analysis outputs |

### When to Use Direct Mode Instead

- **T1/T2 templates** — too simple for subagent overhead
- **Mode A edits** — surgical changes don't need full analysis
- **Subagents unavailable** — fall back to `AGENT-2B-PIPELINE-DESIGN.md` stages S1-S10

### Post-Delivery Analysis (Separate Process)

The build pipeline's validation catches structural and compliance issues. Deep quality
review (visual comparison, golden standard alignment, edge case detection) is a separate
human-triggered process using the Analysis Agent (`ANALYSIS-AGENT-PROMPT.md`).
This separation keeps the build pipeline focused on delivery while allowing thorough
review at a different quality bar.
