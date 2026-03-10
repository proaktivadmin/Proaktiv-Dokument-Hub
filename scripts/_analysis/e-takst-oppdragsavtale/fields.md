# Field Mapping: E-takst oppdragsavtale

## Source
- **File:** `c:\Users\Adrian\Downloads\OneDrive_2026-02-21\maler vi må få produsert\E-takst oppdragsavtale.htm`
- **Registry used:** .planning/field-registry.md

## Summary
- **Total placeholders found:** 45
- **Mapped successfully:** 39
- **Unmapped (need review):** 6
- **Monetary (need $.UD):** 2
- **Optional (need vitec-if guard):** 12
- **Insert fields (underline blanks):** 13

## Field Mapping Table

| # | Source Text / Placeholder | Modern Path | $.UD | Guard | Notes |
|---|--------------------------|-------------|------|-------|-------|
| 1 | (implied: Adresse) "Boligkjøperveien 42A, 5165 Laksevåg i Oslo kommune." | [[eiendom.adresse]] | — | — | Full address; registry: "Fletter gatenavnognr., postnr og poststed" |
| 2 | (implied: Gnr.) 217 | [[*matrikkel.gnr]] | — | foreach | First matrikkel; inside vitec-foreach matrikkel |
| 3 | (implied: Bnr.) 116 | [[*matrikkel.bnr]] | — | foreach | First matrikkel |
| 4 | (implied: Snr.) 21 | [[*matrikkel.snr]] | — | foreach | First matrikkel |
| 5 | (implied: Fnr.) (empty) | [[*matrikkel.fnr]] | — | foreach | First matrikkel; optional for many properties |
| 6 | (implied: Borettslag) (empty) | [[brl.navn]] | — | != "" | Optional; only when eieform is borettslag |
| 7 | (implied: Andelsnr) (empty) | [[eiendom.andelsnr]] | — | != "" | Optional; only when borettslag/aksjelag |
| 8 | (implied: Navn) "Lene Solbakken Nilssen" | [[*selger.navnutenfullmektigogkontaktperson]] | — | foreach | Inside selgere loop |
| 9 | (implied: Fnr) "300681-35237" | [[*selger.idnummer]] or [[*selger.fdato_orgnr]] | — | foreach | Ledetekst: [[*selger.ledetekst_idnummer]] |
| 10 | Statsborgerskap:___________ | (INSERT) | — | — | Manual fill-in; NOT in registry |
| 11 | (implied: Adr) "Skogtunet 7" | [[*selger.hovedgatenavnognr]] or [[*selger.gatenavnognr]] | — | foreach | Street; Alle-flettekoder uses gatenavnognr in foreach |
| 12 | (implied: postnr/poststed) "1369 Stabekk" | [[*selger.postnr]] [[*selger.poststed]] | — | foreach | Or hovedpostnr/hovedpoststed per registry |
| 13 | (implied: Mobil) "41 10 77 07" | [[*selger.mobiltlf]] or [[*selger.hovedtlf]] | — | foreach | mobil = mobiltlf; hovedtlf = primary phone |
| 14 | (implied: E-post) "lene@one2cel.no" | [[*selger.hovedepost]] or [[*selger.emailadresse]] | — | foreach | Alle-flettekoder uses emailadresse in foreach |
| 15 | (implied: Navn slot 2) blank | [[*selger.navnutenfullmektigogkontaktperson]] | — | foreach | Second owner; repeat block |
| 16 | (implied: Fnr slot 2) blank | [[*selger.idnummer]] | — | foreach | — |
| 17 | Statsborgerskap:___________ (slot 2) | (INSERT) | — | — | Manual fill-in; NOT in registry |
| 18 | (implied: Selskap) "Proaktiv Gruppen AS" | [[meglerkontor.navn]] or [[meglerkontor.juridisknavn]] | — | — | Company name; navn = display, juridisknavn = legal |
| 19 | (implied: Megler) "Svein Kvamme Bergum" | [[ansvarligmegler.navn]] | — | != "Mangler data" | Main broker; operativmegler.navn alternative |
| 20 | Når ble eiendommen kjøpt? ______________________ | (INSERT) | — | — | Manual fill-in; NO registry equivalent |
| 21 | Hva var kjøpesummen? __________________________ | [[kontrakt.kjopesum]] or custom | YES | != "" | If from Vitec: kontrakt.kjopesum; else INSERT |
| 22 | Når ble forrige verdivurdering foretatt? Oppgi årstall: _______. | (INSERT) | — | — | Manual fill-in; NO registry equivalent |
| 23 | Eiendommen er ikke verdivurdert siden den ble kjøpt o | (CHECKBOX) | — | — | Data-driven or interactive; NO merge field |
| 24 | Honorar for verdivurderingen er avtalt til kr. _______,- | [[oppdrag.fastpris]] | YES | != "" | E-takst fee; monetary |
| 25 | Sted:___________________________ | (INSERT) | — | — | Signature place |
| 26 | Dato: _____________ | [[dagensdato]] or (INSERT) | — | — | Can merge dagensdato if fixed at produce time |
| 27 | __________________________ (Sign. oppdragsgiver) | (INSERT) | — | — | Signature line |
| 28 | Relasjon til navn: ______________________________________________________ (PEP) | (INSERT) | — | — | PEP form fill-in |
| 29 | Relasjon til navn: ______________________________________________________ (PEP 2) | (INSERT) | — | — | PEP form fill-in |
| 30 | Land/organisasjon/verv: _________________________________________________ | (INSERT) | — | — | PEP form fill-in |
| 31 | Tidsperiode: ___________________________________________________________ | (INSERT) | — | — | PEP form fill-in |
| 32 | Signatur oppdragsgiver: __________________________________________________ | (INSERT) | — | — | PEP declaration signature |
| 33 | Beskrivelse av feil, mangler... (underline blocks) | (INSERT) | — | — | Multi-line insert area |
| 34 | Utfylt skjema sendes til: Proaktiv Gruppen AS, Småstrandgaten 6... | [[meglerkontor.besoksadresse]], [[meglerkontor.postnr]] [[meglerkontor.poststed]] | — | — | Or hardcode if static |
| 35 | E-post: skb@proaktiv.no | [[meglerkontor.epost]] or [[oppgjor.kontorepost]] | — | != "" | Contact for angrerett |
| 36 | tjenester (spesifiser på linjene nedenfor) | (INSERT) | — | — | Angreskjema service description |
| 37 | Avtalen ble inngått den (dato) | (INSERT) or [[oppdrag.dato]] | — | — | Contract date |
| 38 | Forbrukerens/forbrukernes navn og adresse | (INSERT) or [[*selger.navn]] / [[*selger.adresse]] | — | foreach | Angreskjema consumer block |
| 39 | Dato: (underline) | (INSERT) or [[dagensdato]] | — | — | Angreskjema date |
| 40 | Forbrukerens/forbrukernes underskrift | (INSERT) | — | — | Signature line |

$.UD values: `YES` (wrap in $.UD()), `—` (not monetary)

Guard values:
- `—` — always present, no guard needed
- `!= ""` — optional, hide when empty
- `!= "Mangler data"` — optional, hide when "Mangler data"
- `foreach` — inside a vitec-foreach loop, use [[*field]]

## Collections (vitec-foreach candidates)

| Collection Path | Loop Variable | Fields Inside | Guard |
|----------------|---------------|---------------|-------|
| Model.selgere | selger | navnutenfullmektigogkontaktperson, idnummer, ledetekst_idnummer, gatenavnognr, postnr, poststed, mobiltlf/hovedtlf, emailadresse/hovedepost | Count > 0 |
| Model.matrikler | matrikkel | gnr, bnr, snr, fnr | Count > 0; single row if one matrikkel |

**Note on selger field naming:** Alle-flettekoder 25.9 uses `*selger.gatenavnognr`, `*selger.postnr`, `*selger.poststed`, `*selger.emailadresse` in foreach. Registry documents `selger.hovedgatenavnognr`, `selger.hovedpostnr`, etc. Use the foreach-compatible paths that exist in Vitec.

## Monetary Fields ($.UD required)

| Field Path | Context |
|------------|---------|
| [[oppdrag.fastpris]] | E-takst honorar (verdivurdering fee) |
| [[kontrakt.kjopesum]] | Kjøpesum (if "Hva var kjøpesummen?" is merged from Vitec) |

## Unmapped Fields (NEED HUMAN REVIEW)

| # | Source Text | Context in Document | Attempted Match | Confidence |
|---|-------------|---------------------|-----------------|------------|
| 1 | Statsborgerskap:___________ | Section 2, Eier/oppdragsgiver (×2) | — | No field in registry; manual INSERT |
| 2 | Når ble eiendommen kjøpt? ___ | Section 5C, Bakgrunn | — | No field; oppdrag/eiendom purchase date not in registry |
| 3 | Når ble forrige verdivurdering foretatt? Oppgi årstall: ___ | Section 5C, Bakgrunn | — | No field in registry |
| 4 | "Hva var kjøpesummen?" ___ | Section 5C, Bakgrunn | [[kontrakt.kjopesum]] IF from same oppdrag; else INSERT | Low — could be historical purchase, not current kontrakt |
| 5 | Formål checkboxes (Salg, Refinansiering, etc.) | Section 5 tables | — | Interactive/broker-select; Logic Mapper decides vitec-if |
| 6 | PEP Ja/Nei, Førtidig oppstart checkboxes | Sections 7, 10 | — | Interactive; Logic Mapper |

**Recommendation:** Statsborgerskap, "Når ble eiendommen kjøpt", "Forrige verdivurdering årstall", and "Hva var kjøpesummen" are likely manual INSERT fields (user fills at signing) unless Vitec has E-takst-specific schema. Search Alle-flettekoder for `etakst`, `verdivurdering`, `statsborgerskap` if extending registry.

## Insert Fields (underline blanks → span.insert / data-label)

All ___________ patterns should become insert fields for user/broker fill-in:

| Label | Section |
|-------|---------|
| Statsborgerskap | 2 (×2) |
| Når ble eiendommen kjøpt? | 5C |
| Hva var kjøpesummen? | 5C |
| Når ble forrige verdivurdering foretatt? Oppgi årstall | 5C |
| Honorar kr. | 8 |
| Sted | Signature block |
| Dato | Signature block |
| Sign. oppdragsgiver | Signature block |
| Relasjon til navn (PEP) | 11 (×2) |
| Land/organisasjon/verv | 11 |
| Tidsperiode | 11 |
| Signatur oppdragsgiver | 11 |
| Beskrivelse av feil, mangler | 11 |
| Angreskjema: tjenester, dato, navn/adresse, underskrift | Angreskjema |
