# Logic Mapping: Meglerstandard Mars 2020 om salg av eiendom med og uten oppgjørsansvarlig

## Source

- **File:** Meglerstandard for eiendom med og uten oppgjørsansvarlig.htm
- **References used:** vitec-html-ruleset/03-conditional-logic.md, 10-property-conditionals.md, VITEC-IF-DEEP-ANALYSIS.md, vitec-reference.md

## Summary

- **vitec-if conditions:** 25
- **vitec-foreach loops:** 2 (selgere, kjopere)
- **Checkbox groups:** 0 (no explicit checkbox/radio groups identified)
- **Mutually exclusive sections:** 4 (Vedlegg 6 A/B/C, Section 8.6, Section 10, Bilag 1/2)
- **"Mangler data" guards:** 8+

## Conditional Branches

### Property-Type Conditionals

| # | Element | Condition | Scope | Notes |
|---|---------|-----------|-------|-------|
| 1 | div | (see Vedlegg 6 group below) | Vedlegg 6 Version A | Oppgjørsavtale med oppgjørsansvarlig der selgers lån innfris ETTER tinglysing |
| 2 | div | (see Vedlegg 6 group below) | Vedlegg 6 Version B | Oppgjørsavtale med oppgjørsansvarlig der selgers lån innfris VED overtakelse |
| 3 | div | (see Vedlegg 6 group below) | Vedlegg 6 Version C | Oppgjørsavtale uten oppgjørsansvarlig |

### Optional Field Guards

| # | Element | Condition | Content When True | Content When False |
|---|---------|-----------|-------------------|-------------------|
| 1 | p (3.2.1) | Med oppgjørsansvarlig variant | "Kjøpesummen er disponibel på oppgjørskontoen..." (oppgjørsansvarlig text) | — |
| 2 | p (3.2.1) | Uten oppgjørsansvarlig variant | "Vederlaget er disponibelt på Selgers konto etter gjennomføring av oppgjøret..." | — |
| 3 | p (8.6) | Multiple sellers | "Ansvaret til de respektive selgere" section | (hidden) |
| 4 | section (10) | Seller provides security | Section 10 Sikkerhet | (hidden) |
| 5 | section | Bilag 1 Fullmakt | Fullmakt til pantsettelse | (hidden) |
| 6 | section | Bilag 2 Betalingsinstruks | Ugjenkallelig betalingsinstruks | (hidden) |

### Alternative Sections (Mutually Exclusive)

| Group | Option | Condition | Location |
|-------|--------|-----------|----------|
| **Vedlegg 6 (Oppgjørsavtale)** | Version A | Med oppgjørsansvarlig + selgers lån innfris ETTER tinglysing | WordSection2 (line ~3060) |
| **Vedlegg 6** | Version B | Med oppgjørsansvarlig + selgers lån innfris VED overtakelse | WordSection3 (line ~3556) |
| **Vedlegg 6** | Version C | Uten oppgjørsansvarlig | WordSection4 (line ~4167) |
| **Section 8.6** | Show | Model.selgere.Count > 1 | "Ansvaret til de respektive selgere" |
| **Section 10** | Show | Model.kontrakt.selger_stiller_sikkerhet == true (or equivalent) | Section 10 Sikkerhet |
| **Bilag 1** | Show | Oppgjøret IKKE etter tinglysing av skjøte (i.e. ved overtakelse flow) | Fullmakt til pantsettelse |
| **Bilag 2** | Show | Oppgjøret uten oppgjørsansvarlig | Ugjenkallelig betalingsinstruks |

### Vedlegg 6 Three-Way Logic

The three Vedlegg 6 variants are mutually exclusive. Conditions:

| Version | Show when | Strykes when |
|---------|-----------|---------------|
| **A** | Selgers lån innfris ETTER tinglysing + MED oppgjørsansvarlig | Selgers lån innfris ved overtakelse, OR uten oppgjørsansvarlig |
| **B** | Selgers lån innfris VED overtakelse + MED oppgjørsansvarlig | Selgers lån innfris ETTER tinglysing, OR uten oppgjørsansvarlig |
| **C** | Uten oppgjørsansvarlig | Med oppgjørsansvarlig |

**Proposed Model expressions (NEED REVIEW — Vitec may use different field names):**

- Med vs uten oppgjørsansvarlig: `Model.oppgjor.ansvarlig.navn != ""` or `Model.oppdrag.eroppgjorsansvarlig == true` (field name to be confirmed)
- Selgers lån innfris ETTER tinglysing: `Model.kontrakt.selgerslan_innfris_timing == "etter_tinglysing"` or similar
- Selgers lån innfris VED overtakelse: `Model.kontrakt.selgerslan_innfris_timing == "ved_overtakelse"` or similar

### Section 3.2.1 Alternative Text

| Option | Condition | Text |
|--------|-----------|------|
| Med oppgjørsansvarlig | Oppgjøret med oppgjørsansvarlig | "Eiendommen blir først overtatt av Kjøper idet Kjøpesummen er disponibel på oppgjørs­kontoen og vilkårene for utbetaling i punkt 3 i oppgjørsavtalen i vedlegg 6 er oppfylt eller frafalt (Overtakelse)." |
| Uten oppgjørsansvarlig | Oppgjøret uten oppgjørsansvarlig | "Eiendommen blir først overtatt av Kjøper idet Vederlaget er disponibelt på Selgers konto etter gjennomføring av oppgjøret i henhold til oppgjørsavtalen i vedlegg 6 (Overtakelse)." |

### [Alternativt: ...] Text Blocks

| # | Location | Default Text | Alternative Text | Condition |
|---|----------|--------------|-------------------|-----------|
| 1 | Utkast A preamble | (standard signing clause) | "Partene har tatt de forbehold som følger av bud og budaksept, og er ikke bundet før disse forbeholdene er løftet." | To be determined — likely Model.oppdrag.erbudforbehold or similar |
| 2 | Section 8.6 | Proratarisk ansvar (proportional liability) | "De aksjeeiere/personer som utgjør Selger, hefter solidarisk for Kjøpers krav mot Selger som følge av brudd på denne avtalen" | To be determined — likely Model.kontrakt.selger_ansvar_type or similar (proratarisk vs solidarisk) |

### Vedlegg 6 Point 5 (Optional)

Yellow text: "[Om ønskelig kan Dette punktet strykes]" — conditional optional section within Vedlegg 6. No obvious Model field; likely broker/user choice. **Flag for builder review.**

### Vedlegg 6 (Version B/C) Point 4 (Optional)

Yellow text in Version C: "[Om ønskelig kan dette punktet strykes]" — similar optional section. **Flag for builder review.**

## Checkbox State Logic

### Data-Driven Checkboxes

No explicit checkbox groups were found in the source. The document uses yellow-highlighted conditional notes rather than checkboxes.

### Broker-Interactive Checkboxes

None identified.

## Loop Specifications

| # | Collection | Variable | Guard Condition | Fallback Text | Used In |
|---|-----------|----------|-----------------|---------------|---------|
| 1 | Model.selgere | selger | Model.selgere.Count > 0 | [Mangler selger] | Header "mellom" table, Section 1.1, 8.6, signatures, Vedlegg 5, Vedlegg 6, Bilag 1 |
| 2 | Model.kjopere | kjoper | Model.kjopere.Count > 0 | [Mangler kjøper] | Header "og" table, Section 1.2, signatures, Vedlegg 5, Vedlegg 6, Bilag 1, Bilag 2 |

**Party listing patterns (from source flettekoder):**

- `#eiere¤` — seller party header (plural/singular)
- `#flettblankeeiere¤#forsteeier¤#kunadresse.kontakter¤#flettblankeeiere¤` — seller name/address block
- `#Mob: ;mobil.kontakter& ¤#E-post: ;email.kontakter¤` — seller contact (conditional if empty)
- `#nyeeiere¤` — buyer party header
- `#flettblankeeiere¤#forstenyeier¤#kunadresse.kontakter¤#flettblankeeiere¤` — buyer name/address block

**Naming variants:**

- Single vs plural: "Selger" vs "Selgere", "Kjøper" vs "Kjøpere" — use `Model.selgere.Count > 1` and `Model.kjopere.Count > 1` for plural suffix.

## "Mangler Data" Guard List

Fields that should be hidden (not just empty) when Vitec returns "Mangler data":

| Field Path | Guard Expression | Element to Hide |
|-----------|------------------|-----------------|
| selger.tlf / mobil | != "" && != "Mangler data" | Mob: paragraph |
| selger.emailadresse | != "" && != "Mangler data" | E-post: paragraph |
| kjoper.tlf / mobil | != "" && != "Mangler data" | Mob: paragraph |
| kjoper.emailadresse | != "" && != "Mangler data" | E-post: paragraph |
| selger.fullmektig.navn | != "" && != "Mangler data" | Fullmektig section (if present) |
| kjoper.fullmektig.navn | != "" && != "Mangler data" | Fullmektig section (if present) |
| megler.navn | != "" && != "Mangler data" | Megler signature/contact |
| oppgjor.ansvarlig.navn | != "" && != "Mangler data" | Oppgjørsansvarlig section |

## Condition Expression Syntax Reference

All conditions in this document use the MODEL notation. When implementing in HTML:

- `"` in values → `&quot;`
- `>` in comparisons → `&gt;`
- `<` in comparisons → `&lt;`
- `&&` (AND) → `&amp;&amp;`
- Norwegian chars in string values → `\xF8` (ø), `\xE5` (å), `\xE6` (æ)

## Unresolved Logic (NEED REVIEW)

| # | Location | Intent | Why Unresolved |
|---|----------|--------|----------------|
| 1 | Vedlegg 6 A/B/C | Three-way Vedlegg 6 selection | Vitec field names for "med/uten oppgjørsansvarlig" and "selgers lån innfris ved/etter" not found in field registry. May require custom config or broker selection. |
| 2 | Section 10 | Show when Selger provides security | No `selger_stiller_sikkerhet` or equivalent found in registry. |
| 3 | Bilag 1 Fullmakt | Show when oppgjøret IKKE etter tinglysing | Inverse of Vedlegg 6 Version A condition. Need confirmed field. |
| 4 | Bilag 2 Betalingsinstruks | Show when uten oppgjørsansvarlig | Same as Vedlegg 6 Version C condition. |
| 5 | Utkast A [Alternativt] | Bud/budaksept forbehold clause | Source does not specify which field drives this. |
| 6 | Section 8.6 [Alternativt] | Proratarisk vs solidarisk ansvar | No field for ansvarstype found. |
| 7 | Vedlegg 6 Point 5 | "Om ønskelig kan Dette punktet strykes" | Optional broker choice; no data-driven field. |
| 8 | Vedlegg 6 Version C Point 4 | "[Om ønskelig kan dette punktet strykes]" | Same as above. |

## Proposed Vitec-If Conditions (Where Determined)

| Location | Condition | Notes |
|----------|-----------|-------|
| Vedlegg 6 A | `Model.oppgjor.med_oppgjorsansvarlig == true && Model.kontrakt.selgerslan_innfris == "etter_tinglysing"` | **NEED REVIEW** — field names hypothetical |
| Vedlegg 6 B | `Model.oppgjor.med_oppgjorsansvarlig == true && Model.kontrakt.selgerslan_innfris == "ved_overtakelse"` | **NEED REVIEW** |
| Vedlegg 6 C | `Model.oppgjor.med_oppgjorsansvarlig == false` or `Model.oppgjor.ansvarlig.navn == "Mangler data"` | May use oppgjor.ansvarlig absence as proxy |
| Section 3.2.1 med | `Model.oppgjor.ansvarlig.navn != "Mangler data" && Model.oppgjor.ansvarlig.navn != ""` | Show oppgjørsansvarlig wording |
| Section 3.2.1 uten | Inverse of above | Show uten oppgjørsansvarlig wording |
| Section 8.6 | `Model.selgere.Count > 1` | "Ansvaret til de respektive selgere" |
| Section 10 | (custom field TBD) | Selger provides security |
| Bilag 1 | `Model.kontrakt.selgerslan_innfris != "etter_tinglysing"` or equivalent | Fullmakt needed when oppgjøret ved overtakelse |
| Bilag 2 | `Model.oppgjor.med_oppgjorsansvarlig == false` | Only for uten oppgjørsansvarlig |
| Selger plural | `Model.selgere.Count > 1` | "Selgere" |
| Kjøper plural | `Model.kjopere.Count > 1` | "Kjøpere" |

## Appendix: Source Flettekoder (Legacy)

Legacy flettekoder from the Word export (for Field Mapper reference; NOT logic mapping):

- `#navn.firma¤`, `#organisasjonsnummer.firma¤` — Megler
- `#type_oppdrag.oppdrag¤` — Type oppdrag
- `#type_eierformbygninger.oppdrag¤`, `#type_eierformtomt.oppdrag¤` — Eierform
- `#oppdragsnummer.oppdrag¤`, `#omsetningsnummer.oppdrag¤`
- `#eiere¤`, `#nyeeiere¤` — Party headers
- `#flettblankeeiere¤`, `#forsteeier¤`, `#forstenyeier¤`, `#kunadresse.kontakter¤`
- `#Mob: ;mobil.kontakter& ¤`, `#E-post: ;email.kontakter¤`
- `#adresse.oppdrag¤`, `#matrikkelkommune.oppdrag¤`, `#type_eierformtomt.oppdrag¤`, `#seksjonsbrok.oppdrag¤`, `#ideellandel.oppdrag¤`
- `#include_rtfelementer_kontrakt¤` — Contract elements include
