import re
from pathlib import Path

# Paths
base_dir = Path(r"C:\Users\Adrian\Documents\.cursor\puncheveiledning")
html_file = base_dir / "puncheguide_bruktbolig.html"

print("Removing SVG indicators from images...")

# Read HTML
with open(html_file, 'r', encoding='utf-8') as f:
    html_content = f.read()

# Count before
wrapper_count_before = html_content.count('class="img-wrapper"')
print(f"Found {wrapper_count_before} img-wrappers to remove")

# Remove the indicator CSS block
indicator_css_pattern = r'/\* SVG Indicator Overlays \*/.*?\.indicator-circle \{[^}]*\}\s*'
html_content = re.sub(indicator_css_pattern, '', html_content, flags=re.DOTALL)

# Remove img-wrapper divs and SVG overlays, keeping only the img tag
# Pattern: <div class="img-wrapper">...<img ...>...<svg ...>...</svg>...</div>
wrapper_pattern = r'<div class="img-wrapper">\s*(<img[^>]+>)\s*<svg class="indicator-svg"[^>]*>.*?</svg>\s*</div>'
html_content = re.sub(wrapper_pattern, r'\1', html_content, flags=re.DOTALL)

# Count after
wrapper_count_after = html_content.count('class="img-wrapper"')
print(f"Remaining img-wrappers: {wrapper_count_after}")

# Verify SVG indicators are removed
svg_count = html_content.count('class="indicator-svg"')
print(f"Remaining indicator-svg: {svg_count}")

# Write updated HTML
with open(html_file, 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"\nUpdated {html_file}")
print("SVG indicators removed successfully!")

