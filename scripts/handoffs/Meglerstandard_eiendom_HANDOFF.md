# Handoff: Meglerstandard Mars 2020 — Eiendom med og uten oppgjørsansvarlig

## Production File
`scripts/converted_html/Meglerstandard_eiendom_PRODUCTION.html` (1,375 lines)

## Source Document
`Meglerstandard for eiendom med og uten oppgjørsansvarlig.htm` (265K chars, Word HTML export)

## Template Classification
- **Mode:** B (convert existing document)
- **Tier:** T5 (complex contract with 3 alternative appendices, dynamic parties, 2 bilag)

## What's Included

### Main Contract (Sections 1-16)
| Section | Heading | Key Features |
|---------|---------|--------------|
| Header | Megler info, party listings | Conditional eierform fields, roles-table with Mangler data guards |
| 1 | Partene og Eiendommen | Seller/buyer foreach loops, insert fields for gnr/bnr |
| 2 | Kjøpesummen | `$.UD()` formatted amounts, pro & contra deadline insert |
| 3 | Overtakelse, oppgjør og Forsinkelse | **vitec-if** med/uten oppgjørsansvarlig in 3.2.1, (a)-(d) subpoints |
| 4 | Betingelser | Insert fields for damage threshold percentages |
| 5 | Selgers plikter | avoid-page-break, (a)-(e) |
| 6 | Partenes beføyelser | avhendingsloven references |
| 7 | Selgers garantier | 7.1(a)-(g), 7.2 |
| 8 | Erstatning og begrensninger | Insert fields for liability thresholds, **8.6 conditional** (Count > 1) |
| 9 | Skadesløsholdelse | Nested (a)(i)-(iii) |
| 10 | Sikkerhet | Insert field for amount; **must be manually removed** if not applicable |
| 11 | Merverdiavgift | References vedlegg 5 |
| 12 | Fraskrivelse | 12.1-12.4 |
| 13 | Meddelelser | Insert fields for notification addresses |
| 14 | Lovvalg og tvisteløsning | Insert field for verneting |
| 15 | Vedlegg | List 1-7 |
| 16 | Underskrift | Signature block with foreach party names |

### Appendices
| Appendix | Content | Condition |
|----------|---------|-----------|
| Vedlegg 5 | Justeringsavtale (MVA) — byggetiltak table, 9 insert fields | Always included |
| Vedlegg 6A | Oppgjørsavtale med oppgjørsansvarlig, lån innfris ETTER tinglysing | `oppgjor.ansvarlig.navn != ""` |
| Vedlegg 6B | Oppgjørsavtale med oppgjørsansvarlig, lån innfris VED overtakelse | `oppgjor.ansvarlig.navn != ""` |
| Vedlegg 6C | Oppgjørsavtale uten oppgjørsansvarlig | `oppgjor.ansvarlig.navn == ""` |
| Bilag 1 | Fullmakt til pantsettelse — witness section | Always included (comment notes condition) |
| Bilag 2 | Ugjenkallelig betalingsinstruks — payment table | `oppgjor.ansvarlig.navn == ""` |

## Validation Results

### Static Validation: PASS (0 errors, 2 warnings)
1. `[[selger.ledetekst_fdato_orgnr]]` in thead without `*` — correct, it's outside foreach scope
2. `data-label="sikkerhetsbeløp"` has raw ø — acceptable in attribute values

### Content Verification: PASS (26/28 items pass, 2 partial)
All 16 sections, all 6 appendices, all conditional logic, all merge fields verified.

## Known Limitations (Require Broker Action)

### 1. Vedlegg 6A vs 6B (Manual Selection Required)
Both Vedlegg 6A and 6B show when `oppgjor.ansvarlig.navn` has a value. There is no known Vitec field to distinguish "lån innfris etter tinglysing" from "lån innfris ved overtakelse."

**Broker must delete either 6A or 6B** based on the transaction scenario.

### 2. Section 10 (Manual Deletion)
Source says: "Strykes hvis Selger ikke skal stille sikkerhet." No known Vitec field for `selger_stiller_sikkerhet`. Broker must manually remove Section 10 if security is not required.

### 3. Bilag 1 (Conditional on Vedlegg 6B)
Source says: "Strykes hvis oppgjøret gjennomføres etter tinglysing av skjøte." This means Bilag 1 should only be included with Vedlegg 6B (lån innfris ved overtakelse). No automated condition is possible without a timing field.

### 4. Alternative Text Blocks (Comments)
Two alternative text blocks are preserved as HTML comments:
- **Utkast A preamble:** Alternative forbehold clause for bud/budaksept
- **Section 8.6:** Alternative solidarisk liability (default is proratarisk)

## Statistics
- 22 vitec-if conditions
- 35 vitec-foreach loops
- 69 insert fields (data-label) for manual fill-in
- 8 forced page breaks
- 0 footnotes (all 38 editorial footnotes excluded)

## Insert Fields Summary (69 total)
Key unmapped values that brokers must fill in:
- `gnr`, `bnr` (matrikkel, 2x)
- `prosentsats` (damage thresholds, 3x)
- `antall dager` (pro & contra deadline)
- `beløpsgrense enkeltansvar`, `beløpsgrense samlet ansvar`, `ansvarsbegrensning` (liability caps)
- `sikkerhetsbeløp` (security amount)
- `verneting` (court venue)
- `adresse Selger`, `adresse Kjøper`, `adresse/e-post megler` (notifications)
- `Selgers representant`, `Kjøpers representant` (signatures)
- `Oppgjørskonto`, `Kjøpers bank`, `org.nr. Kjøpers bank` (financial)
- `sikringsdokument beløp` (security document amount)
- Plus ~40 more in Vedlegg 5/6 and Bilag 1/2

## Analysis Files
- `scripts/_analysis/meglerstandard_eiendom/structure.md`
- `scripts/_analysis/meglerstandard_eiendom/fields.md`
- `scripts/_analysis/meglerstandard_eiendom/logic.md`
