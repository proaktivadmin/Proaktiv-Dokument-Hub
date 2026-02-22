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
1. Wrap everything in `<div class="proaktiv-theme" id="vitecTemplate">`
2. Add Stilark reference: `<span vitec-template="resource:Vitec Stilark">&nbsp;</span>`
3. Add `<style>` block with CSS counters (Chromium-safe dual-counter pattern)
4. Wrap numbered contract sections in `<article class="item">` with `<h2>` headings
5. Convert layout tables to 100-unit colspan system
6. Add `roles-table` and `costs-table` CSS classes
7. Add `avoid-page-break` class on signature section
8. Convert signature block to `border-bottom: solid 1px #000` signing lines
9. Add `span.insert` placeholders for user fill-in fields

### Step 6: Validate

**Input:** Complete template
**Output:** Validation report (pass/fail per checklist item)

Run the 14-point Section 12 checklist from `.planning/vitec-html-ruleset.md`:
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
- Norwegian characters (æ, ø, å) preserved correctly
- No legacy `#field.context¤` syntax remaining
- UTF-8 encoding clean (no Windows-1252 artifacts)

---

## 3. Template Style Block

Every contract template needs this CSS counter pattern in a `<style>` block:

```css
#vitecTemplate { counter-reset: section; }
#vitecTemplate article.item:not(article.item article.item) {
  counter-increment: section;
  counter-reset: subsection;
}
#vitecTemplate article.item article.item { counter-increment: subsection; }
#vitecTemplate article.item:not(article.item article.item) > h2::before {
  content: counter(section) ". ";
}
#vitecTemplate article.item article.item > h3::before {
  content: counter(section) "." counter(subsection) ". ";
}
#vitecTemplate article { padding-left: 20px; }
#vitecTemplate article article { padding-left: 0; }
#vitecTemplate .avoid-page-break { page-break-inside: avoid; }
#vitecTemplate .roles-table { width: 100%; table-layout: fixed; border-collapse: collapse; }
#vitecTemplate .roles-table th { text-align: left; padding: 4px 6px; border-bottom: 1px solid #000; }
#vitecTemplate .roles-table td { padding: 4px 6px; vertical-align: top; }
#vitecTemplate .roles-table tbody:last-child tr:last-child td { display: none; }
#vitecTemplate .costs-table { width: 100%; table-layout: fixed; border-collapse: collapse; }
#vitecTemplate .costs-table td { padding: 2px 6px; vertical-align: top; }
#vitecTemplate .costs-table tr.sum-row td { border-top: 1px solid #000; font-weight: bold; }
#vitecTemplate .insert { border-bottom: 1px dotted #999; min-width: 80px; display: inline-block; }
```

This uses the **Chromium-safe dual-counter pattern** (not `counters(item, ".")` which breaks in Chrome PDF rendering).

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

```html
<p>
  <span vitec-if="Model.eiendom.tomtetype == &quot;eiertomt&quot;">&#9745;</span>
  <span vitec-if="Model.eiendom.tomtetype != &quot;eiertomt&quot;">&#9744;</span>
  eiet
</p>
```

- `&#9745;` = ☑ (checked checkbox)
- `&#9744;` = ☐ (unchecked checkbox)

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
<p vitec-if="Model.oppdrag.prosjekt.erutbyggersforbeholdsalgsgrad == true">&#9745; Salgsgrad</p>
<p vitec-if="Model.oppdrag.prosjekt.erutbyggersforbeholdigangsettelse == true">&#9745; Igangsettelsestillatelse</p>
<p vitec-if="Model.oppdrag.prosjekt.erutbyggersforbeholdbyggelaan == true">&#9745; Byggelån</p>
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

## 7. Source Document Clue Recognition

When reading a source `.htm` or `.docx`, look for these patterns to identify what needs conversion:

| Source Pattern | What It Means | Action |
|---------------|---------------|--------|
| `#fieldname.context¤` | Legacy merge field | Map to `[[modern.field]]` |
| `font-family:Wingdings` + `q` character | Empty checkbox | Convert to `&#9744;` or auto-check pattern |
| `color:red` in text | Conditional alternative | Create `vitec-if` branch |
| `fra/<u>med</u>` or slash-separated alternatives | Choose-one option | Create `vitec-if` with checkbox |
| "Alt 1:" / "Alt 2:" labels | Explicit alternatives | Create `vitec-if` div blocks |
| "Boligen/fritidsboligen" | Property type conditional | Use `grunntype` condition |
| "1 A" / "1 B" section headers | Ownership form alternatives | Use `eieform` condition |
| `background:yellow` | Placeholder/example value | Replace with merge field or `span.insert` |
| `…………` or `........................` | Fill-in blank | Replace with `<span class="insert">&nbsp;</span>` |
| `<div class=WordSection*>` | Page break in Word | Remove wrapper, content becomes continuous |
| `<br clear=all style='page-break-before:always'>` | Explicit page break | Remove |

---

## 8. Validation Script

A reusable validation script exists at `scripts/validate_template.py`. It checks all 39 validation points from the Section 12 checklist. Run it after every template build:

```bash
python scripts/validate_template.py
```

The script reads from `scripts/converted_html/Kjopekontrakt_prosjekt_enebolig_PRODUCTION.html` by default. Modify the `TEMPLATE` constant to point to a different file.

Target: **39/39 PASS** before any template is considered production-ready.

---

## 9. Template Inventory

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

## 10. Agent Instructions for Template Conversion

### Pre-Requisites

Before starting any template conversion:

1. Read `CLAUDE.md` for project context
2. Read this document (`PRODUCTION-TEMPLATE-PIPELINE.md`) in full
3. Read `.planning/vitec-html-ruleset.md` Section 12 (Conversion Checklist)
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

4. **Run validation** — Use `scripts/validate_template.py` (modify `TEMPLATE` path). Target 39/39 PASS.

5. **Build preview** — Use `scripts/build_preview.py` to generate a visual preview. Open in browser to verify rendering.

6. **Compare against PDF** — Section by section, verify:
   - All sections present
   - All legal text accurate (verbatim from source)
   - All merge fields properly placed
   - All conditionals correctly branched
   - Norwegian characters preserved

### Quality Checklist (Quick Reference)

- [ ] `<div class="proaktiv-theme" id="vitecTemplate">` wrapper
- [ ] `<span vitec-template="resource:Vitec Stilark">&nbsp;</span>` present
- [ ] CSS counter style block present
- [ ] All `<article class="item">` with `<h2>` headings
- [ ] All legacy `#field¤` syntax replaced
- [ ] All `vitec-if` use `&quot;` for quotes, `&gt;` for `>`
- [ ] All `vitec-foreach` have collection guards
- [ ] `roles-table` class on party tables
- [ ] `costs-table` class on financial tables
- [ ] Signature block with `border-bottom: solid 1px #000`
- [ ] `span.insert` for user fill-in fields
- [ ] `avoid-page-break` on signature section
- [ ] Norwegian characters (æ, ø, å) verified
- [ ] No inline `font-family` or `font-size`
- [ ] UTF-8 encoding, no Windows-1252 artifacts

---

## 11. Files Reference

| File | Purpose |
|------|---------|
| `scripts/build_production_template.py` | Builds the pilot Kjøpekontrakt template |
| `scripts/build_preview.py` | Generates visual preview with Stilark CSS |
| `scripts/validate_template.py` | Runs 39-point validation checklist |
| `scripts/source_htm/` | Source .htm files (UTF-8 copies) |
| `scripts/converted_html/` | Output production templates and previews |
| `.planning/vitec-html-ruleset.md` | The HTML ruleset (3,208 lines, 14 sections) |
| `.cursor/Alle-flettekoder-25.9.md` | Complete merge field reference (6,494 lines) |
| `docs/vitec-stilark.md` | Vitec Stilark CSS |

---

## 12. Known Issues & Edge Cases

1. **Console encoding:** Norwegian characters (ø, å, æ) may display as `?` in PowerShell console output. This is a console display issue, not a file encoding problem. Verify by reading the actual file bytes.

2. **File locking:** Word locks `.htm` files while open. The agent will get `IOException` when trying to read. User must close the file in Word first.

3. **Wingdings in .docx:** When mammoth processes .docx files, Wingdings checkboxes become plain `<li>` bullet items, losing the checkbox semantics. The .htm format preserves them.

4. **Red text in .docx:** mammoth strips color styles, so red-text conditional markers are invisible in .docx conversion. The .htm format preserves `color:red` inline styles.

5. **Empty collections:** Some vitec-foreach collections may be empty in certain contexts. Always add a collection guard (`vitec-if="Model.collection.Count &gt; 0"`) on the table/container.

6. **"Mangler data" sentinel:** Vitec Next returns the string `"Mangler data"` for fields that have no value. This is different from an empty string. Use `!= &quot;Mangler data&quot;` for date fields that might not be set.

7. **Field paths with asterisk:** Inside a `vitec-foreach` loop, all merge fields referencing the loop variable must use `[[*variable.field]]` (with asterisk) to indicate they are required within the loop context.
