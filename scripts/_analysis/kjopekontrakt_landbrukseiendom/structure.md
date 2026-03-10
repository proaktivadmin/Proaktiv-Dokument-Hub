# Structure Analysis: Kjøpekontrakt landbrukseiendom

## Source
- **File:** c:\Users\Adrian\Downloads\14.Kjøpekontrakt landbrukseiendom.htm
- **Format:** .htm
- **Encoding:** windows-1252
- **Total sections:** 12

## Document Skeleton

### Section List

| # | Heading | Type | Length | Page Break |
|---|---------|------|--------|------------|
| 1 | (Preamble) Megler info, KJØPEKONTRAKT, Mellom partene | header-info / party-listing | medium | — |
| 2 | § 1 SALGSOBJEKT OG TILBEHØR | legal-text | medium | — |
| 3 | § 2 KJØPESUM OG OMKOSTNINGER | financial | short | — |
| 4 | § 3 OPPGJØR | legal-text | long | internal-wrap |
| 5 | § 4 TINGLYSING OG SIKKERHET | legal-text | long | internal-wrap |
| 6 | § 5 HEFTELSER | checkbox-section / legal-text | medium | — |
| 7 | § 6 FORBEHOLD OM EIENDOMMENS TILSTAND – SELGERS MANGELSANSVAR | legal-text | medium | — |
| 8 | § 7 OVERTAGELSE | legal-text | short | avoid-break |
| 9 | § 8 KONSEKVENSER AV MISLIGHOLD – REKLAMASJON | legal-text | short | avoid-break |
| 10 | § 9 FORSIKRING | legal-text | short | avoid-break |
| 11 | § 10 BILAG | terms | medium | — |
| 12 | (Signature block) | signature-block | short | forced-before |

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
| Section 1 | header-table | Megler, Type oppdrag, Eierform, Oppdragsnr, Omsetningsnr | Header info (label + value pairs) |
| Section 1 | party-intro | Mellom, (blank), (blank) | Party declaration spacer |
| Section 1 | selger-address | (indent), Address/contact | Party listing (selger) |
| Section 1 | kjoper-address | (indent), Address/contact | Party listing (kjøper) |
| Section 3 | costs-table | Kjøpesum og omkostninger, Beløp, (empty) | Payment breakdown header row |
| Section 12 | signature-table | Kjøper, Selger | Signature block (2-column layout) |

### Checkbox Inventory

| Location | Control Type | Count | Description |
|----------|-------------|-------|-------------|
| Section 6 (§ 5) | broker-interactive | 2 | Pengeheftelser: (a) fri for pengeheftelser vs (b) fri med unntak — mutually exclusive |
| Section 4 (3.6) | data-driven | 2 | Alternativ A vs B for fordelingsregnskap — red "Stryk det alternativ som ikke passer" |
| Section 5 (4.2) | data-driven | 2 | Alternativ A vs B for konsesjonsrisiko — red "Stryk det alternativ som ikke passer" |
| Section 6 (Odel) | data-driven | 3 | Alternativ A vs B vs C for odel — red "Stryk de alternativer som ikke passer" |

Control Type values: `data-driven` (system sets via vitec-if), `broker-interactive` (user toggles)

### Signature Block

- **Party groups:** Kjøper, Selger (no Megler column in signature table)
- **Per party:** Signing line (dotted), name/proxy merge field (#fullmaktsinnehavereb_kjoper¤ / #fullmaktsinnehavereb_selger¤)
- **Uses foreach:** Unclear from structure — appears to use single merge fields per party
- **Post-signature blocks:** Conditional blocks (#hvis[sjekkliste2901085=1]standard_ektefellesamtykke¤, #hvis[sjekkliste2901085=2]standard_partnersamtykke¤, #standard_oppgjorsinstruks¤)

### Party Listings

| Role | Location | Pattern |
|------|----------|---------|
| Selger(e) | Section 1 | #eiere¤, #flettblankeeiere¤, #forsteeier¤, #kunadresse.kontakter¤, Mobil/E-post |
| Kjøper(e) | Section 1 | #nyeeiere¤, #flettblankeeiere¤, #forstenyeier¤, #kunadresse.kontakter¤, Mobil/E-post |
| Megler | Section 1 (header) | Single entry: #navn.firma¤, #organisasjonsnummer.firma¤, etc. |

### Subsections (if any)

| Parent | Sub# | Heading | Notes |
|--------|------|---------|-------|
| 4 | 3.1 | Ytelse mot ytelse | Italic subheading |
| 4 | 3.2 | Konto og betalingstidspunkt. Forsinkelsesrenter ved forsinket betaling. | Italic subheading |
| 4 | 3.3 | Betalingsforsinkelse fra kjøper som utgjør vesentlig mislighold | Italic subheading |
| 4 | 3.4 | Forsinket overlevering fra selger | Italic subheading |
| 4 | 3.5 | Kjøpers øvrige forpliktelser forbundet med dokumentasjon og oppgjør | Italic subheading |
| 4 | 3.6 | Driftsutgifter og driftsinntekter på eiendommen. Renter på klientkonto | Italic subheading; contains A/B alternatives |
| 5 | 4.1 | Forutsetninger for oppgjør og frigivelse av kjøpesummen | Italic subheading |
| 5 | 4.2 | Konsesjonsrisiko | Italic subheading; contains A/B alternatives |
| 5 | 4.3 | Deponering og tinglysing av skjøtet og andre dokumenter for tinglysing | Italic subheading |
| 5 | 4.4 | Tinglysing av panterett med urådighet (sikringsobligasjon) | Italic subheading |
| 5 | 4.5 | Selgers forbehold om kjøpers oppfyllelse | Italic subheading |

## Page Break Recommendations

### Short Sections (wrap entire article)
- Section 8: Overtakelse (6 paragraphs)
- Section 9: Konsekvenser av mislighold (3 paragraphs)
- Section 10: Forsikring (5 paragraphs)

### Internal Wraps Needed
- Section 4 (§ 3 OPPGJØR): 6 subsections — keep 3.1–3.6 together where possible
- Section 5 (§ 4 TINGLYSING OG SIKKERHET): 5 subsections — avoid breaking mid-subsection

### Forced Page Breaks
- Before § 1 (document has explicit `page-break-before:always` in source) — major transition from preamble to contract body
- Before Signature block — always on fresh page

## Source Clues Detected

| Line/Area | Clue | Interpretation |
|-----------|------|----------------|
| Section 6 | MS Gothic &#9744; (☐) characters | Checkbox/checkmark locations for pengeheftelser |
| Section 4 (3.6) | Red "[Stryk det alternativ som ikke passer]" | vitec-if branching instruction |
| Section 4 (3.6) | Red "**A**" / "**B**" labels | Alternativ A vs B for fordelingsregnskap |
| Section 5 (4.2) | Red "[Stryk det alternativ som ikke passer]" | vitec-if branching instruction |
| Section 5 (4.2) | Red "**A**" / "**B**" labels | Alternativ A vs B for konsesjonsrisiko |
| Section 6 (Odel) | Red "[Stryk de alternativer som ikke passer]" | vitec-if branching (3-way: A, B, C) |
| Section 6 (Odel) | Red "**A**" / "**B**" / "**C**" labels | Alternativ A/B/C for odel |
| Various | Dotted underlines "……………" | Manual fill / insert field locations (gårdskart dato, eiendomsverdien, klientkonto, grunnbok dato, etc.) |
| § 1 | "datert ………" | Manual date fill for takst/gårdskart |
| § 2 | "kroner ….………." | Manual fill for eiendomsverdien |
| § 3 | "klientkonto nr. ………………………" | Manual fill for account number |
| § 5 | "datert ……." | Manual fill for grunnbok date |
| § 10 | "dagboknummer/dokumentnummer:…………", "Takst datert …………" | Manual fill locations |
| § 10 | "Annet: ……………………………………………." | Manual fill for annex list |
| Signature | "………………………………………………" / "……………………………………………" | Signature line placeholders |
| Post-signature | #hvis[sjekkliste2901085=1] / [=2] | Conditional blocks for ektefellesamtykke vs partnersamtykke |
| § 1, § 6 | Symbol font "·" bullets | Bullet lists (mangel cases, etc.) |
