"""Convert DOCX to HTML preview and text extract for visual comparison."""
import mammoth
from pathlib import Path

DOCX = Path("C:\\Users\\Adrian\\Downloads\\Kj\u00f8pekontrakt Prosjekt selveier .docx")
OUTPUT_DIR = Path(r"C:\Users\Adrian\Documents\Proaktiv-Dokument-Hub\scripts\converted_html")
HTML_OUT = OUTPUT_DIR / "SOURCE_selveier_DOCX.html"
TEXT_OUT = OUTPUT_DIR / "SOURCE_selveier_DOCX.txt"

with open(DOCX, "rb") as f:
    result = mammoth.convert_to_html(f)
    html = result.value
    messages = result.messages

with open(DOCX, "rb") as f:
    text_result = mammoth.extract_raw_text(f)
    raw_text = text_result.value

preview = f"""<!DOCTYPE html>
<html lang="no">
<head>
<meta charset="utf-8">
<title>SOURCE DOCX: Kj\u00f8pekontrakt Prosjekt selveier</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=Open+Sans:wght@300;400;700&display=swap');
html, body {{ margin: 0; padding: 0; font-size: 10pt; font-family: 'Open Sans', sans-serif; background: #e8e8e8; }}
.page-wrapper {{ max-width: 21cm; margin: 2cm auto; background: white; padding: 2.5cm; box-shadow: 0 2px 12px rgba(0,0,0,0.18); border: 1px solid #ccc; }}
.info-bar {{ background: #8B4513; color: #E9E7DC; padding: 14px 24px; font-family: 'Open Sans', sans-serif; font-size: 11px; display: flex; justify-content: space-between; align-items: center; position: sticky; top: 0; z-index: 100; box-shadow: 0 2px 8px rgba(0,0,0,0.3); }}
.info-bar h1 {{ font-size: 14px; margin: 0; font-weight: 400; }}
.info-bar .stats {{ display: flex; gap: 20px; }}
.info-bar .stat-value {{ color: #BCAB8A; font-weight: 700; }}
.legend {{ background: #faf0e6; border: 1px solid #c9a227; padding: 12px 20px; margin: 20px auto; max-width: 21cm; font-size: 11px; }}
table {{ border-collapse: collapse; width: 100%; }}
td, th {{ vertical-align: top; padding: 2px 4px; font-size: 10pt; }}
h1, h2, h3, h4, h5 {{ font-family: 'Open Sans', sans-serif; }}
p {{ margin: 0.5em 0; }}
</style>
</head>
<body>
<div class="info-bar">
  <h1>SOURCE DOCX: Kj\u00f8pekontrakt Prosjekt selveier &mdash; ORIGINAL WORD DOCUMENT</h1>
  <div class="stats">
    <div class="stat">HTML chars: <span class="stat-value">{len(html):,}</span></div>
    <div class="stat">Text chars: <span class="stat-value">{len(raw_text):,}</span></div>
    <div class="stat">Messages: <span class="stat-value">{len(messages)}</span></div>
  </div>
</div>
<div class="legend">
  <strong>Original Word Document (DOCX)</strong> &mdash; Converted via mammoth.js. This shows the raw content before any Vitec template conversion.
  Compare against the production template preview to identify content gaps.
</div>
<div class="page-wrapper">
{html}
</div>
</body>
</html>"""

HTML_OUT.write_text(preview, encoding="utf-8")
TEXT_OUT.write_text(raw_text, encoding="utf-8")

print(f"HTML preview: {HTML_OUT}")
print(f"Text extract: {TEXT_OUT}")
print(f"HTML size: {len(html):,} chars")
print(f"Text size: {len(raw_text):,} chars")
print(f"Conversion messages: {len(messages)}")
for msg in messages[:10]:
    print(f"  {msg}")
