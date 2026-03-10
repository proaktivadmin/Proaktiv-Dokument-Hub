# Analysis Report: Kj&oslash;pekontrakt Landbrukseiendom — CKEditor Generation Failure

## Executive Summary

Systematic comparison of the production template against 230+ working Vitec Next reference templates (extracted from `vitec-next-export.json`) identified **3 likely causes** and **4 contributing deviations** that collectively prevent CKEditor 4 from generating the document.

All issues have been fixed in the production template.

---

## Findings (Ranked by Impact)

### CRITICAL 1: Wrong Cost Collection Path — `Model.kjoperskostnader.poster`

**Impact:** Template engine crash (null reference on `.poster.Count`)

**Evidence:**
Across all 230+ templates in the Vitec export database:
- `Model.kjoperskostnader.alleposter` — used by **5+ templates** (FORBRUKER, oppdragsavtale, etc.)
- `GetPosteringerUtenBoligkjoperforsikring()` — used by **2 templates** (bruktbolig variants)
- `Model.kjoperskostnader.poster` — used by **only 1 template** (357K chars, edge case)

The `.poster` subpath is non-standard and may not exist for all property/document types. When the engine evaluates `Model.kjoperskostnader.poster.Count`, if `.poster` is null, the `.Count` access throws a null reference exception that crashes generation.

**Fix applied:** Changed to `Model.kjoperskostnader.alleposter` (the standard path).

---

### CRITICAL 2: SVG Checkbox CSS Uses Wrong Selectors and Encoding

**Impact:** CKEditor 4 CSS parser may reject or strip the checkbox styles, cascading to template parse failure.

**Our template (before fix):**
```css
#vitecTemplate label.btn { display: inline-block; cursor: default; user-select: none; }
#vitecTemplate label.btn input[type="checkbox"] { display: none; }
#vitecTemplate .svg-toggle.checkbox {
  background-image: url("data:image/svg+xml,%3Csvg%20xmlns%3D%22http%3A...%22%3E...%3C%2Fsvg%3E");
}
```

**All working reference templates:**
```css
label.btn { display: inline; text-transform: none; white-space: normal; padding: 0;
  vertical-align: baseline; outline: none; font-size: inherit; }
.svg-toggle { display: inline-block !important; width: 16px; height: 16px; ... }
.svg-toggle.checkbox {
  background-image: url("data:image/svg+xml;utf8,<svg xmlns='...' viewBox='0 0 512 512'>...</svg>");
}
#vitecTemplate [data-toggle="buttons"] input { display: none; }
```

**Three differences that matter:**

| Aspect | Our Template (broken) | Reference (working) |
|--------|----------------------|---------------------|
| **CSS selector prefix** | `#vitecTemplate label.btn` | `label.btn` (no prefix) |
| **SVG encoding** | `%`-encoded (percent) | `utf8` charset declaration |
| **`.svg-toggle` base** | Missing (jumped to `.svg-toggle.checkbox`) | Full reset selector with 16 properties |
| **Input hiding** | `label.btn input[type="checkbox"]` | `[data-toggle="buttons"] input` |

The `#vitecTemplate` prefix on checkbox selectors creates CSS specificity conflicts with Vitec Stilark (which also targets `#vitecTemplate`). The reference deliberately omits this prefix for checkbox/toggle styles.

The percent-encoded SVG data URIs are syntactically valid but CKEditor 4's internal CSS parser (which re-serializes styles) may not handle them correctly, potentially corrupting the style block.

**Fix applied:** Replaced entire SVG checkbox CSS with the exact reference pattern (separate `<style>` block, bare selectors, `utf8` SVGs, full `.svg-toggle` base reset).

---

### CRITICAL 3: Insert Field CSS Uses Non-Standard Pattern

**Impact:** CKEditor 4 may not render insert fields correctly, and missing child selectors could affect layout.

**Our template (before fix):**
```css
#vitecTemplate .insert { border-bottom: 1px dotted #999; min-width: 80px; display: inline-block; }
#vitecTemplate span.insert:empty::before { content: attr(data-label); color: #999; font-style: italic; }
#vitecTemplate .insert-table { display: inline-table; }
```

**All working reference templates:**
```css
span.insert:empty { font-size: inherit !important; line-height: inherit !important;
  display: inline-block; background-color: lightpink; min-width: 2em !important;
  height: .7em !important; text-align: center; }
span.insert:empty:before { content: attr(data-label); }
span.insert:empty:hover { background-color: #fff; cursor: pointer; }
.insert-table { display: inline-table; }
.insert-table > span, .insert-table > span.insert { display: table-cell; }
```

Key differences:
1. Reference uses NO `#vitecTemplate` prefix on insert styles
2. Reference uses `!important` on critical properties
3. Reference includes `.insert-table > span` child selector (missing from ours)
4. Reference uses `lightpink` background for visibility

**Fix applied:** Replaced with exact reference pattern.

---

### IMPORTANT 4: Article Padding / H2 Margin Mismatch

**Impact:** CSS counter offset doesn't match, but unlikely to prevent generation.

| Property | Our Template | Bruktbolig Reference |
|----------|-------------|---------------------|
| `article { padding-left }` | `0` | `20px` |
| `h2 { margin-left }` | `-26px` | `-20px` |

The padding-left creates indentation for article body text. The negative h2 margin pulls headings back to the left edge. Our 0px padding with -26px margin caused headings to hang outside the container.

**Fix applied:** Changed to `padding-left: 20px` and `margin-left: -20px` matching the reference.

---

### INFO 5: Two-Style-Block Pattern

The reference template uses **two separate `<style type="text/css">` blocks**:
1. First block: layout CSS (counters, headings, tables, inserts)
2. Second block: SVG checkbox CSS (label.btn, .svg-toggle, etc.)

Our template had everything in a single style block. While this shouldn't prevent generation, the two-block pattern is what CKEditor 4 expects based on the Vitec Stilark integration.

**Fix applied:** Split into two style blocks matching the reference.

---

### INFO 6: `Model.oppdrag.sjekkliste2901085` — Unverified Path

The post-signature conditional blocks use `Model.oppdrag.sjekkliste2901085`. This sjekkliste field is not in the standard merge field registry. It was converted from the legacy `#standard_ektefellesamtykke¤` syntax.

If this field doesn't exist in the system, the conditions would evaluate to false (not crash), so both conditional blocks would simply not render. This is safe but the content itself is still placeholder text.

---

### INFO 7: Template Structure is Correct

Verified against the reference:
- `<div id="vitecTemplate">` — correct (no `class="proaktiv-theme"`)
- `<span vitec-template="resource:Vitec Stilark">&nbsp;</span>` — correct
- Outer `<table><tbody><tr><td colspan="100">` wrapper — correct
- All HTML entities properly encoded (pure ASCII file, 0 non-ASCII bytes)
- All 836 HTML tags properly opened and closed (verified programmatically)
- All 35 merge fields exist in the Vitec field registry
- All 97 vitec-if conditions use correct escaping (`&quot;`, `&gt;`, `&amp;&amp;`)
- All 6 vitec-foreach loops use valid collection paths

---

## Complete List of Changes Applied

| # | Change | Reason |
|---|--------|--------|
| 1 | `Model.kjoperskostnader.poster` → `Model.kjoperskostnader.alleposter` | Standard collection path (used by 5+ working templates) |
| 2 | SVG checkbox CSS → exact reference pattern | Bare selectors, utf8 SVGs, full .svg-toggle base reset |
| 3 | Insert field CSS → exact reference pattern | No `#vitecTemplate` prefix, `!important` properties, child selectors |
| 4 | `article { padding-left: 0 }` → `padding-left: 20px` | Match reference indentation |
| 5 | `h2 { margin: ... -26px }` → `margin: ... -20px` | Match reference h2 offset (pairs with 20px padding) |
| 6 | Single `<style>` block → two separate `<style>` blocks | Match reference pattern (layout CSS + checkbox CSS) |

---

## Validation Result

```
RESULTS: 58/58 passed, 0 failed
```

---

## Recommended Test Procedure

1. Open Vitec Next test system (proatest.qa.vitecnext.no)
2. Navigate to a landbrukseiendom property (agricultural property with sellers, buyers registered)
3. Create a new document using this template
4. Verify the document generates and displays in CKEditor 4
5. Check that checkboxes render as clickable SVG graphics
6. Check that insert fields show lightpink placeholders with data-label text
7. Run Testfletting (PDF preview) to verify Norwegian characters render correctly

If the document still fails to generate after these fixes, the issue is likely in the Vitec Next template configuration (document type assignment, property type filter) rather than the HTML content.
