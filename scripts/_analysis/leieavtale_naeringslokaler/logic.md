# Logic Mapping: Leieavtale Næringslokaler (Brukt vs Nye)

## Source

- **File 1 (Brukt):** `scripts/source_html/leieavtale_naeringslokaler_brukt.html`
- **File 2 (Nye):** `scripts/source_html/leieavtale_naeringslokaler_nye.html`
- **References used:** vitec-html-ruleset/03-conditional-logic.md, 10-property-conditionals.md, VITEC-IF-DEEP-ANALYSIS.md

## Summary

- **vitec-if conditions:** ~12+ (Brukt vs Nye branching)
- **vitec-foreach loops:** TBD by Field Mapper (utleier, leietaker, etc.)
- **Checkbox groups:** 0 (document uses "stryk det som ikke passer" cross-out pattern)
- **Mutually exclusive sections:** 2 (Brukt variant vs Nye variant; MERVERDIAVGIFT A vs B)
- **"Mangler data" guards:** TBD by Field Mapper

---

## Master Condition: Brukt vs Nye

The two source documents are variants of the same standard commercial lease agreement:

| Variant | Norwegian | Scope |
|---------|-----------|-------|
| **Brukt** | Brukte/"som de er" lokaler | Used/as-is premises |
| **Nye** | Nye/Rehabiliterte lokaler | New/rehabilitated premises |

**Recommendation — Master condition:** No standard Vitec field exists for this distinction. Commercial lease agreements (næringsleie) are not part of Vitec's standard real estate transaction model (which targets boligkjøp, oppdrag, etc.).

**Proposed approach:** Use a **broker-interactive toggle checkbox** at the document top (e.g. "Brukte lokaler" vs "Nye/rehabiliterte lokaler"). The broker selects which variant applies before generating the document. Implement as:

- **Option A:** CKEditor toggle / custom field in Proaktiv Dokument Hub (e.g. `Model.leieavtale.lokaletype == "brukt"` vs `"nye"`)
- **Option B:** Two separate template records in the library, with the broker choosing which template to use

If a custom field is added to the system, the condition would be:

- Brukt: `Model.leieavtale.lokaletype == &quot;Brukt&quot;` (or equivalent)
- Nye: `Model.leieavtale.lokaletype == &quot;Nye&quot;`

---

## Conditional Branches (Brukt vs Nye)

### Property-Type Conditionals (Document-Level)

| # | Element | Condition | Scope | Notes |
|---|---------|-----------|-------|-------|
| 1 | p | Brukt | Document title | "STANDARD LEIEAVTALE FOR NÆRINGSLOKALER (BRUKTE/"SOM DE ER" LOKALER)" |
| 2 | p | Nye | Document title | "STANDARD LEIEAVTALE FOR NÆRINGSLOKALER (NYE/REHABILITERTE LOKALER LOKALER)" — note duplicate "LOKALER" in source |
| 3 | h2 | Brukt | Section 4 (Leieobjektet) | "Eksklusivt Areal **og** arealfordeling" + "Før Overtakelse skal Utleier utføre arbeider/endringer i Leieobjektet som angitt i **Bilag [ ]**" |
| 4 | h2 | Nye | Section 4 (Leieobjektet) | "Eksklusivt Areal**,** og arealfordeling" + "Leieobjektet skal være i henhold til avtalt **kravspesifikasjon, Bilag 3**" |
| 5 | h2 | Brukt | Section 6 (Overtakelse) | "Leieobjektet **overtas ryddet og rengjort, og for øvrig i den stand som Leieobjektet var i ved Leietakers besiktigelse, og med arbeider/endringer som beskrevet i Bilag [ ]**" |
| 6 | h2 | Nye | Section 6 (Overtakelse) | "Leieobjektet **overtas i henhold til punkt 4.1 ovenfor**" |
| 7 | p | Brukt | Bilag list | Includes "Bilag [ ]: [Arbeider som Utleier skal utføre i Leieobjektet før Overtakelse]" |
| 8 | p | Nye | Bilag list | Includes "Bilag 3: Kravspesifikasjon"; does NOT include the "Arbeider" bilag |
| 9 | h2 | Brukt | Section 12 (miljøsertifisering) | "miljøsertifisering**.**" (no extension) |
| 10 | h2 | Nye | Section 12 (miljøsertifisering) | "miljøsertifisering **slik de til enhver tid gjelder**." |
| 11 | p | Minor | Section 4 | NS 3940: "2023+AC:2024" (Brukt) vs "2023+AC:2024" (Nye, space after colon) |

### Section 11 (Sikkerhetsstillelse)

Content is **nearly identical** in both variants. Brukt has additional anchor IDs on guarantee paragraphs (`_Hlk87864717`, `_Hlk89959455`, etc.); substantive text matches. No distinct "2 extra paragraphs" were found in the current source — if the diff analysis referred to alternative bestemmelser in the appendix, those are broker-selectable (see Alternative Sections).

### Section 13 (Utleiers adgang til Eksklusivt Areal)

Both variants include the miljøtiltak access paragraph: "Leietaker plikter også å gi Utleier adgang til Eksklusivt Areal for gjennomføring av miljøtiltak, herunder for undersøkelse/måling av energiforbruk mv." Differences are cosmetic only (e.g. `<em> </em>` in Brukt).

### Section Structure (H1 Headings)

| Brukt | Nye |
|------|-----|
| Has separate **MERVERDIAVGIFT** as H1 | MERVERDIAVGIFT content may be merged under LEIEREGULERING or adjacent section |
| "Kontrollskifte, Fusjon og fisjon" (mixed case) | "KONTROLLSKIFTE, FUSJON OG FISJON" |
| "Miljø og sirkulære løsninger **mv.**" | "Miljø og sirkulære løsninger" |
| Appendix INNHOLD includes "**Alternativ tekst der Leietaker skal ha ansvaret for offentligrettslige krav per Overtakelse**" | Appendix INNHOLD does not include this line |

---

## "[Stryk de alternativene som ikke passer]" Sections

Broker-interactive choice points where the broker crosses out the option that does not apply. **One explicit occurrence** found in the main body.

| # | Location | Options | Notes |
|---|----------|---------|-------|
| 1 | MERVERDIAVGIFT (punkt 10) | **A:** hele Leieobjektet skal omfattes av Utleiers frivillige registrering i Merverdiavgiftsregisteret<br>**B:** deler av Leieobjektet skal omfattes | Broker crosses out A or B; no checkbox/radio in source |

**Recommendation:** Implement as mutually exclusive `vitec-if` blocks driven by a field (e.g. `Model.leieavtale.mva_dekning == "hele"` vs `"deler"`) or broker-interactive toggle in the editor.

---

## Alternative Sections (Appendix / Tilleggstekster)

Located in **TILLEGGSTEKSTER/ALTERNATIVE TEKSTER/BILAG/KOMMENTARER** at end of document. These are **optional clauses** that the broker may insert by replacing/main text. They should **NOT** appear in the main template body by default — they are reference alternatives.

| Point | Title | Intent |
|-------|-------|--------|
| 4 | Alternativ tekst – arealtabell; Alternativ tekst om parkeringsplasser | Broker may substitute alternative wording |
| 6, 12, 14 | Kommentarer til ansvaret for offentligrettslige krav | Brukt only: "Alternativ tekst der Leietaker skal ha ansvaret for offentligrettslige krav per Overtakelse" |
| 7 | Tilleggstekst til forlengelsesklausuler | Optional extension clause text |
| 10 | Kommentarer til merverdiavgiftsbestemmelsen | Commentary |
| 11 | Alternative bestemmelser om sikkerhetsstillelse; Forslag til garantitekst for morselskapsgaranti | Broker may use morselskapsgaranti instead of bank guarantee |
| 15 | Forslag til tekst til bilag om Felleskostnader; Alternativ regulering om ansvarsmatrise | Alternative Felleskostnader / ansvarsmatrise |
| 19 | Tilleggstekst hvis Leietaker er selvassurandør | Insurance clause variant |
| 20 | Tilleggstekst om brann og destruksjon | Fire/destruction clause variant |
| 22 | Offentlige leietakere og tvangsfullbyrdelse | Public lessee clause |
| 27 | Alternativ bestemmelse vedrørende kontrollskifte | Control change clause |
| 28 | Tilleggstekst (miljøtiltak) | Environment/energy clause (long block) |
| 30 | Alternativ utvidet tekst (menneskerettigheter, sanksjonslister) | Extended CSR/sanctions clause |
| 34 | Alternativ A/B: Solcelleanlegg | **A:** Utleier har rett til å etablere; **B:** Utleier har etablert [skal etablere] |
| 36 | Forslag til kontraktstekst for voldgiftsbehandling | Arbitration clause |
| 38 | Forslag til kontraktstekst for fysisk signatur | Physical signing clause |

**Alternativ A/B patterns (PUNKT 34):** Mutually exclusive. Condition TBD — likely broker choice (no Vitec field for solcelle).

---

## Commentary Sections

| Section | Intent |
|---------|--------|
| **TILLEGGSTEKSTER...** block | Editorial guidance; must be clearly separated from main contract or excluded from final PDF |
| **INNHOLD** (table of contents) | Index of alternative clauses; for broker reference only |
| **Kommentarer** (e.g. Punkt 6, 12, 14) | Legal commentary — do not render in customer-facing output |

---

## Checkbox Patterns

**None identified.** The source uses:
- "[Stryk de alternativene som ikke passer]" with **A** / **B** options (cross-out)
- No `<input type="checkbox">` or `type="radio"`
- No `class="checkbox svg-toggle"` or `data-toggle="button"` patterns

If the builder adds checkbox UX for broker choices, those would be **broker-interactive** (user confirmation), not data-driven.

---

## Bilag List Differences

| Bilag | Brukt | Nye |
|-------|-------|-----|
| 1 | Firmaattest/legitimasjon | Same |
| 2 | Tegninger (arealoversikt) | Tegninger; Section 4 also references "Bilag 3" |
| 3 | — | **Kravspesifikasjon** |
| [ ] | **Arbeider som Utleier skal utføre i Leieobjektet før Overtakelse** | — |
| [ ] | Særregulering for parkeringsplasser | Same |
| [ ] | Skjema for overtakelsesprotokoll | Same |
| [ ] | Eksempler på Felleskostnadene | Same |
| [ ] | mva.-registrering | Same |
| [ ] | Særskilt avtalt sikkerhetsstillelse | Same |
| [ ] | Miljøavtale | Same |
| [ ] | Databehandleravtale | Same |
| [ ] | Samordningsavtale for brannforebygging | Same |

The merged template must branch the Bilag list based on Brukt vs Nye: show "Arbeider..." for Brukt, "Kravspesifikasjon" (Bilag 3) for Nye.

---

## Unresolved Logic (NEED REVIEW)

| # | Location | Intent | Why Unresolved |
|---|----------|--------|----------------|
| 1 | Master condition | Brukt vs Nye branching | No Vitec field; recommend broker toggle or custom field |
| 2 | MERVERDIAVGIFT A/B | Hele vs deler av Leieobjektet mva | No obvious Model field; likely broker choice or custom `leieavtale.mva_dekning` |
| 3 | PUNKT 34 Solcelle | Alternativ A vs B | Broker choice; no Vitec field |
| 4 | Appendix alternatives | Which clauses are included | Each is broker-selected; may need CKEditor "include optional clause" UI |

---

## Condition Expression Syntax Reference

All conditions use MODEL notation. When implementing in HTML:
- `"` in values → `&quot;`
- `>` in comparisons → `&gt;`
- `<` in comparisons → `&lt;`
- `&&` (AND) → `&amp;&amp;`
- Norwegian chars: `\xF8` (ø), `\xE5` (å), `\xE6` (æ)

---

## Proposed vitec-if Conditions (Where Determined)

| Location | Condition | Notes |
|----------|-----------|-------|
| Title (Brukt) | `Model.leieavtale.lokaletype == &quot;Brukt&quot;` | **NEED REVIEW** — custom field |
| Title (Nye) | `Model.leieavtale.lokaletype == &quot;Nye&quot;` | Inverse of above |
| Section 4 Leieobjektet (Brukt) | Same as title | "Før Overtakelse..." + "Bilag [ ]" |
| Section 4 Leieobjektet (Nye) | Same as title | "kravspesifikasjon, Bilag 3" |
| Section 6 Overtakelse (Brukt) | Same as title | "overtas ryddet og rengjort..." |
| Section 6 Overtakelse (Nye) | Same as title | "overtas i henhold til punkt 4.1" |
| Bilag list (Brukt) | Same as title | Include "Arbeider som Utleier skal utføre..." |
| Bilag list (Nye) | Same as title | Include "Bilag 3: Kravspesifikasjon" |
| MERVERDIAVGIFT A | `Model.leieavtale.mva_dekning == &quot;hele&quot;` | **NEED REVIEW** |
| MERVERDIAVGIFT B | `Model.leieavtale.mva_dekning == &quot;deler&quot;` | **NEED REVIEW** |
