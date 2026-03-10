# Field Mapping: Generalfullmakt

## Source
- **File:** c:\Users\Adrian\Downloads\13.Generalfullmakt.htm
- **Registry used:** .planning/field-registry.md

## Summary
- **Total placeholders found:** 22
- **Mapped successfully:** 16
- **Unmapped (need review):** 6
- **Monetary (need $.UD):** 0
- **Optional (need vitec-if guard):** 8

## Field Mapping Table

| # | Source Text / Placeholder | Modern Path | $.UD | Guard | Notes |
|---|--------------------------|-------------|------|-------|-------|
| 1 | #matrikkelkommune.oppdrag¤ | [[komplettmatrikkel]] [[eiendom.kommunenavn]] | — | != "" | Matrikkel + commune; per meglerstandard mapping |
| 2 | #adresse.oppdrag¤ | [[eiendom.adresse]] | — | — | Property address |
| 3 | #postnummer.oppdrag¤ | [[eiendom.postnr]] | — | — | Property postal number |
| 4 | #poststed.oppdrag¤ | [[eiendom.poststed]] | — | — | Property postal place |
| 5 | #flettblankeeiere¤ | *(remove)* | — | — | Layout artifact; gates blank rows; remove in conversion |
| 6 | #forsteselger¤ | [[selger.navnutenfullmektigogkontaktperson]] | — | != "" | First seller (limitation clause); single reference |
| 7 | #kundenavn.kontakter¤ | [[avsender.navn]] or [[selger.fullmektig.navn]] | — | != "" | Fullmakt recipient name; see Unmapped |
| 8 | #pnrorgnrb.kontakter¤ | [[avsender.*]] / [[selger.fullmektig.idnummer]] | — | != "" | Fullmakt recipient ID; registry has kjoper.fullmektig.idnummer, selger.fullmektig.idnummer |
| 9 | #hvis[eierformtomt=2311\|2312]settinntekst_fester\|settinntekst_hjemmelshaver¤ | *(Logic Mapper)* | — | vitec-if | Conditional text block; not a merge field |
| 10 | #hvis[eierformtomt=2311\|2312]settinntekst_Fester\|settinntekst_Hjemmelshaver¤ | *(Logic Mapper)* | — | vitec-if | Same conditional; signature block header |
| 11 | #flettblankeeiere¤#nesteeier¤ | [[*selger.navnutenfullmektigogkontaktperson]] | — | foreach | First grantor row; inside selgere loop |
| 12 | #personnummer.kontakter¤ | [[*selger.idnummer]] | — | foreach | Grantor ID; inside selgere loop |
| 13 | #nesteeier¤ (row 2) | [[*selger.navnutenfullmektigogkontaktperson]] | — | foreach | Next grantor; inside loop |
| 14 | #personnummer.kontakter¤ (row 2) | [[*selger.idnummer]] | — | foreach | Grantor ID |
| 15 | #nesteeier¤ (row 3) | [[*selger.navnutenfullmektigogkontaktperson]] | — | foreach | Same pattern |
| 16 | #personnummer.kontakter¤ (row 3) | [[*selger.idnummer]] | — | foreach | Same pattern |
| 17 | #nesteeier¤ (row 4) | [[*selger.navnutenfullmektigogkontaktperson]] | — | foreach | Same pattern |
| 18 | #personnummer.kontakter¤ (row 4) | [[*selger.idnummer]] | — | foreach | Same pattern |
| 19 | #fontsize_10¤ | *(formatting)* | — | — | Font size command; not a merge field; UNMAPPED |
| 20 | #hvis[sjekkliste2901085=4]settinntekst_&lt;br&gt;Ektefelle/partner samtykke...¤ | *(Logic Mapper)* | — | vitec-if | Conditional text; checkbox 4 = spouse consent not relevant |
| 21 | #hvis[sjekkliste2901085=3]settinntekst_&lt;br&gt;Eiendommen tjener ikke...¤ | *(Logic Mapper)* | — | vitec-if | Conditional text; checkbox 3 = property not shared residence |
| 22 | #standard_ektefellesamtykke¤ | *(block placeholder)* | — | — | Standard spouse consent block; UNMAPPED |
| 23 | #standard_vitnepaategning¤ | *(block placeholder)* | — | — | Standard witness attestation block; UNMAPPED |

**Implied (source has blank underscores, not #fields):**
| # | Source Text / Placeholder | Modern Path | $.UD | Guard | Notes |
|---|--------------------------|-------------|------|-------|-------|
| 24 | Sted, dato: __________________ | [[meglerkontor.poststed]] [[dagensdato]] | — | != "" | Place and date; optional if manually filled |

$.UD values: `YES` (wrap in $.UD()), `—` (not monetary)

Guard values:
- `—` — always present, no guard needed
- `!= ""` — optional, hide when empty
- `foreach` — inside a vitec-foreach loop, use [[*field]]

## Collections (vitec-foreach candidates)

| Collection Path | Loop Variable | Fields Inside | Guard |
|----------------|---------------|---------------|-------|
| Model.selgere | selger | navnutenfullmektigogkontaktperson, idnummer | Count > 0 |

**Note:** The document uses selgere as Fullmaktsgiver (grantors of the power of attorney). The conditional header "Fester" vs "Hjemmelshaver" (eierformtomt=2311|2312) suggests hjemmelshaver may apply for some property types. If Logic Mapper determines hjemmelshaver context, use `Model.hjemmelshavere` with `[[*hjemmelshaver.navnutenfullmektigogkontaktperson]]` and `[[*hjemmelshaver.idnummer]]`.

## Monetary Fields ($.UD required)

None in this template.

## Optional Fields (need vitec-if guard)

| Field Path | Reason |
|-----------|--------|
| [[komplettmatrikkel]] [[eiendom.kommunenavn]] | Matrikkel/commune may be empty for some property types |
| [[selger.navnutenfullmektigogkontaktperson]] | First seller reference may be empty |
| [[avsender.navn]] / fullmektig fields | Fullmakt recipient may vary |
| [[meglerkontor.poststed]] [[dagensdato]] | Sted/dato may be manually filled |
| #standard_ektefellesamtykke¤ | Conditional; shown only when spouse consent required |
| #standard_vitnepaategning¤ | Conditional; shown only when witness attestation required |
| settinntekst blocks (sjekkliste2901085) | Mutually exclusive; one of 3 or 4 applies |

## Unmapped Fields (NEED HUMAN REVIEW)

| # | Source Text | Context in Document | Attempted Match | Confidence |
|---|-------------|---------------------|-----------------|------------|
| 1 | #kundenavn.kontakter¤ | Grant clause: "Det gis herved X ugjenkallelig generalfullmakt"; X = recipient of power | [[avsender.navn]] when megler receives; [[selger.fullmektig.navn]] when owners' fullmektig | Low — "kontakter" is legacy roles-table; recipient role varies |
| 2 | #pnrorgnrb.kontakter¤ | Same; recipient's person/org number | [[selger.fullmektig.idnummer]] or [[meglerkontor.orgnr]] | Low — depends on recipient identity |
| 3 | #fontsize_10¤ | Font size formatting before Section 7 | Formatting command; not in registry | — |
| 4 | #standard_ektefellesamtykke¤ | Standard spouse consent section | Document fragment/snippet; not a merge field | — |
| 5 | #standard_vitnepaategning¤ | Standard witness attestation section | Document fragment/snippet; not a merge field | — |
| 6 | settinntekst_fester / settinntekst_hjemmelshaver | Conditional role label (Fester vs Hjemmelshaver) | Logic Mapper; not a data field | — |

---

*Mapping completed per FORMAT_fields.md. Logic Mapper handles vitec-if conditions. Structure Analyzer handles document structure. No monetary fields. No build script generated.*
