# Structure Analysis: Kjopekontrakt_prosjekt_enebolig

## Source
- **File:** scripts/source_htm/Kjopekontrakt_prosjekt_enebolig.htm
- **Format:** .htm
- **Encoding:** windows-1252
- **Total sections:** 20

## Document Skeleton

### Section List

| # | Heading | Type | Length | Page Break |
|---|---------|------|--------|------------|
| 0 | (Header + intro) | header-info | short | — |
| 1A | Salgsobjekt og tilbehør (selveiet bolig/fritidsbolig) | mixed | medium | — |
| 1B | Salgsobjekt og tilbehør (bolig/fritidsbolig i sameie) | mixed | long | forced-before |
| 2 | Kjøpesum og omkostninger | financial | long | forced-before |
| 3 | Selgers plikt til å stille garantier | legal-text | short | avoid-break |
| 4 | Oppgjør | terms | medium | forced-before |
| 5 | Heftelser | legal-text | medium | — |
| 6 | Tinglysing/sikkerhet | legal-text | short | — |
| 7 | Selgers mangelsansvar/Kjøpers reklamasjonsplikt | legal-text | short | — |
| 8 | Endringsarbeider, tilleggsarbeider og tilvalg | legal-text | medium | — |
| 9 | Overtakelse | mixed | long | forced-before |
| 10 | Ettårsbefaring | legal-text | short | — |
| 11 | Selgers kontraktsbrudd | legal-text | short | — |
| 12 | Kjøpers kontraktsbrudd | legal-text | medium | — |
| 13 | Forsikring | legal-text | short | — |
| 14 | Avbestilling | legal-text | short | — |
| 15 | Selgers forbehold | checkbox-section | medium | — |
| 16 | Annet | terms | long | — |
| 17 | Samtykke til bruk av elektronisk kommunikasjon | legal-text | short | — |
| 18 | Verneting | legal-text | short | — |
| 19 | Bilag | checkbox-section | medium | forced-before |
| 20 | Signatur | signature-block | short | forced-before |

Type values: `party-listing`, `financial`, `legal-text`, `checkbox-section`, `signature-block`, `header-info`, `terms`, `mixed`

Length values: `short` (1-4 paragraphs), `medium` (5-10), `long` (10+)

Page Break values: `avoid-break`, `internal-wrap`, `forced-before`, `—`

### Table Inventory

| Location | Class | Columns | Purpose |
|----------|-------|---------|---------|
| Section 0 | party-table | 1 | Buyer contact info (name, address, mobile, email) |
| Section 2 | payment-schedule | 5 | Vederlag tomt, Delbetaling, Rest, Kjøpesum breakdown |
| Section 2 | costs-table | 5 | Dokumentavgift, Tinglysingsgebyr skjøte, Tinglysingsgebyr pantedokument, Attestgebyr, Driftskonto, Sum omkostninger |
| Section 2 | total-table | 5 | Kjøpesum inkl. omkostninger (summary row) |
| Section 20 | signature-table | 3 | Selger(e) | spacer | Kjøper(e) party labels |
| Section 20 | fullmakt-table | 3 | Fullmaktsinnehaver row for Kjøper column |

### Checkbox Inventory

| Location | Control Type | Count | Description |
|----------|-------------|-------|-------------|
| Section 1A | data-driven | 5 | bolig, fritidsbolig, andel realsameie (mutually exclusive); tomt eiet/festet (mutually exclusive) |
| Section 1B | data-driven | 11 | bolig eierseksjon, fritidsbolig eierseksjon, andel realsameie (mutually exclusive); tomt eiet/festet; Garasjeplass, Parkeringsplass, Bruksrett, Tilleggsareal, Gjesteparkering |
| Section 4 | data-driven | 2 | For tomten vs For boligen (mutually exclusive oppgjørsform) |
| Section 5 | broker-interactive | 4 | Pengeheftelser fri / med unntak; Andre heftelser ikke / følge med |
| Section 9 | data-driven | 2 | Alternativ 1 (fast dato) vs Alternativ 2 (forventet ferdigstillelse) |
| Section 15 | broker-interactive | 4 | xx % boliger solgt, kommunen tillatelse, byggelån, styre beslutning (Symbol font placeholder) |
| Section 19 | broker-interactive | 10 | Bilag checklist: Salgsoppgave, Grunnboksutskrift, Grunnboksutskrift fellesarealer, Erklæringer, Reguleringsplan, Kommunen, Målebrev, Ferdigattest, Protokoll, Annet |

Control Type values: `data-driven` (system sets via vitec-if), `broker-interactive` (user toggles)

### Signature Block

- **Party groups:** Selger(e), Kjøper(e) — no Megler block
- **Per party:** Label line with underline for signature; no explicit date fields (Sted/Dato appears once at top, duplicated for both parties)
- **Uses foreach:** Yes — party names come from #eiere¤ / #nyeeiere¤ merge patterns; fullmaktsinnehaver for Kjøper (#fullmaktsinnehavereb_kjoper¤)
- **Layout:** Two-column table; Selger left, Kjøper right; below labels a second table shows fullmaktsinnehaver in Kjøper column only

### Party Listings

| Role | Location | Pattern |
|------|----------|---------|
| Selger(e) | Section 0, Signature | #eiere¤, #flettblankeeiere¤ merge pattern; no explicit table, paragraph layout |
| Kjøper(e) | Section 0, Signature | #nyeeiere¤ merge pattern; table for contact rows; #fullmaktsinnehavereb_kjoper¤ in signature |
| Megler | — | Not listed in this template |

### Subsections (if any)

| Parent | Sub# | Heading | Notes |
|--------|------|---------|-------|
| 1 | 1A | Salgsobjekt og tilbehør (selveiet bolig/fritidsbolig) | eieform conditional — selveiet |
| 1 | 1B | Salgsobjekt og tilbehør (bolig/fritidsbolig i sameie) | eieform conditional — eierseksjon/realsameie |
| 4 | 4a | Oppgjørsform: For tomten / For boligen | continuation of Section 4 on new page |
| 9 | 9a | Alternativ 1 | Fixed date overtakelse |
| 9 | 9b | Alternativ 2 | Forventet ferdigstillelse |

## Page Break Recommendations

### Short Sections (wrap entire article)
- Section 3: Selgers plikt til å stille garantier (4 paragraphs)
- Section 6: Tinglysing/sikkerhet (~4 paragraphs)
- Section 7: Selgers mangelsansvar (~4 paragraphs)
- Section 10: Ettårsbefaring (1 paragraph)
- Section 11: Selgers kontraktsbrudd (1 paragraph)
- Section 13: Forsikring (~4 paragraphs)
- Section 14: Avbestilling (~2 paragraphs)
- Section 17: Samtykke elektronisk kommunikasjon (1 paragraph)
- Section 18: Verneting (1 paragraph)

### Internal Wraps Needed
- Section 2: Heading + payment-schedule table + costs-table — avoid break between table groups
- Section 1A / 1B: Each subsection is substantial; 1B has many checkboxes — consider avoid-break per subsection
- Section 9: Alternativ 1/2 block + following text — keep each alternative block together

### Forced Page Breaks
- Before Section 1B — explicit page-break-before in source (WordSection2)
- Before Section 2 — explicit page-break-before (WordSection3)
- Before Section 4 continuation (oppgjørsform) — explicit (WordSection4)
- Before Section 9 — major document transition
- Before Section 19 (Bilag) — explicit (WordSection6)
- Before Section 20 (Signatur) — always on fresh page

## Source Clues Detected

| Line/Area | Clue | Interpretation |
|-----------|------|----------------|
| Header | Oppdragsnummer, Omsetningsnummer merge fields | — |
| Section 1A | Wingdings 'q' (5 occurrences) | Checkbox locations: bolig, fritidsbolig, andel realsameie, tomt eiet, tomt festet |
| Section 1A | Red "xx" before "andel i realsameie" | Placeholder or conditional marker |
| Section 1A | Red "fra/`<u>med</u>`" (dotted underline) | Alternative text — conditional preposition |
| Section 1A | Red "Boligen/fritidsboligen" (2×) | Conditional singular/plural |
| Section 1B | Same Wingdings + red patterns | Parallel to 1A; one Wingdings has color:red |
| Section 1B | Red "xx andel i realsameie", red "i ……….kommune" | Placeholder or conditional |
| Section 1B | Yellow background "……" | Insert field for felleskostnad first year |
| Section 2 | Underlined kjøpesum | Merge field / insert location |
| Section 2 | color:#221E1F "00/100" | Conditional ore/decimal display |
| Section 2 | Yellow background on amounts (200 000, 2 800 000, 5000, 525, 5 000, 11 252) | Placeholder values for merge |
| Section 2 | `<u>` wrappers | Dotted underline / insert locations |
| Section 4 | Wingdings 'q' (2×) | For tomten / For boligen checkboxes |
| Section 5 | Wingdings 'q' (4×) | Pengeheftelser + Andre heftelser options |
| Section 6 | Red trailing space | Minor clue, possibly stray |
| Section 9 | "Alternativ 1:" / "Alternativ 2:" text | vitec-if branching for overtakelse type |
| Section 9 | Wingdings 'q' (2×) | One per alternative |
| Section 15 | Symbol font (4× &nbsp; before items) | Placeholder for checkbox — xx % solgt, kommunen, byggelån, styre |
| Section 15 | Symbol "·" bullet | List marker for "Dersom selger gjør forbehold" |
| Section 19 | Wingdings 'q' (10×) | Bilag checklist items |
| Various | Dotted underlines | Insert field locations (merge fields) |
