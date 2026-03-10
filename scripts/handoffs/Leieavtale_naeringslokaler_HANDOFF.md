# Handoff: Standard leieavtale for næringslokaler (Brukt + Nye/Rehabiliterte)

## Production File
`scripts/converted_html/Leieavtale_naeringslokaler_PRODUCTION.html` (648 lines, 62,303 chars)

## Source Documents
- `Standard leieavtale for næringslokaler (Brukt - som de er) - 8. utgave 2025.docx`
- `Standard leieavtale for næringslokaler (Nye_Rehabiliterte) 8. utgave 2025(34890393.1).docx`

Converted via mammoth to intermediate HTML, then hand-built into Vitec template.

## Template Classification
- **Mode:** B (convert existing documents — merged)
- **Tier:** T5 (complex contract with two variant branches, 36 numbered sections)
- **Standard:** Meglerstandard / Norsk Eiendom, 8. utgave 06/25

## What's Included

### Merged Variant Architecture
Both "Brukte/«som de er» lokaler" and "Nye/Rehabiliterte lokaler" are merged into a single template. A broker-interactive checkbox pair at the document top lets the broker select which variant applies. Variant-specific text is marked with bold **[BRUKT:]** and **[NYE:]** labels — the broker deletes the inapplicable variant before finalizing.

### Main Contract (Sections 1-36 + Bilag + Signatur)
| Section | Heading | Key Features |
|---------|---------|--------------|
| 1 | UTLEIER | Insert fields: navn-firma, orgnr |
| 2 | LEIETAKER | Insert fields: navn-firma, orgnr |
| 3 | EIENDOMMEN | Insert fields: adresse, gnr, bnr, fnr, snr, kommune, kommunenr |
| 4 | LEIEOBJEKTET | **DIFFERS:** Nye adds kravspesifikasjon Bilag 3; Brukt adds arbeider Bilag ref |
| 5 | LEIETAKERS VIRKSOMHET | Insert field: virksomhet |
| 6 | OVERTAKELSE/MELDING OM MANGLER | **DIFFERS:** Brukt "ryddet og rengjort"; Nye "i henhold til punkt 4.1" |
| 7 | LEIEPERIODEN | Insert fields: overtakelse.dato, sluttdato |
| 8 | LEIEN MV. | Insert fields: leie.beløp, akonto; "[stryk det som ikke passer]" choices |
| 9 | LEIEREGULERING | Insert fields: indeks.måned, indeks.år |
| 10 | MERVERDIAVGIFT | A/B/C alternatives ("[stryk det som ikke passer]"); **DIFFERS:** fremleie wording |
| 11 | SIKKERHETSSTILLELSE | Insert fields: depositum.måneder, frist |
| 12 | LEIETAKERS BRUK | **DIFFERS:** miljøsertifisering clause extension |
| 13 | UTLEIERS ADGANG | Access to Eksklusivt Areal |
| 14 | UTLEIERS VEDLIKEHOLD | Eierkostnader |
| 15 | FELLESKOSTNADER | Insert fields: bilag-nr (2×) |
| 16 | LEIETAKERS VEDLIKEHOLD | Leietakerkostnader |
| 17 | UTLEIERS ARBEIDER | Endringsarbeid, miljøtiltak |
| 18 | LEIETAKERS ENDRING | Virksomhetsskilt, solavskjerming |
| 19 | FORSIKRING | Partenes forsikringsplikt |
| 20 | BRANN/DESTRUKSJON | Totalskade frigjøring |
| 21 | UTLEIERS AVTALEBRUDD | **DIFFERS:** Brukt adds mangel-materiality threshold |
| 22 | LEIETAKERS AVTALEBRUDD | Tvangsfravikelse |
| 23 | FRAFLYTTING | 6 paragraphs, insert fields: [12] måneder, [3] dager |
| 24 | TINGLYSING/PANTSETTELSE | Opptrinnsrett, pantsettelse |
| 25 | FREMLEIE | Samtykke, avgiftsmessig belastning |
| 26 | OVERDRAGELSE | Eierskifte, samtykke |
| 27 | KONTROLLSKIFTE | 27.1-27.7, saklig grunn insert |
| 28 | MILJØ OG SIRKULÆRE LØSNINGER | Materialer, miljømerking, Bilag ref |
| 29 | INFORMASJONSUTVEKSLING | Data, CSRD rapportering |
| 30 | MENNESKERETTIGHETER | Hvitvasking, korrupsjon, sanksjoner |
| 31 | PERSONVERN | Databehandleravtale, Bilag ref |
| 32 | ANDRE DATA | Anonymiserte data |
| 33 | SAMORDNINGSAVTALE BRANN | Bilag ref |
| 34 | SÆRLIGE BESTEMMELSER | Fritekst insert |
| 35 | FORHOLDET TIL HUSLEIELOVEN | §§ fravikelser |
| 36 | LOVVALG OG TVISTELØSNING | Norsk rett, verneting |
| — | BILAG TIL LEIEAVTALEN | **DIFFERS:** Nye includes Bilag 3 Kravspesifikasjon; Brukt includes Arbeider-bilag |
| — | SIGNATUR | Elektronisk signatur, to parter |

### Commentary Sections EXCLUDED
The source documents contain ~50% editorial commentary ("TILLEGGSTEKSTER/ALTERNATIVE TEKSTER/BILAG/KOMMENTARER"), including:
- Alternative bestemmelser om sikkerhetsstillelse (punkt 11)
- Forslag til tekst til bilag om Felleskostnader (punkt 15)
- Alternativ kontrollskifte-bestemmelse (punkt 27)
- Tilleggstekst miljøtiltak (punkt 28)
- Forslag til voldgiftsbehandling (punkt 36)
- Forslag til fysisk signatur (punkt 38)

These are broker reference materials, NOT contract text, and are intentionally excluded.

## Validation Results

### Static Validation: 38/46 PASS
All 8 "failures" are expected for this template type:

| Check | Why Expected |
|-------|-------------|
| No merge fields | Standard form contract — no Vitec data fields |
| No vitec-if | No Model field for Brukt/Nye; uses bold labels |
| No vitec-foreach | Fixed parties (Utleier/Leietaker), not dynamic |
| No CSS counters | Literal section numbers from published standard |
| No roles-table | No dynamic party listing tables |
| H2 margin | No counter offset needed |

### Entity Encoding: PASS
- 0 literal Norwegian characters
- 498 HTML entity occurrences (&oslash;, &aring;, etc.)

## Variant Differences (7 [BRUKT:] + 5 [NYE:] labels)

| Location | Brukt Text | Nye Text |
|----------|-----------|----------|
| Section 4 | "Før Overtakelse skal Utleier utføre arbeider…Bilag [●]" | "Leieobjektet skal være i henhold til kravspesifikasjon, Bilag 3" |
| Section 6 | "overtas ryddet og rengjort…i den stand som ved besiktigelse" | "overtas i henhold til punkt 4.1 ovenfor" |
| Section 10 | "sørge for at fremleien blir omfattet av registrering" | "umiddelbart søke om frivillig registrering for fremleien" |
| Section 12 | "miljøsertifisering." | "miljøsertifisering slik de til enhver tid gjelder." |
| Section 21 | Adds "Hva gjelder mangel, forutsettes at mangelen er vesentlig" (2×) | Shorter clause without materiality threshold |
| Bilag list | "Arbeider som Utleier skal utføre…før Overtakelse" | "Bilag 3: Kravspesifikasjon" |

## Known Limitations (Require Broker Action)

### 1. Variant Selection (Manual)
No Vitec Model field exists for "Brukt vs Nye" commercial lease distinction. The broker must:
1. Select the applicable checkbox at the top
2. Delete all **[BRUKT:]** or **[NYE:]** labeled paragraphs for the inapplicable variant

### 2. "[Stryk det som ikke passer]" (Manual)
Three broker-choice sections require manual deletion of alternatives:
- Section 8: 1/4 vs 1/12 payment frequency; kvartal vs måned
- Section 8: per kvm BTA per år/kvartal/måned
- Section 10: MVA alternative A, B, or C

### 3. Fixed Numbers in Brackets
Some bracketed values are suggested defaults, not blanks:
- `[12]` måneder — fraflytting notice period
- `[3]` dager — visitor access days per week
- `[to]` uker, `[fire]` uker — kontrollskifte deadlines

### 4. No Party Loops
Utleier and Leietaker are single fixed parties (not Vitec-managed collections). Their details are insert fields, not merge fields.

## Statistics
- **38** article.item sections
- **47** insert fields (data-label) for manual fill-in
- **2** SVG broker-interactive checkboxes (variant selector)
- **5** forced page breaks
- **38** avoid-page-break wrappers (13 articles + 25 internal divs)
- **498** HTML entity encodings
- **0** vitec-if / vitec-foreach / merge fields (by design)

## Insert Fields Summary (47 total)
Key fields the broker must fill in:
- `utleier.navn-firma`, `utleier.orgnr` — Lessor identity
- `leietaker.navn-firma`, `leietaker.orgnr` — Lessee identity
- `eiendom.adresse`, `eiendom.gnr/bnr/fnr/snr`, `eiendom.kommune`, `eiendom.kommunenr` — Property
- `areal.totalt-kvm`, `areal.eksklusivt-kvm` — Area
- `virksomhet` — Permitted use
- `overtakelse.dato`, `leieperioden.sluttdato` — Period
- `leie.beløp`, `akonto.felleskostnader` — Financial
- `indeks.maaned`, `indeks.aar` — Index regulation
- `depositum.maaneder`, `sikkerhetsstillelse.frist` — Security
- `bilag-nr` (×14) — Appendix numbers
- `signatur.dato`, `utleier.representant`, `leietaker.representant` — Signature
- `saerlige-bestemmelser` — Free text provisions

## Analysis Files
- `scripts/_analysis/leieavtale_naeringslokaler/structure.md`
- `scripts/_analysis/leieavtale_naeringslokaler/fields.md`
- `scripts/_analysis/leieavtale_naeringslokaler/logic.md`
- `scripts/_analysis/leieavtale_naeringslokaler/contract_body_brukt.txt`
- `scripts/_analysis/leieavtale_naeringslokaler/contract_body_nye.txt`
