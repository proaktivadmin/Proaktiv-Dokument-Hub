## 11. Known Failure Modes

### 1. Unescaped quotes in vitec-if values

**Symptom:** Conditional never matches, or HTML structure breaks.

**Cause:** Using `"` instead of `&quot;` inside attribute values:
```html
<!-- BROKEN -->
<span vitec-if="Model.eiendom.eieform == "Andel"">text</span>
```

**Fix:** Always use `&quot;`:
```html
<span vitec-if="Model.eiendom.eieform == &quot;Andel&quot;">text</span>
```

### 2. Unescaped `>` in numeric comparisons

**Symptom:** HTML parser interprets `>` as end of attribute/tag. Everything after the `>` renders as plain text or is lost.

**Cause:** Using `>` instead of `&gt;`:
```html
<!-- BROKEN -->
<table vitec-if="Model.kjopere.Count > 0">
```

**Fix:**
```html
<table vitec-if="Model.kjopere.Count &gt; 0">
```

### 3. Norwegian characters in comparisons without \x escaping

**Symptom:** Conditional never matches even when the data contains the expected Norwegian word.

**Cause:** Using literal æ/ø/å in vitec-if expressions:
```html
<!-- MAY NOT MATCH -->
<span vitec-if="Model.eiendom.grunntype == &quot;Næring&quot;">
```

**Fix:** Use `\x` escape sequences:
```html
<span vitec-if="Model.eiendom.grunntype == &quot;N\xE6ring&quot;">
```

### 4. Missing `&nbsp;` in Stilark resource reference

**Symptom:** Stilark CSS not loaded; template renders without styling.

**Cause:** Empty resource span:
```html
<!-- BROKEN -->
<span vitec-template="resource:Vitec Stilark"></span>
```

**Fix:** Must contain `&nbsp;`:
```html
<span vitec-template="resource:Vitec Stilark">&nbsp;</span>
```

### 5. Missing `#vitecTemplate` wrapper

**Symptom:** No Stilark CSS selectors match. Template renders with browser defaults (Times New Roman, etc.).

**Cause:** Content not wrapped in `<div id="vitecTemplate">`.

**Fix:** Always wrap content in the required shell (see Section 1).

### 6. Lambda arrow in foreach filter not HTML-escaped

**Symptom:** `.Where()` filter does not work; may cause render error.

**Cause:** Using `=>` instead of `=&gt;`:
```html
<!-- BROKEN -->
<tbody vitec-foreach="x in Model.list.Where(i => i.code == &quot;X&quot;)">
```

**Fix:**
```html
<tbody vitec-foreach="x in Model.list.Where(i =&gt; i.code == &quot;X&quot;)">
```

### 7. Inline font/color styles fighting Stilark

**Symptom:** Text appears in wrong font or colour; inconsistent rendering across templates.

**Cause:** Inline `font-family`, `font-size`, `color` styles override Stilark. When templates are mixed (e.g., pasted from Word), some elements have inline styles and others don't.

**Fix:** Strip all non-structural inline styles. Use the sanitizer's `PRESERVE_STYLES` list as the reference for what to keep.

### 8. CKEditor stripping custom attributes after re-editing

**Symptom:** `vitec-if` or `vitec-foreach` attributes disappear after saving in CKEditor.

**Cause:** CKEditor's ACF was not configured to allow these attributes, or the configuration was changed between editing sessions.

**Mitigation:** Always verify `vitec-if` and `vitec-foreach` attributes are present after any CKEditor editing session. Vitec's CKEditor configuration should include:
```javascript
extraAllowedContent: '*[vitec-if,vitec-foreach,vitec-template,data-label,data-version,data-toggle,contenteditable]'
```

### 9. `<table>` with direct `<tr>` children (no `<tbody>`)

**Symptom:** CKEditor may restructure the table by adding implicit `<tbody>`.

**Cause:** Browsers and CKEditor both auto-insert `<tbody>` around `<tr>` elements that are direct children of `<table>`. This can break vitec-foreach if the foreach was placed on an element that gets wrapped.

**Fix:** Always explicitly include `<tbody>` in table structures.

### 10. Missing `proaktiv-theme` class on wrapper div

**Symptom:** Company-specific CSS overrides do not apply. Template may render with slightly different styling.

**Cause:** Using only `id="vitecTemplate"` without `class="proaktiv-theme"`:
```html
<!-- INCOMPLETE -->
<div id="vitecTemplate">
```

**Fix:** Always include both:
```html
<div class="proaktiv-theme" id="vitecTemplate">
```

**(DB evidence: All 133 templates use this pattern)**

### 11. `&&` not escaped in HTML attributes

**Symptom:** Logical AND in vitec-if or Where lambda does not work; expression may be truncated.

**Cause:** Using `&&` instead of `&amp;&amp;` inside HTML attributes:
```html
<!-- BROKEN -->
<span vitec-if="Model.a == true && Model.b == false">
```

**Fix:**
```html
<span vitec-if="Model.a == true &amp;&amp; Model.b == false">
```

**(DB evidence: 23 templates use `&amp;&amp;` including "Kjøpekontrakt FORBRUKER", "Oppdragsavtale")**

### 12. `counters()` CSS function breaks in Chromium PDF renderer

**Symptom:** Auto-numbered contract sections (h2/h3) display wrong numbers — subsections restart at unexpected points, or all sections show "1." regardless of nesting depth.

**Cause:** The default Vitec template uses:
```css
#vitecTemplate .item { counter-increment: item; }
#vitecTemplate .item h2:before,
#vitecTemplate .item h3:before { content: counters(item, ".") ". "; }
```
The `counters()` function relies on CSS counter scope inheritance, which Chromium-based PDF renderers handle incorrectly when `counter-reset` and `counter-increment` interact across nested `article.item` elements.

**Fix:** Replace with two explicit counters and `:not()` selectors:
```css
#vitecTemplate { counter-reset: section; }
#vitecTemplate article.item:not(article.item article.item) {
    counter-increment: section;
    counter-reset: subsection;
}
#vitecTemplate article.item article.item {
    counter-increment: subsection;
}
#vitecTemplate article.item:not(article.item article.item) h2::before {
    content: counter(section) ". ";
    display: inline-block;
    width: 26px;
}
#vitecTemplate article.item article.item h3::before {
    content: counter(section) "." counter(subsection) ". ";
    display: inline-block;
    width: 36px;
}
```

**(Evidence: Proaktiv custom Kjøpekontrakt FORBRUKER — production fix)**

### 12b. Double-digit section numbers misalign heading text with body text

**Symptom:** Sections 1-9 have heading text ("HEADING") aligned with body text below. Sections 10+ have heading text pushed to the right, creating a visible misalignment in the rendered PDF.

**Cause:** The CSS `::before` pseudo-element rendering the counter number has variable width. "1. " is ~15px wide, but "10. " is ~23px. With `article { padding-left: 20px; }` and `h2 { margin-left: -20px; }`, single-digit numbers fit within the 20px indent, but double-digit numbers push past it.

**Fix:** Give `::before` a fixed width and increase the indent to accommodate double digits:
```css
#vitecTemplate article { padding-left: 26px; }
#vitecTemplate h2 { margin: 30px 0 0 -26px; }
#vitecTemplate article.item:not(article.item article.item) h2::before {
    content: counter(section) ". ";
    display: inline-block;
    width: 26px;
}
```

The `display: inline-block; width: 26px;` creates a fixed-width column for the number. The article `padding-left` and h2 `margin-left` must both be 26px so heading text starts at the same horizontal position as body text.

**(Evidence: Proaktiv Kjøpekontrakt prosjekt leilighet v3 — 20 sections with visible misalignment at section 10+)**

### 13. `@media` in CSS inside Razor-processed templates

**Symptom:** CSS `@media print` block is silently eaten or causes Razor compilation error. Print styles don't work.

**Cause:** The `@` symbol in `@media` is intercepted by Vitec's Razor engine as a code directive.

**Fix:** Escape `@` using Razor's `@("@")` syntax:
```css
/* BROKEN — Razor interprets @media as code */
@media print { .screen-help { display: none; } }

/* FIXED — Razor outputs literal @ */
@("@")media print { .screen-help { display: none; } }
```

**(Evidence: Kjøpekontrakt Næring production template)**

---
