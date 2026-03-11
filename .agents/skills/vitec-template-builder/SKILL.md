---
name: vitec-template-builder
description: Build production-ready Vitec Next HTML contract templates with flettekoder (merge fields), vitec-if conditionals, and vitec-foreach loops. Use when creating, converting, or editing Vitec document templates, kjøpekontrakter, or any template that uses [[field]] syntax, vitec-if, vitec-foreach, or the vitecTemplate shell. Also applies when converting Word .htm exports to Vitec-compliant HTML.
---

# Vitec Template Builder

## Template Shell (always required)

Every template must be wrapped in this exact shell:

```html
<div class="proaktiv-theme" id="vitecTemplate">
<span vitec-template="resource:Vitec Stilark">&nbsp;</span>
<style type="text/css">
#vitecTemplate { counter-reset: section; }
#vitecTemplate article.item:not(article.item article.item) {
  counter-increment: section;
  counter-reset: subsection;
}
#vitecTemplate article.item article.item { counter-increment: subsection; }
#vitecTemplate article.item:not(article.item article.item) > h2::before {
  content: counter(section) ". ";
}
#vitecTemplate article.item article.item > h3::before {
  content: counter(section) "." counter(subsection) ". ";
}
#vitecTemplate article { padding-left: 20px; }
#vitecTemplate article article { padding-left: 0; }
#vitecTemplate .avoid-page-break { page-break-inside: avoid; }
#vitecTemplate .roles-table { width: 100%; table-layout: fixed; border-collapse: collapse; }
#vitecTemplate .roles-table th { text-align: left; padding: 4px 6px; border-bottom: 1px solid #000; }
#vitecTemplate .roles-table td { padding: 4px 6px; vertical-align: top; }
#vitecTemplate .roles-table tbody:last-child tr:last-child td { display: none; }
#vitecTemplate .costs-table { width: 100%; table-layout: fixed; border-collapse: collapse; }
#vitecTemplate .costs-table td { padding: 2px 6px; vertical-align: top; }
#vitecTemplate .costs-table tr.sum-row td { border-top: 1px solid #000; font-weight: bold; }
#vitecTemplate .insert { border-bottom: 1px dotted #999; min-width: 80px; display: inline-block; }
</style>

<!-- template content here -->

</div>
```

The `<span vitec-template="resource:Vitec Stilark">&nbsp;</span>` must appear immediately after the opening `<div>` — it loads Proaktiv's brand stylesheet.

---

## Merge Fields (Flettekoder)

| Pattern | Use |
|---------|-----|
| `[[field.name]]` | Standard merge field |
| `[[*item.field]]` | Loop variable (inside `vitec-foreach`) |
| `$.UD([[field]])` | Format number with thousand separators |

**Rules:**
- No spaces inside brackets: `[[field.name]]` not `[[ field.name ]]`
- Loop variables always prefixed with `*`: `[[*selger.navn]]`

**Common fields:**
```
[[oppdrag.nr]]                    [[kontrakt.formidling.nr]]
[[kontrakt.kjopesum]]             [[kontrakt.kjopesumibokstaver]]
[[kontrakt.klientkonto]]          [[kontrakt.kid]]
[[kontrakt.totaleomkostninger]]   [[kontrakt.kjopesumogomkostn]]
[[kontrakt.overtagelse.dato]]     [[dagensdato]]
[[eiendom.kommunenavn]]           [[eiendom.leilighetsnr]]
[[eiendom.fellesutgifter]]        [[komplettmatrikkel]]
[[meglerkontor.navn]]
[[oppgjor.kontornavn]]            [[oppgjor.besoksadresse]]
[[oppgjor.besokspostnr]]          [[oppgjor.besokspoststed]]
[[oppgjor.kontortlf]]             [[oppgjor.kontorepost]]
```

---

## Conditional Logic (vitec-if)

`vitec-if` is an HTML attribute — always on the element that should show/hide.

**Escaping rules (mandatory):**
- String quotes → `&quot;`
- `>` → `&gt;`
- `&&` → `&amp;&amp;`
- `||` → `&amp;&amp;` (use `||` in logic, escape as `&#124;&#124;` if needed)

**Patterns:**
```html
<!-- Show/hide element -->
<p vitec-if="Model.eiendom.heftelserogrettigheter != &quot;&quot;">
  [[eiendom.heftelserogrettigheter]]
</p>

<!-- Checkbox pattern (checked/unchecked) -->
<span vitec-if="Model.eiendom.grunntype == &quot;Bolig&quot;">&#9745;</span>
<span vitec-if="Model.eiendom.grunntype != &quot;Bolig&quot;">&#9744;</span>

<!-- Count guard -->
<table vitec-if="Model.selgere.Count &gt; 0">...</table>

<!-- Boolean flag -->
<p vitec-if="Model.oppdrag.prosjekt.erutbyggersforbeholdbyggelaan == true">...</p>

<!-- Compound condition -->
<span vitec-if="(selger.tlf != &quot;&quot; &amp;&amp; selger.emailadresse != &quot;&quot;)"> / </span>
```

**Conditional date sections:**
```html
<div vitec-if="Model.kontrakt.overtagelse.dato != &quot;Mangler data&quot;">
  <p>Overtas den <strong>[[kontrakt.overtagelse.dato]]</strong></p>
</div>
<div vitec-if="Model.kontrakt.overtagelse.dato == &quot;Mangler data&quot;">
  <p>Forventet ferdigstillelse: <span class="insert">&nbsp;</span></p>
</div>
```

---

## Loops (vitec-foreach)

`vitec-foreach` goes on `<tbody>` — always guard the parent `<table>` with a count check.

```html
<!-- Parties table (selgere / kjøpere) -->
<table class="roles-table" vitec-if="Model.selgere.Count &gt; 0">
<thead>
<tr>
  <th colspan="34"><strong>Navn</strong></th>
  <th colspan="48"><strong>Adresse</strong></th>
  <th colspan="18"><strong>[[selger.ledetekst_fdato_orgnr]]</strong></th>
</tr>
</thead>
<tbody vitec-foreach="selger in Model.selgere">
<tr>
  <td colspan="34">[[*selger.navnutenfullmektigogkontaktperson]]</td>
  <td colspan="48">[[*selger.gatenavnognr]], [[*selger.postnr]] [[*selger.poststed]]</td>
  <td colspan="18">[[*selger.fdato_orgnr]]</td>
</tr>
<tr>
  <td colspan="100">
    <span vitec-if="selger.tlf != &quot;&quot;">Mob: [[*selger.tlf]]</span>
    <span vitec-if="(selger.tlf != &quot;&quot; &amp;&amp; selger.emailadresse != &quot;&quot;)"> / </span>
    <span vitec-if="selger.emailadresse != &quot;&quot;">E-post: [[*selger.emailadresse]]</span>
  </td>
</tr>
<tr><td colspan="100">&nbsp;</td></tr>
</tbody>
</table>
```

Available loop collections: `Model.selgere`, `Model.kjopere`, `Model.hjemmelshavere`, `Model.kjoperskostnader.poster`

---

## Table Structure

**100-unit colspan system** — all column widths add up to 100:

```html
<table style="width:100%; table-layout:fixed;">
<tbody>
<tr>
  <td colspan="50">Left half</td>
  <td colspan="50">Right half</td>
</tr>
</tbody>
</table>
```

Common splits: `34/48/18` (3-col party table), `60/10/25/5` (costs), `50/50` (two-col), `40/20/40` (signature).

**Rules:**
- Never use `display:flex` or `display:grid`
- Always wrap `<tr>` in `<tbody>`, `<thead>`, or `<tfoot>`
- No orphan `<tr>` directly inside `<table>`

---

## Section Structure

Contract sections use `<article class="item">` — CSS counters auto-number them:

```html
<article class="item">
<h2>SECTION TITLE</h2>
<p>Content...</p>
</article>

<!-- Subsection inside section -->
<article class="item">
<article class="item">
<h3>Subsection</h3>
</article>
</article>

<!-- Avoid page break on last section (signatures) -->
<article class="item avoid-page-break">
<h2>SIGNATUR</h2>
```

---

## User Fill-in Placeholders

For blanks the broker fills in manually:

```html
<span class="insert">&nbsp;</span>
```

---

## Forbidden Patterns

| Forbidden | Use instead |
|-----------|-------------|
| `display:flex` / `display:grid` | Table layout |
| `<font>` tags | Inherited styles from Stilark |
| `<center>` tags | `style="text-align:center;"` on `<p>` |
| Inline `font-family` | Inherited from Stilark |
| Inline `font-size` | Inherited from Stilark |
| `#field.context¤` (legacy) | `[[field.name]]` |
| `<script>` / `onclick` | Never in templates |
| `<link rel="stylesheet">` | Stilark span handles this |

---

## Word .htm Conversion Workflow

When converting a Word-exported `.htm` file:

1. **Extract** body content between `<body>` tags
2. **Remove** Word classes: all `class="Mso*"` attributes, `lang` attributes
3. **Strip** non-structural inline styles — keep only: `text-align`, `vertical-align`, `border*`, `padding`, `width`, `page-break*`
4. **Unwrap** all `<span>` elements (Word uses spans for formatting)
5. **Unwrap** `<a name="...">` anchors (Word bookmarks)
6. **Unwrap** `<div class="WordSection*">` wrappers
7. **Remove** empty `<p>` and `&nbsp;`-only paragraphs
8. **Map** legacy `#field.context¤` → `[[field.name]]`
9. **Wrap** in vitecTemplate shell
10. **Validate** with `scripts/validate_template.py`

**Run validation after any template build:**
```bash
python scripts/validate_template.py
```

---

## Validation Checklist

Before saving a template, verify:

- [ ] `id="vitecTemplate"` and `class="proaktiv-theme"` on wrapper div
- [ ] Stilark span present with `&nbsp;` content
- [ ] No `display:flex` / `display:grid`
- [ ] No orphan `<tr>` outside `tbody`/`thead`
- [ ] Colspan values sum to 100
- [ ] No inline `font-family` or `font-size`
- [ ] All merge fields use `[[field]]` — no legacy `#field¤`
- [ ] No spaces inside `[[ ]]`
- [ ] All `vitec-if` strings use `&quot;`, `>` uses `&gt;`
- [ ] Each `vitec-foreach` has a `.Count &gt; 0` guard on parent
- [ ] `vitec-foreach` on `<tbody>`, not `<table>` or `<tr>`
- [ ] No `<font>`, `<center>`, `<script>` tags
- [ ] `<article>` open/close tags balanced
- [ ] Norwegian characters (ø, æ, å) as literal UTF-8, not escaped

## Additional Resources

- Build scripts: `scripts/build_production_template.py`, `scripts/build_kjopekontrakt_prosjekt_leilighet.py`
- Validation script: `scripts/validate_template.py`
- Preview generator: `scripts/build_preview.py`
- Output directory: `scripts/converted_html/`
