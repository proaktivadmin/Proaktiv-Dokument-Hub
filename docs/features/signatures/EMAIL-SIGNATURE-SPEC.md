# Email Signature Template Specification v3.0

> Last updated: 2026-01-26

## Overview

Professional email signature templates for Proaktiv Eiendomsmegling employees, optimized for cross-client compatibility including Outlook (Classic/New/Mac), Gmail, Apple Mail, and mobile devices.

---

## Template Variants

| Variant | File | Max Width | Min Width |
|---------|------|-----------|-----------|
| **With Photo** | `email-signature.html` | 540px | 360px |
| **Without Photo** | `email-signature-no-photo.html` | 446px | 320px |

---

## Overall Dimensions

| Property | With Photo | Without Photo |
|----------|------------|---------------|
| **Max width** | 540px | 446px |
| **Min width** | 360px | 320px |
| **Content height** | 96px | 96px |
| **Total height** | ~140px (with footer) | ~140px (with footer) |

---

## Grid Structure (With Photo)

```
┌──────────────────────────────────────────────────────────────────────────┐
│ "Med vennlig hilsen" (12px font, 6px bottom padding)                     │
├────────┬────┬────────────────────┬────┬──┬─┬────┬────────────────────────┤
│        │    │                    │    │  │ │    │                        │
│  COL 1 │GAP1│       COL 2        │GAP2│ L│D│ R  │        COL 3           │
│        │    │                    │    │  │ │    │                        │
│  PHOTO │14px│       INFO         │14px│22│1│14px│    LOGO + ICONS        │
│  80×96 │    │                    │    │  │ │    │        155px           │
│        │    │                    │    │  │ │    │                        │
├────────┴────┴────────────────────┴────┴──┴─┴────┴────────────────────────┤
│ Office info (11px font, 12px top padding)                                │
├──────────────────────────────────────────────────────────────────────────┤
│ Disclaimer (9px gray, 8px top padding)                                   │
└──────────────────────────────────────────────────────────────────────────┘

Legend: L = Left padding, D = Divider (1px), R = Right padding
```

---

## Column Specifications

### Column 1: Employee Photo

| Property | Value |
|----------|-------|
| **Width** | 80px |
| **Height** | 96px |
| **Aspect ratio** | 5:6 (portrait) |
| **Right padding** | 14px |
| **Object-fit** | cover |
| **Object-position** | center top |
| **Outlook rendering** | VML `v:rect` with `v:fill type="frame"` |

**Photo Rendering:**

```html
<!--[if mso]>
<v:rect xmlns:v="urn:schemas-microsoft-com:vml" fill="true" stroke="false" 
        style="width:80px;height:96px;">
  <v:fill type="frame" src="{{EmployeePhotoUrl}}" />
  <v:textbox inset="0,0,0,0" style="mso-fit-shape-to-text:false;"></v:textbox>
</v:rect>
<![endif]-->
<!--[if !mso]><!-->
<img src="{{EmployeePhotoUrl}}" alt="{{DisplayName}}" 
     style="display:block;border:0;width:80px;height:96px;object-fit:cover;object-position:center top;">
<!--<![endif]-->
```

**Notes:**
- Uses CSS `object-fit:cover` for modern clients
- `object-position:center top` keeps faces visible
- VML fallback ensures proper cropping in Outlook
- Photo is cropped from bottom, preserving head/shoulders

---

### Column 2: Employee Information

| Section | Height | Font Size | Line Height | Bottom Padding | Total |
|---------|--------|-----------|-------------|----------------|-------|
| **Name** | 24px | 20px bold | 24px | 4px | **28px** |
| **Title** | 16px | 12px bold | 16px | 10px | **26px** |
| **Phone row** | 18px | 11px | 18px | 0 | **18px** |
| **Gap** | 6px | — | — | — | **6px** |
| **Email row** | 18px | 11px | 18px | 0 | **18px** |
| **TOTAL** | — | — | — | — | **96px** |

**Name styling:**
```html
<td style="font-size:20px;font-weight:bold;line-height:24px;height:24px;padding-bottom:4px;color:#000 !important;white-space:nowrap;">
  {{DisplayName}}
</td>
```

**Phone/Email row structure:**

| Element | Width | Height | Notes |
|---------|-------|--------|-------|
| Icon cell | 14px | 18px | Icon is 14×14px, vertically centered |
| Icon-text gap | 6px | — | Applied as `padding-right` on icon cell |
| Text cell | flexible | 18px | Contains clickable link |

**Link styling (critical for cross-client):**
```html
<a href="tel:{{MobilePhoneRaw}}" style="color:#000000 !important;text-decoration:none;">
  <span style="color:#000000 !important;">{{MobilePhone}}</span>
</a>
```

**Colors:**
- Name: `#000000` (black)
- Title: `#bcab8a` (bronze)
- Phone/Email: `#000000` (black)

---

### Divider

| Property | Value |
|----------|-------|
| **Left padding** | 22px |
| **Line width** | 1px |
| **Line height** | 96px |
| **Line color** | `#bcab8a` (bronze) |
| **Right padding** | 14px (in logo column) |
| **Total spacing** | 37px |

---

### Column 3: Logo & Social Icons

| Section | Height | Details |
|---------|--------|---------|
| **Logo row** | 54px | Logo 155×35px, vertically centered |
| **Icons row** | 42px | 4 icons centered (matches phone+gap+email height) |
| **TOTAL** | **96px** | Matches content height |

**Logo specifications:**
- Width: 155px
- Height: 35px (centered in 54px row)
- Asset: `Proaktiv_sort.png` (black version)

**Social icon specifications:**

| Property | Value |
|----------|-------|
| **Icon size** | 32×32px |
| **Icon gap** | 9px |
| **Row height** | 42px |
| **Icons count** | 4 (Proaktiv, Instagram, LinkedIn, Facebook) |
| **Total width** | 4×32 + 3×9 = **155px** |

**Calculation:** Icons width matches logo width exactly for perfect alignment.

---

## Dark Mode Protection

The template includes comprehensive dark mode protection:

```html
<!-- Meta tags in <head> -->
<meta name="color-scheme" content="light">
<meta name="supported-color-schemes" content="light">
<meta name="x-apple-color-scheme" content="light">

<!-- CSS in <style> -->
:root { color-scheme: light; supported-color-schemes: light; }

@media (prefers-color-scheme: dark) {
  .dark-mode-bg { background-color: #ffffff !important; }
  .dark-mode-text { color: #000000 !important; }
}

/* Outlook.com dark mode */
[data-ogsc] .dark-mode-bg { background-color: #ffffff !important; }
[data-ogsc] .dark-mode-text { color: #000000 !important; }

/* Gmail dark mode */
u + .body .dark-mode-bg { background-color: #ffffff !important; }
u + .body .dark-mode-text { color: #000000 !important; }
```

---

## Link Color Protection

Multiple layers ensure links remain black across all clients:

### 1. MSO Styles (Outlook)
```html
<!--[if gte mso 9]>
<style type="text/css">
  a { color: #000000 !important; }
</style>
<![endif]-->
```

### 2. Apple Mail Data Detectors
```css
a[x-apple-data-detectors] {
  color: #000000 !important;
  text-decoration: none !important;
  font-size: inherit !important;
  font-family: inherit !important;
  font-weight: inherit !important;
  line-height: inherit !important;
}
```

### 3. General Link Styling
```css
a { color: #000000 !important; text-decoration: none !important; }
a:link, a:visited, a:hover, a:active { color: #000000 !important; text-decoration: none !important; }
```

### 4. Inline + Span Wrapper
```html
<a href="..." style="color:#000000 !important;text-decoration:none;">
  <span style="color:#000000 !important;">Link Text</span>
</a>
```

---

## Outlook Compatibility

### MSO Conditional Wrapper

```html
<!--[if mso]>
<table role="presentation" cellpadding="0" cellspacing="0" border="0" width="540">
  <tr><td>
<![endif]-->
  <!-- Content here -->
<!--[if mso]>
  </td></tr>
</table>
<![endif]-->
```

### Table Reset Styles

```css
mso-table-lspace: 0pt;
mso-table-rspace: 0pt;
```

---

## Apple Mail / Mac Outlook

### Font Smoothing

```html
<body style="-webkit-font-smoothing:antialiased;-moz-osx-font-smoothing:grayscale;">
```

### Apple Data Detector Override

See "Link Color Protection" section above.

---

## Template Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `{{EmployeePhotoUrl}}` | Employee profile photo URL | `https://proaktiv.no/d/photos/...` |
| `{{DisplayName}}` | Full name | `Adrian Frøyland` |
| `{{JobTitle}}` | Job title | `IT & IKT Ansvarlig` |
| `{{MobilePhone}}` | Formatted phone number | `46 74 75 09` |
| `{{MobilePhoneRaw}}` | Raw phone for `tel:` link | `+4746747509` |
| `{{Email}}` | Email address | `froyland@proaktiv.no` |
| `{{EmployeeUrl}}` | Employee profile page URL | `https://proaktiv.no/ansatte/...` |
| `{{InstagramUrl}}` | Instagram profile URL | Office → Company default |
| `{{LinkedInUrl}}` | LinkedIn profile URL | Office → Company default |
| `{{FacebookUrl}}` | Facebook page URL | Office → Company default |
| `{{OfficeName}}` | Office name | `Proaktiv Gruppen` |
| `{{OfficeAddress}}` | Street address | `Småstrandgaten 6` |
| `{{OfficePostal}}` | Postal code + city | `5014 Bergen` |

---

## File Locations

```
backend/scripts/templates/
├── email-signature.html          # With photo variant
├── email-signature-no-photo.html # Without photo variant
└── signature-notification-email.html # Notification email
```

---

## Assets

All assets are hosted on the Proaktiv CDN:

| Asset | URL | Size |
|-------|-----|------|
| Logo (black) | `https://proaktiv.no/assets/logos/Proaktiv_sort.png` | 155×35px |
| Proaktiv icon | `https://proaktiv.no/assets/logos/lilje_clean_52.png` | 32×32px |
| Instagram icon | `https://proaktiv.no/assets/logos/instagram.png` | 32×32px |
| LinkedIn icon | `https://proaktiv.no/assets/logos/linkedin.png` | 32×32px |
| Facebook icon | `https://proaktiv.no/assets/logos/facebook.png` | 32×32px |
| Phone icon | `https://proaktiv.no/assets/logos/phone.png` | 14×14px |
| Email icon | `https://proaktiv.no/assets/logos/email.png` | 14×14px |

---

## Email Client Compatibility Matrix

| Feature | Outlook Classic | Outlook New | Mac Outlook | Gmail | Apple Mail |
|---------|-----------------|-------------|-------------|-------|------------|
| Photo cropping | VML | object-fit | object-fit | object-fit | object-fit |
| Link colors | MSO styles | Inline | WebKit | Inline | Apple CSS |
| Dark mode | MSO override | CSS | CSS | u+.body | Meta tags |
| Font smoothing | — | — | WebKit | — | WebKit |

---

## Changelog

### v3.0 (2026-01-26)
- Fixed photo cropping with `object-fit:cover` and explicit 80x96 dimensions
- Fixed Outlook Classic centering: MSO table uses `align="left"` instead of `align="center"`
- Added `object-position:center top` for face-preserving photo crop
- Added Apple Mail `a[x-apple-data-detectors]` link override
- Added Mac Outlook `-webkit-font-smoothing:antialiased`
- Added `<span>` wrappers for aggressive link color override
- Added `white-space:nowrap` on name field
- Aligned no-photo template with photo version (96px height)
- Updated logo to 155×35px (vertically centered in 54px row)
- Updated social icons row to 42px (aligned with phone+email height)

### v2.0 (2026-01-25)
- Complete rewrite with golden ratio proportions
- Added VML fallback for Outlook photo cropping
- Implemented comprehensive dark mode protection
- Fixed icon/text baseline alignment
- Matched social icons width (155px) to logo width

### v1.0 (Initial)
- Basic signature template with photo and info sections
