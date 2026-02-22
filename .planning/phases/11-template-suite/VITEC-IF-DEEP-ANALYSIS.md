# Vitec-If Deep Analysis: Golden Standard Pattern Catalog

> **Sources analyzed:**
> 1. `kjøpekontrakt bruktbolig html.html` — 173 vitec-if conditions (bruktbolig reference)
> 2. `kjøpekontrakt forbruker.html` — 151 vitec-if conditions (forbruker reference)
> 3. `oppdragsavtale.html` — 42 vitec-if conditions (oppdragsavtale reference)
>
> **Total: 366 vitec-if conditions analyzed**

---

## 1. Condition Pattern Taxonomy

### Pattern A: Enum Comparison (most common)

Used for property type branching. Single value or grouped with `||`.

```html
<!-- Single value -->
<span vitec-if="Model.eiendom.eieform == &quot;Selveier&quot;">skjøte</span>
<span vitec-if="Model.eiendom.eieform == &quot;Andel&quot;">hjemmelsoverføring</span>

<!-- Grouped OR -->
<span vitec-if="(Model.eiendom.eieform == &quot;Aksje&quot; || Model.eiendom.eieform == &quot;Obligasjonsleilighet&quot;)">aksjen</span>

<!-- Grouped AND (exclusion) -->
<div vitec-if="(Model.eiendom.eieform != &quot;Andel&quot; &amp;&amp; Model.eiendom.eieform != &quot;Aksje&quot; &amp;&amp; Model.eiendom.eieform != &quot;Obligasjonsleilighet&quot;)">
```

**Fields observed:** `eiendom.eieform`, `eiendom.boligtype`, `eiendom.grunntype`, `eiendom.tomtetype`, `oppdrag.hovedtype`

**Values observed:**
- `eieform`: Selveier, Sameie, Andel, Aksje, Obligasjonsleilighet, Eierseksjon
- `boligtype`: Tomt
- `grunntype`: Bolig, Fritid
- `tomtetype`: eiertomt, festetomt
- `hovedtype`: Salgsoppdrag, Oppgjørsoppdrag, Utleieoppdrag (uses `\xF8` escape for ø)

---

### Pattern B: "Mangler data" Sentinel Check (CRITICAL DISCOVERY)

**The golden standards explicitly use `"Mangler data"` as a branching condition.** This is NOT just hiding content — it's a fallback mechanism where the template renders alternative content when data is unavailable.

**Example 1 — Hjemmelshaver fallback (forbruker):**
```html
<!-- If hjemmelshaver data exists, show it -->
<span vitec-if="Model.hjemmelshaver.navn != &quot;Mangler data&quot;">
  <span vitec-foreach="hjemmelshaver in Model.hjemmelshavere">
    [[*hjemmelshaver.navn]] ([[*hjemmelshaver.fdato_orgnr]])
  </span>
</span>

<!-- If NOT, fall back to selgere names -->
<span vitec-if="Model.hjemmelshaver.navn == &quot;Mangler data&quot;">
  <span vitec-foreach="selger in Model.selgere">
    [[*selger.navnutenfullmektigogkontaktperson]]
  </span>
</span>
```

**Example 2 — Grunneier fallback (forbruker):**
```html
<!-- If grunneier data exists, show it -->
<span vitec-if="Model.grunneier.navn != &quot;Mangler data&quot;">
  <span vitec-foreach="grunneier in Model.grunneiere">
    [[*grunneier.navn]] ([[*grunneier.fdato_orgnr]])
  </span>
</span>

<!-- If NOT, show insert field for manual entry -->
<span vitec-if="Model.grunneier.navn == &quot;Mangler data&quot;">
  <span class="insert-table"><span class="insert" data-label="Grunneiers navn og fødselsdato"></span></span>
</span>
```

**Example 3 — Megler roles (oppdragsavtale):**
```html
<!-- If ansvarligmegler exists AND differs from operativmegler, show both -->
<span vitec-if="(Model.ansvarligmegler.navn != &quot;Mangler data&quot; &amp;&amp; Model.operativmegler.navn != Model.ansvarligmegler.navn)">
  Oppdragsansvarlig er [[operativmegler.navn]].
  Ansvarlig megler er [[ansvarligmegler.navn]].
</span>

<!-- If ansvarligmegler missing OR same person, show only one -->
<span vitec-if="(Model.ansvarligmegler.navn == &quot;Mangler data&quot; || Model.operativmegler.navn == Model.ansvarligmegler.navn)">
  Ansvarlig megler er [[operativmegler.navn]].
</span>

<!-- Medhjelper only shown if data exists -->
<span vitec-if="Model.megler2.navn != &quot;Mangler data&quot;">
  Medhjelper er [[megler2.navn]].
</span>
```

**Key insight:** "Mangler data" checks are used specifically for **entity-level** fields (hjemmelshaver, grunneier, megler) — fields where the entire entity might not exist, not just a property being empty. For **property-level** fields (tlf, emailadresse), the golden standards use only `!= ""` without "Mangler data" guards.

**Implication for our template:** Our fullmektig guard (`!= "" && != "Mangler data"`) is actually MORE defensive than the golden standard, which is a good thing for production quality. But for consistency, we should understand that the golden standards accept "Mangler data" appearing in contact info fields.

---

### Pattern C: Empty String Check

Simple `!= ""` for conditional display of optional property values.

```html
<span vitec-if="selger.tlf != &quot;&quot;">Tlf: [[*selger.tlf]]</span>
<span vitec-if="selger.emailadresse != &quot;&quot;">E-post: [[*selger.emailadresse]]</span>
```

**Important:** The golden standards do NOT add `!= "Mangler data"` to these conditions. If Vitec returns "Mangler data" for a phone number, the golden standard templates would show `Tlf: Mangler data`. Our enhanced guard is non-standard but arguably better.

**Also used for:** `eiendom.heftelserogrettigheter != ""`, `aksjeselskap.partoblnr != "0"`, `eiendom.fellesgjeld != "0,00"`

---

### Pattern D: Boolean Check

For true/false flags from the API.

```html
<p vitec-if="Model.oppdrag.erdetforkjopsfrist == true">Forkjøpsrett...</p>
<p vitec-if="Model.oppdrag.boligselgerforsikringbestilt == false">ikke tegnet</p>
<span vitec-if="Model.oppdrag.vederlagtypeprovisjon == true">Provisjon</span>
```

**Observed boolean fields:** `erdetforkjopsfrist`, `boligselgerforsikringbestilt`, `vederlagtypeprovisjon`, `vederlagtypefastpris`, `erutbyggersforbeholdsalgsgrad`, `erutbyggersforbeholdigangsettelse`, `erutbyggersforbeholdbyggelaan`, `erfellesgjeldinkludertiprovisjonsgrunnlag`

---

### Pattern E: Collection Count

```html
<!-- Guard for non-empty -->
<table vitec-if="Model.selgere.Count &gt; 0">

<!-- Plural/singular -->
<span vitec-if="Model.kjopere.Count == 1">Jeg</span>
<span vitec-if="Model.kjopere.Count &gt; 1">Vi</span>

<!-- Fallback for empty -->
<div vitec-if="Model.selgere.Count == 0">[Mangler selger]</div>
```

---

### Pattern F: Field-to-Field Comparison (ADVANCED)

Only seen in oppdragsavtale — comparing two merge field values.

```html
<span vitec-if="Model.operativmegler.navn != Model.ansvarligmegler.navn">
```

This checks whether the operative broker and responsible broker are different people. If they're the same, only one is shown.

---

### Pattern G: .NET Method Call (ADVANCED)

Only seen in oppdragsavtale — calling `.ToString().Length` on a field.

```html
<article vitec-if="Model.selger.idnummer.ToString().Length == 12">
  <!-- Angrerett section — only for business customers (org.nr = 12 digits) -->
</article>

<p vitec-if="Model.selger.idnummer.ToString().Length == 11">
  <!-- Personal customer (fødselsnr = 11 digits) -->
</p>
```

This reveals that vitec-if evaluates **C#/.NET expressions**, not just simple comparisons. The `.ToString().Length` pattern is a method chain that works within the evaluator.

---

### Pattern H: Compound Conditions

```html
<!-- AND -->
<div vitec-if="(Model.eiendom.eieform != &quot;Andel&quot; &amp;&amp; Model.eiendom.eieform != &quot;Aksje&quot;)">

<!-- OR -->
<span vitec-if="(Model.eiendom.eieform == &quot;Aksje&quot; || Model.eiendom.eieform == &quot;Obligasjonsleilighet&quot;)">

<!-- Mixed AND + OR -->
<p vitec-if="Model.oppdrag.erdetforkjopsfrist == true &amp;&amp; (Model.eiendom.eieform == &quot;Sameie&quot; || Model.eiendom.eieform == &quot;Andel&quot;)">

<!-- Boolean AND value -->
<span vitec-if="Model.oppdrag.erfellesgjeldinkludertiprovisjonsgrunnlag == true &amp;&amp; Model.eiendom.fellesgjeld != &quot;0,00&quot;">
```

**Encoding rules:** `&&` → `&amp;&amp;`, `"` → `&quot;`, `>` → `&gt;`

---

### Pattern I: Razor Server-Side Code (ADVANCED)

Only in oppdragsavtale — actual C# code in HTML comments.

```html
<!-- @{
  var erSalg = "";
  if (Model.oppdrag.hovedtype == "Salgsoppdrag" && !Model.oppdrag.type.Contains("\xF8")) {
    erSalg = "active";
  }
} -->
<label class="btn @erSalg" ...>
```

This is NOT vitec-if — it's Razor template pre-processing that runs server-side. The `@erSalg` variable is interpolated into the HTML before the client-side vitec-if processing. This pattern is used for the oppdragstype radio group where the active state needs to be set at render time.

**Implication:** Some checkbox states in Vitec templates cannot be achieved with vitec-if alone — they require Razor code blocks.

---

### Pattern J: CSS-Based Conditional Display

Also in oppdragsavtale — using CSS selectors instead of vitec-if.

```css
#vitecTemplate .main-type { display: none; }
#vitecTemplate .announced-type { display: none; }
#vitecTemplate .announced-type[data-type="Oppgjørsoppdrag"] { display: inline; }
```

This shows/hides content based on CSS attribute selectors rather than vitec-if. The `data-type` attribute is presumably set by the API.

---

### Pattern K: Unicode Escape in Conditions

The `\xF8` escape sequence appears in condition values:

```html
<div vitec-if="Model.oppdrag.hovedtype == &quot;Oppgj\xF8rsoppdrag&quot;">
```

This is equivalent to `"Oppgjørsoppdrag"`. The vitec-if evaluator interprets JavaScript-style unicode escapes. This is important when condition values contain Norwegian characters.

---

## 2. Element-Level vitec-if Placement

Golden standards place vitec-if on various HTML elements:

| Element | Example | Used for |
|---------|---------|----------|
| `<span>` | Inline text alternatives | Most common — word/phrase switching |
| `<div>` | Block-level content blocks | Sections with multiple paragraphs |
| `<p>` | Entire paragraphs | Single conditional paragraphs |
| `<article>` | Entire numbered sections | Conditional sections (e.g., Festekontrakt) |
| `<table>` | Entire tables | Conditional page sections (angreskjema) |
| `<li>` | List items in bilag section | Conditional list entries |
| `<tr>` | Table rows | Conditional financial line items |

**Notably NOT used on:**
- `<td>` (columns) — use `<span>` inside `<td>` instead
- `<thead>` — use `<table>` level instead
- `<label>` — checkbox state uses class "active", not vitec-if

---

## 3. Checkbox/Radio Patterns (Definitive)

### Standalone Checkbox (no input element)
```html
<label class="btn" contenteditable="false" data-toggle="button">
  <span class="checkbox svg-toggle"></span>
</label>
```

### Standalone Checked Checkbox
```html
<label class="btn active" contenteditable="false" data-toggle="button">
  <span class="checkbox svg-toggle"></span>
</label>
```

### Radio Button Group (mutual exclusion)
```html
<p data-toggle="buttons">
  <label class="btn" contenteditable="false" data-toggle="button">
    <span class="checkbox svg-toggle"></span>
    <input name="rbl001" type="radio" />
  </label> Option A
  <label class="btn" contenteditable="false" data-toggle="button">
    <span class="checkbox svg-toggle"></span>
    <input name="rbl001" type="radio" />
  </label> Option B
</p>
```

**Rules:**
1. `<span>` ALWAYS comes BEFORE `<input>` inside the label
2. Standalone checkboxes have NO `<input>` element
3. Radio groups use `type="radio"` with shared `name="rblNNN"` (incrementing NNN per group)
4. Radio groups require `data-toggle="buttons"` on a parent element (`<p>`, `<td>`, `<tbody>`, `<tr>`, `<div>`)
5. Active state is set via `class="active"` on the `<label>`, or via Razor `@variable`

---

## 4. Vitec-Foreach Patterns

### Standard Collection Iteration
```html
<tbody vitec-foreach="selger in Model.selgere">
  <tr><td>[[*selger.navn]]</td></tr>
</tbody>
```

### Inline List with Separator
```html
<span vitec-foreach="selger in Model.selgere">
  <span class="liste">
    [[*selger.navnutenfullmektigogkontaktperson]]
    <span class="separator">, </span>
  </span>
</span>
```

CSS hides the last separator: `.liste:last-child .separator { display: none; }`

### Financial Line Items
```html
<tbody vitec-foreach="kostnad in Model.kjoperskostnader.alleposter">
  <tr>
    <td>[[*kostnad.beskrivelse]]:</td>
    <td>kr</td>
    <td>$.UD([[*kostnad.belop]])</td>
  </tr>
</tbody>
```

**Collections observed:** `Model.selgere`, `Model.kjopere`, `Model.hjemmelshavere`, `Model.grunneiere`, `Model.kjoperskostnader.alleposter`, `Model.selgervederlag.alleposter`, `Model.selgerutlegg.alleposter`, `Model.selgerutgifter.alleposter`

---

## 5. Special Functions

| Function | Example | Purpose |
|----------|---------|---------|
| `$.UD()` | `$.UD([[kontrakt.kjopesum]])` | Format number with thousands separator |
| `$.CALCHOURS()` | `$.CALCHOURS([[oppdrag.timebudsjettantall]]-[[timer.budsjett.visning]])` | Calculate hours (subtraction) |

---

## 6. Merge Field Reference (New Fields from Golden Standards)

Fields seen in golden standards but NOT in our prosjekt template:

| Field | Template | Purpose |
|-------|----------|---------|
| `[[kontrakt.klientkontoogkid]]` | forbruker | Combined klientkonto + KID |
| `[[oppgjor.postadresse]]` | forbruker, oppdragsavtale | Mailing address (vs besøks) |
| `[[oppgjor.postnr]]` | forbruker | Postal code |
| `[[oppgjor.poststed]]` | forbruker | Postal city |
| `[[oppgjor.orgnr]]` | oppdragsavtale | Oppgjør org number |
| `[[oppgjor.ansvarlig.navn]]` | oppdragsavtale | Oppgjør responsible person |
| `[[kontrakt.dato]]` | forbruker | Contract date (vs dagensdato) |
| `[[kontrakt.overtagelse.klokkeslett]]` | forbruker | Handover time |
| `[[forsikring.selskap]]` | forbruker | Insurance company |
| `[[forsikring.polisenr]]` | forbruker | Insurance policy number |
| `[[komplettmatrikkelutvidet]]` | forbruker | Full property ID |
| `[[eiendom.takstdato]]` | forbruker | Valuation date |
| `[[operativmegler.navn]]` | oppdragsavtale | Operative broker |
| `[[ansvarligmegler.navn]]` | oppdragsavtale | Responsible broker |
| `[[selger.idnummer]]` | oppdragsavtale | ID number (fnr/orgnr) |
| `[[meglerkontor.fullmektigenavn]]` | oppdragsavtale | Office staff names |

---

## 7. Impact on Our Template

### What we're doing RIGHT (confirmed by golden standards):
- Dual `vitec-if` wrapper for conditional checkboxes (Approach A)
- `Model.xxx.Count > 0` guards before foreach loops
- Fallback blocks for empty collections
- `&amp;&amp;` and `||` compound conditions
- `&quot;` for string values, `&gt;` for greater-than
- `$.UD()` for monetary formatting
- Separate `<style>` blocks for template CSS vs checkbox CSS

### What we need to CHANGE:
1. **Checkbox CSS/HTML** — Replace entirely with golden standard block (P0)
2. **Insert field CSS** — Replace with `lightpink` background pattern (P1)
3. **CSS scoping** — Un-scope checkbox and insert-field CSS (P2)

### What we're doing BETTER than golden standards:
1. **"Mangler data" guard on contact info** — Golden standards don't do this, but our enhanced guards prevent ugly "Mob: Mangler data" in the PDF
2. **"Mangler data" guard on fullmektig** — Appropriate since fullmektig is an entity-level field (golden standards do this for similar entity fields like hjemmelshaver and grunneier)

### Patterns we DON'T use yet (may need for future templates):
1. **Field-to-field comparison** (`Model.a.navn != Model.b.navn`)
2. **`.ToString().Length`** for numeric ID type detection
3. **Razor `@{ }` code blocks** for complex checkbox state logic
4. **CSS `[data-type]` selectors** for conditional display
5. **`$.CALCHOURS()`** for arithmetic in merge fields
6. **`\xF8` unicode escapes** in condition string values
7. **Radio button groups** with `data-toggle="buttons"` parent
8. **`.insert-textbox`** for wider text input fields
9. **Inline foreach with `.liste` + `.separator`** pattern
