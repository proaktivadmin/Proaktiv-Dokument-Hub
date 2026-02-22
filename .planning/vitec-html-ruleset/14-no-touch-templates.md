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
