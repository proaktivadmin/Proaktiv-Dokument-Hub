"""
Vitec Template Post-Processor — applies all mandatory fixes automatically.

This is the FINAL step in the build pipeline. It ensures every known
issue from the lessons-learned registry is fixed before validation.

Applies:
  E1: Norwegian character entity encoding (ø→&oslash; etc.)
  E3: Norwegian characters in CSS/HTML comments → ASCII
  S1: Outer table wrapper verification
  S2: Remove proaktiv-theme class if present
  S3: Verify H1 title (warn if H5 found)
  S8: Fix article padding 26px → 20px (production standard)
  S10: Warn if insert-table CSS missing (Chromium fix)
  CB1: Warn if Unicode checkboxes found (needs manual SVG replacement)
  MF2: Warn if bare monetary fields found without $.UD()

Usage:
    python post_process_template.py <template.html>
    python post_process_template.py <template.html> --output fixed.html
    python post_process_template.py <template.html> --dry-run
    python post_process_template.py <template.html> --in-place
"""

import argparse
import os
import re
import sys
from pathlib import Path

ENTITY_MAP = {
    "ø": "&oslash;",
    "å": "&aring;",
    "æ": "&aelig;",
    "Ø": "&Oslash;",
    "Å": "&Aring;",
    "Æ": "&AElig;",
    "§": "&sect;",
    "«": "&laquo;",
    "»": "&raquo;",
    "\u2013": "&ndash;",
    "\u2014": "&mdash;",
    "é": "&eacute;",
}

ENTITY_PATTERN = re.compile("|".join(re.escape(c) for c in ENTITY_MAP))

COMMENT_PATTERN = re.compile(r"(<!--.*?-->|/\*.*?\*/)", re.DOTALL)

COMMENT_CHAR_MAP = {
    "ø": "o",
    "å": "a",
    "æ": "ae",
    "Ø": "O",
    "Å": "A",
    "Æ": "Ae",
    "§": "par.",
    "«": "<<",
    "»": ">>",
    "\u2013": "-",
    "\u2014": "--",
    "é": "e",
}
COMMENT_CHAR_PATTERN = re.compile("|".join(re.escape(c) for c in COMMENT_CHAR_MAP))

MONETARY_FIELDS = [
    "kontrakt.kjopesum",
    "kontrakt.totaleomkostninger",
    "kontrakt.kjopesumogomkostn",
    "kostnad.belop",
    "eiendom.fellesutgifter",
    "eiendom.kommunaleavgifter",
]


def read_file(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read()


def encode_entities_in_text(html: str) -> str:
    """
    Replace Norwegian literal characters with HTML entities,
    but ONLY in text content — not inside HTML tag attributes,
    vitec-if/vitec-foreach expressions, or comments.
    """
    parts = []
    pos = 0

    tag_pattern = re.compile(
        r"(<!--.*?-->|<style[^>]*>.*?</style>|<[^>]+>)",
        re.DOTALL,
    )

    for m in tag_pattern.finditer(html):
        text_before = html[pos:m.start()]
        parts.append(ENTITY_PATTERN.sub(lambda x: ENTITY_MAP[x.group()], text_before))

        tag_content = m.group()
        if tag_content.startswith("<!--") or tag_content.startswith("<style"):
            parts.append(tag_content)
        else:
            parts.append(tag_content)

        pos = m.end()

    remaining = html[pos:]
    parts.append(ENTITY_PATTERN.sub(lambda x: ENTITY_MAP[x.group()], remaining))

    return "".join(parts)


def clean_comments(html: str) -> str:
    """Replace Norwegian characters in HTML/CSS comments with ASCII equivalents."""
    def replace_in_comment(m: re.Match) -> str:
        return COMMENT_CHAR_PATTERN.sub(lambda x: COMMENT_CHAR_MAP[x.group()], m.group())

    return COMMENT_PATTERN.sub(replace_in_comment, html)


def check_outer_table_wrapper(html: str) -> tuple[bool, str]:
    """Verify the template has the outer table wrapper after the style block."""
    style_end = html.rfind("</style>")
    if style_end == -1:
        return False, "No </style> tag found"

    after_style = html[style_end + len("</style>"):style_end + len("</style>") + 200].strip()
    has_table = after_style.startswith("<table")
    if not has_table:
        return False, "Content after </style> does not start with <table>. Wrap body in <table><tbody><tr><td colspan=\"100\">...</td></tr></tbody></table>"
    return True, ""


def check_proaktiv_theme(html: str) -> tuple[bool, str]:
    """Check for and remove proaktiv-theme class."""
    if 'class="proaktiv-theme"' in html:
        return True, "Found class=\"proaktiv-theme\" — should be removed (no reference template uses it)"
    return False, ""


def remove_proaktiv_theme(html: str) -> str:
    """Remove proaktiv-theme class from root div."""
    html = html.replace(' class="proaktiv-theme"', "")
    html = html.replace(" class='proaktiv-theme'", "")
    return html


def check_title_tag(html: str) -> list[str]:
    """Warn if H5 is used for title instead of H1."""
    warnings = []
    if "<h5>" in html.lower() and "<h1>" not in html.lower():
        warnings.append("S3: Template uses <h5> for title. Should use <h1>.")
    return warnings


def check_unicode_checkboxes(html: str) -> list[str]:
    """Warn if Unicode checkbox characters are present."""
    warnings = []
    unicode_checks = re.findall(r"&#9744;|&#9745;|\u2610|\u2611", html)
    if unicode_checks:
        warnings.append(
            f"CB1: Found {len(unicode_checks)} Unicode checkbox character(s). "
            "Replace with SVG checkbox pattern (see PATTERNS.md)."
        )
    return warnings


def check_bare_monetary_fields(html: str) -> list[str]:
    """Warn if monetary fields are used without $.UD() wrapper."""
    warnings = []
    for field in MONETARY_FIELDS:
        bare_pattern = re.compile(rf"\[\[{re.escape(field)}\]\]")
        ud_pattern = re.compile(rf"\$\.UD\(\[\[{re.escape(field)}\]\]\)")
        bare_count = len(bare_pattern.findall(html))
        ud_count = len(ud_pattern.findall(html))
        if bare_count > ud_count:
            warnings.append(
                f"MF2: Found {bare_count - ud_count} bare [[{field}]] without $.UD() wrapper."
            )
    return warnings


def check_foreach_guards(html: str) -> list[str]:
    """Check that all foreach loops have guards and fallbacks."""
    warnings = []
    foreachs = re.findall(r'vitec-foreach="(\w+)\s+in\s+([\w.]+)"', html)
    for item, collection in foreachs:
        guard = f"{collection}.Count"
        if guard not in html:
            warnings.append(f"V2: foreach '{item} in {collection}' has no .Count guard.")
        fallback = f"{collection}.Count == 0"
        if fallback not in html:
            warnings.append(f"V2: foreach '{item} in {collection}' has no empty fallback.")
    return warnings


def fix_article_padding(html: str) -> tuple[str, bool]:
    """Fix article padding from 26px to production standard 20px."""
    fixed = html
    changed = False
    old_patterns = [
        (r"padding-left:\s*26px", "padding-left: 20px"),
        (r"margin:\s*30px\s+0\s+0\s+-26px", "margin: 30px 0 0 -20px"),
    ]
    for pattern, replacement in old_patterns:
        new_html = re.sub(pattern, replacement, fixed)
        if new_html != fixed:
            changed = True
            fixed = new_html
    return fixed, changed


def check_insert_table_css(html: str) -> list[str]:
    """Warn if the Chromium insert-table fix is missing."""
    warnings = []
    has_insert_fields = "insert-table" in html or 'class="insert"' in html or "data-label=" in html
    has_insert_table_css = "display: inline-table" in html or "display:inline-table" in html
    if has_insert_fields and not has_insert_table_css:
        warnings.append(
            "S10: Template uses insert fields but missing Chromium fix: "
            ".insert-table { display: inline-table; } — add from PATTERNS.md section 3"
        )
    return warnings


def post_process(html: str, dry_run: bool = False) -> tuple[str, list[str], list[str]]:
    """
    Apply all mandatory post-processing fixes.
    Returns (processed_html, fixes_applied, warnings).
    """
    fixes = []
    warnings = []

    original = html

    # E3: Clean comments first (before entity encoding)
    cleaned = clean_comments(html)
    if cleaned != html:
        fixes.append("E3: Replaced Norwegian characters in comments with ASCII")
        html = cleaned

    # E1: Entity encoding (the big one)
    encoded = encode_entities_in_text(html)
    if encoded != html:
        literal_count = sum(1 for c in html if c in ENTITY_MAP) - sum(1 for c in encoded if c in ENTITY_MAP)
        fixes.append(f"E1: Encoded {literal_count} Norwegian character(s) as HTML entities")
        html = encoded

    # S2: Remove proaktiv-theme
    has_theme, theme_msg = check_proaktiv_theme(html)
    if has_theme:
        html = remove_proaktiv_theme(html)
        fixes.append("S2: Removed proaktiv-theme class from root div")

    # S8: Fix article padding 26px → 20px
    html, padding_fixed = fix_article_padding(html)
    if padding_fixed:
        fixes.append("S8: Fixed article padding/margin from 26px to production standard 20px")

    # Checks (warnings only — these need manual fixes)
    has_wrapper, wrapper_msg = check_outer_table_wrapper(html)
    if not has_wrapper:
        warnings.append(f"S1: {wrapper_msg}")

    warnings.extend(check_title_tag(html))
    warnings.extend(check_unicode_checkboxes(html))
    warnings.extend(check_bare_monetary_fields(html))
    warnings.extend(check_foreach_guards(html))
    warnings.extend(check_insert_table_css(html))

    if dry_run:
        html = original

    return html, fixes, warnings


def main():
    parser = argparse.ArgumentParser(
        description="Post-process a Vitec template (entity encoding, cleanup, checks)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="This should be the LAST step before validation.\n"
               "Run AFTER all content changes are finalized.",
    )
    parser.add_argument("template", help="Path to the template HTML file")
    parser.add_argument("--output", "-o", help="Write processed file to this path (default: stdout summary)")
    parser.add_argument("--in-place", action="store_true", help="Overwrite the input file")
    parser.add_argument("--dry-run", action="store_true", help="Show what would change without modifying")
    args = parser.parse_args()

    if not os.path.isfile(args.template):
        print(f"ERROR: File not found: {args.template}", file=sys.stderr)
        sys.exit(2)

    html = read_file(args.template)
    processed, fixes, warnings = post_process(html, dry_run=args.dry_run)

    print(f"{'=' * 60}")
    print("VITEC TEMPLATE POST-PROCESSOR")
    print(f"{'=' * 60}")
    print(f"Template: {os.path.basename(args.template)}")
    print(f"Size: {len(html):,} chars")
    if args.dry_run:
        print("Mode: DRY RUN (no changes written)")
    print(f"{'=' * 60}\n")

    if fixes:
        print(f"Fixes applied ({len(fixes)}):")
        for f in fixes:
            print(f"  [FIX] {f}")
        print()
    else:
        print("No fixes needed.\n")

    if warnings:
        print(f"Warnings ({len(warnings)}) — require manual attention:")
        for w in warnings:
            print(f"  [WARN] {w}")
        print()
    else:
        print("No warnings.\n")

    if not args.dry_run:
        if args.in_place:
            with open(args.template, "w", encoding="utf-8") as f:
                f.write(processed)
            print(f"Written in-place: {args.template}")
        elif args.output:
            Path(args.output).parent.mkdir(parents=True, exist_ok=True)
            with open(args.output, "w", encoding="utf-8") as f:
                f.write(processed)
            print(f"Written to: {args.output}")
        else:
            delta = len(processed) - len(html)
            sign = "+" if delta >= 0 else ""
            print(f"Processed size: {len(processed):,} chars ({sign}{delta})")
            if fixes:
                print(f"\nUse --in-place or --output to write the processed file.")

    has_issues = bool(warnings)
    sys.exit(1 if has_issues and not fixes else 0)


if __name__ == "__main__":
    main()
