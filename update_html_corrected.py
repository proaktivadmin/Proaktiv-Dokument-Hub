import json
import re
from pathlib import Path

# Paths
base_dir = Path(r"C:\Users\Adrian\Documents\.cursor\puncheveiledning")
html_source = base_dir / "Utkast" / "puncheguide_bruktbolig - Copy.html"
html_output = base_dir / "puncheguide_bruktbolig.html"
json_file = base_dir / "image_base64_map_corrected.json"

# Load CORRECTED Base64 mappings
with open(json_file, 'r', encoding='utf-8') as f:
    image_map = json.load(f)

# Read source HTML (original, unmodified)
with open(html_source, 'r', encoding='utf-8') as f:
    html_content = f.read()

print("Updating HTML file with CORRECTED image mapping...")

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
for img_ref, base64_data in image_map.items():
    if img_ref.endswith('.png') and img_ref != "lilje_hel_warmgrey.png":
        pattern = f'src="images/{img_ref}"'
        replacement = f'src="data:image/png;base64,{base64_data}"'
        count_before = html_content.count(pattern)
        html_content = html_content.replace(pattern, replacement)
        if count_before > 0:
            print(f"  Replaced {count_before}x: {img_ref}")

# Remove bracket divs
html_content = re.sub(r'<div class="bracket[^"]*"></div>\s*', '', html_content)

# Remove bracket CSS
html_content = re.sub(r'\.bracket\s*\{[^}]*\}', '', html_content)
html_content = re.sub(r'\.bracket-tl\s*\{[^}]*\}', '', html_content)
html_content = re.sub(r'\.bracket-br\s*\{[^}]*\}', '', html_content)

# Fix watermark CSS - remove filter, add opacity
html_content = html_content.replace(
    'style="filter: brightness(0.75) sepia(0.05); opacity: 0.12;"',
    'style="opacity: 0.10;"'
)

# Update .watermark-lily CSS to add opacity
html_content = re.sub(
    r'(\.watermark-lily\s*\{[^}]*)(z-index:\s*1;)(\s*\})',
    r'\1\2\n            opacity: 0.10;\3',
    html_content
)

# INCREASE IMAGE SIZE - Update .img-container.open max-height
html_content = re.sub(
    r'(\.img-container\.open\s*\{\s*max-height:\s*)600px',
    r'\g<1>1200px',
    html_content
)

# Add print styles improvements
print_css_additions = """
        @page {
            size: A4;
            margin: 0;
        }
        
        .step, .info-box, .img-container, .appendix-item, .critical-box {
            break-inside: avoid;
            page-break-inside: avoid;
        }
"""

# Insert print CSS additions before @media print (only once)
if '@page' not in html_content and '@media print' in html_content:
    html_content = html_content.replace('@media print', print_css_additions + '\n        @media print')

# Write updated HTML
with open(html_output, 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"\nUpdated {html_output}")
print("Changes made:")
print("  - Replaced all image references with CORRECTED Base64 mapping")
print("  - Updated logo references")
print("  - Removed bracket divs")
print("  - Fixed watermark CSS (opacity only)")
print("  - Increased image container max-height to 1200px")
print("  - Added print break-inside rules")

