# Handoff: Kjøpekontrakt prosjekt (leilighet)

## Spec
- **Mode:** B (Convert/Migrate)
- **Tier:** T4 (Complex contract)
- **Template:** Kjøpekontrakt prosjekt (leilighet med delinnbetalinger)

## Production File
- **Path:** `scripts/converted_html/Kjopekontrakt_prosjekt_leilighet_PRODUCTION.html`
- **Size:** 50,812 chars
- **Build script:** `scripts/build_kjopekontrakt_prosjekt_leilighet.py`

## Template Stats
- Sections: 21 (including 1A/1B ownership form alternatives)
- Merge fields: 44 — `dagensdato`, `eiendom.fellesutgifter`, `eiendom.heftelserogrettigheter`, `eiendom.kommunenavn`, `eiendom.leilighetsnr`, `kjoper.emailadresse`, `kjoper.fdato_orgnr`, `kjoper.fullmektig.navn`, `kjoper.gatenavnognr`, `kjoper.ledetekst_fdato_orgnr`, `kjoper.navn`, `kjoper.navnutenfullmektigogkontaktperson`, `kjoper.postnr`, `kjoper.poststed`, `kjoper.tlf`, `kontrakt.formidling.nr`, `kontrakt.kid`, `kontrakt.kjopesum`, `kontrakt.kjopesumibokstaver`, `kontrakt.kjopesumogomkostn`, `kontrakt.klientkonto`, `kontrakt.overtagelse.dato`, `kontrakt.totaleomkostninger`, `meglerkontor.navn`, `meglerkontor.orgnr`, `meglerkontor.poststed`, `oppdrag.nr`, `oppdrag.prosjekt.antallenheter`, `oppgjor.besoksadresse`, `oppgjor.besokspostnr`, `oppgjor.besokspoststed`, `oppgjor.kontorepost`, `oppgjor.kontornavn`, `oppgjor.kontortlf`, `selger.emailadresse`, `selger.fdato_orgnr`, `selger.fullmektig.navn`, `selger.gatenavnognr`, `selger.ledetekst_fdato_orgnr`, `selger.navn`, `selger.navnutenfullmektigogkontaktperson`, `selger.postnr`, `selger.poststed`, `selger.tlf`
- vitec-if conditions: 53
- vitec-foreach loops: 4 — `selger in Model.selgere` (roles table), `kjoper in Model.kjopere` (roles table), `selger in Model.selgere` (signature), `kjoper in Model.kjopere` (signature)
- Insert fields: 30
- SVG checkboxes: ~50 instances (conditional auto-check + static unchecked)

## Validation Result
- Validator: `validate_vitec_template.py --tier 4`
- Result: **51/51 PASS, 0 FAIL**

```
============================================================
VITEC TEMPLATE VALIDATION REPORT
============================================================
Template: Kjopekontrakt_prosjekt_leilighet_PRODUCTION.html
Size: 50,788 chars
Tier: T4
============================================================

  [+] PASS: [A] vitecTemplate wrapper div
  [+] PASS: [A] No proaktiv-theme class (not used by reference templates)
  [+] PASS: [A] Stilark resource span
  [+] PASS: [A] Stilark span contains &nbsp;
  [+] PASS: [A] Outer table body wrapper
  [+] PASS: [A] H1 title element
  [+] PASS: [A] H1 CSS styling in style block
  [+] PASS: [A] H2 CSS styling with negative margin
  [+] PASS: [B] No CSS flexbox/grid
  [+] PASS: [B] No orphan <tr> outside tbody/thead
  [+] PASS: [B] Uses 100-unit colspan system
  [+] PASS: [C] No inline font-family
  [+] PASS: [C] No inline font-size
  [+] PASS: [D] Merge fields use [[field]] syntax
  [+] PASS: [D] No spaces inside brackets
  [+] PASS: [D] No legacy #field.context¤ syntax
  [+] PASS: [E] Has vitec-if conditions
  [+] PASS: [E] String comparisons use &quot;
  [+] PASS: [E] Greater-than uses &gt;
  [+] PASS: [F] Has vitec-foreach loops
  [+] PASS: [F] Foreach on <tbody> elements
  [+] PASS: [F] Guard for Model.selgere
  [+] PASS: [F] Guard for Model.kjopere
  [+] PASS: [F] Guard for Model.selgere
  [+] PASS: [F] Guard for Model.kjopere
  [+] PASS: [F] Fallback for empty Model.selgere
  [+] PASS: [F] Fallback for empty Model.kjopere
  [+] PASS: [F] Fallback for empty Model.selgere
  [+] PASS: [F] Fallback for empty Model.kjopere
  [+] PASS: [G] No image tags (contract templates)
  [+] PASS: [H] Has insert field placeholders
  [+] PASS: [H] Insert fields have data-label attributes
  [+] PASS: [H] Insert fields use insert-table wrapper
  [+] PASS: [H] No Unicode checkboxes (render as ? in PDF)
  [+] PASS: [H] SVG checkbox CSS present
  [+] PASS: [I] No <font> tags
  [+] PASS: [I] No <center> tags
  [+] PASS: [I] Norwegian chars are HTML entities (not literal UTF-8)
  [+] PASS: [I] HTML entities present for Norwegian characters
  [+] PASS: [J] Uses <article class='item'>
  [+] PASS: [J] CSS counters present
  [+] PASS: [J] Dual counter pattern (section/subsection)
  [+] PASS: [J] H2 in top-level articles
  [+] PASS: [J] roles-table class present
  [+] PASS: [J] Signature block with border-bottom
  [+] PASS: [J] avoid-page-break class
  [+] PASS: [J] Monetary fields use $.UD() wrapper
  [+] PASS: [K] Well-formed HTML (basic check)
  [+] PASS: [K] No onclick/onload handlers
  [+] PASS: [K] No external stylesheet links
  [+] PASS: [K] No JavaScript

============================================================
RESULTS: 51/51 passed, 0 failed
============================================================
```

## Fixes Applied

| # | Fix | Summary |
|---|-----|---------|
| 1 | Entity Encoding (CRITICAL) | Added `encode_entities()` post-processing step that converts all literal Norwegian chars (ø,å,æ,Ø,Å,Æ,§,«,»,–,—,é) to HTML entities. Applied as final step after template assembly. |
| 2 | SVG Checkboxes (CRITICAL) | Replaced all ~50 Unicode checkbox characters (&#9744;/&#9745;) with SVG `label.btn` + `span.checkbox.svg-toggle` pattern. Added full SVG checkbox CSS block to `<style>`. Conditional checkboxes use dual `vitec-if` wrappers (Approach A). |
| 3 | Remove proaktiv-theme (IMPORTANT) | Changed `<div class="proaktiv-theme" id="vitecTemplate">` to `<div id="vitecTemplate">`. |
| 4 | Title h5→h1 (IMPORTANT) | Changed `<h5 style="text-align:center;">KJØPEKONTRAKT</h5>` to `<h1>Kjøpekontrakt</h1>`. CSS handles centering via `#vitecTemplate h1 { text-align: center; }`. |
| 5 | Outer table wrapper (IMPORTANT) | Wrapped entire body content in `<table><tbody><tr><td colspan="100">` structure with right-aligned `<small>` header info row containing `meglerkontor.orgnr`, `oppdrag.nr`, `kontrakt.formidling.nr`. |
| 6 | Complete CSS (IMPORTANT) | Added heading styles (h1 14pt centered, h2 11pt with -20px margin, h3 10pt), table base (`width:100%; table-layout:fixed`), `.borders`, `ul`/`li` list styles, `a.bookmark`, `.liste .separator`, insert field CSS with `data-label` + `insert-table`, and full SVG checkbox CSS block. |
| 7 | Insert field pattern (IMPORTANT) | Updated all `<span class="insert">&nbsp;</span>` to `<span class="insert-table"><span class="insert" data-label="..."></span></span>` with appropriate labels: "dato", "beløp", "tekst", "gnr", "bnr", "heftelser". |
| 8 | $.UD() on monetary fields (IMPORTANT) | Wrapped `[[kontrakt.totaleomkostninger]]` and `[[kontrakt.kjopesumogomkostn]]` and `[[eiendom.fellesutgifter]]` in `$.UD()`. `[[kontrakt.kjopesum]]` was already wrapped. |
| 9 | Guillemets (IMPORTANT) | Replaced all `&ldquo;`/`&rdquo;` with `«`/`»` (entity-encoded to `&laquo;`/`&raquo;` by post-processing). |
| 10 | Signature block (IMPORTANT) | Fixed colspan from 40 to 45, added conditional plural (`Selger<span vitec-if>e</span>`), replaced manual date with `[[dagensdato]]`, added `[[meglerkontor.poststed]]` location, implemented `vitec-foreach` loops for multi-party signatures matching reference pattern. |
| 11 | Payment model (CONTENT) | **CORRECTED**: Replaced enebolig "For tomten"/"For boligen" with selveier "Alternativ 1: Forskudd" / "Alternativ 2: Hele kjøpesummen" from source. |
|| 15 | Sec 2 payment table (CONTENT) | Replaced enebolig multi-installment table with selveier model (10% ved kontraktsinngåelse + Sluttoppgjør). |
|| 16 | Sec 3 garanti (CONTENT) | Added 3 missing paragraphs: §12 forbehold, §12 withholding right, §47 forskuddsgaranti. |
|| 17 | Sec 6 tinglysing (CONTENT) | "vederlaget for tomten i henhold til punkt 2" → "fullt oppgjør"; "eiendomsmegler" → "megler". |
|| 18 | Sec 8 endringsarbeider (CONTENT) | "garantier" → "forskuddsgaranti" + missing Utbygger påslag sentence. |
| 12 | Kjøper fullmektig (VISUAL) | Added `<p vitec-if="Model.kjoper.fullmektig.navn != &quot;&quot;">Kjøper er representert ved fullmektig [[kjoper.fullmektig.navn]]</p>` after kjøper roles table. |
| 13 | Complete heading CSS (VISUAL) | Included in Fix 6 — full heading hierarchy (h1/h2/h3) matching bruktbolig reference. Removed `>` direct child selector from counter CSS. |
| 14 | Roles table headers (VISUAL) | Changed "Adresse" column header to "Adresse/Kontaktinfo", added `rowspan="2"` on name and fdato cells so contact info aligns under address column. |
| Extra | Collection fallbacks (Rule 1) | Added `[Mangler selger]` and `[Mangler kjøper]` fallback blocks for empty collection guard compliance. |

## Potential Issues & Uncertainties

- **Fix 11 — Payment model: RESOLVED.** Verified against both the `.htm` source (`Kjøpekontrakt prosjekt selveier.htm`) and DOCX (`Kjøpekontrakt Prosjekt selveier .docx`). The selveier source uses "Alternativ 1: Forskudd" / "Alternativ 2: Hele kjøpesummen" in Section 4 (Oppgjør), NOT the enebolig's "For tomten"/"For boligen" model. The prior builder had confused the enebolig source with the selveier source. Now corrected with Fixes 11, 15-18.
- **§47/§12 guarantee provisions: RESOLVED.** Added §12 forbehold, §12 withholding right, and §47 forskuddsgaranti paragraphs to Section 3 (Garanti), matching the selveier source exactly.
- **`[[kontrakt.klientkonto]]` + `[[kontrakt.kid]]` vs `[[kontrakt.klientkontoogkid]]`:** The template uses separate fields. The bruktbolig reference uses the combined `[[kontrakt.klientkontoogkid]]` field. The separate fields were kept as-is from the existing template; verify which format the Vitec API expects.
- **`[[oppgjor.besoksadresse]]` vs `[[oppgjor.postadresse]]`:** The bruktbolig reference uses `[[oppgjor.postadresse]]`. Our template uses `[[oppgjor.besoksadresse]]`. Kept as-is; verify against the field registry which is correct for this contract type.
- **`[[selger.navn]]` in signature block:** The foreach-based signature uses `[[*selger.navn]]` and `[[*kjoper.navn]]` for signing lines. Verify these field paths are correct (vs. `navnutenfullmektigogkontaktperson` which is used in roles tables).

## Content Notes
- Legal text verified against both `.htm` source (`Kjøpekontrakt prosjekt selveier.htm`) and DOCX (`Kjøpekontrakt Prosjekt selveier .docx`)
- Section 1A (selveiet) and 1B (eierseksjon/sameie) are conditional alternatives based on `Model.eiendom.eieform`
- Section 2 (Kjøpesum) uses 10% deposit + sluttoppgjør model (selveier), not delinnbetalinger (enebolig)
- Section 3 (Garanti) includes full §12 + §47 provisions
- Section 4 (Oppgjør) uses "Alternativ 1: Forskudd" / "Alternativ 2: Full payment" model (selveier)
- Section 9 (Overtakelse) uses conditional date/expected date alternatives based on `Model.kontrakt.overtagelse.dato != "Mangler data"`
- Section 15 (Forbehold) has 3 conditional project forbehold (salgsgrad, igangsettelse, byggelån) + 1 static
- Guillemets «» are used consistently for Norwegian legal quote marks

## Known Limitations
- SVG checkbox CSS uses the simplified PIPELINE-DESIGN pattern (URL-encoded data URIs) rather than the bruktbolig reference's more verbose CSS. Both produce identical visual results.
- The `insert-table` + `data-label` pattern shows placeholder text in CKEditor but not in PDF output — this is expected behavior.
- The template cannot be fully tested without a property that has all conditional branches (selveiet + eierseksjon, bolig + fritid, etc.)
- The signature foreach pattern creates one signing line per party; in CKEditor, the `data-toggle="button"` behavior for checkboxes may differ slightly from static HTML rendering.

## Recommendations
- ~~**Priority 1:** Human review of Fix 11~~ **DONE** — Payment model corrected to selveier "Alternativ 1/2". Verified against both .htm and DOCX sources.
- **Priority 1:** Verify field paths `kontrakt.klientkonto`/`kontrakt.kid` vs `kontrakt.klientkontoogkid` and `oppgjor.besoksadresse` vs `oppgjor.postadresse` against the Vitec API.
- **Priority 2:** Run live verification (Testfletting) with test property Solåsveien 30 to confirm PDF rendering of SVG checkboxes and entity-encoded text.
- **Suggested test properties:** Use a property with `eieform == "Eierseksjon"` to test Section 1B, and a property with `kontrakt.overtagelse.dato` set to verify Section 9 alternatives.
