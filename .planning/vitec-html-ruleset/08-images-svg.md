## 8. SVG, Images, and Media

### Base64 SVG checkbox/radio pattern

Vitec templates implement interactive checkboxes and radio buttons using SVG images referenced via CSS `background-image` with inline SVG data URIs:

#### Checkbox (unchecked)
```css
background-image: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 512 512'><rect style='fill:black;' height='496' width='496' x='9.1' y='9.1'></rect><rect style='fill:white;' height='400' width='400' x='57.1' y='60.6'></rect></svg>");
```

#### Checkbox (checked)
Same as above plus a checkmark path:
```css
<path style='fill:black;' d='M396.1,189.9L223.5,361.1c-4.7,4.7-12.3,4.6-17-0.1l-90.8-91.5...'/>
```

#### Radio button (unchecked)
```css
background-image: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 512 512'><circle style='fill:black;' cx='257.1' cy='257.1' r='248'></circle><circle style='fill:white;' cx='257.1' cy='257.1' r='200'></circle></svg>");
```

#### Radio button (selected)
Same as above plus an inner filled circle.

**Usage pattern:**
```html
<label class="btn" contenteditable="false" data-toggle="button">
  <span class="checkbox svg-toggle"></span>
</label>
```

```html
<label class="btn" contenteditable="false" data-toggle="button">
  <span class="radio svg-toggle"></span>
  <input name="rbl01" type="radio" />Ja
</label>
```

**Evidence:** Lines 207–272 (CSS), lines 6175–6210 (HTML usage).

The `<input>` elements inside are hidden (`display: none` via CSS at line 269) — they exist only for semantic grouping via `name` attribute. The visual toggle is handled entirely by the SVG background images on `.svg-toggle`.

#### Large SVG toggle variant

A `.large` modifier class doubles the toggle size to 24×24px:

```css
.svg-toggle.large {
    width: 24px;
    height: 24px;
    background-size: 24px 24px;
}
```

Usage: `<span class="checkbox large svg-toggle"></span>`

**(DB evidence: "Akseptbrev kjøper uten oppgjørsskjema (e-post)")**

#### Inline toggle pattern (without checkbox-table)

Contracts use SVG toggles inline within `<p>` elements via `data-toggle="buttons"` on the paragraph. Radio buttons share a `name` attribute to form a mutually-exclusive group:

```html
<p data-toggle="buttons">
  <label class="btn" contenteditable="false" data-toggle="button">
    <span class="checkbox svg-toggle"></span>
    <input name="rbl001" type="radio" />
  </label>
  <span vitec-if="Model.kjopere.Count == 1">Jeg </span>
  <span vitec-if="Model.kjopere.Count &gt; 1">Vi </span>ønsker boligkjøperforsikring

  &nbsp;&nbsp;&nbsp;

  <label class="btn" contenteditable="false" data-toggle="button">
    <span class="checkbox svg-toggle"></span>
    <input name="rbl001" type="radio" />
  </label>
  <span vitec-if="Model.kjopere.Count == 1">Jeg </span>
  <span vitec-if="Model.kjopere.Count &gt; 1">Vi </span>ønsker ikke boligkjøperforsikring
</p>
```

Key details:
- `data-toggle="buttons"` on the `<p>` wrapper enables Bootstrap toggle behavior
- `data-toggle="button"` on each `<label>` makes it individually toggleable
- `input[type="radio"]` elements are hidden via CSS (`display: none`) in PDF output
- `name="rbl001"` groups the radio buttons (only one active at a time)
- `contenteditable="false"` on labels prevents CKEditor from modifying the toggle structure

CSS for hiding radio inputs in PDF:
```css
#vitecTemplate [data-toggle="buttons"] input {
    display: none;
}
```

**(Evidence: Kjøpekontrakt FORBRUKER — both DB and custom versions)**

### Image embedding conventions

#### Merge field images

```html
<img alt="" src="@Model.ansvarligmegler.hovedbilde" />
<img alt="" src="[[meglerkontor.firmalogourl]]" style="max-height:1.5cm; max-width:6cm" />
```

Both `@Model.` and `[[...]]` syntax work for image sources.

#### Figure/figcaption pattern

```html
<figure>
  <figcaption>ansvarligmegler.hovedbilde</figcaption>
  <img alt="" src="@Model.ansvarligmegler.hovedbilde" />
</figure>
```

CSS rules:
```css
#vitecTemplate figure {
    text-align: center;
    display: inline-block;
}
#vitecTemplate figure img:not(.scaled-image) {
    max-width: 3cm;
    max-height: 3cm;
}
#vitecTemplate figure figcaption {
    font-size: smaller;
    display: block;
}
```

**Evidence:** Lines 47–60 (CSS), lines 6241–6292 (HTML).

#### Scaled/circular image

```html
<img alt="Eiendommens bilde" class="scaled-image" src="$.SKALER(@Model.eiendom.hovedbilde, h=100)" />
```

CSS:
```css
#vitecTemplate .scaled-image {
    width: 100px;
    height: 100px;
    object-fit: cover;
    object-position: center center;
    border-radius: 50%;
}
```

**Evidence:** Lines 62–68 (CSS), line 6292 (HTML). The `$.SKALER()` function generates a server-side scaled version of the image.

#### QR code generation

```html
<img alt="QR code" src="https://api.qrserver.com/v1/create-qr-code/?size=80x80&amp;data=@Model.oppdrag.estateid;@Model.oppdrag.installationId;Dokumentnavn;Dokumenttype&amp;format=svg" />
```

**Evidence:** Line 6280. Uses an external API with Razor model values embedded in the URL.

### Available image merge fields

| Field | Content |
|-------|---------|
| `@Model.ansvarligmegler.hovedbilde` | Agent profile photo |
| `@Model.ansvarligmegler.signatur` | Agent signature image |
| `@Model.megler1.hovedbilde` | Co-agent photo |
| `@Model.megler1.signatur` | Co-agent signature |
| `@Model.avsender.bilde` | Sender photo |
| `@Model.avsender.signatur` | Sender signature |
| `@Model.avsender.firmalogourl` | Company logo |
| `@Model.meglerkontor.firmalogourl` | Office logo |
| `@Model.eiendom.hovedbilde` | Property main photo |
| `@Model.oppdrag.prosjekt.logo` | Project logo |

---
