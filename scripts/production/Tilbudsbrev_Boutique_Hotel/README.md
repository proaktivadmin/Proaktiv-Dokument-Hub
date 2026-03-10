# Tilbudsbrev Boutique Hotel — Versioned Template

Incremental visual upgrades for safe rollback if Vitec PDF generation fails.

## Version Overview

| Version | File | Changes | Use when |
|---------|------|---------|----------|
| **v01** | `v01_baseline.html` | Current working state (no visual upgrades) | Fallback if any upgrade causes crash |
| **v02** | `v02_summary_styling.html` | Total-info: bold, underline, navy (#272630) | Test summary line emphasis only |
| **v03** | `v03_section_spacing.html` | v02 + section spacing (18px), sum-box margin (36px) | Test spacing changes |
| **v04** | `v04_row_polish.html` | v03 + row padding (6px), sum-row padding (8px) | Test row polish |
| **v99** | `v99_FINAL.html` | All upgrades combined (= v04) | Deploy when all tests pass |

## Workflow

1. **Deploy v99_FINAL** first — if PDF generates OK, you're done.
2. **If v99 crashes** — copy `v04_row_polish.html` into Vitec and test.
3. **If v04 crashes** — try `v03_section_spacing.html`.
4. **If v03 crashes** — try `v02_summary_styling.html`.
5. **If v02 crashes** — stay on `v01_baseline.html` (current production).

## Deploy to Vitec

Copy the desired `.html` file contents into the template in Vitec Next.  
The root `Tilbudsbrev_Boutique_Hotel_PRODUCTION.html` in `scripts/production/` mirrors v01 baseline.

## What Did NOT Cause the Earlier Crash

- Summary styling (bold, underline, color)
- Google Fonts `@import`
- Inline SVG logo
- CSS L-brackets (qf-tr, qf-bl)

The crash was caused by inline `@functions` and `@{}` blocks (Boligselgerforsikring). Those have been removed.
