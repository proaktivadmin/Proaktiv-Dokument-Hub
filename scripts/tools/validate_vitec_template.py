"""
Unified Vitec Next template validator.

Validates production templates against the complete quality checklist
from AGENT-2B-PIPELINE-DESIGN.md and PRODUCTION-TEMPLATE-PIPELINE.md.

Usage:
    python validate_vitec_template.py <template.html>
    python validate_vitec_template.py <template.html> --tier 4
    python validate_vitec_template.py <template.html> --compare-snapshot snapshot.html
"""

import argparse
import re
import os
import sys


def read_file(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read()


NORWEGIAN_LITERALS = re.compile(r"[æøåÆØÅ§«»–—é]")
NORWEGIAN_IN_MERGE_FIELD = re.compile(r"\[\[[^\]]*[æøåÆØÅ]\w*[^\]]*\]\]")


def validate(html: str, tier: int = 4) -> list[tuple[str, bool, str]]:
    results = []

    def check(section: str, name: str, passed: bool, detail: str = ""):
        results.append((f"[{section}] {name}", passed, detail))

    # ===================== A. Template Shell =====================
    has_vitec_id = 'id="vitecTemplate"' in html
    has_proaktiv_theme = 'class="proaktiv-theme"' in html

    check("A", "vitecTemplate wrapper div",
          has_vitec_id,
          'Missing id="vitecTemplate"' if not has_vitec_id else "")

    check("A", "No proaktiv-theme class (Proaktiv convention, not Vitec standard — 0/249 official templates use it)",
          not has_proaktiv_theme,
          'Remove class="proaktiv-theme" from root div')

    check("A", "Stilark resource span",
          'vitec-template="resource:Vitec Stilark"' in html)

    stilark_match = re.search(r'vitec-template="resource:Vitec Stilark">\s*&nbsp;\s*</span>', html)
    check("A", "Stilark span contains &nbsp;", stilark_match is not None)

    check("A", "Outer table body wrapper",
          bool(re.search(r'<table[^>]*>\s*<tbody', html)),
          "Template should have an outer <table><tbody> wrapper for body content")

    check("A", "H1 title element",
          "<h1>" in html or "<h1 " in html,
          "Use <h1> for the template title, not <h5> or other levels")

    has_h1_css = "h1" in html and "font-size: 14pt" in html or "font-size:14pt" in html
    check("A", "H1 CSS styling in style block",
          has_h1_css,
          "Add #vitecTemplate h1 { text-align: center; font-size: 14pt; } to <style>")

    has_h2_css = bool(re.search(r"margin:\s*30px\s+0\s+0\s+-20px", html))
    check("A", "H2 CSS styling with negative margin (-20px)",
          has_h2_css,
          "Add #vitecTemplate h2 { font-size: 11pt; margin: 30px 0 0 -20px; } to <style>")

    has_article_padding = bool(re.search(r"article\s*\{[^}]*padding-left:\s*20px", html))
    check("A", "Article padding-left: 20px (production standard)",
          has_article_padding or tier < 3,
          "Use padding-left: 20px (not 26px) — matches production Bruktbolig/FORBRUKER")

    has_insert_table = "display: inline-table" in html or "display:inline-table" in html
    check("A", "Chromium insert-table fix (.insert-table { display: inline-table })",
          has_insert_table or tier < 3,
          "Missing .insert-table { display: inline-table; } — critical for Chromium rendering")

    # ===================== A2. Post-Processor Checks =====================
    has_svg_css = "svg-toggle" in html and "label.btn" in html
    check("A2", "SVG checkbox CSS present (from PATTERNS.md)",
          has_svg_css or tier < 3,
          "Missing SVG checkbox CSS block. Copy from PATTERNS.md section 4." if tier >= 3 else "")

    has_insert_css = "span.insert:empty" in html
    check("A2", "Insert field CSS present",
          has_insert_css or tier < 3,
          "Missing insert-field CSS block. Copy from PATTERNS.md section 3." if tier >= 3 else "")

    style_end_pos = html.rfind("</style>")
    if style_end_pos > 0:
        after_style = html[style_end_pos + 8:].strip()
        has_table_after_style = after_style.startswith("<table")
        check("A2", "Outer table wrapper after </style>",
              has_table_after_style,
              "Body content must be inside <table><tbody><tr><td colspan=\"100\">")
    else:
        check("A2", "Has style block", False, "No </style> tag found")

    # ===================== B. Table Structure =====================
    check("B", "No CSS flexbox/grid",
          "display:flex" not in html and "display:grid" not in html and "display: flex" not in html)

    orphan_tr = re.findall(r"<table[^>]*>\s*<tr", html)
    check("B", "No orphan <tr> outside tbody/thead", len(orphan_tr) == 0,
          f"Found {len(orphan_tr)} orphan <tr>")

    check("B", "Uses 100-unit colspan system",
          'colspan="100"' in html or 'colspan="50"' in html or 'colspan="45"' in html)

    # ===================== C. Inline Styles =====================
    font_family_inline = re.findall(r'style="[^"]*font-family[^"]*"', html)
    check("C", "No inline font-family", len(font_family_inline) == 0,
          f"Found {len(font_family_inline)} inline font-family")

    font_size_inline = re.findall(r'style="[^"]*font-size[^"]*"', html)
    check("C", "No inline font-size", len(font_size_inline) == 0,
          f"Found {len(font_size_inline)} inline font-size")

    # ===================== D. Merge Fields =====================
    merge_fields = re.findall(r"\[\[[\*]?([^\]]+)\]\]", html)
    check("D", "Merge fields use [[field]] syntax", len(merge_fields) > 0,
          f"Found {len(merge_fields)} merge fields")

    bad_spaces = re.findall(r"\[\[\s+|\s+\]\]", html)
    check("D", "No spaces inside brackets", len(bad_spaces) == 0,
          f"Found {len(bad_spaces)} with spaces")

    legacy_fields = re.findall(r"#\w+\.\w+¤", html)
    check("D", "No legacy #field.context¤ syntax", len(legacy_fields) == 0,
          f"Found legacy: {legacy_fields}")

    # ===================== E. Conditional Logic =====================
    vitec_ifs = re.findall(r'vitec-if="([^"]*)"', html)
    check("E", "Has vitec-if conditions", len(vitec_ifs) > 0,
          f"Found {len(vitec_ifs)} conditions")

    bad_quotes = [v for v in vitec_ifs if '"' in v.replace("&quot;", "").replace("&amp;", "")]
    check("E", "String comparisons use &quot;", len(bad_quotes) == 0,
          f"Bad: {bad_quotes[:3]}")

    bad_gt = [v for v in vitec_ifs if re.search(r"(?<!&amp;)(?<!&quot;)(?<!&lt;)(?<!&gt;)(?<!&)>", v)]
    check("E", "Greater-than uses &gt;", len(bad_gt) == 0,
          f"Bad: {bad_gt[:3]}")

    # ===================== F. Iteration =====================
    foreachs = re.findall(r'vitec-foreach="([^"]*)"', html)
    check("F", "Has vitec-foreach loops", len(foreachs) > 0,
          f"Found {len(foreachs)}: {foreachs}")

    foreach_on_tbody = re.findall(r"<tbody\s+vitec-foreach=", html)
    check("F", "Foreach on <tbody> elements", len(foreach_on_tbody) > 0,
          f"Found {len(foreach_on_tbody)} on tbody")

    foreach_parsed = re.findall(r'vitec-foreach="(\w+)\s+in\s+([\w.]+)"', html)

    for item, collection in foreach_parsed:
        guard_pattern = f"{collection}.Count"
        check("F", f"Guard for {collection}", guard_pattern in html,
              f"foreach '{item} in {collection}' has no Count guard")

    for item, collection in foreach_parsed:
        fallback_pattern = f"{collection}.Count == 0"
        check("F", f"Fallback for empty {collection}", fallback_pattern in html,
              f"No '[Mangler ...]' fallback for empty {collection}")

    # ===================== G. Images and SVG =====================
    img_tags = re.findall(r"<img\s[^>]*>", html)
    check("G", "No image tags (contract templates)",
          len(img_tags) == 0 or all("alt=" in img for img in img_tags),
          f"Found {len(img_tags)} images")

    # ===================== H. Form Elements / Checkboxes =====================
    check("H", "Has insert field placeholders", 'class="insert"' in html)

    has_data_label = "data-label=" in html
    check("H", "Insert fields have data-label attributes", has_data_label,
          "Use <span class=\"insert\" data-label=\"...\"> for placeholder text")

    has_insert_table = "insert-table" in html
    check("H", "Insert fields use insert-table wrapper", has_insert_table,
          "Wrap insert spans in <span class=\"insert-table\">")

    unicode_checkboxes = re.findall(r"&#9744;|&#9745;|\u2610|\u2611|☐|☑", html)
    check("H", "No Unicode checkboxes (render as ? in PDF)",
          len(unicode_checkboxes) == 0,
          f"Found {len(unicode_checkboxes)} Unicode checkboxes — replace with SVG pattern from PATTERNS.md section 5/6")

    data_driven_with_input = re.findall(
        r'vitec-if="[^"]*">\s*<label[^>]*>\s*<input\s+type="checkbox"', html
    )
    check("H", "Data-driven checkboxes have no <input> tag",
          len(data_driven_with_input) == 0,
          f"Found {len(data_driven_with_input)} data-driven checkboxes with <input> — remove the input element")

    # ===================== I. Text and Formatting =====================
    font_tags = re.findall(r"<font\b", html)
    check("I", "No <font> tags", len(font_tags) == 0,
          f"Found {len(font_tags)}")

    center_tags = re.findall(r"<center\b", html)
    check("I", "No <center> tags", len(center_tags) == 0,
          f"Found {len(center_tags)}")

    # Entity encoding checks: Norwegian characters must be HTML entities
    text_content = re.sub(r"<[^>]+>", "", html)
    text_content = re.sub(r"\[\[[^\]]*\]\]", "", text_content)
    text_content = re.sub(r'vitec-if="[^"]*"', "", text_content)
    text_content = re.sub(r'vitec-foreach="[^"]*"', "", text_content)

    literal_norwegian = NORWEGIAN_LITERALS.findall(text_content)
    check("I", "Norwegian chars are HTML entities (not literal UTF-8)",
          len(literal_norwegian) == 0,
          f"Found {len(literal_norwegian)} literal chars: {set(literal_norwegian)}" if literal_norwegian else "")

    has_entities = any(e in html for e in ["&oslash;", "&aring;", "&aelig;",
                                            "&Oslash;", "&Aring;", "&AElig;", "&sect;"])
    check("I", "HTML entities present for Norwegian characters", has_entities,
          "Expected &oslash;, &aring;, &aelig; etc. in template content")

    # ===================== J. Contract-Specific (T3+ only) =====================
    if tier >= 3:
        check("J", "Uses <article class='item'>",
              '<article class="item">' in html or '<article class="avoid-page-break item">' in html)

        check("J", "CSS counters present",
              "counter-reset: section" in html and "counter-increment: section" in html)

        check("J", "Dual counter pattern (section/subsection)",
              "subsection" in html)

        check("J", "H2 in top-level articles", "<h2>" in html)

        check("J", "roles-table class present", 'class="roles-table"' in html)

        check("J", "Signature block with border-bottom",
              "border-bottom" in html and "solid 1px #000" in html)

        monetary_fields = re.findall(
            r"\[\[(?:kontrakt\.kjopesum|kontrakt\.totaleomkostninger|"
            r"kontrakt\.kjopesumogomkostn|kostnad\.belop|eiendom\.fellesutgifter)\]\]",
            html,
        )
        monetary_with_ud = re.findall(
            r"\$\.UD\(\[\[(?:kontrakt\.kjopesum|kontrakt\.totaleomkostninger|"
            r"kontrakt\.kjopesumogomkostn|kostnad\.belop|eiendom\.fellesutgifter)\]\]\)",
            html,
        )
        check("J", "Monetary fields use $.UD() wrapper",
              len(monetary_fields) == 0 or len(monetary_with_ud) > 0,
              f"Found {len(monetary_fields)} bare monetary fields without $.UD()")

    # ===================== L. Page Break Analysis =====================
    apb_elements = re.findall(r'class="[^"]*avoid-page-break[^"]*"', html)
    apb_count = len(apb_elements)
    forced_breaks = re.findall(r'page-break-before:\s*always', html)
    fb_count = len(forced_breaks)
    total_articles = len(re.findall(r'<article\b', html))
    protected_articles = len(re.findall(r'<article[^>]*avoid-page-break', html))
    apb_divs = len(re.findall(r'<div[^>]*avoid-page-break', html))

    if tier >= 3:
        check("L", "avoid-page-break CSS rule in style block",
              "#vitecTemplate .avoid-page-break" in html,
              "Add #vitecTemplate .avoid-page-break { page-break-inside: avoid; }")

        min_wrappers = max(5, total_articles // 2)
        check("L", f"Sufficient page break wrappers ({apb_count} found, min {min_wrappers})",
              apb_count >= min_wrappers,
              f"Only {apb_count} wrappers for {total_articles} sections. "
              f"Golden standard uses 20-30. Add avoid-page-break to headings, tables, and short sections.")

        unprotected = total_articles - protected_articles
        check("L", f"Article sections protected ({protected_articles}/{total_articles})",
              protected_articles >= total_articles // 3,
              f"{unprotected} articles without avoid-page-break class. "
              f"Short sections should have class=\"avoid-page-break item\" on their article.")

        if fb_count > 0:
            check("L", f"Forced page breaks present ({fb_count})", True)

    # ===================== K. Final Validation =====================
    check("K", "Well-formed HTML (basic check)",
          html.count("<article") == html.count("</article>"),
          f"articles: {html.count('<article')} open, {html.count('</article>')} close")

    check("K", "No onclick/onload handlers",
          "onclick" not in html and "onload" not in html)

    check("K", "No external stylesheet links",
          '<link rel="stylesheet"' not in html)

    check("K", "No JavaScript",
          "<script" not in html)

    return results


def compare_snapshot(current_html: str, snapshot_path: str) -> list[tuple[str, bool, str]]:
    """Compare current template against a pre-edit snapshot for Mode A regression detection."""
    results = []
    snapshot_html = read_file(snapshot_path)

    def check(name: str, passed: bool, detail: str = ""):
        results.append((f"[SNAPSHOT] {name}", passed, detail))

    current_fields = set(re.findall(r"\[\[[\*]?([^\]]+)\]\]", current_html))
    snapshot_fields = set(re.findall(r"\[\[[\*]?([^\]]+)\]\]", snapshot_html))
    lost = snapshot_fields - current_fields
    added = current_fields - snapshot_fields
    check("No merge fields lost", len(lost) == 0,
          f"Lost: {sorted(lost)}" if lost else "")
    if added:
        check("New merge fields added", True, f"Added: {sorted(added)}")

    current_ifs = set(re.findall(r'vitec-if="([^"]*)"', current_html))
    snapshot_ifs = set(re.findall(r'vitec-if="([^"]*)"', snapshot_html))
    lost_ifs = snapshot_ifs - current_ifs
    check("No vitec-if conditions lost", len(lost_ifs) == 0,
          f"Lost: {sorted(lost_ifs)}" if lost_ifs else "")

    current_loops = set(re.findall(r'vitec-foreach="([^"]*)"', current_html))
    snapshot_loops = set(re.findall(r'vitec-foreach="([^"]*)"', snapshot_html))
    lost_loops = snapshot_loops - current_loops
    check("No vitec-foreach loops lost", len(lost_loops) == 0,
          f"Lost: {sorted(lost_loops)}" if lost_loops else "")

    current_articles = len(re.findall(r'<article\s+class="[^"]*item[^"]*">', current_html))
    snapshot_articles = len(re.findall(r'<article\s+class="[^"]*item[^"]*">', snapshot_html))
    check("Article count unchanged or increased",
          current_articles >= snapshot_articles,
          f"Was {snapshot_articles}, now {current_articles}")

    return results


def main():
    parser = argparse.ArgumentParser(
        description="Validate a Vitec Next production template",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="Examples:\n"
               "  python validate_vitec_template.py template.html\n"
               "  python validate_vitec_template.py template.html --tier 2\n"
               "  python validate_vitec_template.py template.html --compare-snapshot snapshot.html\n",
    )
    parser.add_argument("template", help="Path to the production HTML template to validate")
    parser.add_argument("--tier", type=int, default=4, choices=[1, 2, 3, 4, 5],
                        help="Complexity tier (1-5). Section J checks are skipped for T1/T2. Default: 4")
    parser.add_argument("--compare-snapshot", metavar="SNAPSHOT",
                        help="Path to a pre-edit snapshot HTML for Mode A regression comparison")
    args = parser.parse_args()

    if not os.path.isfile(args.template):
        print(f"ERROR: Template file not found: {args.template}", file=sys.stderr)
        sys.exit(2)

    html = read_file(args.template)
    results = validate(html, tier=args.tier)

    snapshot_results = []
    if args.compare_snapshot:
        if not os.path.isfile(args.compare_snapshot):
            print(f"ERROR: Snapshot file not found: {args.compare_snapshot}", file=sys.stderr)
            sys.exit(2)
        snapshot_results = compare_snapshot(html, args.compare_snapshot)

    all_results = results + snapshot_results
    passed = sum(1 for _, p, _ in all_results if p)
    failed = sum(1 for _, p, _ in all_results if not p)
    total = len(all_results)

    print(f"{'=' * 60}")
    print("VITEC TEMPLATE VALIDATION REPORT")
    print(f"{'=' * 60}")
    print(f"Template: {os.path.basename(args.template)}")
    print(f"Size: {len(html):,} chars")
    print(f"Tier: T{args.tier}")
    if args.compare_snapshot:
        print(f"Snapshot: {os.path.basename(args.compare_snapshot)}")
    print(f"{'=' * 60}\n")

    for name, p, detail in results:
        status = "PASS" if p else "FAIL"
        icon = "+" if p else "!"
        line = f"  [{icon}] {status}: {name}"
        if detail and not p:
            line += f" -- {detail}"
        print(line)

    if snapshot_results:
        print(f"\n{'=' * 60}")
        print("SNAPSHOT COMPARISON (Mode A regression)")
        print(f"{'=' * 60}\n")
        for name, p, detail in snapshot_results:
            status = "PASS" if p else "FAIL"
            icon = "+" if p else "!"
            line = f"  [{icon}] {status}: {name}"
            if detail:
                line += f" -- {detail}"
            print(line)

    print(f"\n{'=' * 60}")
    print(f"RESULTS: {passed}/{total} passed, {failed} failed")
    print(f"{'=' * 60}")

    merge_fields = sorted(set(re.findall(r"\[\[[\*]?([^\]]+)\]\]", html)))
    print(f"\nMerge fields ({len(merge_fields)}):")
    for f in merge_fields:
        print(f"  [[{f}]]")

    vitec_ifs = re.findall(r'vitec-if="([^"]*)"', html)
    print(f"\nvitec-if conditions ({len(vitec_ifs)}):")
    for expr in sorted(set(vitec_ifs)):
        print(f"  {expr}")

    foreachs = re.findall(r'vitec-foreach="([^"]*)"', html)
    print(f"\nvitec-foreach loops ({len(foreachs)}):")
    for expr in foreachs:
        print(f"  {expr}")

    apb_els = re.findall(r'class="[^"]*avoid-page-break[^"]*"', html)
    fb_els = re.findall(r'page-break-before:\s*always', html)
    total_art = len(re.findall(r'<article\b', html))
    prot_art = len(re.findall(r'<article[^>]*avoid-page-break', html))
    apb_d = len(re.findall(r'<div[^>]*avoid-page-break', html))
    print(f"\nPage break controls:")
    print(f"  avoid-page-break wrappers: {len(apb_els)} ({prot_art} articles + {apb_d} divs)")
    print(f"  forced page breaks: {len(fb_els)}")
    print(f"  articles protected: {prot_art}/{total_art}")

    if failed > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
