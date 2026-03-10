## 7. CSS and Styling Rules

### Vitec Stilark — Complete Source (authoritative)

The Vitec Stilark is the **base stylesheet** applied to all templates via the `<span vitec-template="resource:Vitec Stilark">` resource reference. It is injected as an inline `<div>` element:

```html
<div id="vitec-stilark" style="display:inline">
<style type="text/css">
@import url('https://fonts.googleapis.com/css2?family=Open+Sans:wght@300;400;700&display=swap');

html, body {
    margin: 0;
    padding: 0;
    font-size: 10pt;
    line-height: normal;
    font-family: 'Open sans', sans-serif;
}

#vitecTemplate * {
    font-variant-ligatures: none;
}

#editDocumentTemplate #vitec-stilark:after {
    display: block;
    padding: 1cm 1cm 1.5cm 1cm;
    content: "Se kildekode";
    font-size: 26pt;
    font-weight: 400;
    font-family: 'Open sans', sans-serif;
    color: rgba(124, 124, 124, 0.7);
}

#vitecTemplate p,
#vitecTemplate th p,
#vitecTemplate td p {
    font-size: 10pt;
    line-height: normal;
    font-family: 'Open sans', sans-serif;
    margin: 1em 0;
    padding-bottom: 0;
}

#vitecTemplate h1,
#vitecTemplate h2,
#vitecTemplate h3,
#vitecTemplate h4,
#vitecTemplate h5 {
    font-family: 'Open sans', sans-serif;
}

#vitecTemplate table {
    border-collapse: collapse;
    border-spacing: 0;
}

#vitecTemplate table th,
#vitecTemplate table td {
    vertical-align: top;
    font-size: 10pt;
    line-height: normal;
    font-family: 'Open sans', sans-serif;
}

#vitecTemplate table th {
    text-align: left;
}

#vitecTemplate strong {
    font-size: 10pt;
    line-height: normal;
    font-family: 'Open sans', sans-serif;
    font-weight: 700;
}

#vitecTemplate ul li,
#vitecTemplate ol li {
    font-size: 10pt;
    line-height: normal;
    font-family: 'Open sans', sans-serif;
}

#vitecTemplate div {
    font-size: 10pt;
    line-height: normal;
    font-family: 'Open sans', sans-serif;
}

/* "Ikke overstyre font-størrelser satt med CK Editor" */
#vitecTemplate span > strong {
    font-size: inherit;
}
</style>
</div>
```

#### Stilark analysis

The Stilark is intentionally minimal — it is a **font and reset baseline**, not a layout framework. All complex CSS (counters, data-labels, borders, checkbox toggles, etc.) comes from template-specific `<style>` blocks.

**What the Stilark does:**

| Rule | Selector | Effect |
|------|----------|--------|
| Font loading | `@import url(...)` | Loads Open Sans from Google Fonts (weights 300, 400, 700) |
| Body reset | `html, body` | `margin: 0; padding: 0; font-size: 10pt` |
| Ligature prevention | `#vitecTemplate *` | `font-variant-ligatures: none` on all elements |
| Paragraph spacing | `#vitecTemplate p` | `margin: 1em 0; padding-bottom: 0` |
| Heading font | `#vitecTemplate h1–h5` | Font family only — NO font-size override (browser defaults apply) |
| Table reset | `#vitecTemplate table` | `border-collapse: collapse; border-spacing: 0` (no borders by default) |
| Cell alignment | `#vitecTemplate th, td` | `vertical-align: top; text-align: left` (th only for text-align) |
| Bold weight | `#vitecTemplate strong` | `font-weight: 700` |
| CKEditor fix | `#vitecTemplate span > strong` | `font-size: inherit` — prevents Stilark from overriding CKEditor-set font sizes |
| Editor placeholder | `#editDocumentTemplate #vitec-stilark:after` | Shows "Se kildekode" in CKEditor (editor-only, not visible in output) |

**What the Stilark does NOT do:**

- No colors (no `color`, no `background-color`)
- No heading sizes (h1–h5 use browser defaults)
- No border styles (tables have `border-collapse` but no `border`)
- No print-specific styles (no `@media print`)
- No layout widths (no `width: 21cm`)
- No padding/margin on tables or cells
- No CSS classes defined

**Key implication:** All layout, borders, colors, heading sizes, and interactive styles (checkboxes, data-labels, counters) must be provided by template-specific `<style>` blocks. The Stilark only ensures consistent font rendering.

#### Stilark injection mechanism

When rendered, the `<span vitec-template="resource:Vitec Stilark">&nbsp;</span>` is replaced by the Stilark's actual content — a `<div id="vitec-stilark" style="display:inline">` containing a `<style>` block. The `display:inline` ensures the injected div doesn't affect layout.

**(Evidence: Vitec Stilark system template source code, provided by Proaktiv admin)**

### Inline styles — what survives

The project's `SanitizerService` (`backend/app/services/sanitizer_service.py`) defines which inline styles are preserved. These are the **structural** properties that control layout:

| Category | Preserved properties |
|----------|---------------------|
| **Dimensions** | `width`, `height`, `max-width`, `max-height`, `min-width`, `min-height` |
| **Spacing** | `margin`, `margin-top/bottom/left/right`, `padding`, `padding-top/bottom/left/right` |
| **Borders** | `border`, `border-top/bottom/left/right`, `border-collapse`, `border-spacing` |
| **Alignment** | `text-align`, `vertical-align` |
| **Layout** | `display`, `float`, `clear`, `position`, `top/bottom/left/right`, `table-layout` |
| **Page breaks** | `page-break-before`, `page-break-after`, `page-break-inside` |

### Inline styles — what gets stripped

When the sanitizer runs (full strip mode), these are removed because the Stilark handles them:

- `font-family` — Stilark sets Open Sans on all elements
- `font-size` — Stilark sets 10pt; only override where necessary (e.g. `<small>` for 8pt)
- `color` — Let the browser default (black) handle it
- `background-color` — Stripped unless structural
- `font-weight` — Use `<strong>` instead
- `font-style` — Use `<em>` instead
- `line-height` — Stilark sets `normal`

### Inline styles observed in production templates

Despite the sanitizer, production templates in the database already have clean inline styles. Common patterns:

```css
/* Cell padding */
padding: 0 5px;
padding: 16px 2px 5px 4px;
padding-left: 1cm;
padding-right: 1cm;

/* Dimensions */
width: 21cm;
width: 100%;
width: 3cm;
height: 1.5cm;

/* Borders */
border-top: solid 1px #000;
border-top: solid 1px #ededed;
border-style: none;
border-width: 0px;

/* Alignment */
text-align: right;
text-align: center;
text-align: left;
vertical-align: top;
vertical-align: middle;
vertical-align: bottom;

/* Layout */
table-layout: fixed;
float: right;
display: inline-block;
display: inline-table;
display: none;
position: relative;
position: absolute;

/* Image sizing */
max-height: 4cm;
max-width: 4cm;
max-height: 1.5cm;
max-width: 6cm;
```

### CSS classes available

From Alle-flettekoder `<style>` blocks and **133 database templates** (100+ distinct classes observed):

#### Core classes (from Alle-flettekoder)

| Class | Purpose | Defined in |
|-------|---------|-----------|
| `form-table` | Bordered form layout table | Line 80 |
| `insert` | Editable placeholder span | Line 108 |
| `insert-table` | Inline-table wrapper for insert spans | Line 127 |
| `btn` | Bootstrap-style button/label | Line 209 |
| `active` | Active state for toggles | Lines 219, 249 |
| `svg-toggle` | SVG checkbox/radio visual | Line 225 |
| `checkbox` | Checkbox variant of svg-toggle | Line 245 |
| `radio` | Radio variant of svg-toggle | Line 255 |
| `scaled-image` | Circular cropped image (100×100px) | Line 62 |
| `no-border` | Remove borders from cells | `vitec-reference.md` line 850 |

#### Structural/layout classes (from database templates)

| Class | Purpose | Evidence |
|-------|---------|----------|
| `proaktiv-theme` | Company theme on wrapper div | All 133 templates |
| `avoid-page-break` | Prevents page break inside element | "Kjøpekontrakt FORBRUKER" |
| `item` | CSS counter section numbering | "Kjøpekontrakt FORBRUKER", "Oppdragsavtale" |
| `a4-main` | A4 page main content area | Multiple templates |
| `main-table` | Primary layout table | Multiple templates |
| `first-table` / `first-page-table` | First page table styling | Multiple templates |
| `last-table` | Last table special styling | Multiple templates |
| `roles-table` | Party listing table (sellers/buyers) | "Kjøpekontrakt FORBRUKER" |
| `info-table` | Information display table | "Oppdragsavtale" |
| `witness-table` | Witness signature table | Multiple templates |
| `bordered-table` | Table with full borders | Multiple templates |
| `with-nested-table` | Cell containing nested table (padding: 0) | "Skjøte" |

#### Border utility classes

| Class | Purpose | Evidence |
|-------|---------|----------|
| `borders` | Top + bottom borders | "Forslag til fordelingskjennelse" |
| `border-bottom` | Bottom border only | Multiple templates |
| `border-top` | Top border only | Multiple templates |
| `border-left` | Left border | "Søknad om konsesjon" |
| `border-right` | Right border | Multiple templates |
| `sideborders` | Left + right borders | Multiple templates |
| `border-bottom-dotted` | Dotted bottom border | Multiple templates |

#### Alignment utility classes

| Class | Purpose | Evidence |
|-------|---------|----------|
| `vtop` / `vertical-top` | `vertical-align: top` | Multiple templates |
| `vbottom` | `vertical-align: bottom` | Multiple templates |
| `vcenter` | `vertical-align: middle` | Multiple templates |
| `hcenter` | `text-align: center` (horizontal) | Multiple templates |
| `center` | `text-align: center` | Multiple templates |
| `text-right` | `text-align: right` | "Forslag til fordelingskjennelse" |
| `text-center` | `text-align: center` | Multiple templates |

#### Color/background classes

| Class | Purpose | Evidence |
|-------|---------|----------|
| `bg-color` | Header/accent background color | Multiple templates |
| `bg-green` / `bg-green-light` | Green status background | Multiple templates |
| `bg-red` / `bg-red-light` | Red status background | Multiple templates |
| `row-header` | Row header with grey background (`#f2f2f2`) | "Skjøte" |
| `header-cell` | Header cell styling | Multiple templates |

#### Settlement/financial classes

| Class | Purpose | Evidence |
|-------|---------|----------|
| `borderoppgjor` | Settlement row with bottom border | "Oppgjørsoppstilling Selger" |
| `bordersum` | Sum row with top + bottom borders | "Oppgjørsoppstilling Selger" |
| `delsumlinje` | Subtotal row | Multiple templates |
| `sumlinje` | Total row | Multiple templates |
| `mvacell` | VAT cell (italic, lightgray background) | "Oppgjørsoppstilling Selger" |

#### Form/input classes

| Class | Purpose | Evidence |
|-------|---------|----------|
| `checkbox-table` | Checkbox layout table | "Akseptbrev kjøper email" |
| `checkbox-table-one-row` | Single-row checkbox layout | "Akseptbrev kjøper email" |
| `checkbox-row` | Row with extra padding for data-choice | "Skjøte" |
| `sign-field` / `sign-field1` / `sign-fields` | Signature line (inline-block, border-top, 45% width) | "Akseptbrev kjøper email" |
| `insert-box` / `insert-textbox` | Editable input areas | Multiple templates |
| `bold-data-label` | Bold floating label variant | "Skjøte" |
| `add-signature` | Add-signature button area | Multiple templates |

#### List/iteration classes

| Class | Purpose | Evidence |
|-------|---------|----------|
| `liste` | List item wrapper (with `:last-child .separator { display: none }`) | "Forslag til fordelingskjennelse" |
| `separator` | Comma/delimiter hidden on last item | "Oppgjørsoppstilling Selger" |
| `nummerert-liste` | CSS counter auto-numbered paragraph | "Forslag til fordelingskjennelse" |
| `foreach-list` | Foreach loop list container | "Skjøte" |
| `list` | General list styling with vertical padding | "Forslag til fordelingskjennelse" |
| `seller` / `buyer` / `saksokte` | Role-specific list item (same `:last-child .separator` pattern) | "Oppgjørsoppstilling Selger" |

#### Other utility classes

| Class | Purpose | Evidence |
|-------|---------|----------|
| `overskrift1` / `overskrift2` | Heading styles (grey bg, bold) | "Akseptbrev kjøper email" |
| `bookmark` | Internal document link (no underline, italic) | "Kjøpekontrakt FORBRUKER" |
| `collapse` / `collapse-span` | Bootstrap collapsible sections | "Aksjeeierbok (Næring)" |
| `screen-help` / `screen-help-info` | On-screen help buttons (hidden in PDF) | Multiple templates |
| `version` | Version display | Multiple templates |
| `page-info` | Page information area | Multiple templates |
| `small` / `x-small` | Size variants | Multiple templates |
| `bold-text` / `normal-text` | Text weight variants | Multiple templates |
| `indented` | Left-indented content | Multiple templates |
| `part` / `parts` | Party section containers | Multiple templates |
| `related-box` / `info-box` | Information boxes | Multiple templates |
| `inline-flex` | Inline flex display for btn labels | "Kjøpekontrakt FORBRUKER" |

### Custom CSS ID scoping in templates

Some templates use custom element IDs for CSS scoping beyond `#vitecTemplate`:

| ID | Used in | Purpose |
|----|---------|---------|
| `#vitecTemplate` | All templates | Main CSS scope (required) |
| `#vitecHeader` | Custom headers | Inner wrapper for header-specific CSS |
| `#bunntekstTabell` | Footer templates (Oppdragsavtale, custom) | Footer table styling (height, padding, font-size) |
| `#Avsender` | Avsender resource template | Sender block styling (padding-left: 0) |
| `#Mottaker` | Mottaker resource template | Recipient block styling (padding-left: 0) |
| `#vitec-stilark` | Vitec Stilark injection | `display:inline` wrapper for injected CSS (system-generated, not user-created) |

### Google Fonts loading

Self-contained templates (legal footers, custom headers) load fonts via `@import url()`:

```css
@import url('https://fonts.googleapis.com/css2?family=Open+Sans:wght@300;400;700&display=swap');
```

Also seen in Proaktiv custom templates:
```css
@import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@700&family=Open+Sans:wght@400&display=swap');
```

This is used when the template does NOT include the Stilark (which normally provides the base font). The `@import` must appear at the very start of the `<style>` block.

### CSS reset pattern (self-contained templates)

Legal footers and some headers include a full CSS reset:

```css
html, body { margin: 0; padding: 0; }
#vitecTemplate * { font-variant-ligatures: none; }
```

This is only needed when the template does NOT use the Stilark. Do not add this to templates that include `<span vitec-template="resource:Vitec Stilark">` — the Stilark already handles these resets.

### CSS properties to avoid

- `font-variant-ligatures` — Already set by Stilark; do not override
- `font-family` — Already set by Stilark; redundant inline (exception: self-contained templates that don't use Stilark, and email signatures using Calibri)
- `font-size` — Only override when specifically needed (e.g. footer `8pt`)
- Media queries — Not supported in PDF rendering context
- CSS variables — No evidence of usage; avoid
- `!important` — Only used in SVG toggle styles; avoid in template content

---
