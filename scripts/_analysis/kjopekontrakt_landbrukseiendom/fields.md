# Field Mapping: Kjopekontrakt landbrukseiendom

## Source
- **File:** c:\Users\Adrian\Downloads\14.Kjøpekontrakt landbrukseiendom.htm
- **Registry used:** .planning/field-registry.md

## Summary
- **Total placeholders found:** 37
- **Mapped successfully:** 30
- **Unmapped (need review):** 5
- **Layout artifacts (remove):** 2
- **Monetary (need $.UD):** 2
- **Optional (need vitec-if guard):** 8
- **Conditional includes:** 3

## Field Mapping Table

| # | Source Text / Placeholder | Modern Path | $.UD | Guard | Notes |
|---|--------------------------|-------------|------|-------|-------|
| 1 | #navn.firma¤ | [[meglerkontor.navn]] | — | — | Megler firm name |
| 2 | #organisasjonsnummer.firma¤ | [[meglerkontor.orgnr]] | — | — | Org number |
| 3 | #type_oppdrag.oppdrag¤ | [[oppdrag.type]] | — | — | Oppdragstype |
| 4 | #type_eierformbygninger.oppdrag¤ | [[eiendom.eieform]] | — | — | Eierform bygninger |
| 5 | #type_eierformtomt.oppdrag¤ | [[eiendom.eieform]] | — | — | Eierform tomt (source has both; modern uses single eieform) |
| 6 | #oppdragsnummer.oppdrag¤ | [[oppdrag.nr]] | — | — | Oppdragsnr |
| 7 | #omsetningsnummer.oppdrag¤ | [[kontrakt.formidling.nr]] | — | — | Omsetningsnr |
| 8 | #eiere¤ | *(structural)* | — | foreach | Section marker → vitec-foreach="selger in Model.selgere" |
| 9 | #flettblankeeiere¤ | *(remove)* | — | — | Layout artifact, no content |
| 10 | #forsteeier¤ | [[*selger.navnutenfullmektigogkontaktperson]] | — | foreach | Inside selger loop |
| 11 | #kunadresse.kontakter¤ (selger block) | [[*selger.gatenavnognr]], [[*selger.postnr]] [[*selger.poststed]] | — | foreach | Address inside selger loop |
| 12 | #Mob: ;mobil.kontakter& ¤ (selger block) | Mob: [[*selger.hovedtlf]] | — | foreach, != "" | Phone; optional; prefix "Mob: " |
| 13 | #E-post: ;email.kontakter¤ (selger block) | E-post: [[*selger.hovedepost]] | — | foreach, != "" | Email; optional; prefix "E-post: " |
| 14 | #nyeeiere¤ | *(structural)* | — | foreach | Section marker → vitec-foreach="kjoper in Model.kjopere" |
| 15 | #forstenyeier¤ | [[*kjoper.navnutenfullmektigogkontaktperson]] | — | foreach | Inside kjoper loop |
| 16 | #kunadresse.kontakter¤ (kjoper block) | [[*kjoper.gatenavnognr]], [[*kjoper.postnr]] [[*kjoper.poststed]] | — | foreach | Address inside kjoper loop |
| 17 | #Mob: ;mobil.kontakter& ¤ (kjoper block) | Mob: [[*kjoper.hovedtlf]] | — | foreach, != "" | Phone; optional |
| 18 | #E-post: ;email.kontakter¤ (kjoper block) | E-post: [[*kjoper.hovedepost]] | — | foreach, != "" | Email; optional |
| 19 | #adresse.oppdrag¤ | [[eiendom.adresse]] | — | — | Property address |
| 20 | #matrikkelkommune.oppdrag¤ | [[komplettmatrikkel]] | — | — | Cadastral reference; may combine with [[eiendom.kommunenavn]] |
| 21 | #seksjonsbrok.oppdrag¤ | **UNMAPPED** | — | — | Seksjonsbrøk; see Unmapped |
| 22 | #ideellandel.oppdrag¤ | **UNMAPPED** | — | — | Ideell andel; see Unmapped |
| 23 | #forstehjemmelshaver¤ | [[*hjemmelshaver.navn]] (first) | — | foreach | First title holder; Model.hjemmelshavere |
| 24 | #nesteeier¤ | [[*hjemmelshaver.navn]] (second) | — | foreach | Second title holder; same loop, separator " og " |
| 25 | #takstdato.oppdrag¤ | [[eiendom.takstdato]] | — | — | Takst/valuation date; cf. golden standard |
| 26 | #salgssum.oppdrag¤ | [[kontrakt.kjopesum]] | YES | — | Kjøpesum; monetary |
| 27 | #bilagslinjerny_kjøper,1,0,0,1¤ | *(structural)* | — | foreach | Buyer cost lines → vitec-foreach="kostnad in Model.kjoperskostnader.poster" (or alleposter) |
| 28 | *(implied: cost rows)* | [[*kostnad.beskrivelse]], [[*kostnad.belop]] | YES | foreach | Inside kostnad loop; belop needs $.UD |
| 29 | #forsikringsselskap.oppdrag¤ | [[forsikring.selskap]] | — | != "" | Insurance company; optional |
| 30 | #id_avdelinger.sesjoner¤ | **UNMAPPED** | — | — | Dept ID/session; see Unmapped |
| 31 | #stedsnavndokument.avdelinger¤ | [[meglerkontor.poststed]] | — | — | Signing place; cf. golden standard "Sted" |
| 32 | #fokuserdagbok_kontraktsmøte¤ | [[kontrakt.dato]] | — | — | Contract meeting date |
| 33 | #fullmaktsinnehavereb_kjoper¤ | [[kjoper.fullmektig.navn]] | — | != "" | Buyer's representative; optional |
| 34 | #fullmaktsinnehavereb_selger¤ | [[selger.fullmektig.navn]] | — | != "" | Seller's representative; optional |
| 35 | #hvis[sjekkliste2901085=1]standard_ektefellesamtykke¤ | *(conditional block)* | — | vitec-if | Logic Mapper: sjekkliste2901085 == 1 |
| 36 | #hvis[sjekkliste2901085=2]standard_partnersamtykke¤ | *(conditional block)* | — | vitec-if | Logic Mapper: sjekkliste2901085 == 2 |
| 37 | #standard_oppgjorsinstruks¤ | *(conditional block)* | — | — | Standard oppgjørsinstruks clause block |

$.UD values: `YES` (wrap in $.UD()), `—` (not monetary)

Guard values:
- `—` — always present, no guard needed
- `!= ""` — optional, hide when empty
- `foreach` — inside a vitec-foreach loop, use [[*variable.field]]
- `vitec-if` — conditional include; expression is Logic Mapper's job

## Collections (vitec-foreach candidates)

| Collection Path | Loop Variable | Fields Inside | Guard |
|-----------------|---------------|---------------|-------|
| Model.selgere | selger | navnutenfullmektigogkontaktperson, gatenavnognr, postnr, poststed, hovedtlf, hovedepost | Count > 0 |
| Model.kjopere | kjoper | navnutenfullmektigogkontaktperson, gatenavnognr, postnr, poststed, hovedtlf, hovedepost | Count > 0 |
| Model.hjemmelshavere | hjemmelshaver | navn (source uses forstehjemmelshaver + nesteeier with " og ") | Count > 0 |
| Model.kjoperskostnader.poster | kostnad | beskrivelse, belop | Count > 0 |

**Note:** Source uses `#bilagslinjerny_kjøper,1,0,0,1¤` — legacy format for buyer cost line items. Map to `vitec-foreach="kostnad in Model.kjoperskostnader.poster"` (or `alleposter` per docs). Inner fields: `[[*kostnad.beskrivelse]]`, `$.UD([[*kostnad.belop]])`.

## Monetary Fields ($.UD required)

| Field Path | Context |
|------------|---------|
| [[kontrakt.kjopesum]] | Kjøpesum (§ 2) |
| [[*kostnad.belop]] | Cost item amounts (inside foreach) |

## Unmapped Fields (NEED HUMAN REVIEW)

| # | Source Text | Context in Document | Attempted Match | Confidence |
|---|-------------|---------------------|-----------------|------------|
| 1 | #seksjonsbrok.oppdrag¤ | § 1 Salgsobjekt: "m/#type_eierformtomt.oppdrag¤#, seksjonsbrøk ;seksjonsbrok.oppdrag¤#" | [[*matrikkel.andel]] (inside Model.matrikler)? [[komplettmatrikkelutvidet]]? | Low — no direct seksjonsbrok in registry |
| 2 | #ideellandel.oppdrag¤ | § 1: "ideell andel ;ideellandel.oppdrag¤" | Part of [[komplettmatrikkelutvidet]]? [[*matrikkel.andel]]? | Low — ideellandel not in registry |
| 3 | #id_avdelinger.sesjoner¤ | § 10 Bilag / Signatur: "Sted/dato: #id_avdelinger.sesjoner¤#stedsnavndokument..." | [[meglerkontor.internid]]? Department identifier | Low — legacy avdeling/sesjon context |
| 4 | #matrikkelkommune.oppdrag¤ | § 1: Cadastral + kommune | Mapped to [[komplettmatrikkel]] — if source expects separate matrikkel vs kommune, use [[komplettmatrikkel]] + [[eiendom.kommunenavn]] | Medium |
| 5 | standard_ektefellesamtykke / standard_partnersamtykke / standard_oppgjorsinstruks | Conditional clause blocks (no #¤ in output) | Full HTML clause blocks; not merge fields; Logic Mapper handles inclusion | — |

## Conditional Includes (Logic Mapper's job)

| Source Pattern | Condition | Content |
|----------------|-----------|---------|
| #hvis[sjekkliste2901085=1]standard_ektefellesamtykke¤ | sjekkliste2901085 == 1 | Ektefellesamtykke clause |
| #hvis[sjekkliste2901085=2]standard_partnersamtykke¤ | sjekkliste2901085 == 2 | Partnersamtykke clause |
| #standard_oppgjorsinstruks¤ | Always? | Oppgjørsinstruks clause (verify if conditional) |

## Implied Fields (no merge syntax in source)

Manual fill blanks in source; consider adding if data exists:
- **Eiendomsverdi** (kroner ……….): No placeholder; could use calculated or dedicated field if available
- **Klientkonto nr.**: `………………………` — [[kontrakt.klientkonto]] (add if used in § 3.2)
- **Grunnboksdato**: `………..` — [[eiendom.grunnboksdato]]
- **Takst/boligsalgsrapport datert**: `…………` — [[eiendom.takstdato]] or [[eiendom.rapportdato]]
- **Dagboknummer/dokumentnummer**: `…………` — insert field or pant.dagboknr

## Cross-Reference

- **PRODUCTION-TEMPLATE-PIPELINE.md § 4:** oppdragsnummer→oppdrag.nr, omsetningsnummer→kontrakt.formidling.nr, salgssum→kontrakt.kjopesum, fullmaktsinnehavereb_kjoper→kjoper.fullmektig.navn, flettblankeeiere→remove
- **Kjøpekontrakt forbruker (golden standard):** meglerkontor.poststed + kontrakt.dato for "Sted/dato"; eiendom.takstdato for takst/rapport; hjemmelshaver foreach for title holders
- **Alle-flettekoder-25.9.md:** kontrakt.dato, komplettmatrikkel, eiendom.eieform, Model.hjemmelshavere, Model.kjoperskostnader.poster
