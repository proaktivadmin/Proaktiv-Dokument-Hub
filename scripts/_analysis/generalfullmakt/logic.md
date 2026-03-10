# Logic Mapping: Generalfullmakt

## Source
- **File:** `c:\Users\Adrian\Downloads\13.Generalfullmakt.htm`
- **References used:** vitec-html-ruleset/03-conditional-logic.md, 10-property-conditionals.md, VITEC-IF-DEEP-ANALYSIS.md

## Summary
- **vitec-if conditions:** 6
- **vitec-foreach loops:** 1 (owners/fullmaktsgivere)
- **Checkbox groups:** 0 (no broker-interactive checkboxes)
- **Mutually exclusive sections:** 1 (spouse consent alternatives)
- **"Mangler data" guards:** 3

## Conditional Branches

### Property-Type Conditionals (eierformtomt)

| # | Element | Condition | Scope | Notes |
|---|---------|-----------|-------|-------|
| 1 | span | (Model.eiendom.eierformtomt == "2311" \|\| Model.eiendom.eierformtomt == "2312") | Body text, limitation clause | When true → "fester"; when false → "hjemmelshaver". Source: #hvis[eierformtomt=2311\|2312]settinntekst_fester\|settinntekst_hjemmelshaver¤ |
| 2 | span | (Model.eiendom.eierformtomt == "2311" \|\| Model.eiendom.eierformtomt == "2312") | Signature table header | When true → "Fester"; when false → "Hjemmelshaver". Source: #hvis[eierformtomt=2311\|2312]settinntekst_Fester\|settinntekst_Hjemmelshaver¤ |

**Field mapping note:** Source uses numeric Kartverket codes 2311 and 2312 (feste/land lease). If Vitec Model exposes `eiendom.tomtetype` (eiertomt/festetomt) instead of numeric codes, use:
- **Alternative:** `Model.eiendom.tomtetype == "festetomt"` for "fester" branch; `Model.eiendom.tomtetype != "festetomt"` for "hjemmelshaver" branch. (See 10-property-conditionals.md, 14-no-touch-templates.md)

### Checklist-Based Conditionals (sjekkliste2901085)

| # | Element | Condition | Content When True | Content When False |
|---|---------|-----------|-------------------|-------------------|
| 1 | p or div | Model.oppdrag.sjekkliste2901085 == "4" | "Ektefelle/partner samtykke er ikke aktuelt, ettersom eiendommen eies sammen" | (hidden) |
| 2 | p or div | Model.oppdrag.sjekkliste2901085 == "3" | "Eiendommen tjener ikke til felles bopæl for ektefeller/registrerte partnere" | (hidden) |

**Mutually exclusive:** When sjekkliste2901085 is 4, show alternative 1. When 3, show alternative 2. When neither 3 nor 4, the `#standard_ektefellesamtykke¤` block renders (standard spouse consent). These three options are mutually exclusive.

### Standard Blocks (Vitec System Macros)

| Block | Location | Notes |
|-------|----------|-------|
| #standard_ektefellesamtykke¤ | Section 7 | Renders when sjekkliste2901085 is not 3 or 4. Internal conditional logic is Vitec-provided; do not replicate. |
| #standard_vitnepaategning¤ | Section 7 | Witness attestation block. Vitec system macro. |

## Optional Field Guards

No optional field guards required for this template. Merge fields (matrikkelkommune, adresse, kundenavn, pnrorgnrb, personnummer) are core to the document; hide only if "Mangler data" sentinel — see Mangler Data Guard List.

## Alternative Sections (Mutually Exclusive)

| Group | Option | Condition | Location |
|-------|--------|-----------|----------|
| Spouse consent | Alternativ 1 (co-owned) | Model.oppdrag.sjekkliste2901085 == "4" | Section 7 |
| Spouse consent | Alternativ 2 (not joint residence) | Model.oppdrag.sjekkliste2901085 == "3" | Section 7 |
| Spouse consent | Standard block | (Model.oppdrag.sjekkliste2901085 != "4" &amp;&amp; Model.oppdrag.sjekkliste2901085 != "3") | Section 7 |

## Checkbox State Logic

### Data-Driven Checkboxes

None. The sjekkliste2901085 conditions drive **text replacement**, not checkbox checked/unchecked state. No checkbox UI elements in source.

### Broker-Interactive Checkboxes

None.

## Loop Specifications

| # | Collection | Variable | Guard Condition | Fallback Text | Used In |
|---|-----------|----------|-----------------|---------------|---------|
| 1 | Model.selgere | selger | Model.selgere.Count &gt; 0 | [Mangler fullmaktsgivere] | Section 3 (intro), Section 6 (signature block) |

**Implementation notes:**
- **Source pattern:** `#flettblankeeiere¤#forsteselger¤` in intro; `#nesteeier¤` in signature rows. The first owner uses forsteselger context (#kundenavn.kontakter¤, #pnrorgnrb.kontakter¤); subsequent owners use nesteeier (#nesteeier¤, #personnummer.kontakter¤) in 4 fixed table rows.
- **Collection mapping:** Document uses mixed terminology (forsteselger, nesteeier, flettblankeeiere). In "Fullmakt selger" context (doc cat 22), grantors are typically Model.selgere. If a dedicated Model.eiere or Model.fullmaktsgivere exists, Field Mapper should confirm.
- **Vitec-foreach placement:** Wrap the signature table body in `vitec-foreach="selger in Model.selgere"` on `<tbody>` or per-row `<tr>`. Fallback: `<em vitec-if="Model.selgere.Count == 0">[Mangler fullmaktsgivere]</em>`.

## "Mangler Data" Guard List

Fields that should be hidden when Vitec returns "Mangler data":

| Field Path | Guard Expression | Element to Hide |
|-----------|------------------|-----------------|
| sted (place) | Model.oppdrag.sted != "" &amp;&amp; Model.oppdrag.sted != "Mangler data" | Sted portion of "Sted, dato" |
| dato (date) | Model.oppdrag.dato != "" &amp;&amp; Model.oppdrag.dato != "Mangler data" | Dato portion of "Sted, dato" |
| kundenavn.kontakter | Model.selger.navn != "" &amp;&amp; Model.selger.navn != "Mangler data" | Grantor name in intro paragraph |

**Note:** If sted/dato are rendered as a single merged block, guard the entire "Sted, dato:" line. Known "Mangler data" fields per 03-conditional-logic.md: selger.tlf, kjoper.tlf, mottaker.visning.dato, grunneier.navn, hjemmelshaver.navn. Contact/party name fields may also return this sentinel.

## Condition Expression Syntax Reference

All conditions in this document use the MODEL notation. When implementing in HTML:
- `"` in values → `&quot;`
- `>` in comparisons → `&gt;`
- `<` in comparisons → `&lt;`
- `&&` (AND) → `&amp;&amp;`
- `||` (OR) → `\|\|` (escape if needed in attribute)
- Norwegian chars in string values → `\xF8` (ø), `\xE5` (å), `\xE6` (æ)

## Unresolved Logic (NEED REVIEW)

| # | Location | Intent | Why Unresolved |
|---|----------|--------|----------------|
| 1 | eierformtomt | Use "fester" when property is festetomt (land lease) | Source uses numeric codes 2311|2312; Model may expose eiendom.tomtetype ("festetomt") or eiendom.eierformtomt (numeric). Builder: verify field path. |
| 2 | sjekkliste2901085 | Checklist value drives spouse consent text | Exact Model path for checklist 2901085 not found in references. May be Model.oppdrag.sjekkliste["2901085"] or similar. Builder: verify. |

## Implementation Checklist

1. **eierformtomt (2 places):** Implement dual span with vitec-if for fester/hjemmelshaver (lowercase in body, title case in header).
2. **sjekkliste2901085 (2 branches + default):** Three blocks — value 4, value 3, and standard_ektefellesamtykke as fallback when neither.
3. **standard_ektefellesamtykke, standard_vitnepaategning:** Preserve as Vitec system blocks; do not convert to vitec-if.
4. **Owner loop:** Replace #forsteselger¤/#nesteeier¤ with vitec-foreach on Model.selgere (or confirmed collection), guard with Count &gt; 0.
5. **Mangler data:** Apply double-guards to sted, dato, and grantor name if those fields can return "Mangler data".
