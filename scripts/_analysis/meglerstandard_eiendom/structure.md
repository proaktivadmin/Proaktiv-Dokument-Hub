# Structure Analysis: Meglerstandard Mars 2020 om salg av eiendom med og uten oppgjørsansvarlig

## Source
- **File:** `Meglerstandard for eiendom med og uten oppgjørsansvarlig.htm` (from OneDrive_2026-02-21/maler vi må få produsert/)
- **Format:** .htm (Word HTML export)
- **Encoding:** windows-1252 (Norwegian characters)
- **Total sections:** 16 main contract + 1 Vedlegg 5 + 3 alternative Vedlegg 6 + 2 Bilag + header block
- **Body start:** Line ~1870 (after ~1870 lines of Word CSS)

## Document Skeleton

### Section List

| # | Heading | Type | Length | Page Break |
|---|---------|------|--------|------------|
| — | Header block (Megler info, Utkast, KJØPEKONTRAKT mellom, party listings) | header-info | short | forced-before (after party intro) |
| 1 | Partene og Eiendommen | party-listing | short | — |
| 2 | Kjøpesummen og eiendommens avkastning og kostnader | financial | medium | — |
| 3 | Overtakelse, oppGjør og Forsinkelse | legal-text | medium | — |
| 4 | Betingelser for gjennomføring av avtalen | mixed | long | internal-wrap |
| 5 | Selgers plikter før Overtakelse | legal-text | short | avoid-break |
| 6 | Partenes beføyelser ved avtalebrudd | legal-text | medium | — |
| 7 | Selgers garantier | legal-text | long | internal-wrap |
| 8 | Rett til erstatning og Begrensninger i Selgers ansvar | legal-text | long | internal-wrap |
| 9 | Skadesløsholdelse fra selger | legal-text | medium | — |
| 10 | Sikkerhet | mixed | short | avoid-break |
| 11 | Merverdiavgift. overføring av justerings-/tilbakeføringsforpliktelser | legal-text | short | avoid-break |
| 12 | Fraskrivelse av retten til å gjøre krav gjeldende mot andre enn partene | legal-text | medium | — |
| 13 | Meddelelser | terms | short | avoid-break |
| 14 | Lovvalg og tvisteløsning | terms | short | avoid-break |
| 15 | Vedlegg | terms | short | avoid-break |
| 16 | Underskrift | signature-block | short | forced-before |
| V5 | Vedlegg 5: Justeringsavtale (MVA) | mixed | medium | forced-before |
| V6a | Vedlegg 6: Oppgjørsavtale med oppgjørsansvarlig — lån innfris etter tinglysing | mixed | long | forced-before |
| V6b | Vedlegg 6: Oppgjørsavtale med oppgjørsansvarlig — lån innfris ved overtakelse | mixed | long | forced-before |
| V6c | Vedlegg 6: Oppgjørsavtale uten oppgjørsansvarlig | mixed | medium | forced-before |
| B1 | Bilag 1: Fullmakt til pantsettelse | mixed | short | forced-before |
| B2 | Bilag 2: Ugjenkallelig betalingsinstruks | mixed | short | forced-before |

### Table Inventory

| Location | Class | Columns | Purpose |
|----------|-------|---------|---------|
| Header | MsoTableGrid | 2 (Label, Value) | Megler metadata (Megler, Type oppdrag, Eierform, Oppdragsnr, Omsetningsnr) |
| Header | MsoNormalTable | 2 (spacer, content) | Selger party listing (#eiere¤) |
| Header | MsoNormalTable | 2 (spacer, content) | Kjøper party listing (#nyeeiere¤) |
| Section 16 | MsoNormalTable | 3 | Main contract signature block (Selger | empty | Kjøper) |
| Vedlegg 5 | BAHR | 2 (Beskrivelse, Value) | MVA justeringsavtale — building measures table |
| Vedlegg 5 | MsoNormalTable | 3 | Vedlegg 5 signature block (Overdrager | empty | Mottaker) |
| Vedlegg 6a | MsoTableGrid | 4 (Nr, Handling, Ansvarlig, Frist) | Oppgjørsavtale — actions before overtakelse (8 rows) |
| Vedlegg 6a | MsoNormalTable | 3 | Vedlegg 6a signature block (Selger | empty | Kjøper) |
| Vedlegg 6a | MsoNormalTable | 2 | Vedlegg 6a Megler signature block |
| Vedlegg 6b | MsoTableGrid | 4 (Nr, Handling, Ansvarlig, Frist) | Oppgjørsavtale ved overtakelse — actions (10 rows) |
| Vedlegg 6b | MsoNormalTable | 3 | Vedlegg 6b signature block |
| Vedlegg 6b | MsoNormalTable | 2 | Vedlegg 6b Megler signature block |
| Vedlegg 6c | MsoTableGrid | 5 (Nr, Handling, Ansvarlig, Frist, Status) | Oppgjørsavtale uten oppgjørsansvarlig (6 rows) |
| Bilag 1 | MsoNormalTable | 3 | Vitne-signatur section (2 witness columns) |
| Bilag 2 | BAHR | 5 (Nr, Mottaker, Kontonummer, Melding, Beløp) | Betalingsinstruks — payment rows (1–3 + Totalt) |
| Bilag 2 | MsoNormalTable | 1 | Kjøper signature block |
| Bilag 2 | MsoNormalTable | 1 | Selger signature block |

### Checkbox Inventory

| Location | Control Type | Count | Description |
|----------|-------------|-------|-------------|
| Document | N/A | 0 | No explicit checkbox controls in source. Wingdings font referenced in CSS (line 10) but checkbox glyphs not observed in body. Document uses [●] bullet placeholders and alternative text blocks instead. |
| Section 3.2 | data-driven | 1 | Alternative paragraph: "med oppgjørsansvarlig" vs "uten oppgjørsansvarlig" — mutually exclusive wording |
| Section 4.1/4.2 | data-driven | 2 | Kjøper vs Selger betingelser — parallel condition blocks |
| Vedlegg 6a/b/c | data-driven | 3 | Three mutually exclusive Vedlegg 6 alternatives (strykes instructions) |
| Bilag 1 vs Bilag 2 | data-driven | 2 | Bilag 1 strykes if lån innfris etter tinglysing; Bilag 2 benyttes ikke if oppgjørsansvarlig |

**Note:** No broker-interactive checkboxes identified. All branching is via strykes/yellow-highlight instructions indicating conditional inclusion.

### Signature Block

- **Main contract (Section 16):** Party groups: Selger, Kjøper (no Megler in main contract)
- **Per party:** "for [Selger]" / "for [Kjøper]" label, signing line (border-bottom), representative line [Selgers repr.] / [Kjøpers repr.]
- **Uses foreach:** No — single Selger/Kjøper slots (representative names are placeholders)
- **Vedlegg 5:** Overdrager (Selger) | Mottaker (Kjøper) — 2-column layout
- **Vedlegg 6a, 6b, 6c:** Selger | Kjøper in one table; Megler in separate table below
- **Bilag 1:** Single Selger signature + 2 witness signature columns
- **Bilag 2:** Kjøper signature block, then Selger confirmation block

### Party Listings

| Role | Location | Pattern |
|------|----------|---------|
| Selger(e) | Header (#eiere¤), Section 1, Section 16, all Vedlegg and Bilag | Merge-field placeholders; multiple [Selger], [org.nr. Selger], [Selgers repr.] anchors |
| Kjøper(e) | Header (#nyeeiere¤), Section 1, Section 16, all Vedlegg and Bilag | Merge-field placeholders; multiple [Kjøper], [org.nr. Kjøper], [Kjøpers repr.] anchors |
| Megler | Header, Vedlegg 6a/b (Oppgjørsansvarlig), Vedlegg 6c (Megleren), Bilag 2 | [Megler], [org.nr. megler]; single entry |
| Overdrager/Mottaker | Vedlegg 5 | Alias for Selger/Kjøper in MVA context |

### Subsections

| Parent | Sub# | Heading | Notes |
|--------|------|---------|-------|
| 1 | 1.1 | [Selger] | Named anchor Snavn2 |
| 1 | 1.2 | Selger og [Kjøper] | Named anchor Knavn2, Korgnr1 |
| 2 | 2.1 | Kjøpesummen og omkostninger | 2.1.1–2.1.3 |
| 2 | 2.2 | Eiendommens avkastning og kostnader | 2.2.1–2.2.2 |
| 3 | 3.1 | Avtalt overtakelse | Odato7 anchor |
| 3 | 3.2 | Faktisk overtakelse. Oppgjør | Alternative wording block |
| 3 | 3.3 | Forsinkelse | (a)–(d) subpoints |
| 4 | 4.1 | Kjøpers betingelser | (a) only |
| 4 | 4.2 | Selgers betingelser | (a) only |
| 4 | 4.3 | Betydningen av at avtalen bortfaller | — |
| 6 | 6.1–6.4 | Numbered paragraphs | — |
| 7 | 7.1 | Selger garanterer | (a)–(g) subpoints |
| 7 | 7.2 | Med forhold som Selger kjenner til | — |
| 8 | 8.1–8.6 | Multiple subheadings | 8.3.1, 8.3.2, 8.4.1–8.4.3 |
| 9 | 9.1, 9.2 | Subpoints with (a)(i)(ii)(iii) | — |
| 13 | 13.1, 13.2 | Meddelelser | — |
| 14 | 14.1, 14.2 | Lovvalg, tvisteløsning | — |

## Page Break Recommendations

### Short Sections (wrap entire article)
- Section 1: Partene og Eiendommen (~2 paragraphs)
- Section 5: Selgers plikter før Overtakelse (5 subpoints)
- Section 10: Sikkerhet (1 paragraph)
- Section 11: Merverdiavgift
- Section 13: Meddelelser
- Section 14: Lovvalg og tvisteløsning
- Section 15: Vedlegg (list only)

### Internal Wraps Needed
- Section 4: Betingelser — long with 4.1, 4.2, 4.3
- Section 7: Selgers garantier — 7.1 (a)–(g), 7.2
- Section 8: Rett til erstatning — many subpoints

### Forced Page Breaks
- After header/party intro (explicit `page-break-before:always` at line 2035)
- Before Section 16 (Underskrift) — always on fresh page
- Before Vedlegg 5, each Vedlegg 6 alternative, Bilag 1, Bilag 2 (each in separate WordSection divs)

## Source Clues Detected

| Line/Area | Clue | Interpretation |
|-----------|------|----------------|
| CSS line 10 | `font-family:Wingdings` | Font defined; used for possible checkbox/symbol glyphs (not widely observed in body) |
| Section 3.2 | "Hvis oppgjøret gjennomføres uten oppgjørsansvarlig, skriver man her: «Eiendommen blir først overtatt...» [Hvis... skriver man her: «...»]" | Alternative text block — vitec-if for oppgjørsansvarlig vs uten |
| Section 4.1 | "[10] %" placeholder | Fill-in for damage threshold |
| Section 4.2 | "[10] %" placeholder | Same |
| Throughout | `[&#9679;]` or `[•]` | Bullet/dot placeholder — fill-in or merge field |
| Throughout | `[Selger]`, `[Kjøper]`, `[Megler]`, `[org.nr. Selger]`, `[overtakelsesdato]`, `[signeringsdato]`, `[sted]`, `[Selgers repr.]`, `[Kjøpers repr.]` | Named anchors (Snavn2, Korgnr1, Odato7, Sted1, Sdato1, Mnavn1–4, Snavn3–5, Knavn3–5, Srepr1, Krepr1, etc.) — merge field insertion points |
| Section 8.6 | Yellow highlight: `[Strykes hvis det kun er én selger]` | Conditional — single vs multiple sellers |
| Section 10 | Yellow highlight: `[Strykes hvis Selger ikke skal stille sikkerhet]` | Conditional — security requirement |
| Vedlegg 6a title | Yellow highlight: `[dette vedlegget strykes hvis selgers lån skal innfris ved overtakelse, eller hvis oppgjøret skal gjennomføres uten oppgjørsansvarlig.]` | Mutually exclusive Vedlegg 6 selection |
| Vedlegg 6b title | Yellow highlight: `[dette vedlegget strykes hvis selgers lån skal innfris ETTER TINGLYSING AV SKJØTET TIL KJØPER eller hvis oppgjøret skal gjennomføres uten oppgjørsansvarlig.]` | Mutually exclusive |
| Vedlegg 6c title | Yellow highlight: `[dette vedlegget strykes hvis oppgjøret skal gjennomføres med en oppgjørsansvarlig]` | Mutually exclusive |
| Vedlegg 6a §5, 6b §5 | Yellow: `[Om ønskelig kan dette punktet strykes]` / `[Om ønskelig kan dette punktet strykes]` | Optional clause |
| Bilag 1 title | Yellow: `[Dette vedlegget strykes hvis oppgjøret skal gjennomføres etter tinglysing av skjøte]` | Conditional — used only when lån innfris ved overtakelse |
| Bilag 2 title | Yellow: `[Dette vedlegget benyttes ikke hvis oppgjøret gjennomføres med en oppgjørsansvarlig.]` | Conditional — used only when uten oppgjørsansvarlig |
| Header | "Utkast A [dato] av [Megler] ved [forfatter]" | Placeholders |
| Header | "Alternativt: «Partene har tatt de forbehold...»" (in span) | Alternative wording block |
| Various | Footnote refs [1]–[38] | 38 footnotes — advisory/editorial, not conditional structure |
| Vedlegg 5 | `[Angivelse av hvilket byggetiltak...]`, `[Dato]`, `Kr [..]`, `[..] %` | Table cell placeholders |
| Bilag 2 | `[•]` in table cells | Payment instruction placeholders |
| Document | `border-bottom:solid windowtext 1.0pt` on signature cells | Underline for signing lines (solid, not dotted) |
| Vedlegg 7 | `[Datarom på minnepinne]` (italic) | Conditional/optional vedlegg item |
