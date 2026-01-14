import re
from pathlib import Path

html_file = Path(r"C:\Users\Adrian\Documents\.cursor\puncheveiledning\puncheguide_bruktbolig.html")

with open(html_file, 'r', encoding='utf-8') as f:
    content = f.read()

print("=== Verifying Image Mapping ===\n")

# Find all img-toggle buttons and their associated images
# Pattern: button followed by img-container with img
pattern = r'<button class="img-toggle"[^>]*>([^<]+)</button>\s*<div class="img-container">\s*<img src="(data:image/[^"]+)"'

matches = re.findall(pattern, content[:500000], re.DOTALL)

print(f"Found {len(matches)} button-image pairs in main content\n")

for i, (button_text, img_src) in enumerate(matches[:10], 1):
    # Get first 50 chars of base64 to identify image
    base64_start = img_src.split(',')[1][:50] if ',' in img_src else img_src[:50]
    print(f"{i}. Button: {button_text.strip()}")
    print(f"   Image base64 start: {base64_start}...")
    print()

# Verify specific mappings by checking the order
print("\n=== Expected Order (from HTML) ===")
expected = [
    ("Vis: Sok og opprett kontakt", "002830 - Sokefelt med Ingen treff"),
    ("Vis: Nytt eierskap", "003030 - Eierskap med Nytt eierskap knapp"),
    ("Vis: Opprett befaring", "003123 - Eierskap med Opprett befaring i meny"),
    ("Vis: Oppdragstype-valg", "003224 - Opprett befaring skjema"),
    ("Vis: Oppdragsparter", "004423 - Oppdragsparter med meny"),
    ("Vis: Selger-meny", "004647 - Selger panel med verktoy"),
    ("Vis: ID-verifisering", "004633 - Ny identifikasjon"),
    ("Vis: Alfanavn-feltet", "004033 - Objektbeskrivelse med ALFANAVN"),
]

for button, expected_img in expected:
    print(f"  {button} -> {expected_img}")

print("\n=== Verification Complete ===")
print("Please open the HTML file in a browser to visually verify the mappings.")

