# Field Mapping: Leieavtale Næringslokaler (Brukt + Nye)

## Source
- **File 1 (Brukt):** scripts/source_html/leieavtale_naeringslokaler_brukt.html
- **File 2 (Nye):** scripts/source_html/leieavtale_naeringslokaler_nye.html
- **Registry used:** .planning/field-registry.md
- **Document:** Norwegian standard commercial lease ("Standard leieavtale for næringslokaler") — Brukte/"som de er" vs Nye/rehabiliterte lokaler

## Summary
- **Total placeholders found:** 53 (Brukt), 50 (Nye)
- **Main fill-in character:** `[●]` (U+2026 HORIZONTAL ELLIPSIS, displayed as `[…]` in some viewers)
- **Other patterns:** `[..]` (short free text), `[...]` (bilag nr, garantitekst), `[dato]`, `[to]`, `[fire]`, `[12]`, `[18]`, `[3]`, `[27]`
- **Mapped to insert fields (data-label):** 53
- **Potential Vitec merge field matches:** 7 (eiendom.*, dagensdato — registry has no utleier/leietaker)
- **Monetary (need $.UD):** 4
- **Bilag [●] references (appendix numbers):** 14+

## Placeholder Types

| Type | Pattern | Usage |
|------|---------|-------|
| Fill-in blank | `[●]` | Main placeholder → `<span class="insert" data-label="…"></span>` |
| Short free text | `[..]` | "Som saklig grunn regnes blant annet at [..] ikke lenger har..." |
| Appendix number | `Bilag [●]` | Appendix reference → data-label: `bilag-nr` |
| Broker choice | `(stryk det som ikke passer)` | Interactive; "per kvm BTA per år/per kvartal/per måned" |
| Fixed alternatives | `[12]`, `[18]`, `[3]`, `[27]` | Clause numbers / month counts (may be fixed or variable) |
| Number words | `[to]`, `[fire]` | "innen [to] uker", "innen [fire] uker" |
| Date placeholder | `[dato]` | "Denne leieavtalen er inngått [dato]" |
| Optional party | `[og megler]` | "sendt partene [og megler] per e-post" |

---

## Field Mapping Table

All `[●]` placeholders become insert fields. Order follows Brukt document; Nye differs only where sections are omitted (Brukt has 3 extra: Bilag for arbeider før overtakelse, overtakelsesprotokoll, etc.).

| # | Context (before → after) | data-label | Vitec Path (if any) | $.UD | Variant | Notes |
|---|--------------------------|------------|---------------------|------|---------|-------|
| 1 | Navn/Firma: [●] (Utleier) | utleier.navn-firma | — | — | Both | Utleier = lessor; no utleier in registry |
| 2 | Fødsels- eller organisasjonsnummer: [●] (Utleier) | utleier.orgnr | — | — | Both | Person- or org.nr. |
| 3 | Navn/Firma: [●] (Leietaker) | leietaker.navn-firma | — | — | Both | Leietaker = lessee |
| 4 | Fødsels- eller organisasjonsnummer: [●] (Leietaker) | leietaker.orgnr | — | — | Both | Person- or org.nr. |
| 5 | Adresse [●] (Eiendommen) | eiendom.adresse | [[eiendom.adresse]] | — | Both | **Registry match** |
| 6 | Gnr. [●] bnr. | eiendom.gnr | [[*matrikkel.gnr]] | — | Both | Matrikkel; registry has *matrikkel.gnr |
| 7 | bnr. [●] fnr. | eiendom.bnr | — | — | Both | bnr not in registry as standalone |
| 8 | fnr. [●] snr. | eiendom.fnr | — | — | Both | fnr not in registry |
| 9 | snr. [●] i | eiendom.snr | — | — | Both | snr not in registry |
| 10 | i [●] kommune | eiendom.kommune | [[eiendom.kommunenavn]] | — | Both | **Registry match** |
| 11 | kommunenummer [●] | eiendom.kommunenr | [[eiendom.kommunenr]] | — | Both | **Registry match** |
| 12 | totalt ca. [●] kvm. BTA | areal.totalt-kvm | [[eiendom.bruttoareal]] | — | Both | BTA; **Registry match** |
| 13 | Eksklusivt Areal ca. [●] kvm. BTA | areal.eksklusivt-kvm | — | — | Both | Eksklusivt areal only |
| 14 | Bilag [●] (arbeider før overtakelse) | bilag-nr | — | — | Brukt | Arbeider som Utleier skal utføre |
| 15 | benyttes til [●] | virksomhet | — | — | Both | Leietakers virksomhet/branche |
| 16 | Bilag [●] (arbeider beskrevet) | bilag-nr | — | — | Brukt | Same as #14 in different context |
| 17 | vedlagt som Bilag [●] (overtakelsesprotokoll) | bilag-nr | — | — | Brukt | Skjema for overtakelsesprotokoll |
| 18 | løper fra [●] (Overtakelse) | overtakelse.dato | [[kontrakt.overtagelse.dato]] | — | Both | **Registry match** |
| 19 | til [●] (Leieperioden) | leieperioden.sluttdato | — | — | Both | Sluttdato leieforhold |
| 20 | Leien utgjør NOK [●] | leie.belop | — | YES | Both | **Monetary** — årsleie |
| 21 | akontobeløpet … stipulert til NOK [●] | akonto.felleskostnader | — | YES | Both | **Monetary** — felleskostnader |
| 22 | indeksen for [●] måned | indeks.maaned | — | — | Both | Opprinnelig kontraktsindeks |
| 23 | måned år [●] | indeks.aar | — | — | Both | År for indeks |
| 24 | Garantien skal tilsvare [●] måneders leie | depositum.maaneder | — | — | Both | Antall måneder |
| 25 | foreligge senest [●] | sikkerhetsstillelse.frist | — | — | Both | Dato |
| 26 | Bilag [●] (eksempler kostnader) | bilag-nr | — | — | Both | Felleskostnadene |
| 27 | Bilag [●] (fordelingsnøkkel) | bilag-nr | — | — | Both | Fordelingsnøkkel |
| 28 | Bilag [●] (Miljøavtale) | bilag-nr | — | — | Both | Miljøavtale |
| 29 | Bilag [●] (Databehandleravtale) | bilag-nr | — | — | Both | Databehandleravtale |
| 30 | Bilag [●] (samordningsavtale brann) | bilag-nr | — | — | Both | Brannforebygging |
| 31 | SÆRLIGE BESTEMMELSER [●] | saerlige-bestemmelser | — | — | Both | Fritekst forbehold |
| 32 | Bilag [●]: Særregulering parkeringsplasser | bilag-nr | — | — | Both | I bilagsliste |
| 33 | Bilag [●]: Arbeider Utleier … overtakelse | bilag-nr | — | — | Both | I bilagsliste |
| 34 | Bilag [●]: Skjema overtakelsesprotokoll | bilag-nr | — | — | Both | I bilagsliste |
| 35 | Bilag [●]: Eksempler kostnader | bilag-nr | — | — | Both | I bilagsliste |
| 36 | Bilag [●]: Tegninger mva.-registrering | bilag-nr | — | — | Both | I bilagsliste |
| 37 | Bilag [●]: Sikkerhetsstillelse | bilag-nr | — | — | Both | I bilagsliste |
| 38 | Bilag [●]: Miljøavtale | bilag-nr | — | — | Both | I bilagsliste |
| 39 | Bilag [●]: Databehandleravtale | bilag-nr | — | — | Both | I bilagsliste |
| 40 | Bilag [●]: Samordningsavtale brann | bilag-nr | — | — | Both | I bilagsliste |
| 41 | Bilag [●] (parkeringsplasser i §) | bilag-nr | — | — | Both | Angitt i og på betingelser |
| 42 | forlenge … periode på [●] år | forlengelse.antall-aar | — | — | Both | Variant A |
| 43 | forlenge … periode på [●] år (justering) | forlengelse.antall-aar | — | — | Both | Variant B |
| 44 | næringseiendom i [●] | kommune-område | [[eiendom.kommunenavn]] / [[eiendom.omraade]] | — | Both | Markedet for næringseiendom |
| 45 | Depositumet … [●] måneders leie | depositum.maaneder | — | — | Both | 11.2 variant |
| 46 | foreligge senest [●] (11.6) | sikkerhetsstillelse.frist | — | — | Both | Dato |
| 47 | Bilag [●] (sikkerhetsstillelse 11.1) | bilag-nr | — | — | Both | Sikkerhetsstillelse |
| 48 | foreligge senest [●] (11.2) | sikkerhetsstillelse.frist | — | — | Both | Dato |
| 49 | Administrasjonpåslag [●] % | administrasjon.prosent | — | — | Both | Prosent påslag |
| 50 | Bilag [●] (ansvar oversikt 15.2) | bilag-nr | — | — | Both | Punkt 15 alternativ |
| 51 | repareres … senest [●] måneder | gjenoppforing.maaneder | — | — | Both | Gjenoppføringsperiode |
| 52 | Bilag [●] (Miljøavtalen) | bilag-nr | — | — | Both | Punkt 27 alternativ |
| 53 | Bilag [●] (Solcelleavtalen) | bilag-nr | — | — | Nye | Nye-variant only |

$.UD values: `YES` (wrap in $.UD() if becomes merge field), `—` (not monetary)

---

## Other Placeholders (non-[●])

| # | Source Text | data-label | Notes |
|---|-------------|------------|-------|
| 1 | `[..]` i "Som saklig grunn regnes blant annet at [..] ikke lenger har bestemmende innflytelse" | saklig-grunn | Short free text; Nye + Brukt |
| 2 | `[...]` i "Bilag [...]" (MVA-registrering) | bilag-nr | Ellipsis variant |
| 3 | `[...], org. nr. [...]` (garantitekst etter signaturlinjen) | garantist.navn, garantist.orgnr | Garanter som selvskyldner |
| 4 | `[dato]` i "Denne leieavtalen er inngått [dato]" | signatur.dato | [[dagensdato]] or [[kontrakt.dato]] |
| 5 | `[og megler]` i "sendt partene [og megler] per e-post" | megler-valg | Broker-interactive; stryk hvis ikke megler |
| 6 | `[to]` i "innen [to] uker" | uker-tall | Fixed or variable |
| 7 | `[fire]` i "innen [fire] uker" | uker-tall | Fixed or variable |
| 8 | `[12]` måneder, `[18]` måneder | maaneder-tall | Oppsigelse/fravflytting |
| 9 | `[3]` dager (forhåndsvarsel) | dager-tall | Adgang til Eksklusivt Areal |
| 10 | `[27]` (punktreferanse) | punkt-nr | PUNKT 27 alternativ |
| 11 | `per kvm BTA per år/per kvartal/per måned (stryk det som ikke passer)` | leie-enhet | Broker choice; ikke fill-in |

---

## Potential Vitec Registry Mappings

The field registry has **no utleier/leietaker** (lease parties). These apply only where eiendom/oppdrag context fits:

| data-label | Vitec Path | Context |
|------------|------------|---------|
| eiendom.adresse | [[eiendom.adresse]] | Eiendommens adresse |
| eiendom.kommune | [[eiendom.kommunenavn]] | Kommune |
| eiendom.kommunenr | [[eiendom.kommunenr]] | Kommunenummer |
| areal.totalt-kvm | [[eiendom.bruttoareal]] | BTA |
| overtakelse.dato | [[kontrakt.overtagelse.dato]] | Overtakelsesdato |
| kommune-område | [[eiendom.kommunenavn]] / [[eiendom.omraade]] | Markedet for næringseiendom |
| signatur.dato | [[dagensdato]] or [[kontrakt.dato]] | Kontraktsdato |

Matrikkel: Registry has `[[*matrikkel.gnr]]`; gnr maps. bnr, fnr, snr not in registry; use `[[komplettmatrikkel]]` or insert fields.

---

## Monetary Fields ($.UD required if merge fields)

| Field | Context |
|-------|---------|
| leie.belop | Leien for Leieobjektet per år (NOK) |
| akonto.felleskostnader | Akontobeløp felleskostnader (NOK) |
| depositum (beløp) | Not explicit fill-in; "tilsvare X måneders leie" — amount derived |

---

## Variant Differences (Brukt vs Nye)

| Difference | Brukt | Nye |
|-----------|-------|-----|
| Bilag for arbeider før overtakelse | Yes (#14, #16, #17) | No (nye lokaler, ferdig rehab) |
| Solcelleavtale Bilag | No | Yes (#53) |
| Total [●] count | 53 | 50 |

---

## Broker-Interactive / "stryk det som ikke passer"

These are **not** fill-in blanks; broker chooses which alternatives to keep:

- `[per kvm BTA per år/per kvartal/per måned (stryk det som ikke passer)]` — LEIEN
- `[per kvm BTA per år/per år/per kvartal/per måned (stryk det som ikke passer)]` — Nye variant (dobbelt "per år")
- `[Stryk de alternativene som ikke passer.]` — various clauses
- `[eventuelt kun Leietaker]` — party scope
- `[og megler]` — include megler in "sendt partene"

---

## Unmapped / Need Review

- **Utleier / Leietaker:** No Vitec merge fields for lease parties. Use insert fields with data-label; consider extending registry for næringsutleie if such fields exist in Vitec.
- **Matrikkel fnr, snr, bnr:** Registry has `*matrikkel.gnr` only. Use `[[komplettmatrikkel]]` or insert.
- **Fixed numbers [12], [18], [3], [27], [to], [fire]:** Clarify if these are fixed contract terms or variable.
- **Garantitekst `[…], org. nr. […]`:** Garanter (selvskyldner) — no registry match; insert fields.

---

*Mapping completed per FORMAT_fields.md. Logic Mapper and Structure Analyzer handle vitec-if conditions and document structure. Do NOT determine vitec-if; do NOT analyze document structure.*
