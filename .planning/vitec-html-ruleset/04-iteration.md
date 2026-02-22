## 4. Vitec-foreach Iteration

### Basic syntax

```html
<element vitec-foreach="item in Model.collection">
  [[item.property]]
</element>
```

The element is repeated once for each item in the collection. The loop variable (`item`) is available inside the element and its descendants.

#### Custom method as collection source

When a support template defines `@functions` methods that return a `List<>`, those methods can be used as the collection source in `vitec-foreach` — **without the `@` prefix**:

```html
<!-- Standard: iterate Model collection -->
<tbody vitec-foreach="kostnad in Model.kjoperskostnader.alleposter">

<!-- Custom: iterate method return value (no @ prefix) -->
<tbody vitec-foreach="kostnad in GetPosteringerUtenBoligkjoperforsikring()">
```

The loop variable (`kostnad`) works identically in both cases — merge fields like `[[*kostnad.beskrivelse]]` and `[[*kostnad.belop]]` resolve against each item.

**(Evidence: custom Proaktiv Kjøpekontrakt Bruktbolig)**

### Safe container elements for vitec-foreach

| Element | Example | Evidence |
|---------|---------|----------|
| `<tbody>` | `<tbody vitec-foreach="selger in Model.selgere">` | Most common; lines 501, 1123, 1821, 3012, 4843 |
| `<table>` | `<table vitec-foreach="pant in Model.oppdrag.kjoperspant">` | Lines 1282, 3522, 3676, 3783, 4009 |
| `<ul>` | `<ul vitec-foreach="kjoper in Model.kjopere">` | Lines 1961, 5162 |
| `<span>` | `<span vitec-foreach="selger in Model.selgere">` | Used for inline comma-separated lists (DB evidence: "Oppgjørsoppstilling Selger", "Forslag til fordelingskjennelse") |
| `<div>` | (implied by reference docs) | |
| `<tr>` | (possible but not observed as primary pattern) | |

**Best practice:** Use `<tbody>` as the foreach container when iterating table rows. This allows multiple `<tbody>` sections in a single `<table>`.

### Inline list separator pattern

For rendering comma-separated lists inline (e.g., "Name1, Name2, Name3"), use the `.liste` / `.separator` pattern:

```html
<span vitec-foreach="selger in Model.selgere">
  <span class="liste">
    [[*selger.navn]]<span class="separator">, </span>
  </span>
</span>
```

CSS hides the separator on the last item:
```css
#vitecTemplate .liste:last-child .separator {
    display: none;
}
```

Variants use different class names for the same pattern: `.seller`, `.buyer`, `.saksokte` instead of `.liste`.

**(DB evidence: "Oppgjørsoppstilling Selger" uses `.seller`, "Forslag til fordelingskjennelse" uses `.liste`)**

### Filtering with .Where()

Filter a collection to a subset:

```html
<tbody vitec-foreach="kostnad in Model.kjoperskostnader.alleposter.Where(x =&gt; x.kode == &quot;PARKERING&quot;)">
  <tr>
    <td>[[*kostnad.belop]]</td>
  </tr>
</tbody>
```

**Evidence:** Line 6381. Note the `=&gt;` (HTML entity for `=>` lambda arrow).

#### Complex Where with logical AND and cross-collection references

```html
<tbody vitec-foreach="pant in Model.oppdrag.pantforinnfrielse.Where(x =&gt; x.ertypeutleggsforretning == true &amp;&amp; Model.saksoker.firmanavn != x.navn)">
```

Note: `&&` must be HTML-escaped as `&amp;&amp;`. The lambda can reference both the iteration variable (`x`) and Model-level data (`Model.saksoker.firmanavn`).

**(DB evidence: "Forslag til fordelingskjennelse (Tvangssalg)", "Kjennelse ved fordeling av kjøpesum etter tvangssalg")**

#### Chaining .Where() with .Take()

```html
<tbody vitec-foreach="pant in Model.oppdrag.pantforinnfrielse.Where(x =&gt; x.ertypelegalpant == true).Take(1)">
```

Filters the collection first, then takes only the first N results. Observed chained patterns:
- `.Where(x =&gt; x.ertypelegalpant == true).Take(1)`
- `.Where(x =&gt; x.ertypelegalpant == false).Take(1)`
- `.Where(x =&gt; x.ertypeutleggsforretning == false).Take(1)`

**(DB evidence: "Forslag til fordelingskjennelse (Tvangssalg)")**

### Limiting with .Take()

Take only the first N items:

```html
<tbody vitec-foreach="pant in Model.oppdrag.pantforinnfrielse.Take(2)">
```

**Evidence:** Line 6482; also `Model.oppdrag.pantforinnfrielse.Take(1)` (DB evidence: "Forslag til fordelingskjennelse").

### Combined vitec-if and vitec-foreach on same element

Both attributes can appear on the same element:

```html
<tbody vitec-foreach="pant in Model.oppdrag.pantforinnfrielse.Take(2)" vitec-if="Model.oppdrag.pantforinnfrielse.Any()">
  <tr>
    <td>[[*pant.prioritet]]</td>
    <td>[[*pant.navn]]</td>
  </tr>
</tbody>
```

**Evidence:** Line 6482. The `vitec-if` acts as a guard — if the collection is empty, the element is not rendered at all.

### Nested foreach

Foreach can be nested. The inner loop uses the outer loop variable to access sub-collections:

```html
<ul vitec-foreach="kjoper in Model.kjopere">
  <li>Kjøper: [[*kjoper.navn]]
    <ul vitec-foreach="fullmektig in kjoper.fullmektiger_hvis_gruppe">
      <li>Fullmektig: [[*fullmektig.navn]]</li>
    </ul>
  </li>
</ul>
```

**Evidence:** Lines 1961–1967. Note the inner loop iterates over `kjoper.fullmektiger_hvis_gruppe` — a sub-property of the outer loop variable.

Another nested example with `<tbody>` inside `<table>`:

```html
<table vitec-foreach="pant in Model.oppdrag.mottakerspantforinnfrielse">
  <!-- ... pant rows ... -->
  <tbody vitec-foreach="laan in pant.laan">
    <tr><td>[[*laan.belop]]</td></tr>
  </tbody>
</table>
```

**Evidence:** Lines 3676–3742.

#### Grouped settlement pattern (nested table foreach)

Settlement documents use a two-level grouping pattern where an outer `vitec-foreach` iterates groups and an inner foreach iterates posts within each group:

```html
<table vitec-foreach="gruppe in Model.oppgjorselger.gruppering">
  <tbody>
    <tr class="borderoppgjor">
      <td colspan="100">[[*gruppe.overskrift]]</td>
    </tr>
  </tbody>
  <tbody vitec-foreach="post in gruppe.poster">
    <tr>
      <td colspan="14">[[*post.posteringsdato]]</td>
      <td colspan="40">[[*post.beskrivelse]]</td>
      <td colspan="17" style="text-align:right">
        <span vitec-if='post.debet != ""'>[[*post.debet]]</span>
      </td>
      <td colspan="17" style="text-align:right">
        <span vitec-if='post.kredit != ""'>[[*post.kredit]]</span>
      </td>
    </tr>
  </tbody>
</table>
```

**(DB evidence: "Oppgjørsoppstilling Selger")**

### Known collections

Collections observed in production templates (partial list):

| Collection | Loop variable | Evidence |
|------------|--------------|----------|
| `Model.meglerkontor.aktiveansatte` | `ansatt` | Line 501 |
| `Model.selgere` | `selger` | Lines 4843, 5022 |
| `Model.kjopere` | `kjoper` | Line 1821 |
| `Model.arvinger` | `arving` | Line 3012 |
| `Model.grunneiere` | `grunneier` | Line 3194 |
| `Model.hjemmelshavere` | `hjemmelshaver` | Line 3318 |
| `Model.tidligereeiere` | `tidligereeier` | Line 3434 |
| `Model.hoyestebud.budgivere` | `budgiver` | Line 1123 |
| `Model.matrikler` | `matrikkel` | Line 2261 |
| `Model.oppdrag.kjoperspant` | `pant` | Line 3522 |
| `Model.oppdrag.pantforinnfrielse` | `pant` | Line 3894 |
| `Model.oppdrag.mottakerspant` | `pant` | Line 3783 |
| `Model.oppdrag.mottakerspantforinnfrielse` | `pant` | Line 3676 |
| `pant.laan` | `laan` | Lines 3742, 3849, 3960 |
| `Model.selgervederlag.poster` | `vederlag` | Line 2703 |
| `Model.selgervederlag.alleposter` | `vederlag` | Line 2726 |
| `Model.selgerutlegg.poster` | `utlegg` | Line 2763 |
| `Model.selgerutlegg.alleposter` | `utlegg` | Line 2786 |
| `Model.selgerutgifter.poster` | `utgift` | Line 2823 |
| `Model.selgerutgifter.alleposter` | `utgift` | Line 2846 |
| `Model.selgersfakturerte.poster` | `faktura` | Line 2897 |
| `Model.selgersfakturerte.alleposter` | `faktura` | Line 2929 |
| `Model.kjoperskostnader.poster` | `kostnad` | Line 2066 |
| `Model.kjoperskostnader.alleposter` | `kostnad` | Line 2088 |
| `Model.kjopersfakturerte.poster` | `faktura` | Line 2138 |
| `Model.kjopersfakturerte.alleposter` | `faktura` | Line 2170 |
| `Model.solgteoppdragiomraade` | `oppdrag` | Line 2400 |
| `Model.mottaker.utbetalingsposter` | `postering` | Line 4009 |
| `Model.oppgjorkjoper.gruppering` | `gruppe` | Line 4066 |
| `gruppe.poster` | `post` | Lines 4073, 4131 |
| `Model.oppgjorselger.gruppering` | `gruppe` | Line 4124 |
| `Model.oppdrag.prosjekt.prosjektenheter` | `prosjektenhet` | Line 4226 |
| `Model.oppdrag.prosjekt.utbyggersforbehold.forbehold` | `forbehold` | Line 4350 |
| `Model.oppdrag.prosjektenhet.parkeringsplasser` | `prosjektenhet` | Line 4452 |
| `Model.oppdrag.prosjekt.vederlagpaomsetninger` | `vederlagpaomsetning` | Line 4689 |
| `Model.eiendom.kommendevisninger` | `visning` | Line 5807 |
| `visning.slots` | `slot` | Line 5824 |
| `Model.saksokere` | `saksoker` | Line 5354 |
| `Model.saksokteliste` | `saksokte` | Line 5713 |
| `Model.oppdrag.pantedokumenterkjoper` | `depotdokument` | Line 1282 |
| `kjoper.fullmektiger_hvis_gruppe` | `fullmektig` | Lines 1963, 5164 |
| `selger.fullmektiger_hvis_gruppe` | `fullmektig` | Line 5164 |
| `Model.oppdrag.saksokerspant` | `pant` | Line 5485 |

#### Additional collections from database templates

| Collection | Loop variable | Evidence |
|------------|--------------|----------|
| `Model.oppdrag.pantforinnfrielse.Where(x =&gt; x.ertypelegalpant == true)` | `pant` | (DB: "Forslag til fordelingskjennelse") |
| `Model.oppdrag.pantforinnfrielse.Where(x =&gt; x.ertypefrivilligpant == true &amp;&amp; Model.saksoker.firmanavn != x.navn)` | `pant` | (DB: "Forslag til fordelingskjennelse") |
| `Model.oppdrag.pantforinnfrielse.Where(x =&gt; x.ertypeutleggsforretning == true &amp;&amp; Model.saksoker.firmanavn != x.navn)` | `pant` | (DB: "Kjennelse ved fordeling") |
| `Model.selgerutgifter.alleposter` | `utgifter` | (DB: multiple settlement templates) — Note: alternative variable name `utgifter` alongside `utgift` |

---
