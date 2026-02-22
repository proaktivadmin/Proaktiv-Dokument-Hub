# Field Mapping: Kjopekontrakt_prosjekt_enebolig

## Source
- **File:** scripts/source_htm/Kjopekontrakt_prosjekt_enebolig.htm
- **Registry used:** .planning/field-registry.md

## Summary
- **Total placeholders found:** 21
- **Mapped successfully:** 14
- **Unmapped (need review):** 5
- **Structural/foreach markers:** 2
- **Monetary (need $.UD):** 2
- **Optional (need vitec-if guard):** 5

## Field Mapping Table

| # | Source Text / Placeholder | Modern Path | $.UD | Guard | Notes |
|---|--------------------------|-------------|------|-------|-------|
| 1 | #oppdragsnummer.oppdrag¤ | [[oppdrag.nr]] | — | — | Always present; Oppdragsnr. |
| 2 | #omsetningsnummer.oppdrag¤ | [[kontrakt.formidling.nr]] | — | — | Omsetningsnr. |
| 3 | #salgssum.oppdrag¤ (2×) | [[kontrakt.kjopesum]] | YES | — | Kjøpesum; Monetary |
| 4 | #eiere¤ | *(structural)* | — | foreach | Section marker → vitec-foreach="selger in Model.selgere" |
| 5 | #flettblankeeiere¤ | *(structural)* | — | foreach | Line separator between party rows (inside loop) |
| 6 | #forsteeier¤ | [[*selger.navnutenfullmektigogkontaktperson]] | — | foreach | Inside selger loop |
| 7 | #kunadresse.kontakter¤ | [[*selger.gatenavnognr]], [[*selger.postnr]] [[*selger.poststed]] | — | foreach | Address inside loop |
| 8 | ;mobil.kontakter& ¤ | [[*selger.hovedtlf]] / [[*kjoper.hovedtlf]] | — | foreach, != "" | Phone; optional; inside loop |
| 9 | ;email.kontakter¤ | [[*selger.hovedepost]] / [[*kjoper.hovedepost]] | — | foreach, != "" | E-post; optional; inside loop |
| 10 | #nyeeiere¤ | *(structural)* | — | foreach | Section marker → vitec-foreach="kjoper in Model.kjopere" |
| 11 | #forstenyeier¤ | [[*kjoper.navnutenfullmektigogkontaktperson]] | — | foreach | Inside kjoper loop |
| 12 | #standard_kontaktoppgjor¤ | — | — | — | **UNMAPPED** — Oppgjørsavdeling contact block |
| 13 | #klientkonto.avdelinger¤ | [[kontrakt.klientkonto]] | — | != "" | Klientkonto; registry has kontrakt.klientkonto only |
| 14 | #betalingsmerknadkjoper.oppdrag¤ | [[kontrakt.kid]] or [[kontrakt.klientkontoogkid]] | — | != "" | KID/betalingsmerknad; optional |
| 15 | #fullmaktsinnehavereb_kjoper¤ | — | — | != "" | **UNMAPPED** — Kjøpers fullmaktsinnehaver (signature block) |

$.UD values: `YES` (wrap in $.UD()), `—` (not monetary)

Guard values:
- `—` — always present, no guard needed
- `!= ""` — optional, hide when empty
- `foreach` — inside a vitec-foreach loop, use [[*field]]

## Collections (vitec-foreach candidates)

| Collection Path | Loop Variable | Fields Inside | Guard |
|-----------------|---------------|---------------|-------|
| Model.selgere | selger | navnutenfullmektigogkontaktperson, gatenavnognr, postnr, poststed, hovedtlf, hovedepost | Count > 0 |
| Model.kjopere | kjoper | navnutenfullmektigogkontaktperson, gatenavnognr, postnr, poststed, hovedtlf, hovedepost | Count > 0 |

**Note:** The source uses legacy markers `#eiere¤`, `#forsteeier¤`, `#flettblankeeiere¤`, `#kunadresse.kontakter¤`, `;mobil.kontakter`, `;email.kontakter` for the selger block, and `#nyeeiere¤`, `#forstenyeier¤` plus same address/contact patterns for the kjoper block. These map to the roles-table pattern with `vitec-foreach` on Model.selgere and Model.kjopere.

## Monetary Fields ($.UD required)

| Field Path | Context |
|------------|---------|
| [[kontrakt.kjopesum]] | Kjøpesum (appears twice: main display and table total) |

## Unmapped Fields (NEED HUMAN REVIEW)

| # | Source Text | Context in Document | Attempted Match | Confidence |
|---|-------------|---------------------|-----------------|------------|
| 1 | #standard_kontaktoppgjor¤ | Section 4 "Oppgjør" – contact details for oppgjørsavdelingen | — | — |
| 2 | #fullmaktsinnehavereb_kjoper¤ | Section 20 "Signatur" – kjøper(e) signature cell | [[kjoper.fullmektig.navn]]? | Low – different semantics |
| 3 | #klientkonto.avdelinger¤ | Section 4 – klientkonto text | [[kontrakt.klientkonto]] | Medium – registry has kontrakt.klientkonto; ".avdelinger" may be department-specific variant |
| 4 | #betalingsmerknadkjoper.oppdrag¤ | Section 4 – KID/betalingsmerknad for kjøper | [[kontrakt.kid]] or [[kontrakt.klientkontoogkid]] | Medium – logical match |
| 5 | ;mobil.kontakter / ;email.kontakter | Semicolon-prefix; inside party blocks | [[*selger.hovedtlf]], [[*selger.hovedepost]] | Medium – Alle-flettekoder uses *selger.tlf, *selger.emailadresse in foreach; registry has hovedtlf/hovedepost for single entity |

## Implied Fields (no merge syntax in source)

The following appear as manual fill blanks or boilerplate; no merge fields present:

- **Leilighetsnr.:** `…………..` — could use [[eiendom.leilighetsnr]] if available for prosjekt
- **Felleskostnader første driftsår:** `……` — could use [[eiendom.fellesutgifter]]
- **Prosjekt enheter:** `…………………` — could use [[oppdrag.prosjekt.antallenheter]]
- **Overtakelsesdato:** `(DATO)` — could use [[kontrakt.overtagelse.dato]]
- **Kjøpesum inkl. omkostninger** — sum row; no placeholder; typically calculated from [[kontrakt.kjopesum]] + omkostninger, or [[kontrakt.kjopesumogomkostn]] if available for prosjekt

## Cross-Reference: Alle-flettekoder-25.9.md

Searched for: oppdrag.nr, kontrakt.formidling.nr, kontrakt.kjopesum, kontrakt.klientkonto, selger.*, kjoper.*. All confirmed. Legacy names `oppdragsnummer`, `omsetningsnummer`, `salgssum` are not in Alle-flettekoder; mapping follows field-registry and production template (Kjopekontrakt_prosjekt_leilighet_PRODUCTION.html) conventions.
