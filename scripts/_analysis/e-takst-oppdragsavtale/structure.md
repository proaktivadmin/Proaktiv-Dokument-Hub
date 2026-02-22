# Structure Analysis: E-takst oppdragsavtale

## Source
- **File:** `E-takst oppdragsavtale.htm` (from OneDrive_2026-02-21/maler vi må få produsert/)
- **Format:** .htm (Word HTML export)
- **Encoding:** windows-1252 (from meta charset)
- **Total sections:** 10 numbered sections + 1 main signature block + 1 conditional appendix (PEP) + 1 vedlegg (Angreskjema)

## Document Skeleton

### Section List

| # | Heading | Type | Length | Page Break |
|---|---------|------|--------|------------|
| — | Header (logo image, title "BESTILLING AV VERDIVURDERING/E-TAKST") | header-info | short | — |
| 1 | Eiendommen | header-info | short | — |
| 2 | Eier/oppdragsgiver | party-listing | medium | — |
| 3 | Oppdragstaker | party-listing | short | — |
| 4 | Oppdraget | legal-text | short | avoid-break |
| 5 | Formål og bakgrunn | mixed | medium | — |
| 6 | Kundetiltak etter Lov om tiltak mot hvitvasking og terrorfinansiering | legal-text | medium | — |
| 7 | Politisk eksponert person | checkbox-section | short | avoid-break |
| 8 | Vederlag | financial | short | avoid-break |
| 9 | Personvern | terms | short | avoid-break |
| 10 | Angrerett | mixed | medium | internal-wrap |
| — | Signature block (Sted, Dato, Sign. oppdragsgiver) | signature-block | short | forced-before |
| 11 | Egenerklæring Politisk Eksponert Person | checkbox-section | long | forced-before |
| — | Angreskjema (ved kjøp av ikke finansielle tjenester) | terms | medium | — |

Type values: `party-listing`, `financial`, `legal-text`, `checkbox-section`, `signature-block`, `header-info`, `terms`, `mixed`

Length values: `short` (1-4 paragraphs), `medium` (5-10), `long` (10+)

Page Break values: `avoid-break`, `internal-wrap`, `forced-before`, `—`

### Table Inventory

| Location | Class | Columns | Purpose |
|----------|-------|---------|---------|
| Section 5 | MsoTableGrid (left) | 2 (Formål option, Wingdings checkbox) | Purpose selection — 7 rows (Salg, Refinansiering, Bytte bank, Oppta boligkreditt, Oppta lån til oppussing, Oppta lån for kjøp av fritidseiendom, Oppta lån for kjøp av sekundærbolig) |
| Section 5 | MsoTableGrid (right) | 2 (Formål option, Wingdings checkbox) | Purpose selection — 6 rows (Stille bolig som sikkerhet/realkausjon, Vil bare vite hva boligen er verdt, Arveoppgjør/forskudd på arv, Samlivsbrudd, Refinansiere annen gjeld) |
| Section 11 | List structure (Symbol bullets) | N/A | PEP declaration checklist — two list groups |
| Angreskjema | MsoNormalTable | 1 (spacer) | Service description lines (2 rows with top border) |
| Angreskjema | MsoNormalTable | 3 (label, date, spacer) | "Avtalen ble inngått den (dato)" row |
| Angreskjema | MsoNormalTable | 3 (label, date field, spacer) | "Dato:" with underline |
| Angreskjema | MsoNormalTable | 1 | "Forbrukerens/forbrukernes underskrift" row |

### Checkbox Inventory

| Location | Control Type | Count | Description |
|----------|-------------|-------|-------------|
| Section 5 | broker-interactive | 13 | Formål tables — left table 7 options, right table 6 options; mutually exclusive (single choice) |
| Section 5 | broker-interactive | 1 | "Eiendommen er ikke verdivurdert siden den ble kjøpt" — single checkbox |
| Section 7 | broker-interactive | 2 | Ja / Nei — PEP question (mutually exclusive) |
| Section 10 | broker-interactive | 2 | "Jeg ønsker at..." vs "Jeg ønsker IKKE at..." — førtidig oppstart of angrerett (mutually exclusive) |
| Section 11 | broker-interactive | 16+ | PEP declaration — Symbol font ð bullets as checklist items; user marks applicable categories |

Control Type values: `data-driven` (system sets via vitec-if), `broker-interactive` (user toggles)

### Signature Block

- **Party groups:** Oppdragsgiver only (single signer)
- **Per party:** Sted (line) + Dato (line) + Sign. oppdragsgiver (signing line)
- **Uses foreach:** No — single block for one client signer
- **Note:** Section 2 has two owner slots (Eier 1, Eier 2) but the main signature block does not repeat; single "Sign. oppdragsgiver" line only

### Party Listings

| Role | Location | Pattern |
|------|----------|---------|
| Eier/Oppdragsgiver | Section 2 | 2 slots — Navn, Fnr, Statsborgerskap, Adr, Mobil, E-post; second slot blank (repeatable for additional owners) |
| Oppdragstaker | Section 3 | Single — Selskap, Megler |
| Signatur | Main block | Oppdragsgiver only |
| PEP skjema | Section 11 | Conditional page; filled when Section 7 = Ja |

### Subsections (if any)

| Parent | Sub# | Heading | Notes |
|--------|------|---------|-------|
| 5 | 5A | Formål table (left) | 7 formål options |
| 5 | 5B | Formål table (right) | 6 formål options |
| 5 | 5C | Bakgrunn questions | Når kjøpt, Kjøpesum, Forrige verdivurdering årstall, "Eiendommen er ikke verdivurdert..." checkbox |
| 10 | 10A | Angrerett legal text | 4 paragraphs |
| 10 | 10B | Førtidig oppstart checkboxes | 2 mutually exclusive options |
| 11 | 11A | "Jeg er eller har vært" list | 8 Symbol ð bullets |
| 11 | 11B | "Jeg er nærstående til" list | 5 Symbol ð bullets |
| 11 | 11C | "Jeg er kjent medarbeider..." list | 3 Symbol ð bullets |

## Page Break Recommendations

### Short Sections (wrap entire article)
- Section 4: Oppdraget (2 paragraphs)
- Section 7: Politisk eksponert person (2 paragraphs)
- Section 8: Vederlag (1 paragraph)
- Section 9: Personvern (1 paragraph)

### Internal Wraps Needed
- Section 10: Heading + legal text + checkbox subsection — avoid breaking between "Førtidig oppstart" heading and the two checkbox options

### Forced Page Breaks
- Before main signature block — WordSection3 starts with page-break-before
- Before Section 11 (Egenerklæring PEP) — WordSection4 starts with page-break-before; conditional on PEP=Ja
- Document uses `page-break-before:always` between WordSection1→2, 2→3, 3→4

## Source Clues Detected

| Line/Area | Clue | Interpretation |
|-----------|------|-----------------|
| Section 5 tables | Wingdings 'o' (font-family:Wingdings; character 'o') | Checkbox/radio locations — circle bullet; one selected per group |
| Section 5 | "Eiendommen er ikke verdivurdert..." + Wingdings 'o' | Standalone checkbox (alternate to year input) |
| Section 7 | "Ja" + Wingdings 'o' / "Nei" + Wingdings 'o' | Mutually exclusive Ja/Nei for PEP |
| Section 7 | "Hvis «Ja», må skjema på s. 3 fylles ut" | Conditional inclusion — PEP declaration (Section 11) only when Ja |
| Section 10 | Segoe UI Symbol &#9744; (empty checkbox) | Two checkbox options for angrerett/førtidig oppstart |
| Section 11 | Symbol font 'ð' (delta) | Bullet list for PEP categories — 8 + 5 + 3 items |
| Section 2 | Statsborgerskap:___________ | Underscore fill-in (insert field) |
| Section 2 | Second owner slot (Navn, Fnr blank) | Repeatable owner block — possible foreach |
| Section 1 | Borettslag / Andelsnr fields | Conditional visibility for borettslag vs selveier |
| Section 1 | Empty span with text-decoration:none inside u tag | Dotted underline placeholder (line 185-186) |
| Various | background:#4F81BD on headings | Section header styling (blue band) |
| Various | background:#B8CCE4 on table cells | Light blue table header/cell background |
| Angreskjema | Reference "s. 3" in Section 7 | PEP skjema is on page 3 (Section 11) — conditional page |
