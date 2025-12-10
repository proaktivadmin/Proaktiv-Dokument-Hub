# Proaktiv Design System & Brand Guide

**Last Updated:** 2025-12-10
**Source:** Extracted from "Proaktiv Brand Manual" and "Vitec Next" system constraints.

## 1. Core Identity
The Proaktiv brand is defined by a "Premium," "Corporate," and "Minimalist" aesthetic. It avoids standard "out-of-the-box" styling in favor of bespoke, sharp, and high-contrast designs.

## 2. Color Palette (Design Tokens)

| Token Name | Hex Code | Usage |
| :--- | :--- | :--- |
| **PG - MØRK BLÅ** | `#272630` | **Primary Brand Color.** Used for main headings, text, and heavy structural elements. |
| **PG - BEIGE** | `#e9e7dc` | **Primary Background.** Used for info cards, page backgrounds, and softening contrast. |
| **PG - BRONSE** | `#bcab8a` | **Accent.** Used for quotes, dividers, subheaders, and the "Proaktiv" logo element. |
| **PG - GRØNN** | `#a4b5a8` | **Secondary Accent.** Used sparingly for specific highlights or distinct sections. |
| **PG - SORT** | `#1d1d1d` | **Black.** Standard text color for high readability on white backgrounds. |

## 3. Typography
*Note: Vitec Next has limited font support for PDF generation. We use web fonts where possible, but fallbacks are critical.*

### Primary Serif (Headings & Bolignavn)
*   **Font Family:** "Playfair Display", serif.
*   **Usage:** Property titles ("Bolignavn"), large quotes, cover page text.
*   **Weight:** Semibold / Bold.

### Primary Sans-Serif (Body Text)
*   **Font Family:** Arial, Helvetica, sans-serif.
*   **Usage:** Standard paragraph text, tables, technical specifications.
*   **Reasoning:** Safe cross-platform rendering in Vitec's PDF engine (PrinceXML/wkhtmltopdf).

## 4. UI Patterns & Shapes

### The "Proaktiv L-Bracket"
A signature design element used to frame content (images or text).
*   **Visual:** Two intersecting border lines forming a corner.
*   **Implementation:** CSS pseudo-elements (`::before`, `::after`) or nested divs with specific border styling.
*   **Colors:** Often `PG - MØRK BLÅ` or `PG - BRONSE`.

### Geometry
*   **Border Radius:** **0px**. All buttons, cards, images, and inputs must have sharp 90-degree corners. No rounding.
*   **Spacing:** Generous "premium" whitespace. Avoid cramped layouts.

## 5. CSS Implementation (Vitec Specific)
To use these styles in Vitec templates, reference the **Proaktiv Theme v1** variables:

```css
:root {
  --theme-color-primary: #272630;
  --theme-color-secondary: #e9e7dc;
  --theme-color-accent: #bcab8a;
  --theme-font-serif: 'Playfair Display', serif;
}
```

*This file serves as the "Source of Truth" for future design updates.*
