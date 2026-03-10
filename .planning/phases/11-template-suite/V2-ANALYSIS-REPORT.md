# V2 Analysis Report: Kjøpekontrakt prosjekt (leilighet)

> **Template:** Kjøpekontrakt prosjekt (leilighet / eierseksjon under oppføring)
> **Version:** 2 (post content-corrections, Fixes 1-18)
> **Validation:** 51/51 PASS (tiers A–K)
> **PDF tested:** Testfletting via Vitec Next, property Solåsveien 30, 2026-02-22
> **Reference:** `kjøpekontrakt bruktbolig html.html` (production gold standard)

---

## Severity Definitions

| Level | Meaning |
|-------|---------|
| **P0 — BLOCKING** | Will cause incorrect rendering in Vitec Next PDF output. Must fix before production. |
| **P1 — IMPORTANT** | Deviates from reference standard. Functionally works but visually or structurally wrong. |
| **P2 — MINOR** | Small deviation. Unlikely to cause issues but does not match production quality bar. |
| **P3 — COSMETIC** | Polish items. No functional impact, but would improve consistency with gold standard. |

---

## P0 — BLOCKING

### P0-1: SVG Checkbox Design Does Not Match Vitec Standard

**Status:** Must fix before production deployment.

The checkbox SVG design is visibly different from every other contract template in Vitec Next. Side-by-side, our checkboxes look "web-modern" while the reference checkboxes look like traditional legal form checkboxes.

**Our implementation (wrong):**
- ViewBox: `0 0 16 16` (tiny coordinate space)
- Border: 1px `stroke="#000"` (thin outline)
- Corners: `rx="2" ry="2"` (rounded)
- Checkmark: Small bezier curve path

**Reference implementation (correct):**
- ViewBox: `0 0 512 512` (large coordinate space, more precise rendering)
- Border: Filled black rect 496×496 with white rect 400×400 inset (thick solid border, ~48px visual weight)
- Corners: Sharp (no rounding)
- Checkmark: Large bezier path with visual weight matching the border

**Why it matters:** When a broker prints this contract alongside a bruktbolig contract, the checkboxes will look different. This undermines trust — it looks like a non-standard or home-made template.

**Reference SVG data URIs (copy these exactly):**

Unchecked:
```
data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 512 512'><rect style='fill:black;' height='496' width='496' x='9.1' y='9.1'></rect><rect style='fill:white;' height='400' width='400' x='57.1' y='60.6'></rect></svg>
```

Checked:
```
data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 512 512'><rect style='fill:black;' height='496' width='496' x='9.1' y='9.1'></rect><rect style='fill:white;' height='400' width='400' x='57.1' y='60.6'></rect><path style='fill:black;' d='M396.1,189.9L223.5,361.1c-4.7,4.7-12.3,4.6-17-0.1l-90.8-91.5c-4.7-4.7-4.6-12.3,0.1-17l22.7-22.5c4.7-4.7,12.3-4.6,17,0.1 l59.8,60.3l141.4-140.2c4.7-4.7,12.3-4.6,17,0.1l22.5,22.7C400.9,177.7,400.8,185.3,396.1,189.9L396.1,189.9z'></path></svg>
```

---

### P0-2: Checkbox CSS Block Missing Critical Properties

**Status:** Must fix before production deployment.

Our checkbox CSS is a simplified version that omits critical reset properties from the reference. When the Vitec Stilark CSS loads (which includes Bootstrap-derived styles), our checkboxes will inherit unintended styling.

**Missing or wrong properties (12 differences):**

| Property | Reference | Ours | Impact |
|----------|-----------|------|--------|
| `label.btn` display | `inline` | `inline-block` | Changes line-height behavior, may shift checkbox position |
| `label.btn` padding | `0` | not set | May inherit Stilark button padding |
| `label.btn` vertical-align | `baseline` | not set | Inconsistent vertical alignment with text |
| `label.btn` white-space | `normal` | not set | May inherit `nowrap` from Stilark |
| `label.btn` font-size | `inherit` | not set | May inherit Bootstrap button font-size |
| `label.btn` text-transform | `none` | not set | May inherit `uppercase` from Bootstrap |
| `label.btn` outline | `none` | not set | Focus outline may appear in CKEditor |
| `.svg-toggle` margin | `0 5px` | not set | Checkbox sits hard against text — no spacing |
| `.svg-toggle` display | `inline-block !important` | `inline-block` (no !important) | Stilark may override with `display:none` or `block` |
| `.svg-toggle` cursor | `pointer` | `default` on label | Minor, but pointer is the CKEditor expectation |
| `.svg-toggle` background-position | `center center` | not set | SVG may not center in the 16×16 box |
| `.svg-toggle` background-size | `16px 16px` (explicit) | `contain` | `contain` may render differently in PDF pipeline |
| `.btn.active` box-shadow | `none; outline: none` | not set | Active checkbox may show blue glow in CKEditor |

**Correct CSS block (from reference, with `#vitecTemplate` scoping added):**

```css
/* Klikkbare sjekkbokser og radioknapper */
label.btn {
    display: inline;
    text-transform: none;
    white-space: normal;
    padding: 0;
    vertical-align: baseline;
    outline: none;
    font-size: inherit;
}

    label.btn:active,
    label.btn.active {
        box-shadow: none;
        outline: none;
    }

.svg-toggle {
    display: inline-block !important;
    width: 16px;
    height: 16px;
    margin: 0 5px;
    vertical-align: bottom;
    padding: 0;
    border: none;
    background: transparent;
    border-radius: 0;
    box-shadow: none !important;
    cursor: pointer;
    white-space: normal;
    text-align: left;
    background-repeat: no-repeat;
    background-size: 16px 16px;
    background-position: center center;
}

    .svg-toggle.checkbox { /* unchecked */ }
    .svg-toggle.checkbox.active,
    .btn.active > .svg-toggle.checkbox { /* checked */ }

#vitecTemplate [data-toggle="buttons"] input {
    display: none;
}
```

**Key observation:** The reference checkbox CSS is NOT scoped under `#vitecTemplate` (except the input-hide rule). This is intentional — the Stilark loads label/button styles globally, and the checkbox CSS must override them at the same specificity level. Our `#vitecTemplate label.btn` selector has higher specificity which might seem safer, but it does not match how Vitec's own templates interact with the Stilark.

---

### P0-3: Checkbox HTML Structure Has Unnecessary `<input>` Tag

**Status:** Must fix before production deployment.

**Our pattern (wrong for standalone checkboxes):**
```html
<label class="btn" contenteditable="false" data-toggle="button">
  <input type="checkbox" />
  <span class="checkbox svg-toggle"></span>
</label>
```

**Reference pattern (standalone checkbox — no `<input>`):**
```html
<label class="btn" contenteditable="false" data-toggle="button">
  <span class="checkbox svg-toggle"></span>
</label>
```

**Reference pattern (radio group — with `<input type="radio">`):**
```html
<label class="btn" contenteditable="false" data-toggle="button">
  <span class="checkbox svg-toggle"></span>
  <input name="rbl001" type="radio" />
</label>
```

Three differences:
1. Standalone checkboxes in the reference have **no `<input>` element at all**
2. When an `<input>` is used (radio groups), it goes **after** the `<span>`, not before
3. Radio inputs use `type="radio"` with a `name` attribute for mutual exclusion, not `type="checkbox"`

**Risk:** The hidden `<input type="checkbox">` may cause Vitec's PDF renderer to detect form fields and render them as interactive PDF form elements (breaking the visual layout). Even if it works, it's technically incorrect markup that may fail in future Vitec updates.

---

## P1 — IMPORTANT

### P1-1: Insert Field CSS Diverges from Reference

**Our implementation:**
```css
#vitecTemplate .insert {
  border-bottom: 1px dotted #999;
  min-width: 80px;
  display: inline-block;
}
#vitecTemplate span.insert:empty::before {
  content: attr(data-label);
  color: #999;
  font-style: italic;
}
```

**Reference implementation:**
```css
span.insert:empty {
    font-size: inherit !important;
    line-height: inherit !important;
    display: inline-block;
    background-color: lightpink;
    min-width: 2em !important;
    height: .7em !important;
    text-align: center;
}
span.insert:empty:before {
    content: attr(data-label);
}
span.insert:empty:hover {
    background-color: #fff;
    cursor: pointer;
}
.insert-table > span,
.insert-table > span.insert {
    display: table-cell;
}
```

**Differences:**
- Reference uses `lightpink` background fill (visible in CKEditor as a pink rectangle). Ours uses dotted bottom border (underline style).
- Reference uses `min-width: 2em !important` with `height: .7em !important`. Ours uses `min-width: 80px`.
- Reference has hover state (`background-color: #fff; cursor: pointer`). Ours doesn't.
- Reference has `.insert-table > span.insert { display: table-cell }`. Ours doesn't.
- Reference label text has no color/italic styling. Ours adds `color: #999; font-style: italic`.

**Impact:** Insert fields will look different in CKEditor. The pink background is the standard Vitec visual cue — brokers are trained to look for pink rectangles as "fill-in-here" indicators. Our grey-italic-dotted-underline style is non-standard. In PDF output, the visual difference is smaller (both show placeholder text), but CKEditor behavior may confuse users.

**In the PDF:** The insert field labels ("tekst", "beløp", "dato", etc.) render visibly. This is correct CKEditor behavior — they show as placeholder text for the user to replace. No action needed for PDF rendering, but the CKEditor visual cue should match the pink convention.

---

### P1-2: `.costs-table` Is Custom — Not in Reference

Our template introduces a custom `.costs-table` class:
```css
#vitecTemplate .costs-table { width: 100%; table-layout: fixed; border-collapse: collapse; }
#vitecTemplate .costs-table td { padding: 2px 6px; vertical-align: top; }
#vitecTemplate .costs-table tr.sum-row td { border-top: 1px solid #000; font-weight: bold; }
```

The reference template does not have this class. It uses inline styles on tables or the standard `.borders` class. While this works functionally, it is a non-standard addition that may conflict with future Stilark updates or produce unexpected results if the template is edited in CKEditor (where the class name has no meaning).

**Recommendation:** Consider replacing with inline styles on the `<tr>` and `<td>` elements, or use the standard `.borders` class where applicable.

---

### P1-3: `vitec-if` Does Not Guard Against "Mangler data"

Visible in PDF line 16: `Selger er representert ved fullmektig Mangler data`

The condition `Model.selger.fullmektig.navn != ""` passes because Vitec returns the string `"Mangler data"` for empty fields — it's not an empty string. This means the fullmektig paragraph shows even when no fullmektig is assigned.

**Reference behavior:** Reference templates typically do NOT guard against "Mangler data" — they rely on the data being properly populated. This is technically consistent with Vitec's standard behavior. However, for a production contract, showing "Mangler data" in a legal paragraph is unprofessional.

**Possible fix:** Add a compound condition:
```
Model.selger.fullmektig.navn != "" && Model.selger.fullmektig.navn != "Mangler data"
```

**Risk:** This is non-standard — verify that `&amp;&amp;` compound conditions work reliably in Vitec's `vitec-if` evaluator before deploying.

---

## P2 — MINOR

### P2-1: `#vitecTemplate` Scoping Inconsistency

Our CSS scopes all rules under `#vitecTemplate`. The reference template scopes most rules under `#vitecTemplate` but leaves the checkbox CSS and insert-field CSS UNSCOPED (or partially scoped).

This is intentional in the reference — these rules need to interact with the globally-loaded Stilark CSS at the correct specificity level. Over-scoping under `#vitecTemplate` raises the specificity, which may win over Stilark rules we want to keep and lose against Stilark rules that use `!important`.

**Specific cases where reference is unscoped:**
- `label.btn { ... }` — NO `#vitecTemplate` prefix
- `.svg-toggle { ... }` — NO `#vitecTemplate` prefix
- `.svg-toggle.checkbox { ... }` — NO `#vitecTemplate` prefix
- `span.insert:empty { ... }` — NO `#vitecTemplate` prefix
- `.insert-table { ... }` — NO `#vitecTemplate` prefix

**Scoped in reference:**
- `#vitecTemplate .avoid-page-break`
- `#vitecTemplate article`
- `#vitecTemplate h1/h2/h3`
- `#vitecTemplate table`
- `#vitecTemplate .roles-table`
- `#vitecTemplate a.bookmark`
- `#vitecTemplate .liste:last-child .separator`

**Recommendation:** Match the reference scoping pattern exactly.

---

### P2-2: `.roles-table` CSS Differences

**Our rules:**
```css
#vitecTemplate .roles-table th { text-align: left; padding: 4px 6px; border-bottom: 1px solid #000; }
#vitecTemplate .roles-table td { padding: 4px 6px; vertical-align: top; }
```

**Reference:** Only has the hide-last-row rule:
```css
#vitecTemplate .roles-table tbody:last-child tr:last-child td { display: none; }
```

The th/td padding and border styling comes from the Stilark, not the template CSS. By adding our own rules, we may override Stilark defaults in ways that are visually inconsistent with other Vitec templates.

---

### P2-3: Duplicate Oppgjør Introductory Paragraph

The Oppgjør section (Section 4) has two nearly identical opening paragraphs:

> "Oppgjøret mellom partene foretas av megler og gjennomføres i henhold til inngått avtale mellom kjøper og selger."
>
> "Oppgjøret mellom partene foretas av meglerforetakets oppgjørsavdeling:"

Both appear in the source document, so this is technically correct content. But it reads redundantly. The first paragraph may be unnecessary since the second paragraph immediately specifies the oppgjørsavdeling details. **Keep as-is** (verbatim from source), but flag for human review if the broker finds it odd.

---

### P2-4: `[[oppgjor.besoksadresse]]` vs `[[oppgjor.postadresse]]`

Our template uses `besoksadresse`/`besokspostnr`/`besokspoststed`. The reference uses `postadresse`/`postnr`/`poststed`. These are different merge fields — the reference shows the mailing address while ours shows the visit address.

**Risk:** For the oppgjørsavdeling section, the mailing address is more appropriate (this is where documents should be sent). The visit address may be different. Verify against the field registry which is correct for contract documents.

---

### P2-5: `[[kontrakt.klientkonto]]` + `[[kontrakt.kid]]` vs `[[kontrakt.klientkontoogkid]]`

Our template uses two separate fields. The reference template uses the combined field `[[kontrakt.klientkontoogkid]]`. Either format may work, but the combined field ensures consistent formatting as defined by the Vitec API. Verify which format is preferred for prosjekt contracts.

---

## P3 — COSMETIC

### P3-1: Second `<style>` Block vs Single Block

The reference template uses TWO separate `<style>` blocks:
1. First block: Template-specific CSS (counters, headings, tables, inserts)
2. Second block: Checkbox/radiobutton CSS (prefixed with comment `/* Klikkbare sjekkbokser og radioknapper */`)

Our template merges everything into a single `<style>` block. While functionally identical, the two-block pattern is how Vitec organizes its templates. If the checkbox CSS is ever updated globally (new Stilark version), having it in a separate block makes surgical updates easier.

---

### P3-2: `data-toggle="buttons"` Missing on Parent Container

The reference uses `data-toggle="buttons"` on a parent `<p>` element for grouped radio buttons:
```html
<p data-toggle="buttons"><label class="btn">...</label> ... <label class="btn">...</label></p>
```

Our template doesn't use radio groups (all checkboxes are standalone), so this doesn't apply. But if radio-style mutual exclusion is ever needed (e.g., "Alternativ 1 OR Alternativ 2"), the reference pattern should be followed.

---

### P3-3: Minor Wording: "eiendomsmegler" vs "megler"

Sections 6 and 4 now correctly use "megler" (matching the selveier source). However, Section 6 paragraph 2 still says "eiendomsmegler" in two places:

> "Pantedokumentet er tinglyst, eller skal tinglyses, av **eiendomsmegler**."
> "**Eiendomsmegleren** skal vederlagsfritt besørge pantedokumentet slettet..."

These match the selveier source exactly, so they are correct. The document uses both "megler" (informal) and "eiendomsmegler" (formal/legal) appropriately depending on context.

---

## Summary: Fix Plan

| Priority | Count | Action |
|----------|-------|--------|
| **P0** | 3 | Replace checkbox CSS, SVG data URIs, and HTML structure to match reference exactly |
| **P1** | 3 | Update insert-field CSS, remove custom `.costs-table`, evaluate "Mangler data" guard |
| **P2** | 5 | Scoping adjustments, merge field verification, roles-table CSS cleanup |
| **P3** | 3 | Structural polish — two style blocks, data-toggle, wording consistency |

**Critical path to production:** Fix P0-1 through P0-3 (all checkbox-related), then re-test with Testfletting. The remaining items can be addressed iteratively.

---

## Appendix: Reference CSS (Complete — Gold Standard)

Source: `kjøpekontrakt bruktbolig html.html` (working production template)

### Style Block 1 — Template CSS
```css
#vitecTemplate { counter-reset: section; }
#vitecTemplate article.item:not(article.item article.item) {
    counter-increment: section; counter-reset: subsection;
}
#vitecTemplate article.item article.item { counter-increment: subsection; }
#vitecTemplate article.item:not(article.item article.item) h2::before { content: counter(section) ". "; }
#vitecTemplate article.item article.item h3::before { content: counter(section) "." counter(subsection) ". "; }
#vitecTemplate .avoid-page-break { page-break-inside: avoid; }
#vitecTemplate article { padding-left: 26px; }
#vitecTemplate article article { padding-left: 0; }
#vitecTemplate h1 { text-align: center; font-size: 14pt; margin: 0; padding: 0; }
#vitecTemplate h2 { font-size: 11pt; margin: 30px 0 0 -26px; padding: 0; }
#vitecTemplate h3 { font-size: 10pt; margin: 20px 0 0 0; padding: 0; }
#vitecTemplate table { width: 100%; table-layout: fixed; }
#vitecTemplate table .borders { width: 100%; table-layout: fixed; border-bottom: solid 1px black; border-top: solid 1px black; }
#vitecTemplate ul { list-style-type: disc; margin-left: 0; }
#vitecTemplate ul li { list-style-position: outside; line-height: 20px; margin-left: 0; }
span.insert:empty { font-size: inherit !important; line-height: inherit !important; display: inline-block; background-color: lightpink; min-width: 2em !important; height: .7em !important; text-align: center; }
span.insert:empty:before { content: attr(data-label); }
span.insert:empty:hover { background-color: #fff; cursor: pointer; }
.insert-table { display: inline-table; }
.insert-table > span, .insert-table > span.insert { display: table-cell; }
#vitecTemplate .roles-table tbody:last-child tr:last-child td { display: none; }
#vitecTemplate a.bookmark { color: #000; font-style: italic; text-decoration: none; }
#vitecTemplate .liste:last-child .separator { display: none; }
```

### Style Block 2 — Checkbox/Radio CSS
```css
/* Klikkbare sjekkbokser og radioknapper */
label.btn {
    display: inline; text-transform: none; white-space: normal;
    padding: 0; vertical-align: baseline; outline: none; font-size: inherit;
}
label.btn:active, label.btn.active { box-shadow: none; outline: none; }
.svg-toggle {
    display: inline-block !important; width: 16px; height: 16px;
    margin: 0 5px; vertical-align: bottom; padding: 0; border: none;
    background: transparent; border-radius: 0; box-shadow: none !important;
    cursor: pointer; white-space: normal; text-align: left;
    background-repeat: no-repeat; background-size: 16px 16px; background-position: center center;
}
.svg-toggle.checkbox {
    background-image: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 512 512'><rect style='fill:black;' height='496' width='496' x='9.1' y='9.1'></rect><rect style='fill:white;' height='400' width='400' x='57.1' y='60.6'></rect></svg>");
}
.svg-toggle.checkbox.active, .btn.active > .svg-toggle.checkbox {
    background-image: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 512 512'><rect style='fill:black;' height='496' width='496' x='9.1' y='9.1'></rect><rect style='fill:white;' height='400' width='400' x='57.1' y='60.6'></rect><path style='fill:black;' d='M396.1,189.9L223.5,361.1c-4.7,4.7-12.3,4.6-17-0.1l-90.8-91.5c-4.7-4.7-4.6-12.3,0.1-17l22.7-22.5c4.7-4.7,12.3-4.6,17,0.1 l59.8,60.3l141.4-140.2c4.7-4.7,12.3-4.6,17,0.1l22.5,22.7C400.9,177.7,400.8,185.3,396.1,189.9L396.1,189.9z'></path></svg>");
    box-shadow: none !important;
}
.svg-toggle.radio {
    background-image: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 512 512'><circle style='fill:black;' cx='257.1' cy='257.1' r='248'></circle><circle style='fill:white;' cx='257.1' cy='257.1' r='200'></circle></svg>");
}
.svg-toggle.radio.active, .btn.active > .svg-toggle.radio {
    background-image: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 512 512'><circle style='fill:black;' cx='257.1' cy='257.1' r='248'></circle><circle style='fill:white;' cx='257.1' cy='257.1' r='200'></circle><circle style='fill:black;' cx='257.1' cy='257.1' r='91.5'></circle></svg>");
    box-shadow: none !important;
}
#vitecTemplate [data-toggle="buttons"] input { display: none; }
```

### Checkbox HTML Patterns
```html
<!-- Standalone unchecked (no <input>) -->
<label class="btn" contenteditable="false" data-toggle="button">
  <span class="checkbox svg-toggle"></span>
</label>

<!-- Standalone checked (no <input>) -->
<label class="btn active" contenteditable="false" data-toggle="button">
  <span class="checkbox svg-toggle"></span>
</label>

<!-- Conditional auto-check via vitec-if (Approach A — dual wrapper) -->
<span vitec-if="CONDITION_TRUE">
  <label class="btn active" contenteditable="false" data-toggle="button">
    <span class="checkbox svg-toggle"></span>
  </label>
</span>
<span vitec-if="CONDITION_FALSE">
  <label class="btn" contenteditable="false" data-toggle="button">
    <span class="checkbox svg-toggle"></span>
  </label>
</span>
```
