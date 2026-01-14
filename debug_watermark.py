from pathlib import Path
import re

html = Path(r"C:\Users\Adrian\Documents\.cursor\puncheveiledning\puncheguide_bruktbolig.html").read_text(encoding="utf-8")

print("=== Debugging Watermark ===")

# Check CSS
if ".watermark-lily" in html:
    # Find the CSS block
    css_match = re.search(r'\.watermark-lily\s*\{([^}]+)\}', html)
    if css_match:
        print("CSS found:")
        print(css_match.group(0)[:200])
else:
    print("NO .watermark-lily CSS found!")

print()

# Check img tag
img_match = re.search(r'<img[^>]*class="watermark-lily"[^>]*>', html)
if img_match:
    tag = img_match.group(0)
    print("IMG tag found!")
    print(f"Has base64: {'data:image/png;base64' in tag}")
    print(f"Tag preview: {tag[:150]}...")
else:
    print("NO watermark-lily img tag found!")

print()

# Check position in document
cover_idx = html.find('<div class="page cover-page">')
lily_img_idx = html.find('class="watermark-lily"')
print(f"cover-page div at char: {cover_idx}")
print(f"watermark-lily at char: {lily_img_idx}")

if lily_img_idx > cover_idx and lily_img_idx < cover_idx + 5000:
    print("Watermark is correctly placed inside cover-page")
else:
    print("WARNING: Watermark may not be in correct position!")

