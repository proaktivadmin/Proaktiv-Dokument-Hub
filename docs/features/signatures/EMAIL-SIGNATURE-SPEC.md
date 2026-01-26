# Email Signature Template Specification v2.0

> Last updated: 2026-01-25

## Overview

Professional email signature templates for Proaktiv Eiendomsmegling employees, optimized for cross-client compatibility including Outlook, Gmail, Apple Mail, and mobile devices.

---

## Template Variants

| Variant | File | Max Width | Min Width |
|---------|------|-----------|-----------|
| **With Photo** | `email-signature.html` | 540px | 360px |
| **Without Photo** | `email-signature-no-photo.html` | 480px | 320px |

---

## Overall Dimensions

| Property | With Photo | Without Photo |
|----------|------------|---------------|
| **Max width** | 540px | 480px |
| **Min width** | 360px | 360px |
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

**Technical notes:**
- Uses CSS `object-fit: cover` for modern clients
- VML fallback ensures proper cropping in Outlook
- Photo is cropped from center-top to preserve faces

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

**Phone/Email row structure:**

| Element | Width | Height | Notes |
|---------|-------|--------|-------|
| Icon cell | 14px | 18px | Icon is 14×14px, vertically centered |
| Icon-text gap | 6px | — | Applied as `padding-right` on icon cell |
| Text cell | flexible | 18px | Contains clickable link |

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
| **Right padding** | 14px |
| **Total width** | 37px |

---

### Column 3: Logo & Social Icons

| Section | Height | Details |
|---------|--------|---------|
| **Logo row** | 54px | Logo 155×48px + 6px visual padding |
| **Gap row** | 6px | Spacer (aligns with phone/email gap) |
| **Icons row** | 36px | 4 icons centered vertically |
| **TOTAL** | **96px** | Matches content height |

**Logo specifications:**
- Width: 155px
- Height: 48px
- Asset: `Proaktiv_sort.png` (black version)

**Social icon specifications:**

| Property | Value |
|----------|-------|
| **Icon size** | 32×32px |
| **Icon gap** | 9px |
| **Row height** | 36px |
| **Icons count** | 4 (Proaktiv, Instagram, LinkedIn, Facebook) |
| **Total width** | 4×32 + 3×9 = **155px** |

**Calculation:** Icons width matches logo width exactly for perfect alignment.

---

## Spacing & Golden Ratio

The template uses golden ratio (φ ≈ 1.618) principles for harmonious proportions.

| Gap Location | Size | Ratio Notes |
|--------------|------|-------------|
| Photo → Info | 14px | Base unit |
| Info → Divider (left) | 14px | Base unit |
| Divider left padding | 22px | 22:14 ≈ 1.57 (≈ φ) |
| Divider right padding | 14px | Base unit |
| Divider → Logo | 14px | Base unit |
| Phone ↔ Email gap | 6px | 11/φ ≈ 6.8 |
| Icon gaps | 9px | Calculated for 155px total |

---

## Footer Sections

| Section | Font Size | Color | Top Padding | Max Width |
|---------|-----------|-------|-------------|-----------|
| **Office info** | 11px | `#000000` | 12px | — |
| **Disclaimer** | 9px | `#888888` | 8px | 516px |

---

## Dark Mode Protection

The template includes comprehensive dark mode protection:

```html
<!-- Meta tags -->
<meta name="color-scheme" content="light">
<meta name="supported-color-schemes" content="light">
<meta name="x-apple-color-scheme" content="light">

<!-- CSS classes -->
.dark-mode-bg { background-color: #ffffff !important; }
.dark-mode-text { color: #000000 !important; }
```

**Supported clients:**
- Apple Mail (macOS/iOS)
- Outlook.com
- Gmail
- Microsoft Outlook desktop

---

## Outlook Compatibility

### MSO Conditional Comments

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

### VML Photo Fallback

```html
<!--[if mso]>
<v:rect xmlns:v="urn:schemas-microsoft-com:vml" fill="true" stroke="false" 
        style="width:80px;height:96px;">
  <v:fill type="frame" src="{{EmployeePhotoUrl}}" />
  <v:textbox inset="0,0,0,0" style="mso-fit-shape-to-text:false;"></v:textbox>
</v:rect>
<![endif]-->
```

### Table Reset Styles

```css
mso-table-lspace: 0pt;
mso-table-rspace: 0pt;
mso-line-height-rule: exactly;
```

---

## Template Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `{{EmployeePhotoUrl}}` | Employee profile photo URL | `https://proaktiv.no/photos/...` |
| `{{DisplayName}}` | Full name | `Adrian Frøyland` |
| `{{JobTitle}}` | Job title | `IT & IKT Ansvarlig` |
| `{{MobilePhone}}` | Formatted phone number | `46 74 75 09` |
| `{{MobilePhoneRaw}}` | Raw phone for `tel:` link | `+4746747509` |
| `{{Email}}` | Email address | `froyland@proaktiv.no` |
| `{{EmployeeUrl}}` | Employee profile page URL | `https://proaktiv.no/ansatte/...` |
| `{{InstagramUrl}}` | Instagram profile URL | `https://instagram.com/...` |
| `{{LinkedInUrl}}` | LinkedIn profile URL | `https://linkedin.com/...` |
| `{{FacebookUrl}}` | Facebook page URL | `https://facebook.com/...` |
| `{{OfficeName}}` | Office name | `Proaktiv Gruppen` |
| `{{OfficeAddress}}` | Street address | `Småstrandgaten 6` |
| `{{OfficePostal}}` | Postal code + city | `5014 Bergen` |

---

## Mobile Responsiveness

The template uses:
- `max-width` and `min-width` constraints
- Percentage-based widths where appropriate
- Viewport meta tag for proper scaling
- No complex media queries (better compatibility)

---

## File Locations

```
backend/scripts/templates/
├── email-signature.html          # With photo variant
└── email-signature-no-photo.html # Without photo variant
```

---

## Assets

All assets are hosted on the Proaktiv CDN:

| Asset | URL | Size |
|-------|-----|------|
| Logo (black) | `https://proaktiv.no/assets/logos/Proaktiv_sort.png` | 155×48px |
| Proaktiv icon | `https://proaktiv.no/assets/logos/lilje_clean_52.png` | 32×32px |
| Instagram icon | `https://proaktiv.no/assets/logos/instagram.png` | 32×32px |
| LinkedIn icon | `https://proaktiv.no/assets/logos/linkedin.png` | 32×32px |
| Facebook icon | `https://proaktiv.no/assets/logos/facebook.png` | 32×32px |
| Phone icon | `https://proaktiv.no/assets/logos/phone.png` | 14×14px |
| Email icon | `https://proaktiv.no/assets/logos/email.png` | 14×14px |

---

## Changelog

### v2.0 (2026-01-25)
- Complete rewrite with golden ratio proportions
- Added VML fallback for Outlook photo cropping
- Implemented comprehensive dark mode protection
- Fixed icon/text baseline alignment
- Matched social icons width (155px) to logo width
- Added precise height calculations for 96px content block
- Improved mobile responsiveness

### v1.0 (Initial)
- Basic signature template with photo and info sections
