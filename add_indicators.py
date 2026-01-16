import re
from pathlib import Path

# Paths
base_dir = Path(r"C:\Users\Adrian\Documents\.cursor\puncheveiledning")
html_file = base_dir / "puncheguide_bruktbolig.html"

print("Adding SVG indicators to images...")

# Read HTML
with open(html_file, 'r', encoding='utf-8') as f:
    html_content = f.read()

# CSS for indicators - insert before </style>
indicator_css = """
        /* SVG Indicator Overlays */
        .img-wrapper {
            position: relative;
            display: inline-block;
            width: 100%;
        }
        .img-wrapper img {
            display: block;
            width: 100%;
        }
        .indicator-svg {
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            z-index: 10;
        }
        .indicator-box {
            fill: none;
            stroke: #FF6B35;
            stroke-width: 2;
            stroke-dasharray: none;
        }
        .indicator-arrow {
            fill: #FF6B35;
            stroke: none;
        }
        .indicator-circle {
            fill: none;
            stroke: #FF6B35;
            stroke-width: 2;
        }
"""

# Insert CSS before </style>
html_content = html_content.replace('</style>', indicator_css + '\n    </style>')

# Define SVG indicators for each image by alt text
# Coordinates are in percentage (0-100) of image dimensions
indicators = {
    'opprett ny kontakt': '''
        <rect class="indicator-box" x="85" y="20" width="10" height="18" rx="2"/>
        <polygon class="indicator-arrow" points="80,29 85,26 85,32"/>
    ''',
    'nytt eierskap': '''
        <rect class="indicator-box" x="35" y="42" width="18" height="10" rx="2"/>
        <polygon class="indicator-arrow" points="30,47 35,44 35,50"/>
    ''',
    'opprett befaring': '''
        <rect class="indicator-box" x="88" y="8" width="11" height="8" rx="2"/>
        <polygon class="indicator-arrow" points="83,12 88,9 88,15"/>
    ''',
    'opprett befaring skjema': '''
        <rect class="indicator-box" x="5" y="58" width="90" height="8" rx="2"/>
        <polygon class="indicator-arrow" points="50,52 53,58 47,58"/>
    ''',
    'oppdragsparter': '''
        <rect class="indicator-box" x="87" y="12" width="12" height="45" rx="2"/>
        <polygon class="indicator-arrow" points="82,35 87,32 87,38"/>
    ''',
    'selger meny': '''
        <rect class="indicator-box" x="3" y="55" width="94" height="5" rx="2"/>
        <polygon class="indicator-arrow" points="50,50 53,55 47,55"/>
    ''',
    'ny identifikasjon': '''
        <rect class="indicator-box" x="8" y="52" width="84" height="40" rx="3"/>
        <polygon class="indicator-arrow" points="50,47 53,52 47,52"/>
    ''',
    'alfanavn felt': '''
        <rect class="indicator-box" x="28" y="22" width="18" height="6" rx="2"/>
        <polygon class="indicator-arrow" points="23,25 28,22 28,28"/>
    ''',
    'bilder opplasting': '''
        <rect class="indicator-box" x="76" y="14" width="22" height="30" rx="2"/>
        <polygon class="indicator-arrow" points="71,29 76,26 76,32"/>
    ''',
    'dokument kategorisering': '''
        <rect class="indicator-box" x="88" y="26" width="10" height="4" rx="1"/>
        <polygon class="indicator-arrow" points="83,28 88,25 88,31"/>
    ''',
    'budsjett oppstilling': '''
        <rect class="indicator-box" x="38" y="29" width="12" height="5" rx="2"/>
        <polygon class="indicator-arrow" points="33,32 38,29 38,35"/>
    ''',
    'pant og': '''
        <rect class="indicator-box" x="3" y="20" width="94" height="60" rx="3"/>
    ''',
    'sjekkliste': '''
        <rect class="indicator-box" x="70" y="25" width="8" height="55" rx="2"/>
        <polygon class="indicator-arrow" points="65,52 70,49 70,55"/>
    ''',
    'marked og tjenester': '''
        <rect class="indicator-box" x="2" y="32" width="15" height="10" rx="2"/>
        <rect class="indicator-box" x="2" y="50" width="12" height="8" rx="2"/>
    ''',
    'depot og tinglysing': '''
        <rect class="indicator-box" x="73" y="3" width="26" height="95" rx="3"/>
        <polygon class="indicator-arrow" points="68,50 73,47 73,53"/>
    ''',
    'visninger': '''
        <rect class="indicator-box" x="2" y="25" width="10" height="6" rx="2"/>
        <polygon class="indicator-arrow" points="17,28 12,25 12,31"/>
    ''',
    'bud detaljer': '''
        <rect class="indicator-box" x="2" y="18" width="23" height="14" rx="2"/>
        <polygon class="indicator-arrow" points="27,25 25,22 25,28"/>
    ''',
}

# Find all img-container blocks and add wrappers
img_container_pattern = r'(<div class="img-container">)\s*(<img src="data:image/png;base64,[^"]+"\s*alt="([^"]+)"[^>]*>)'

def add_indicator_wrapper(match):
    container_open = match.group(1)
    img_tag = match.group(2)
    alt_text = match.group(3).lower()
    
    svg_content = None
    
    # Match alt text to indicator
    for alt_pattern, svg in indicators.items():
        if alt_pattern in alt_text:
            svg_content = svg
            break
    
    if svg_content:
        wrapped = f'''{container_open}
                    <div class="img-wrapper">
                        {img_tag}
                        <svg class="indicator-svg" viewBox="0 0 100 100" preserveAspectRatio="none">{svg_content}
                        </svg>
                    </div>'''
        return wrapped
    
    return match.group(0)

html_content = re.sub(img_container_pattern, add_indicator_wrapper, html_content)

# Count replacements
wrapped_count = html_content.count('class="img-wrapper"')
print(f"Added {wrapped_count} indicator wrappers")

# Write updated HTML
with open(html_file, 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"Updated {html_file}")
print("Indicators added for images based on their alt text")

