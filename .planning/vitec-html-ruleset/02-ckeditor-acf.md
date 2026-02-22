## 2. CKEditor 4 Compatibility Rules

Vitec Next uses CKEditor 4 as its template editor. CKEditor 4's Advanced Content Filter (ACF) strips or rewrites HTML it considers invalid unless the Vitec installation has configured `extraAllowedContent` rules.

### How ACF works

By default, CKEditor 4 only allows HTML elements and attributes that are registered by loaded plugins. Non-standard attributes are stripped. Vitec Next must configure CKEditor's ACF to allow its custom attributes — and the evidence from production templates confirms that it does.

### Confirmed safe elements

These elements appear in production templates and survive CKEditor editing:

| Element | Status | Evidence |
|---------|--------|----------|
| `<div>` | **Safe** | Used as root wrapper and structural containers throughout |
| `<p>` | **Safe** | Standard text paragraphs |
| `<span>` | **Safe** | Used extensively for conditional content and styling |
| `<table>`, `<tbody>`, `<thead>`, `<tfoot>`, `<tr>`, `<th>`, `<td>` | **Safe** | Primary layout mechanism in all templates |
| `<strong>`, `<em>` | **Safe** | Inline formatting |
| `<small>` | **Safe** | Used for reduced-size annotations and footer text |
| `<br>` | **Safe** | Line breaks |
| `<ul>`, `<ol>`, `<li>` | **Safe** | List structures; `<ul>` used with `vitec-foreach` (line 1961) |
| `<img>` | **Safe** | Images with `src`, `alt`, `style`, `class` attributes |
| `<figure>`, `<figcaption>` | **Safe** | Image containers with captions (lines 6241–6292) |
| `<a>` | **Safe** | Hyperlinks and internal bookmark anchors; `<a id="section-name"></a>` for targets, `<a class="bookmark" href="#section-name">` for links (Evidence: Kjøpekontrakt FORBRUKER) |
| `<u>` | **Safe** | Underline text within contract clauses (Evidence: Kjøpekontrakt FORBRUKER) |
| `<h1>`–`<h5>` | **Safe** | Headings; `<h1>`, `<h2>`, `<h3>` used extensively. `<h2>` confirmed in contract templates (DB evidence: "Kjøpekontrakt FORBRUKER", "Oppdragsavtale") |
| `<article>` | **Safe** | Structural container for numbered sections in contracts. Used with `class="item"` for CSS counter auto-numbering. (DB evidence: "Kjøpekontrakt FORBRUKER", "Kjøpekontrakt AS-IS", "Oppdragsavtale") |
| `<label>` | **Safe** | Used for SVG checkbox/radio toggles (lines 6175–6210) |
| `<input>` | **Safe** | Radio buttons inside label toggles (lines 6179–6207) |
| `<button>` | **Safe** | Version toggle button (line 273) |
| `<code>` | **Safe** | Inline code display (line 6161) |
| `<style>` | **Safe** | Embedded CSS blocks (lines 2–272) |
| `<sup>` | **Safe** | Superscript; `&sup2;` used for m² |

### Confirmed safe custom attributes

These non-standard attributes survive in production templates, proving Vitec's CKEditor configuration allows them:

| Attribute | Used on | Purpose | Evidence |
|-----------|---------|---------|----------|
| `vitec-template` | `<span>` | Resource inclusion (Stilark) | Every template's shell |
| `vitec-if` | `<span>`, `<em>`, `<table>`, `<tbody>`, `<tr>`, `<div>`, `<ul>` | Conditional rendering | 118+ instances in Alle-flettekoder |
| `vitec-foreach` | `<tbody>`, `<table>`, `<ul>`, `<div>` | Iteration/loops | 50+ instances in Alle-flettekoder |
| `data-label` | `<td>`, `<span>` | Floating label via CSS `::before` | 7 instances in Alle-flettekoder (form-table pattern) |
| `data-version` | `<tr>`, `<td>` | Version tagging with visual badge | 100 instances in Alle-flettekoder |
| `data-toggle` | `<tr>`, `<label>`, `<button>` | Bootstrap-style toggle behaviour | Lines 6177, 6175, 273 |
| `data-choice` | `<td>` | Floating choice/selection label below cell content via CSS `::after`. Used in form templates alongside `data-label`. | (DB evidence: 41 templates including "Skjøte", "Akseptbrev kjøper", "Oppgjørsskjema kjøper") |
| `data-target` | `<button>`, `<a>` | Bootstrap collapse/expand target reference | (DB evidence: "Aksjeeierbok (Næring)", "Eierskiftemelding grunneier") |
| `contenteditable` | `<label>`, `<tr>` | Prevents editing of specific elements | Lines 289, 6175–6210 |
| `colspan` | `<td>`, `<th>` | Column spanning in tables | Pervasive |
| `rowspan` | `<td>` | Row spanning in tables | Line 6188 |
| `cellspacing` | `<table>` | Legacy spacing removal (`cellspacing="0"`) | (DB evidence: "Vitec Bunntekst") |

### Elements and patterns CKEditor 4 typically strips (by default)

Without explicit ACF configuration, CKEditor 4 would strip:

| Pattern | Default behaviour | Vitec override |
|---------|-------------------|----------------|
| Custom attributes (`vitec-if`, `vitec-foreach`) | **Stripped** | Vitec configures `extraAllowedContent` to allow these |
| `<input>` elements | **Stripped** unless forms plugin loaded | Allowed in Vitec — used inside `<label>` toggles |
| `<button>` elements | **Stripped** unless explicitly allowed | Allowed — version toggle button |
| `<style>` blocks | **Preserved** if `allowedContent` includes them | Present in production templates |
| `<font>` tags | **May be generated** by CKEditor (legacy) | Should be unwrapped; sanitizer already handles this |
| `<center>` tags | **May be preserved** from legacy content | Should be unwrapped; sanitizer handles this |

### CKEditor 4 capabilities beyond current Vitec usage

Based on CKEditor 4's built-in plugins and ACF system, these capabilities exist but are not observed in Vitec templates:

| Capability | CKEditor 4 support | Current Vitec usage |
|------------|--------------------|--------------------|
| `<blockquote>` | Yes (blockquote plugin) | Not used in any observed template |
| `<pre>` | Yes (format plugin) | Not used |
| `<iframe>` | Yes (iframe plugin, if loaded) | Not used |
| `<video>`, `<audio>` | Via plugins | Not used |
| `<dl>`, `<dt>`, `<dd>` | Yes | Not used |
| `<abbr>` | Via plugin | Not used |
| `<sub>` | Yes (basicstyles plugin) | Not used (only `<sup>` seen) |
| Custom `data-*` attributes | Yes via `extraAllowedContent: '*[data-*]'` | `data-label`, `data-version`, `data-toggle`, `data-choice`, `data-target` observed |
| CSS classes on any element | Yes via ACF | Extensive usage — see Section 7 for full list. 100+ distinct CSS classes observed across 133 database templates. |
| `style` attribute on any element | Yes via ACF | Extensively used for structural inline styles |

### CKEditor rewriting behaviour

CKEditor 4 is known to:

1. **Add `&nbsp;` to empty elements** — Empty `<td>`, `<p>`, `<div>` elements may get `&nbsp;` inserted. This is generally harmless.
2. **Normalize self-closing tags** — `<br />` may become `<br>`, `<img ... />` may become `<img ...>`. Both are valid HTML5.
3. **Reformat whitespace** — Indentation and line breaks in source may be altered. Do not rely on specific whitespace formatting.
4. **Merge adjacent identical inline elements** — Two adjacent `<strong>` tags may be merged into one.
5. **Convert entities** — Some character references may be converted between named and numeric forms.

---
