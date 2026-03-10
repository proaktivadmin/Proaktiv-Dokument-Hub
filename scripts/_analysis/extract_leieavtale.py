#!/usr/bin/env python3
"""Extract structure from leieavtale source HTML for analysis."""
import re
from pathlib import Path

def extract_structure(path: str) -> dict:
    with open(path, 'r', encoding='utf-8', errors='replace') as f:
        html = f.read()
    
    # H1 section headings
    h1s = re.findall(r'<h1>([^<]+)</h1>', html)
    
    # Numbered subsections X.Y
    subs = re.findall(r'>(\d+\.\d+)\s+([^<]{5,80})', html)
    
    # Fill-ins: [x] where x is ellipsis, short, or placeholder
    # Unicode ellipsis U+2026
    ellipsis_fills = len(re.findall(r'\[\s*…\s*\]|\[\s*\.{2,}\s*\]', html))
    # Generic short brackets
    bracket_groups = re.findall(r'\[([^\]]{1,50})\]', html)
    fill_style = [b for b in bracket_groups if 
        '…' in b or '..' in b or b.strip() in ('', 'dato', 'og megler') 
        or (len(b) <= 5 and not b.startswith('Bilag') and not b.startswith('Tillegg')
            and not b.startswith('Stryk') and not b.startswith('Alternative'))]
    
    # Full list of meaningful fill-ins with context
    fill_contexts = []
    for m in re.finditer(r'[^\[\]]{0,50}\[([^\]]{1,30})\][^\[\]]{0,50}', html):
        inner = m.group(1)
        if ('Bilag' in inner or 'Tillegg' in inner or 'Stryk' in inner 
            or 'Alternative' in inner or 'Veiledning' in inner or len(inner) > 25):
            continue
        ctx = m.group(0).replace('\n', ' ').strip()
        fill_contexts.append((inner, ctx[:100]))
    
    # Stryk choice points
    stryk = re.findall(r'\[[^\]]*[Ss]tryk[^\]]*\]|[^<]{0,30}stryk det som ikke passer[^<]{0,30}', html)
    
    # Bilag refs
    bilag = sorted(set(re.findall(r'Bilag\s*\d+', html)))
    
    # Commentary markers
    veiledning = re.findall(r'[Vv]eiledning(?:\s+til)?[^<]{0,60}', html)
    
    return {
        'h1': [h.strip() for h in h1s],
        'subs': subs[:80],
        'fill_count': len(fill_style),
        'fill_contexts': fill_contexts[:80],
        'stryk': stryk,
        'bilag': bilag,
        'veiledning': veiledning,
    }

def main():
    base = Path(__file__).parent.parent / 'source_html'
    brukt = extract_structure(str(base / 'leieavtale_naeringslokaler_brukt.html'))
    nye = extract_structure(str(base / 'leieavtale_naeringslokaler_nye.html'))
    
    print("BRUKT H1:", len(brukt['h1']))
    for i, h in enumerate(brukt['h1'], 1):
        print(f"  {i}. {h}")
    print("\nNYE H1:", len(nye['h1']))
    for i, h in enumerate(nye['h1'], 1):
        print(f"  {i}. {h}")
    
    print("\n--- DIFFERS ---")
    for i in range(max(len(brukt['h1']), len(nye['h1']))):
        b = brukt['h1'][i] if i < len(brukt['h1']) else "(none)"
        n = nye['h1'][i] if i < len(nye['h1']) else "(none)"
        if b != n:
            print(f"  {i+1}. Brukt: {b} | Nye: {n}")
    
    print("\n--- FILL-IN CONTEXTS (Brukt, sample) ---")
    seen = set()
    for inner, ctx in brukt['fill_contexts']:
        key = (inner[:20], ctx[:50])
        if key not in seen:
            seen.add(key)
            print(f"  [{inner}] -> ...{ctx}...")
    
    print("\n--- BILAG ---")
    print("Brukt:", brukt['bilag'])
    print("Nye:", nye['bilag'])

if __name__ == '__main__':
    main()
