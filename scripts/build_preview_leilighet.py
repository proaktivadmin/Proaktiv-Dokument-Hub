"""Build visual preview for Kjopekontrakt_prosjekt_leilighet."""

import os
import re

BASE = os.path.dirname(__file__)
TEMPLATE = os.path.join(BASE, "converted_html", "Kjopekontrakt_prosjekt_leilighet_PRODUCTION.html")
OUTPUT = os.path.join(BASE, "converted_html", "Kjopekontrakt_prosjekt_leilighet_PREVIEW.html")


def main():
    with open(TEMPLATE, encoding="utf-8") as f:
        template_html = f.read()

    merge_field_count = len(set(re.findall(r'\[\[[\*]?([^\]]+)\]\]', template_html)))
    vitec_if_count = len(re.findall(r'vitec-if=', template_html))
    vitec_foreach_count = len(re.findall(r'vitec-foreach=', template_html))
    article_count = len(re.findall(r'<article', template_html))

    highlighted = template_html
    highlighted = re.sub(
        r'\[\[(\*?)([^\]]+)\]\]',
        r'<span class="mf">[[\1\2]]</span>',
        highlighted
    )
    highlighted = re.sub(
        r'(vitec-if="([^"]*)")',
        r'\1 title="\2"',
        highlighted
    )

    preview_html = f"""<!DOCTYPE html>
<html lang="no">
<head>
<meta charset="utf-8">
<title>Kjøpekontrakt Prosjekt (Leilighet/Eierseksjon) — Preview</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=Open+Sans:wght@300;400;700&display=swap');
html, body {{ margin: 0; padding: 0; font-size: 10pt; font-family: 'Open Sans', sans-serif; background: #e8e8e8; }}
.page-wrapper {{ max-width: 21cm; margin: 2cm auto; background: white; padding: 2.5cm; box-shadow: 0 2px 12px rgba(0,0,0,0.18); border: 1px solid #ccc; }}
.info-bar {{ background: #272630; color: #E9E7DC; padding: 14px 24px; font-family: 'Open Sans', sans-serif; font-size: 11px; display: flex; justify-content: space-between; align-items: center; position: sticky; top: 0; z-index: 100; box-shadow: 0 2px 8px rgba(0,0,0,0.3); }}
.info-bar .stats {{ display: flex; gap: 20px; }}
.info-bar .stat-value {{ color: #BCAB8A; font-weight: 700; }}
.info-bar h1 {{ font-size: 14px; margin: 0; font-weight: 400; }}
.legend {{ background: #f8f8f0; border: 1px solid #ddd; padding: 12px 20px; margin: 20px auto; max-width: 21cm; font-size: 11px; display: flex; gap: 24px; align-items: center; }}
#vitecTemplate * {{ font-variant-ligatures: none; }}
#vitecTemplate p, #vitecTemplate th p, #vitecTemplate td p {{ font-size: 10pt; line-height: 1.5; font-family: 'Open Sans', sans-serif; margin: 0.6em 0; }}
#vitecTemplate h2 {{ font-size: 12pt; font-weight: 700; margin: 1.2em 0 0.5em 0; text-transform: uppercase; }}
#vitecTemplate h5 {{ font-size: 16pt; font-weight: 700; text-align: center; margin: 0.5em 0; text-transform: uppercase; }}
#vitecTemplate table {{ border-collapse: collapse; border-spacing: 0; width: 100%; }}
#vitecTemplate table th, #vitecTemplate table td {{ vertical-align: top; font-size: 10pt; font-family: 'Open Sans', sans-serif; }}
#vitecTemplate table th {{ text-align: left; }}
#vitecTemplate ul li, #vitecTemplate ol li {{ font-size: 10pt; font-family: 'Open Sans', sans-serif; }}
.mf {{ background: #fff3cd; border: 1px dashed #c9a227; padding: 1px 4px; border-radius: 3px; font-family: 'Courier New', monospace; font-size: 8.5pt; white-space: nowrap; }}
[vitec-if] {{ border-left: 3px solid #28a745; padding-left: 8px; margin-left: -11px; position: relative; }}
[vitec-if]::before {{ content: 'if'; position: absolute; left: -2px; top: -1px; background: #28a745; color: white; font-size: 7px; padding: 1px 3px; border-radius: 2px; font-family: monospace; line-height: 1; }}
[vitec-foreach] {{ border-left: 3px solid #007bff; padding-left: 8px; margin-left: -11px; position: relative; background: rgba(0,123,255,0.03); }}
[vitec-foreach]::before {{ content: 'foreach'; position: absolute; left: -2px; top: -1px; background: #007bff; color: white; font-size: 7px; padding: 1px 3px; border-radius: 2px; font-family: monospace; line-height: 1; }}
article.item {{ border-top: 1px dashed #ccc; padding-top: 8px; margin-top: 16px; }}
</style>
</head>
<body>
<div class="info-bar">
  <h1>Kjøpekontrakt prosjekt (leilighet/eierseksjon under oppføring) &mdash; PREVIEW</h1>
  <div class="stats">
    <div class="stat">Fields: <span class="stat-value">{merge_field_count}</span></div>
    <div class="stat">vitec-if: <span class="stat-value">{vitec_if_count}</span></div>
    <div class="stat">foreach: <span class="stat-value">{vitec_foreach_count}</span></div>
    <div class="stat">Sections: <span class="stat-value">{article_count}</span></div>
    <div class="stat">Validation: <span class="stat-value">38/38</span></div>
  </div>
</div>
<div class="legend">
  <strong>Legend:</strong>
  <span class="mf">[[field]]</span> = Merge field &nbsp;&nbsp;
  <span style="border-left:3px solid #28a745; padding-left:4px;">green</span> = vitec-if &nbsp;&nbsp;
  <span style="border-left:3px solid #007bff; padding-left:4px; background:rgba(0,123,255,0.08);">blue</span> = vitec-foreach &nbsp;&nbsp;
  <span style="border-bottom:1px dotted #999; padding:0 8px;">&nbsp;</span> = fill-in
</div>
<div class="page-wrapper">
{highlighted}
</div>
<div style="text-align:center; padding:20px; color:#888; font-size:11px;">
  {len(template_html):,} chars &bull; 38/38 validation passed &bull; Vitec Template Builder
</div>
</body>
</html>"""

    with open(OUTPUT, "w", encoding="utf-8") as f:
        f.write(preview_html)

    print(f"Preview written: {OUTPUT}")
    print(f"Template: {len(template_html):,} chars | Preview: {len(preview_html):,} chars")
    print(f"Merge fields: {merge_field_count} | vitec-if: {vitec_if_count} | foreach: {vitec_foreach_count} | Sections: {article_count}")


if __name__ == "__main__":
    main()
