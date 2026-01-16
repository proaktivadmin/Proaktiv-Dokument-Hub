import re
from pathlib import Path

html_file = Path(r"C:\Users\Adrian\Documents\.cursor\puncheveiledning\puncheguide_bruktbolig.html")

html = html_file.read_text(encoding="utf-8")

# Find and update the watermark-lily img tag to add filter and opacity
# Current: <img class="watermark-lily" src="data:image/png;base64,..." alt="Lilje">
# Target: <img class="watermark-lily" src="data:image/png;base64,..." alt="Lilje" style="filter: brightness(0.75) sepia(0.05); opacity: 0.12;">

pattern = r'(<img class="watermark-lily" src="data:image/png;base64,[^"]+") alt="Lilje">'
replacement = r'\1 alt="Lilje" style="filter: brightness(0.75) sepia(0.05); opacity: 0.12;">'

html_new = re.sub(pattern, replacement, html)

if html_new != html:
    html_file.write_text(html_new, encoding="utf-8")
    print("Updated watermark-lily img tag with filter and opacity")
else:
    print("No changes made - pattern not found")
    # Try alternative pattern
    if 'alt="Lilje">' in html:
        html_new = html.replace('alt="Lilje">', 'alt="Lilje" style="filter: brightness(0.75) sepia(0.05); opacity: 0.12;">')
        html_file.write_text(html_new, encoding="utf-8")
        print("Updated using simple replace")

