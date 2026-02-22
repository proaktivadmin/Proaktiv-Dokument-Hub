# Structure Analysis: Leieavtale Næringslokaler (Standard)

## Source

- **Files:** `scripts/source_html/leieavtale_naeringslokaler_brukt.html`, `scripts/source_html/leieavtale_naeringslokaler_nye.html`
- **Format:** HTML (mammoth-converted from DOCX)
- **Encoding:** UTF-8
- **Edition:** 8. utgave 06/25 (Meglerstandard)
- **Variants:**
  - **Brukt:** "BRUKTE/«SOM DE ER» LOKALER" — used/second-hand premises as-is
  - **Nye:** "NYE/REHABILITERTE LOKALER" — new or rehabilitated premises with kravspesifikasjon

## Document Overview

Standard form commercial lease agreements (Meglerstandard). The two documents are ~90% identical; key differences are in title, Section 4 (Leieobjektet), Section 6 (Overtakelse), Section 11 (Sikkerhetsstillelse), and section numbering (Nye omits MERVERDIAVGIFT as standalone H1, shifts subsequent sections).

Documents contain:
- **Contract text** — legal agreement (goes INTO template)
- **Commentary/guidance** — "Veiledning", "Alternative bestemmelser", "Forslag til kontraktstekst" (FLAGGED as commentary, exclude from contract template)

Fill-in blanks use `[…]` (Unicode ellipsis U+2026) or literal `[...]` — **not** `[●]` as sometimes seen in other templates. Choice points use "[stryk det som ikke passer]" / "[Stryk de alternativene som ikke passer.]".

---

## Document Skeleton

### Section List (Unified)

Sections are numbered sequentially based on headings found in BOTH sources. Where the two variants differ in structure, the unified list uses the Brukt numbering as base and notes DIFFERS.

| # | Heading | Type | Length | Page Break | Notes |
|---|---------|------|--------|------------|-------|
| 1 | UTLEIER | party-listing | short | — | |
| 2 | LEIETAKER | party-listing | short | — | |
| 3 | EIENDOMMEN | header-info | short | — | |
| 4 | LEIEOBJEKTET | legal-text | medium | — | DIFFERS: Nye references Bilag 3 (kravspesifikasjon); Brukt has parking/endringer Bilag ref |
| 5 | LEIETAKERS VIRKSOMHET | terms | short | — | |
| 6 | OVERTAKELSE/MELDING OM MANGLER | legal-text | medium | avoid-break | DIFFERS: Brukt "ryddet og rengjort… besiktigelse… Bilag X"; Nye "i henhold til punkt 4.1" (kravspesifikasjon) |
| 7 | LEIEPERIODEN | financial | short | — | |
| 8 | LEIEN MV. | financial | long | — | Payment terms, forfall, Felleskostnader |
| 9 | LEIEREGULERING | legal-text | medium | — | Indeksregulering, forlengelse, takstkommisjon |
| 10 | MERVERDIAVGIFT | legal-text | short | — | Brukt only; Nye merges into other section |
| 10a | FORSIKRING | legal-text | short | — | Nye numbering; Brukt has as 11 |
| 11 | FORSIKRING / Sikkerhetsstillelse | legal-text | medium | avoid-break | DIFFERS: Brukt has 4 alternatives (depositum, morselskapgaranti, annen sikkerhet, ingen sikkerhet); Nye simpler |
| 12 | BRANN/DESTRUKSJON | legal-text | medium | — | |
| 13 | UTLEIERS AVTALEBRUDD | legal-text | medium | — | |
| 14 | LEIETAKERS AVTALEBRUDD/UTKASTELSE | legal-text | medium | — | |
| 15 | FRAFLYTTING | legal-text | medium | — | |
| 16 | TINGLYSING/PANTSETTELSE | legal-text | short | — | |
| 17 | Kontrollskifte, Fusjon og fisjon | legal-text | long | internal-wrap | Subsections 17.1–17.7 (approx) |
| 18 | Miljø og sirkulære løsninger mv. / Personvern | mixed | medium | — | DIFFERS: Brukt "Miljø... mv."; Nye "Personvern" (different content) |
| 19 | ANDRE DATA (SOM IKKE ER PERSONOPPLYSNINGER) | terms | short | — | |
| 20 | Samordningsavtale for brannforebygging | legal-text | short | — | |
| 21 | SÆRLIGE BESTEMMELSER/forbehold | mixed | medium | — | Custom clauses placeholder |
| 22 | FORHOLDET TIL HUSLEIELOVEN | legal-text | short | — | |
| 23 | LOVVALG OG TVISTELØSNING | legal-text | short | — | |
| 24 | BILAG TIL LEIEAVTALEN | header-info | short | — | Appendix list |
| 25 | SIGNATUR | signature-block | short | forced-before | |

**Note:** Section numbering differs between Brukt and Nye after point 9 because Nye does not have MERVERDIAVGIFT as a standalone H1. The table above uses a unified scheme. Subsections use decimal numbering (4.1, 4.2, 7.3, 11.1, etc.).

### Table Inventory

| Location | Class | Columns | Purpose |
|----------|-------|---------|---------|
| Section 24 | bilag-list | Bilag nr., Tittel | Appendix index |

No substantial data tables in the contract body. Party info (Utleier, Leietaker, Eiendommen, Leieobjektet) is structured as H1/H2 blocks, not table rows.

### Checkbox Inventory

| Location | Control Type | Count | Description |
|----------|-------------|-------|-------------|
| Section 8 (Leie forfall) | data-driven | 2 | 1/4 vs 1/12 of Leien — "stryk det som ikke passer" |
| Section 8 (Betalingsfrekvens) | data-driven | 2 | kvartal vs måned — "stryk det som ikke passer" |
| Section 11 (Brukt) | data-driven | 4 | Depositum / Morselskapgaranti / Annen sikkerhet / Ingen sikkerhet (mutually exclusive) |
| Section 30.7 | data-driven | 1 | "Partene [eventuelt kun Leietaker]" — optional scope |

Control Type: `data-driven` (system sets via vitec-if based on document variant / user choices)

### Subsections (Selected)

| Parent | Sub# | Heading | Notes |
|--------|------|---------|-------|
| 4 | 4.1 | Leieobjektet | Main definition; Nye adds kravspesifikasjon Bilag 3 |
| 4 | 4.2 | Leieobjektet (parking) | Brukt: inkluderer ikke / inkluderer per Bilag X |
| 7 | 7.3–7.9 | Forlengelse av Leieperioden | Markedsleie, takstkommisjon |
| 8 | 8.x | Leie, forfall, Felleskostnader | Payment structure |
| 11 | 11.1–11.7 | Depositum / alternativer | Brukt: 4 mutually exclusive alternatives |
| 12 | 12.x | Brann/destruksjon | Reparasjon, erstatningsleie |
| 15 | 15.2 | Felleskostnader bilag | "Som Bilag […]..." |
| 17 | 17.1–17.7 | Kontrollskifte | Definition, varsling, hevingsrett |
| 18 | 26.x, 28.x, 29.x | Miljø, energitiltak | Brukt has miljø; Nye has Personvern |
| 23 | 36.1–36.4 | Lovvalg, voldgift | Norsk rett, voldgiftssted |

---

## Fill-in Blanks ([…] / [...])

**Total count (Brukt):** ~53 `[…]` + ~4 `[...]` ≈ **57 fill-in blanks** (excluding structural brackets like [Bilag 1], [Stryk...]).

### Inventory by Section/Context

| # | Label/Context | Count |
|---|---------------|-------|
| 1–2 | Utleier: Navn/Firma, org.nr | 2 |
| 1–2 | Leietaker: Navn/Firma, org.nr | 2 |
| 3 | Eiendommen: Adresse, Gnr, bnr, fnr, snr, kommune, kommunenummer | 7 |
| 4 | Leieobjektet: totalt kvm BTA, Eksklusivt kvm BTA, Bilag nr (endringer), Bilag nr (arbeider), Bilag nr (foto/video), parkeringsplasser Bilag | 6+ |
| 5 | Virksomhet: bruk/formål | 1 |
| 6 | Bilag nr (arbeider/endringer) | 1 |
| 7 | Overtakelsesdato, Leieperioden (sluttdato) | 2 |
| 8 | Leiebeløp NOK, forfall (1/4 eller 1/12), kvartal/måned, Felleskostnader beløp, kontraktsindeks | 5+ |
| 9 | Forlengelsesperiode (år), varslingsfrister (18/12 mnd), område for takstkommisjon | 4+ |
| 11 | Måneders leie (depositum), dato (sikkerhet senest), Bilag nr (annen sikkerhet) | 3+ |
| 12 | Reparasjon/gjenoppføring måneder | 1 |
| 15 | Bilag nr (Felleskostnader oversikt) | 1 |
| 17 | Varslingsfrister [to] uker, [fire] uker | 2 |
| 18 | Bilag nr (Miljøavtale), Bilag nr (Solcelleavtale) | 2 |
| 20 | Bilag nr (Samordningsavtale brannforebygging) | 1 |
| 21 | Særlige bestemmelser (fritekst) | 1 |
| 23 | Voldgiftssted (sted) | 1 |
| 24 | Bilag-liste: variable Bilag-nummer og titler | 10+ |
| 25 | Dato, "og megler", Utleiers repr., Leietakers repr., garantitekst | 5+ |

Additional placeholders: [12], [3] (dager), [18], [27] (punktnummer), [eventuelt kun Leietaker], [dato], [og megler], [to], [fire], [Administrasjonspåslag %], etc.

---

## "[stryk det som ikke passer]" Choice Points

| Location | Alternatives | Notes |
|----------|--------------|-------|
| Section 8 (Leie forfall) | 1/4 vs 1/12 av Leien | Betalingsfrekvens (kvartalsvis vs månedlig) |
| Section 8 (Betalingsdato) | "i hver(t) kvartal/måned" | Same choice as above |
| Section 8 (Leie oppgitt) | "per kvm BTA per år / per kvartal / per måned" | Angivelse av leie |
| Section 24 / Tilleggstekster | "[Stryk de alternativene som ikke passer.]" | General instruction for appendix alternatives |

---

## Commentary Sections (EXCLUDE from Contract Template)

| Location | Type | Description |
|----------|------|-------------|
| Header | Note | "[Tilleggstekster, alternative tekster, bilag og kommentarer er inntatt bakerst i avtalen]" |
| Punkt 11 | Alternative bestemmelser | "Punkt 11 — Alternative bestemmelser om sikkerhetsstillelse" — variants for depositum, morselskapgaranti, etc. (editorial) |
| Punkt 15 | Forslag til tekst | "PUNKT 15 - FORSLAG TIL TEKST TIL BILAG OM FELLESKOSTNADER" (Nye) |
| Punkt 27 | Alternativ | "PUNKT [27] – ALTERNATIV TIL PUNKT..." — alternative kontrollskifte wording |
| TILLEGGSTEKSTER | Section | "TILLEGGSTEKSTER/ALTERNATIVE TEKSTER" — appendix with optional clauses |
| Veiledning | (if present) | "Veiledning til..." — guidance for broker |

**Rule:** Contract text = sections 1–25 main body. Commentary = "Alternative bestemmelser", "Forslag til", "Veiledning", appendix guidance. Exclude commentary from the merged template; include as optional/separate or clearly flagged.

---

## Signature Block

- **Party groups:** Utleier, Leietaker
- **Per party:** Signaturlinje ("________________"), label ([Utleiers repr.] / [Leietakers repr.])
- **Header:** "Denne leieavtalen er inngått [dato], undertegnet elektronisk og sendt partene [og megler] per e-post."
- **Uses foreach:** No — fixed two parties (Utleier, Leietaker)
- **Garanti block (Brukt):** Morselskapgaranti can be appended "etter signaturlinjen" with placeholder "[...], org. nr. ... garanterer som selvskyldner..."

---

## Party Listings

| Role | Location | Pattern |
|------|----------|---------|
| Utleier | Sections 1, 25 | Single party; Navn/Firma, org.nr |
| Leietaker | Sections 2, 25 | Single party; Navn/Firma, org.nr |
| Eiendommen | Section 3 | Address, matrikkel data (Gnr, bnr, fnr, snr, kommune) |
| Leieobjektet | Section 4 | Areal, Bilag refs |

No megler (broker) in contract body; "og megler" in signature block refers to distribution of signed copy.

---

## Bilag References

| Bilag | Purpose |
|-------|---------|
| Bilag 1 | (Variable — titler varierer) |
| Bilag 2 | Arealoversikt og tegninger |
| Bilag 3 | Kravspesifikasjon (Nye only) |
| Bilag [●] | Endringer/arbeider (Brukt Section 4, 6) |
| Bilag [●] | Parkeringsplasser betingelser (Brukt Section 4) |
| Bilag [●] | Foto/video (Section 6) |
| Bilag [●] | Felleskostnader fordeling |
| Bilag [●] | Frivillig registrering (tinglysing) |
| Bilag [●] | Miljøavtale |
| Bilag [●] | Samordningsavtale brannforebygging |
| Bilag [●] | Skjema overtakelsesprotokoll |
| Bilag [●] | Databehandleravtale |
| Bilag [●] | Solcelleavtale |

---

## Page Break Recommendations

### Short Sections (wrap entire article)
- Section 6: Overtakelse/Melding om mangler
- Section 11: Sikkerhetsstillelse
- Section 16: Tinglysing/Pantsettelse
- Section 22: Forholdet til husleieloven
- Section 23: Lovvalg og tvisteløsning

### Internal Wraps Needed
- Section 8: Leien mv. (long payment section)
- Section 9: Leieregulering (forlengelse, takstkommisjon)
- Section 17: Kontrollskifte, Fusjon og fisjon

### Forced Page Breaks
- Before Section 25 (SIGNATUR) — always on fresh page

---

## Source Clues Detected

| Line/Area | Clue | Interpretation |
|-----------|------|----------------|
| Title | "BRUKTE/«SOM DE ER»" vs "NYE/REHABILITERTE" | Document variant (Brukt vs Nye) |
| Section 4 | Bilag 3 kravspesifikasjon | Nye only — conditional |
| Section 6 | "ryddet og rengjort... besiktigelse" vs "punkt 4.1" | Overtakelse variant text |
| Section 8 | "1/4 / 1/12 [stryk det som ikke passer]" | Choice: kvartal vs måned |
| Section 8 | "kvartal/måned [stryk det som ikke passer]" | Same choice |
| Section 11 | 4 alternative blocks (depositum, morselskap, annen, ingen) | Mutually exclusive sikkerhetsstillelse |
| Punkt 11 appendix | "Alternative bestemmelser om sikkerhetsstillelse" | Commentary — variants for broker |
| Various | `[…]` ellipsis in brackets | Fill-in blank location |
| Bilag list | Variable Bilag X: Tittel | Appendix references |

---

## Section Numbering Differs (Brukt vs Nye)

| Unified # | Brukt H1 | Nye H1 |
|-----------|----------|--------|
| 10 | MERVERDIAVGIFT | (—) |
| 11 | FORSIKRING | FORSIKRING |
| 12 | BRANN/DESTRUKSJON | BRANN/DESTRUKSJON |
| 13–16 | UTLEIERS AVTALEBRUDD … TINGLYSING | Same, shifted |
| 17 | Kontrollskifte, Fusjon og fisjon | KONTROLLSKIFTE, FUSJON OG FISJON |
| 18 | Miljø og sirkulære løsninger mv. | Personvern |
| 19 | ANDRE DATA | ANDRE DATA |

Merverdiavgift exists in both documents; in Nye it may be folded into LEIEN MV. or another section rather than a standalone H1. Merge strategy: use conditional branches for Brukt vs Nye where text differs; unify section numbering in the template.
