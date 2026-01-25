# Email Signature Dark Mode Analysis & Fixes

**Date:** 2026-01-25  
**Template:** `backend/scripts/templates/email-signature.html`

---

## 1. DARK MODE ISSUES FOUND

### Critical Issues

1. **Dark Text Becomes Invisible**
   - `#333333` used for all text (name, links, footer)
   - Dark mode clients invert backgrounds but NOT text colors
   - Result: Dark text on dark background = invisible

2. **Missing Dark Mode Meta Tags**
   - No `color-scheme` meta tag
   - No `prefers-color-scheme` handling
   - Email clients don't know how to handle dark mode

3. **Logo Container Not Protected**
   - White background (`#ffffff`) on logo container
   - Dark mode may invert this to black, making black logo invisible
   - Needs explicit dark mode protection

4. **Links Unreadable**
   - Phone and email links use `#333333`
   - Will be invisible in dark mode
   - Need light color fallback

5. **No Background Color on Main Container**
   - Outer table has no explicit background
   - Dark mode clients may apply dark background
   - Text will disappear

6. **Footer Text Too Dark**
   - `#888888` may be too dark on dark backgrounds
   - Needs lighter fallback

### Moderate Issues

7. **Bronze Accent Color**
   - `#bcab8a` should remain visible (warm tone)
   - May need slight adjustment for contrast

8. **Image Background Color**
   - `#f5f5f5` on photo placeholder
   - May invert to dark, affecting image visibility

---

## 2. RECOMMENDED META TAGS

Add these to `<head>` section:

```html
<meta name="color-scheme" content="light">
<meta name="supported-color-schemes" content="light">
```

**Why:**
- `color-scheme: light` tells email clients to **preserve** light mode
- Prevents automatic dark mode inversion
- Works in Outlook, Apple Mail, Gmail, etc.

**Alternative Approach (if you want dark mode support):**
```html
<meta name="color-scheme" content="light dark">
<meta name="supported-color-schemes" content="light dark">
```
Then use CSS media queries (but email client support is limited).

**Recommendation:** Use `light` only to force light mode preservation.

---

## 3. CSS FIXES

### Fix 1: Force Light Background
Add explicit white background to all containers:

```css
background-color: #ffffff !important;
```

### Fix 2: Use Dark Text with Light Fallback
For text that must remain dark:

```css
color: #333333;
/* Dark mode fallback via media query (limited support) */
@media (prefers-color-scheme: dark) {
  color: #ffffff;
}
```

**Better approach:** Use `color-scheme: light` meta tag to prevent inversion.

### Fix 3: Protect Logo Container
Ensure logo container stays white:

```css
background-color: #ffffff !important;
```

### Fix 4: Light Link Colors
For links, use a color that works in both modes, or force light:

```css
color: #333333;
/* Or use a medium color that works in both */
color: #0066cc; /* Blue links work better */
```

### Fix 5: Outlook Dark Mode Selectors
For Outlook (which uses `[data-ogsc]`):

```css
/* Outlook dark mode - force light colors */
[data-ogsc] .text-dark {
  color: #ffffff !important;
}
```

**Note:** Outlook dark mode support is limited. Best to force light mode.

---

## 4. FULL CORRECTED TEMPLATE

See `email-signature-dark-mode.html` for the complete fixed version.

**Key Changes:**
1. Added `color-scheme: light` meta tags
2. Explicit `background-color: #ffffff` on all containers
3. All text colors remain `#333333` (protected by meta tag)
4. Logo container explicitly white
5. Links use `#333333` (will be visible due to light mode enforcement)
6. Added `!important` flags for critical styles
7. Added Outlook-specific dark mode protection

---

## 5. TESTING CHECKLIST

Test in these email clients with dark mode enabled:

- [ ] Outlook (Windows) - Dark mode
- [ ] Outlook (Mac) - Dark mode
- [ ] Apple Mail (macOS) - Dark mode
- [ ] Apple Mail (iOS) - Dark mode
- [ ] Gmail (Web) - Dark mode
- [ ] Gmail (iOS) - Dark mode
- [ ] Gmail (Android) - Dark mode
- [ ] Yahoo Mail - Dark mode
- [ ] Thunderbird - Dark mode

**Expected Result:** Signature should render in light mode regardless of client dark mode setting.

---

## 6. ALTERNATIVE APPROACH: Support Dark Mode

If you want to support dark mode (not recommended for signatures):

1. Use `color-scheme: light dark` meta tag
2. Add CSS media queries (limited support)
3. Use Outlook `[data-ogsc]` selectors
4. Test extensively in all clients

**Recommendation:** Force light mode for signatures. They're meant to be consistent brand elements.
