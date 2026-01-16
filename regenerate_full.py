import json
import re
from pathlib import Path

# Paths
base_dir = Path(r"C:\Users\Adrian\Documents\.cursor\puncheveiledning")
html_source = base_dir / "Utkast" / "puncheguide_bruktbolig - Copy.html"
html_output = base_dir / "puncheguide_bruktbolig.html"
json_file = base_dir / "image_base64_map_corrected.json"

print("Regenerating HTML with all images and correct lily watermark...")

# Load Base64 mappings
with open(json_file, 'r', encoding='utf-8') as f:
    image_map = json.load(f)

# Read source HTML
with open(html_source, 'r', encoding='utf-8') as f:
    html_content = f.read()

# Replace logo references
html_content = html_content.replace(
    'src="https://proaktiv.no/assets/logos/lilje_hel_warmgrey.png"',
    f'src="data:image/png;base64,{image_map["lilje_hel_warmgrey.png"]}"'
)
html_content = html_content.replace(
    'src="https://proaktiv.no/assets/logos/logo.svg"',
    f'src="data:image/svg+xml;base64,{image_map["logo.svg"]}"'
)

# Replace all image references with Base64
replaced_count = 0
for img_ref, base64_data in image_map.items():
    if img_ref.endswith('.png') and img_ref != "lilje_hel_warmgrey.png":
        pattern = f'src="images/{img_ref}"'
        replacement = f'src="data:image/png;base64,{base64_data}"'
        count_before = html_content.count(pattern)
        html_content = html_content.replace(pattern, replacement)
        if count_before > 0:
            replaced_count += count_before
            print(f"  Replaced {count_before}x: {img_ref}")

# Remove bracket divs
html_content = re.sub(r'<div class="bracket[^"]*"></div>\s*', '', html_content)

# Remove bracket CSS
html_content = re.sub(r'\.bracket\s*\{[^}]*\}', '', html_content)
html_content = re.sub(r'\.bracket-tl\s*\{[^}]*\}', '', html_content)
html_content = re.sub(r'\.bracket-br\s*\{[^}]*\}', '', html_content)

# Keep the original watermark styling from the source (filter + opacity)
# The source already has: style="filter: brightness(0.75) sepia(0.05); opacity: 0.12;"

# Update .img-container.open max-height for larger images
html_content = re.sub(
    r'(\.img-container\.open\s*\{\s*max-height:\s*)600px',
    r'\g<1>1200px',
    html_content
)

# Add print styles if not present
print_css = """
        @page {
            size: A4;
            margin: 0;
        }
        
        .step, .info-box, .img-container, .appendix-item, .critical-box {
            break-inside: avoid;
            page-break-inside: avoid;
        }
"""

if '@page' not in html_content and '@media print' in html_content:
    html_content = html_content.replace('@media print', print_css + '\n        @media print')

# Write updated HTML
with open(html_output, 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"\nRegenerated {html_output}")
print(f"Total image replacements: {replaced_count}")
print(f"File size: {len(html_content)} bytes")

