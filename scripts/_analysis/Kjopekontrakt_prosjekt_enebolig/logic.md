# Logic Mapping: Kjopekontrakt_prosjekt_enebolig

## Source
- **File:** scripts/source_htm/Kjopekontrakt_prosjekt_enebolig.htm
- **References used:** vitec-html-ruleset/03-conditional-logic.md, 10-property-conditionals.md, VITEC-IF-DEEP-ANALYSIS.md

## Summary
- **vitec-if conditions:** 24
- **vitec-foreach loops:** 3
- **Checkbox groups:** 10
- **Mutually exclusive sections:** 2 (1A vs 1B, Alt 1 vs Alt 2 overtakelse)
- **"Mangler data" guards:** 8

## Conditional Branches

### Property-Type Conditionals

| # | Element | Condition | Scope | Notes |
|---|---------|-----------|-------|-------|
| 1 | div | Model.eiendom.eieform != "Eierseksjon" | Section 1A (entire) | Show selveiet bolig/fritidsbolig variant |
| 2 | div | Model.eiendom.eieform == "Eierseksjon" | Section 1B (entire) | Show bolig/fritidsbolig i sameie variant |
| 3 | span | Model.eiendom.grunntype == "Bolig" | Inline text | "Boligen" |
| 4 | span | Model.eiendom.grunntype == "Fritid" | Inline text | "Fritidsboligen" |
| 5 | span | Model.eiendom.grunntype == "Bolig" | Header text | "boligens" |
| 6 | span | Model.eiendom.grunntype == "Fritid" | Header text | "fritidsboligens" |
| 7 | span | Model.eiendom.grunntype == "Bolig" | Section 1B | "Boligen" |
| 8 | span | Model.eiendom.grunntype == "Fritid" | Section 1B | "Fritidsboligen" |

### Optional Field Guards

| # | Element | Condition | Content When True | Content When False |
|---|---------|-----------|-------------------|-------------------|
| 1 | p | Model.selger.fullmektig.navn != "" && Model.selger.fullmektig.navn != "Mangler data" | Fullmektig paragraph (selger) | (hidden) |
| 2 | p | Model.kjoper.fullmektig.navn != "" && Model.kjoper.fullmektig.navn != "Mangler data" | Fullmektig paragraph (kjøper) | (hidden) |
| 3 | span | selger.tlf != "" && selger.tlf != "Mangler data" | Mob: [[*selger.tlf]] | (hidden) |
| 4 | span | selger.emailadresse != "" && selger.emailadresse != "Mangler data" | E-post: [[*selger.emailadresse]] | (hidden) |
| 5 | span | (selger.tlf != "" && selger.emailadresse != "") | " / " separator | (hidden) |
| 6 | span | kjoper.tlf != "" && kjoper.tlf != "Mangler data" | Mob: [[*kjoper.tlf]] | (hidden) |
| 7 | span | kjoper.emailadresse != "" && kjoper.emailadresse != "Mangler data" | E-post: [[*kjoper.emailadresse]] | (hidden) |
| 8 | span | (kjoper.tlf != "" && kjoper.emailadresse != "") | " / " separator | (hidden) |
| 9 | p | (Model.eiendom.heftelserogrettigheter == "" \|\| Model.eiendom.heftelserogrettigheter == "Mangler data") | Pengeheftelser Alt 1 checked | Alt 2 checked |
| 10 | p | (Model.eiendom.heftelserogrettigheter != "" && Model.eiendom.heftelserogrettigheter != "Mangler data") | Pengeheftelser Alt 2 checked + show content | Alt 1 checked |
| 11 | div | Model.kontrakt.overtagelse.dato != "Mangler data" | Alt 1 checked (fixed date) | Alt 2 checked |
| 12 | div | Model.kontrakt.overtagelse.dato == "Mangler data" | Alt 2 checked (project) | Alt 1 checked (insert field) |

### Alternative Sections (Mutually Exclusive)

| Group | Option | Condition | Location |
|-------|--------|-----------|----------|
| Salgsobjekt | 1A (selveiet) | Model.eiendom.eieform != "Eierseksjon" | WordSection1 |
| Salgsobjekt | 1B (sameie) | Model.eiendom.eieform == "Eierseksjon" | WordSection2 |
| Overtakelse | Alternativ 1 | Model.kontrakt.overtagelse.dato != "Mangler data" | Section 9 |
| Overtakelse | Alternativ 2 | Model.kontrakt.overtagelse.dato == "Mangler data" | Section 9 |

## Checkbox State Logic

### Data-Driven Checkboxes

| # | Location | Checked Condition | Unchecked Condition | Label Text |
|---|----------|-------------------|---------------------|------------|
| 1 | Section 1A/1B | Model.eiendom.grunntype == "Bolig" | Model.eiendom.grunntype != "Bolig" | bolig |
| 2 | Section 1A/1B | Model.eiendom.grunntype == "Fritid" | Model.eiendom.grunntype != "Fritid" | fritidsbolig |
| 3 | Section 1A/1B | Model.eiendom.tomtetype == "eiertomt" | Model.eiendom.tomtetype != "eiertomt" | eiet |
| 4 | Section 1A/1B | Model.eiendom.tomtetype == "festetomt" | Model.eiendom.tomtetype != "festetomt" | festet |
| 5 | Section 5 | (Model.eiendom.heftelserogrettigheter == "" \|\| Model.eiendom.heftelserogrettigheter == "Mangler data") | opposite | Eiendommen overdras fri for pengeheftelser |
| 6 | Section 5 | (Model.eiendom.heftelserogrettigheter != "" && Model.eiendom.heftelserogrettigheter != "Mangler data") | opposite | Eiendommen overdras fri ... med unntak for |
| 7 | Section 9 | Model.kontrakt.overtagelse.dato != "Mangler data" | Model.kontrakt.overtagelse.dato == "Mangler data" | Alternativ 1: Eiendommen overtas den (DATO) |
| 8 | Section 9 | Model.kontrakt.overtagelse.dato == "Mangler data" | Model.kontrakt.overtagelse.dato != "Mangler data" | Alternativ 2: Forventet ferdigstillelse |

### Pluralization (Dynamic Text)

| # | Location | Condition | Text When True | Text When False |
|---|----------|------------|----------------|-----------------|
| 1 | Parties/Signature | Model.selgere.Count > 1 | Selgere | Selger |
| 2 | Parties/Signature | Model.kjopere.Count > 1 | Kjøpere | Kjøper |

### Broker-Interactive Checkboxes

| # | Location | Label Text | Notes |
|---|----------|------------|-------|
| 1 | Section 1B | Garasjeplass(er), antall | User fills count; no data-driven state |
| 2 | Section 1B | Parkeringsplass(er), antall | User fills count |
| 3 | Section 1B | Bruksrett til del av fellesarealer | Sameiet tilvalg |
| 4 | Section 1B | Tilleggsareal, se vedlegg | Sameiet tilvalg |
| 5 | Section 1B | Gjesteparkering, antall plasser | Sameiet tilvalg |
| 6 | Section 5 | Det er ikke tinglyst andre heftelser | vs "Følgende andre heftelser..." |
| 7 | Section 19 (Bilag) | Salgsoppgave, Grunnboksutskrift, etc. | Document checklist; broker confirms |

## Loop Specifications

| # | Collection | Variable | Guard Condition | Fallback Text | Used In |
|---|-----------|----------|-----------------|---------------|---------|
| 1 | Model.selgere | selger | Model.selgere.Count > 0 | [Mangler selger] | Parties table, Signature |
| 2 | Model.kjopere | kjoper | Model.kjopere.Count > 0 | [Mangler kjøper] | Parties table, Signature |
| 3 | (optional) Model.kontrakt.omkostninger or Model.kjoperskostnader.alleposter | kostnad | Model.kontrakt.omkostninger.Count > 0 (or equivalent) | [Ingen omkostninger registrert] | Section 2 costs table |

Note: Section 2 costs in source are static rows (Dokumentavgift, Tinglysingsgebyr, etc.). If Vitec provides dynamic cost line items, use foreach; otherwise keep static rows with merge fields per row. Flag for Field Mapper.

## "Mangler Data" Guard List

Fields that should be hidden (or trigger fallback) when Vitec returns "Mangler data":

| Field Path | Guard Expression | Element to Hide |
|-----------|------------------|-----------------|
| selger.fullmektig.navn | != "" && != "Mangler data" | Fullmektig paragraph (selger) |
| kjoper.fullmektig.navn | != "" && != "Mangler data" | Fullmektig paragraph (kjøper) |
| selger.tlf | != "" && != "Mangler data" | Mob: display |
| selger.emailadresse | != "" && != "Mangler data" | E-post: display |
| kjoper.tlf | != "" && != "Mangler data" | Mob: display |
| kjoper.emailadresse | != "" && != "Mangler data" | E-post: display |
| eiendom.heftelserogrettigheter | != "" && != "Mangler data" | Pengeheftelser Alt 1 (show Alt 2 when Mangler data or empty) |
| kontrakt.overtagelse.dato | != "Mangler data" | Overtakelse Alternativ 1 vs Alternativ 2 toggle |

## Condition Expression Syntax Reference

All conditions in this document use the MODEL notation. When implementing in HTML:
- `"` in values → `&quot;`
- `>` in comparisons → `&gt;`
- `<` in comparisons → `&lt;`
- `&&` (AND) → `&amp;&amp;`
- `||` (OR) → `||` (or `&amp;#124;&amp;#124;` if needed)
- Norwegian chars in string values → `\xF8` (ø), `\xE5` (å), `\xE6` (æ)

## Unresolved Logic (NEED REVIEW)

| # | Location | Intent | Why Unresolved |
|---|----------|--------|----------------|
| 1 | Section 1A: "på fradelt tomt fra/med" | Inline text swap | Source shows "fra/med" — tomtetype may determine which word (eiertomt = med?, festetomt = fra?). No reference confirms. |
| 2 | Section 4: Oppgjørsform checkboxes | Two checkboxes for tomt + bolig payment | Source has "For tomten:" and "For boligen:" — both describe prosjekt flow. No field drives checked state; likely broker-interactive. |
| 3 | Section 2: Payment schedule table | Dynamic vs static rows | Source has fixed structure (Vederlag tomt, Delbetaling, Rest kjøpesum, Kjøpesum). May need oppdrag/kontrakt fields — Field Mapper. |
| 4 | Section 2: Omkostninger table | Foreach vs static | Source has static rows. If Model.kontrakt.omkostninger or kjoperskostnader.alleposter exists, use foreach; else static. |

---

**Template-specific notes:**
- Enebolig = single-family house. Section 1A = selveiet (Selveier, Tomt, or other non-Eierseksjon). Section 1B = Eierseksjon (condo/sameie in project).
- "andel i realsameie" option in source is marked red/disabled — exclude from production (or guard with eiendom.eieform if ever supported).
- Pluralization: "Selger" vs "Selgere", "Kjøper" vs "Kjøpere" when Count > 1 — use `Model.selgere.Count > 1` / `Model.kjopere.Count > 1` per dynamic pluralization pattern.
