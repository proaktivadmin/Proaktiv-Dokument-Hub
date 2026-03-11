"""Build visual preview for the bruktbolig reference template (gold standard)."""

import os
import re

REF = r"C:\Users\Adrian\Downloads\kjøpekontrakt bruktbolig html.html"
OUTPUT = os.path.join(os.path.dirname(__file__), "converted_html", "REFERENCE_bruktbolig_PREVIEW.html")


def main():
    with open(REF, encoding="utf-8") as f:
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
<title>REFERENCE: Kjøpekontrakt Bruktbolig — Preview</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=Open+Sans:wght@300;400;700&display=swap');
html, body {{ margin: 0; padding: 0; font-size: 10pt; font-family: 'Open Sans', sans-serif; background: #e8e8e8; }}
.page-wrapper {{ max-width: 21cm; margin: 2cm auto; background: white; padding: 2.5cm; box-shadow: 0 2px 12px rgba(0,0,0,0.18); border: 1px solid #ccc; }}
.info-bar {{ background: #1a5c2a; color: #E9E7DC; padding: 14px 24px; font-family: 'Open Sans', sans-serif; font-size: 11px; display: flex; justify-content: space-between; align-items: center; position: sticky; top: 0; z-index: 100; box-shadow: 0 2px 8px rgba(0,0,0,0.3); }}
.info-bar .stats {{ display: flex; gap: 20px; }}
.info-bar .stat-value {{ color: #BCAB8A; font-weight: 700; }}
.info-bar h1 {{ font-size: 14px; margin: 0; font-weight: 400; }}
.legend {{ background: #f0f8f0; border: 1px solid #8b8; padding: 12px 20px; margin: 20px auto; max-width: 21cm; font-size: 11px; display: flex; gap: 24px; align-items: center; }}
#vitecTemplate * {{ font-variant-ligatures: none; }}
#vitecTemplate p, #vitecTemplate th p, #vitecTemplate td p {{ font-size: 10pt; line-height: 1.5; font-family: 'Open Sans', sans-serif; margin: 0.6em 0; }}
#vitecTemplate h1 {{ text-align: center; font-size: 14pt; margin: 0; padding: 0; }}
#vitecTemplate h2 {{ font-size: 11pt; margin: 30px 0 0 -20px; padding: 0; }}
#vitecTemplate h3 {{ font-size: 10pt; margin: 20px 0 0 0; padding: 0; }}
#vitecTemplate table {{ border-collapse: collapse; border-spacing: 0; width: 100%; table-layout: fixed; }}
#vitecTemplate table th, #vitecTemplate table td {{ vertical-align: top; font-size: 10pt; font-family: 'Open Sans', sans-serif; }}
#vitecTemplate table th {{ text-align: left; }}
#vitecTemplate ul li, #vitecTemplate ol li {{ font-size: 10pt; font-family: 'Open Sans', sans-serif; }}
#vitecTemplate article {{ padding-left: 20px; }}
#vitecTemplate article article {{ padding-left: 0; }}
#vitecTemplate .avoid-page-break {{ page-break-inside: avoid; }}
#vitecTemplate .borders {{ border-bottom: solid 1px black; border-top: solid 1px black; }}
#vitecTemplate .roles-table tbody:last-child tr:last-child td {{ display: none; }}
#vitecTemplate a.bookmark {{ color: #000; font-style: italic; text-decoration: none; }}
#vitecTemplate .liste:last-child .separator {{ display: none; }}
span.insert:empty {{ font-size: inherit !important; line-height: inherit !important; display: inline-block; background-color: lightpink; min-width: 2em !important; height: .7em !important; text-align: center; }}
span.insert:empty:before {{ content: attr(data-label); }}
.insert-table {{ display: inline-table; }}
.insert-table > span, .insert-table > span.insert {{ display: table-cell; }}
label.btn {{ display: inline; text-transform: none; white-space: normal; padding: 0; vertical-align: baseline; outline: none; font-size: inherit; }}
label.btn:active, label.btn.active {{ box-shadow: none; outline: none; }}
.svg-toggle {{ display: inline-block !important; width: 16px; height: 16px; margin: 0 5px; vertical-align: bottom; padding: 0; border: none; background: transparent; border-radius: 0; box-shadow: none !important; cursor: pointer; background-repeat: no-repeat; background-size: 16px 16px; background-position: center center; }}
.svg-toggle.checkbox {{ background-image: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 512 512'><rect style='fill:black;' height='496' width='496' x='9.1' y='9.1'></rect><rect style='fill:white;' height='400' width='400' x='57.1' y='60.6'></rect></svg>"); }}
.svg-toggle.checkbox.active, .btn.active > .svg-toggle.checkbox {{ background-image: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 512 512'><rect style='fill:black;' height='496' width='496' x='9.1' y='9.1'></rect><rect style='fill:white;' height='400' width='400' x='57.1' y='60.6'></rect><path style='fill:black;' d='M396.1,189.9L223.5,361.1c-4.7,4.7-12.3,4.6-17-0.1l-90.8-91.5c-4.7-4.7-4.6-12.3,0.1-17l22.7-22.5c4.7-4.7,12.3-4.6,17,0.1 l59.8,60.3l141.4-140.2c4.7-4.7,12.3-4.6,17,0.1l22.5,22.7C400.9,177.7,400.8,185.3,396.1,189.9L396.1,189.9z'></path></svg>"); box-shadow: none !important; }}
.svg-toggle.radio {{ background-image: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 512 512'><circle style='fill:black;' cx='257.1' cy='257.1' r='248'></circle><circle style='fill:white;' cx='257.1' cy='257.1' r='200'></circle></svg>"); }}
.svg-toggle.radio.active, .btn.active > .svg-toggle.radio {{ background-image: url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 512 512'><circle style='fill:black;' cx='257.1' cy='257.1' r='248'></circle><circle style='fill:white;' cx='257.1' cy='257.1' r='200'></circle><circle style='fill:black;' cx='257.1' cy='257.1' r='91.5'></circle></svg>"); box-shadow: none !important; }}
#vitecTemplate [data-toggle="buttons"] input {{ display: none; }}
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
  <h1>REFERENCE: Kj&oslash;pekontrakt Bruktbolig (Working Vitec Template) &mdash; GOLD STANDARD</h1>
  <div class="stats">
    <div class="stat">Fields: <span class="stat-value">{merge_field_count}</span></div>
    <div class="stat">vitec-if: <span class="stat-value">{vitec_if_count}</span></div>
    <div class="stat">foreach: <span class="stat-value">{vitec_foreach_count}</span></div>
    <div class="stat">Sections: <span class="stat-value">{article_count}</span></div>
  </div>
</div>
<div class="legend">
  <strong>REFERENCE TEMPLATE (Working in Production)</strong> &mdash;
  <span class="mf">[[field]]</span> = Merge field &nbsp;&nbsp;
  <span style="border-left:3px solid #28a745; padding-left:4px;">green</span> = vitec-if &nbsp;&nbsp;
  <span style="border-left:3px solid #007bff; padding-left:4px; background:rgba(0,123,255,0.08);">blue</span> = foreach
</div>
<div class="page-wrapper">
{highlighted}
</div>
<div style="text-align:center; padding:20px; color:#888; font-size:11px;">
  Reference template &bull; {len(template_html):,} chars &bull; GOLD STANDARD
</div>
</body>
</html>"""

    with open(OUTPUT, "w", encoding="utf-8") as f:
        f.write(preview_html)

    print(f"Reference preview written: {OUTPUT}")
    print(f"Template: {len(template_html):,} chars | Fields: {merge_field_count} | vitec-if: {vitec_if_count} | foreach: {vitec_foreach_count}")


if __name__ == "__main__":
    main()
