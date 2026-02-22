## 12. Conversion Checklist

This checklist is for the Word-to-HTML Conversion Agent (Agent 2). Follow each step mechanically. All rules referenced below are defined in this document.

### A. Template Shell

- [ ] Content is wrapped in `<div class="proaktiv-theme" id="vitecTemplate">...</div>` (both class and id required)
- [ ] `<span vitec-template="resource:Vitec Stilark">&nbsp;</span>` is present as the first child of the wrapper div
- [ ] The resource span contains `&nbsp;` (not empty)

### B. Table Structure

- [ ] All layout uses `<table>` elements (not CSS flexbox/grid)
- [ ] Outer table has `style="width:21cm; table-layout:fixed"` for A4 templates
- [ ] All `<tr>` elements are inside `<tbody>`, `<thead>`, or `<tfoot>` (never directly inside `<table>`)
- [ ] Column spans use the 100-unit system (e.g. `colspan="30"` + `colspan="70"` = 100)
- [ ] Nested tables inside `<td>` cells have `style="table-layout:fixed; width:100%"`
- [ ] No `<table>` elements are self-closing or empty

### C. Inline Styles

- [ ] No `font-family` in inline styles (Stilark handles this)
- [ ] No `font-size` in inline styles unless intentionally overriding (e.g. footer at `8pt`)
- [ ] No `color` or `background-color` in inline styles unless specifically required
- [ ] Preserved structural styles only: `width`, `height`, `margin`, `padding`, `border`, `text-align`, `vertical-align`, `display`, `float`, `table-layout`, `position`, `page-break-*`
- [ ] All dimensions use `cm` units for print measurements (not `px`, `em`, `rem`)

### D. Merge Fields

- [ ] All merge fields use `[[field.path]]` syntax with double square brackets
- [ ] Required fields use `[[*field.path]]` with asterisk prefix
- [ ] Field paths match documented paths in `.cursor/vitec-reference.md`
- [ ] Image sources use `@Model.field` or `[[field]]` syntax in `src` attribute
- [ ] No spaces inside brackets: `[[field.name]]` not `[[ field.name ]]`

### E. Conditional Logic (vitec-if)

- [ ] All string values in comparisons use `&quot;` for quotes
- [ ] All `>` comparisons use `&gt;` HTML entity
- [ ] All `<` comparisons use `&lt;` HTML entity
- [ ] All `&&` logical AND uses `&amp;&amp;`
- [ ] Lambda arrows in `.Where()` and `.Any()` use `=&gt;`
- [ ] Norwegian characters (æ, ø, å) in comparisons use `\x` escapes (`\xE6`, `\xF8`, `\xE5`, `\xC6`, `\xD8`, `\xC5`)
- [ ] Top-level expressions reference `Model.` prefix; loop variable expressions omit it (e.g. `selger.ergift`)
- [ ] `vitec-if` is placed on an appropriate container element (`<span>`, `<em>`, `<p>`, `<div>`, `<tr>`, `<tbody>`, `<table>`, `<article>`, `<li>`)

### F. Iteration (vitec-foreach)

- [ ] Foreach uses `<tbody>` as container for table rows
- [ ] Loop variable name is descriptive and consistent
- [ ] Inner merge fields reference the loop variable (e.g. `[[*selger.navn]]`), not `Model.`
- [ ] Collection guards present: `vitec-if="Model.collection.Count &gt; 0"` before foreach
- [ ] Empty state message present: `vitec-if="Model.collection.Count == 0"` with "Ingen registrert" or similar
- [ ] Nested foreach correctly references parent loop variable for sub-collections

### G. Images and SVG

- [ ] All `<img>` elements have `alt` attribute (even if empty: `alt=""`)
- [ ] Logo images have `max-height` and `max-width` constraints
- [ ] SVG checkboxes/radios use the documented `.svg-toggle` CSS class pattern
- [ ] `<figure>` and `<figcaption>` used for captioned images
- [ ] No inline base64 images larger than necessary (use `$.SKALER()` for scaled versions)

### H. Form Elements

- [ ] `data-label` on `<td>` elements has corresponding CSS for `::before` pseudo-element
- [ ] `data-choice` on `<td>` elements has corresponding CSS for `::after` pseudo-element (if used)
- [ ] Combined `data-label` + `data-choice` cells have appropriate padding (16px top and bottom)
- [ ] `contenteditable="false"` used on non-editable rows (form numbers, static text)
- [ ] `span.insert` elements have `data-label` attribute with placeholder text
- [ ] Form tables use `class="form-table"` for bordered layout
- [ ] Checkbox layouts use `class="checkbox-table"` (not `form-table`)

### I. Text and Formatting

- [ ] No `<font>` tags (unwrap to plain content)
- [ ] No `<center>` tags (use `text-align: center` instead)
- [ ] `<strong>` for bold, `<em>` for italic (not inline `font-weight`/`font-style`)
- [ ] `<small>` for reduced text (e.g. footnotes, form numbers)
- [ ] `&nbsp;` used for intentional non-breaking spaces (not as content filler)
- [ ] Norwegian characters preserved as HTML entities where needed (`&aelig;`, `&oslash;`, `&aring;`)

### J. Contract-Specific (Kjøpekontrakt, Oppdragsavtale)

- [ ] Uses `<article class="item">` for auto-numbered sections (not `<div>`)
- [ ] CSS counters use the **Chromium-safe** dual-counter pattern (`section`/`subsection`), NOT `counters(item, ".")`
- [ ] Top-level `<article class="item">` contains `<h2>` (numbered "1. ", "2. ", ...)
- [ ] Nested `<article class="item">` contains `<h3>` (numbered "1.1. ", "1.2. ", ...)
- [ ] `<article>` has `padding-left: 26px`; nested `<article article>` has `padding-left: 0`
- [ ] `h2::before` has `display: inline-block; width: 26px;` (double-digit section number alignment)
- [ ] `h2` has `margin-left: -26px` matching article `padding-left` (heading/body text alignment)
- [ ] Eieform-conditional sections use `vitec-if` directly on `<article>` or `<div>`
- [ ] Internal cross-references use `<a id="section-name"></a>` anchors + `<a class="bookmark" href="#section-name">` links
- [ ] `roles-table` class on party-listing tables with `tbody:last-child tr:last-child td { display: none }` CSS
- [ ] Inline toggles (boligkjøperforsikring) use `<p data-toggle="buttons">` with `<label class="btn">` containing SVG toggles
- [ ] Signature block uses nested `vitec-foreach` inside `<td>` with `border-bottom: solid 1px #000000; height: 40px` for signing lines
- [ ] `span.insert` placeholders used for dates and amounts that the user fills in manually
- [ ] `.avoid-page-break` class applied to sections that must not split across pages

### K. Final Validation

- [ ] **FIRST: Verify this is NOT a protected Kartverket template (Section 14) — if it is, DO NOT proceed with any changes**
- [ ] HTML is well-formed (all tags properly closed)
- [ ] No JavaScript event handlers (`onclick`, `onload`, etc.)
- [ ] No external stylesheet links (only Stilark resource reference)
- [ ] Template renders correctly when Stilark CSS is applied
- [ ] All `vitec-if` expressions are syntactically valid (test with simple true/false)
- [ ] All `vitec-foreach` collections are listed in the known collections table (Section 4)

---
