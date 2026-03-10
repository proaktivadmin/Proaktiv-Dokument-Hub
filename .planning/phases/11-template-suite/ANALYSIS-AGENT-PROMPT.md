# Deep Analysis: Vitec Template Pipeline Quality Assessment

You are a dedicated analysis agent. Your task is to perform a systematic comparison between our generated Vitec Next HTML templates, the original source documents, and working production reference templates from Vitec. The goal is to produce a comprehensive findings report that identifies every deviation, flags rendering issues, and recommends specific pipeline improvements.

## Context

We built two templates through our pipeline. The second was live-verified in Vitec's test system (Testfletting) and the resulting PDF had critical issues: Norwegian characters rendered as mojibake (ø→Ã¸, å→Ã¥, §→Â§) and checkboxes rendered as "?". A previous analysis session has already produced a `TEMPLATE-ANALYSIS-REPORT.md` with findings. Your job is to verify, extend, or re-run the analysis as needed.

---

## Pre-Flight: Setup and Extract Reference Data

Before starting analysis, prepare reference files and tooling:

### 1. Extract FORBRUKER Reference Template

If it doesn't already exist at `scripts/reference_templates/Kjopekontrakt_FORBRUKER_REFERENCE.html`:

```python
import json
with open(r'C:\Users\Adrian\Documents\Proaktiv-Dokument-Hub\data\vitec-next-export.json', 'r', encoding='utf-8') as f:
    data = json.load(f)
for t in data['templates']:
    if t.get('vitec_template_id') == 'ce208318-fa6e-43b5-a78c-3eec3a3c10ea':
        with open(r'...\Kjopekontrakt_FORBRUKER_REFERENCE.html', 'w', encoding='utf-8') as out:
            out.write(t['content'])
        break
```

### 2. Copy Source Files for Preview (if not already done)

Run `C:\Users\Adrian\Documents\Proaktiv-Dokument-Hub\scripts\copy_sources.py` to copy original Word-exported `.htm` files from the OneDrive download into the `converted_html/` preview directory.

### 3. Start Preview Server

```bash
python -m http.server 8765 --directory "C:\Users\Adrian\Documents\Proaktiv-Dokument-Hub\scripts\converted_html"
```

This serves all preview files at `http://localhost:8765/`. The browser MCP tool can then navigate to these URLs for visual inspection.

---

## Available Scripts and Tools

All scripts are in `C:\Users\Adrian\Documents\Proaktiv-Dokument-Hub\scripts\`:

| Script | Purpose |
|--------|---------|
| `build_production_template.py` | Enebolig builder (BeautifulSoup-based, parses source HTM) |
| `build_kjopekontrakt_prosjekt_leilighet.py` | Leilighet builder (hardcoded template string, source: `8966142_3.htm`) |
| `build_preview.py` | Build A4-like annotated preview for enebolig production template |
| `build_preview_leilighet.py` | Build A4-like annotated preview for leilighet production template |
| `build_reference_preview.py` | Build annotated preview for bruktbolig reference template (includes SVG checkbox CSS) |
| `convert_docx_preview.py` | Convert `.docx` source to HTML preview via mammoth |
| `copy_sources.py` | Copy source `.htm` files from OneDrive download to preview directory |
| `compare_source_vs_production.py` | Automated content comparison: legacy fields, sections, checkboxes, key phrases |
| `count_checkboxes.py` | Count checkbox encoding types (entity vs literal Unicode) in production templates |
| `validate_template.py` | Enebolig validator (14-point checklist — has known false assumptions) |
| `validate_leilighet.py` | Leilighet validator |

### Preview Tool Architecture

The `build_preview*.py` scripts wrap production templates in an A4-like viewer with:
- Sticky info bar (field count, vitec-if count, foreach count, sections)
- Merge field highlighting (yellow `<span class="mf">`)
- vitec-if visual indicators (green left-border + "if" badge)
- vitec-foreach visual indicators (blue left-border + "foreach" badge)
- A4 page wrapper (21cm max-width, 2.5cm padding, box-shadow)

Color-coded header bars distinguish file types:
- **Navy** = Our production templates
- **Green** = Working Vitec reference templates (gold standard)
- **Brown** = Original DOCX source (via mammoth conversion)
- **White** = Word .htm export source

---

## Files to Read and Compare

### Our Generated Templates (READ BOTH)

- `scripts/production/Kjopekontrakt_prosjekt_enebolig_PRODUCTION.html` — pilot template (~38 KB)
- `scripts/production/Kjopekontrakt_prosjekt_leilighet_PRODUCTION.html` — second template (~37 KB), live-verified in Vitec Testfletting

### Our Build Scripts (READ BOTH — compare approaches)

- `scripts/build_production_template.py` — enebolig builder (BeautifulSoup-based, 770 lines)
- `scripts/build_kjopekontrakt_prosjekt_leilighet.py` — leilighet builder (hardcoded template, ~623 lines)

### Our Validators (READ BOTH)

- `scripts/validate_template.py` — enebolig validator
- `scripts/validate_leilighet.py` — leilighet validator

### Original Source Documents

All in `C:\Users\Adrian\Downloads\OneDrive_2026-02-21\maler vi må få produsert\`:

| Source File (.htm) | RTF Counterpart | Template Built |
|--------------------|-----------------|----------------|
| `Kjøpekontrakt prosjekt (enebolig med delinnbetalinger).htm` | In `konvertert/` | Enebolig (pilot) |
| `Kjøpekontrakt prosjekt selveier.htm` | In `konvertert/` | Leilighet (second) |
| `Kjøpekontrakt prosjekt profesjonell kjøper.htm` | In `konvertert/` | Not yet |
| `Kjøpekontrakt prosjekt Borettslag.htm` | In `konvertert/` | Not yet |
| `Meglerstandard for eiendom med og uten oppgjørsansvarlig.htm` | In `konvertert/` | Not yet |
| `E-takst oppdragsavtale.htm` | In `konvertert/` | Not yet |

Additional source files:
- `C:\Users\Adrian\Downloads\Kjøpekontrakt Prosjekt selveier .docx` — Original DOCX for selveier (can be converted via mammoth using `convert_docx_preview.py`)
- `scripts/source_htm/Kjopekontrakt_prosjekt_enebolig.htm` — Copy of enebolig source (104 KB, windows-1252)

**IMPORTANT:** The file previously referenced as `8966142_3.htm` no longer exists locally. The actual selveier source is `Kjøpekontrakt prosjekt selveier.htm` from the OneDrive download.

### Working Vitec Reference Templates (Gold Standard)

- `C:\Users\Adrian\Downloads\kjøpekontrakt bruktbolig html.html` — **PRIMARY reference** (~101 KB). Working bruktbolig kjøpekontrakt. Most directly comparable to our contracts. 64 merge fields, 173 vitec-if, 9 foreach.
- `C:\Users\Adrian\Downloads\oppdragsavtale prosjekt.html` — **Supplementary reference**. Shows additional patterns (insert-textbox, info-table, sign-field).
- `scripts/reference_templates/Kjopekontrakt_FORBRUKER_REFERENCE.html` — **Secondary reference** (~95 KB). Extracted from `vitec-next-export.json`. Shows SVG checkbox patterns and extensive conditional branching.

### Pre-Generated Preview Files (in `scripts/converted_html/`)

| Preview File | Type | Server URL |
|-------------|------|-----------|
| `preview_production.html` | Enebolig production preview | `http://localhost:8765/preview_production.html` |
| `Kjopekontrakt_prosjekt_leilighet_PREVIEW.html` | Leilighet production preview | `http://localhost:8765/Kjopekontrakt_prosjekt_leilighet_PREVIEW.html` |
| `REFERENCE_bruktbolig_PREVIEW.html` | Reference template preview | `http://localhost:8765/REFERENCE_bruktbolig_PREVIEW.html` |
| `SOURCE_enebolig.htm` | Enebolig Word source | `http://localhost:8765/SOURCE_enebolig.htm` |
| `SOURCE_selveier_leilighet.htm` | Selveier/leilighet Word source | `http://localhost:8765/SOURCE_selveier_leilighet.htm` |
| `SOURCE_selveier_DOCX.html` | Selveier DOCX (via mammoth) | `http://localhost:8765/SOURCE_selveier_DOCX.html` |
| `SOURCE_profesjonell_kjoper.htm` | Profesjonell kjøper source | `http://localhost:8765/SOURCE_profesjonell_kjoper.htm` |
| `SOURCE_borettslag.htm` | Borettslag source | `http://localhost:8765/SOURCE_borettslag.htm` |

### Pipeline Design Documents (for context)

- `.planning/phases/11-template-suite/AGENT-2B-PIPELINE-DESIGN.md`
- `.planning/phases/11-template-suite/PRODUCTION-TEMPLATE-PIPELINE.md`

### Previous Analysis Report

- `.planning/phases/11-template-suite/TEMPLATE-ANALYSIS-REPORT.md` — Comprehensive report from previous analysis session. Review this first to avoid duplicate work. Extend or correct as needed.

---

## Analysis Framework: 11 Dimensions

Analyze each dimension systematically. For every finding, cite specific code from both our template AND the reference template side-by-side.

### D0: Internal Consistency (Enebolig vs. Leilighet)

Compare our two generated templates against each other:

- Identify patterns from the pilot (enebolig) that were LOST in the second build (leilighet).
- **Known regressions (confirmed):** enebolig uses `<h1>` for title, leilighet uses `<h5>`; enebolig wraps header in outer `<table>`, leilighet does not; enebolig has `.sign-line` and `.liste` CSS, leilighet does not; enebolig uses «guillemets», leilighet uses "curly quotes".
- Compare the two build approaches: BeautifulSoup programmatic parsing vs. hardcoded template string. Which is more maintainable?

### D1: Encoding and Character Handling

- **Confirmed critical:** Our templates use literal UTF-8 characters. Working references use HTML entities (`&oslash;`, `&aring;`, `&aelig;`, `&sect;`) in body text and `\xF8` unicode escapes inside `vitec-if` attribute strings.
- Map exactly which characters MUST be entities for CKEditor/Vitec PDF rendering.

### D2: Checkbox and Interactive Element Patterns

- **Confirmed critical:** Working references use SVG-based interactive checkboxes (`label.btn` + `.svg-toggle.checkbox` + `data-toggle="buttons"` with inline SVG data URIs). Our templates use `&#9744;`/`&#9745;` HTML entities which render as "?" in PDF.
- The full SVG checkbox CSS block has been extracted and is in the Reference Patterns Library section of the existing report.

### D3: DOM Structure and Layout Architecture

- **Confirmed:** Working references wrap body in `<table><tbody><tr><td colspan="100">...</td></tr></tbody></table>`. Our leilighet template lacks this (regression from enebolig).
- Check `class="proaktiv-theme"` — references don't use it.

### D4: CSS Counter and Numbering System

- Compare counter patterns across references (bruktbolig uses `section`/`subsection`, FORBRUKER uses `item`/`counters(item, ".")`).

### D5: Merge Field Coverage and Accuracy

- Enebolig production has 48 modern merge fields expanded from 13 legacy fields.
- Leilighet production has 39 modern merge fields (fewer — missing some like `[[dagensdato]]`, `[[komplettmatrikkel]]`, `[[eiendom.ettaarsbefaring.dato]]`).
- Check `$.UD()` and `$.CALC()` usage consistency.

### D6: Conditional Logic Patterns

- Reference template has 173 vitec-if (3-4x more than ours). This is expected due to different contract scope.
- Compare vitec-if escaping patterns.

### D7: Content Fidelity (Source Document vs. Production)

**Run `compare_source_vs_production.py` or perform equivalent manual analysis.**

Key confirmed findings:
- All 22 sections from source documents are present in both production templates.
- Text content preservation is ~99% (22,477 chars source vs 22,225 chars production for enebolig).
- **[CRITICAL] Leilighet uses wrong payment model:** The selveier source has "Alternativ 1: Forskudd" / "Alternativ 2: Full payment" but the production template uses the enebolig's "For tomten" / "For boligen" delinnbetalinger structure instead.
- **[IMPORTANT] Missing guarantee paragraphs in leilighet:** forskuddsbetaling, forskuddsgaranti provisions from bustadoppføringslova §§ 12 and 47 are absent.
- **[COSMETIC] Missing "Eierseksjonsloven" reference in enebolig**, "Alternativ 1/2" labels dropped from both.

### D8: Validator Gap Analysis

- Validators check for `class="proaktiv-theme"` (false assumption — references don't have it).
- Validators check for literal Norwegian characters (incorrect — should check for entities).
- Missing checks: SVG checkboxes, outer table wrapper, `data-label` on inserts, correct title tag, consistent `$.UD()` usage.
- Recommendation: Unify `validate_template.py` and `validate_leilighet.py` into a single parameterized validator.

### D9: Visual Comparison (Browser-Rendered)

**Use the preview server and browser MCP tool for visual inspection.**

Compare rendered output across:
1. Source Word documents (`.htm` exports and DOCX via mammoth)
2. Our production template previews (annotated with merge field highlighting)
3. Working Vitec reference template preview

Key visual areas to inspect:
- Header layout (left-aligned paragraphs vs right-aligned table wrapper)
- Title rendering (`<h1>` vs `<h5>` sizing)
- Checkbox rendering (Unicode symbols vs SVG graphics)
- Section numbering (CSS counters in action)
- Conditional logic density (vitec-if/foreach indicator borders)
- Cross-reference navigation (bookmark links in reference)
- Parties table structure (column widths, rowspan usage)

### D10: Source-to-Production Content Diff

**Run `compare_source_vs_production.py` for automated analysis.**

This compares:
- HTML size reduction (source ~100KB Word markup → production ~37KB clean HTML)
- Text content preservation (should be ~99%)
- Legacy merge field mapping (13 `#field¤` → 39-48 `[[field]]` modern fields)
- Checkbox count mapping (source "q" chars vs production `&#9744;`/`&#9745;` entities)
- Section presence verification (all sections from source must exist in production)
- Key legal phrase presence (Eierseksjonsloven, forskuddsbetaling, Alternativ 1/2, etc.)

Also verify against the original `.docx` file using `convert_docx_preview.py` to confirm no data loss in the Word-to-HTM export step.

---

## Output

Write your complete analysis to:

`.planning/phases/11-template-suite/TEMPLATE-ANALYSIS-REPORT.md`

If the report already exists, review the existing findings and either:
- **Verify and extend** — add new findings, correct inaccuracies, fill gaps
- **Re-run from scratch** — if significant new data or templates are available

Use this structure:

```
# Vitec Template Analysis Report

## Executive Summary
[Top findings ranked by impact — what MUST change before the next template build]

## Visual Comparison (Browser-Rendered)
[Screenshots and observations from browser rendering of all previews]

## Source Document vs. Production Template Comparison
[Automated and manual content diff between Word source and production HTML]

## D0: Internal Consistency
### Findings
[Each finding with CRITICAL/IMPORTANT/COSMETIC/INFO severity]
### Evidence
[Side-by-side code snippets from both templates]
### Recommendation
[Specific action items]

## D1: Encoding and Character Handling
[Same structure for each dimension...]

[... D2 through D10 ...]

## Pipeline Improvement Actions
[Categorized list of specific changes needed in each file:]
- AGENT-2B-PIPELINE-DESIGN.md: [changes]
- SKILL.md: [changes]
- validate_template.py: [changes]
- PRODUCTION-TEMPLATE-PIPELINE.md: [changes]
- Build approach: [changes]

## Reference Patterns Library
[Complete, copy-pasteable code blocks for standard patterns:]
- SVG checkbox CSS + HTML markup
- Norwegian character entity encoding map
- Outer table wrapper structure
- insert-table / data-label pattern
- Page break pattern
- Signature block pattern
- Counter CSS pattern variants
- Roles table with rowspan
- Bookmark/anchor cross-reference
- Inline list (.liste / .separator)
```

### Severity Levels

- **CRITICAL**: Breaks rendering in PDF (encoding, checkboxes, content mismatch)
- **IMPORTANT**: Structural deviation from Vitec patterns that may cause issues
- **COSMETIC**: Style preference that doesn't affect function
- **INFO**: Notable observation, no action needed

---

## Key Confirmed Findings (from previous analysis)

These have been verified and should be treated as established facts:

1. **UTF-8 literals → HTML entities** (CRITICAL): Body text must use `&oslash;`, `&aring;`, `&aelig;`, `&sect;`, etc. Vitec-if attributes use `\xF8` unicode escapes.
2. **Unicode checkboxes → SVG pattern** (CRITICAL): Replace `&#9744;`/`&#9745;` with the SVG data URI checkbox system from the reference.
3. **Missing outer table wrapper** (IMPORTANT): Wrap body in `<table><tbody><tr><td colspan="100">`.
4. **Wrong payment model in leilighet** (CRITICAL): Uses enebolig delinnbetalinger instead of selveier Alternativ 1/2.
5. **Missing guarantee provisions** (IMPORTANT): forskuddsbetaling and forskuddsgaranti paragraphs omitted from leilighet.
6. **`proaktiv-theme` class** (IMPORTANT): Not used by any reference template — remove.
7. **Leilighet regressions** (IMPORTANT): `<h5>` title, missing table header wrapper, missing `.sign-line`/`.liste` CSS, wrong quote style.
8. **Validator false assumptions** (COSMETIC): Checks for `proaktiv-theme`, literal characters instead of entities.

Be thorough and specific. Cite line numbers. Show code from BOTH sides. This report will directly drive pipeline improvements.
