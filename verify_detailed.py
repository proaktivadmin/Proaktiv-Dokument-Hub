import json
import re
from pathlib import Path

base_dir = Path(r"C:\Users\Adrian\Documents\.cursor\puncheveiledning")
html_file = base_dir / "puncheguide_bruktbolig.html"
json_file = base_dir / "image_base64_map_corrected.json"

# Load the mapping
with open(json_file, 'r', encoding='utf-8') as f:
    image_map = json.load(f)

# Read HTML
with open(html_file, 'r', encoding='utf-8') as f:
    html_content = f.read()

print("=== Detailed Image Verification ===\n")

# Check each mapped image is present in HTML
for ref_name, base64_data in image_map.items():
    if ref_name.endswith('.png') and ref_name != "lilje_hel_warmgrey.png":
        # Check if this base64 is in the HTML
        base64_start = base64_data[:100]
        is_present = base64_start in html_content
        count = html_content.count(base64_start)
        status = "OK" if is_present else "MISSING"
        print(f"[{status}] {ref_name}: found {count}x")

print("\n=== Summary ===")
print(f"Total mapped images (excl logos): {len([k for k in image_map.keys() if k.endswith('.png') and k != 'lilje_hel_warmgrey.png'])}")
print(f"Total Base64 images in HTML: {html_content.count('data:image/png;base64')}")

# Verify file size is reasonable (should be ~10MB with all images)
file_size_mb = len(html_content) / (1024 * 1024)
print(f"\nFile size: {file_size_mb:.2f} MB")

if file_size_mb > 5:
    print("File size looks good - images are embedded")
else:
    print("WARNING: File might be missing images")

