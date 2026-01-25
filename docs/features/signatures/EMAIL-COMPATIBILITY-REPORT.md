# Email Signature HTML Compatibility Report

**Date:** 2026-01-25  
**Template:** `email-signature.html` (WITH PHOTO version)  
**Analyzed For:** Outlook 2016-2024, Gmail, Apple Mail, iOS Mail, Android Gmail, Outlook.com, Yahoo Mail

---

## 🔴 CRITICAL ISSUES

### 1. `object-fit:cover` Not Supported in Outlook
**Location:** Line 14  
**Issue:** Outlook (all versions) ignores `object-fit` CSS property. Images will display incorrectly if aspect ratio doesn't match 80x80.

**Current Code:**
```html
<img src="{{EmployeePhotoUrl}}" width="80" height="80" alt="{{DisplayName}}" style="display:block;border:0;background-color:#f5f5f5;object-fit:cover;">
```

**Fix:**
```html
<img src="{{EmployeePhotoUrl}}" width="80" height="80" alt="{{DisplayName}}" style="display:block;border:0;background-color:#f5f5f5;">
<!-- Remove object-fit:cover - not supported in email -->
```

**Impact:** Photos may appear stretched or distorted in Outlook if source images aren't square.

---

### 2. `height="auto"` Ignored in Outlook
**Location:** Line 40  
**Issue:** Outlook doesn't respect `height="auto"` on images. Logo may display incorrectly.

**Current Code:**
```html
<img src="https://proaktiv.no/assets/logos/Proaktiv_sort_310_transparent.png" width="155" height="auto" style="display:block;border:0;max-width:100%;">
```

**Fix:**
```html
<!-- Calculate actual height based on aspect ratio, or use fixed height -->
<img src="https://proaktiv.no/assets/logos/Proaktiv_sort_310_transparent.png" width="155" height="60" style="display:block;border:0;">
<!-- If logo is 310px wide and ~120px tall, 155px wide = ~60px tall -->
```

**Impact:** Logo may not display at correct proportions in Outlook.

---

### 3. `border-radius` Not Supported in Outlook 2007-2016
**Location:** Line 39  
**Issue:** `border-radius:4px` is ignored in older Outlook versions (2007-2016). Newer Outlook (2019+) supports it, but inconsistent.

**Current Code:**
```html
<td align="center" style="padding:8px;padding-bottom:16px;background-color:#ffffff;border-radius:4px;">
```

**Fix:**
```html
<!-- Use MSO conditional for Outlook-specific styling -->
<td align="center" style="padding:8px;padding-bottom:16px;background-color:#ffffff;">
<!--[if mso]>
<td align="center" style="padding:8px;padding-bottom:16px;background-color:#ffffff;">
<![endif]-->
<!--[if !mso]><!-->
<td align="center" style="padding:8px;padding-bottom:16px;background-color:#ffffff;border-radius:4px;">
<!--<![endif]-->
```

**Impact:** Rounded corners won't appear in older Outlook versions (visual only, not breaking).

---

### 4. `max-width` on Div Not Respected in Outlook
**Location:** Line 84  
**Issue:** Outlook doesn't respect `max-width` on `<div>` elements. Text may overflow.

**Current Code:**
```html
<div style="color:#888888;font-size:9px;line-height:1.4;max-width:516px;">Denne e-posten...</div>
```

**Fix:**
```html
<!-- Use table cell instead of div for width control -->
<td style="color:#888888;font-size:9px;line-height:1.4;width:516px;max-width:516px;">Denne e-posten...</td>
```

**Impact:** Disclaimer text may overflow container in Outlook.

---

### 5. Missing MSO Conditionals for Outlook-Specific Fixes
**Issue:** No Microsoft Office (MSO) conditionals to handle Outlook's Word rendering engine quirks.

**Fix:** Add MSO conditionals for:
- Font rendering
- Padding/margin consistency
- Image display issues
- Background colors

**Example:**
```html
<!--[if mso]>
<style type="text/css">
  table { border-collapse: collapse; }
  td { padding: 0; }
</style>
<![endif]-->
```

---

### 6. `target="_blank"` May Be Stripped
**Location:** Lines 48, 54, 60, 66  
**Issue:** Some email clients (especially Outlook.com web) strip `target="_blank"` attributes.

**Current Code:**
```html
<a href="{{EmployeeUrl}}" target="_blank">
```

**Fix:**
```html
<!-- Add rel="noopener" for security and better compatibility -->
<a href="{{EmployeeUrl}}" target="_blank" rel="noopener">
```

**Impact:** Links may open in same window instead of new tab in some clients.

---

## 🟡 MODERATE ISSUES

### 7. No Dark Mode Support
**Issue:** Hardcoded colors (`#333333`, `#ffffff`) will not adapt to dark mode in Gmail, Apple Mail, Outlook.com.

**Fix:** Add `prefers-color-scheme` media query and dark mode colors:
```html
<!--[if !mso]><!-->
<style type="text/css">
  @media (prefers-color-scheme: dark) {
    .email-signature { color: #e0e0e0 !important; }
    .email-signature-bg { background-color: #1a1a1a !important; }
  }
</style>
<!--<![endif]-->
```

**Impact:** Signature may be hard to read in dark mode email clients.

---

### 8. Image Blocking Fallbacks Missing
**Issue:** If external images are blocked, phone/email icons disappear with no text fallback.

**Current Code:**
```html
<a href="tel:{{MobilePhoneRaw}}" style="color:#333333;text-decoration:none;">
  <img src="https://proaktiv.no/assets/logos/phone.png" width="14" height="14" style="vertical-align:middle;border:0;margin-right:6px;">{{MobilePhone}}
</a>
```

**Fix:**
```html
<a href="tel:{{MobilePhoneRaw}}" style="color:#333333;text-decoration:none;">
  <img src="https://proaktiv.no/assets/logos/phone.png" width="14" height="14" alt="📞" style="vertical-align:middle;border:0;margin-right:6px;">{{MobilePhone}}
</a>
<!-- Alt text with emoji provides visual fallback -->
```

**Impact:** Users with image blocking see broken image icons instead of meaningful content.

---

### 9. Social Media Icons Have No Alt Text
**Location:** Lines 49, 55, 61, 67  
**Issue:** Social media icons have no `alt` text. If images are blocked, users see nothing.

**Current Code:**
```html
<img src="https://proaktiv.no/assets/logos/lilje_clean_52.png" width="26" height="26" style="display:block;border:0;">
```

**Fix:**
```html
<img src="https://proaktiv.no/assets/logos/lilje_clean_52.png" width="26" height="26" alt="Proaktiv" style="display:block;border:0;">
<!-- Add descriptive alt text for each icon -->
```

**Impact:** Accessibility issue and poor UX when images are blocked.

---

### 10. `line-height` May Be Overridden
**Location:** Line 84  
**Issue:** Some email clients override `line-height` values, especially on small text.

**Current Code:**
```html
<div style="color:#888888;font-size:9px;line-height:1.4;max-width:516px;">
```

**Fix:**
```html
<!-- Use !important for critical line-height, or use table cell -->
<td style="color:#888888;font-size:9px;line-height:1.4 !important;width:516px;">
```

**Impact:** Disclaimer text may have inconsistent line spacing.

---

### 11. Font Size in Pixels May Be Scaled
**Issue:** Some mobile email clients scale pixel-based font sizes inconsistently.

**Recommendation:** Consider using `em` or `rem` units for better mobile scaling, but this is lower priority since most clients handle px reasonably.

---

### 12. `vertical-align:middle` on Images
**Location:** Lines 21, 26  
**Issue:** `vertical-align` on images can be inconsistent across clients, especially in table cells.

**Current Code:**
```html
<img src="..." style="vertical-align:middle;border:0;margin-right:6px;">
```

**Fix:**
```html
<!-- Use table cell alignment instead -->
<td style="vertical-align:middle;">
  <img src="..." style="border:0;margin-right:6px;">
</td>
```

**Impact:** Icons may not align properly with text in some clients.

---

## 🟢 MINOR ISSUES (Best Practices)

### 13. Missing `lang` Attribute
**Issue:** HTML tag should specify language for accessibility.

**Fix:**
```html
<html lang="no">
```

---

### 14. Missing Viewport Meta Tag
**Issue:** No viewport meta tag for mobile optimization.

**Fix:**
```html
<meta name="viewport" content="width=device-width, initial-scale=1.0">
```

**Note:** Some email clients ignore this, but it's best practice.

---

### 15. Font Stack Could Be More Robust
**Current:** `Arial,Helvetica,sans-serif`

**Better:**
```html
font-family:Arial,Helvetica,'Helvetica Neue',sans-serif;
```

---

### 16. Hardcoded Organization Number
**Location:** Line 79  
**Issue:** Organization number is hardcoded. Should be a placeholder if it varies by office.

**Current Code:**
```html
{{OfficeName}} – Org. nr. 912 404 447 | {{OfficeAddress}}, {{OfficePostal}}
```

**Fix:**
```html
{{OfficeName}} – Org. nr. {{OfficeOrgNumber}} | {{OfficeAddress}}, {{OfficePostal}}
```

---

### 17. Missing `role="presentation"` on Layout Tables
**Issue:** Layout tables should have `role="presentation"` for accessibility.

**Fix:**
```html
<table cellpadding="0" cellspacing="0" border="0" role="presentation" style="...">
```

---

### 18. `display:block` on Images May Cause Spacing Issues
**Location:** Lines 14, 40, 49, 55, 61, 67  
**Issue:** `display:block` can cause unexpected spacing in some clients.

**Recommendation:** Keep `display:block` but ensure proper `line-height` and `font-size` on parent elements.

---

## 📋 PRIORITY FIX RECOMMENDATIONS

### Immediate (Critical)
1. ✅ Remove `object-fit:cover` (Line 14)
2. ✅ Fix `height="auto"` on logo (Line 40)
3. ✅ Replace `div` with `td` for disclaimer (Line 84)
4. ✅ Add `alt` text to all images
5. ✅ Add `rel="noopener"` to links

### High Priority (Moderate)
6. ✅ Add dark mode support
7. ✅ Add MSO conditionals for Outlook
8. ✅ Fix `vertical-align` issues
9. ✅ Add image blocking fallbacks

### Nice to Have (Minor)
10. ✅ Add `lang="no"` attribute
11. ✅ Add viewport meta tag
12. ✅ Improve font stack
13. ✅ Add `role="presentation"` to tables

---

## 🔧 COMPLETE FIXED TEMPLATE

See `email-signature-fixed.html` for the fully corrected version with all critical and moderate issues addressed.

---

## 📚 EMAIL CLIENT TESTING CHECKLIST

Test the fixed template in:
- [ ] Outlook 2016 (Windows)
- [ ] Outlook 2019 (Windows)
- [ ] Outlook 2021 (Windows)
- [ ] Outlook 365 (Windows)
- [ ] Outlook.com (Web)
- [ ] Gmail (Web)
- [ ] Gmail (Android App)
- [ ] Apple Mail (macOS)
- [ ] iOS Mail (iPhone)
- [ ] Yahoo Mail (Web)
- [ ] Dark mode in Gmail
- [ ] Dark mode in Apple Mail
- [ ] Image blocking enabled
- [ ] Mobile viewport (320px, 375px, 414px)

---

## 📖 REFERENCES

- [Can I Email](https://www.caniemail.com/) - CSS/HTML email support database
- [Email on Acid](https://www.emailonacid.com/) - Email testing service
- [Litmus](https://www.litmus.com/) - Email testing and analytics
- [Campaign Monitor CSS Guide](https://www.campaignmonitor.com/css/) - Email CSS support guide
