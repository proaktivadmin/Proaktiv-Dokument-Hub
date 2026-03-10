## 3. Vitec-if Conditional Logic

### Basic syntax

```html
<element vitec-if="expression">Content shown when true</element>
```

The `vitec-if` attribute causes the element and its contents to be included in the rendered output only when the expression evaluates to true. When false, the entire element (including children) is removed from the output.

### Expression syntax

All expressions reference the `Model` object, which contains the template data context.

#### Comparison operators

| Operator | Syntax | Example |
|----------|--------|---------|
| Equals | `==` | `Model.eiendom.eieform == &quot;Andel&quot;` |
| Not equals | `!=` | `Model.eiendom.eieform != &quot;Andel&quot;` |
| Greater than | `&gt;` | `Model.oppdrag.antallvisninger &gt; 0` |
| Less than | `&lt;` | (implied, not observed directly) |
| Greater/equal | `&gt;=` | (implied) |
| Less/equal | `&lt;=` | (implied) |

**Critical:** In HTML attributes, `>` must be written as `&gt;` and `<` as `&lt;`. Quotes inside the attribute value must use `&quot;`.

#### String methods

| Method | Syntax | Example |
|--------|--------|---------|
| Contains | `.Contains(&quot;text&quot;)` | `Model.oppdrag.type.Contains(&quot;tleie&quot;)` |
| StartsWith | `.StartsWith(&quot;text&quot;)` | `Model.meglerkontor.internid.StartsWith(&quot;2&quot;)` |
| ToString | `.ToString()` | `kjoper.idnummer.ToString().Length == 11` — converts a numeric field to string for length checking. (DB evidence: "Egenerklæring om konsesjonsfrihet") |
| Remove | `.Remove(start, count)` | `@Model.oppgjorkjoper.saldo.Remove(0,1)` (inline text, not vitec-if) |

#### Collection methods

| Method | Syntax | Example |
|--------|--------|---------|
| Count (property) | `.Count` | `Model.kjopere.Count == 0` |
| Count (method) | `.Count()` | `Model.oppdrag.pantforinnfrielse.Where(x =&gt; ...).Count() == 0` — used after `.Where()` filter chain. (DB evidence: "Forslag til fordelingskjennelse") |
| Any (parameterless) | `.Any()` | `Model.oppdrag.pantforinnfrielse.Any()` — simple existence check. (DB evidence: "Varsel om heving av tvangssalg") |
| Any (filtered) | `.Any(x =&gt; x.prop == &quot;val&quot;)` | `Model.kjoperskostnader.alleposter.Any(x =&gt; x.kode == &quot;PARKERING&quot;) == false` |
| Any (cross-ref) | `.Any(x =&gt; x.prop == Model.other.prop)` | `Model.saksokere.Any(x =&gt; x.firmanavn == Model.mottaker.navn)` — references Model-level data inside lambda. (DB evidence: "Pantedokument (sikring)") |
| Where+Count | `.Where(x =&gt; ...).Count()` | `Model.oppdrag.pantforinnfrielse.Where(x =&gt; x.ertypeutleggsforretning == true &amp;&amp; Model.saksoker.firmanavn != x.navn).Count() == 0` (DB evidence: "Forslag til fordelingskjennelse") |
| FirstOrDefault | `.FirstOrDefault(x =&gt; ...)` | Returns first matching item or null. Used in `@functions` blocks: `@Model.kjoperskostnader.alleposter.FirstOrDefault(x => codeList.Contains(x.kode))` (Evidence: custom Kjøpekontrakt FORBRUKER) |
| ToList | `.ToList()` | Materializes a LINQ query. Used in `@functions` blocks: `.Where(x => !codeList.Contains(x.kode)).ToList()` (Evidence: custom Kjøpekontrakt FORBRUKER) |
| Contains (negated) | `!list.Contains(x.prop)` | Used inside `.Where()` lambda to exclude items: `.Where(x => !codeList.Contains(x.kode))` (Evidence: custom Kjøpekontrakt FORBRUKER) |

#### Boolean values

Explicit comparison:
```html
<span vitec-if="Model.megler2.erstudent == true">Ja</span>
<span vitec-if="Model.megler2.erstudent == false">Nei</span>
```

Implicit boolean (without `== true`):
```html
<span vitec-if="selger.ergift">Gift</span>
```

**(DB evidence: "Hjemmelserklæring")** — The implicit form (without `== true`) is valid and used in production templates.

#### Empty string comparison

```html
<span vitec-if='post.debet != ""'>[[*post.debet]]</span>
```

Checking whether a field has a value by comparing to empty string `""`. **(DB evidence: "Oppgjørsoppstilling Selger")**

#### Dynamic pluralization pattern

Conditionally append a plural suffix when a collection has more than one item:

```html
<strong>Selger<span vitec-if="Model.selgere.Count &gt; 1">e</span></strong>
```

Renders "Selger" for a single seller, "Selgere" for multiple. Used in the Grunnlag brevmal letter templates for party listing table headers. **(Evidence: Grunnlag brevmal selger, kjøper, selger og kjøper)**

#### "Mangler data" sentinel value

Some merge fields return the string `"Mangler data"` instead of an empty string when data is unavailable. Best practice is to check for both:

```html
<span vitec-if='!(Model.field == "Mangler data" || Model.field == "")'>
  [[field.value]]
</span>
```

Known fields that return "Mangler data": `selger.tlf`, `kjoper.tlf`, `esignering.melding`, `mottaker.visning.dato`, `grunneier.navn`, `hjemmelshaver.navn`. **(Evidence: Grunnlag brevmal selger/kjøper, "E-signeringsforespørsel SMS", "Visningsbekreftelse", Skjøte)**

#### Logical operators

**AND (`&&`)** — HTML-escaped as `&amp;&amp;`:
```html
<span vitec-if="Model.pant.ertypelegalpant == false &amp;&amp; (Model.saksokere.Any(x =&gt; x.firmanavn != Model.mottaker.navn))">
```
**(DB evidence: "Pantedokument (sikring)")**

**OR (`||`)** — Used in compound conditions:
```html
<p vitec-if='!(Model.esignering.melding == "Mangler data" || Model.esignering.melding == "")'>
  [[esignering.melding]]
</p>
```
**(DB evidence: "E-signeringsforespørsel SMS")**

**Note:** `&&` must be HTML-escaped as `&amp;&amp;` when used inside HTML attributes. `||` appears to work unescaped in single-quoted attribute values.

#### Negation

Prefix `!` negates the entire expression:

```html
<span vitec-if="!Model.oppdrag.type.Contains(&quot;tleie&quot;)">Selger</span>
```

`!()` wrapping negates a compound expression:
```html
<p vitec-if='!(Model.esignering.melding == "Mangler data" || Model.esignering.melding == "")'>
```
**(DB evidence: "E-signeringsforespørsel SMS", "E-signeringspåminnelse SMS")**

### Safe container elements for vitec-if

Confirmed safe from production templates:

| Element | Example | Evidence |
|---------|---------|----------|
| `<span>` | `<span vitec-if="...">text</span>` | Most common; lines 952, 1649, 2332, 6306, 6408 |
| `<em>` | `<em vitec-if="...">Ingen registrert</em>` | Lines 499, 1121, 1819 |
| `<table>` | `<table vitec-if="Model.x.Count &gt; 0">` | Lines 500, 1122, 1820 |
| `<tbody>` | `<tbody vitec-if="...">` | Lines 6387, 6482 |
| `<tr>` | `<tr vitec-if="Model.dokumentoutput == &quot;pdf&quot;">` | Lines 6160, 6164 |
| `<div>` | `<div vitec-if="Model.x.Count &gt; 0">` | Line 1281; also `<div style="page-break-inside:avoid" vitec-if="...">` (DB evidence: "Oppgjørsoppstilling Selger") |
| `<p>` | `<p vitec-if='...'>text</p>` | (DB evidence: "E-signeringsforespørsel SMS", "E-signeringspåminnelse SMS") |
| `<article>` | `<article class="item" vitec-if="...">` | Contract sections conditionally shown by eieform (Evidence: Kjøpekontrakt FORBRUKER) |
| `<li>` | `<li vitec-if="Model.oppdrag.hovedtype != ...">` | Conditional list items in Bilag section (Evidence: Kjøpekontrakt FORBRUKER) |
| `<ol>` | `<ol class="avoid-page-break">` | Ordered lists for numbered legal conditions (Evidence: Kjøpekontrakt FORBRUKER) |
| `<ul>` | (implied by vitec-foreach on `<ul>`, combined with vitec-if) | |

### Loop variable field access in vitec-if

Inside a `vitec-foreach` block, `vitec-if` expressions can reference the loop variable directly (without `Model.` prefix):

```html
<tbody vitec-foreach="matrikkel in Model.matrikler">
  <tr vitec-if="matrikkel.fnr != 0">
    <td>[[*matrikkel.fnr]]</td>
  </tr>
</tbody>
```

Also valid with nested property access:
```html
<span vitec-if="kjoper.idnummer.ToString().Length == 11">
  Personnr: [[*kjoper.idnummer]]
</span>
```

**(DB evidence: "Skjøte", "Egenerklæring om konsesjonsfrihet")**

### Escaping rules (critical)

#### Quotes in attribute values

All string comparisons require `&quot;` for quote characters:

```html
<!-- CORRECT -->
<span vitec-if="Model.eiendom.eieform == &quot;Andel&quot;">

<!-- WRONG — will break -->
<span vitec-if="Model.eiendom.eieform == "Andel"">
```

#### Norwegian characters (æ, ø, å)

Norwegian characters in vitec-if comparisons must use escape sequences:

| Character | Escape | Example |
|-----------|--------|---------|
| æ (liten) | `\xE6` | `Model.eiendom.grunntype == &quot;N\xE6ring&quot;` |
| Æ (stor) | `\xC6` | |
| ø (liten) | `\xF8` | `Model.oppdrag.hovedtype == &quot;Oppgj\xF8rsoppdrag&quot;` |
| Ø (stor) | `\xD8` | |
| å (liten) | `\xE5` | `Model.eiendom.poststed == &quot;\xC5rnes&quot;` |
| Å (stor) | `\xC5` | (note: uses uppercase Å escape for "Årnes") |

**Evidence:** Lines 6401–6428 in Alle-flettekoder explicitly document these escapes with examples.

#### Greater than / Less than

Must use HTML entities in attribute values:

```html
<!-- CORRECT -->
<table vitec-if="Model.kjopere.Count &gt; 0">

<!-- WRONG — HTML parser will break -->
<table vitec-if="Model.kjopere.Count > 0">
```

### Nesting rules

`vitec-if` can be nested — an element with `vitec-if` can contain children that also have `vitec-if`. This is implicitly confirmed by patterns like:

```html
<table vitec-if="Model.kjopere.Count &gt; 0">
  <tbody vitec-foreach="kjoper in Model.kjopere">
    <tr>
      <td><span vitec-if="kjoper.erfirma == true">Ja</span></td>
    </tr>
  </tbody>
</table>
```

Here `vitec-if` on `<table>` wraps a `vitec-foreach` on `<tbody>`, which contains `vitec-if` on `<span>`. (Lines 1820–1850)

### Common conditional patterns

#### Empty collection guard + foreach

The most common pattern guards a `vitec-foreach` with a `vitec-if` check for empty collections:

```html
<em vitec-if="Model.selgere.Count == 0">Ingen registrert</em>
<table vitec-if="Model.selgere.Count &gt; 0">
  <tbody vitec-foreach="selger in Model.selgere">
    <tr><td>[[*selger.navn]]</td></tr>
  </tbody>
</table>
```

#### Boolean toggle (Ja/Nei)

```html
<span vitec-if="Model.kjoper.erfirma == true">Ja</span>
<span vitec-if="Model.kjoper.erfirma == false">Nei</span>
```

#### Output channel branching

```html
<tr vitec-if="Model.dokumentoutput == &quot;pdf&quot;">
  <!-- PDF-only content -->
</tr>
<tr vitec-if="Model.dokumentoutput == &quot;email&quot;">
  <!-- Email-only content -->
</tr>
```

#### Sale vs rental branching

```html
<span vitec-if="!Model.oppdrag.type.Contains(&quot;tleie&quot;)">Selger</span>
<span vitec-if="Model.oppdrag.type.Contains(&quot;tleie&quot;)">Utleier</span>
```

### Known failure modes

1. **Missing `&quot;` escaping** — Using raw `"` inside attribute values breaks HTML parsing. The browser/renderer sees the attribute value as terminated early.
2. **Using `>` instead of `&gt;`** — Numeric comparisons with `>` will be interpreted as HTML tag closing, corrupting the element structure.
3. **Norwegian characters without `\x` escaping** — Comparing against strings containing æ, ø, or å without proper `\x` escapes causes the condition to never match.

---
