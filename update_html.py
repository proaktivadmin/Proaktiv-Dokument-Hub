import json
import re
from pathlib import Path

# Paths
base_dir = Path(r"C:\Users\Adrian\Documents\.cursor\puncheveiledning")
html_file = base_dir / "puncheguide_bruktbolig.html"
json_file = base_dir / "image_base64_map.json"

# Load Base64 mappings
with open(json_file, 'r', encoding='utf-8') as f:
    image_map = json.load(f)

# Read HTML
with open(html_file, 'r', encoding='utf-8') as f:
    html_content = f.read()

print("Updating HTML file...")

# Replace logo references
html_content = html_content.replace(
    'src="https://proaktiv.no/assets/logos/lilje_hel_warmgrey.png"',
    f'src="data:image/png;base64,{image_map["lilje_hel_warmgrey.png"]}"'
)
html_content = html_content.replace(
    'src="https://proaktiv.no/assets/logos/logo.svg"',
    f'src="data:image/svg+xml;base64,{image_map["logo.svg"]}"'
)

# Replace all image references
for img_ref, base64_data in image_map.items():
    if img_ref.endswith('.png') and img_ref != "lilje_hel_warmgrey.png":
        # Replace both regular img tags and appendix-img tags
        pattern1 = f'src="images/{img_ref}"'
        replacement1 = f'src="data:image/png;base64,{base64_data}"'
        html_content = html_content.replace(pattern1, replacement1)
        
        # Also handle any variations
        pattern2 = f"src='images/{img_ref}'"
        replacement2 = f"src='data:image/png;base64,{base64_data}'"
        html_content = html_content.replace(pattern2, replacement2)

# Remove bracket divs
html_content = re.sub(r'<div class="bracket[^"]*"></div>\s*', '', html_content)

# Remove bracket CSS
html_content = re.sub(r'\.bracket[^{]*\{[^}]*\}', '', html_content)
html_content = re.sub(r'\.bracket-tl[^{]*\{[^}]*\}', '', html_content)
html_content = re.sub(r'\.bracket-br[^{]*\{[^}]*\}', '', html_content)

# Fix watermark CSS - remove filter, keep only opacity
html_content = html_content.replace(
    'style="filter: brightness(0.75) sepia(0.05); opacity: 0.12;"',
    'style="opacity: 0.10;"'
)

# Also update CSS for watermark-lily class
html_content = re.sub(
    r'\.watermark-lily\s*\{[^}]*filter:[^;]*;[^}]*\}',
    '.watermark-lily {\n            position: absolute;\n            top: 45%;\n            right: -80px;\n            transform: translateY(-50%);\n            width: 400px;\n            pointer-events: none;\n            z-index: 1;\n            opacity: 0.10;\n        }',
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

# Insert print CSS additions before @media print
if '@media print' in html_content:
    html_content = html_content.replace('@media print', print_css_additions + '\n        @media print')

# Write updated HTML
output_file = base_dir / "puncheguide_bruktbolig.html"
with open(output_file, 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"Updated {output_file}")
print("Changes made:")
print("  - Replaced all image references with Base64")
print("  - Updated logo references")
print("  - Removed bracket divs")
print("  - Fixed watermark CSS")
print("  - Added print break-inside rules")
