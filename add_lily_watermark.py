import json
from pathlib import Path

# Paths
base_dir = Path(r"C:\Users\Adrian\Documents\.cursor\puncheveiledning")
html_file = base_dir / "puncheguide_bruktbolig.html"
json_file = base_dir / "image_base64_map_corrected.json"

print("Adding lily watermark to cover page...")

# Load Base64 data
with open(json_file, 'r', encoding='utf-8') as f:
    image_map = json.load(f)

lily_base64 = image_map.get("lilje_hel_warmgrey.png", "")

if not lily_base64:
    print("ERROR: Lily image not found in JSON!")
    exit(1)

# Read HTML
with open(html_file, 'r', encoding='utf-8') as f:
    html_content = f.read()

# Create the watermark img tag
watermark_img = f'''
        <img class="watermark-lily" src="data:image/png;base64,{lily_base64}" alt="Lilje" style="opacity: 0.10;">
'''

# Find the cover-page div and insert the watermark after it opens
# Pattern: <div class="page cover-page">
target = '<div class="page cover-page">'
if target in html_content:
    # Insert watermark after the opening tag
    html_content = html_content.replace(
        target,
        target + watermark_img
    )
    print("Watermark added successfully!")
else:
    print("ERROR: Could not find cover-page div!")
    exit(1)

# Write updated HTML
with open(html_file, 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"Updated {html_file}")

