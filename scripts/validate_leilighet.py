"""Quick validation for Kjopekontrakt_prosjekt_leilighet_PRODUCTION.html"""
import re, os, sys

TEMPLATE = os.path.join(os.path.dirname(__file__), "converted_html", "Kjopekontrakt_prosjekt_leilighet_PRODUCTION.html")

with open(TEMPLATE, encoding="utf-8") as f:
    html = f.read()

results = []
def check(section, name, passed, detail=""):
    results.append((f"[{section}] {name}", passed, detail))

check("A", "vitecTemplate wrapper div", 'id="vitecTemplate"' in html and 'class="proaktiv-theme"' in html)
check("A", "Stilark resource span", 'vitec-template="resource:Vitec Stilark"' in html)
stilark_match = re.search(r'vitec-template="resource:Vitec Stilark">\s*&nbsp;\s*</span>', html)
check("A", "Stilark span contains &nbsp;", stilark_match is not None)
check("B", "No CSS flexbox/grid", "display:flex" not in html and "display:grid" not in html)
orphan_tr = re.findall(r"<table[^>]*>\s*<tr", html)
check("B", "No orphan tr outside tbody/thead", len(orphan_tr) == 0, f"Found {len(orphan_tr)}")
check("B", "Uses 100-unit colspan system", 'colspan="100"' in html or 'colspan="50"' in html)
font_family_inline = re.findall(r'style="[^"]*font-family[^"]*"', html)
check("C", "No inline font-family", len(font_family_inline) == 0, f"Found {len(font_family_inline)}")
font_size_inline = re.findall(r'style="[^"]*font-size[^"]*"', html)
check("C", "No inline font-size", len(font_size_inline) == 0, f"Found {len(font_size_inline)}")
merge_fields = re.findall(r"\[\[[\*]?([^\]]+)\]\]", html)
check("D", "Merge fields use [[field]] syntax", len(merge_fields) > 0, f"Found {len(merge_fields)}")
bad_spaces = re.findall(r"\[\[\s+|\s+\]\]", html)
check("D", "No spaces inside brackets", len(bad_spaces) == 0, f"Found {len(bad_spaces)}")
legacy_fields = re.findall(r"#\w+\.\w+\xa4", html)
check("D", "No legacy #field.context syntax", len(legacy_fields) == 0, f"Found: {legacy_fields}")
vitec_ifs = re.findall(r'vitec-if="([^"]*)"', html)
check("E", "Has vitec-if conditions", len(vitec_ifs) > 0, f"Found {len(vitec_ifs)}")
bad_quotes = [v for v in vitec_ifs if '"' in v.replace("&quot;", "").replace("&amp;", "")]
check("E", "String comparisons use &quot;", len(bad_quotes) == 0, f"Bad: {bad_quotes[:3]}")
bad_gt = [v for v in vitec_ifs if re.search(r"(?<!&amp;)(?<!&quot;)(?<!&lt;)(?<!&gt;)(?<!&)>", v)]
check("E", "Greater-than uses &gt;", len(bad_gt) == 0, f"Bad: {bad_gt[:3]}")
foreachs = re.findall(r'vitec-foreach="([^"]*)"', html)
check("F", "Has vitec-foreach loops", len(foreachs) > 0, f"Found {len(foreachs)}")
foreach_on_tbody = re.findall(r"<tbody\s+vitec-foreach=", html)
check("F", "Foreach on tbody elements", len(foreach_on_tbody) > 0, f"Found {len(foreach_on_tbody)}")
for fe in foreachs:
    parts = fe.split(" in ")
    if len(parts) == 2:
        col = parts[1]
        check("F", f"Guard for {col}", f"{col}.Count" in html)
img_tags = re.findall(r"<img\s[^>]*>", html)
check("G", "No image tags", len(img_tags) == 0, f"Found {len(img_tags)}")
check("H", "Has span.insert placeholders", 'class="insert"' in html)
font_tags = re.findall(r"<font\b", html)
check("I", "No font tags", len(font_tags) == 0)
center_tags = re.findall(r"<center\b", html)
check("I", "No center tags", len(center_tags) == 0)
check("I", "Contains o-slash (ø)", "\u00f8" in html)
check("I", "Contains ae-ligature (æ)", "\u00e6" in html)
check("I", "Contains a-ring (å)", "\u00e5" in html)
check("J", "Uses article.item", '<article class="item">' in html)
check("J", "CSS counters present", "counter-reset: section" in html and "counter-increment: section" in html)
check("J", "Dual counter subsection", "subsection" in html)
check("J", "H2 in top-level articles", "<h2>" in html)
check("J", "roles-table class", 'class="roles-table"' in html)
check("J", "costs-table class", 'class="costs-table"' in html)
check("J", "Signature border-bottom", "border-bottom" in html and "solid 1px #000" in html)
check("J", "span.insert placeholders", 'class="insert"' in html)
check("J", "avoid-page-break class", "avoid-page-break" in html)
check("K", "Well-formed articles", html.count("<article") == html.count("</article>"),
      f"{html.count('<article')} open vs {html.count('</article>')} close")
check("K", "No onclick/onload", "onclick" not in html and "onload" not in html)
check("K", "No external stylesheets", '<link rel="stylesheet"' not in html)
check("K", "No JavaScript", "<script" not in html)

passed = sum(1 for _, p, _ in results if p)
total = len(results)
print(f"{'='*60}")
print(f"VITEC TEMPLATE VALIDATION: Kjopekontrakt_prosjekt_leilighet")
print(f"{'='*60}")
print(f"Size: {len(html):,} chars\n")
for name, p, detail in results:
    icon = "+" if p else "!"
    status = "PASS" if p else "FAIL"
    line = f"  [{icon}] {status}: {name}"
    if detail and not p:
        line += f" -- {detail}"
    print(line)
print(f"\nRESULTS: {passed}/{total} PASS")

merge_fields_set = sorted(set(re.findall(r"\[\[[\*]?([^\]]+)\]\]", html)))
print(f"\nMerge fields ({len(merge_fields_set)}):")
for mf in merge_fields_set:
    print(f"  [[{mf}]]")

print(f"\nvitec-if conditions ({len(vitec_ifs)}):")
for expr in sorted(set(vitec_ifs)):
    print(f"  {expr}")

print(f"\nvitec-foreach loops ({len(foreachs)}):")
for expr in foreachs:
    print(f"  {expr}")

if passed < total:
    sys.exit(1)
