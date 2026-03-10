# Handoff: Standard Leieavtale for Næringsbygg — Brukt/Nytt kombinert

## Production File
`scripts/converted_html/Leieavtale_naeringsbygg_PRODUCTION.html` (736 lines)

## Source Documents
- `Standard leieavtale for næringsbygg (Brukt - som det er) 8. utgave 2025.pdf` (31 pages — 16 main + 15 supplements)
- `Standard leieavtale for næringsbygg (Nytt/rehabilitert) 6. utgave 2025.pdf`
- `Leieavtale næringsbygg.pdf` (combined variant preview from Vitec with sample data)

## Template Classification
- **Mode:** A (create new from standard PDF source)
- **Tier:** T4 (dual-variant form with interactive checkboxes, manual fill-in fields, no vitec-if logic)

## Architecture: Dual-Variant Template

This template combines **both** contract variants ("Brukt / som det er" and "Nytt / rehabilitert") in a single template. The user selects which variant to use via checkbox at the top. This is correct for this document type — the standard form is designed so both variants print and the broker manually strikes through the inapplicable one.

### Toggle-Hide Feature (CSS :has())
- Selecting **Brukt** checkbox hides all `variant-nytt` sections
- Selecting **Nytt** checkbox hides all `variant-brukt` sections
- Selecting **both** (or neither) shows all sections
- Uses CSS `:has()` — works in modern browsers (Chrome 105+, Firefox 121+, Safari 15.4+)
- In Vitec PDF output, both variants print regardless (intended behavior)

## What's Included

### Main Contract (Sections 1–35 + Bilag + Signatur)

| Section | Heading | Variant Handling |
|---------|---------|------------------|
| Header | Megler org.nr, oppdragsnr, omsetningsnr | 3 Vitec merge fields |
| Variant Selector | Brukt/Nytt checkbox choice | Interactive SVG checkboxes with toggle-hide |
| 1 | UTLEIER | Identical — insert fields |
| 2 | LEIETAKER | Identical — insert fields |
| 3 | EIENDOMMEN | Identical — gnr/bnr/fnr/snr inserts |
| 4 | LEIEOBJEKTET | **Brukt/Nytt** — 4 variant divs (4.1 × 2, areal alt, 4.4 × 2) |
| 5 | LEIETAKERS VIRKSOMHET | Identical |
| 6 | OVERTAKELSE/MELDING OM MANGLER | **Brukt/Nytt** — 4 variant divs (6.1 × 2, 6.3 × 2) |
| 7 | LEIEPERIODEN | **Brukt/Nytt** — 2 variant divs |
| 8 | LEIEN | **Brukt/Nytt** — 4 variant divs (8.1 × 2, 8.2 checkboxes × 2) |
| 9 | LEIEREGULERING | Identical |
| 10 | MERVERDIAVGIFT | Identical — 3 SVG checkboxes (A/B/C) |
| 11 | SIKKERHETSSTILLELSE | Identical |
| 12 | LEIETAKERS BRUK AV LEIEOBJEKTET | Identical |
| 13 | UTLEIERS ADGANG TIL LEIEOBJEKTET MV. | Identical |
| 14 | UTLEIERS VEDLIKEHOLDS- OG UTSKIFTINGSPLIKT | **Brukt only** — 1 variant div (14.2) |
| 15 | LEIETAKERS PLIKT TIL DRIFT OG VEDLIKEHOLD | Identical |
| 16 | UTLEIERS ARBEIDER I LEIEOBJEKTET/EIENDOMMEN | Identical |
| 17 | LEIETAKERS ENDRING AV LEIEOBJEKTET | Identical |
| 18 | FORSIKRING | Identical |
| 19 | BRANN/DESTRUKSJON | **Brukt/Nytt** — 2 variant divs |
| 20 | UTLEIERS AVTALEBRUDD | **Brukt/Nytt** — 2 variant divs (Nytt adds dagmulkt) |
| 21 | LEIETAKERS AVTALEBRUDD/UTKASTELSE | Identical (references punkt 20.4/20.7) |
| 22 | FRAFLYTTING | Identical |
| 23 | TINGLYSING/PANTSETTELSE | Identical |
| 24 | FREMLEIE | Identical |
| 25 | OVERDRAGELSE | Identical |
| 26 | KONTROLLSKIFTE, FUSJON OG FISJON | Identical |
| 27 | MILJØ OG SIRKULÆRE LØSNINGER | Identical |
| 28 | INFORMASJONSUTVEKSLING OG INNHENTING AV DATA MV. | Identical |
| 29 | MENNESKERETTIGHETER, HVITVASKING OG KORRUPSJON MV. | Identical |
| 30 | PERSONVERN | Identical |
| 31 | ANDRE DATA (SOM IKKE ER PERSONOPPLYSNINGER) | Identical |
| 32 | SAMORDNINGSAVTALE FOR BRANNFOREBYGGING | Identical |
| 33 | SÆRLIGE BESTEMMELSER/FORBEHOLD | Identical — free text insert |
| 34 | FORHOLDET TIL HUSLEIELOVEN | Identical |
| 35 | LOVVALG OG TVISTELØSNING | Identical |
| — | BILAG TIL LEIEAVTALEN | **Brukt/Nytt** — 2 variant lists (Brukt: 10 items, Nytt: 12 items) |
| — | SIGNATUR | **Brukt/Nytt** — 3 variant divs (Nytt sted/dato, signatur × 2) |

### Summary
- **35 sections** + bilag + signatur (100% coverage from source PDFs)
- **22 sections** identical between variants (shared)
- **13 sections** with variant-specific content (Brukt/Nytt divs)

## Statistics
| Metric | Count |
|--------|-------|
| Vitec merge fields (`[[...]]`) | 3 (header only) |
| Insert fields (`data-label`) | ~54 |
| SVG checkboxes | 9 |
| `variant-brukt` divs | 12 |
| `variant-nytt` divs | 13 |
| vitec-if conditions | 0 |
| vitec-foreach loops | 0 |
| Page breaks | 1 (signature page) |
| Template size | 736 lines / ~42 KB |

## Bugs Fixed in This Version

### 1. Double Checkbox Rendering (was CRITICAL)
**Symptom:** Each checkbox showed two boxes — the native `<input type="checkbox">` plus the SVG span.
**Root cause:** CSS rule `[data-toggle="buttons"] input { display: none }` didn't match because labels used `data-toggle="button"` (singular) without a parent `data-toggle="buttons"` wrapper.
**Fix:** Added `label.btn input { display: none }` as catch-all, plus `data-toggle="buttons"` on all parent `<p>` elements (matches golden standard pattern). Reordered `<span>` before `<input>` inside labels.

### 2. Bullet Point Alignment (was COSMETIC)
**Symptom:** List bullets in section 8 alternative text appeared misaligned.
**Root cause:** `<ul>` had `margin-left: 0` with no `padding-left`.
**Fix:** Added `padding-left: 24px` to `#vitecTemplate ul`.

### 3. Variant Toggle-Hide (NEW FEATURE)
Added CSS `:has()` rules to hide irrelevant variant sections when Brukt or Nytt is selected at the top.

## Content NOT Included (Supplementary Material)

The Brukt source PDF (31 pages) contains 15 pages of "Tilleggstekster, alternative tekster, bilag og kommentarer" (pages 17–31). These are **not included** in the production template:

| Supplement | Content | Impact |
|------------|---------|--------|
| Punkt 4 | Alternative area table format | Low — niche use |
| Punkt 6/12/14 | Commentary on public law responsibilities | Reference only |
| **Punkt 7** | Extension clauses (Variant A: same terms, Variant B: market rent + arbitration) | **High** — commonly used |
| Punkt 10 | Detailed MVA commentary | Reference only |
| **Punkt 11** | 4 alternative security provisions (Depositum / Morselskap / Annet / Ingen) | **High** — commonly used |
| Punkt 18 | Self-insurer text | Low |
| Punkt 19 | Fire/destruction supplement (19.2-19.3) | Medium — already in Nytt variant |
| Punkt 21 | Public tenant note | Low |
| **Punkt 26** | Alternative control change clause (7 subsections) | Medium |
| **Punkt 27** | Environmental agreement (27.5-27.12 incl. Energibidrag) | Medium |
| **Punkt 29** | Extended human rights/sanctions text (29.1-29.8) | Medium |
| Punkt 33 | Solar panel provisions (2 alternatives) | Low |
| Punkt 35 | Arbitration text (voldgift) | Low |
| Punkt 38 | Physical signature text | Low |

**Recommendation:** Consider adding Punkt 7, 11, 26, 27, and 29 in a future iteration.

## Validation Results

### Encoding: PASS
All Norwegian characters use HTML entities (`&oslash;`, `&aring;`, `&aelig;`, `&sect;`, etc.). No literal UTF-8 characters in body text.

### Checkbox Pattern: PASS
SVG data URI checkboxes with `label.btn` + `span.svg-toggle.checkbox`. Native inputs hidden via CSS. Matches golden standard pattern.

### DOM Structure: PASS
- `#vitecTemplate` wrapper with `vitec-template="resource:Vitec Stilark"` reference
- Outer `<table><tbody><tr><td colspan="100">` wrapper
- `article.item` with CSS counter numbering
- No `proaktiv-theme` class

### Content Fidelity: PASS
~100% text match between source PDFs and production HTML. All 35 sections + bilag + signature present.

## Insert Fields Summary (~54 total)

Key fields brokers must fill in:
- `utleier`, `leietaker` (party names)
- `fødselsnr./org.nr.` (ID numbers, × 2)
- `adresse`, `gnr`, `bnr`, `fnr`, `snr`, `kommune`, `kommunenr` (property)
- `areal kvm` (total area)
- `virksomhet` (permitted use)
- `dato` (multiple — besiktigelse, overtakelse, leieperiode, signatur)
- `beløp` (multiple — rent, per-kvm rates, dagmulkt)
- `antall måneder`, `antall år`, `antall dager` (durations)
- `bilag nr` (multiple — appendix references)
- `måned`, `år` (index period)
- `tekst` (special provisions)
- `sted/dato` (Nytt variant signing location)
- `Utleiers repr.`, `Leietakers repr.` (signatory names)

## Analysis Files
- `.planning/phases/11-template-suite/LEIEAVTALE-ANALYSIS-REPORT.md`
