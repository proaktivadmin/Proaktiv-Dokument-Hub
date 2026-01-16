import base64
import os
import json
from pathlib import Path

# Paths
base_dir = Path(r"C:\Users\Adrian\Documents\.cursor\puncheveiledning")
images_dir = base_dir / "images"
utkast_dir = base_dir / "Utkast"

print("Converting images with CORRECTED mapping based on visual analysis...")

# CORRECTED mapping based on visual analysis of each image
# Format: (source_filename, target_reference_name)
image_mapping = [
    # Main guide images (in order of appearance in HTML)
    ("Skjermbilde 2025-12-16 002830.png", "opprett-ny-kontakt.png"),      # Søkefelt med "Ingen treff" og + knapp
    ("Skjermbilde 2025-12-16 003030.png", "nytt-eierskap.png"),           # Eierskap med "+ Nytt eierskap" knapp
    ("Skjermbilde 2025-12-16 003123.png", "opprett-befaring.png"),        # Eierskap-detaljer med "Opprett befaring" i Utfør-meny
    ("Skjermbilde 2025-12-16 003224.png", "opprett-befaring-skjema.png"), # Opprett befaring skjema med OPPDRAGSTYPE
    ("Skjermbilde 2025-12-16 004423.png", "oppdragsparter.png"),          # Oppdragsparter med Utfør-meny
    ("Skjermbilde 2025-12-16 004647.png", "selger-meny.png"),             # Selger-panel med verktøymeny
    ("Skjermbilde 2025-12-16 004633.png", "ny-identifikasjon.png"),       # "Ny identifikasjon" opplastingsskjema
    ("Skjermbilde 2025-12-16 004033.png", "alfanavn-field.png"),          # Objektbeskrivelse med ALFANAVN tydelig synlig
    ("Skjermbilde 2025-12-16 004105.png", "bilder-opplasting.png"),       # Bilder-fanen med "DRA OG SLIPP"
    ("Skjermbilde 2025-12-16 004500.png", "dokument-kategorisering.png"), # Dokumenter med "Signert manuelt" toggle
    ("Skjermbilde 2025-12-16 003720.png", "budsjett-oppstilling.png"),    # Budsjettoppstilling med "Forslag" knapp
    ("Skjermbilde 2025-12-16 005423.png", "pant-og-laan.png"),            # Pant og lån med heftelser
    ("Skjermbilde 2025-12-16 004903.png", "sjekkliste.png"),              # MEGLERS SJEKKLISTE nærbilde
    ("Skjermbilde 2025-12-16 004257.png", "marked-og-tjenester.png"),     # Marked og tjenester
    ("Skjermbilde 2025-12-16 005400.png", "depot-og-tinglysing.png"),     # Depot og e-Tinglysing med Depotføring panel
    ("Skjermbilde 2025-12-16 004343.png", "visninger.png"),               # Visninger med kommende visning
    ("Skjermbilde 2025-12-16 005259.png", "bud-detaljer.png"),            # Bud og omsetning med registrert bud
    
    # Appendix images
    ("Skjermbilde 2025-12-16 003306.png", "hjemmelshaver-selger.png"),    # Hjemmelshaver skjema
    ("Skjermbilde 2025-12-16 004656.png", "identifikasjon-panel.png"),    # Identifikasjon panel med "Legg til ny ID"
    ("Skjermbilde 2025-12-16 004133.png", "dokumenter-opplasting.png"),   # Dokumenter med "Nytt dokument"
    ("Skjermbilde 2025-12-16 005032.png", "bud-og-omsetning.png"),        # Bud og omsetning med Utfør-meny
    ("Skjermbilde 2025-12-16 004836.png", "oppdrag-dashboard.png"),       # Dashboard med aktiviteter og sjekkliste
]

# Convert images to Base64 with correct mapping
image_base64_map = {}

for source_file, target_name in image_mapping:
    img_path = images_dir / source_file
    if img_path.exists():
        with open(img_path, 'rb') as f:
            img_data = f.read()
            base64_data = base64.b64encode(img_data).decode('utf-8')
            image_base64_map[target_name] = base64_data
            print(f"  {source_file} -> {target_name} ({len(base64_data)} chars)")
    else:
        print(f"  WARNING: {source_file} not found!")

# Convert logo files
print("\nConverting logos...")
lily_path = utkast_dir / "Lilje_Hel_WarmGrey.1.0.png"
logo_path = utkast_dir / "logo.svg"

if lily_path.exists():
    with open(lily_path, 'rb') as f:
        lily_base64 = base64.b64encode(f.read()).decode('utf-8')
        image_base64_map["lilje_hel_warmgrey.png"] = lily_base64
        print(f"  Lily logo: {len(lily_base64)} chars")

if logo_path.exists():
    with open(logo_path, 'rb') as f:
        logo_base64 = base64.b64encode(f.read()).decode('utf-8')
        image_base64_map["logo.svg"] = logo_base64
        print(f"  Logo SVG: {len(logo_base64)} chars")

# Save to JSON file
output_file = base_dir / "image_base64_map_corrected.json"
with open(output_file, 'w', encoding='utf-8') as f:
    json.dump(image_base64_map, f, indent=2)

print(f"\nSaved corrected mapping to {output_file}")
print(f"Total entries: {len(image_base64_map)}")

