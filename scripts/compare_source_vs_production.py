"""Compare source Word .htm files against production HTML templates.
Identifies content gaps, missing sections, and unmapped merge fields."""

import re
from pathlib import Path

CONVERTED = Path(r"C:\Users\Adrian\Documents\Proaktiv-Dokument-Hub\scripts\converted_html")
SOURCE_ENEBOLIG = CONVERTED / "SOURCE_enebolig.htm"
SOURCE_SELVEIER = CONVERTED / "SOURCE_selveier_leilighet.htm"
PROD_ENEBOLIG = CONVERTED / "Kjopekontrakt_prosjekt_enebolig_PRODUCTION.html"
PROD_LEILIGHET = CONVERTED / "Kjopekontrakt_prosjekt_leilighet_PRODUCTION.html"


def extract_text_content(html: str) -> str:
    clean = re.sub(r'<style[^>]*>.*?</style>', '', html, flags=re.DOTALL)
    clean = re.sub(r'<[^>]+>', ' ', clean)
    clean = re.sub(r'&nbsp;', ' ', clean)
    clean = re.sub(r'&amp;', '&', clean)
    clean = re.sub(r'&lt;', '<', clean)
    clean = re.sub(r'&gt;', '>', clean)
    clean = re.sub(r'&oslash;', '\u00f8', clean)
    clean = re.sub(r'&aring;', '\u00e5', clean)
    clean = re.sub(r'&aelig;', '\u00e6', clean)
    clean = re.sub(r'&Oslash;', '\u00d8', clean)
    clean = re.sub(r'&Aring;', '\u00c5', clean)
    clean = re.sub(r'&sect;', '\u00a7', clean)
    clean = re.sub(r'&laquo;', '\u00ab', clean)
    clean = re.sub(r'&raquo;', '\u00bb', clean)
    clean = re.sub(r'&ldquo;', '\u201c', clean)
    clean = re.sub(r'&rdquo;', '\u201d', clean)
    clean = re.sub(r'&mdash;', '\u2014', clean)
    clean = re.sub(r'&ndash;', '\u2013', clean)
    clean = re.sub(r'&#\d+;', '', clean)
    clean = re.sub(r'\s+', ' ', clean).strip()
    return clean


def extract_legacy_fields(html: str) -> list[str]:
    return sorted(set(re.findall(r'#([a-z_]+(?:\.[a-z_]+)*)(?:&\s*)?¤', html, re.IGNORECASE)))


def extract_modern_fields(html: str) -> list[str]:
    return sorted(set(re.findall(r'\[\[\*?([^\]]+)\]\]', html)))


def extract_section_headings(text: str) -> list[str]:
    lines = text.split('  ')
    headings = []
    for line in lines:
        line = line.strip()
        upper = line.upper()
        if upper == line and len(line) > 5 and len(line) < 80 and any(c.isalpha() for c in line):
            if not line.startswith('q ') and not line.startswith('\u2610') and not line.startswith('\u2611'):
                headings.append(line)
    return headings


def count_checkbox_q(text: str) -> int:
    return len(re.findall(r'\bq\b', text))


def count_checkbox_unicode(text: str) -> int:
    return len(re.findall(r'[\u2610\u2611]', text))


def compare_pair(src_path: Path, prod_path: Path, label: str):
    try:
        src_html = src_path.read_text(encoding='utf-8')
    except UnicodeDecodeError:
        src_html = src_path.read_text(encoding='cp1252')
    prod_html = prod_path.read_text(encoding='utf-8')

    src_text = extract_text_content(src_html)
    prod_text = extract_text_content(prod_html)

    src_fields = extract_legacy_fields(src_html)
    prod_fields = extract_modern_fields(prod_html)

    src_checkboxes = count_checkbox_q(src_text)
    prod_checkboxes = count_checkbox_unicode(prod_text)

    print(f"\n{'='*70}")
    print(f"  {label}")
    print(f"{'='*70}")
    print(f"\n--- Size ---")
    print(f"  Source HTML:     {len(src_html):>8,} chars")
    print(f"  Production HTML: {len(prod_html):>8,} chars")
    print(f"  Source text:     {len(src_text):>8,} chars")
    print(f"  Production text: {len(prod_text):>8,} chars")

    print(f"\n--- Merge Fields ---")
    print(f"  Source (legacy #...¤): {len(src_fields)}")
    for f in src_fields:
        print(f"    #{f}¤")
    print(f"  Production ([[...]]): {len(prod_fields)}")
    for f in prod_fields:
        print(f"    [[{f}]]")

    print(f"\n--- Checkboxes ---")
    print(f"  Source 'q' checkboxes: {src_checkboxes}")
    print(f"  Production Unicode checkboxes: {prod_checkboxes}")
    if src_checkboxes != prod_checkboxes:
        print(f"  *** MISMATCH: {abs(src_checkboxes - prod_checkboxes)} checkbox(es) differ ***")

    src_keywords = set()
    prod_keywords = set()
    section_markers = [
        "SALGSOBJEKT OG TILBEH",
        "KJOPESUM OG OMKOSTNINGER",
        "KJØPESUM OG OMKOSTNINGER",
        "SELGERS PLIKT",
        "OPPGJ",
        "HEFTELSER",
        "TINGLYSING",
        "MANGELSANSVAR",
        "ENDRINGSARBEIDER",
        "OVERTAKELSE",
        "ETT\u00c5RSBEFARING",
        "ETTÅRSBEFARING",
        "SELGERS KONTRAKTSBRUDD",
        "KJØPERS KONTRAKTSBRUDD",
        "FORSIKRING",
        "AVBESTILLING",
        "SELGERS FORBEHOLD",
        "ANNET",
        "SAMTYKKE",
        "VERNETING",
        "BILAG",
        "SIGNATUR",
    ]

    print(f"\n--- Section Presence ---")
    for marker in section_markers:
        in_src = marker.lower() in src_text.lower()
        in_prod = marker.lower() in prod_text.lower()
        status = "OK" if in_src and in_prod else "MISSING IN PROD" if in_src and not in_prod else "ADDED" if not in_src and in_prod else "BOTH MISSING"
        if status != "OK":
            print(f"  [{status}] {marker}")
        else:
            print(f"  [OK] {marker}")

    key_phrases = [
        "Eierseksjonsloven",
        "realsameie",
        "fullmektig",
        "bustadoppføringslova § 12",
        "bustadoppføringslova § 47",
        "forskuddsbetaling",
        "forskuddsgaranti",
        "Alternativ 1",
        "Alternativ 2",
        "For tomten",
        "For boligen",
        "delinnbetaling",
        "Kontrollbefaring",
        "kontrollbefaring",
        "tvangsfravikelse",
        "ettårsbefaring",
        "dagmulkt",
        "Boligkjøperforsikring",
        "boligkjøperforsikring",
    ]

    print(f"\n--- Key Content Phrases ---")
    for phrase in key_phrases:
        in_src = phrase.lower() in src_text.lower()
        in_prod = phrase.lower() in prod_text.lower()
        if in_src != in_prod:
            if in_src and not in_prod:
                print(f"  [MISSING IN PROD] \"{phrase}\"")
            else:
                print(f"  [ADDED IN PROD] \"{phrase}\"")


if __name__ == "__main__":
    print("SOURCE vs PRODUCTION TEMPLATE COMPARISON")
    print("=" * 70)

    compare_pair(SOURCE_ENEBOLIG, PROD_ENEBOLIG, "ENEBOLIG: Source .htm vs Production .html")
    compare_pair(SOURCE_SELVEIER, PROD_LEILIGHET, "LEILIGHET: Selveier Source .htm vs Leilighet Production .html")

    print("\n\n--- CROSS-TEMPLATE: Source Differences (Enebolig vs Selveier) ---")
    try:
        ene_src = SOURCE_ENEBOLIG.read_text(encoding='utf-8')
    except UnicodeDecodeError:
        ene_src = SOURCE_ENEBOLIG.read_text(encoding='cp1252')
    try:
        sel_src = SOURCE_SELVEIER.read_text(encoding='utf-8')
    except UnicodeDecodeError:
        sel_src = SOURCE_SELVEIER.read_text(encoding='cp1252')
    ene_text = extract_text_content(ene_src)
    sel_text = extract_text_content(sel_src)

    ene_fields = extract_legacy_fields(ene_src)
    sel_fields = extract_legacy_fields(sel_src)

    if ene_fields == sel_fields:
        print("  Merge fields: IDENTICAL")
    else:
        only_ene = set(ene_fields) - set(sel_fields)
        only_sel = set(sel_fields) - set(ene_fields)
        if only_ene:
            print(f"  Only in enebolig source: {only_ene}")
        if only_sel:
            print(f"  Only in selveier source: {only_sel}")

    ene_q = count_checkbox_q(ene_text)
    sel_q = count_checkbox_q(sel_text)
    print(f"  Enebolig source checkboxes: {ene_q}")
    print(f"  Selveier source checkboxes: {sel_q}")
