## 6. Table Patterns

Tables are the primary layout mechanism in Vitec templates.

### Standard table structure

```html
<table style="table-layout:fixed; width:21cm">
  <tbody>
    <tr>
      <td colspan="30">Label</td>
      <td colspan="70">[[field.value]]</td>
    </tr>
  </tbody>
</table>
```

### Column spanning convention

Vitec templates use a 100-unit colspan system. Columns are expressed as percentages:

| Pattern | Usage | Evidence |
|---------|-------|----------|
| `30/70` | Label + value | Most common; lines 297–425 |
| `100` | Full-width section headers | Lines 292–293, 355–356 |
| `20/80` | Narrow label + wide value | Lines 503–517 |
| `25/25/25/25` | Four equal columns | Lines 6239–6282 (images) |
| `30/40/30` | Three-column footer | `vitec-reference.md` line 635 |
| `25/75` | Two-column with wider right | Lines 6222–6223 |
| `33/34/33` | Three roughly equal columns | Line 6226–6228 |
| `30/35/35` | Label + two-choice radio | Lines 6178–6180 |
| `75/25` | Wide left + narrow right | Line 6222 |
| `50/50` | Half-and-half | Lines 1841, 1850 |

### Multiple `<tbody>` sections

A single `<table>` can contain multiple `<tbody>` elements. This is valid HTML and is the standard Vitec pattern for grouping rows:

```html
<table>
  <thead>
    <tr><th colspan="100"><h1>Title</h1></th></tr>
  </thead>
  <tfoot>
    <tr><th colspan="100">Footer</th></tr>
  </tfoot>
  <tbody>
    <tr><td colspan="100"><h3>Section 1</h3></td></tr>
    <!-- rows -->
  </tbody>
  <tbody>
    <tr><td colspan="100"><h3>Section 2</h3></td></tr>
    <!-- rows -->
  </tbody>
</table>
```

**Evidence:** The entire Alle-flettekoder template uses this structure — one `<table>` with `<thead>`, `<tfoot>`, and many `<tbody>` sections.

### `<tbody>` as foreach container

When iterating table rows, `vitec-foreach` goes on the `<tbody>`:

```html
<table>
  <tbody vitec-foreach="selger in Model.selgere">
    <tr>
      <td colspan="30">[[*selger.navn]]</td>
      <td colspan="70">[[*selger.fodselsnr]]</td>
    </tr>
  </tbody>
</table>
```

This creates a new `<tbody>` for each iteration, which is valid HTML.

### Nested tables

Tables can be nested inside `<td>` cells:

```html
<tr>
  <td colspan="70">
    <table vitec-if="Model.kjopere.Count &gt; 0">
      <tbody vitec-foreach="kjoper in Model.kjopere">
        <tr><td>[[*kjoper.navn]]</td></tr>
      </tbody>
    </table>
  </td>
</tr>
```

**Evidence:** Lines 500–522, 1820–1955.

### `form-table` class pattern

The `form-table` class creates bordered form-like tables:

```html
<table class="form-table">
  <tbody>
    <tr>
      <td colspan="75" data-label="Adresse">[[eiendom.gatenavnognr]]</td>
      <td colspan="25" data-label="Oppdragsnr.">[[oppdrag.nr]]</td>
    </tr>
  </tbody>
</table>
```

CSS rules for `form-table`:
```css
#vitecTemplate .form-table {
    border-top: solid 1px #000;
}
#vitecTemplate .form-table td {
    border: solid 1px #000;
}
#vitecTemplate .form-table td p {
    margin: 0;
    padding: 0;
}
```

**Evidence:** Lines 80–91 (CSS), line 6219 (usage).

### Table attributes

| Attribute | Values observed | Purpose |
|-----------|----------------|---------|
| `style="table-layout:fixed"` | On outer tables | Prevents column width from depending on content |
| `style="width:21cm"` | On outer tables | A4 page width |
| `style="width:100%"` | On nested tables | Fill parent container |
| `cellspacing="0"` | On some tables | Legacy spacing removal |
| `border-collapse:collapse` | Via Stilark CSS | Default for all tables under `#vitecTemplate` |
| `colspan` | Numeric (1–100) | Column spanning |
| `rowspan` | Numeric | Row spanning (line 6188) |

### Page break control

Page breaks are controlled via CSS properties and a dedicated CSS class. Observed in **52 database templates**:

| Pattern | CSS | Usage | Evidence |
|---------|-----|-------|----------|
| Prevent break inside | `page-break-inside: avoid` | On sections that should not split across pages | Most common (45+ templates) |
| Force break after | `page-break-after: always` | Between major document sections | "Akseptbrev kjøper", "Seksjoneringsbegjæring" |
| Force break before | `page-break-before: always` | Before new sections | "Hjemmelsoverføring" |
| CSS class | `.avoid-page-break` | Same as inline `page-break-inside: avoid` | "Kjøpekontrakt FORBRUKER", "Oppdragsavtale" |

Applied via inline style:
```html
<div style="page-break-inside:avoid">
  <!-- Content that must stay on one page -->
</div>
```

Or via CSS class:
```html
<article class="avoid-page-break item">
  <!-- Contract section -->
</article>
```

Also applied at the table/row level:
```html
<table style="page-break-inside:avoid">
#vitecTemplate table tr { page-break-inside: avoid; }
```

**(DB evidence: 52 templates use page-break patterns)**

### Empty table hiding

Tables that render empty (e.g., when a foreach produces no iterations) can be hidden:

```css
#vitecTemplate table:empty {
    display: none;
}
```

**(DB evidence: "Forslag til fordelingskjennelse (Tvangssalg)")**

### Known table issues in CKEditor

CKEditor 4 has opinions about tables:

1. **Empty cells** — CKEditor may insert `&nbsp;` into empty `<td>` elements. This is harmless.
2. **Table structure validation** — CKEditor validates `<table>` → `<tbody>`/`<thead>`/`<tfoot>` → `<tr>` → `<td>`/`<th>` hierarchy. Elements out of this order may be restructured.
3. **Missing `<tbody>`** — CKEditor may add `<tbody>` wrapper if rows are directly inside `<table>`.

---
