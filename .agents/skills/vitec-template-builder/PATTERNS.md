# Reference Pattern Library

Copy-pasteable code blocks for every standard Vitec template pattern.
Extracted from **working reference templates** (bruktbolig, forbruker, oppdragsavtale) and
verified against the **249 official Vitec Next templates** scraped from production (2026-02-23).

**Source of truth:** The working reference templates and Vitec Stilark are authoritative.
The old `vitec-html-ruleset-FULL.md` (based on 133 Proaktiv DB templates) is supplementary only.

**Rule:** Use these patterns verbatim. Do not improvise alternatives.

---

## 1. Template Shell

The outermost structure every template must have:

```html
<div id="vitecTemplate">
<span vitec-template="resource:Vitec Stilark">&nbsp;</span>
<style type="text/css">
/* CSS block goes here — see patterns below */
</style>
<!-- Optional: SVG checkbox CSS in separate <style> block -->
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
        <h1>TEMPLATE TITLE HERE</h1>
        <!-- All body content inside this cell -->
      </td>
    </tr>
  </tbody>
</table>
</div>
```

**Key rules:**
- `id="vitecTemplate"` — NO `class="proaktiv-theme"`
- Stilark resource span with `&nbsp;` content
- Body wrapped in `<table><tbody><tr><td colspan="100">`
- Title as `<h1>`, never `<h5>`

---

## 2. CSS Block — Core (T3+)

Matches production Kjøpekontrakt Bruktbolig / Kjøpekontrakt FORBRUKER exactly (2026-02-23).

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
}

#vitecTemplate article.item article.item h3::before {
    content: counter(section) "." counter(subsection) ". ";
}

#vitecTemplate .avoid-page-break {
    page-break-inside: avoid;
}

#vitecTemplate article {
    padding-left: 20px;
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
    margin: 30px 0 0 -20px;
    padding: 0;
}

#vitecTemplate h3 {
    font-size: 10pt;
    margin: 20px 0 0 0;
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
```

**Key production values (do NOT deviate):**
- Article padding: `20px` (not 26px)
- H2 margin-left: `-20px` (matches article padding, pulls heading flush left)
- Counter `::before` selectors: `content:` ONLY — no `display` or `width` properties
- H3 counter content includes trailing period: `". "` after subsection number
- `.borders` class is scoped under `#vitecTemplate table`
- No `.costs-table` or `.roles-table th/td` rules — the Stilark provides base table styles

---

## 3. CSS Block — Insert Fields + Roles/Bookmark/Liste (unscoped section)

This block is placed after the scoped `#vitecTemplate` rules, still within the same `<style>` tag.
These selectors are intentionally UNSCOPED (no `#vitecTemplate` prefix) to match production.
The `.insert-table { display: inline-table }` pattern is the Chromium-compatible fix — it ensures
insert fields render correctly in both Chromium-based browsers and Vitec's PDF renderer.

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

**Key rules:**
- `span.insert:empty`, `.insert-table` — UNSCOPED (no `#vitecTemplate` prefix)
- `.roles-table` — Only the hide-last-row rule (Stilark provides base table styles)
- `.liste:last-child .separator` — Only this one rule (no `.liste { display: inline }` etc.)
- `.insert-table { display: inline-table }` — Critical for Chromium rendering of insert fields

**Insert field HTML usage:**
```html
<span class="insert-table"><span class="insert" data-label="dato"></span></span>
```

---

## 4. CSS Block — SVG Checkboxes (Separate `<style>` tag)

Place this in a SEPARATE `<style>` block after the main CSS.
**SVG encoding:** Data URIs use `;utf8,<svg...>` inline format (not percent-encoded `%3Csvg`). Empirically confirmed: 74 of 75 templates with SVG checkboxes use utf8 inline encoding (mining report 2026-02-24).

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
#vitecTemplate [data-toggle="buttons"] input {
  display: none;
}
```

---

## 5. Broker-Interactive Checkbox (User Toggles)

```html
<label class="btn" contenteditable="false" data-toggle="button">
  <span class="checkbox svg-toggle"></span>
</label>
```

With label text:
```html
<label class="btn" contenteditable="false" data-toggle="button">
  <span class="checkbox svg-toggle"></span>
</label> Alternativ A: Full betaling ved overtakelse
```

---

## 6. Data-Driven Checkbox (System Sets State)

NO `<input>` tag. State controlled by `vitec-if`:

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

---

## 7. Party Loop (foreach with Guard + Fallback)

```html
<div vitec-if="Model.selgere.Count &gt; 0">
  <table class="roles-table">
    <thead>
      <tr>
        <th style="width:45%">Navn</th>
        <th style="width:30%">Adresse</th>
        <th style="width:25%">[[selger.ledetekst_fdato_orgnr]]</th>
      </tr>
    </thead>
    <tbody vitec-foreach="selger in Model.selgere">
      <tr>
        <td>[[*selger.navnutenfullmektigogkontaktperson]]</td>
        <td>[[*selger.gatenavnognr]], [[*selger.postnr]] [[*selger.poststed]]</td>
        <td>[[*selger.fdato_orgnr]]</td>
      </tr>
      <tr vitec-if="Model.selger.fullmektig.navn != &quot;&quot;">
        <td colspan="3"><em>v/ fullmektig: [[*selger.fullmektig.navn]]</em></td>
      </tr>
    </tbody>
  </table>
</div>
<div vitec-if="Model.selgere.Count == 0">
  <p>[Mangler selgerinformasjon]</p>
</div>
```

**Key rules:**
- `vitec-foreach` goes on `<tbody>`, not `<table>` or `<tr>`
- Fields inside foreach use `[[*variable.field]]` (asterisk prefix)
- Guard checks `.Count &gt; 0` (HTML-encoded `>`)
- Fallback checks `.Count == 0`

---

## 8. Safe Fallback Pattern (Triple-Span Guard)

For critical fields that might be empty or return "Mangler data":

```html
<span vitec-if="Model.field != &quot;&quot; &amp;&amp; Model.field != &quot;Mangler data&quot;">[[field]]</span><span vitec-if="Model.field == &quot;&quot;"><span class="insert-table"><span class="insert" data-label="placeholder"></span></span></span><span vitec-if="Model.field == &quot;Mangler data&quot;"><span class="insert-table"><span class="insert" data-label="placeholder"></span></span></span>
```

Use for: header info (org.nr, oppdragsnr, omsetningsnr), party fields in loops, date fields, address fields.

---

## 9. Article Section (T3+)

### Short section (avoid page break on entire article):
```html
<article class="avoid-page-break item">
  <h2>SECTION HEADING</h2>
  <p>Content paragraph...</p>
</article>
```

### Long section (selective page break protection):
```html
<article class="item">
  <div class="avoid-page-break">
    <h2>SECTION HEADING</h2>
    <p>First paragraph that must stay with heading...</p>
  </div>
  <p>Content that can break naturally...</p>
  <div class="avoid-page-break">
    <table class="roles-table"><!-- table that must stay together --></table>
  </div>
</article>
```

### Forced page break at major transition:
```html
<article class="item" style="page-break-before: always;">
  <h2>MAJOR SECTION</h2>
</article>
```

---

## 10. Costs Table (Buyer/Seller Costs)

```html
<div vitec-if="Model.kjoperskostnader.alleposter.Count &gt; 0">
  <table class="costs-table">
    <tbody vitec-foreach="kostnad in Model.kjoperskostnader.alleposter">
      <tr>
        <td style="width:70%">[[*kostnad.beskrivelse]]</td>
        <td style="width:30%; text-align:right">$.UD([[*kostnad.belop]])</td>
      </tr>
    </tbody>
    <tr class="sum-row">
      <td>Sum</td>
      <td style="text-align:right">$.UD([[kontrakt.totaleomkostninger]])</td>
    </tr>
  </table>
</div>
<div vitec-if="Model.kjoperskostnader.alleposter.Count == 0">
  <p>[Ingen kj&oslash;perskostnader registrert]</p>
</div>
```

---

## 11. Signature Block

```html
<article class="avoid-page-break item" style="page-break-before: always;">
  <h2>UNDERSKRIFT</h2>
  <p>&nbsp;</p>
  <table class="roles-table">
    <tbody>
      <tr>
        <td style="width:50%">
          <p>Sted: <span vitec-if="Model.meglerkontor.poststed != &quot;&quot;">[[meglerkontor.poststed]]</span><span vitec-if="Model.meglerkontor.poststed == &quot;&quot;"><span class="insert-table"><span class="insert" data-label="sted"></span></span></span></p>
        </td>
        <td style="width:50%">
          <p>Dato: <span vitec-if="Model.kontrakt.dato != &quot;&quot;">[[kontrakt.dato]]</span><span vitec-if="Model.kontrakt.dato == &quot;&quot;"><span class="insert-table"><span class="insert" data-label="dato"></span></span></span></p>
        </td>
      </tr>
    </tbody>
  </table>
  <p>&nbsp;</p>
  <table class="roles-table">
    <tbody>
      <tr>
        <td style="width:50%">
          <p style="border-bottom: 1px solid #000; padding-bottom: 40px;">&nbsp;</p>
          <p>Selger</p>
        </td>
        <td style="width:50%">
          <p style="border-bottom: 1px solid #000; padding-bottom: 40px;">&nbsp;</p>
          <p>Kj&oslash;per</p>
        </td>
      </tr>
    </tbody>
  </table>
  <p>&nbsp;</p>
  <table class="roles-table">
    <tbody>
      <tr>
        <td style="width:50%">
          <p style="border-bottom: 1px solid #000; padding-bottom: 40px;">&nbsp;</p>
          <p>Selger</p>
        </td>
        <td style="width:50%">
          <p style="border-bottom: 1px solid #000; padding-bottom: 40px;">&nbsp;</p>
          <p>Kj&oslash;per</p>
        </td>
      </tr>
    </tbody>
  </table>
  <p>&nbsp;</p>
  <table class="roles-table">
    <tbody>
      <tr>
        <td>
          <p style="border-bottom: 1px solid #000; padding-bottom: 40px;">&nbsp;</p>
          <p>Ansvarlig megler: [[operativmegler.navn]]</p>
        </td>
      </tr>
    </tbody>
  </table>
</article>
```

---

## 12. Conditional Content (vitec-if)

### Simple condition:
```html
<span vitec-if="Model.eiendom.grunntype == &quot;Bolig&quot;">boligen</span>
<span vitec-if="Model.eiendom.grunntype == &quot;Fritid&quot;">fritidsboligen</span>
```

### Norwegian characters in condition values:
```html
<span vitec-if="Model.oppdrag.hovedtype == &quot;Oppgj\xF8rsoppdrag&quot;">
  <!-- content for oppgjorsoppdrag -->
</span>
```

### Multi-condition with AND:
```html
<div vitec-if="Model.eiendom.eieform == &quot;Selveier&quot; &amp;&amp; Model.eiendom.grunntype == &quot;Bolig&quot;">
```

### Section alternative (A/B pattern):
```html
<div vitec-if="Model.eiendom.eieform == &quot;Selveier&quot;">
  <p>Selveier-specific content...</p>
</div>
<div vitec-if="Model.eiendom.eieform == &quot;Borettslag&quot;">
  <p>Borettslag-specific content...</p>
</div>
```

---

## 13. Entity Encoding Reference

**Text content** — always use HTML entities:
| Char | Entity |
|------|--------|
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

**vitec-if string values** — use unicode escapes:
| Char | Escape |
|------|--------|
| ø | `\xF8` |
| å | `\xE5` |
| æ | `\xE6` |
| Ø | `\xD8` |
| Å | `\xC5` |
| Æ | `\xC6` |

**vitec-if operators** — use HTML entities:
| Operator | Entity |
|----------|--------|
| `"` | `&quot;` |
| `>` | `&gt;` |
| `<` | `&lt;` |
| `&&` | `&amp;&amp;` |

---

## 14. Hjemmelshaver Fallback Pattern

When hjemmelshavere collection is empty, fall back to selgere names:

```html
<div vitec-if="Model.hjemmelshavere.Count &gt; 0">
  <table class="roles-table">
    <tbody vitec-foreach="hjemmelshaver in Model.hjemmelshavere">
      <tr>
        <td>[[*hjemmelshaver.navn]]</td>
        <td>[[*hjemmelshaver.fdato_orgnr]]</td>
      </tr>
    </tbody>
  </table>
</div>
<div vitec-if="Model.hjemmelshavere.Count == 0">
  <div vitec-if="Model.selgere.Count &gt; 0">
    <table class="roles-table">
      <tbody vitec-foreach="selger in Model.selgere">
        <tr>
          <td>[[*selger.navnutenfullmektigogkontaktperson]]</td>
          <td>[[*selger.fdato_orgnr]]</td>
        </tr>
      </tbody>
    </table>
  </div>
  <div vitec-if="Model.selgere.Count == 0">
    <p>[Mangler hjemmelshaverinformasjon]</p>
  </div>
</div>
```
