# Logic Mapping: Kjøpekontrakt landbrukseiendom

## Source
- **File:** c:\Users\Adrian\Downloads\14.Kjøpekontrakt landbrukseiendom.htm
- **References used:** scripts/_analysis/FORMAT_logic.md, VITEC-IF-DEEP-ANALYSIS.md, PRODUCTION-TEMPLATE-PIPELINE.md Section 5, .planning/vitec-html-ruleset/10-property-conditionals.md, scripts/golden standard/kjøpekontrakt forbruker.html

## Summary
- **vitec-if conditions:** 14
- **vitec-foreach loops:** 4
- **Checkbox groups:** 4 (3 broker-interactive groups + 1 pengeheftelser group)
- **Mutually exclusive sections:** 3 groups
- **"Mangler data" guards:** 9

## Conditional Branches

### Oppdragstype Conditionals

| # | Element | Condition | Scope | Notes |
|---|---------|-----------|-------|-------|
| 1 | p | Model.oppdrag.hovedtype == "Oppgj\xF8rsoppdrag" | Preamble | "Ved oppgjørsoppdrag gjelder følgende, særskilte ansvarsbegrensning..." — Show oppgjør disclaimer paragraph only when assignment is Oppgjørsoppdrag |

### Optional Field Guards

| # | Element | Condition | Content When True | Content When False |
|---|---------|-----------|-------------------|-------------------|
| 1 | span/p | Model.hjemmelshaver.navn != "" && Model.hjemmelshaver.navn != "Mangler data" | Hjemmelshaver foreach/list | Fallback (see Loop Specifications) |
| 2 | span | Model.takstdato.oppdrag != "" && != "Mangler data" | "datert [[takstdato]]" | Omit or show insert field |
| 3 | span | Model.forsikringsselskap.oppdrag != "" && != "Mangler data" | "[[forsikringsselskap]]" | (hidden or insert) |

Note: Contact fields (mobil, email) inside foreach use `selger.tlf != ""` / `kjoper.emailadresse != ""` per VITEC-IF-DEEP-ANALYSIS Pattern C. Add `!= "Mangler data"` for defensive guard if desired.

### Alternative Sections (Mutually Exclusive) — Broker-Interactive

| Group | Option | Condition | Location |
|-------|--------|-----------|----------|
| Fordelingsregnskap (§3.6) | Alternativ A | Broker selects via checkbox/radio | "Fordelingsregnskap settes opp av selger per overtagelsesdato..." |
| Fordelingsregnskap (§3.6) | Alternativ B | Broker selects (mutually exclusive with A) | "Senest 30 dager etter overtagelse skal selger sende til kjøper..." |
| Konsesjonsrisiko (§4.2) | Alternativ A | Broker selects | "Hver av partene kan i så fall fri seg fra avtalen ved skriftlig melding til megler." |
| Konsesjonsrisiko (§4.2) | Alternativ B | Broker selects (mutually exclusive with A) | "Partene har da avtalt at avtalen likevel skal gjelde, men til den høyeste pris..." |
| Odel (§5) | Alternativ A | Broker selects | "Det hviler ikke odel på eiendommen." |
| Odel (§5) | Alternativ B | Broker selects | "Alle kjente odelsberettigede har fraskrevet seg odelsretten..." |
| Odel (§5) | Alternativ C | Broker selects (one of three) | "De odelsberettigede har ikke fraskrevet seg sin odelsrett..." |

**Implementation:** Use broker-interactive radio groups with `<input type="radio" name="rbl_fordelingsregnskap" />`, `<input type="radio" name="rbl_konsesjonsrisiko" />`, `<input type="radio" name="rbl_odel" />`. Parent element needs `data-toggle="buttons"`. Per VITEC-IF-DEEP-ANALYSIS Section 3: no vitec-if drives state — broker toggles at runtime.

### Checklist-Based Conditionals (sjekkliste2901085)

| # | Element | Condition | Content When True | Content When False |
|---|---------|-----------|-------------------|-------------------|
| 1 | div/block | Model.oppdrag.sjekkliste2901085 == "1" | #standard_ektefellesamtykke¤ block | (hidden) |
| 2 | div/block | Model.oppdrag.sjekkliste2901085 == "2" | #standard_partnersamtykke¤ block | (hidden) |

**Mutually exclusive:** Value 1 = ektefellesamtykke (spouse consent), value 2 = partnersamtykke (partner consent). Only one renders. When neither 1 nor 2, neither block shows.

**Note:** #standard_oppgjorsinstruks¤ has no #hvis in source — render unconditionally after the conditional blocks.

## Checkbox State Logic

### Broker-Interactive Checkboxes

| # | Location | Label Text | Notes |
|---|----------|------------|-------|
| 1 | §5 Pengeheftelser | Eiendommen overdras fri for pengeheftelser. | Option (a) — mutually exclusive with #2 |
| 2 | §5 Pengeheftelser | Eiendommen overdras fri for pengeheftelser, med unntak av følgende pantedokumenter: | Option (b) — mutually exclusive with #1 |
| 3 | §3.6 Driftsutgifter | Alternativ A (fordelingsregnskap) | Radio group — broker selects A or B |
| 4 | §3.6 Driftsutgifter | Alternativ B (fordelingsregnskap) | Radio group |
| 5 | §4.2 Konsesjonsrisiko | Alternativ A (fri seg fra avtalen) | Radio group — broker selects A or B |
| 6 | §4.2 Konsesjonsrisiko | Alternativ B (avtalen likevel gjelder) | Radio group |
| 7 | §5 Odel | Alternativ A (ikke odel) | Radio group — broker selects A, B, or C |
| 8 | §5 Odel | Alternativ B (fraskrevet) | Radio group |
| 9 | §5 Odel | Alternativ C (ikke fraskrevet, risiko) | Radio group |

**Pengeheftelser:** Use two broker-interactive checkboxes (or radio if strictly one-of-two). Per source: Unicode &#9744; (☐) — replace with SVG checkbox pattern. Broker checks the one that applies.

**A/B/C alternatives:** Per user instructions and PRODUCTION-TEMPLATE-PIPELINE Section 8: "Stryk det alternativ som ikke passer" indicates broker strikes through — implement as radio groups with `<input type="radio">` so broker selects which applies.

## Loop Specifications

| # | Collection | Variable | Guard Condition | Fallback Text | Used In |
|---|-----------|----------|-----------------|---------------|---------|
| 1 | Model.selgere | selger | Model.selgere.Count > 0 | [Mangler selger] | Section 1 (Mellom partene), Signature |
| 2 | Model.kjopere | kjoper | Model.kjopere.Count > 0 | [Mangler kjøper] | Section 1, Signature |
| 3 | Model.hjemmelshavere | hjemmelshaver | Model.hjemmelshavere.Count > 0 | Use selgere (per kjøpekontrakt forbruker) OR insert field | §1 "Hjemmelshaver til eiendommen er:" |
| 4 | Model.kjoperskostnader.alleposter (or equivalent) | kostnad | Model.kjoperskostnader.alleposter.Count > 0 | (empty table or "[Ingen omkostninger]") | §2 costs table (#bilagslinjerny_kjøper,1,0,0,1¤) |

### Loop 3 (Hjemmelshavere) — Fallback Logic

Per VITEC-IF-DEEP-ANALYSIS Pattern B and kjøpekontrakt forbruker:

```html
<span vitec-if="Model.hjemmelshaver.navn != &quot;Mangler data&quot;">
  <span vitec-foreach="hjemmelshaver in Model.hjemmelshavere">
    [[*hjemmelshaver.navn]] ([[*hjemmelshaver.fdato_orgnr]])<span class="separator">, </span>
  </span>
</span>
<span vitec-if="Model.hjemmelshaver.navn == &quot;Mangler data&quot;">
  <span vitec-foreach="selger in Model.selgere">[[*selger.navnutenfullmektigogkontaktperson]]<span class="separator">, </span></span>
</span>
```

Source has `#forstehjemmelshaver¤# og ;nesteeier¤` — maps to hjemmelshavere foreach with separator. First + rest pattern handled by foreach.

### Loop 1 & 2 (Selger/Kjøper) — Inner Fields

- **Name:** [[*selger.navnutenfullmektigogkontaktperson]] / [[*kjoper.navnutenfullmektigogkontaktperson]]
- **Address:** [[*selger.gatenavnognr]], [[*selger.postnr]] [[*selger.poststed]] (kunadresse.kontakter)
- **Mobil:** [[*selger.tlf]] / [[*kjoper.tlf]] — guard: `selger.tlf != ""`
- **E-post:** [[*selger.emailadresse]] / [[*kjoper.emailadresse]] — guard: `selger.emailadresse != ""`
- **Separator:** " / " between Mob and E-post when both present (per PRODUCTION-TEMPLATE-PIPELINE Pattern)

## "Mangler Data" Guard List

Fields that should be hidden (not just empty) when Vitec returns "Mangler data":

| Field Path | Guard Expression | Element to Hide |
|-----------|------------------|-----------------|
| hjemmelshaver.navn | != "" && != "Mangler data" | Hjemmelshaver paragraph (use selgere fallback when "Mangler data") |
| takstdato.oppdrag | != "" && != "Mangler data" | "datert #takstdato.oppdrag¤" — show insert when missing |
| forsikringsselskap.oppdrag | != "" && != "Mangler data" | §9 forsikringsselskap display |
| kontrakt.klientkonto | != "" && != "Mangler data" | Klientkonto nr. in §3.2 (or use insert as fallback) |
| stedsnavndokument.avdelinger | != "" && != "Mangler data" | Sted/dato in signature |
| fokuserdagbok_kontraktsmøte | != "" && != "Mangler data" | Dato in signature |
| selger.fullmektig.navn | != "" && != "Mangler data" | Fullmektig paragraph (if present) |
| kjoper.fullmektig.navn | != "" && != "Mangler data" | Fullmektig paragraph (if present) |
| adresse.oppdrag | != "" && != "Mangler data" | Salgsobjekt address in §1 |

## Insert Fields (Fill-in Blanks)

| Location | data-label | Notes |
|----------|------------|-------|
| §1 | "Gårdskart dato" | "eller utskrift av gårdskart med arealopplysninger datert …………" |
| §2 | "Eiendomsverdi" | "Av kjøpesummen utgjør kroner ….………. vederlag for selve eiendommen" |
| §2 | "Konsesjonsgebyr" | "Konsesjonsgebyret, stort kr ……… faktureres kjøper direkte" |
| §3.2 | "Klientkontonummer" | "meglers klientkonto nr. ………………………" |
| §5 | "Grunnbok dato" | "En bekreftet utskrift av eiendommens grunnbok datert ……." |
| §10 bilag 3 | "Dagboknummer/dokumentnummer" | "dagboknummer/dokumentnummer:…………" |
| §10 bilag 4 | "Takst/boligsalgsrapport dato" | "Takst/boligsalgsrapport datert …………" |
| §10 bilag 14 | "Annet" | "Annet: ……………………………………………." |
| Signature | "Signatur" | Dotted lines for Kjøper/Selger signing |

## Condition Expression Syntax Reference

All conditions in this document use MODEL notation. When implementing in HTML:
- `"` → `&quot;`
- `>` → `&gt;`
- `<` → `&lt;`
- `&&` → `&amp;&amp;`
- Norwegian chars: `\xF8` (ø), `\xE5` (å), `\xE6` (æ)

## Unresolved Logic (NEED REVIEW)

| # | Location | Intent | Why Unresolved |
|---|----------|--------|----------------|
| 1 | §2 #bilagslinjerny_kjøper,1,0,0,1¤ | Cost line items table | Legacy Vitec syntax; exact collection path (kjoperskostnader.alleposter vs bilagslinje*) unknown. Builder: verify against field registry or Alle-flettekoder. |
| 2 | sjekkliste2901085 | Exact Model path | generalfullmakt uses Model.oppdrag.sjekkliste2901085; may be sjekkliste["2901085"] or oppdrag.sjekkliste_2901085. Builder: verify. |

All other logic fully mapped.
