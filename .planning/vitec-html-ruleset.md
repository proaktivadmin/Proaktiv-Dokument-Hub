# Vitec HTML Ruleset

> **Source of truth for Vitec Next template HTML patterns.**
> Produced by Documentation Agent (Phase 11, Agent 1).
> All rules are evidence-based, derived from `docs/Alle-flettekoder-25.9.md` (6,494 lines of production HTML), `.cursor/vitec-reference.md`, and **133 Vitec Next tagged database templates** (queried via PostgreSQL MCP).
> Patterns marked **(DB evidence: "Template Title")** were discovered from database template analysis.

---

> **CRITICAL WARNING — NO-TOUCH KARTVERKET & GOVERNMENT TEMPLATES**
>
> Several templates in this system are **legally regulated government forms** (Kartverket, Landbruksdirektoratet, Kommunal- og moderniseringsdepartementet) used for property registration (tinglysing), concession declarations, and sectioning applications. These templates **MUST NEVER be modified, edited, or altered in any way.**
>
> **Additionally:** These protected templates were converted to work within Vitec Next but are **NOT built according to Vitec Next best practices.** They contain workarounds and patterns that should **NOT be used as reference** when developing or updating regular templates. The rules in Sections 1–12 of this document define best practices — the Kartverket forms in Section 14 are archival documentation only.
>
> **See Section 14 for the complete list of no-touch templates and rules.**

---

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

    /* h2: "1. ", "2. ", "3. " */
    #vitecTemplate article.item:not(article.item article.item) h2::before {
        content: counter(section) ". ";
    }

    /* h3: "1.1. ", "1.2. ", "2.1. " */
    #vitecTemplate article.item article.item h3::before {
        content: counter(section) "." counter(subsection) ". ";
    }

    #vitecTemplate .avoid-page-break { page-break-inside: avoid; }
    #vitecTemplate article { padding-left: 20px; }
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

## 2. CKEditor 4 Compatibility Rules

Vitec Next uses CKEditor 4 as its template editor. CKEditor 4's Advanced Content Filter (ACF) strips or rewrites HTML it considers invalid unless the Vitec installation has configured `extraAllowedContent` rules.

### How ACF works

By default, CKEditor 4 only allows HTML elements and attributes that are registered by loaded plugins. Non-standard attributes are stripped. Vitec Next must configure CKEditor's ACF to allow its custom attributes — and the evidence from production templates confirms that it does.

### Confirmed safe elements

These elements appear in production templates and survive CKEditor editing:

| Element | Status | Evidence |
|---------|--------|----------|
| `<div>` | **Safe** | Used as root wrapper and structural containers throughout |
| `<p>` | **Safe** | Standard text paragraphs |
| `<span>` | **Safe** | Used extensively for conditional content and styling |
| `<table>`, `<tbody>`, `<thead>`, `<tfoot>`, `<tr>`, `<th>`, `<td>` | **Safe** | Primary layout mechanism in all templates |
| `<strong>`, `<em>` | **Safe** | Inline formatting |
| `<small>` | **Safe** | Used for reduced-size annotations and footer text |
| `<br>` | **Safe** | Line breaks |
| `<ul>`, `<ol>`, `<li>` | **Safe** | List structures; `<ul>` used with `vitec-foreach` (line 1961) |
| `<img>` | **Safe** | Images with `src`, `alt`, `style`, `class` attributes |
| `<figure>`, `<figcaption>` | **Safe** | Image containers with captions (lines 6241–6292) |
| `<a>` | **Safe** | Hyperlinks and internal bookmark anchors; `<a id="section-name"></a>` for targets, `<a class="bookmark" href="#section-name">` for links (Evidence: Kjøpekontrakt FORBRUKER) |
| `<u>` | **Safe** | Underline text within contract clauses (Evidence: Kjøpekontrakt FORBRUKER) |
| `<h1>`–`<h5>` | **Safe** | Headings; `<h1>`, `<h2>`, `<h3>` used extensively. `<h2>` confirmed in contract templates (DB evidence: "Kjøpekontrakt FORBRUKER", "Oppdragsavtale") |
| `<article>` | **Safe** | Structural container for numbered sections in contracts. Used with `class="item"` for CSS counter auto-numbering. (DB evidence: "Kjøpekontrakt FORBRUKER", "Kjøpekontrakt AS-IS", "Oppdragsavtale") |
| `<label>` | **Safe** | Used for SVG checkbox/radio toggles (lines 6175–6210) |
| `<input>` | **Safe** | Radio buttons inside label toggles (lines 6179–6207) |
| `<button>` | **Safe** | Version toggle button (line 273) |
| `<code>` | **Safe** | Inline code display (line 6161) |
| `<style>` | **Safe** | Embedded CSS blocks (lines 2–272) |
| `<sup>` | **Safe** | Superscript; `&sup2;` used for m² |

### Confirmed safe custom attributes

These non-standard attributes survive in production templates, proving Vitec's CKEditor configuration allows them:

| Attribute | Used on | Purpose | Evidence |
|-----------|---------|---------|----------|
| `vitec-template` | `<span>` | Resource inclusion (Stilark) | Every template's shell |
| `vitec-if` | `<span>`, `<em>`, `<table>`, `<tbody>`, `<tr>`, `<div>`, `<ul>` | Conditional rendering | 118+ instances in Alle-flettekoder |
| `vitec-foreach` | `<tbody>`, `<table>`, `<ul>`, `<div>` | Iteration/loops | 50+ instances in Alle-flettekoder |
| `data-label` | `<td>`, `<span>` | Floating label via CSS `::before` | 7 instances in Alle-flettekoder (form-table pattern) |
| `data-version` | `<tr>`, `<td>` | Version tagging with visual badge | 100 instances in Alle-flettekoder |
| `data-toggle` | `<tr>`, `<label>`, `<button>` | Bootstrap-style toggle behaviour | Lines 6177, 6175, 273 |
| `data-choice` | `<td>` | Floating choice/selection label below cell content via CSS `::after`. Used in form templates alongside `data-label`. | (DB evidence: 41 templates including "Skjøte", "Akseptbrev kjøper", "Oppgjørsskjema kjøper") |
| `data-target` | `<button>`, `<a>` | Bootstrap collapse/expand target reference | (DB evidence: "Aksjeeierbok (Næring)", "Eierskiftemelding grunneier") |
| `contenteditable` | `<label>`, `<tr>` | Prevents editing of specific elements | Lines 289, 6175–6210 |
| `colspan` | `<td>`, `<th>` | Column spanning in tables | Pervasive |
| `rowspan` | `<td>` | Row spanning in tables | Line 6188 |
| `cellspacing` | `<table>` | Legacy spacing removal (`cellspacing="0"`) | (DB evidence: "Vitec Bunntekst") |

### Elements and patterns CKEditor 4 typically strips (by default)

Without explicit ACF configuration, CKEditor 4 would strip:

| Pattern | Default behaviour | Vitec override |
|---------|-------------------|----------------|
| Custom attributes (`vitec-if`, `vitec-foreach`) | **Stripped** | Vitec configures `extraAllowedContent` to allow these |
| `<input>` elements | **Stripped** unless forms plugin loaded | Allowed in Vitec — used inside `<label>` toggles |
| `<button>` elements | **Stripped** unless explicitly allowed | Allowed — version toggle button |
| `<style>` blocks | **Preserved** if `allowedContent` includes them | Present in production templates |
| `<font>` tags | **May be generated** by CKEditor (legacy) | Should be unwrapped; sanitizer already handles this |
| `<center>` tags | **May be preserved** from legacy content | Should be unwrapped; sanitizer handles this |

### CKEditor 4 capabilities beyond current Vitec usage

Based on CKEditor 4's built-in plugins and ACF system, these capabilities exist but are not observed in Vitec templates:

| Capability | CKEditor 4 support | Current Vitec usage |
|------------|--------------------|--------------------|
| `<blockquote>` | Yes (blockquote plugin) | Not used in any observed template |
| `<pre>` | Yes (format plugin) | Not used |
| `<iframe>` | Yes (iframe plugin, if loaded) | Not used |
| `<video>`, `<audio>` | Via plugins | Not used |
| `<dl>`, `<dt>`, `<dd>` | Yes | Not used |
| `<abbr>` | Via plugin | Not used |
| `<sub>` | Yes (basicstyles plugin) | Not used (only `<sup>` seen) |
| Custom `data-*` attributes | Yes via `extraAllowedContent: '*[data-*]'` | `data-label`, `data-version`, `data-toggle`, `data-choice`, `data-target` observed |
| CSS classes on any element | Yes via ACF | Extensive usage — see Section 7 for full list. 100+ distinct CSS classes observed across 133 database templates. |
| `style` attribute on any element | Yes via ACF | Extensively used for structural inline styles |

### CKEditor rewriting behaviour

CKEditor 4 is known to:

1. **Add `&nbsp;` to empty elements** — Empty `<td>`, `<p>`, `<div>` elements may get `&nbsp;` inserted. This is generally harmless.
2. **Normalize self-closing tags** — `<br />` may become `<br>`, `<img ... />` may become `<img ...>`. Both are valid HTML5.
3. **Reformat whitespace** — Indentation and line breaks in source may be altered. Do not rely on specific whitespace formatting.
4. **Merge adjacent identical inline elements** — Two adjacent `<strong>` tags may be merged into one.
5. **Convert entities** — Some character references may be converted between named and numeric forms.

---

## 3. Vitec-if Conditional Logic

### Basic syntax

```html
<element vitec-if="expression">Content shown when true</element>
```

The `vitec-if` attribute causes the element and its contents to be included in the rendered output only when the expression evaluates to true. When false, the entire element (including children) is removed from the output.

### Expression syntax

All expressions reference the `Model` object, which contains the template data context.

#### Comparison operators

| Operator | Syntax | Example |
|----------|--------|---------|
| Equals | `==` | `Model.eiendom.eieform == &quot;Andel&quot;` |
| Not equals | `!=` | `Model.eiendom.eieform != &quot;Andel&quot;` |
| Greater than | `&gt;` | `Model.oppdrag.antallvisninger &gt; 0` |
| Less than | `&lt;` | (implied, not observed directly) |
| Greater/equal | `&gt;=` | (implied) |
| Less/equal | `&lt;=` | (implied) |

**Critical:** In HTML attributes, `>` must be written as `&gt;` and `<` as `&lt;`. Quotes inside the attribute value must use `&quot;`.

#### String methods

| Method | Syntax | Example |
|--------|--------|---------|
| Contains | `.Contains(&quot;text&quot;)` | `Model.oppdrag.type.Contains(&quot;tleie&quot;)` |
| StartsWith | `.StartsWith(&quot;text&quot;)` | `Model.meglerkontor.internid.StartsWith(&quot;2&quot;)` |
| ToString | `.ToString()` | `kjoper.idnummer.ToString().Length == 11` — converts a numeric field to string for length checking. (DB evidence: "Egenerklæring om konsesjonsfrihet") |
| Remove | `.Remove(start, count)` | `@Model.oppgjorkjoper.saldo.Remove(0,1)` (inline text, not vitec-if) |

#### Collection methods

| Method | Syntax | Example |
|--------|--------|---------|
| Count (property) | `.Count` | `Model.kjopere.Count == 0` |
| Count (method) | `.Count()` | `Model.oppdrag.pantforinnfrielse.Where(x =&gt; ...).Count() == 0` — used after `.Where()` filter chain. (DB evidence: "Forslag til fordelingskjennelse") |
| Any (parameterless) | `.Any()` | `Model.oppdrag.pantforinnfrielse.Any()` — simple existence check. (DB evidence: "Varsel om heving av tvangssalg") |
| Any (filtered) | `.Any(x =&gt; x.prop == &quot;val&quot;)` | `Model.kjoperskostnader.alleposter.Any(x =&gt; x.kode == &quot;PARKERING&quot;) == false` |
| Any (cross-ref) | `.Any(x =&gt; x.prop == Model.other.prop)` | `Model.saksokere.Any(x =&gt; x.firmanavn == Model.mottaker.navn)` — references Model-level data inside lambda. (DB evidence: "Pantedokument (sikring)") |
| Where+Count | `.Where(x =&gt; ...).Count()` | `Model.oppdrag.pantforinnfrielse.Where(x =&gt; x.ertypeutleggsforretning == true &amp;&amp; Model.saksoker.firmanavn != x.navn).Count() == 0` (DB evidence: "Forslag til fordelingskjennelse") |
| FirstOrDefault | `.FirstOrDefault(x =&gt; ...)` | Returns first matching item or null. Used in `@functions` blocks: `@Model.kjoperskostnader.alleposter.FirstOrDefault(x => codeList.Contains(x.kode))` (Evidence: custom Kjøpekontrakt FORBRUKER) |
| ToList | `.ToList()` | Materializes a LINQ query. Used in `@functions` blocks: `.Where(x => !codeList.Contains(x.kode)).ToList()` (Evidence: custom Kjøpekontrakt FORBRUKER) |
| Contains (negated) | `!list.Contains(x.prop)` | Used inside `.Where()` lambda to exclude items: `.Where(x => !codeList.Contains(x.kode))` (Evidence: custom Kjøpekontrakt FORBRUKER) |

#### Boolean values

Explicit comparison:
```html
<span vitec-if="Model.megler2.erstudent == true">Ja</span>
<span vitec-if="Model.megler2.erstudent == false">Nei</span>
```

Implicit boolean (without `== true`):
```html
<span vitec-if="selger.ergift">Gift</span>
```

**(DB evidence: "Hjemmelserklæring")** — The implicit form (without `== true`) is valid and used in production templates.

#### Empty string comparison

```html
<span vitec-if='post.debet != ""'>[[*post.debet]]</span>
```

Checking whether a field has a value by comparing to empty string `""`. **(DB evidence: "Oppgjørsoppstilling Selger")**

#### Dynamic pluralization pattern

Conditionally append a plural suffix when a collection has more than one item:

```html
<strong>Selger<span vitec-if="Model.selgere.Count &gt; 1">e</span></strong>
```

Renders "Selger" for a single seller, "Selgere" for multiple. Used in the Grunnlag brevmal letter templates for party listing table headers. **(Evidence: Grunnlag brevmal selger, kjøper, selger og kjøper)**

#### "Mangler data" sentinel value

Some merge fields return the string `"Mangler data"` instead of an empty string when data is unavailable. Best practice is to check for both:

```html
<span vitec-if='!(Model.field == "Mangler data" || Model.field == "")'>
  [[field.value]]
</span>
```

Known fields that return "Mangler data": `selger.tlf`, `kjoper.tlf`, `esignering.melding`, `mottaker.visning.dato`, `grunneier.navn`, `hjemmelshaver.navn`. **(Evidence: Grunnlag brevmal selger/kjøper, "E-signeringsforespørsel SMS", "Visningsbekreftelse", Skjøte)**

#### Logical operators

**AND (`&&`)** — HTML-escaped as `&amp;&amp;`:
```html
<span vitec-if="Model.pant.ertypelegalpant == false &amp;&amp; (Model.saksokere.Any(x =&gt; x.firmanavn != Model.mottaker.navn))">
```
**(DB evidence: "Pantedokument (sikring)")**

**OR (`||`)** — Used in compound conditions:
```html
<p vitec-if='!(Model.esignering.melding == "Mangler data" || Model.esignering.melding == "")'>
  [[esignering.melding]]
</p>
```
**(DB evidence: "E-signeringsforespørsel SMS")**

**Note:** `&&` must be HTML-escaped as `&amp;&amp;` when used inside HTML attributes. `||` appears to work unescaped in single-quoted attribute values.

#### Negation

Prefix `!` negates the entire expression:

```html
<span vitec-if="!Model.oppdrag.type.Contains(&quot;tleie&quot;)">Selger</span>
```

`!()` wrapping negates a compound expression:
```html
<p vitec-if='!(Model.esignering.melding == "Mangler data" || Model.esignering.melding == "")'>
```
**(DB evidence: "E-signeringsforespørsel SMS", "E-signeringspåminnelse SMS")**

### Safe container elements for vitec-if

Confirmed safe from production templates:

| Element | Example | Evidence |
|---------|---------|----------|
| `<span>` | `<span vitec-if="...">text</span>` | Most common; lines 952, 1649, 2332, 6306, 6408 |
| `<em>` | `<em vitec-if="...">Ingen registrert</em>` | Lines 499, 1121, 1819 |
| `<table>` | `<table vitec-if="Model.x.Count &gt; 0">` | Lines 500, 1122, 1820 |
| `<tbody>` | `<tbody vitec-if="...">` | Lines 6387, 6482 |
| `<tr>` | `<tr vitec-if="Model.dokumentoutput == &quot;pdf&quot;">` | Lines 6160, 6164 |
| `<div>` | `<div vitec-if="Model.x.Count &gt; 0">` | Line 1281; also `<div style="page-break-inside:avoid" vitec-if="...">` (DB evidence: "Oppgjørsoppstilling Selger") |
| `<p>` | `<p vitec-if='...'>text</p>` | (DB evidence: "E-signeringsforespørsel SMS", "E-signeringspåminnelse SMS") |
| `<article>` | `<article class="item" vitec-if="...">` | Contract sections conditionally shown by eieform (Evidence: Kjøpekontrakt FORBRUKER) |
| `<li>` | `<li vitec-if="Model.oppdrag.hovedtype != ...">` | Conditional list items in Bilag section (Evidence: Kjøpekontrakt FORBRUKER) |
| `<ol>` | `<ol class="avoid-page-break">` | Ordered lists for numbered legal conditions (Evidence: Kjøpekontrakt FORBRUKER) |
| `<ul>` | (implied by vitec-foreach on `<ul>`, combined with vitec-if) | |

### Loop variable field access in vitec-if

Inside a `vitec-foreach` block, `vitec-if` expressions can reference the loop variable directly (without `Model.` prefix):

```html
<tbody vitec-foreach="matrikkel in Model.matrikler">
  <tr vitec-if="matrikkel.fnr != 0">
    <td>[[*matrikkel.fnr]]</td>
  </tr>
</tbody>
```

Also valid with nested property access:
```html
<span vitec-if="kjoper.idnummer.ToString().Length == 11">
  Personnr: [[*kjoper.idnummer]]
</span>
```

**(DB evidence: "Skjøte", "Egenerklæring om konsesjonsfrihet")**

### Escaping rules (critical)

#### Quotes in attribute values

All string comparisons require `&quot;` for quote characters:

```html
<!-- CORRECT -->
<span vitec-if="Model.eiendom.eieform == &quot;Andel&quot;">

<!-- WRONG — will break -->
<span vitec-if="Model.eiendom.eieform == "Andel"">
```

#### Norwegian characters (æ, ø, å)

Norwegian characters in vitec-if comparisons must use escape sequences:

| Character | Escape | Example |
|-----------|--------|---------|
| æ (liten) | `\xE6` | `Model.eiendom.grunntype == &quot;N\xE6ring&quot;` |
| Æ (stor) | `\xC6` | |
| ø (liten) | `\xF8` | `Model.oppdrag.hovedtype == &quot;Oppgj\xF8rsoppdrag&quot;` |
| Ø (stor) | `\xD8` | |
| å (liten) | `\xE5` | `Model.eiendom.poststed == &quot;\xC5rnes&quot;` |
| Å (stor) | `\xC5` | (note: uses uppercase Å escape for "Årnes") |

**Evidence:** Lines 6401–6428 in Alle-flettekoder explicitly document these escapes with examples.

#### Greater than / Less than

Must use HTML entities in attribute values:

```html
<!-- CORRECT -->
<table vitec-if="Model.kjopere.Count &gt; 0">

<!-- WRONG — HTML parser will break -->
<table vitec-if="Model.kjopere.Count > 0">
```

### Nesting rules

`vitec-if` can be nested — an element with `vitec-if` can contain children that also have `vitec-if`. This is implicitly confirmed by patterns like:

```html
<table vitec-if="Model.kjopere.Count &gt; 0">
  <tbody vitec-foreach="kjoper in Model.kjopere">
    <tr>
      <td><span vitec-if="kjoper.erfirma == true">Ja</span></td>
    </tr>
  </tbody>
</table>
```

Here `vitec-if` on `<table>` wraps a `vitec-foreach` on `<tbody>`, which contains `vitec-if` on `<span>`. (Lines 1820–1850)

### Common conditional patterns

#### Empty collection guard + foreach

The most common pattern guards a `vitec-foreach` with a `vitec-if` check for empty collections:

```html
<em vitec-if="Model.selgere.Count == 0">Ingen registrert</em>
<table vitec-if="Model.selgere.Count &gt; 0">
  <tbody vitec-foreach="selger in Model.selgere">
    <tr><td>[[*selger.navn]]</td></tr>
  </tbody>
</table>
```

#### Boolean toggle (Ja/Nei)

```html
<span vitec-if="Model.kjoper.erfirma == true">Ja</span>
<span vitec-if="Model.kjoper.erfirma == false">Nei</span>
```

#### Output channel branching

```html
<tr vitec-if="Model.dokumentoutput == &quot;pdf&quot;">
  <!-- PDF-only content -->
</tr>
<tr vitec-if="Model.dokumentoutput == &quot;email&quot;">
  <!-- Email-only content -->
</tr>
```

#### Sale vs rental branching

```html
<span vitec-if="!Model.oppdrag.type.Contains(&quot;tleie&quot;)">Selger</span>
<span vitec-if="Model.oppdrag.type.Contains(&quot;tleie&quot;)">Utleier</span>
```

### Known failure modes

1. **Missing `&quot;` escaping** — Using raw `"` inside attribute values breaks HTML parsing. The browser/renderer sees the attribute value as terminated early.
2. **Using `>` instead of `&gt;`** — Numeric comparisons with `>` will be interpreted as HTML tag closing, corrupting the element structure.
3. **Norwegian characters without `\x` escaping** — Comparing against strings containing æ, ø, or å without proper `\x` escapes causes the condition to never match.

---

## 4. Vitec-foreach Iteration

### Basic syntax

```html
<element vitec-foreach="item in Model.collection">
  [[item.property]]
</element>
```

The element is repeated once for each item in the collection. The loop variable (`item`) is available inside the element and its descendants.

#### Custom method as collection source

When a support template defines `@functions` methods that return a `List<>`, those methods can be used as the collection source in `vitec-foreach` — **without the `@` prefix**:

```html
<!-- Standard: iterate Model collection -->
<tbody vitec-foreach="kostnad in Model.kjoperskostnader.alleposter">

<!-- Custom: iterate method return value (no @ prefix) -->
<tbody vitec-foreach="kostnad in GetPosteringerUtenBoligkjoperforsikring()">
```

The loop variable (`kostnad`) works identically in both cases — merge fields like `[[*kostnad.beskrivelse]]` and `[[*kostnad.belop]]` resolve against each item.

**(Evidence: custom Proaktiv Kjøpekontrakt Bruktbolig)**

### Safe container elements for vitec-foreach

| Element | Example | Evidence |
|---------|---------|----------|
| `<tbody>` | `<tbody vitec-foreach="selger in Model.selgere">` | Most common; lines 501, 1123, 1821, 3012, 4843 |
| `<table>` | `<table vitec-foreach="pant in Model.oppdrag.kjoperspant">` | Lines 1282, 3522, 3676, 3783, 4009 |
| `<ul>` | `<ul vitec-foreach="kjoper in Model.kjopere">` | Lines 1961, 5162 |
| `<span>` | `<span vitec-foreach="selger in Model.selgere">` | Used for inline comma-separated lists (DB evidence: "Oppgjørsoppstilling Selger", "Forslag til fordelingskjennelse") |
| `<div>` | (implied by reference docs) | |
| `<tr>` | (possible but not observed as primary pattern) | |

**Best practice:** Use `<tbody>` as the foreach container when iterating table rows. This allows multiple `<tbody>` sections in a single `<table>`.

### Inline list separator pattern

For rendering comma-separated lists inline (e.g., "Name1, Name2, Name3"), use the `.liste` / `.separator` pattern:

```html
<span vitec-foreach="selger in Model.selgere">
  <span class="liste">
    [[*selger.navn]]<span class="separator">, </span>
  </span>
</span>
```

CSS hides the separator on the last item:
```css
#vitecTemplate .liste:last-child .separator {
    display: none;
}
```

Variants use different class names for the same pattern: `.seller`, `.buyer`, `.saksokte` instead of `.liste`.

**(DB evidence: "Oppgjørsoppstilling Selger" uses `.seller`, "Forslag til fordelingskjennelse" uses `.liste`)**

### Filtering with .Where()

Filter a collection to a subset:

```html
<tbody vitec-foreach="kostnad in Model.kjoperskostnader.alleposter.Where(x =&gt; x.kode == &quot;PARKERING&quot;)">
  <tr>
    <td>[[*kostnad.belop]]</td>
  </tr>
</tbody>
```

**Evidence:** Line 6381. Note the `=&gt;` (HTML entity for `=>` lambda arrow).

#### Complex Where with logical AND and cross-collection references

```html
<tbody vitec-foreach="pant in Model.oppdrag.pantforinnfrielse.Where(x =&gt; x.ertypeutleggsforretning == true &amp;&amp; Model.saksoker.firmanavn != x.navn)">
```

Note: `&&` must be HTML-escaped as `&amp;&amp;`. The lambda can reference both the iteration variable (`x`) and Model-level data (`Model.saksoker.firmanavn`).

**(DB evidence: "Forslag til fordelingskjennelse (Tvangssalg)", "Kjennelse ved fordeling av kjøpesum etter tvangssalg")**

#### Chaining .Where() with .Take()

```html
<tbody vitec-foreach="pant in Model.oppdrag.pantforinnfrielse.Where(x =&gt; x.ertypelegalpant == true).Take(1)">
```

Filters the collection first, then takes only the first N results. Observed chained patterns:
- `.Where(x =&gt; x.ertypelegalpant == true).Take(1)`
- `.Where(x =&gt; x.ertypelegalpant == false).Take(1)`
- `.Where(x =&gt; x.ertypeutleggsforretning == false).Take(1)`

**(DB evidence: "Forslag til fordelingskjennelse (Tvangssalg)")**

### Limiting with .Take()

Take only the first N items:

```html
<tbody vitec-foreach="pant in Model.oppdrag.pantforinnfrielse.Take(2)">
```

**Evidence:** Line 6482; also `Model.oppdrag.pantforinnfrielse.Take(1)` (DB evidence: "Forslag til fordelingskjennelse").

### Combined vitec-if and vitec-foreach on same element

Both attributes can appear on the same element:

```html
<tbody vitec-foreach="pant in Model.oppdrag.pantforinnfrielse.Take(2)" vitec-if="Model.oppdrag.pantforinnfrielse.Any()">
  <tr>
    <td>[[*pant.prioritet]]</td>
    <td>[[*pant.navn]]</td>
  </tr>
</tbody>
```

**Evidence:** Line 6482. The `vitec-if` acts as a guard — if the collection is empty, the element is not rendered at all.

### Nested foreach

Foreach can be nested. The inner loop uses the outer loop variable to access sub-collections:

```html
<ul vitec-foreach="kjoper in Model.kjopere">
  <li>Kjøper: [[*kjoper.navn]]
    <ul vitec-foreach="fullmektig in kjoper.fullmektiger_hvis_gruppe">
      <li>Fullmektig: [[*fullmektig.navn]]</li>
    </ul>
  </li>
</ul>
```

**Evidence:** Lines 1961–1967. Note the inner loop iterates over `kjoper.fullmektiger_hvis_gruppe` — a sub-property of the outer loop variable.

Another nested example with `<tbody>` inside `<table>`:

```html
<table vitec-foreach="pant in Model.oppdrag.mottakerspantforinnfrielse">
  <!-- ... pant rows ... -->
  <tbody vitec-foreach="laan in pant.laan">
    <tr><td>[[*laan.belop]]</td></tr>
  </tbody>
</table>
```

**Evidence:** Lines 3676–3742.

#### Grouped settlement pattern (nested table foreach)

Settlement documents use a two-level grouping pattern where an outer `vitec-foreach` iterates groups and an inner foreach iterates posts within each group:

```html
<table vitec-foreach="gruppe in Model.oppgjorselger.gruppering">
  <tbody>
    <tr class="borderoppgjor">
      <td colspan="100">[[*gruppe.overskrift]]</td>
    </tr>
  </tbody>
  <tbody vitec-foreach="post in gruppe.poster">
    <tr>
      <td colspan="14">[[*post.posteringsdato]]</td>
      <td colspan="40">[[*post.beskrivelse]]</td>
      <td colspan="17" style="text-align:right">
        <span vitec-if='post.debet != ""'>[[*post.debet]]</span>
      </td>
      <td colspan="17" style="text-align:right">
        <span vitec-if='post.kredit != ""'>[[*post.kredit]]</span>
      </td>
    </tr>
  </tbody>
</table>
```

**(DB evidence: "Oppgjørsoppstilling Selger")**

### Known collections

Collections observed in production templates (partial list):

| Collection | Loop variable | Evidence |
|------------|--------------|----------|
| `Model.meglerkontor.aktiveansatte` | `ansatt` | Line 501 |
| `Model.selgere` | `selger` | Lines 4843, 5022 |
| `Model.kjopere` | `kjoper` | Line 1821 |
| `Model.arvinger` | `arving` | Line 3012 |
| `Model.grunneiere` | `grunneier` | Line 3194 |
| `Model.hjemmelshavere` | `hjemmelshaver` | Line 3318 |
| `Model.tidligereeiere` | `tidligereeier` | Line 3434 |
| `Model.hoyestebud.budgivere` | `budgiver` | Line 1123 |
| `Model.matrikler` | `matrikkel` | Line 2261 |
| `Model.oppdrag.kjoperspant` | `pant` | Line 3522 |
| `Model.oppdrag.pantforinnfrielse` | `pant` | Line 3894 |
| `Model.oppdrag.mottakerspant` | `pant` | Line 3783 |
| `Model.oppdrag.mottakerspantforinnfrielse` | `pant` | Line 3676 |
| `pant.laan` | `laan` | Lines 3742, 3849, 3960 |
| `Model.selgervederlag.poster` | `vederlag` | Line 2703 |
| `Model.selgervederlag.alleposter` | `vederlag` | Line 2726 |
| `Model.selgerutlegg.poster` | `utlegg` | Line 2763 |
| `Model.selgerutlegg.alleposter` | `utlegg` | Line 2786 |
| `Model.selgerutgifter.poster` | `utgift` | Line 2823 |
| `Model.selgerutgifter.alleposter` | `utgift` | Line 2846 |
| `Model.selgersfakturerte.poster` | `faktura` | Line 2897 |
| `Model.selgersfakturerte.alleposter` | `faktura` | Line 2929 |
| `Model.kjoperskostnader.poster` | `kostnad` | Line 2066 |
| `Model.kjoperskostnader.alleposter` | `kostnad` | Line 2088 |
| `Model.kjopersfakturerte.poster` | `faktura` | Line 2138 |
| `Model.kjopersfakturerte.alleposter` | `faktura` | Line 2170 |
| `Model.solgteoppdragiomraade` | `oppdrag` | Line 2400 |
| `Model.mottaker.utbetalingsposter` | `postering` | Line 4009 |
| `Model.oppgjorkjoper.gruppering` | `gruppe` | Line 4066 |
| `gruppe.poster` | `post` | Lines 4073, 4131 |
| `Model.oppgjorselger.gruppering` | `gruppe` | Line 4124 |
| `Model.oppdrag.prosjekt.prosjektenheter` | `prosjektenhet` | Line 4226 |
| `Model.oppdrag.prosjekt.utbyggersforbehold.forbehold` | `forbehold` | Line 4350 |
| `Model.oppdrag.prosjektenhet.parkeringsplasser` | `prosjektenhet` | Line 4452 |
| `Model.oppdrag.prosjekt.vederlagpaomsetninger` | `vederlagpaomsetning` | Line 4689 |
| `Model.eiendom.kommendevisninger` | `visning` | Line 5807 |
| `visning.slots` | `slot` | Line 5824 |
| `Model.saksokere` | `saksoker` | Line 5354 |
| `Model.saksokteliste` | `saksokte` | Line 5713 |
| `Model.oppdrag.pantedokumenterkjoper` | `depotdokument` | Line 1282 |
| `kjoper.fullmektiger_hvis_gruppe` | `fullmektig` | Lines 1963, 5164 |
| `selger.fullmektiger_hvis_gruppe` | `fullmektig` | Line 5164 |
| `Model.oppdrag.saksokerspant` | `pant` | Line 5485 |

#### Additional collections from database templates

| Collection | Loop variable | Evidence |
|------------|--------------|----------|
| `Model.oppdrag.pantforinnfrielse.Where(x =&gt; x.ertypelegalpant == true)` | `pant` | (DB: "Forslag til fordelingskjennelse") |
| `Model.oppdrag.pantforinnfrielse.Where(x =&gt; x.ertypefrivilligpant == true &amp;&amp; Model.saksoker.firmanavn != x.navn)` | `pant` | (DB: "Forslag til fordelingskjennelse") |
| `Model.oppdrag.pantforinnfrielse.Where(x =&gt; x.ertypeutleggsforretning == true &amp;&amp; Model.saksoker.firmanavn != x.navn)` | `pant` | (DB: "Kjennelse ved fordeling") |
| `Model.selgerutgifter.alleposter` | `utgifter` | (DB: multiple settlement templates) — Note: alternative variable name `utgifter` alongside `utgift` |

---

## 5. Merge Field Reference

### Standard merge field syntax

```
[[field.path]]
```

Double square brackets delimit a merge field. The field path uses dot notation to traverse the data model.

### Required fields (asterisk)

```
[[*field.path]]
```

The asterisk prefix marks a field as required. If the field has no value at render time, the rendered output will contain a visible placeholder or error marker instead of blank space. Used inside foreach loops to ensure loop items have the expected data.

**Evidence:** `[[*ansatt.navn]]` (line 504), `[[*selger.navn]]` (line 4844), `[[*pant.prioritet]]` (line 6484).

### Merge field paths

Fields follow a hierarchical path structure. Top-level objects include:
- `meglerkontor` — Office information
- `avsender` — Sender (logged-in user)
- `mottaker` — Recipient
- `eiendom` — Property
- `oppdrag` — Assignment/listing
- `selger` / `selgere` — Seller(s)
- `kjoper` / `kjopere` — Buyer(s)
- `kontrakt` — Contract
- `ansvarligmegler`, `megler1`, `megler2`, `medhjelper`, `salgsmegler` — Agents
- `oppgjorsansvarlig` — Settlement officer
- `borettslag` — Housing cooperative
- `pant` — Mortgage/lien
- `bud` / `budgivere` — Bid(s)
- `visning` / `visninger` — Showing(s)
- `dagsdato`, `dagensdato`, `dato`, `p`, `P` — Date and page numbers
- `timer` — Time tracking (`timer.paalopt.salg`, `.visning`, `.bud`, `.kontrakt`, `.oppgjor`)
- `tvangssalgrefnr` — Forced sale reference number
- `skjema` — Kartverket form data (`skjema.innsender.navn`, `.adresse`, `.postnr`, `.poststed`, `.orgnr`; `skjema.referansenr`)
- `sameie` — Co-ownership data (`sameie.sameiebrok`)
- `komplettmatrikkelutvidet` — Full cadastral reference (expanded format)
- `esignering` — E-signing (`esignering.dokumentnavn`, `.melding`, `.lenke`)

Full field listing: see `.cursor/vitec-reference.md` sections "Flettekoder (Merge Fields) — Komplett Oversikt".

### Additional merge field paths from database templates

| Path | Description | Evidence |
|------|-------------|----------|
| `oppgjorselger.sumdebet` | Settlement debit total | (DB: "Oppgjørsoppstilling Selger") |
| `oppgjorselger.sumkredit` | Settlement credit total | (DB: "Oppgjørsoppstilling Selger") |
| `oppgjorselger.summva` | Settlement VAT total | (DB: "Oppgjørsoppstilling Selger") |
| `oppgjorselger.saldo` | Settlement balance | (DB: "Oppgjørsoppstilling Selger") |
| `kontrakt.formidling.nr` | Transaction number | (DB: "Kjøpekontrakt FORBRUKER") |
| `kontrakt.dato` | Contract signing date | Kjøpekontrakt Aksje |
| `kontrakt.kjopesum` | Purchase price (numeric, format via `$.UD()`) | Kjøpekontrakt Aksje |
| `kontrakt.overtagelse.dato` | Agreed takeover date | Kjøpekontrakt Aksje |
| `oppdrag.nr` | Assignment/case number ("Vår ref:" in letters) | Grunnlag brevmal, Kjøpekontrakt Aksje |
| `eiendom.prosjektnavn` | Project name | (DB: "Oppgjørsoppstilling Selger") |
| `eiendom.alfanavn` | Unit alpha name | (DB: "Oppgjørsoppstilling Selger") |
| `eiendom.leilighetsnr` | Apartment number | (DB: "Oppgjørsoppstilling Selger") |
| `timer.paalopt.*` | Elapsed hours by phase (salg, visning, bud, kontrakt, oppgjor) | (DB: "Oppgjørsoppstilling Selger") |
| `avsender.navn` | Sender's full name | System signatures |
| `avsender.tittel` | Sender's job title | System signatures |
| `avsender.mobiltlf` | Sender's mobile phone | System signatures |
| `avsender.epost` | Sender's email | System signatures |
| `avsender.meglerkontor.navn` | Office name (legal) | E-post signatur |
| `avsender.meglerkontor.markedsforingsnavn` | Office marketing name (display name) | SMS-signatur, Avsender PDF |
| `avsender.meglerkontor.besoksadresse` | Office visit address | E-post signatur |
| `avsender.meglerkontor.postnr` | Office postal code | E-post signatur |
| `avsender.meglerkontor.poststed` | Office postal city | E-post signatur |
| `meglerkontor.kjedenavn` | Chain/franchise name | Vitec Topptekst |
| `meglerkontor.firmalogourl` | Company logo URL | Vitec Topptekst |
| `meglerkontor.juridisknavn` | Legal company name | Vitec Bunntekst |
| `meglerkontor.besokspostnr` | Visit address postal code | Vitec Bunntekst |
| `meglerkontor.besokspoststed` | Visit address postal city | Vitec Bunntekst |
| `mottaker.navn` | Recipient name | Mottaker resource |
| `mottaker.adresse` | Recipient street address | Mottaker resource |
| `mottaker.postnr` | Recipient postal code | Mottaker resource |
| `mottaker.poststed` | Recipient postal city | Mottaker resource |
| `dagensdato` | Today's date (at generation time) | Mottaker resource |
| `skjema.innsender.navn` | Form submitter name | "Skjøte" (Kartverket form header) |
| `skjema.innsender.adresse` | Form submitter address | "Skjøte" (Kartverket form header) |
| `skjema.innsender.postnr` | Form submitter postal code | "Skjøte" (Kartverket form header) |
| `skjema.innsender.poststed` | Form submitter postal city | "Skjøte" (Kartverket form header) |
| `skjema.innsender.orgnr` | Form submitter org/personal ID | "Skjøte" (Kartverket form header) |
| `skjema.referansenr` | Form reference number | "Skjøte" (Kartverket form header) |
| `eiendom.kommunenr` | Municipality number | "Skjøte" |
| `eiendom.kommunenavn` | Municipality name | "Skjøte" |
| `eiendom.typegrunn` | Ground use classification (7 Kartverket categories) | "Skjøte" |
| `eiendom.typebolig` | Housing type classification (5 Kartverket categories) | "Skjøte" |
| `kontrakt.avgiftsgrunnlag` | Tax basis / sales value | "Skjøte" |
| `kontrakt.kjopesumibokstaver` | Purchase price in words | "Skjøte" |
| `sameie.sameiebrok` | Co-ownership fraction | "Skjøte" |
| `selger.selgersektefelle.navnutenfullmektig` | Seller's spouse name (without fullmektig) | "Skjøte" |
| `oppdrag.prosjekt.saerskilteavtaler` | Special agreements (tinglysing) | "Skjøte" |
| `oppdrag.prosjekt.andreavtaler` | Other agreements (non-tinglysing) | "Skjøte" |
| `selger.ledetekst_fdato_orgnr` | Dynamic label: "Fødselsdato" or "Org.nr." depending on party type | Grunnlag brevmal |
| `selger.fdato_orgnr` | Combined birth date / org number value | Grunnlag brevmal |
| `kjoper.ledetekst_fdato_orgnr` | Dynamic label: "Fødselsdato" or "Org.nr." depending on party type | Grunnlag brevmal |
| `kjoper.fdato_orgnr` | Combined birth date / org number value | Grunnlag brevmal |
| `selger.firmanavn` | Seller company/firm name (vs `selger.navn` for person) | Kjøpekontrakt Næring |
| `selger.hovedkontakt.navn` | Seller's main contact person name | Kjøpekontrakt Næring |
| `selger.hovedgatenavnognr` | Seller's head office street address | Kjøpekontrakt Næring |
| `selger.hovedpostnr` | Seller's head office postal code | Kjøpekontrakt Næring |
| `selger.hovedpoststed` | Seller's head office postal city | Kjøpekontrakt Næring |
| `selger.hovedkontonummer` | Seller's main bank account number | Kjøpekontrakt Næring |
| `kjoper.firmanavn` | Buyer company/firm name | Kjøpekontrakt Næring |
| `kjoper.hovedkontakt.navn` | Buyer's main contact person name | Kjøpekontrakt Næring |
| `kjoper.hovedgatenavnognr` | Buyer's head office street address | Kjøpekontrakt Næring |
| `kjoper.hovedpostnr` | Buyer's head office postal code | Kjøpekontrakt Næring |
| `kjoper.hovedpoststed` | Buyer's head office postal city | Kjøpekontrakt Næring |
| `operativmegler.navn` | Operating broker's name | Kjøpekontrakt Næring |
| `operativmegler.epost` | Operating broker's email | Kjøpekontrakt Næring |
| `kontrakt.klientkonto` | Client escrow account number | Kjøpekontrakt Næring |
| `pant.navn` | Mortgage holder / bank name (foreach loop) | Kjøpekontrakt Næring |
| `pant.panthaverorgnr` | Mortgage holder org number (foreach loop) | Kjøpekontrakt Næring |
| `aksjeselskap.navn` | Company name (in share sale transactions) | Kjøpekontrakt Aksje |
| `aksjeselskap.orgnr` | Company org number | Kjøpekontrakt Aksje |
| `aksjeselskap.aksjenr` | Share numbers (e.g., "1-100") | Kjøpekontrakt Aksje |
| `hjemmelshaver.navn` | Title holder name (when different from seller) | Kjøpekontrakt Aksje |
| `hjemmelshaver.fdato_orgnr` | Title holder birth date / org number | Kjøpekontrakt Aksje |
| `selger.hovedepost` | Seller's main email address | Kjøpekontrakt Aksje |
| `selger.idnummer` | Seller's ID number (birth date or org number) | Kjøpekontrakt Aksje |
| `kjoper.hovedepost` | Buyer's main email address | Kjøpekontrakt Aksje |
| `komplettmatrikkelutvidet` | Full cadastral reference (expanded format) | Kjøpekontrakt Aksje |
| `komplettmatrikkel` | Short cadastral reference (compact format, used in Bilag) | Kjøpekontrakt Aksje |
| `selger.gatenavnognr` | Seller's street address (in foreach loop) | Grunnlag brevmal, Kjøpekontrakt Aksje |
| `selger.postnr` | Seller's postal code (in foreach loop) | Grunnlag brevmal, Kjøpekontrakt Aksje |
| `selger.poststed` | Seller's postal city (in foreach loop) | Grunnlag brevmal, Kjøpekontrakt Aksje |
| `selger.tlf` | Seller's phone number (in foreach loop) | Grunnlag brevmal, Kjøpekontrakt Aksje |
| `selger.emailadresse` | Seller's email address (in foreach loop) | Grunnlag brevmal, Kjøpekontrakt Aksje |
| `kjoper.gatenavnognr` | Buyer's street address (in foreach loop) | Grunnlag brevmal, Kjøpekontrakt Aksje |
| `kjoper.postnr` | Buyer's postal code (in foreach loop) | Grunnlag brevmal, Kjøpekontrakt Aksje |
| `kjoper.poststed` | Buyer's postal city (in foreach loop) | Grunnlag brevmal, Kjøpekontrakt Aksje |
| `kjoper.tlf` | Buyer's phone number (in foreach loop) | Grunnlag brevmal, Kjøpekontrakt Aksje |
| `kjoper.emailadresse` | Buyer's email address (in foreach loop) | Grunnlag brevmal, Kjøpekontrakt Aksje |

### Merge fields inside foreach loops

Inside a `vitec-foreach` block, merge fields use the loop variable instead of `Model`:

```html
<tbody vitec-foreach="selger in Model.selgere">
  <tr>
    <td>[[*selger.navn]]</td>
    <td>[[*selger.fodselsnr]]</td>
  </tr>
</tbody>
```

### Merge fields in attributes vs text nodes

**In text nodes (standard):**
```html
<td>[[meglerkontor.navn]]</td>
```

**In `src` attributes (images):**

Images use the `@Model.` Razor syntax instead of `[[...]]`:
```html
<img src="@Model.ansvarligmegler.hovedbilde" />
<img src="@Model.meglerkontor.firmalogourl" />
```

**Evidence:** Lines 6243–6292. All image `src` values use `@Model.` prefix, not `[[...]]`.

There is also a `[[...]]` variant for image URLs in some templates:
```html
<img src="[[meglerkontor.firmalogourl]]" style="max-height:1.5cm; max-width:6cm" />
```

**Evidence:** Header template in `vitec-reference.md` line 949. Both syntaxes appear to work.

**In vitec-if expressions:**
```html
vitec-if="Model.eiendom.eieform == &quot;Andel&quot;"
```

Note: vitec-if uses `Model.` prefix (no `@`), no `[[...]]` brackets.

### Function wrappers

| Function | Purpose | Syntax | Example |
|----------|---------|--------|---------|
| `$.UD()` | Format number without decimals | `$.UD([[field]])` | `$.UD([[eiendom.pris]])` → "5 000 000" |
| `$.BOKST()` | Number to Norwegian words | `$.BOKST([[field]])` | `$.BOKST([[kontraktsposisjon.totalpris]])` |
| `$.CALC()` | Mathematical calculation | `$.CALC(expression)` | `$.CALC([[oppdrag.timeprisinklmva]]/1,25)` |
| `$.CALC(UD:...)` | Calculation without decimals | `$.CALC(UD:expression)` | `$.CALC(UD:1 + 2 - 3)` |
| `$.CALCHOURS()` | Sum hours (HH:MM format) | `$.CALCHOURS(expr)` | `$.CALCHOURS([[timer.paalopt.salg]]+[[timer.paalopt.visning]]+[[timer.paalopt.bud]]+[[timer.paalopt.kontrakt]]+[[timer.paalopt.oppgjor]])` (DB evidence: "Oppgjørsoppstilling Selger") |
| `$.CALCBOKST()` | Calculation result as words | `$.CALCBOKST(expr)` | `$.CALCBOKST([[eiendom.pris]] + [[eiendom.fellesgjeld]])` |
| `$.SKALER()` | Scale image | `$.SKALER(@Model.url, h=px)` | `$.SKALER(@Model.eiendom.hovedbilde, h=100)` |

**Evidence:** Lines 6302–6367 document all functions with live examples.

**CALC operators:**
- Addition: `+`
- Subtraction: `-`
- Multiplication: `*` or `x`
- Division: `/`
- Parentheses: `(` `)`
- Decimal separator: comma `,` or period `.`

**CALC operands:** Expressions can mix merge fields and Razor method calls:
- Merge fields: `[[kontrakt.kjopesumogomkostn]]`
- Custom method calls: `@GetPosteringsVerdiForBoligkjoperforsikring()`
- Example: `$.CALC(UD:[[kontrakt.kjopesumogomkostn]]-@GetPosteringsVerdiForBoligkjoperforsikring())` — subtracts the boligkjøperforsikring amount from total, outputs with tusenskilletegn formatting.

**(Evidence: custom Proaktiv Kjøpekontrakt Bruktbolig)**

### Page numbering

| Field | Output |
|-------|--------|
| `[[p]]` | Current page number |
| `[[P]]` | Total page count |
| `[[dagensdato]]` | Today's date |

**Evidence:** Footer templates in `vitec-reference.md` lines 806–807; Alle-flettekoder line 284 uses `[[dagensdato]]` (note: slightly different from `[[dagsdato]]` in reference docs).

### Inline Razor expressions

Some templates use Razor syntax (`@Model.property`) directly in text nodes:

```html
<td>kr @Model.oppgjorkjoper.saldo.Remove(0,1)</td>
```

This is used for inline string manipulation (e.g., removing a minus sign). **This is not the same as `[[...]]` syntax** — Razor expressions are processed server-side before merge field substitution.

**Evidence:** Line 6306.

---

## 6. Table Patterns

Tables are the primary layout mechanism in Vitec templates.

### Standard table structure

```html
<table style="table-layout:fixed; width:21cm">
  <tbody>
    <tr>
      <td colspan="30">Label</td>
      <td colspan="70">[[field.value]]</td>
    </tr>
  </tbody>
</table>
```

### Column spanning convention

Vitec templates use a 100-unit colspan system. Columns are expressed as percentages:

| Pattern | Usage | Evidence |
|---------|-------|----------|
| `30/70` | Label + value | Most common; lines 297–425 |
| `100` | Full-width section headers | Lines 292–293, 355–356 |
| `20/80` | Narrow label + wide value | Lines 503–517 |
| `25/25/25/25` | Four equal columns | Lines 6239–6282 (images) |
| `30/40/30` | Three-column footer | `vitec-reference.md` line 635 |
| `25/75` | Two-column with wider right | Lines 6222–6223 |
| `33/34/33` | Three roughly equal columns | Line 6226–6228 |
| `30/35/35` | Label + two-choice radio | Lines 6178–6180 |
| `75/25` | Wide left + narrow right | Line 6222 |
| `50/50` | Half-and-half | Lines 1841, 1850 |

### Multiple `<tbody>` sections

A single `<table>` can contain multiple `<tbody>` elements. This is valid HTML and is the standard Vitec pattern for grouping rows:

```html
<table>
  <thead>
    <tr><th colspan="100"><h1>Title</h1></th></tr>
  </thead>
  <tfoot>
    <tr><th colspan="100">Footer</th></tr>
  </tfoot>
  <tbody>
    <tr><td colspan="100"><h3>Section 1</h3></td></tr>
    <!-- rows -->
  </tbody>
  <tbody>
    <tr><td colspan="100"><h3>Section 2</h3></td></tr>
    <!-- rows -->
  </tbody>
</table>
```

**Evidence:** The entire Alle-flettekoder template uses this structure — one `<table>` with `<thead>`, `<tfoot>`, and many `<tbody>` sections.

### `<tbody>` as foreach container

When iterating table rows, `vitec-foreach` goes on the `<tbody>`:

```html
<table>
  <tbody vitec-foreach="selger in Model.selgere">
    <tr>
      <td colspan="30">[[*selger.navn]]</td>
      <td colspan="70">[[*selger.fodselsnr]]</td>
    </tr>
  </tbody>
</table>
```

This creates a new `<tbody>` for each iteration, which is valid HTML.

### Nested tables

Tables can be nested inside `<td>` cells:

```html
<tr>
  <td colspan="70">
    <table vitec-if="Model.kjopere.Count &gt; 0">
      <tbody vitec-foreach="kjoper in Model.kjopere">
        <tr><td>[[*kjoper.navn]]</td></tr>
      </tbody>
    </table>
  </td>
</tr>
```

**Evidence:** Lines 500–522, 1820–1955.

### `form-table` class pattern

The `form-table` class creates bordered form-like tables:

```html
<table class="form-table">
  <tbody>
    <tr>
      <td colspan="75" data-label="Adresse">[[eiendom.gatenavnognr]]</td>
      <td colspan="25" data-label="Oppdragsnr.">[[oppdrag.nr]]</td>
    </tr>
  </tbody>
</table>
```

CSS rules for `form-table`:
```css
#vitecTemplate .form-table {
    border-top: solid 1px #000;
}
#vitecTemplate .form-table td {
    border: solid 1px #000;
}
#vitecTemplate .form-table td p {
    margin: 0;
    padding: 0;
}
```

**Evidence:** Lines 80–91 (CSS), line 6219 (usage).

### Table attributes

| Attribute | Values observed | Purpose |
|-----------|----------------|---------|
| `style="table-layout:fixed"` | On outer tables | Prevents column width from depending on content |
| `style="width:21cm"` | On outer tables | A4 page width |
| `style="width:100%"` | On nested tables | Fill parent container |
| `cellspacing="0"` | On some tables | Legacy spacing removal |
| `border-collapse:collapse` | Via Stilark CSS | Default for all tables under `#vitecTemplate` |
| `colspan` | Numeric (1–100) | Column spanning |
| `rowspan` | Numeric | Row spanning (line 6188) |

### Page break control

Page breaks are controlled via CSS properties and a dedicated CSS class. Observed in **52 database templates**:

| Pattern | CSS | Usage | Evidence |
|---------|-----|-------|----------|
| Prevent break inside | `page-break-inside: avoid` | On sections that should not split across pages | Most common (45+ templates) |
| Force break after | `page-break-after: always` | Between major document sections | "Akseptbrev kjøper", "Seksjoneringsbegjæring" |
| Force break before | `page-break-before: always` | Before new sections | "Hjemmelsoverføring" |
| CSS class | `.avoid-page-break` | Same as inline `page-break-inside: avoid` | "Kjøpekontrakt FORBRUKER", "Oppdragsavtale" |

Applied via inline style:
```html
<div style="page-break-inside:avoid">
  <!-- Content that must stay on one page -->
</div>
```

Or via CSS class:
```html
<article class="avoid-page-break item">
  <!-- Contract section -->
</article>
```

Also applied at the table/row level:
```html
<table style="page-break-inside:avoid">
#vitecTemplate table tr { page-break-inside: avoid; }
```

**(DB evidence: 52 templates use page-break patterns)**

### Empty table hiding

Tables that render empty (e.g., when a foreach produces no iterations) can be hidden:

```css
#vitecTemplate table:empty {
    display: none;
}
```

**(DB evidence: "Forslag til fordelingskjennelse (Tvangssalg)")**

### Known table issues in CKEditor

CKEditor 4 has opinions about tables:

1. **Empty cells** — CKEditor may insert `&nbsp;` into empty `<td>` elements. This is harmless.
2. **Table structure validation** — CKEditor validates `<table>` → `<tbody>`/`<thead>`/`<tfoot>` → `<tr>` → `<td>`/`<th>` hierarchy. Elements out of this order may be restructured.
3. **Missing `<tbody>`** — CKEditor may add `<tbody>` wrapper if rows are directly inside `<table>`.

---

## 7. CSS and Styling Rules

### Vitec Stilark — Complete Source (authoritative)

The Vitec Stilark is the **base stylesheet** applied to all templates via the `<span vitec-template="resource:Vitec Stilark">` resource reference. It is injected as an inline `<div>` element:

```html
<div id="vitec-stilark" style="display:inline">
<style type="text/css">
@import url('https://fonts.googleapis.com/css2?family=Open+Sans:wght@300;400;700&display=swap');

html, body {
    margin: 0;
    padding: 0;
    font-size: 10pt;
    line-height: normal;
    font-family: 'Open sans', sans-serif;
}

#vitecTemplate * {
    font-variant-ligatures: none;
}

#editDocumentTemplate #vitec-stilark:after {
    display: block;
    padding: 1cm 1cm 1.5cm 1cm;
    content: "Se kildekode";
    font-size: 26pt;
    font-weight: 400;
    font-family: 'Open sans', sans-serif;
    color: rgba(124, 124, 124, 0.7);
}

#vitecTemplate p,
#vitecTemplate th p,
#vitecTemplate td p {
    font-size: 10pt;
    line-height: normal;
    font-family: 'Open sans', sans-serif;
    margin: 1em 0;
    padding-bottom: 0;
}

#vitecTemplate h1,
#vitecTemplate h2,
#vitecTemplate h3,
#vitecTemplate h4,
#vitecTemplate h5 {
    font-family: 'Open sans', sans-serif;
}

#vitecTemplate table {
    border-collapse: collapse;
    border-spacing: 0;
}

#vitecTemplate table th,
#vitecTemplate table td {
    vertical-align: top;
    font-size: 10pt;
    line-height: normal;
    font-family: 'Open sans', sans-serif;
}

#vitecTemplate table th {
    text-align: left;
}

#vitecTemplate strong {
    font-size: 10pt;
    line-height: normal;
    font-family: 'Open sans', sans-serif;
    font-weight: 700;
}

#vitecTemplate ul li,
#vitecTemplate ol li {
    font-size: 10pt;
    line-height: normal;
    font-family: 'Open sans', sans-serif;
}

#vitecTemplate div {
    font-size: 10pt;
    line-height: normal;
    font-family: 'Open sans', sans-serif;
}

/* "Ikke overstyre font-størrelser satt med CK Editor" */
#vitecTemplate span > strong {
    font-size: inherit;
}
</style>
</div>
```

#### Stilark analysis

The Stilark is intentionally minimal — it is a **font and reset baseline**, not a layout framework. All complex CSS (counters, data-labels, borders, checkbox toggles, etc.) comes from template-specific `<style>` blocks.

**What the Stilark does:**

| Rule | Selector | Effect |
|------|----------|--------|
| Font loading | `@import url(...)` | Loads Open Sans from Google Fonts (weights 300, 400, 700) |
| Body reset | `html, body` | `margin: 0; padding: 0; font-size: 10pt` |
| Ligature prevention | `#vitecTemplate *` | `font-variant-ligatures: none` on all elements |
| Paragraph spacing | `#vitecTemplate p` | `margin: 1em 0; padding-bottom: 0` |
| Heading font | `#vitecTemplate h1–h5` | Font family only — NO font-size override (browser defaults apply) |
| Table reset | `#vitecTemplate table` | `border-collapse: collapse; border-spacing: 0` (no borders by default) |
| Cell alignment | `#vitecTemplate th, td` | `vertical-align: top; text-align: left` (th only for text-align) |
| Bold weight | `#vitecTemplate strong` | `font-weight: 700` |
| CKEditor fix | `#vitecTemplate span > strong` | `font-size: inherit` — prevents Stilark from overriding CKEditor-set font sizes |
| Editor placeholder | `#editDocumentTemplate #vitec-stilark:after` | Shows "Se kildekode" in CKEditor (editor-only, not visible in output) |

**What the Stilark does NOT do:**

- No colors (no `color`, no `background-color`)
- No heading sizes (h1–h5 use browser defaults)
- No border styles (tables have `border-collapse` but no `border`)
- No print-specific styles (no `@media print`)
- No layout widths (no `width: 21cm`)
- No padding/margin on tables or cells
- No CSS classes defined

**Key implication:** All layout, borders, colors, heading sizes, and interactive styles (checkboxes, data-labels, counters) must be provided by template-specific `<style>` blocks. The Stilark only ensures consistent font rendering.

#### Stilark injection mechanism

When rendered, the `<span vitec-template="resource:Vitec Stilark">&nbsp;</span>` is replaced by the Stilark's actual content — a `<div id="vitec-stilark" style="display:inline">` containing a `<style>` block. The `display:inline` ensures the injected div doesn't affect layout.

**(Evidence: Vitec Stilark system template source code, provided by Proaktiv admin)**

### Inline styles — what survives

The project's `SanitizerService` (`backend/app/services/sanitizer_service.py`) defines which inline styles are preserved. These are the **structural** properties that control layout:

| Category | Preserved properties |
|----------|---------------------|
| **Dimensions** | `width`, `height`, `max-width`, `max-height`, `min-width`, `min-height` |
| **Spacing** | `margin`, `margin-top/bottom/left/right`, `padding`, `padding-top/bottom/left/right` |
| **Borders** | `border`, `border-top/bottom/left/right`, `border-collapse`, `border-spacing` |
| **Alignment** | `text-align`, `vertical-align` |
| **Layout** | `display`, `float`, `clear`, `position`, `top/bottom/left/right`, `table-layout` |
| **Page breaks** | `page-break-before`, `page-break-after`, `page-break-inside` |

### Inline styles — what gets stripped

When the sanitizer runs (full strip mode), these are removed because the Stilark handles them:

- `font-family` — Stilark sets Open Sans on all elements
- `font-size` — Stilark sets 10pt; only override where necessary (e.g. `<small>` for 8pt)
- `color` — Let the browser default (black) handle it
- `background-color` — Stripped unless structural
- `font-weight` — Use `<strong>` instead
- `font-style` — Use `<em>` instead
- `line-height` — Stilark sets `normal`

### Inline styles observed in production templates

Despite the sanitizer, production templates in the database already have clean inline styles. Common patterns:

```css
/* Cell padding */
padding: 0 5px;
padding: 16px 2px 5px 4px;
padding-left: 1cm;
padding-right: 1cm;

/* Dimensions */
width: 21cm;
width: 100%;
width: 3cm;
height: 1.5cm;

/* Borders */
border-top: solid 1px #000;
border-top: solid 1px #ededed;
border-style: none;
border-width: 0px;

/* Alignment */
text-align: right;
text-align: center;
text-align: left;
vertical-align: top;
vertical-align: middle;
vertical-align: bottom;

/* Layout */
table-layout: fixed;
float: right;
display: inline-block;
display: inline-table;
display: none;
position: relative;
position: absolute;

/* Image sizing */
max-height: 4cm;
max-width: 4cm;
max-height: 1.5cm;
max-width: 6cm;
```

### CSS classes available

From Alle-flettekoder `<style>` blocks and **133 database templates** (100+ distinct classes observed):

#### Core classes (from Alle-flettekoder)

| Class | Purpose | Defined in |
|-------|---------|-----------|
| `form-table` | Bordered form layout table | Line 80 |
| `insert` | Editable placeholder span | Line 108 |
| `insert-table` | Inline-table wrapper for insert spans | Line 127 |
| `btn` | Bootstrap-style button/label | Line 209 |
| `active` | Active state for toggles | Lines 219, 249 |
| `svg-toggle` | SVG checkbox/radio visual | Line 225 |
| `checkbox` | Checkbox variant of svg-toggle | Line 245 |
| `radio` | Radio variant of svg-toggle | Line 255 |
| `scaled-image` | Circular cropped image (100×100px) | Line 62 |
| `no-border` | Remove borders from cells | `vitec-reference.md` line 850 |

#### Structural/layout classes (from database templates)

| Class | Purpose | Evidence |
|-------|---------|----------|
| `proaktiv-theme` | Company theme on wrapper div | All 133 templates |
| `avoid-page-break` | Prevents page break inside element | "Kjøpekontrakt FORBRUKER" |
| `item` | CSS counter section numbering | "Kjøpekontrakt FORBRUKER", "Oppdragsavtale" |
| `a4-main` | A4 page main content area | Multiple templates |
| `main-table` | Primary layout table | Multiple templates |
| `first-table` / `first-page-table` | First page table styling | Multiple templates |
| `last-table` | Last table special styling | Multiple templates |
| `roles-table` | Party listing table (sellers/buyers) | "Kjøpekontrakt FORBRUKER" |
| `info-table` | Information display table | "Oppdragsavtale" |
| `witness-table` | Witness signature table | Multiple templates |
| `bordered-table` | Table with full borders | Multiple templates |
| `with-nested-table` | Cell containing nested table (padding: 0) | "Skjøte" |

#### Border utility classes

| Class | Purpose | Evidence |
|-------|---------|----------|
| `borders` | Top + bottom borders | "Forslag til fordelingskjennelse" |
| `border-bottom` | Bottom border only | Multiple templates |
| `border-top` | Top border only | Multiple templates |
| `border-left` | Left border | "Søknad om konsesjon" |
| `border-right` | Right border | Multiple templates |
| `sideborders` | Left + right borders | Multiple templates |
| `border-bottom-dotted` | Dotted bottom border | Multiple templates |

#### Alignment utility classes

| Class | Purpose | Evidence |
|-------|---------|----------|
| `vtop` / `vertical-top` | `vertical-align: top` | Multiple templates |
| `vbottom` | `vertical-align: bottom` | Multiple templates |
| `vcenter` | `vertical-align: middle` | Multiple templates |
| `hcenter` | `text-align: center` (horizontal) | Multiple templates |
| `center` | `text-align: center` | Multiple templates |
| `text-right` | `text-align: right` | "Forslag til fordelingskjennelse" |
| `text-center` | `text-align: center` | Multiple templates |

#### Color/background classes

| Class | Purpose | Evidence |
|-------|---------|----------|
| `bg-color` | Header/accent background color | Multiple templates |
| `bg-green` / `bg-green-light` | Green status background | Multiple templates |
| `bg-red` / `bg-red-light` | Red status background | Multiple templates |
| `row-header` | Row header with grey background (`#f2f2f2`) | "Skjøte" |
| `header-cell` | Header cell styling | Multiple templates |

#### Settlement/financial classes

| Class | Purpose | Evidence |
|-------|---------|----------|
| `borderoppgjor` | Settlement row with bottom border | "Oppgjørsoppstilling Selger" |
| `bordersum` | Sum row with top + bottom borders | "Oppgjørsoppstilling Selger" |
| `delsumlinje` | Subtotal row | Multiple templates |
| `sumlinje` | Total row | Multiple templates |
| `mvacell` | VAT cell (italic, lightgray background) | "Oppgjørsoppstilling Selger" |

#### Form/input classes

| Class | Purpose | Evidence |
|-------|---------|----------|
| `checkbox-table` | Checkbox layout table | "Akseptbrev kjøper email" |
| `checkbox-table-one-row` | Single-row checkbox layout | "Akseptbrev kjøper email" |
| `checkbox-row` | Row with extra padding for data-choice | "Skjøte" |
| `sign-field` / `sign-field1` / `sign-fields` | Signature line (inline-block, border-top, 45% width) | "Akseptbrev kjøper email" |
| `insert-box` / `insert-textbox` | Editable input areas | Multiple templates |
| `bold-data-label` | Bold floating label variant | "Skjøte" |
| `add-signature` | Add-signature button area | Multiple templates |

#### List/iteration classes

| Class | Purpose | Evidence |
|-------|---------|----------|
| `liste` | List item wrapper (with `:last-child .separator { display: none }`) | "Forslag til fordelingskjennelse" |
| `separator` | Comma/delimiter hidden on last item | "Oppgjørsoppstilling Selger" |
| `nummerert-liste` | CSS counter auto-numbered paragraph | "Forslag til fordelingskjennelse" |
| `foreach-list` | Foreach loop list container | "Skjøte" |
| `list` | General list styling with vertical padding | "Forslag til fordelingskjennelse" |
| `seller` / `buyer` / `saksokte` | Role-specific list item (same `:last-child .separator` pattern) | "Oppgjørsoppstilling Selger" |

#### Other utility classes

| Class | Purpose | Evidence |
|-------|---------|----------|
| `overskrift1` / `overskrift2` | Heading styles (grey bg, bold) | "Akseptbrev kjøper email" |
| `bookmark` | Internal document link (no underline, italic) | "Kjøpekontrakt FORBRUKER" |
| `collapse` / `collapse-span` | Bootstrap collapsible sections | "Aksjeeierbok (Næring)" |
| `screen-help` / `screen-help-info` | On-screen help buttons (hidden in PDF) | Multiple templates |
| `version` | Version display | Multiple templates |
| `page-info` | Page information area | Multiple templates |
| `small` / `x-small` | Size variants | Multiple templates |
| `bold-text` / `normal-text` | Text weight variants | Multiple templates |
| `indented` | Left-indented content | Multiple templates |
| `part` / `parts` | Party section containers | Multiple templates |
| `related-box` / `info-box` | Information boxes | Multiple templates |
| `inline-flex` | Inline flex display for btn labels | "Kjøpekontrakt FORBRUKER" |

### Custom CSS ID scoping in templates

Some templates use custom element IDs for CSS scoping beyond `#vitecTemplate`:

| ID | Used in | Purpose |
|----|---------|---------|
| `#vitecTemplate` | All templates | Main CSS scope (required) |
| `#vitecHeader` | Custom headers | Inner wrapper for header-specific CSS |
| `#bunntekstTabell` | Footer templates (Oppdragsavtale, custom) | Footer table styling (height, padding, font-size) |
| `#Avsender` | Avsender resource template | Sender block styling (padding-left: 0) |
| `#Mottaker` | Mottaker resource template | Recipient block styling (padding-left: 0) |
| `#vitec-stilark` | Vitec Stilark injection | `display:inline` wrapper for injected CSS (system-generated, not user-created) |

### Google Fonts loading

Self-contained templates (legal footers, custom headers) load fonts via `@import url()`:

```css
@import url('https://fonts.googleapis.com/css2?family=Open+Sans:wght@300;400;700&display=swap');
```

Also seen in Proaktiv custom templates:
```css
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Open+Sans:wght@400&display=swap');
```

This is used when the template does NOT include the Stilark (which normally provides the base font). The `@import` must appear at the very start of the `<style>` block.

### CSS reset pattern (self-contained templates)

Legal footers and some headers include a full CSS reset:

```css
html, body { margin: 0; padding: 0; }
#vitecTemplate * { font-variant-ligatures: none; }
```

This is only needed when the template does NOT use the Stilark. Do not add this to templates that include `<span vitec-template="resource:Vitec Stilark">` — the Stilark already handles these resets.

### CSS properties to avoid

- `font-variant-ligatures` — Already set by Stilark; do not override
- `font-family` — Already set by Stilark; redundant inline (exception: self-contained templates that don't use Stilark, and email signatures using Calibri)
- `font-size` — Only override when specifically needed (e.g. footer `8pt`)
- Media queries — Not supported in PDF rendering context
- CSS variables — No evidence of usage; avoid
- `!important` — Only used in SVG toggle styles; avoid in template content

---

## 8. SVG, Images, and Media

### Base64 SVG checkbox/radio pattern

Vitec templates implement interactive checkboxes and radio buttons using SVG images referenced via CSS `background-image` with inline SVG data URIs:

#### Checkbox (unchecked)
```css
background-image: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 512 512'><rect style='fill:black;' height='496' width='496' x='9.1' y='9.1'></rect><rect style='fill:white;' height='400' width='400' x='57.1' y='60.6'></rect></svg>");
```

#### Checkbox (checked)
Same as above plus a checkmark path:
```css
<path style='fill:black;' d='M396.1,189.9L223.5,361.1c-4.7,4.7-12.3,4.6-17-0.1l-90.8-91.5...'/>
```

#### Radio button (unchecked)
```css
background-image: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 512 512'><circle style='fill:black;' cx='257.1' cy='257.1' r='248'></circle><circle style='fill:white;' cx='257.1' cy='257.1' r='200'></circle></svg>");
```

#### Radio button (selected)
Same as above plus an inner filled circle.

**Usage pattern:**
```html
<label class="btn" contenteditable="false" data-toggle="button">
  <span class="checkbox svg-toggle"></span>
</label>
```

```html
<label class="btn" contenteditable="false" data-toggle="button">
  <span class="radio svg-toggle"></span>
  <input name="rbl01" type="radio" />Ja
</label>
```

**Evidence:** Lines 207–272 (CSS), lines 6175–6210 (HTML usage).

The `<input>` elements inside are hidden (`display: none` via CSS at line 269) — they exist only for semantic grouping via `name` attribute. The visual toggle is handled entirely by the SVG background images on `.svg-toggle`.

#### Large SVG toggle variant

A `.large` modifier class doubles the toggle size to 24×24px:

```css
.svg-toggle.large {
    width: 24px;
    height: 24px;
    background-size: 24px 24px;
}
```

Usage: `<span class="checkbox large svg-toggle"></span>`

**(DB evidence: "Akseptbrev kjøper uten oppgjørsskjema (e-post)")**

#### Inline toggle pattern (without checkbox-table)

Contracts use SVG toggles inline within `<p>` elements via `data-toggle="buttons"` on the paragraph. Radio buttons share a `name` attribute to form a mutually-exclusive group:

```html
<p data-toggle="buttons">
  <label class="btn" contenteditable="false" data-toggle="button">
    <span class="checkbox svg-toggle"></span>
    <input name="rbl001" type="radio" />
  </label>
  <span vitec-if="Model.kjopere.Count == 1">Jeg </span>
  <span vitec-if="Model.kjopere.Count &gt; 1">Vi </span>ønsker boligkjøperforsikring

  &nbsp;&nbsp;&nbsp;

  <label class="btn" contenteditable="false" data-toggle="button">
    <span class="checkbox svg-toggle"></span>
    <input name="rbl001" type="radio" />
  </label>
  <span vitec-if="Model.kjopere.Count == 1">Jeg </span>
  <span vitec-if="Model.kjopere.Count &gt; 1">Vi </span>ønsker ikke boligkjøperforsikring
</p>
```

Key details:
- `data-toggle="buttons"` on the `<p>` wrapper enables Bootstrap toggle behavior
- `data-toggle="button"` on each `<label>` makes it individually toggleable
- `input[type="radio"]` elements are hidden via CSS (`display: none`) in PDF output
- `name="rbl001"` groups the radio buttons (only one active at a time)
- `contenteditable="false"` on labels prevents CKEditor from modifying the toggle structure

CSS for hiding radio inputs in PDF:
```css
#vitecTemplate [data-toggle="buttons"] input {
    display: none;
}
```

**(Evidence: Kjøpekontrakt FORBRUKER — both DB and custom versions)**

### Image embedding conventions

#### Merge field images

```html
<img alt="" src="@Model.ansvarligmegler.hovedbilde" />
<img alt="" src="[[meglerkontor.firmalogourl]]" style="max-height:1.5cm; max-width:6cm" />
```

Both `@Model.` and `[[...]]` syntax work for image sources.

#### Figure/figcaption pattern

```html
<figure>
  <figcaption>ansvarligmegler.hovedbilde</figcaption>
  <img alt="" src="@Model.ansvarligmegler.hovedbilde" />
</figure>
```

CSS rules:
```css
#vitecTemplate figure {
    text-align: center;
    display: inline-block;
}
#vitecTemplate figure img:not(.scaled-image) {
    max-width: 3cm;
    max-height: 3cm;
}
#vitecTemplate figure figcaption {
    font-size: smaller;
    display: block;
}
```

**Evidence:** Lines 47–60 (CSS), lines 6241–6292 (HTML).

#### Scaled/circular image

```html
<img alt="Eiendommens bilde" class="scaled-image" src="$.SKALER(@Model.eiendom.hovedbilde, h=100)" />
```

CSS:
```css
#vitecTemplate .scaled-image {
    width: 100px;
    height: 100px;
    object-fit: cover;
    object-position: center center;
    border-radius: 50%;
}
```

**Evidence:** Lines 62–68 (CSS), line 6292 (HTML). The `$.SKALER()` function generates a server-side scaled version of the image.

#### QR code generation

```html
<img alt="QR code" src="https://api.qrserver.com/v1/create-qr-code/?size=80x80&amp;data=@Model.oppdrag.estateid;@Model.oppdrag.installationId;Dokumentnavn;Dokumenttype&amp;format=svg" />
```

**Evidence:** Line 6280. Uses an external API with Razor model values embedded in the URL.

### Available image merge fields

| Field | Content |
|-------|---------|
| `@Model.ansvarligmegler.hovedbilde` | Agent profile photo |
| `@Model.ansvarligmegler.signatur` | Agent signature image |
| `@Model.megler1.hovedbilde` | Co-agent photo |
| `@Model.megler1.signatur` | Co-agent signature |
| `@Model.avsender.bilde` | Sender photo |
| `@Model.avsender.signatur` | Sender signature |
| `@Model.avsender.firmalogourl` | Company logo |
| `@Model.meglerkontor.firmalogourl` | Office logo |
| `@Model.eiendom.hovedbilde` | Property main photo |
| `@Model.oppdrag.prosjekt.logo` | Project logo |

---

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

## 10. Property Type Conditional Patterns

These patterns use `vitec-if` to branch content based on property type, ownership form, and assignment type. They are the foundation for template merging work.

### Ownership form (eieform) branching

```html
<span vitec-if="Model.eiendom.eieform == &quot;Andel&quot;">andel i borettslag</span>
<span vitec-if="Model.eiendom.eieform != &quot;Andel&quot;">fast eiendom</span>
```

Known eieform values: `Andel`, `Eiet`, `Aksje`, `Obligasjon`, `Eierseksjon`.

**Evidence:** `vitec-reference.md` lines 868–869 (Sikring footer).

### Sale vs rental branching

```html
<span vitec-if="!Model.oppdrag.type.Contains(&quot;tleie&quot;)">Selger</span>
<span vitec-if="Model.oppdrag.type.Contains(&quot;tleie&quot;)">Utleier</span>
```

The string `"tleie"` (a substring of "Utleie") is used as the discriminator.

| Condition | Assignment type |
|-----------|----------------|
| Contains "tleie" | Rental (Utleie) |
| Does NOT contain "tleie" | Sale (Salg) |

**Evidence:** `vitec-reference.md` lines 735–746 (Kontrakt footer).

### Assignment category branching

```html
<span vitec-if="Model.oppdrag.hovedtype == &quot;Oppgj\xF8rsoppdrag&quot;">Ja</span>
<span vitec-if="Model.oppdrag.hovedtype != &quot;Oppgj\xF8rsoppdrag&quot;">Nei</span>
```

Note the `\xF8` escape for `ø`.

**Evidence:** Line 6418.

### Property base type branching

```html
<span vitec-if="Model.eiendom.grunntype == &quot;N\xE6ring&quot;">Ja</span>
<span vitec-if="Model.eiendom.grunntype != &quot;N\xE6ring&quot;">Nei</span>
```

Known grunntype values: `bolig`, `fritid`, `tomt`, `Næring` (note: `\xE6` escape needed for æ).

**Evidence:** Line 6408.

### Output channel branching

```html
<tr vitec-if="Model.dokumentoutput == &quot;pdf&quot;">
  <!-- PDF-specific content -->
</tr>
<tr vitec-if="Model.dokumentoutput == &quot;email&quot;">
  <!-- Email-specific content -->
</tr>
```

**Evidence:** Lines 6160–6167. The `dokumentoutput` field determines whether the template is being rendered for PDF (document creation) or email (send-as-email flow).

### Boolean property flags

```html
<span vitec-if="Model.oppdrag.vederlagtypeprovisjon == true">JA</span>
<span vitec-if="Model.oppdrag.vederlagtypeprovisjon == false">NEI</span>
```

Other boolean flags observed:
- `Model.oppdrag.vederlagtypetimepris`
- `Model.oppdrag.vederlagtypefastpris`
- `Model.oppdrag.boligselgerforsikringbestilt` (DB evidence: "Oppdragsavtale")
- `Model.oppdrag.erdetforkjopsfrist` (DB evidence: multiple)
- `Model.kjoper.erfirma` / `Model.selger.erfirma`
- `Model.kjoper.fullmektig.erfirma`
- `Model.megler2.erstudent`
- `Model.medhjelper.erstudent`
- `Model.eiendom.erprosjektmaster`
- `Model.kjoper.fullmektig_er_gruppe`
- `Model.pant.ertypefrivilligpant` (DB evidence: "Pantedokument (sikring)")
- `Model.pant.ertypelegalpant` (DB evidence: "Pantedokument (sikring)")
- `selger.ergift` — implicit boolean on loop variable (DB evidence: "Hjemmelserklæring")

**Evidence:** Lines 2482–2652 (fee type branching), 1649 (company flag), 952/991 (student flag).

### Razor `@{}` code blocks for dynamic CSS classes

Complex templates use Razor C# code blocks to compute CSS class values at render time. This is a server-side pattern distinct from `vitec-if`:

```html
@{
    var erGrunntypeBolig = "";
    var erGrunntypeFritid = "";
    var erGrunntypeNaering = "";
    var erGrunntypeTomt = "";
    if (Model.eiendom.grunntype == "Bolig") {
        erGrunntypeBolig = "active";
    }
    if (Model.eiendom.grunntype == "Fritid") {
        erGrunntypeFritid = "active";
    }
    // ... etc
}

<label class="btn @erGrunntypeBolig" contenteditable="false" data-toggle="button">
  <span class="checkbox svg-toggle"></span> Bolig
</label>
<label class="btn @erGrunntypeFritid" contenteditable="false" data-toggle="button">
  <span class="checkbox svg-toggle"></span> Fritid
</label>
```

When the Razor variable is `"active"`, the label gets `class="btn active"` which triggers the checked SVG toggle state. When empty, it stays as `class="btn "` (unchecked).

Known Razor class variables:

| Variable | Condition field | Templates |
|----------|----------------|-----------|
| `@erGrunntypeBolig` | `Model.eiendom.grunntype == "Bolig"` | "Hjemmelsoverføring" |
| `@erGrunntypeFritid` | `Model.eiendom.grunntype == "Fritid"` | "Hjemmelsoverføring" |
| `@erGrunntypeNaering` | `Model.eiendom.grunntype == "Næring"` | "Hjemmelsoverføring" |
| `@erGrunntypeTomt` | `Model.eiendom.grunntype == "Tomt"` | "Hjemmelsoverføring" |
| `@erTomtetypeEiertomt` | `Model.eiendom.tomtetype == "eiertomt"` | "Hjemmelserklæring", "Skjøte" |
| `@erTomtetypeFestetomt` | `Model.eiendom.tomtetype == "festetomt"` | "Hjemmelserklæring", "Skjøte" |
| `@erHovedtypeSalg` | `Model.eiendom.grunntype == "Salg"` | "Kundeopplysningsskjema kjøper/selger" |
| `@erHovedtypeProsjektsalg` | Prosjektsalg type | "Kundeopplysningsskjema" |
| `@erHovedtypeUtleie` | Utleie type | "Kundeopplysningsskjema" |
| `@erHovedtypeOppgjorsOppdrag` | Oppgjørsoppdrag type | "Kundeopplysningsskjema" |
| `@erHovedtypeVerdivurdering` | Verdivurdering type | "Kundeopplysningsskjema" |
| `@erSalg` / `@erKjop` / `@erUtleie` | Assignment type | "Oppdragsavtale" |
| `@erOppgjorsoppdrag` | Oppgjørsoppdrag type | "Oppdragsavtale" |
| `@erTvangssalg` / `@erIkkeTvangssalg` | Forced sale flag | Multiple |
| `@erIkkeOppgjorsOppdrag` | Not oppgjørsoppdrag | Multiple |
| `@erTypeGrunnBoligeiendom` | `Model.eiendom.typegrunn == "Boligeiendom"` | "Skjøte" (Kartverket code **B**) |
| `@erTypeGrunnFritidseiendom` | `Model.eiendom.typegrunn == "Fritidseiendom"` | "Skjøte" (Kartverket code **F**) |
| `@erTypeGrunnForretningKontor` | `Model.eiendom.typegrunn == "Forretning - kontor"` | "Skjøte" (Kartverket code **V**) |
| `@erTypeGrunnIndustriBergverk` | `Model.eiendom.typegrunn == "Industri - bergverk"` | "Skjøte" (Kartverket code **I**) |
| `@erTypeGrunnLandbrukFiske` | `Model.eiendom.typegrunn == "Landbruk - fiske"` | "Skjøte" (Kartverket code **L**) |
| `@erTypeGrunnOffentligVei` | `Model.eiendom.typegrunn == "Offentlig vei"` | "Skjøte" (Kartverket code **K**) |
| `@erTypeGrunnAnnet` | `Model.eiendom.typegrunn == "Annet"` | "Skjøte" (Kartverket code **A**) |
| `@erTypeBoligFrittliggendeEnebolig` | `Model.eiendom.typebolig == "Frittliggende enebolig"` | "Skjøte" (Kartverket code **FB**) |
| `@erTypeBoligTomannsbolig` | `Model.eiendom.typebolig == "Tomannsbolig"` | "Skjøte" (Kartverket code **TB**) |
| `@erTypeBoligRekkehusKjede` | `Model.eiendom.typebolig == "Rekkehus/Kjede"` | "Skjøte" (Kartverket code **RK**) |
| `@erTypeBoligBlokkleilighet` | `Model.eiendom.typebolig == "Blokkleilighet"` | "Skjøte" (Kartverket code **BL**) |
| `@erTypeBoligAnnet` | `Model.eiendom.typebolig == "Annet"` | "Skjøte" (Kartverket code **AN**) |

**(DB evidence: "Hjemmelsoverføring", "Hjemmelserklæring", "Kundeopplysningsskjema kjøper", "Kundeopplysningsskjema selger", "Oppdragsavtale", "Skjøte")**

### ID number type detection (personal vs. organization)

```html
<span vitec-if="kjoper.idnummer.ToString().Length == 11">
  <!-- Personal ID (fødselsnummer: 11 digits) -->
</span>
<span vitec-if="kjoper.idnummer.ToString().Length == 12">
  <!-- Organization number (12 digits with dash) -->
</span>
```

Uses `.ToString().Length` to distinguish between personal ID numbers (11 digits) and organization numbers (12 digits). Also used for `Model.selger.idnummer.ToString().Length`.

**(DB evidence: "Egenerklæring om konsesjonsfrihet", "Oppdragsavtale")**

### Count-based branching

```html
<em vitec-if="Model.selgere.Count == 0">Ingen registrert</em>
<table vitec-if="Model.selgere.Count &gt; 0">
  <!-- content -->
</table>
```

### String value branching

```html
<span vitec-if="Model.mottaker.visning.dato != &quot;Mangler data&quot;">
  [[mottaker.visning.dato]] [[mottaker.visning.tidsrom]]
</span>
<span vitec-if="Model.mottaker.visning.dato == &quot;Mangler data&quot;">
  Ingen visning registrert på mottakeren.
</span>
```

**Evidence:** Lines 2332–2333. The string `"Mangler data"` is Vitec's placeholder for missing data.

### Numeric comparison with negated greater-than

For "less than or equal" comparisons, Vitec uses negated `>`:

```html
<span vitec-if="!(Model.oppdrag.prosjektenhet.antallgarasjeplasser &gt; 4)">3 or fewer</span>
<span vitec-if="Model.oppdrag.prosjektenhet.antallgarasjeplasser &gt; 3">More than 3</span>
```

**Evidence:** Lines 6469–6470.

---

## 11. Known Failure Modes

### 1. Unescaped quotes in vitec-if values

**Symptom:** Conditional never matches, or HTML structure breaks.

**Cause:** Using `"` instead of `&quot;` inside attribute values:
```html
<!-- BROKEN -->
<span vitec-if="Model.eiendom.eieform == "Andel"">text</span>
```

**Fix:** Always use `&quot;`:
```html
<span vitec-if="Model.eiendom.eieform == &quot;Andel&quot;">text</span>
```

### 2. Unescaped `>` in numeric comparisons

**Symptom:** HTML parser interprets `>` as end of attribute/tag. Everything after the `>` renders as plain text or is lost.

**Cause:** Using `>` instead of `&gt;`:
```html
<!-- BROKEN -->
<table vitec-if="Model.kjopere.Count > 0">
```

**Fix:**
```html
<table vitec-if="Model.kjopere.Count &gt; 0">
```

### 3. Norwegian characters in comparisons without \x escaping

**Symptom:** Conditional never matches even when the data contains the expected Norwegian word.

**Cause:** Using literal æ/ø/å in vitec-if expressions:
```html
<!-- MAY NOT MATCH -->
<span vitec-if="Model.eiendom.grunntype == &quot;Næring&quot;">
```

**Fix:** Use `\x` escape sequences:
```html
<span vitec-if="Model.eiendom.grunntype == &quot;N\xE6ring&quot;">
```

### 4. Missing `&nbsp;` in Stilark resource reference

**Symptom:** Stilark CSS not loaded; template renders without styling.

**Cause:** Empty resource span:
```html
<!-- BROKEN -->
<span vitec-template="resource:Vitec Stilark"></span>
```

**Fix:** Must contain `&nbsp;`:
```html
<span vitec-template="resource:Vitec Stilark">&nbsp;</span>
```

### 5. Missing `#vitecTemplate` wrapper

**Symptom:** No Stilark CSS selectors match. Template renders with browser defaults (Times New Roman, etc.).

**Cause:** Content not wrapped in `<div id="vitecTemplate">`.

**Fix:** Always wrap content in the required shell (see Section 1).

### 6. Lambda arrow in foreach filter not HTML-escaped

**Symptom:** `.Where()` filter does not work; may cause render error.

**Cause:** Using `=>` instead of `=&gt;`:
```html
<!-- BROKEN -->
<tbody vitec-foreach="x in Model.list.Where(i => i.code == &quot;X&quot;)">
```

**Fix:**
```html
<tbody vitec-foreach="x in Model.list.Where(i =&gt; i.code == &quot;X&quot;)">
```

### 7. Inline font/color styles fighting Stilark

**Symptom:** Text appears in wrong font or colour; inconsistent rendering across templates.

**Cause:** Inline `font-family`, `font-size`, `color` styles override Stilark. When templates are mixed (e.g., pasted from Word), some elements have inline styles and others don't.

**Fix:** Strip all non-structural inline styles. Use the sanitizer's `PRESERVE_STYLES` list as the reference for what to keep.

### 8. CKEditor stripping custom attributes after re-editing

**Symptom:** `vitec-if` or `vitec-foreach` attributes disappear after saving in CKEditor.

**Cause:** CKEditor's ACF was not configured to allow these attributes, or the configuration was changed between editing sessions.

**Mitigation:** Always verify `vitec-if` and `vitec-foreach` attributes are present after any CKEditor editing session. Vitec's CKEditor configuration should include:
```javascript
extraAllowedContent: '*[vitec-if,vitec-foreach,vitec-template,data-label,data-version,data-toggle,contenteditable]'
```

### 9. `<table>` with direct `<tr>` children (no `<tbody>`)

**Symptom:** CKEditor may restructure the table by adding implicit `<tbody>`.

**Cause:** Browsers and CKEditor both auto-insert `<tbody>` around `<tr>` elements that are direct children of `<table>`. This can break vitec-foreach if the foreach was placed on an element that gets wrapped.

**Fix:** Always explicitly include `<tbody>` in table structures.

### 10. Missing `proaktiv-theme` class on wrapper div

**Symptom:** Company-specific CSS overrides do not apply. Template may render with slightly different styling.

**Cause:** Using only `id="vitecTemplate"` without `class="proaktiv-theme"`:
```html
<!-- INCOMPLETE -->
<div id="vitecTemplate">
```

**Fix:** Always include both:
```html
<div class="proaktiv-theme" id="vitecTemplate">
```

**(DB evidence: All 133 templates use this pattern)**

### 11. `&&` not escaped in HTML attributes

**Symptom:** Logical AND in vitec-if or Where lambda does not work; expression may be truncated.

**Cause:** Using `&&` instead of `&amp;&amp;` inside HTML attributes:
```html
<!-- BROKEN -->
<span vitec-if="Model.a == true && Model.b == false">
```

**Fix:**
```html
<span vitec-if="Model.a == true &amp;&amp; Model.b == false">
```

**(DB evidence: 23 templates use `&amp;&amp;` including "Kjøpekontrakt FORBRUKER", "Oppdragsavtale")**

### 12. `counters()` CSS function breaks in Chromium PDF renderer

**Symptom:** Auto-numbered contract sections (h2/h3) display wrong numbers — subsections restart at unexpected points, or all sections show "1." regardless of nesting depth.

**Cause:** The default Vitec template uses:
```css
#vitecTemplate .item { counter-increment: item; }
#vitecTemplate .item h2:before,
#vitecTemplate .item h3:before { content: counters(item, ".") ". "; }
```
The `counters()` function relies on CSS counter scope inheritance, which Chromium-based PDF renderers handle incorrectly when `counter-reset` and `counter-increment` interact across nested `article.item` elements.

**Fix:** Replace with two explicit counters and `:not()` selectors:
```css
#vitecTemplate { counter-reset: section; }
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
```

**(Evidence: Proaktiv custom Kjøpekontrakt FORBRUKER — production fix)**

### 13. `@media` in CSS inside Razor-processed templates

**Symptom:** CSS `@media print` block is silently eaten or causes Razor compilation error. Print styles don't work.

**Cause:** The `@` symbol in `@media` is intercepted by Vitec's Razor engine as a code directive.

**Fix:** Escape `@` using Razor's `@("@")` syntax:
```css
/* BROKEN — Razor interprets @media as code */
@media print { .screen-help { display: none; } }

/* FIXED — Razor outputs literal @ */
@("@")media print { .screen-help { display: none; } }
```

**(Evidence: Kjøpekontrakt Næring production template)**

---

## 12. Conversion Checklist

This checklist is for the Word-to-HTML Conversion Agent (Agent 2). Follow each step mechanically. All rules referenced below are defined in this document.

### A. Template Shell

- [ ] Content is wrapped in `<div class="proaktiv-theme" id="vitecTemplate">...</div>` (both class and id required)
- [ ] `<span vitec-template="resource:Vitec Stilark">&nbsp;</span>` is present as the first child of the wrapper div
- [ ] The resource span contains `&nbsp;` (not empty)

### B. Table Structure

- [ ] All layout uses `<table>` elements (not CSS flexbox/grid)
- [ ] Outer table has `style="width:21cm; table-layout:fixed"` for A4 templates
- [ ] All `<tr>` elements are inside `<tbody>`, `<thead>`, or `<tfoot>` (never directly inside `<table>`)
- [ ] Column spans use the 100-unit system (e.g. `colspan="30"` + `colspan="70"` = 100)
- [ ] Nested tables inside `<td>` cells have `style="table-layout:fixed; width:100%"`
- [ ] No `<table>` elements are self-closing or empty

### C. Inline Styles

- [ ] No `font-family` in inline styles (Stilark handles this)
- [ ] No `font-size` in inline styles unless intentionally overriding (e.g. footer at `8pt`)
- [ ] No `color` or `background-color` in inline styles unless specifically required
- [ ] Preserved structural styles only: `width`, `height`, `margin`, `padding`, `border`, `text-align`, `vertical-align`, `display`, `float`, `table-layout`, `position`, `page-break-*`
- [ ] All dimensions use `cm` units for print measurements (not `px`, `em`, `rem`)

### D. Merge Fields

- [ ] All merge fields use `[[field.path]]` syntax with double square brackets
- [ ] Required fields use `[[*field.path]]` with asterisk prefix
- [ ] Field paths match documented paths in `.cursor/vitec-reference.md`
- [ ] Image sources use `@Model.field` or `[[field]]` syntax in `src` attribute
- [ ] No spaces inside brackets: `[[field.name]]` not `[[ field.name ]]`

### E. Conditional Logic (vitec-if)

- [ ] All string values in comparisons use `&quot;` for quotes
- [ ] All `>` comparisons use `&gt;` HTML entity
- [ ] All `<` comparisons use `&lt;` HTML entity
- [ ] All `&&` logical AND uses `&amp;&amp;`
- [ ] Lambda arrows in `.Where()` and `.Any()` use `=&gt;`
- [ ] Norwegian characters (æ, ø, å) in comparisons use `\x` escapes (`\xE6`, `\xF8`, `\xE5`, `\xC6`, `\xD8`, `\xC5`)
- [ ] Top-level expressions reference `Model.` prefix; loop variable expressions omit it (e.g. `selger.ergift`)
- [ ] `vitec-if` is placed on an appropriate container element (`<span>`, `<em>`, `<p>`, `<div>`, `<tr>`, `<tbody>`, `<table>`, `<article>`, `<li>`)

### F. Iteration (vitec-foreach)

- [ ] Foreach uses `<tbody>` as container for table rows
- [ ] Loop variable name is descriptive and consistent
- [ ] Inner merge fields reference the loop variable (e.g. `[[*selger.navn]]`), not `Model.`
- [ ] Collection guards present: `vitec-if="Model.collection.Count &gt; 0"` before foreach
- [ ] Empty state message present: `vitec-if="Model.collection.Count == 0"` with "Ingen registrert" or similar
- [ ] Nested foreach correctly references parent loop variable for sub-collections

### G. Images and SVG

- [ ] All `<img>` elements have `alt` attribute (even if empty: `alt=""`)
- [ ] Logo images have `max-height` and `max-width` constraints
- [ ] SVG checkboxes/radios use the documented `.svg-toggle` CSS class pattern
- [ ] `<figure>` and `<figcaption>` used for captioned images
- [ ] No inline base64 images larger than necessary (use `$.SKALER()` for scaled versions)

### H. Form Elements

- [ ] `data-label` on `<td>` elements has corresponding CSS for `::before` pseudo-element
- [ ] `data-choice` on `<td>` elements has corresponding CSS for `::after` pseudo-element (if used)
- [ ] Combined `data-label` + `data-choice` cells have appropriate padding (16px top and bottom)
- [ ] `contenteditable="false"` used on non-editable rows (form numbers, static text)
- [ ] `span.insert` elements have `data-label` attribute with placeholder text
- [ ] Form tables use `class="form-table"` for bordered layout
- [ ] Checkbox layouts use `class="checkbox-table"` (not `form-table`)

### I. Text and Formatting

- [ ] No `<font>` tags (unwrap to plain content)
- [ ] No `<center>` tags (use `text-align: center` instead)
- [ ] `<strong>` for bold, `<em>` for italic (not inline `font-weight`/`font-style`)
- [ ] `<small>` for reduced text (e.g. footnotes, form numbers)
- [ ] `&nbsp;` used for intentional non-breaking spaces (not as content filler)
- [ ] Norwegian characters preserved as HTML entities where needed (`&aelig;`, `&oslash;`, `&aring;`)

### J. Contract-Specific (Kjøpekontrakt, Oppdragsavtale)

- [ ] Uses `<article class="item">` for auto-numbered sections (not `<div>`)
- [ ] CSS counters use the **Chromium-safe** dual-counter pattern (`section`/`subsection`), NOT `counters(item, ".")`
- [ ] Top-level `<article class="item">` contains `<h2>` (numbered "1. ", "2. ", ...)
- [ ] Nested `<article class="item">` contains `<h3>` (numbered "1.1. ", "1.2. ", ...)
- [ ] `<article>` has `padding-left: 20px`; nested `<article article>` has `padding-left: 0`
- [ ] Eieform-conditional sections use `vitec-if` directly on `<article>` or `<div>`
- [ ] Internal cross-references use `<a id="section-name"></a>` anchors + `<a class="bookmark" href="#section-name">` links
- [ ] `roles-table` class on party-listing tables with `tbody:last-child tr:last-child td { display: none }` CSS
- [ ] Inline toggles (boligkjøperforsikring) use `<p data-toggle="buttons">` with `<label class="btn">` containing SVG toggles
- [ ] Signature block uses nested `vitec-foreach` inside `<td>` with `border-bottom: solid 1px #000000; height: 40px` for signing lines
- [ ] `span.insert` placeholders used for dates and amounts that the user fills in manually
- [ ] `.avoid-page-break` class applied to sections that must not split across pages

### K. Final Validation

- [ ] **FIRST: Verify this is NOT a protected Kartverket template (Section 14) — if it is, DO NOT proceed with any changes**
- [ ] HTML is well-formed (all tags properly closed)
- [ ] No JavaScript event handlers (`onclick`, `onload`, etc.)
- [ ] No external stylesheet links (only Stilark resource reference)
- [ ] Template renders correctly when Stilark CSS is applied
- [ ] All `vitec-if` expressions are syntactically valid (test with simple true/false)
- [ ] All `vitec-foreach` collections are listed in the known collections table (Section 4)

---

## 13. Vitec Next Template Admin Interface

This section documents the built-in system features of the Vitec Next template editor and management interface, based on screenshots of the production admin UI.

### CKEditor toolbar

Templates are edited using CKEditor 4 with the following toolbar:

| Button/Group | Function |
|-------------|----------|
| **Testfletting** | Test merge — renders the template with sample data to preview the output |
| **Normal (...)** | Paragraph style dropdown (Normal, Heading 1–5, etc.) |
| **Skrift** | Font family dropdown |
| **Størrelse** | Font size dropdown |
| **B I U S T** | Bold, Italic, Underline, Strikethrough, and text formatting |
| List buttons | Ordered and unordered lists |
| Indent buttons | Increase/decrease indent |
| Alignment | Left, Center, Right, Justify |
| **Q** (magnifier) | Find/Replace |
| **A** / **A** (colored) | Text color / Background color pickers |
| Table icon | Insert/edit tables |
| Link/Unlink | Insert/remove hyperlinks |
| **[P]** | Insert page break |
| **[d]** | Insert merge field / data field |
| **Kilde** | Source view — switch to raw HTML editing mode |

The editor shows the current template name at the bottom: `Dokumentmal: [Template Name]`.

**Key workflow:** Editors typically work in the visual WYSIWYG view. The "Kilde" (Source) button switches to raw HTML where `vitec-if`, `vitec-foreach`, and merge fields can be edited directly. "Testfletting" previews how the template will look with real data.

### Template categorization settings

Each template has a "Kategorisering" (Categorization) panel with the following configurable fields:

#### Core metadata

| Field | Norwegian label | Description | Example |
|-------|----------------|-------------|---------|
| Template type | MALTYPE | `Objekt/Kontakt` (document) or `System` (system template) | `Objekt/Kontakt` |
| Objects | OBJEKTER | Link to specific property/contact objects | `Finn objekt` (search) |
| Template name | MALNAVN | Display name of the template | `Kjøpekontrakt Bruktbolig` |
| Receiver type | MOTTAKERTYPE | Who receives this document | `Systemstandard` |
| Receiver | MOTTAKER | Specific receiver selection | `Ingen valgt` |
| Extra receivers | EKSTRA MOTTAKERE | Additional receivers | `Ingen valgt` |

#### Filtering and classification

| Field | Norwegian label | Description | Example |
|-------|----------------|-------------|---------|
| Access restrictions | FILTRERING | Restrict who can use this template | (configurable) |
| Channels | KANALER | Output channels | `PDF og e-post`, `Kun SMS`, `Kun e-post` |
| Category | KATEGORI | Document category | `Kontrakt`, `Oppdragsavtale`, `Akseptbrev kjøper`, etc. |
| Assignment category groups | OPPDRAGSKATEGORIGRUPPER | Which assignment categories this applies to | `Oppgjørsoppdrag (Bolig, Fritid, Tomt), Salg (Bolig, Fritid, Tomt)` |
| Assignment types | OPPDRAGSTYPER | Specific assignment types | `Oppgjørsoppdrag (Bolig, Fritid, Tomt), Salg (Bruktbolig, Fritid, Tomt)` |
| Depot journal groups | DEPOTJOURNALGRUPPER | Depot journal classification | `Ingen valgt` |
| Depot journal types | DEPOTJOURNALTYPER | Specific depot journal types | `Ingen valgt` |
| Phases | FASER | Which workflow phases | `Innsalg`, `Til salgs`, `Kontrakt`, `Oppgjør`, etc. |
| Ownership types | EIERFORMER | Property ownership filter | `Ingen valgt` (all) or specific types |
| Departments | AVDELINGER | Office/department filter | `Ingen valgt` (all) |

#### Email settings

| Field | Norwegian label | Description | Example |
|-------|----------------|-------------|---------|
| Subject | EMNE | Email subject line — supports merge fields! | `Kjøpekontrakt - [[oppdrag.nr]]` |

This confirms that `[[merge.fields]]` work in email subject lines, not just in template body content.

#### PDF settings — Header, footer, and margins

This is the critical section that controls how headers and footers are attached:

| Field | Norwegian label | Description | Example |
|-------|----------------|-------------|---------|
| Header template | TOPPTEKST | Dropdown to select header template (or "Ingen" = none) | `Ingen`, `Vitec Topptekst` |
| Footer template | BUNNTEKST | Dropdown to select footer template (or "Ingen" = none) | `Vitec Bunntekst Kontrakt` |

**Page margins** are configured per template with a visual A4 diagram:

| Margin | Norwegian label | Unit | Max | Example (Kjøpekontrakt) |
|--------|----------------|------|-----|------------------------|
| Top | TOPP | cm | 10 | `1,5` |
| Left | VENSTRE | cm | 10 | `1` |
| Right | HØYRE | cm | 10 | `1,2` |
| Bottom | BUNN | cm | 10 | `1` |

Note: "Angi marger i cm (eks. 2.25). Maksimalt 10 cm." — Margins are specified in cm with decimal values (Norwegian comma separator), maximum 10 cm.

**Example: Kjøpekontrakt Bruktbolig PDF settings:**
- Topptekst: **Ingen** (no header — the contract has its own header content)
- Bunntekst: **Vitec Bunntekst Kontrakt** (contract footer with signature lines)
- Margins: Top 1.5cm, Left 1cm, Right 1.2cm, Bottom 1cm

This confirms that the Kjøpekontrakt does NOT use a header template — the org number, assignment number, and title ("Kjøpekontrakt") at the top of the template are part of the body content itself.

### Template management sidebar

Each template has a "Dokumentmal" sidebar with:

| Section | Norwegian label | Description |
|---------|----------------|-------------|
| Categorization | Kategorisering | All metadata fields (expandable) |
| PDF attachments | PDF-vedlegg | Attach additional PDF documents to the template output |
| Copy as new | Kopier som ny mal | Duplicate the template as a starting point |
| History | Historikk | Version history of changes |
| Activate | AKTIVER MALEN | Toggle template active/inactive (green = active) |
| Delete | SLETT | Toggle to mark for deletion |
| Document concerns | DOKUMENTET OMHANDLER | What the document is about |
| Relations | VELG RELASJONER | Link to related templates |

### Template list view

The template list shows all templates with the following columns:

| Column | Norwegian | Description |
|--------|-----------|-------------|
| Template name | MALNAVN | Template display name |
| Type | TYPE | `Objekt/Kontakt` or `System` |
| Phase | FASE | Workflow phase(s) |
| Receiver | MOTTAKER | Receiver type |
| Category | KATEGORI | Document category |
| Header/Footer | TOPP/BUNN... | Cloud icons indicating header/footer assignment |
| Assignment type | OPPDRAGSTYPE | Assignment type filter |
| Depot journal | DEPO JOURNAL... | Journal classification |
| Posting code | POSTERINGSKOD... | Accounting code |
| Icons | IKONER | Status indicators (active, published, channels) |
| Departments | AVDELINGER | Department restrictions |
| Last modified | SIST ENDRET | Date and time of last edit |
| Modified by | ENDRET AV | User code who last edited |

Icon indicators visible in the list:
- Green checkmark — template is active/published
- Cloud icon — has header or footer assigned
- Email icon (@) — available for email channel
- Document icon — available for PDF channel

### Action menu (Utfør)

The gear icon "Utfør" menu provides:

| Action | Norwegian | Description |
|--------|-----------|-------------|
| New document template | Ny dokumentmal | Create a new HTML template from scratch |
| New Word template | Ny Word-mal | Create a Word document template |
| Select standard templates | Velg standardmaler | Import Vitec's default standard templates |
| Select function templates | Velg funksjonsmaler | Import function-specific templates (Saldoforespørsel, etc.) |
| Vitec templates | Vitecmaler | Browse all available Vitec system templates |
| Import template | Importer mal | Import a template from file |
| Filter | Filter | Open filter panel |
| View as cards | Vis som kort | Switch from list view to card view |

### Filter panel

The filter panel allows narrowing the template list:

| Filter | Norwegian | Options |
|--------|-----------|---------|
| Show inactive | VIS INAKTIVE MALER | Toggle — shows deactivated templates |
| System only | VIS KUN SYSTEMMALER | Toggle — filter to system templates only |
| Selection | UTVALG | `KUNDEMALER` (customer/custom) or `VITECMALER` (Vitec defaults) |
| Channel | KANAL | `KUN SMS` (SMS only) or `KUN E-POST` (email only) |
| Content search | INNHOLD | Free text search within template HTML content |

The "KUNDEMALER" vs "VITECMALER" distinction is important:
- **Vitecmaler** — Default templates provided by Vitec (cannot be modified directly, must be copied first)
- **Kundemaler** — Company-customized templates (copies of Vitecmaler or newly created)

### Confirmed from UI: Boligkjøperforsikring is a System template

The template list screenshot confirms that **Boligkjøperforsikring** is categorized as a `System` template type (last modified 16.02.2026). This is the support template containing the `@functions` block, referenced by the Kjøpekontrakt via `<span vitec-template="resource:Boligkjøperforsikring">`.

**(Evidence: Vitec Next admin UI screenshots from Proaktiv production environment, 2026-02-21)**

---

## 14. No-Touch Templates — Government Registration Forms (ABSOLUTE — DO NOT MODIFY)

> **LEGALLY BINDING RESTRICTION — NO EXCEPTIONS**
>
> The templates listed in this section are standardized government forms used for property registration (tinglysing), concession declarations, and sectioning applications. They are submitted to **Kartverket** (Norwegian Mapping Authority), **Landbruksdirektoratet** (Norwegian Agriculture Agency), and municipal authorities where they are **manually inspected** for compliance with the official form specifications.
>
> **ANY modification — including cosmetic changes, CSS adjustments, whitespace alterations, font changes, or structural edits — will cause the submission to be REJECTED.** Rejected forms delay property transfers and can have serious legal and financial consequences for buyers, sellers, and the brokerage.

### Rules for no-touch templates

1. **NEVER edit the HTML source code** of any template listed below — not a single character
2. **NEVER apply CSS changes** that could affect the rendered output of these forms
3. **NEVER modify their assigned header/footer templates** (Vitec Bunntekst Skjøte, Vitec Bunntekst Sikring)
4. **NEVER change page margins** configured for these templates in the PDF settings
5. **NEVER alter merge field references** — the field paths and formatting must match the government agency's expectations exactly
6. **NEVER "upgrade" or "modernize"** these templates when performing system-wide template updates
7. **NEVER include these templates** in batch conversion or migration operations
8. **Use "Kopier som ny mal" (Copy as new)** if you need to create a variant — never edit the original
9. **If Vitec releases an updated version** of these forms, adopt the new Vitec version as-is — do not manually merge changes

### Anti-pattern warning — do NOT reference these templates for new development

> **IMPORTANT:** These government forms were **converted to work within Vitec Next** — they were not built natively for the platform. As a result, they contain patterns, CSS approaches, and structural workarounds that are **NOT considered best practice** from a Vitec Next template development standpoint.
>
> Examples of patterns found in these forms that should **NOT** be replicated in new templates:
> - Self-contained CSS with `@import url()` instead of using `<span vitec-template="resource:Vitec Stilark">`
> - Missing `class="proaktiv-theme"` on the root div
> - Hardcoded page numbers ("Side 1 av 2") instead of `[[p]]` / `[[P]]` merge fields
> - Direct array indexing (`@Model.selgere[0].navn`) instead of `vitec-foreach`
> - Hidden merge fields (`<span style="display:none!important">[[field]]</span>`) to force data loading
> - Font family overrides (Arial, Calibri) that bypass the Vitec Stilark
> - Fixed A4 height simulation (`td.a4-main { height: 27.5cm }`)
>
> **For best practices when building new templates, follow Sections 1–12 of this document.**

### Tier 1: Core government registration forms (NO TOUCH)

These are legal documents submitted to government agencies (Kartverket, Landbruksdirektoratet, Kommunal- og moderniseringsdepartementet) for property registration, concession declarations, and sectioning. They use agency-specific form numbers, layout specifications, and are subject to manual review.

| Template name | Size | Agency | Form ref | Notes |
|--------------|------|--------|----------|-------|
| **Skjøte** | 43K | Kartverket | GA-5400 B (footer) | Title deed — primary property transfer document |
| **Hjemmelsoverføring** | 23K | Kartverket | GA-5400 B | Title transfer (borettslag cooperative shares) |
| **Pantedokument (sikring)** | 25K | Kartverket | Statens kartverk rev 01/19 | Mortgage/security document |
| **Hjemmelserklæring** | 28K | Kartverket | — | Title declaration (inheritance, gift, estate division) |
| **Seksjoneringsbegjæring** | ~40K | Kommunaldept. | KMD form | Sectioning application (4-page municipal form) |
| **Egenerklæring om konsesjonsfrihet (Grønt skjema)** | 66K | Landbruksdirektoratet | LDIR-360 B | Self-declaration: no concession required |
| **Egenerklæring om konsesjonsfrihet (Rødt skjema)** | 60K | Landbruksdirektoratet | LDIR-356 B | Self-declaration: reduced concession threshold |
| **Søknad om konsesjon (Blått skjema)** | 58K | Landbruksdirektoratet | LDIR-359 B | Application for concession (agricultural/forestry) |
| **Begjæring om utstedelse av skjøte/hjemmelsdokument (Tvangssalg)** | 5K | Kartverket | — | Title document issuance request (forced sale) |

### Tier 2: System footers for Kartverket forms (STRICTLY PROTECTED)

These system footers contain Kartverket form numbers and "Statens kartverk" references. They are paired with the Tier 1 forms and must not be modified.

| Template name | Size | Form reference | Paired with |
|--------------|------|----------------|-------------|
| **Vitec Bunntekst Skjøte** | 594 | GA-5400 B | Skjøte, Hjemmelsoverføring |
| **Vitec Bunntekst Sikring** | 773 | Statens kartverk — rev 01/19 | Pantedokument (sikring) |

### Tier 3: Tinglysing attachments and declarations (PROTECTED)

These templates are submitted alongside or as part of tinglysing packages. While they may not have Kartverket form numbers, they follow regulated formats.

| Template name | Size | Notes |
|--------------|------|-------|
| **Vedlegg skjøte/hjemmelsoverføring prosjekt — fullmakt kjøper** | 5K | Power of attorney attachment for project sales |
| **Vedlegg skjøte prosjekt — erklæring boligseksjon** | 3K | Housing section declaration for project sales |
| **Erklæring om pantefrafall** | 5K | Declaration of mortgage waiver |
| **Pantefrafall** | 4K | Mortgage waiver document |
| **Anmodning pantefrafall** | 5K | Request for mortgage waiver |

### Tier 4: Tinglysing cover letters (EDITABLE WITH CAUTION)

These are brokerage cover letters that accompany tinglysing submissions. They are NOT Kartverket-regulated forms themselves, but serve as professional correspondence to Kartverket. They may be customized for branding (Proaktiv variants exist), but the legal references and merge fields within them should remain accurate.

| Template name | Size | Notes |
|--------------|------|-------|
| Følgebrev tinglysing | 4K | General tinglysing cover letter |
| Følgebrev sikring | 3K | Cover letter for security registration |
| Følgebrev sletting av sikring | 3K | Cover letter for security deletion |
| Følgebrev sletting av sikring m/urådighet Proaktiv | — | Proaktiv variant (Kundemal) |
| Følgebrev tinglyst pantedokument | 4K | Cover letter for registered mortgage |
| Følgebrev tinglyst pant | — | Cover letter variant (Kundemal) |
| Følgebrev — Tinglyst pantedokument til kjøpers bank | — | Proaktiv variants (QA-1 and V.2.1) |
| Følgebrev pantedokument i tinglyst stand — Bortfester V.3.0 | — | Leasehold variant |
| Samtykke til overdragelse — Bortfester | — | Consent to transfer (leasehold) |

### How to identify a no-touch template

When working with templates, check these indicators — if **any** match, treat the template as no-touch:

1. **Template name** contains: `Skjøte`, `Pantedokument`, `Hjemmelserklæring`, `Hjemmelsoverføring`, `konsesjonsfrihet`, `konsesjon`, `Tvangssalg`, `pantefrafall`, `Seksjoneringsbegjæring`
2. **Footer assignment** is `Vitec Bunntekst Skjøte` or `Vitec Bunntekst Sikring`
3. **HTML contains** `contenteditable="false"` on structural elements (government forms lock layout elements)
4. **HTML contains** agency references: `GA-5400`, `Statens kartverk`, `LDIR-356`, `LDIR-359`, `LDIR-360`, `Landbruksdirektoratet`, `Kommunal- og moderniseringsdepartementet`
5. **HTML uses self-contained CSS** with `@import url('https://fonts.googleapis.com/...')` instead of referencing the Vitec Stilark
6. **Template size** is 20K+ and contains complex table structures with `data-choice`, `data-label` attributes
7. **Category** is `Kontrakt` or `Annet` with tinglysing-related assignment types

### What IS allowed on no-touch templates

- **Viewing** the template in the editor (read-only inspection)
- **Testing** with "Testfletting" to verify merge field output
- **Copying** via "Kopier som ny mal" to create a working reference copy (clearly rename it)
- **Assigning/unassigning** the template to different assignment types, phases, or departments (metadata only — does not alter the HTML)
- **Changing email subject** line in template settings (does not affect the PDF form)

### Archival reference: Skjøte template architecture (DO NOT USE AS DEVELOPMENT GUIDE)

> **ARCHIVAL ONLY** — The following analysis documents patterns found in the Skjøte form. These patterns are specific to converted government forms and contain workarounds that are **NOT best practice for Vitec Next template development.** For guidance on building new templates, use Sections 1–12.

The Skjøte (title deed) source code has been analyzed to document how government forms differ architecturally from regular brokerage templates.

#### Key architectural differences from regular templates

| Aspect | Regular template | Kartverket form (Skjøte) |
|--------|-----------------|--------------------------|
| Stilark | `<span vitec-template="resource:Vitec Stilark">` | **Not used** — self-contained CSS |
| Root class | `class="proaktiv-theme"` | **No class** — bare `id="vitecTemplate"` |
| Font size | 10pt (Stilark default) | **8pt** body, 9pt row headers, 7pt labels |
| Line height | `normal` (Stilark) | **9–10pt** explicit on all elements |
| CSS location | Stilark + optional `<style>` inside div | **Two `<style>` blocks** at top of `#vitecTemplate` div |
| Content locking | Rare | **Extensive** `contenteditable="false"` on all structural/legal text |
| Table layout | Variable | **100-column grid** (`colspan="100"` base), `table-layout: fixed` |
| Page breaks | `.avoid-page-break` class | `page-break-inside: avoid` on tables and rows |

#### Numbered section structure (Kartverket standard)

The Skjøte follows Kartverket's mandatory numbered section layout:

| Section | Norwegian | Content |
|---------|-----------|---------|
| 1 | Eiendommen(e) | Property identification (matrikkel numbers) |
| 2 | Kjøpesum | Purchase price + omsetningstype classification |
| 3 | Salgsverdi/avgiftsgrunnlag | Sales value / tax basis |
| 4 | Overdras fra | Transfer from (seller/heir/defendant) |
| 5 | Til | Transfer to (buyer) |
| 6 | Særskilte avtaler | Special agreements (tinglysing-relevant only) |
| 7 | Kjøpers/erververs erklæring | Buyer's declaration (housing section law) |
| 8 | Erklæring om sivilstand mv. | Marital status declaration |
| 9 | Underskrifter og bekreftelser | Signatures and witness confirmations |
| 10 | Erklæring om sivilstand mv. for hjemmelshaver | Title holder marital status (conditional) |
| 11 | Underskrifter og bekreftelser | Title holder signatures (conditional) |
| — | Innsending og veiledning | Kartverket submission address and instructions |

Sections 10–11 are **conditional** — they only render when `Model.grunneier.navn != "Mangler data" || Model.hjemmelshaver.navn != "Mangler data"` and include `page-break-before: always`.

#### Kartverket address embedded in template

```
Kartverket Tinglysing
Postboks 600 Sentrum
3507 Hønefoss
```

With links to `www.kartverket.no/skjote` and `www.kartverket.no/eiendom`.

#### Triple-source party listing pattern (Section 4)

The Skjøte demonstrates a complex conditional pattern for the "Overdras fra" (transfer from) section, where three different Model collections are used depending on the transaction type:

```html
<!-- Regular sale (not forced, not estate) -->
<div vitec-if="Model.oppdrag.hovedtype != &quot;Tvangssalg&quot; &amp;&amp; Model.oppdrag.erdodsbo == false">
  <ul vitec-foreach="selger in Model.selgere">
    <li>[[*selger.idnummer]]</li>
  </ul>
</div>

<!-- Estate sale (dødsbo) -->
<div vitec-if="Model.oppdrag.hovedtype != &quot;Tvangssalg&quot; &amp;&amp; Model.oppdrag.erdodsbo == true">
  <ul vitec-foreach="arving in Model.arvinger">
    <li>[[*arving.idnummer]]</li>
  </ul>
</div>

<!-- Forced sale (tvangssalg) -->
<div vitec-if="Model.oppdrag.hovedtype == &quot;Tvangssalg&quot;">
  <ul vitec-foreach="saksokte in Model.saksokteliste">
    <li>[[*saksokte.idnummer]]</li>
  </ul>
</div>
```

This pattern repeats for each column (ID number, Name, Ideell andel) and in both the "Overdras fra" and "Underskrifter" sections.

#### Razor code blocks for Kartverket form classification

The Skjøte contains extensive `@{ }` Razor code blocks that set CSS class variables for radio button pre-selection. These cover the official Kartverket classification codes:

**Ground type (Bruk av grunn) — 7 categories:**

| Variable | Model condition | Kartverket code |
|----------|----------------|-----------------|
| `@erTypeGrunnBoligeiendom` | `Model.eiendom.typegrunn == "Boligeiendom"` | **B** Boligeiendom |
| `@erTypeGrunnFritidseiendom` | `Model.eiendom.typegrunn == "Fritidseiendom"` | **F** Fritidseiendom |
| `@erTypeGrunnForretningKontor` | `Model.eiendom.typegrunn == "Forretning - kontor"` | **V** Forretning/kontor |
| `@erTypeGrunnIndustriBergverk` | `Model.eiendom.typegrunn == "Industri - bergverk"` | **I** Industri |
| `@erTypeGrunnLandbrukFiske` | `Model.eiendom.typegrunn == "Landbruk - fiske"` | **L** Landbruk |
| `@erTypeGrunnOffentligVei` | `Model.eiendom.typegrunn == "Offentlig vei"` | **K** Off. vei |
| `@erTypeGrunnAnnet` | `Model.eiendom.typegrunn == "Annet"` | **A** Annet |

**Housing type (Type bolig) — 5 categories:**

| Variable | Model condition | Kartverket code |
|----------|----------------|-----------------|
| `@erTypeBoligFrittliggendeEnebolig` | `Model.eiendom.typebolig == "Frittliggende enebolig"` | **FB** Frittligg. enebolig |
| `@erTypeBoligTomannsbolig` | `Model.eiendom.typebolig == "Tomannsbolig"` | **TB** Tomannsbolig |
| `@erTypeBoligRekkehusKjede` | `Model.eiendom.typebolig == "Rekkehus/Kjede"` | **RK** Rekkehus kjede |
| `@erTypeBoligBlokkleilighet` | `Model.eiendom.typebolig == "Blokkleilighet"` | **BL** Blokkleilighet |
| `@erTypeBoligAnnet` | `Model.eiendom.typebolig == "Annet"` | **AN** Annet |

**Other classification variables in Skjøte:**

| Variable | Model condition | Purpose |
|----------|----------------|---------|
| `@erTomtetypeEiertomt` | `Model.eiendom.tomtetype == "eiertomt"` | Plot type: owned |
| `@erTomtetypeFestetomt` | `Model.eiendom.tomtetype == "festetomt"` | Plot type: leasehold |
| `@erGrunntypeTomt` / `@erIkkeGrunntypeTomt` | `Model.eiendom.grunntype == "Tomt"` | Bebygd/Ubebygd (built/unbuilt) |
| `@erOppgjorsOppdrag` / `@erIkkeOppgjorsOppdrag` | `Model.oppdrag.hovedtype == "Oppgjørsoppdrag"` | Settlement assignment |
| `@erTvangssalg` / `@erIkkeTvangssalg` | `Model.oppdrag.hovedtype == "Tvangssalg"` | Forced sale |

#### Skjøte-specific merge fields

| Path | Kartverket field | Section |
|------|-----------------|---------|
| `skjema.innsender.navn` | Innsenders navn | Header |
| `skjema.innsender.adresse` | Adresse | Header |
| `skjema.innsender.postnr` | Postnr | Header |
| `skjema.innsender.poststed` | Poststed | Header |
| `skjema.innsender.orgnr` | (Under-) organisasjonsnr/fødselsnr | Header |
| `skjema.referansenr` | Ref.nr. | Header |
| `eiendom.kommunenr` | Kommunenr. | 1. Eiendommen(e) |
| `eiendom.kommunenavn` | Kommunenavn | 1. Eiendommen(e) |
| `matrikkel.gnr` | Gnr. | 1. Eiendommen(e) |
| `matrikkel.bnr` | Bnr. | 1. Eiendommen(e) |
| `matrikkel.fnr` | Festenr. | 1. Eiendommen(e) |
| `matrikkel.snr` | Seksjonsnr. | 1. Eiendommen(e) |
| `matrikkel.andel` | Ideell andel | 1. Eiendommen(e) |
| `kontrakt.kjopesum` | Kjøpesum (formatted via `$.UD()`) | 2. Kjøpesum |
| `kontrakt.kjopesumibokstaver` | Kjøpesum i bokstaver | 2. Kjøpesum |
| `kontrakt.avgiftsgrunnlag` | Avgiftsgrunnlag (formatted via `$.UD()`) | 3. Salgsverdi |
| `eiendom.fellesgjeld` | Fellesgjeld (for sameie) | 3. Salgsverdi |
| `sameie.sameiebrok` | Sameiebrøk | 1. / 3. |
| `selger.idnummer` | Fødselsnr./Org.nr. | 4. Overdras fra |
| `selger.navnutenfullmektigogkontaktperson` | Navn (without fullmektig/kontaktperson) | 4. / 9. |
| `selger.eierbrok` | Ideell andel | 4. Overdras fra |
| `selger.ergift` | Er gift (boolean) | 9. Underskrifter |
| `selger.selgersektefelle.navnutenfullmektig` | Ektefelle/partner name | 9. Underskrifter |
| `kjoper.idnummer` | Fødselsnr./Org.nr. | 5. Til |
| `kjoper.navnutenfullmektigogkontaktperson` | Navn | 5. Til |
| `kjoper.eierbrok` | Ideell andel | 5. Til |
| `arving.idnummer` / `arving.navnutenfullmektigogkontaktperson` / `arving.eierbrok` | Heir fields (dødsbo) | 4. Overdras fra |
| `saksokte.idnummer` / `saksokte.navnutenfullmektigogkontaktperson` / `saksokte.eierbrok` | Defendant fields (tvangssalg) | 4. Overdras fra |
| `grunneier.idnummer` / `grunneier.navn` | Land owner fields | 9. / 11. Underskrifter |
| `hjemmelshaver.idnummer` / `hjemmelshaver.navn` | Title holder fields | 11. Underskrifter |
| `oppdrag.prosjekt.saerskilteavtaler` | Special agreements (tinglysing-relevant) | 6. Særskilte avtaler |
| `oppdrag.prosjekt.andreavtaler` | Other agreements (non-tinglysing) | 6. (conditional) |
| `oppdrag.hovedtype` | Assignment main type | Classification logic |
| `oppdrag.erdodsbo` | Is estate/dødsbo (boolean) | Party source selection |
| `eiendom.eieform` | Ownership form ("Sameie", etc.) | 1. / 7. |
| `eiendom.tomtetype` | Plot type ("eiertomt", "festetomt") | 1. Classification |
| `eiendom.grunntype` | Ground type ("Tomt", etc.) | 1. Classification |
| `eiendom.typegrunn` | Ground use classification (7 categories) | 1. Classification |
| `eiendom.typebolig` | Housing type classification (5 categories) | 1. Classification |

#### CSS patterns unique to Kartverket forms

The Skjøte CSS includes patterns not found in regular templates:

- **`data-label` floating labels** — Absolute-positioned `::before` pseudo-elements showing field labels at 7pt above the field content. Padding: `14px 2px 2px 2px`.
- **`data-choice` floating choice labels** — Absolute-positioned `::after` pseudo-elements showing selection labels below the content. Padding: `0 2px 14px 2px`.
- **Combined `data-label` + `data-choice`** — When both are present, padding increases to `16px 2px 16px 2px`.
- **`checkbox-row` extended padding** — `padding-bottom: 24px` for rows with long `data-choice` text.
- **`foreach-list` cells** — `min-height: 34px`, `<ul>` inside `<td>` with `list-style: none`, `margin: 0`, `min-height: 13px` (for empty loops).
- **`contenteditable="false"` user-select** — All children of locked elements get `user-select: none`.
- **CKEditor widget override** — `.cke_widget_inline { white-space: pre-wrap; word-break: break-all; }` prevents placeholder widgets from breaking table cell widths.
- **`text-transform: uppercase`** — Applied to `<li>` elements in "Gjenta med blokkbokstaver" (repeat in block letters) fields.

**(Evidence: Skjøte source code from Vitec Next production, 2026-02-21)**

### Archival reference: Hjemmelsoverføring template architecture (DO NOT USE AS DEVELOPMENT GUIDE)

> **ARCHIVAL ONLY** — Same warning as above. These patterns are from a converted government form, not native Vitec Next development.

The Hjemmelsoverføring (transfer of title to housing cooperative share) is another Tier 1 Kartverket form. It shares the same form family as the Skjøte (GA-5400 B) but is specifically for borettslag (housing cooperative) share transfers under borettslagsloven chapter 6.

#### Differences from Skjøte

| Aspect | Skjøte | Hjemmelsoverføring |
|--------|--------|-------------------|
| Title | "Skjøte" (right-aligned, 16pt) | "Overføring av hjemmel til andel i borettslag" (in header cell, 14pt) with subtitle |
| Subject | Fast eiendom (real property) | Andel i borettslag (cooperative share) |
| Sections | 11 numbered sections | 7 numbered sections |
| Page count | Variable (conditional sections 10–11) | **Fixed 2 pages** with hardcoded "Side 1 av 2" / "Side 2 av 2" |
| Page numbering | Uses `[[p]]` / `[[P]]` merge fields (in footer) | **Hardcoded** page numbers in the body — does NOT use merge fields |
| Matrikkel (Section 1) | Property cadastral numbers | Borettslag org number + share number |
| Ground categories | 7 categories (B/F/V/I/L/K/A) | **3 categories** (B. Bolig, F. Fritidsbolig, N. Næring/kontor) |
| Omsetningstype | 8 categories | **6 categories** (no "Ekspropriasjon" or "Opphør av samboerskap") |
| Default omsetningstype | None pre-selected | **"1. Fritt salg" pre-selected** (`class="btn active"`) |
| CSS `data-label` text | Normal case | **`text-transform: uppercase`** |
| CSS `data-label` padding | `14px 2px 2px 2px` | `16px 2px 4px 2px` |
| CSS `data-choice` padding | `0 2px 14px 2px` | `4px 2px 16px 2px` |
| CSS `label.btn` | `display: inline-flex; align-items: center` | `display: inline; vertical-align: baseline` |
| Body reset | `html, body { margin: 0; padding: 0; }` | `body { margin: 0; padding: 0; }` (no `html`) |
| Extra border classes | — | `border-right-svart`, `border-left-svart`, `border-left` |

These CSS differences mean the two forms are NOT interchangeable even at the styling level. Each has its own carefully tuned spacing.

#### Borettslag-specific sections

| Section | Content | Differs from Skjøte |
|---------|---------|-------------------|
| 1. Opplysninger om borettslaget | Borettslag name, address, org number | Replaces matrikkel (cadastral) section |
| 2. Andelen | Share identification: org number, share number, ideal share, classification | Uses `brl.*` and `eiendom.andelsnr` fields |
| 3. Kjøpesum | Same pattern as Skjøte but simpler | Fewer omsetningstype options |
| 4. Overdras fra | Identical triple-source pattern (selgere/arvinger/saksokteliste) | Same |
| 5. Overdras til | Identical buyer listing | Same |
| 6. Særskilte avtaler | Empty field (130px height, no merge fields) | Simpler — no `prosjekt.saerskilteavtaler` field |
| 7. Erklæring + Underskrifter | Combined marital status + signatures | Combined (Skjøte has separate 8+9) |

#### Borettslag merge fields (new)

| Path | Description | Section |
|------|-------------|---------|
| `brl.navn` | Borettslag name and address | 1. Opplysninger om borettslaget |
| `brl.orgnr` | Borettslag organization number | 1. + 2. Andelen |
| `brl.andel` | Borettslag ideal share fraction | 2. Andelen |
| `eiendom.andelsnr` | Share number within the borettslag | 2. Andelen |

#### Hardcoded page numbers — critical pattern

Unlike all other templates that use `[[p]]` / `[[P]]` merge fields for page numbering (typically in the footer template), the Hjemmelsoverføring embeds page numbers directly in the body:

```html
<tr contenteditable="false">
  <td class="no-border" colspan="20"><small>GA-5400 B</small></td>
  <td class="no-border" colspan="60" style="text-align:center"><small>Hjemmelsoverføring</small></td>
  <td class="no-border" colspan="20" style="text-align:right"><small>Side 1 av 2</small></td>
</tr>
```

This pattern appears at the bottom of each page (end of each `<table>`) and means:
- The form is **always exactly 2 pages** — content is laid out to fit precisely
- Page numbers are **not dynamic** — adding content would not update them
- The template should use **no header/footer** (TOPPTEKST: Ingen, BUNNTEKST: Ingen) since form numbering is built into the body
- The GA-5400 B form reference appears on both pages

**(Evidence: Hjemmelsoverføring source code from Vitec Next production, 2026-02-21)**

### Archival reference: Remaining no-touch template characteristics (DO NOT USE AS DEVELOPMENT GUIDE)

> **ARCHIVAL ONLY** — Source code for these forms was reviewed for completeness. The summary below captures key distinguishing characteristics per form. These are converted government forms — do not replicate their patterns.

| Template | Font | Base size | Pages | Agency form | Key architectural notes |
|----------|------|-----------|-------|-------------|------------------------|
| **Pantedokument (sikring)** | Open Sans | 8pt | Variable | Statens kartverk rev 01/19 | Conditional matrikkel vs borettslag (`Model.eiendom.eieform`); `skjema.pantsetter.*` merge fields; larger SVG toggle size than Skjøte; `Model.grunneiere` / `Model.hjemmelshavere` collections for conditional sections |
| **Hjemmelserklæring** | Open Sans | 8pt | Variable | Kartverket | Dynamic section titles ("Eiendommen(e)" vs "Andel"); background `#ccffcc` for row headers; `Model.tidligereeiere` collection; conditional matrikkel vs borettslag display |
| **Seksjoneringsbegjæring** | Calibri, Arial | 9pt body / 7.5pt cells | 4 (fixed) | Kommunaldept. | Only form using Calibri font; `#D9E2F3` header cell color; `a4-main` class for vertical alignment; `page-break-after: always` on `main-table` (`:last-child` override); `reduced-size` class; complex sectioning grid (S.nr, Formål, Brøk, Tilleggsareal); `meglerkontor.*` and `hjemmelshaver.*` merge fields; hardcoded "Side X av 4" page numbers |
| **Egenerklæring (Grønt)** | Arial | 8.5pt | 4 (per buyer) | LDIR-360 B | Root-level `vitec-foreach="kjoper in Model.kjopere"` repeats entire form per buyer; `bg-green-light` / `bg-green` CSS classes; hidden `[[selger.eierbrok]]` field for data loading; extensive checkbox declarations for legal conditions; `kjoper.idnummer.ToString().Length` for ID type detection |
| **Egenerklæring (Rødt)** | Arial | 8.5pt | 4 (per buyer) | LDIR-356 B | Same root-level foreach pattern; `bg-red-light` / `bg-red` CSS classes; additional fields for municipality concession thresholds; `arving.slektskapsforhold` field; Landbruksdirektoratet SVG logo embedded |
| **Søknad om konsesjon (Blått)** | Arial | 9pt | 4 (per buyer) | LDIR-359 B | Root-level foreach; `info-box` / `info-cell` / `info-cell-light` CSS classes; `masked-top-border` for floating labels; uses `@Model.selgere[0].navn` direct array indexing (anti-pattern); extensive land/property detail fields (`totalareal`, `fulldyrket_jord`, `produktiv_skog`); embedded guidance text within template |

#### Shared characteristics of LDIR forms (Grønt, Rødt, Blått)

These three Landbruksdirektoratet forms share a common architectural family:
- **Root-level `vitec-foreach`** — The entire multi-page form is wrapped in `vitec-foreach="kjoper in Model.kjopere"`, generating one complete copy per buyer/applicant
- **Fixed A4 simulation** — Use `td.a4-main { height: 27.5cm }` for vertical content areas
- **Page breaks between tables** — Each page is a separate `<table>` with `page-break-before: always`
- **Extensive checkbox-based legal declarations** — Multiple `<input type="radio">` with SVG toggle styling for legal condition checkboxes
- **`contenteditable` mixing** — Some sections are `contenteditable="false"` (locked legal text), others allow input
- **No Stilark reference** — All CSS is self-contained via `<style>` block
- **No `proaktiv-theme` class** — Bare `id="vitecTemplate"` wrapper

**(Evidence: Source code analysis of Pantedokument (sikring), Hjemmelserklæring, Seksjoneringsbegjæring, Egenerklæring om konsesjonsfrihet (Grønt/Rødt skjema), and Søknad om konsesjon (Blått skjema) from Vitec Next production, 2026-02-21)**

---

*Produced by Documentation Agent, Phase 11. Original rules (Sections 1–12) backed by evidence from `docs/Alle-flettekoder-25.9.md` and `.cursor/vitec-reference.md`. Supplemented with evidence from 133 Vitec Next tagged database templates (queried via PostgreSQL MCP, 2026-02-21), custom Proaktiv production templates, Vitec Stilark source code, Vitec Next admin UI screenshots, Grunnlag brevmal system templates (5 letter template variants), Kjøpekontrakt Næring legacy template (screen-help guided editing pattern), and Kjøpekontrakt Aksje legacy template (dynamic cross-reference CSS, Bilag suite, embedded Oppgjørsavtale — full source code analysis 2026-02-21). Section 13 from admin UI analysis. Section 14 (archival, no-touch) from source code analysis of 8 government forms: Skjøte, Hjemmelsoverføring, Pantedokument (sikring), Hjemmelserklæring, Seksjoneringsbegjæring, Egenerklæring om konsesjonsfrihet (Grønt/Rødt skjema), and Søknad om konsesjon (Blått skjema). Database-sourced additions marked with `(DB evidence: "Template Title")`. Chromium CSS counter fix sourced from Proaktiv custom Kjøpekontrakt FORBRUKER production template.*
