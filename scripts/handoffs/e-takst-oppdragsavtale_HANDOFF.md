# Handoff: E-takst oppdragsavtale

## Template Info

| Property | Value |
|----------|-------|
| **Name** | Bestilling av verdivurdering/E-takst |
| **Mode** | B (Word/HTM conversion) |
| **Tier** | T3 (Structured document) |
| **Source** | `E-takst oppdragsavtale.htm` (Word HTML export) |
| **Output** | `scripts/production/e-takst-oppdragsavtale_PRODUCTION.html` |
| **Size** | 33,468 chars |
| **Validation** | 52/52 PASS |

## Template Stats

| Metric | Count |
|--------|-------|
| Sections | 10 numbered + PEP form + Angreskjema |
| Merge fields | 26 |
| vitec-if conditions | 9 (6 unique expressions) |
| vitec-foreach loops | 3 (all on Model.selgere) |
| Insert fields | 9 |
| SVG checkboxes | 25 |
| Radio groups | 2 (PEP Ja/Nei, Angrerett) |
| Page break wrappers | 10 |
| Forced page breaks | 2 |

## Document Structure

### Page 1 (Main table)
1. **Eiendommen** — Address, matrikkel (merge fields), borettslag/andelsnr (conditional on eieform=="Andel")
2. **Eier/oppdragsgiver** — vitec-foreach on Model.selgere with name, ID, statsborgerskap (insert), address, tlf, email (tlf/email guarded with vitec-if)
3. **Oppdragstaker** — Company name + megler (merge fields)
4. **Oppdraget** — Legal text about E-takst (verbatim)

### Page 2 (continues main table)
5. **Formål og bakgrunn** — 12 standalone checkboxes in 2-column layout + 3 insert fields (purchase date, purchase price, last valuation) + 1 standalone checkbox
6. **Kundetiltak** — AML/KYC legal text (verbatim)
7. **Politisk eksponert person** — Ja/Nei radio group (rbl001)
8. **Vederlag** — Fee with insert field for amount
9. **Personvern** — Privacy text (verbatim)
10. **Angrerett** — Consumer-only (vitec-if idnummer.Length==12), legal text + førtidig oppstart radio (rbl002)
- **Signature block** — Sted (insert) + Dato (merge: dagensdato) + signing line

### Page 3 (separate table, always shown)
- **Egenerklæring PEP** — 8 + 5 + 3 standalone checkboxes, insert fields for relasjon/land/tidsperiode/signatur, 8-line writing area

### Page 4 (separate table, consumer-only)
- **Angreskjema** — Withdrawal form following golden standard pattern (seller/separator inline, sign-field)

## Conditional Logic

| Condition | Scope |
|-----------|-------|
| `Model.eiendom.eieform == "Andel"` | Borettslag + Andelsnr fields (Section 1) |
| `Model.selgere.Count > 0` | Owner loop guard (3 locations) |
| `Model.selgere.Count == 0` | Fallback "[Mangler eier/oppdragsgiver]" (3 locations) |
| `Model.selger.idnummer.ToString().Length == 12` | Angrerett section + Angreskjema (consumer-only) |
| `Model.selgere.Count == 1` / `> 1` | "Forbrukerens" vs "Forbrukernes" (Angreskjema) |

## Design Decisions

1. **Formål checkboxes** — Standalone (multi-select, no `<input>`), because a client can have multiple purposes for the valuation
2. **PEP form** — Always included (no conditional), the broker fills it when Section 7 = Ja
3. **Honorar/kjøpesum** — Insert fields (not merge fields), as the E-takst fee varies and historical purchase price isn't reliably in Vitec
4. **Matrikkel** — Uses `[[komplettmatrikkelutvidet]]` (single field) instead of separate gnr/bnr/snr/fnr foreach loop for simplicity
5. **Signature** — Single "Sign. oppdragsgiver" line (not foreach-looped), matching the source document's design

## Remaining Steps

- [ ] Upload to Vitec test system (proatest.qa.vitecnext.no)
- [ ] Testfletting with test property (Solåsveien 30)
- [ ] PDF inspect — verify page breaks, checkboxes, insert fields
- [ ] Commit to database
- [ ] Production deployment

## Content Verification Notes

All 13 sections verified against source document. Three minor punctuation fixes applied after content verification:
1. Personvern: "dato, iht." → "dato. iht." (matching source)
2. PEP: "fylles ut med" → "fylles ut. med" (matching source verbatim)
3. Angreskjema: Added missing "Sett kryss og dato:" label
