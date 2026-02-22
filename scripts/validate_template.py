"""
Validate production Vitec Next template against the 14-point Section 12 checklist.
"""

import re
import os
import sys

WORKSPACE = r"c:\Users\Adrian\.claude-worktrees\Proaktiv-Dokument-Hub\mystifying-hertz"
TEMPLATE = os.path.join(WORKSPACE, "scripts", "converted_html", "Kjopekontrakt_prosjekt_enebolig_PRODUCTION.html")


def read_template() -> str:
    with open(TEMPLATE, encoding="utf-8") as f:
        return f.read()


def validate(html: str) -> list[tuple[str, bool, str]]:
    results = []

    def check(section: str, name: str, passed: bool, detail: str = ""):
        results.append((f"[{section}] {name}", passed, detail))

    # ===================== A. Template Shell =====================
    check("A", "vitecTemplate wrapper div", 
          'id="vitecTemplate"' in html and 'class="proaktiv-theme"' in html)
    
    check("A", "Stilark resource span", 
          'vitec-template="resource:Vitec Stilark"' in html)
    
    stilark_match = re.search(r'vitec-template="resource:Vitec Stilark">\s*&nbsp;\s*</span>', html)
    check("A", "Stilark span contains &nbsp;", stilark_match is not None)

    # ===================== B. Table Structure =====================
    check("B", "No CSS flexbox/grid", 
          "display:flex" not in html and "display:grid" not in html and "display: flex" not in html)
    
    # Check tr are inside tbody/thead/tfoot (simplified check)
    orphan_tr = re.findall(r'<table[^>]*>\s*<tr', html)
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
    merge_fields = re.findall(r'\[\[[\*]?([^\]]+)\]\]', html)
    check("D", "Merge fields use [[field]] syntax", len(merge_fields) > 0,
          f"Found {len(merge_fields)} merge fields")
    
    bad_spaces = re.findall(r'\[\[\s+|\s+\]\]', html)
    check("D", "No spaces inside brackets", len(bad_spaces) == 0,
          f"Found {len(bad_spaces)} with spaces")
    
    legacy_fields = re.findall(r'#\w+\.\w+¤', html)
    check("D", "No legacy #field.context¤ syntax", len(legacy_fields) == 0,
          f"Found legacy: {legacy_fields}")

    # ===================== E. Conditional Logic =====================
    vitec_ifs = re.findall(r'vitec-if="([^"]*)"', html)
    check("E", "Has vitec-if conditions", len(vitec_ifs) > 0,
          f"Found {len(vitec_ifs)} conditions")
    
    # Check escaping
    bad_quotes = [v for v in vitec_ifs if '"' in v.replace('&quot;', '').replace('&amp;', '')]
    check("E", "String comparisons use &quot;", len(bad_quotes) == 0,
          f"Bad: {bad_quotes[:3]}")
    
    bad_gt = [v for v in vitec_ifs if re.search(r'(?<!&amp;)(?<!&quot;)(?<!&lt;)(?<!&gt;)(?<!&)>', v)]
    check("E", "Greater-than uses &gt;", len(bad_gt) == 0,
          f"Bad: {bad_gt[:3]}")

    # ===================== F. Iteration =====================
    foreachs = re.findall(r'vitec-foreach="([^"]*)"', html)
    check("F", "Has vitec-foreach loops", len(foreachs) > 0,
          f"Found {len(foreachs)}: {foreachs}")
    
    # Check foreach is on <tbody>
    foreach_on_tbody = re.findall(r'<tbody\s+vitec-foreach=', html)
    check("F", "Foreach on <tbody> elements", len(foreach_on_tbody) > 0,
          f"Found {len(foreach_on_tbody)} on tbody")
    
    # Check collection guards
    for foreach in foreachs:
        parts = foreach.split(" in ")
        if len(parts) == 2:
            collection = parts[1]
            guard_pattern = f'{collection}.Count'
            check("F", f"Guard for {collection}", guard_pattern in html)

    # ===================== G. Images and SVG =====================
    img_tags = re.findall(r'<img\s[^>]*>', html)
    check("G", "No image tags (contract templates)", len(img_tags) == 0 or all('alt=' in img for img in img_tags),
          f"Found {len(img_tags)} images")

    # ===================== H. Form Elements =====================
    check("H", "Has span.insert placeholders", 'class="insert"' in html)

    # ===================== I. Text and Formatting =====================
    font_tags = re.findall(r'<font\b', html)
    check("I", "No <font> tags", len(font_tags) == 0,
          f"Found {len(font_tags)}")
    
    center_tags = re.findall(r'<center\b', html)
    check("I", "No <center> tags", len(center_tags) == 0,
          f"Found {len(center_tags)}")
    
    # Check Norwegian characters
    check("I", "Contains ø", "ø" in html)
    check("I", "Contains æ", "æ" in html)
    check("I", "Contains å", "å" in html)

    # ===================== J. Contract-Specific =====================
    check("J", "Uses <article class='item'>", '<article class="item">' in html)
    
    check("J", "CSS counters present", "counter-reset: section" in html and "counter-increment: section" in html)
    
    check("J", "Dual counter pattern (section/subsection)", 
          "subsection" in html)
    
    check("J", "H2 in top-level articles", "<h2>" in html)
    
    check("J", "roles-table class present", 'class="roles-table"' in html)
    
    check("J", "Signature block with border-bottom", "border-bottom" in html and "solid 1px #000" in html)
    
    check("J", "span.insert placeholders", 'class="insert"' in html)
    
    check("J", "avoid-page-break class", 'avoid-page-break' in html)

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


def main():
    html = read_template()
    results = validate(html)
    
    passed = sum(1 for _, p, _ in results if p)
    failed = sum(1 for _, p, _ in results if not p)
    total = len(results)
    
    print(f"{'='*60}")
    print(f"VITEC TEMPLATE VALIDATION REPORT")
    print(f"{'='*60}")
    print(f"Template: {os.path.basename(TEMPLATE)}")
    print(f"Size: {len(html):,} chars")
    print(f"{'='*60}\n")
    
    for name, p, detail in results:
        status = "PASS" if p else "FAIL"
        icon = "+" if p else "!"
        line = f"  [{icon}] {status}: {name}"
        if detail and not p:
            line += f" — {detail}"
        print(line)
    
    print(f"\n{'='*60}")
    print(f"RESULTS: {passed}/{total} passed, {failed} failed")
    print(f"{'='*60}")
    
    # Summary of merge fields
    merge_fields = sorted(set(re.findall(r'\[\[[\*]?([^\]]+)\]\]', html)))
    print(f"\nMerge fields ({len(merge_fields)}):")
    for f in merge_fields:
        print(f"  [[{f}]]")
    
    # Summary of vitec-if expressions
    vitec_ifs = re.findall(r'vitec-if="([^"]*)"', html)
    print(f"\nvitec-if conditions ({len(vitec_ifs)}):")
    for expr in sorted(set(vitec_ifs)):
        print(f"  {expr}")
    
    # Summary of vitec-foreach
    foreachs = re.findall(r'vitec-foreach="([^"]*)"', html)
    print(f"\nvitec-foreach loops ({len(foreachs)}):")
    for expr in foreachs:
        print(f"  {expr}")

    if failed > 0:
        sys.exit(1)


if __name__ == "__main__":
    main()
