## 1. Required Template Shell

Every Vitec Next template must follow this outer structure:

```html
<div class="proaktiv-theme" id="vitecTemplate">
  <span vitec-template="resource:Vitec Stilark">&nbsp;</span>
  <!-- Template content here -->
</div>
```

### Mandatory elements

| Element | Purpose | Evidence |
|---------|---------|----------|
| `<div class="proaktiv-theme" id="vitecTemplate">` | Root wrapper. All Stilark CSS rules are scoped under `#vitecTemplate`. The `proaktiv-theme` class provides company-specific overrides. **All 133 database templates** use both `class="proaktiv-theme"` and `id="vitecTemplate"`. | Every template in the database (DB evidence: all 133 templates) |
| `<span vitec-template="resource:Vitec Stilark">&nbsp;</span>` | At render time, this span is replaced by `<div id="vitec-stilark" style="display:inline"><style>...</style></div>` containing the base CSS (Open Sans font, 10pt, ligature prevention, table reset). Must contain `&nbsp;` (not empty). See Section 7 for complete Stilark source. | `Alle-flettekoder-25.9.md` line 1, all header/footer templates, Stilark system template source |

#### Support template references

The `vitec-template="resource:..."` mechanism is not limited to the Stilark stylesheet. Templates can reference **additional system templates** as support files — for example, a template containing `@functions` helper methods:

```html
<div id="vitecTemplate">
<span vitec-template="resource:Vitec Stilark">&nbsp;</span>
<span vitec-template="resource:Boligkjøperforsikring">&nbsp;</span>
```

The support template reference appears immediately after the Stilark reference, before the `<style>` block. Both use identical syntax — a `<span>` with `vitec-template="resource:TemplateName"` containing `&nbsp;`.

This allows templates to pull in custom C# methods, shared HTML partials, or other resources defined as separate system templates. The support template pattern is used when standard merge fields and vitec-if/foreach logic are insufficient — e.g., when complex LINQ filtering or value extraction is needed. See the `@functions` section below for a concrete example.

**(Evidence: custom Proaktiv Kjøpekontrakt Bruktbolig — references support template named "Boligkjøperforsikring")**

### A4 page dimensions

Templates targeting PDF output use a fixed A4 width:

```html
<table style="width:21cm; table-layout:fixed">
```

Standard margins are applied via inline `padding`:
- Left/right: `1cm` (applied to `<td>` elements, e.g. `padding-left:1cm; padding-right:1cm`)
- Top/bottom: controlled by the header/footer template heights

**Evidence:** Standard header template uses `style="width:21cm"` on the outer table (`vitec-reference.md` line 941). Footer templates use `padding-left:1cm` on wrapper divs (`vitec-reference.md` line 855).

### Header and footer templates

Headers and footers are **separate system templates** that Vitec Next attaches to document templates at render time. They are NOT embedded inside the document template itself — they are standalone HTML templates configured per template through the admin interface's PDF settings.

> See also: **Section 13** for full documentation of the admin UI and all template settings.

#### How attachment works

1. **Per-template dropdown selection:** Each document template has **TOPPTEKST** (header) and **BUNNTEKST** (footer) dropdown selectors in the "Kategorisering → PDF-INNSTILLINGER" panel. These can be set to "Ingen" (none) or to any available system header/footer template (e.g., `Vitec Topptekst`, `Vitec Bunntekst Kontrakt`).

2. **Per-template margins:** The same panel configures page margins (TOPP, VENSTRE, HØYRE, BUNN) in centimeters, maximum 10cm. These values control the rendered PDF output spacing and affect how much room headers/footers have.

3. **Render-time injection:** When a document is generated as PDF, the Vitec rendering engine:
   - Renders the header template at the top of every page
   - Renders the document body template as the main content
   - Renders the footer template at the bottom of every page
   - Page numbering fields (`[[p]]`, `[[P]]`) are resolved across all three

4. **No `vitec-template` reference needed:** Unlike the Stilark (which must be explicitly referenced via `<span vitec-template="resource:Vitec Stilark">`), headers and footers do NOT need to be referenced from within the document template. They are injected by the system based on the formatting configuration.

#### System header/footer templates

The following system templates serve as headers and footers:

| Template name | Type | Purpose |
|--------------|------|---------|
| **Vitec Topptekst** | Header | Standard header with company name + logo |
| **Vitec Bunntekst** | Footer | Standard footer with office info (juridisk navn, adresse, org.nr, tlf, epost) |
| **Vitec Bunntekst Kontrakt** | Footer | Contract footer with Selger/Kjøper signature lines (conditional: Utleier/Leietaker for rentals) |
| **Vitec Bunntekst Fremleiekontrakt** | Footer | Sublease footer with Utleier/Fremleier/Fremleietaker signature lines |
| **Vitec Bunntekst Sidetall** | Footer | Minimal footer with page numbers only |
| **Vitec Bunntekst Sikring** | Footer | Pantedokument footer with Dato/Underskrift fields + "Statens kartverk" reference |
| **Vitec Bunntekst Skjøte** | Footer | Skjøte footer with Dato/Underskrift fields + "GA-5400 B" form number |
| **Vitec Bunntekst Oppdragsavtale** | Footer | Oppdragsavtale-specific footer with signature lines and office info |

Custom/company-specific header/footer templates (from database):

| Template name | Purpose |
|--------------|---------|
| **Proaktiv Standard Topptekst - Header Brevmal V.1.0** | Full letter header with Playfair Display + Open Sans fonts |
| **Proaktiv - Topptekst - Header Minimal V.1.0** | Minimal centered header with logo only |
| **Topptekst Proaktiv v3 (Vitec kopi)** | Latest Proaktiv header, Gold Navy theme |
| **Proaktiv Bunntekst Standard V.2.0** | Proaktiv custom footer, Gold Navy theme |

#### Header template structure

Headers use `#vitecTemplate` wrapper with a width-constrained table:

```html
<div class="proaktiv-theme" id="vitecTemplate">
  <span vitec-template="resource:Vitec Stilark">&nbsp;</span>
  <table style="width:21cm">
    <tbody>
      <tr>
        <td style="padding:1cm">
          <strong><small>[[meglerkontor.kjedenavn]]</small></strong>
        </td>
        <td style="padding:1cm; text-align:right">
          <img src="[[meglerkontor.firmalogourl]]" style="max-height:1.5cm; max-width:6cm" />
        </td>
      </tr>
    </tbody>
  </table>
</div>
```

Custom headers may use `#vitecHeader` as an inner wrapper for CSS scoping:
```html
<div class="proaktiv-theme" id="vitecTemplate">
  <div id="vitecHeader">
    <style type="text/css">
      #vitecHeader table { width: 100%; ... }
    </style>
    <!-- header content -->
  </div>
</div>
```

#### Footer template categories

Footers fall into three structural categories based on their CSS architecture:

**Category A: Stilark-based footers** (Vitec Bunntekst, Bunntekst Kontrakt, Bunntekst Fremleiekontrakt)
- Include Stilark via `<span vitec-template="resource:Vitec Stilark">`
- CSS comes from the Stilark
- Content inside `#vitecTemplate` div
- Use `<small>` for text sizing

**Category B: Custom-ID footers** (Bunntekst Oppdragsavtale, custom footers)
- Include Stilark but also add `<style>` block inside the div
- Use a custom table ID (`#bunntekstTabell`) for CSS scoping
- Taller heights for signature lines

**Category C: Self-contained footers** (Bunntekst Skjøte, Bunntekst Sikring, Bunntekst Sidetall)
- `<style>` block is placed **OUTSIDE and BEFORE** the `#vitecTemplate` div
- Load their own fonts via `@import url()` (Google Fonts Open Sans)
- Include full CSS reset (`html, body { margin: 0; padding: 0; }`)
- Add `font-variant-ligatures: none` on all elements
- Do NOT include Stilark reference

#### Footer: Vitec Bunntekst (Standard)

Standard 2-row footer with office info. Layout: **30/40/30 colspan**.

```html
<div id="vitecTemplate">
  <span vitec-template="resource:Vitec Stilark">&nbsp;</span>
  <table cellspacing="0" style="border-collapse:collapse; table-layout:fixed; width:21cm">
    <tbody>
      <tr>
        <td colspan="30" style="padding-left:1cm">
          <small>[[meglerkontor.juridisknavn]]</small>
        </td>
        <td colspan="40" style="text-align:center">
          <small>[[meglerkontor.adresse]], [[meglerkontor.postnr]] [[meglerkontor.poststed]]</small>
        </td>
        <td colspan="30" style="padding-right:1cm; text-align:right">
          <small>Tlf: [[meglerkontor.tlf]]</small>
        </td>
      </tr>
      <tr>
        <td colspan="30" style="padding-left:1cm">
          <small>Org.nr: [[meglerkontor.orgnr]]</small>
        </td>
        <td colspan="40" style="text-align:center">
          <small>Besøksadresse: [[meglerkontor.besoksadresse]], ...</small>
        </td>
        <td colspan="30" style="padding-right:1cm; text-align:right">
          <small>[[meglerkontor.epost]]</small>
        </td>
      </tr>
    </tbody>
  </table>
</div>
```

#### Footer: Vitec Bunntekst Kontrakt (conditional Salg/Utleie)

Two signature lines with conditional labels based on `Model.oppdrag.type`:

```html
<div id="vitecTemplate">
  <span vitec-template="resource:Vitec Stilark">&nbsp;</span>
  <table style="height:1.5cm; table-layout:fixed; width:20cm">
    <tbody>
      <tr>
        <td style="font-size:8pt; padding:0.25cm 0.5cm 0.5cm 2cm; vertical-align:bottom">
          <div style="border-top:solid 1px #000000; text-align:center; width:3cm">
            <span vitec-if="!Model.oppdrag.type.Contains(&quot;tleie&quot;)">Selger</span>
            <span vitec-if="Model.oppdrag.type.Contains(&quot;tleie&quot;)">Utleier</span>
          </div>
        </td>
        <td style="padding:0.5cm; text-align:center">
          <span style="font-size:8pt">side [[p]] av [[P]]</span>
        </td>
        <td style="font-size:8pt; padding:0.25cm 1cm 0.5cm 0.5cm; text-align:right; vertical-align:bottom">
          <div style="border-top:solid 1px #000000; float:right; text-align:center; width:3cm">
            <span vitec-if="!Model.oppdrag.type.Contains(&quot;tleie&quot;)">Kjøper</span>
            <span vitec-if="Model.oppdrag.type.Contains(&quot;tleie&quot;)">Leietaker</span>
          </div>
        </td>
      </tr>
    </tbody>
  </table>
</div>
```

Note: `.Contains("tleie")` uses string matching (substring of "Utleie"), and `!` for negation (not `== false`).

#### Footer: Vitec Bunntekst Oppdragsavtale (signature lines + office info)

Taller footer (`height: 2.4cm`) with nested table for signature lines. Uses `#bunntekstTabell` custom ID:

```html
<div id="vitecTemplate">
  <span vitec-template="resource:Vitec Stilark">&nbsp;</span>
  <style type="text/css">
    #bunntekstTabell { width: 21cm; table-layout: fixed; height: 2.4cm; ... }
    #bunntekstTabell tr > td { vertical-align: top; padding: 0px 8px; font-size: 9pt; }
  </style>
  <table id="bunntekstTabell">
    <tbody>
      <tr>
        <td colspan="49" style="padding-left:1cm">
          [[meglerkontor.navn]]<br/>
          [[meglerkontor.adresse]], ...
        </td>
        <td colspan="2">&nbsp;</td>
        <td colspan="49" style="padding-right:1cm">
          <table style="width:100%"><!-- nested: signature lines --></table>
        </td>
      </tr>
    </tbody>
  </table>
</div>
```

Signature line labels: **Oppdragsgiver** (left) / **Oppdragstaker** (right), with `border-bottom: 1px solid black` above each.

#### Footer: Legal document footers (Skjøte, Sikring) — self-contained CSS

These footers place `<style>` blocks **OUTSIDE** the `#vitecTemplate` div, load their own fonts, and do NOT reference the Stilark:

```html
<style type="text/css">
  @import url('https://fonts.googleapis.com/css2?family=Open+Sans:wght@300;400;700&display=swap');
  html, body { margin: 0; padding: 0; }
  #vitecTemplate * { font-variant-ligatures: none; }
  #vitecTemplate table { width: 100%; height: 1.5cm; font-family: 'Open sans', sans-serif; font-size: 8pt; ... }
  #vitecTemplate td[data-label] { padding: 16px 2px 4px 3px; position: relative; }
  #vitecTemplate td[data-label]:before { content: attr(data-label); font-size: 7pt; ... }
  #vitecTemplate td.no-border { border: none; }
  #vitecTemplate [contenteditable="false"] * { user-select: none; }
</style>
<div id="vitecTemplate" style="padding-left:0.5cm; padding-right:0.5cm">
  <table>
    <tbody>
      <tr>
        <td colspan="25" data-label="Dato">&nbsp;</td>
        <td colspan="75" data-label="Utstederens underskrift">&nbsp;</td>
      </tr>
      <tr contenteditable="false">
        <td class="no-border" colspan="20"><small>GA-5400 B</small></td>
        <td class="no-border" colspan="60" style="text-align:center"><small>Skjøte</small></td>
        <td class="no-border" colspan="20" style="text-align:right"><small>Side [[p]] av [[P]]</small></td>
      </tr>
    </tbody>
  </table>
</div>
```

Key differences from other footers:
- `@import url()` loads Google Fonts (Open Sans) directly
- `font-variant-ligatures: none` prevents rendering issues
- `user-select: none` on `contenteditable="false"` descendants
- All cells have `border: solid 1px #000` by default; `.no-border` removes it
- `data-label` provides floating field labels via CSS `::before`

| Document | Form number | Label | Padding |
|----------|------------|-------|---------|
| Skjøte | GA-5400 B | "Utstederens underskrift" | `0.5cm` |
| Pantedokument (Sikring) | Statens kartverk - rev 01/19 | "Pantsetters underskrift" | `1cm` |

Sikring footer also has conditional document type text:
```html
<small>Pantedokument - Panterett i
  <span vitec-if="Model.eiendom.eieform != &quot;Andel&quot;">fast eiendom</span>
  <span vitec-if="Model.eiendom.eieform == &quot;Andel&quot;">andel i borettslag</span>
</small>
```

#### Footer height reference

| Footer template | Height | Width |
|----------------|--------|-------|
| Vitec Bunntekst (Standard) | implicit | 21cm |
| Vitec Bunntekst Kontrakt | 1.5cm | 20cm |
| Vitec Bunntekst Fremleiekontrakt | 1.5cm | 20cm |
| Vitec Bunntekst Sidetall | 1.5cm | 100% |
| Vitec Bunntekst Skjøte | implicit (via CSS) | 100% |
| Vitec Bunntekst Sikring | implicit (via CSS) | 100% |
| Vitec Bunntekst Oppdragsavtale | 2.4cm | 21cm |
| Custom footers with `#bunntekstTabell` | 1.4cm | 21cm |

#### Page numbering in headers/footers

| Merge field | Output | Example |
|-------------|--------|---------|
| `[[p]]` | Current page number | `side 1 av 5` |
| `[[P]]` | Total page count | `side 1 av 5` |

Common patterns:
- `[[p]] av [[P]]` — simple page counter
- `side [[p]] av [[P]]` — with Norwegian label (lowercase)
- `Side [[p]] av [[P]]` — capitalized (legal documents)

#### Signature and sender resource templates

In addition to headers/footers, Vitec Next has **signature** and **sender** system templates:

**SMS-signatur** — plain `<div>` elements, no styling:
```html
<div>&nbsp;</div>
<div>Vennlig hilsen</div>
<div>[[avsender.navn]]</div>
<div>&nbsp;</div>
<div>[[avsender.tittel]]</div>
<div>[[avsender.meglerkontor.markedsforingsnavn]]</div>
```

Note: SMS uses `[[avsender.meglerkontor.markedsforingsnavn]]` (marketing name), not `[[avsender.meglerkontor.navn]]` (legal name).

**E-post signatur** — Calibri font at 11pt, `<span>` with inline styles:
```html
<div>
  <span style="font-family:calibri,sans-serif; font-size:11pt">Med vennlig hilsen</span><br/>
  <span style="font-family:calibri,sans-serif; font-size:11pt">[[avsender.navn]]</span><br/>
  ...
  <span style="font-family:calibri,sans-serif; font-size:11pt">Mobil: [[avsender.mobiltlf]], e-post: [[avsender.epost]]</span><br/>
  <span style="font-family:calibri,sans-serif; font-size:11pt">Besøksadresse: [[avsender.meglerkontor.besoksadresse]], ...</span>
</div>
```

**Avsender (resource template)** — A dual-output template with conditional rendering for PDF vs email, referenced by document templates via `<span vitec-template="resource:Avsender">`:

```html
<!-- PDF output: table layout with page-break-inside:avoid -->
<table id="Avsender" style="page-break-inside:avoid; width:100%"
       vitec-if="Model.dokumentoutput == &quot;pdf&quot;">
  <tbody>
    <tr><td><br/><br/><strong>Med vennlig hilsen</strong></td></tr>
    <tr><td>[[avsender.meglerkontor.markedsforingsnavn]]</td></tr>
    <tr><td>&nbsp;</td></tr>
    <tr><td>[[avsender.navn]]</td></tr>
    <tr><td>[[avsender.tittel]]</td></tr>
    <tr><td>Mobil: [[avsender.mobiltlf]]</td></tr>
    <tr><td>E-post: [[avsender.epost]]</td></tr>
  </tbody>
</table>

<!-- Email output: div layout with Calibri font -->
<div style="font-family:calibri,sans-serif; font-size:11pt"
     vitec-if="Model.dokumentoutput == &quot;email&quot;">
  <span style="...">Med vennlig hilsen</span><br/>
  <span style="...">[[avsender.navn]]</span><br/>
  ...
</div>
```

Key patterns in the Avsender template:
- **Dual output:** `Model.dokumentoutput == "pdf"` vs `"email"` determines which block renders
- **PDF uses table** with `#Avsender` custom ID; **email uses div/span** with inline Calibri font
- **CSS scoping:** `#Avsender td { padding-left: 0; }` resets padding for the sender table
- **PDF gets `page-break-inside:avoid`** to keep the sender block together
- **Company name order differs:** PDF shows company name first, then person; email shows person first, then company

**Mottaker (resource template)** — Provides the recipient address block for letter-style documents. PDF-only (email handles recipients differently). Referenced via `<span vitec-template="resource:Mottaker">`:

```html
<!-- CSS -->
<style type="text/css">
#Mottaker td { padding-left: 0; }
</style>

<!-- PDF output only -->
<table id="Mottaker" style="table-layout:fixed; width:100%"
       vitec-if="Model.dokumentoutput == &quot;pdf&quot;">
  <tbody>
    <tr>
      <td colspan="100" style="height:1.25cm">&nbsp;</td>  <!-- top spacer -->
    </tr>
    <tr>
      <td colspan="67" style="vertical-align:top">
        <div><strong>[[mottaker.navn]]</strong></div>
        <div>&nbsp;</div>
        <div>[[mottaker.adresse]]</div>
        <div>[[mottaker.postnr]] [[mottaker.poststed]]</div>
      </td>
      <td colspan="33" style="vertical-align:top">
        <div>&nbsp;</div>
        <div>&nbsp;</div>
        <div style="text-align:right">Vår ref: [[oppdrag.nr]]</div>
        <div style="text-align:right">[[avsender.meglerkontor.poststed]], [[dagensdato]]</div>
      </td>
    </tr>
    <tr>
      <td colspan="100" style="height:2cm">&nbsp;</td>  <!-- bottom spacer -->
    </tr>
  </tbody>
</table>

<p>&nbsp;</p>  <!-- email fallback: empty paragraph -->
```

Key patterns in the Mottaker template:
- **PDF-only table:** `vitec-if="Model.dokumentoutput == &quot;pdf&quot;"` — email output gets just `<p>&nbsp;</p>`
- **Letter layout:** 67/33 colspan ratio — recipient address (left, bold name), reference info (right, right-aligned)
- **Spacer rows:** `height:1.25cm` top, `height:2cm` bottom — creates standard Norwegian letter spacing
- **Custom ID:** `#Mottaker` with `padding-left: 0` (same pattern as `#Avsender`)
- **HTML comments:** `<!-- IF-OUTPUT: PDF -->` / `<!-- /IF-OUTPUT: PDF -->` are documentation-only annotations; the actual conditional is the `vitec-if`
- **Cross-template merge fields:** Uses both `[[mottaker.*]]` (recipient) and `[[avsender.*]]` (sender office city) in the same template
- **`[[dagensdato]]`** — Today's date, rendered at generation time

**Mottaker merge fields:**

| Field | Description |
|-------|-------------|
| `[[mottaker.navn]]` | Recipient name (bold) |
| `[[mottaker.adresse]]` | Recipient street address |
| `[[mottaker.postnr]]` | Recipient postal code |
| `[[mottaker.poststed]]` | Recipient postal city |
| `[[oppdrag.nr]]` | Assignment/case number ("Vår ref:") |
| `[[dagensdato]]` | Today's date |

#### Summary: Resource template pattern

Avsender and Mottaker follow the same architectural pattern:

| Aspect | Avsender | Mottaker |
|--------|----------|----------|
| Purpose | Sender signature block | Recipient address block |
| Custom ID | `#Avsender` | `#Mottaker` |
| PDF output | Table with `page-break-inside:avoid` | Table with spacer rows (1.25cm + 2cm) |
| Email output | Div with Calibri font | Empty `<p>&nbsp;</p>` |
| CSS | `#Avsender td { padding-left: 0; }` | `#Mottaker td { padding-left: 0; }` |
| colspan | Single column (100) | Two columns (67/33) |
| Position in document | End (after body) | Start (before body) |

Templates reference these via:
```html
<span vitec-template="resource:Mottaker">&nbsp;</span>
<!-- document body content -->
<span vitec-template="resource:Avsender">&nbsp;</span>
```

**(Evidence: Mottaker and Avsender system template source code, provided by Proaktiv admin)**

#### Key design rules for headers/footers

1. **Height:** Footers range from 1.4cm to 2.4cm depending on content. Standard is 1.5cm. Oppdragsavtale uses 2.4cm for signature lines.
2. **Width:** Headers use `21cm` (full A4). Footers use `20cm` or `21cm` depending on whether padding is on the wrapper or table. Self-contained footers use `100%`.
3. **Font:** Stilark-based footers use `<small>` (~8pt). Self-contained footers explicitly set `font-family: 'Open sans', sans-serif` at `8pt`.
4. **Stilark inclusion varies:** Stilark-based footers include `<span vitec-template="resource:Vitec Stilark">`. Self-contained footers (Skjøte, Sikring, Sidetall) do NOT — they carry all their CSS inline.
5. **All use `#vitecTemplate`:** Every header/footer uses `id="vitecTemplate"` for consistent CSS scoping.
6. **CSS placement varies:** Stilark-based footers may add `<style>` inside the div. Self-contained footers place `<style>` outside and before the div.
7. **Custom IDs for scoping:** Some footers use `#bunntekstTabell` or `#Avsender` for template-specific CSS rules without conflicting with `#vitecTemplate` styles.

**(Evidence: complete source code for all 9 system header/footer templates + Avsender resource + SMS/email signatures, provided by Proaktiv admin)**

### Letter template architecture (Grunnlag brevmal)

Vitec provides 5 foundation letter templates ("Grunnlag brevmal") that define the standard structure for letter-type documents. All follow a **3-section table layout**: Mottaker → Content body → Avsender.

```html
<div id="vitecTemplate"><span vitec-template="resource:Vitec Stilark">&nbsp;</span>
<style type="text/css">
    /* Insert-field CSS (shared across all letter templates) */
    span.insert:empty {
        font-size: inherit !important;
        line-height: inherit !important;
        display: inline-block;
        background-color: lightpink;
        min-width: 2em !important;
        height: .7em !important;
        text-align: center;
    }
    span.insert:empty:before { content: attr(data-label); }
    span.insert:empty:hover { background-color: #fff; cursor: pointer; }
    .insert-table { display: inline-table; }
    .insert-table>span, .insert-table>span.insert { display: table-cell; }
    #vitecTemplate table { width: 100%; table-layout: fixed; }
</style>
<table>
  <tbody>
    <tr><td><div vitec-template="resource: Mottaker">&nbsp;</div></td></tr>
    <tr><td>
      <p><strong>Vedr. eiendommen [[eiendom.gatenavnognr]] - [[komplettmatrikkelutvidet]]
        i [[eiendom.kommunenavn]] kommune</strong></p>
      <!-- Letter body content here -->
    </td></tr>
    <tr><td><div vitec-template="resource: Avsender">&nbsp;</div></td></tr>
  </tbody>
</table>
</div>
```

#### The 5 letter template variants

| Template | Party tables | Content focus |
|----------|-------------|---------------|
| **Grunnlag brevmal generell** | None | Simplest — subject line, body text, insert field |
| **Grunnlag brevmal selger** | Seller (detailed + compact) | Letters addressed regarding the seller |
| **Grunnlag brevmal kjøper** | Buyer (detailed + compact) | Letters addressed regarding the buyer |
| **Grunnlag brevmal selger og kjøper** | Both seller + buyer (detailed + compact) | Full party listing with "Overdras fra:" / "til:" framing |
| **Grunnlag brevmal tabell** | None | Adds user-customizable data table with inline editing instructions |

#### Party listing table pattern (detailed variant)

The seller/buyer letter templates include a two-row-per-party table with address and contact info:

```html
<table style="table-layout:fixed; width:100%" vitec-if="Model.selgere.Count &gt; 0">
  <thead>
    <tr>
      <th colspan="37"><strong>Selger<span vitec-if="Model.selgere.Count &gt; 1">e</span></strong></th>
      <th colspan="45"><strong>Adresse/Kontaktinfo</strong></th>
      <th colspan="18">[[selger.ledetekst_fdato_orgnr]]</th>
    </tr>
  </thead>
  <tbody vitec-foreach="selger in Model.selgere">
    <tr>
      <td colspan="37" rowspan="2">[[*selger.navn]]</td>
      <td colspan="45">[[*selger.gatenavnognr]], [[*selger.postnr]] [[*selger.poststed]]</td>
      <td colspan="18">[[*selger.fdato_orgnr]]</td>
    </tr>
    <tr>
      <td colspan="63">
        <span vitec-if="selger.tlf != &quot;&quot;">Tlf: [[*selger.tlf]]</span>
        <span vitec-if="(selger.tlf != &quot;&quot; &amp;&amp; selger.emailadresse != &quot;&quot;)"> / </span>
        <span vitec-if="selger.emailadresse != &quot;&quot;">E-post: [[*selger.emailadresse]]</span>
      </td>
    </tr>
  </tbody>
</table>
```

Key patterns:
- **Dynamic pluralization** — `Selger` + `<span vitec-if="Model.selgere.Count > 1">e</span>` adds the plural suffix conditionally
- **`ledetekst_fdato_orgnr`** — Dynamic column header that adapts label based on whether the party is a person ("Fødselsdato") or organization ("Org.nr.")
- **`fdato_orgnr`** — Combined value field for birth date or org number
- **`rowspan="2"`** — Name cell spans both the address row and the contact info row
- **Conditional separator** — Phone / email separated by " / " only when both exist, using compound `&amp;&amp;` condition
- **37/45/18 colspan ratio** — Standard column widths: Name (37%), Address (45%), ID (18%)

#### Party listing table pattern (compact variant)

A simpler single-row-per-party table is also included for signature/reference sections:

```html
<table vitec-if="Model.selgere.Count &gt; 0">
  <tbody vitec-foreach="selger in Model.selgere">
    <tr>
      <td colspan="37">[[*selger.navn]]</td>
      <td colspan="15" style="align:right">[[*selger.ledetekst_fdato_orgnr]]</td>
      <td colspan="48">[[*selger.fdato_orgnr]]</td>
    </tr>
  </tbody>
</table>
```

#### "Mangler data" sentinel value

Some merge fields return the string `"Mangler data"` (Norwegian for "Missing data") instead of an empty string when data is unavailable. The letter templates demonstrate **inconsistent checking** across variants:

- **Grunnlag brevmal selger** and **kjøper** check `selger.tlf != "Mangler data"` (sentinel check)
- **Grunnlag brevmal selger og kjøper** checks `selger.tlf != ""` (empty string check)

Both approaches work, but **best practice is to check for both** when the field may return either value:

```html
<span vitec-if='!(Model.field == "Mangler data" || Model.field == "")'>
  [[field.value]]
</span>
```

This dual-check pattern is confirmed in production templates like the Visningsbekreftelse. **(DB evidence: "Visningsbekreftelse")**

#### Resource reference syntax: space after colon

The letter templates use `resource: Mottaker` (with a space after the colon) while the Stilark reference uses `resource:Vitec Stilark` (without space before the name). Both syntaxes work — the Vitec rendering engine trims whitespace in resource names.

#### Table variant: inline editing instructions

The "Grunnlag brevmal tabell" includes instructional text teaching users how to:
- Add rows using the Tab key
- Add columns via right-click → "Kolonne" → "Sett inn ny kolonne"
- Adjust column widths by editing `colspan` values in source (must sum to 100)

This embedded inner table uses `border="1"` (visible borders) unlike the outer letter structure table (borderless). The table variant also adds `#vitecTemplate strong { font-size: unset; }` to prevent the Stilark's `10pt` override on bold text.

**(Evidence: Grunnlag brevmal generell, selger, kjøper, selger og kjøper, and tabell system template source code from Vitec Next production, 2026-02-21)**

### Minimal complete template

```html
<div class="proaktiv-theme" id="vitecTemplate">
  <span vitec-template="resource:Vitec Stilark">&nbsp;</span>
  <table style="width:21cm; table-layout:fixed">
    <tbody>
      <tr>
        <td style="padding:0 1cm">
          <p>Template content goes here.</p>
        </td>
      </tr>
    </tbody>
  </table>
</div>
```

### Templates with custom `<style>` blocks

Many templates include one or more `<style>` blocks inside `#vitecTemplate` in addition to the Stilark resource reference. This is confirmed safe and extremely common — complex templates like Kjøpekontrakt FORBRUKER (71K), Skjøte (43K), and Oppdragsavtale (42K) all include multiple `<style>` blocks for template-specific CSS rules (CSS counters, form styling, checkbox toggles, etc.). **(DB evidence: all complex templates)**

### Contract document structure

Contracts (Kjøpekontrakt, Oppdragsavtale) use a specific structural pattern with `<article>` elements and CSS counters for auto-numbered sections.

**⚠️ IMPORTANT: Chromium CSS counter fix** — The default Vitec system template uses `counters(item, ".")` with a single counter, which **breaks in Chromium-based PDF renderers** due to unreliable counter scope inheritance. The production-ready fix uses two explicit counters:

```html
<div class="proaktiv-theme" id="vitecTemplate">
  <span vitec-template="resource:Vitec Stilark">&nbsp;</span>
  <style type="text/css">
    /* Chromium-safe: two explicit counters instead of counters() */
    #vitecTemplate { counter-reset: section; }

    /* Top-level sections only */
    #vitecTemplate article.item:not(article.item article.item) {
        counter-increment: section;
        counter-reset: subsection;
    }

    /* Sub-sections only */
    #vitecTemplate article.item article.item {
        counter-increment: subsection;
    }

    /* h2: "1. ", "2. ", ... "10. " — fixed-width prevents double-digit misalignment */
    #vitecTemplate article.item:not(article.item article.item) h2::before {
        content: counter(section) ". ";
        display: inline-block;
        width: 26px;
    }

    /* h3: "1.1. ", "1.2. ", "2.1. " */
    #vitecTemplate article.item article.item h3::before {
        content: counter(section) "." counter(subsection) ". ";
        display: inline-block;
        width: 36px;
    }

    #vitecTemplate .avoid-page-break { page-break-inside: avoid; }
    /* padding must match h2 negative margin (26px) for heading/body alignment */
    #vitecTemplate article { padding-left: 26px; }
    #vitecTemplate article article { padding-left: 0; }
  </style>
  <h1>Contract Title</h1>
  <article class="item">
    <h2>Section heading (auto-numbered: "1. ")</h2>
    <!-- section content -->
    <article class="item">
      <h3>Sub-section (auto-numbered: "1.1. ")</h3>
    </article>
  </article>
</div>
```

**Why two counters?** The default Vitec template uses:
```css
/* DEFAULT (broken in Chromium) */
#vitecTemplate .item { counter-increment: item; }
#vitecTemplate .item > .item { counter-reset: item; }
#vitecTemplate .item ~ .item { counter-reset: none; }
#vitecTemplate .item h2:before,
#vitecTemplate .item h3:before { content: counters(item, ".") ". "; }
```
The `counters()` function relies on CSS counter scope inheritance, which Chromium's PDF renderer handles incorrectly — subsections get wrong numbers or reset at unexpected points. The fix with explicit `section`/`subsection` counters and `:not()` selectors is deterministic and works across all renderers.

**(DB evidence: "Kjøpekontrakt FORBRUKER", "Kjøpekontrakt AS-IS", "Oppdragsavtale"; Chromium fix: custom Proaktiv production template)**

### Internal bookmark anchors

Contract templates use anchor elements for internal document navigation:

```html
<!-- Anchor target (empty <a> with id) -->
<article class="item"><a id="tinglysing-notifisering-og-sikkerhet"></a>
  <h2>Tinglysing og sikkerhet</h2>
  ...
</article>

<!-- Bookmark link -->
<a class="bookmark" href="#tinglysing-notifisering-og-sikkerhet">
  Tinglysing og Sikkerhet
</a>
```

CSS for bookmark links:
```css
#vitecTemplate a.bookmark {
    color: #000;
    font-style: italic;
    text-decoration: none;
}
```

**(Evidence: custom Kjøpekontrakt FORBRUKER template)**

### `@functions` blocks — Custom C# method definitions (support template pattern)

When a template requires custom business logic beyond what `vitec-if`, `vitec-foreach`, and merge fields can express, Vitec supports Razor `@functions` blocks that define C# helper methods. This is considered a **non-standard practice** — most templates do not use it.

**Architecture:** The `@functions` code is placed in a **separate system template file** that serves as a support/reference resource. The main template (e.g. Kjøpekontrakt) references this support template, making the defined methods available for use. This separation keeps the main template clean and the custom logic isolated.

The support template content is wrapped in an HTML comment inside a `<p>` tag to prevent visual rendering:

```html
<p><!-- @functions {
private string GetPosteringsVerdiForBoligkjoperforsikring()
{
    var codeList = new List<string>(){"10098"};
    return GetPosteringsVerdi(codeList);
}

private List<Vitec.Megler.DocumentMerging.DocumentFullModelPool.ModelPost>
    GetPosteringerUtenBoligkjoperforsikring()
{
    var codeList = new List<string>(){"10098"};
    return GetPosteringerExcept(codeList);
}

private List<...> GetPosteringerExcept(List<string> codeList)
{
    return @Model.kjoperskostnader.alleposter
        .Where(x => !codeList.Contains(x.kode)).ToList();
}

private string GetPosteringsVerdi(List<string> codeList)
{
    var post = @Model.kjoperskostnader.alleposter
        .FirstOrDefault(x => codeList.Contains(x.kode));
    return post != null ? post.belop : "0";
}
}--></p>
```

This reveals:
- **Support template pattern** — A separate system template file created specifically to hold `@functions` code, referenced by the main template
- **`Vitec.Megler.DocumentMerging.DocumentFullModelPool.ModelPost`** — full C# type path for template model posts
- **`.FirstOrDefault()`** — LINQ method returning first match or null
- **`.ToList()`** — LINQ method materializing a query
- **`!codeList.Contains(x.kode)`** — negated Contains in Where lambda
- Custom methods can filter by business code lists (e.g. code `"10098"` for boligkjøperforsikring) and return computed values
- The methods separate boligkjøperforsikring from other buyer costs, allowing the template to render them in different table sections

**When to use this pattern:** Only when standard vitec-if/vitec-foreach cannot express the required logic — e.g. filtering a collection by a code list and extracting a specific value, or splitting one collection into two subsets for separate rendering.

#### Calling custom methods from the main template

Once methods are defined in a support template, the main template calls them using the `@MethodName()` syntax (Razor method invocation). Three usage contexts are observed:

**1. In `vitec-foreach` — replacing `Model.collection` with a method call:**
```html
<!-- DEFAULT: iterates ALL buyer costs -->
<tbody vitec-foreach="kostnad in Model.kjoperskostnader.alleposter">

<!-- CUSTOM: iterates only costs EXCLUDING boligkjøperforsikring -->
<tbody vitec-foreach="kostnad in GetPosteringerUtenBoligkjoperforsikring()">
```
Note: Custom method calls in `vitec-foreach` do NOT use the `@` prefix — the method name is used directly.

**2. In `$.CALC()` — arithmetic with mixed merge fields and method calls:**
```html
<strong>$.CALC(UD:[[kontrakt.kjopesumogomkostn]]-@GetPosteringsVerdiForBoligkjoperforsikring())</strong>
```
This subtracts the boligkjøperforsikring amount from the total, then formats the result with `UD:` (tusenskilletegn). The `@` prefix IS required when calling methods inside `$.CALC()` and `$.UD()`.

**3. In `vitec-if` — conditional rendering based on method return value:**
```html
<span vitec-if="@GetPosteringsVerdiForBoligkjoperforsikring()!=&quot;0&quot;">
    $.UD(@GetPosteringsVerdiForBoligkjoperforsikring())
</span>
<strong vitec-if="@GetPosteringsVerdiForBoligkjoperforsikring()==&quot;0&quot;">
    <span class="insert-table"><span class="insert" data-label="beløp"></span></span>
</strong>
```
If the method returns a non-"0" value (cost exists in the data), it displays the formatted amount. If it returns "0" (no cost found), it shows an editable placeholder field for manual entry.

**4. In `$.UD()` — formatting a method return value:**
```html
$.UD(@GetPosteringsVerdiForBoligkjoperforsikring())
```

**Summary of `@` prefix rules:**
| Context | Prefix | Example |
|---------|--------|---------|
| `vitec-foreach` collection | No `@` | `kostnad in GetPosteringerUtenBoligkjoperforsikring()` |
| `vitec-if` expression | `@` required | `@GetPosteringsVerdiForBoligkjoperforsikring()!=&quot;0&quot;` |
| `$.CALC()` expression | `@` required | `$.CALC(UD:[[field]]-@MethodName())` |
| `$.UD()` argument | `@` required | `$.UD(@MethodName())` |
| Inline text output | `@` required | `@MethodName()` |

**Business context:** The custom Proaktiv Kjøpekontrakt splits `Model.kjoperskostnader.alleposter` into two groups:
1. All costs **except** boligkjøperforsikring (code `10098`) → displayed in the main cost table
2. The boligkjøperforsikring cost alone → displayed separately below, conditionally shown only for non-company buyers (`Model.kjoper.erfirma == false`)

The default system template shows ALL costs in one table and uses manual `span.insert` placeholders for the boligkjøperforsikring amount, requiring the user to type the value by hand.

**(Evidence: custom Proaktiv Kjøpekontrakt Bruktbolig — support template + main template integration)**

### Legal document numbered list structure

Legal documents use a `nummerert-liste` pattern for auto-numbered paragraphs:

```html
<style type="text/css">
  #vitecTemplate .nummerert-liste:before {
    font-weight: 700;
    counter-increment: main-counter;
    content: counter(main-counter) ". ";
  }
  #vitecTemplate { counter-reset: main-counter; }
</style>
<table>
  <tbody>
    <tr class="border-bottom">
      <td colspan="4"><div class="nummerert-liste"> </div></td>
      <td colspan="96"><strong>Section title text</strong></td>
    </tr>
  </tbody>
</table>
```

**(DB evidence: "Forslag til fordelingskjennelse (Tvangssalg)")**

---
