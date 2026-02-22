# Logic Mapping: E-takst oppdragsavtale

## Source

- **File:** `c:\Users\Adrian\Downloads\OneDrive_2026-02-21\maler vi må få produsert\E-takst oppdragsavtale.htm`
- **References used:** vitec-html-ruleset/03-conditional-logic.md, 10-property-conditionals.md, VITEC-IF-DEEP-ANALYSIS.md

## Summary

- **vitec-if conditions:** 4
- **vitec-foreach loops:** 2
- **Checkbox groups:** 4 (all broker-interactive)
- **Mutually exclusive sections:** 1 (Angrerett + Angreskjema — consumer-only)
- **"Mangler data" guards:** 5

---

## Conditional Branches

### Property-Type Conditionals

| # | Element | Condition | Scope | Notes |
|---|---------|-----------|-------|-------|
| 1 | div/p block | Model.eiendom.eieform == &quot;Andel&quot; | Borettslag + Andelsnr block (Section 1) | Show when property is borettslag/andel. Hide when Selveier (no Borettslag fields apply) |
| 2 | article/div | Model.selgere.Any(x =&gt; x.idnummer.ToString().Length == 12) | Section 10 (Angrerett) — entire block | Angrerett applies only to forbrukere (consumers). Per oppdragsavtale golden standard: idnummer Length 12 = forbruker. Hide when all selgere are businesses (Length 11) or empty |
| 3 | div/table | Model.selgere.Any(x =&gt; x.idnummer.ToString().Length == 12) | Angreskjema (vedlegg) | Same as #2 — withdrawal form only for consumers |

**Note on idnummer lengths:** Golden standard oppdragsavtale uses `Model.selger.idnummer.ToString().Length == 12` for Angrerett visibility. E-takst has `Model.selgere` (plural); use `.Any()` to show when at least one oppdragsgiver is consumer.

### Optional Field Guards (Section 1 — Eiendommen)

Section 1 Borettslag/Andelsnr: When eieform != "Andel", the Borettslag and Andelsnr fields do not apply. Wrap the entire Borettslag+Andelsnr block in vitec-if.

**Unresolved:** Verify eieform values for E-takst/verdivurdering context. Standard Vitec values: Andel, Selveier, Sameie, Aksje, Obligasjonsleilighet, Eierseksjon.

---

## Optional Field Guards

| # | Element | Condition | Content When True | Content When False |
|---|---------|-----------|-------------------|-------------------|
| 1 | span | Model.ansvarligmegler.navn != &quot;&quot; &amp;&amp; Model.ansvarligmegler.navn != &quot;Mangler data&quot; | Show ansvarlig megler if different from operativmegler | (hide) |
| 2 | span | Model.megler2.navn != &quot;&quot; &amp;&amp; Model.megler2.navn != &quot;Mangler data&quot; | Medhjelper paragraph | (hide) |

**Note:** Section 3 (Oppdragstaker) has Selskap + Megler. If Proaktiv uses ansvarligmegler/operativmegler pattern like oppdragsavtale, apply same dual-megler conditional. Field Mapper will confirm exact field paths.

---

## Alternative Sections (Mutually Exclusive)

| Group | Option | Condition | Location |
|-------|--------|-----------|----------|
| Angrerett applicability | Show Section 10 + Angreskjema | Model.selgere.Any(x =&gt; x.idnummer.ToString().Length == 12) | Section 10, Angreskjema vedlegg |
| Angrerett applicability | Hide both | !Model.selgere.Any(...) or Model.selgere.Count == 0 | — |

---

## Checkbox State Logic

### Data-Driven Checkboxes

**None.** This template has no data-driven checkboxes. All checkboxes are broker-interactive.

### Broker-Interactive Checkboxes

| # | Location | Label Text | Notes |
|---|----------|------------|-------|
| 1 | Section 5 (left table) | Salg av eiendommen | Formål — pick one from 7 |
| 2 | Section 5 (left table) | Refinansiering i eksisterende bank | |
| 3 | Section 5 (left table) | Bytte bank | |
| 4 | Section 5 (left table) | Oppta boligkreditt | |
| 5 | Section 5 (left table) | Oppta lån til oppussing | |
| 6 | Section 5 (left table) | Oppta lån for kjøp av fritidseiendom | |
| 7 | Section 5 (left table) | Oppta lån for kjøp av sekundærbolig (utleiebolig) | |
| 8 | Section 5 (right table) | Stille bolig som sikkerhet for tredjemanns lån (realkausjon) | Formål — pick one from 6 |
| 9 | Section 5 (right table) | Vil bare vite hva boligen er verdt | |
| 10 | Section 5 (right table) | Arveoppgjør/forskudd på arv | |
| 11 | Section 5 (right table) | Samlivsbrudd | |
| 12 | Section 5 (right table) | Refinansiere annen gjeld (privat gjeld el.l.) | |
| 13 | Section 5 (inline) | Eiendommen er ikke verdivurdert siden den ble kjøpt | Standalone checkbox |
| 14 | Section 7 | Ja | PEP question — mutually exclusive with Nei |
| 15 | Section 7 | Nei | PEP question — mutually exclusive with Ja |
| 16 | Section 10 | Jeg ønsker at eiendomsmeglingsforetaket skal sette i gang arbeidet... | Førtidig oppstart — mutually exclusive with #17 |
| 17 | Section 10 | Jeg ønsker IKKE at eiendomsmeglingsforetaket skal sette i gang arbeidet... | No early start — mutually exclusive with #16 |
| 18–33 | Section 11 (PEP form) | 16+ Symbol ð checklist items | PEP declaration — user marks applicable categories (multi-select within groups) |

**Radio groups:** Formål (items 1–12) = one selection across both tables. Section 7 Ja/Nei = one selection. Section 10 (items 16–17) = one selection.

---

## Loop Specifications

| # | Collection | Variable | Guard Condition | Fallback Text | Used In |
|---|-----------|----------|-----------------|---------------|---------|
| 1 | Model.selgere | selger | Model.selgere.Count &gt; 0 | [Mangler eier/oppdragsgiver] | Section 2 (Eier/oppdragsgiver) — two owner slots |
| 2 | Model.selgere | selger | Model.selgere.Count &gt; 0 | (signature block uses single signer) | Signature block — use first selger or primary |

**Note:** Source has exactly 2 owner slots. Use `vitec-foreach="selger in Model.selgere"` — with Count 1 renders 1 block, Count 2 renders 2. No need for second-slot conditional; foreach handles it. If Model has only one selger, one block renders; second slot area may need explicit handling for empty state when Count == 1. Structure Analyzer notes single "Sign. oppdragsgiver" line — signature does not repeat per owner.

---

## "Mangler Data" Guard List

Fields that should be hidden (not just empty) when Vitec returns "Mangler data":

| Field Path | Guard Expression | Element to Hide |
|------------|------------------|-----------------|
| eiendom.adresse | != &quot;&quot; &amp;&amp; != &quot;Mangler data&quot; | Address paragraph (show fallback or insert field) |
| selger.navn | != &quot;&quot; &amp;&amp; != &quot;Mangler data&quot; | Owner block — use fallback per loop |
| selger.tlf / selger.mobil | != &quot;&quot; &amp;&amp; != &quot;Mangler data&quot; | Mobil line |
| selger.emailadresse | != &quot;&quot; &amp;&amp; != &quot;Mangler data&quot; | E-post line |
| megler.navn (or operativmegler) | != &quot;&quot; &amp;&amp; != &quot;Mangler data&quot; | Megler line in Section 3 |

**Note:** Double-guard pattern per VITEC-IF-DEEP-ANALYSIS. Field Mapper will confirm exact paths.

---

## Insert Fields (Broker Fill-In)

| Location | Label | Notes |
|----------|-------|-------|
| Section 2 | Statsborgerskap | Per owner; underlined blank |
| Section 5 | Når ble eiendommen kjøpt? | Free text |
| Section 5 | Hva var kjøpesummen? | Free text |
| Section 5 | Når ble forrige verdivurdering foretatt? Oppgi årstall | Free text |
| Section 8 | kr. _______,- | Honorar amount |
| Section 10/11 | Sted | Signature location |
| Section 10/11 | Dato | Signature date |
| Section 11 | Relasjon til navn | PEP form |
| Section 11 | Land/organisasjon/verv | PEP form |
| Section 11 | Tidsperiode | PEP form |
| Section 11 | Signatur oppdragsgiver | PEP form |
| Section 11 | Beskrivelse av feil, mangler | Multi-line |
| Angreskjema | Avtalen ble inngått den (dato) | |
| Angreskjema | Forbrukerens navn og adresse | |
| Angreskjema | Dato | |
| Angreskjema | Underskrift | |

---

## Condition Expression Syntax Reference

All conditions use Model notation. Builder handles HTML escaping:

- `"` → `&quot;`
- `>` → `&gt;`
- `<` → `&lt;`
- `&&` → `&amp;&amp;`
- `=>` (lambda) → `=&gt;`
- Norwegian chars: `\xF8` (ø), `\xE5` (å), `\xE6` (æ)

---

## Unresolved Logic (NEED REVIEW)

| # | Location | Intent | Why Unresolved |
|---|----------|--------|----------------|
| 1 | Section 1 | Borettslag/Andelsnr visibility | E-takst is verdivurdering — eiendom.eieform may differ from salgsoppdrag. Confirm eieform values for valuation context |
| 2 | Section 11 (PEP form) | Conditional inclusion when Section 7 = Ja | No Model field for PEP answer; broker selects Ja/Nei interactively. Options: (A) Always include PEP form; (B) Add custom field (e.g. Model.oppdrag.pepSvar) for conditional inclusion; (C) Two template variants |
| 3 | idnummer Length 12 vs 11 | Which = forbruker? | Oppdragsavtale golden standard uses Length == 12 for Angrerett. If E-takst/Proaktiv uses different idnummer format, condition may need adjustment |
| 4 | Section 3 | ansvarligmegler vs operativmegler | Proaktiv may use different broker model; Field Mapper will confirm. If single megler only, no conditional needed |

---

## PEP Form (Egenerklæring) — Visibility

Section 11 "Egenerklæring Politisk Eksponert Person" is a full-page form. Source instructs: "Hvis «Ja», må skjema på s. 3 fylles ut." 

**Recommendation:** Always include the PEP form in the template. The broker/oppdragsgiver fills it when they answered Ja to the PEP question in Section 7. No vitec-if for PEP form visibility unless a field is added. Flag for builder: if Vitec/Proaktiv provides a PEP-answer field, wrap the PEP form page in vitec-if.
