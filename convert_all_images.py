import base64
import os
import json
from pathlib import Path

# Paths
base_dir = Path(r"C:\Users\Adrian\Documents\.cursor\puncheveiledning")
images_dir = base_dir / "images"
utkast_dir = base_dir / "Utkast"

# Get all PNG files sorted by name (timestamp order)
image_files = sorted([f for f in os.listdir(images_dir) if f.endswith('.png')])

print(f"Found {len(image_files)} images in images/")

# Image reference mapping based on order in HTML
# These are the image references found in puncheguide_bruktbolig.html
image_refs = [
    "opprett-ny-kontakt.png",
    "nytt-eierskap.png", 
    "opprett-befaring.png",
    "opprett-befaring-skjema.png",
    "oppdragsparter.png",
    "selger-meny.png",
    "ny-identifikasjon.png",
    "alfanavn-field.png",
    "bilder-opplasting.png",
    "dokument-kategorisering.png",
    "budsjett-oppstilling.png",
    "pant-og-laan.png",
    "sjekkliste.png",
    "marked-og-tjenester.png",
    "depot-og-tinglysing.png",
    "visninger.png",
    "bud-detaljer.png",
    "hjemmelshaver-selger.png",
    "identifikasjon-panel.png",
    "dokumenter-opplasting.png",
    "bud-og-omsetning.png",
    "oppdrag-dashboard.png"
]

# Convert images to Base64
image_base64_map = {}
for idx, img_file in enumerate(image_files):
    img_path = images_dir / img_file
    with open(img_path, 'rb') as f:
        img_data = f.read()
        base64_data = base64.b64encode(img_data).decode('utf-8')
        
        # Map to reference name if we have one
        if idx < len(image_refs):
            ref_name = image_refs[idx]
            image_base64_map[ref_name] = base64_data
            print(f"{idx+1}. {img_file} -> {ref_name} ({len(base64_data)} chars)")
        else:
            # Store with original name for potential future use
            image_base64_map[img_file] = base64_data
            print(f"{idx+1}. {img_file} (unmapped) ({len(base64_data)} chars)")

# Convert logo files
print("\nConverting logos...")
lily_path = utkast_dir / "Lilje_Hel_WarmGrey.1.0.png"
logo_path = utkast_dir / "logo.svg"

with open(lily_path, 'rb') as f:
    lily_base64 = base64.b64encode(f.read()).decode('utf-8')
    image_base64_map["lilje_hel_warmgrey.png"] = lily_base64
    print(f"Lily logo: {len(lily_base64)} chars")

with open(logo_path, 'rb') as f:
    logo_base64 = base64.b64encode(f.read()).decode('utf-8')
    image_base64_map["logo.svg"] = logo_base64
    print(f"Logo SVG: {len(logo_base64)} chars")

# Save to JSON file for easy access
output_file = base_dir / "image_base64_map.json"
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(image_base64_map, f, indent=2)

print(f"\nSaved mapping to {output_file}")
print(f"Total entries: {len(image_base64_map)}")
