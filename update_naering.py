import json
import re
from pathlib import Path

# Paths
base_dir = Path(r"C:\Users\Adrian\Documents\.cursor\puncheveiledning")
html_file = base_dir / "puncheguide_naering_prosjekt.html"
json_file = base_dir / "image_base64_map.json"

# Load Base64 mappings
with open(json_file, 'r', encoding='utf-8') as f:
    image_map = json.load(f)

# Read HTML
with open(html_file, 'r', encoding='utf-8') as f:
    html_content = f.read()

print("Updating naering_prosjekt HTML file...")

# Replace logo references
html_content = html_content.replace(
    'src="https://proaktiv.no/assets/logos/lilje_hel_warmgrey.png"',
    f'src="data:image/png;base64,{image_map["lilje_hel_warmgrey.png"]}"'
)
html_content = html_content.replace(
    'src="https://proaktiv.no/assets/logos/logo.svg"',
    f'src="data:image/svg+xml;base64,{image_map["logo.svg"]}"'
)

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

# Update CSS for watermark-lily class to add opacity
if '.watermark-lily' in html_content and 'opacity:' not in html_content.split('.watermark-lily')[1].split('}')[0]:
    html_content = re.sub(
        r'(\.watermark-lily\s*\{[^}]*)(\})',
        r'\1\n            opacity: 0.10;\n        \2',
        html_content
    )

# Add accordion system if not present
if 'img-toggle' not in html_content:
    # Add CSS for accordion
    accordion_css = """
        /* ===========================================
           SCREENSHOT SYSTEM - DIGITAL VERSION
           Collapsible accordion for inline viewing
           =========================================== */
        .img-toggle {
            display: inline-flex;
            align-items: center;
            gap: 6px;
            background: var(--color-beige);
            border: 1px solid var(--color-bronze);
            padding: 6px 12px;
            font-size: 11px;
            font-weight: 600;
            color: var(--color-dark);
            cursor: pointer;
            border-radius: 3px;
            margin: 10px 0;
            transition: all 0.2s ease;
        }
        .img-toggle:hover {
            background: var(--color-bronze);
            color: white;
        }
        .img-toggle::before {
            content: "📷";
            font-size: 12px;
        }
        .img-toggle::after {
            content: "▼";
            font-size: 8px;
            transition: transform 0.2s ease;
        }
        .img-toggle.active::after {
            transform: rotate(180deg);
        }

        .img-container {
            max-height: 0;
            overflow: hidden;
            transition: max-height 0.3s ease;
            margin: 0 0 15px 0;
        }
        .img-container.open {
            max-height: 600px;
        }
        .img-container img {
            width: 100%;
            border: 1px solid #ddd;
            border-radius: 4px;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
        }
        .img-caption {
            font-size: 10px;
            color: #888;
            font-style: italic;
            margin-top: 6px;
            text-align: center;
        }

        /* Image reference for print */
        .img-ref {
            display: inline-block;
            background: var(--color-beige);
            padding: 2px 8px;
            font-size: 10px;
            font-weight: 600;
            color: var(--color-bronze);
            border-radius: 3px;
            margin-left: 5px;
        }
"""
    # Insert before @media print
    if '@media print' in html_content:
        html_content = html_content.replace('@media print', accordion_css + '\n        @media print')

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

# Insert print CSS additions before @media print (if not already there)
if '@page' not in html_content and '@media print' in html_content:
    html_content = html_content.replace('@media print', print_css_additions + '\n        @media print')

# Add print media query improvements if not present
if '.img-toggle' in html_content and '@media print' in html_content:
    if '.img-toggle { display: none' not in html_content:
        # Add print hiding rules
        print_hide = """
            /* Hide digital-only elements in print */
            .img-toggle { display: none !important; }
            .img-container { display: none !important; }
            
            /* Show print references */
            .img-ref { display: inline-block !important; }
"""
        html_content = html_content.replace(
            '@media print {',
            '@media print {' + print_hide
        )

# Add screen media query if not present
if '@media screen' not in html_content:
    screen_css = """
        @media screen {
            .print-only { display: none; }
            .img-ref { display: none; }
        }
"""
    # Insert before closing style tag
    html_content = html_content.replace('</style>', screen_css + '\n    </style>')

# Add JavaScript for accordion if not present
if 'function toggleImg' not in html_content:
    accordion_js = """
    <script>
        function toggleImg(button) {
            button.classList.toggle('active');
            const container = button.nextElementSibling;
            if (container && container.classList.contains('img-container')) {
                container.classList.toggle('open');
            }
        }
    </script>
"""
    html_content = html_content.replace('</body>', accordion_js + '\n</body>')

# Write updated HTML
output_file = base_dir / "puncheguide_naering_prosjekt.html"
with open(output_file, 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"Updated {output_file}")
print("Changes made:")
print("  - Updated logo references")
print("  - Removed bracket divs")
print("  - Fixed watermark CSS")
print("  - Added accordion system")
print("  - Added print break-inside rules")
