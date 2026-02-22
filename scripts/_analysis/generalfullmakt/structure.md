# Structure Analysis: Generalfullmakt

## Source
- **File:** `13.Generalfullmakt.htm` (from Downloads)
- **Format:** .htm (Word HTML export)
- **Encoding:** windows-1252
- **Total sections:** 7

## Document Skeleton

### Section List

| # | Heading | Type | Length | Page Break |
|---|---------|------|--------|------------|
| 1 | GENERALFULLMAKT (title + sted/dato) | header-info | short | — |
| 2 | Matrikkel og adresse | header-info | short | avoid-break |
| 3 | Det gis herved... fullmakt (grant intro) | party-listing | short | avoid-break |
| 4 | Powers list (tinglysing, deling, byggemelding, etc.) | legal-text | short | avoid-break |
| 5 | Scope, limitation, personal liability disclaimer | legal-text | short | avoid-break |
| 6 | Fullmaktsgiver (signature block) | signature-block | short | forced-before |
| 7 | Ektefelle/partner samtykke / Vitnepåtegning | mixed | short | avoid-break |

Type values: `party-listing`, `financial`, `legal-text`, `checkbox-section`,
`signature-block`, `header-info`, `terms`, `mixed`

Length values: `short` (1-4 paragraphs), `medium` (5-10), `long` (10+)

Page Break values:
- `avoid-break` — short section, wrap entire article
- `internal-wrap` — long section, needs internal avoid-break divs
- `forced-before` — major transition, add page-break-before
- `—` — no special treatment needed

### Table Inventory

| Location | Class | Columns | Purpose |
|----------|-------|---------|---------|
| Section 1 | MsoTableGrid | 2 (Title, Sted/dato) | Title and place/date header |
| Section 2 | MsoTableGrid | 2 (Label, Value) | Property info: Matrikkel, Adresse |
| Section 6 | MsoTableGrid | 3 (Signatur, Navn i blokkbokstaver, Fødselsnummer) | Signature block — 1 header row + 4 data rows |

### Checkbox Inventory

| Location | Control Type | Count | Description |
|----------|-------------|-------|-------------|
| Section 7 | data-driven | 2 | sjekkliste2901085=4 vs =3 — mutually exclusive spouse consent text (eiendommen eies sammen vs eiendommen tjener ikke til felles bopæl) |
| Section 7 | data-driven | 2 | #standard_ektefellesamtykke¤ and #standard_vitnepaategning¤ — conditional blocks for spouse consent and witness attestation |

Control Type values: `data-driven` (system sets via vitec-if), `broker-interactive` (user toggles)

**Note:** No explicit checkbox controls or Wingdings glyphs in source. Conditional text driven by merge-field conditionals (#hvis[sjekkliste2901085=...], #standard_ektefellesamtykke¤, #standard_vitnepaategning¤).

### Signature Block

- **Party groups:** Fullmaktsgiver only (single party — grantor(s) of power of attorney)
- **Per party:** Signatur (signing line), Navn i blokkbokstaver, Fødselsnummer (evt. orgnr)
- **Uses foreach:** Yes — 4 data rows with #nesteeier¤ / #personnummer.kontakter¤ pattern; first row uses #flettblankeeiere¤#nesteeier¤
- **Header label:** Conditional — "Fester" vs "Hjemmelshaver" per #hvis[eierformtomt=2311|2312]

### Party Listings

| Role | Location | Pattern |
|------|----------|---------|
| Fullmaktsgiver(e) | Section 3 (intro), Section 6 (signature block) | #forsteselger¤, #nesteeier¤; #flettblankeeiere¤ gates blank rows; #kundenavn.kontakter¤, #pnrorgnrb.kontakter¤, #personnummer.kontakter¤ |
| — | — | Single party type; role label conditional (Fester/Hjemmelshaver) |

### Subsections (if any)

| Parent | Sub# | Heading | Notes |
|--------|------|---------|-------|
| 4 | 4.1 | Powers bullet list | 6 items (tinglysing, deling, byggemelding, overskjøting, pantsettelse, oppgjør) |
| 5 | 5.1 | Scope paragraph | ".. samt ethvert tiltak..." |
| 5 | 5.2 | Fullmakt til undertegne | Tinglysingsloven § 13 |
| 5 | 5.3 | Limitation | "Fullmakten gjelder kun forføying..." with conditional settinntekst |

## Page Break Recommendations

### Short Sections (wrap entire article)
- Section 1: Title block
- Section 2: Matrikkel/adresse table
- Section 3: Grant intro
- Section 4: Powers list (6 bullets)
- Section 5: Scope/limitation paragraphs
- Section 7: Conditional spouse/witness text

### Internal Wraps Needed
- None — document is short; single-page layout

### Forced Page Breaks
- Before Section 6 (Fullmaktsgiver signature block) — always on fresh page

## Source Clues Detected

| Line/Area | Clue | Interpretation |
|-----------|------|----------------|
| Lines 74–85 | Title "GENERALFULLMAKT" + "Sted, dato: __________________,_______________" | Placeholder underscores for place/date fill-in |
| Lines 90–111 | Table with Matrikkel, Adresse | Property metadata; #matrikkelkommune.oppdrag¤, #adresse.oppdrag¤, etc. |
| Line 117 | #flettblankeeiere¤#forsteselger¤ | Conditional first-seller intro (possibly blank if no secondary owners) |
| Line 118 | #kundenavn.kontakter¤ #pnrorgnrb.kontakter¤ | Grantor identity merge fields |
| Lines 123–139 | Symbol font · (bullet) | Bullet list — 6 powers; not Wingdings |
| Line 163 | #hvis[eierformtomt=2311\|2312] settinntekst fester/hjemmelshaver | Conditional role label in limitation clause |
| Line 172 | #hvis[eierformtomt=2311\|2312] settinntekst Fester/Hjemmelshaver | Same conditional in signature block header |
| Lines 201–256 | 4 data rows with #nesteeier¤ / #personnummer.kontakter¤ | Repeated pattern — vitec-foreach for multiple grantors |
| Line 263 | #fontsize_10¤ | Font size switch |
| Line 263 | #hvis[sjekkliste2901085=4]settinntekst_...Ektefelle/partner samtykke er ikke aktuelt...¤ | Checkbox-driven: value 4 = spouse consent not relevant (owned together) |
| Line 263 | #hvis[sjekkliste2901085=3]settinntekst_...Eiendommen tjener ikke til felles bopæl...¤ | Checkbox-driven: value 3 = property not shared residence |
| Line 263 | #standard_ektefellesamtykke¤ | Conditional block for spouse consent section |
| Line 263 | #standard_vitnepaategning¤ | Conditional block for witness attestation section |
| Line 263 | HTML entities &lt;br&gt; inside settinntekst | Line breaks in conditional text |
| Section 6 | Gray background (#E6E6E6) on header row | Visual styling for signature table header |
| — | No Wingdings characters | Document uses Symbol bullets (·), not checkbox glyphs |
| — | No red text | No red styling in source |
| — | No "Alt 1/2" markers | Alternatives expressed via #hvis conditionals |
| — | No dotted underlines | Underscores in "Sted, dato" are placeholder-style blanks |
