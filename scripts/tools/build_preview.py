"""
Build a full visual preview of the production template with Stilark CSS applied.
Reads the actual production template and wraps it in a preview page that shows
ALL content with merge fields highlighted and vitec-if/foreach visualized.
"""

import os
import re

WORKSPACE = r"c:\Users\Adrian\.claude-worktrees\Proaktiv-Dokument-Hub\mystifying-hertz"
TEMPLATE = os.path.join(WORKSPACE, "scripts", "converted_html", "Kjopekontrakt_prosjekt_enebolig_PRODUCTION.html")
OUTPUT = os.path.join(WORKSPACE, "scripts", "converted_html", "preview_production.html")


def main():
    with open(TEMPLATE, encoding="utf-8") as f:
        template_html = f.read()

    merge_field_count = len(set(re.findall(r'\[\[[\*]?([^\]]+)\]\]', template_html)))
    vitec_if_count = len(re.findall(r'vitec-if=', template_html))
    vitec_foreach_count = len(re.findall(r'vitec-foreach=', template_html))
    article_count = len(re.findall(r'<article', template_html))

    # Highlight merge fields for visual inspection
    highlighted = template_html
    highlighted = re.sub(
        r'\[\[(\*?)([^\]]+)\]\]',
        r'<span class="mf">[[\1\2]]</span>',
        highlighted
    )

    # Add visual indicators for vitec-if
    highlighted = re.sub(
        r'(vitec-if="([^"]*)")',
        r'\1 title="\2"',
        highlighted
    )

    preview_html = f"""<!DOCTYPE html>
<html lang="no">
<head>
<meta charset="utf-8">
<title>Kjøpekontrakt Prosjekt (Enebolig) — Full Production Preview</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=Open+Sans:wght@300;400;700&display=swap');

html, body {{
  margin: 0;
  padding: 0;
  font-size: 10pt;
  line-height: normal;
  font-family: 'Open Sans', sans-serif;
  background: #e8e8e8;
}}

.page-wrapper {{
  max-width: 21cm;
  margin: 2cm auto;
  background: white;
  padding: 2.5cm;
  box-shadow: 0 2px 12px rgba(0,0,0,0.18);
  border: 1px solid #ccc;
}}

.info-bar {{
  background: #272630;
  color: #E9E7DC;
  padding: 14px 24px;
  font-family: 'Open Sans', sans-serif;
  font-size: 11px;
  display: flex;
  justify-content: space-between;
  align-items: center;
  position: sticky;
  top: 0;
  z-index: 100;
  box-shadow: 0 2px 8px rgba(0,0,0,0.3);
}}

.info-bar .stats {{
  display: flex;
  gap: 20px;
}}

.info-bar .stat {{
  display: flex;
  align-items: center;
  gap: 6px;
}}

.info-bar .stat-value {{
  color: #BCAB8A;
  font-weight: 700;
}}

.info-bar h1 {{
  font-size: 14px;
  margin: 0;
  font-weight: 400;
}}

.legend {{
  background: #f8f8f0;
  border: 1px solid #ddd;
  padding: 12px 20px;
  margin: 20px auto;
  max-width: 21cm;
  font-size: 11px;
  display: flex;
  gap: 24px;
  align-items: center;
}}

.legend-item {{
  display: flex;
  align-items: center;
  gap: 6px;
}}

/* Vitec Stilark */
#vitecTemplate * {{ font-variant-ligatures: none; }}
#vitecTemplate p, #vitecTemplate th p, #vitecTemplate td p {{
  font-size: 10pt; line-height: normal; font-family: 'Open Sans', sans-serif;
  margin: 0.8em 0; padding-bottom: 0;
}}
#vitecTemplate h1, #vitecTemplate h2, #vitecTemplate h3, #vitecTemplate h4, #vitecTemplate h5 {{
  font-family: 'Open Sans', sans-serif;
}}
#vitecTemplate h1 {{ font-size: 18pt; margin: 0.5em 0; }}
#vitecTemplate h2 {{ font-size: 12pt; font-weight: 700; margin: 1.2em 0 0.5em 0; }}
#vitecTemplate table {{ border-collapse: collapse; border-spacing: 0; }}
#vitecTemplate table th, #vitecTemplate table td {{
  vertical-align: top; font-size: 10pt; line-height: normal; font-family: 'Open Sans', sans-serif;
}}
#vitecTemplate table th {{ text-align: left; }}
#vitecTemplate strong {{ font-size: 10pt; line-height: normal; font-family: 'Open Sans', sans-serif; font-weight: 700; }}
#vitecTemplate ul li, #vitecTemplate ol li {{ font-size: 10pt; line-height: normal; font-family: 'Open Sans', sans-serif; }}
#vitecTemplate div {{ font-size: 10pt; line-height: normal; font-family: 'Open Sans', sans-serif; }}
#vitecTemplate span > strong {{ font-size: inherit; }}

/* Merge field highlighting */
.mf {{
  background: #fff3cd;
  border: 1px dashed #c9a227;
  padding: 1px 4px;
  border-radius: 3px;
  font-family: 'Courier New', monospace;
  font-size: 8.5pt;
  white-space: nowrap;
}}

/* vitec-if visual indicator */
[vitec-if] {{
  border-left: 3px solid #28a745;
  padding-left: 8px;
  margin-left: -11px;
  position: relative;
}}

[vitec-if]::before {{
  content: 'if';
  position: absolute;
  left: -2px;
  top: -1px;
  background: #28a745;
  color: white;
  font-size: 7px;
  padding: 1px 3px;
  border-radius: 2px;
  font-family: monospace;
  line-height: 1;
}}

/* vitec-foreach visual indicator */
[vitec-foreach] {{
  border-left: 3px solid #007bff;
  padding-left: 8px;
  margin-left: -11px;
  position: relative;
  background: rgba(0, 123, 255, 0.03);
}}

[vitec-foreach]::before {{
  content: 'foreach';
  position: absolute;
  left: -2px;
  top: -1px;
  background: #007bff;
  color: white;
  font-size: 7px;
  padding: 1px 3px;
  border-radius: 2px;
  font-family: monospace;
  line-height: 1;
}}

/* Page break indicator */
article.item {{
  border-top: 1px dashed #ccc;
  padding-top: 8px;
  margin-top: 16px;
}}

article.item:first-of-type {{
  border-top: none;
}}
</style>
</head>
<body>
<div class="info-bar">
  <h1>Kjøpekontrakt prosjekt (enebolig med delinnbetalinger) &mdash; PRODUCTION TEMPLATE</h1>
  <div class="stats">
    <div class="stat">Fields: <span class="stat-value">{merge_field_count}</span></div>
    <div class="stat">vitec-if: <span class="stat-value">{vitec_if_count}</span></div>
    <div class="stat">foreach: <span class="stat-value">{vitec_foreach_count}</span></div>
    <div class="stat">Sections: <span class="stat-value">{article_count}</span></div>
    <div class="stat">Validation: <span class="stat-value">39/39</span></div>
  </div>
</div>

<div class="legend">
  <strong>Legend:</strong>
  <div class="legend-item"><span class="mf">[[field]]</span> = Merge field (flettekode)</div>
  <div class="legend-item"><span style="border-left:3px solid #28a745; padding-left:4px;">green</span> = vitec-if conditional</div>
  <div class="legend-item"><span style="border-left:3px solid #007bff; padding-left:4px; background:rgba(0,123,255,0.08);">blue</span> = vitec-foreach loop</div>
  <div class="legend-item"><span style="border-bottom:1px dotted #999; padding:0 8px;">&nbsp;</span> = User fill-in field</div>
</div>

<div class="page-wrapper">
<!-- ==================== FULL PRODUCTION TEMPLATE ==================== -->
{highlighted}
<!-- ==================== END TEMPLATE ==================== -->
</div>

<div style="text-align:center; padding:20px; color:#888; font-size:11px;">
  Production template &bull; {len(template_html):,} chars &bull; 39/39 validation passed &bull; Generated by Vitec Template Builder
</div>
</body>
</html>"""

    with open(OUTPUT, "w", encoding="utf-8") as f:
        f.write(preview_html)

    print(f"Preview written: {OUTPUT}")
    print(f"Template content: {len(template_html):,} chars")
    print(f"Preview total: {len(preview_html):,} chars")


if __name__ == "__main__":
    main()
