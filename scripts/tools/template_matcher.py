"""
Template Matcher — finds templates in the master library by various strategies.

Used by the orchestrator command to resolve human-language template references
to actual template files in templates/index.json.

Usage:
    python template_matcher.py "akseptbrev kjøper"
    python template_matcher.py --category "Kontrakt"
    python template_matcher.py --id "2a5982c3-fe34-4beb-8e3b-5c49f2942c4a"
    python template_matcher.py --grep "telefonnummer"
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path

TEMPLATES_ROOT = Path(__file__).resolve().parent.parent.parent / "templates"
INDEX_PATH = TEMPLATES_ROOT / "index.json"


def load_index() -> dict:
    with open(INDEX_PATH, encoding="utf-8") as f:
        return json.load(f)


def normalize(text: str) -> str:
    """Lowercase and strip special chars for fuzzy matching."""
    text = text.lower().strip()
    text = text.replace("æ", "ae").replace("ø", "o").replace("å", "a")
    text = re.sub(r"[^a-z0-9\s]", "", text)
    return re.sub(r"\s+", " ", text)


def score_match(query_tokens: list[str], candidate: str) -> float:
    """Score how well query tokens match a candidate string (0-1)."""
    candidate_norm = normalize(candidate)
    matched = sum(1 for t in query_tokens if t in candidate_norm)
    if not query_tokens:
        return 0.0
    return matched / len(query_tokens)


def find_by_id(index: dict, template_id: str) -> list[dict]:
    """Exact match on vitec_template_id."""
    return [
        t for t in index["templates"]
        if t["vitec_template_id"] == template_id
    ]


def find_by_exact_title(index: dict, title: str) -> list[dict]:
    """Case-insensitive exact substring match on title."""
    title_lower = title.lower().strip()
    return [
        t for t in index["templates"]
        if title_lower in t["title"].lower()
    ]


def find_by_category(index: dict, category: str) -> list[dict]:
    """Match templates by category name (case-insensitive substring)."""
    cat_lower = category.lower().strip()
    return [
        t for t in index["templates"]
        if cat_lower in t.get("category", "").lower()
    ]


def find_by_fuzzy(index: dict, query: str, threshold: float = 0.5) -> list[dict]:
    """Fuzzy token-based search across title + category."""
    tokens = normalize(query).split()
    if not tokens:
        return []

    scored = []
    for t in index["templates"]:
        combined = f"{t['title']} {t.get('category', '')}"
        s = score_match(tokens, combined)
        if s >= threshold:
            scored.append((s, t))

    scored.sort(key=lambda x: x[0], reverse=True)
    return [t for _, t in scored]


def find_by_content_grep(index: dict, pattern: str) -> list[dict]:
    """Search through actual HTML files for a text pattern."""
    matches = []
    pattern_re = re.compile(re.escape(pattern), re.IGNORECASE)

    for t in index["templates"]:
        file_path = TEMPLATES_ROOT / t["file"]
        if file_path.exists():
            try:
                content = file_path.read_text(encoding="utf-8")
                if pattern_re.search(content):
                    matches.append(t)
            except (OSError, UnicodeDecodeError):
                continue
    return matches


def find_template(
    query: str | None = None,
    template_id: str | None = None,
    category: str | None = None,
    grep: str | None = None,
) -> list[dict]:
    """
    Multi-strategy template search. Tries strategies in order of specificity:
    1. Exact ID match
    2. Exact title substring match
    3. Category match
    4. Fuzzy title/category search
    5. Content grep (slowest)
    """
    index = load_index()

    if template_id:
        results = find_by_id(index, template_id)
        if results:
            return results

    if category:
        results = find_by_category(index, category)
        if results:
            return results

    if query:
        results = find_by_exact_title(index, query)
        if results:
            return results

        results = find_by_fuzzy(index, query)
        if results:
            return results

    if grep:
        results = find_by_content_grep(index, grep)
        if results:
            return results

    if query and not grep:
        results = find_by_content_grep(index, query)
        if results:
            return results

    return []


def format_result(t: dict) -> str:
    """Format a single template result for display."""
    status_label = {"published": "[PUB]", "archived": "[ARK]", "draft": "[UTKAST]"}.get(t.get("status", ""), "[?]")
    return (
        f"  {status_label} {t['title']}\n"
        f"     ID: {t['vitec_template_id']}\n"
        f"     Category: {t.get('category', 'N/A')} | Channel: {t.get('channel', 'N/A')} | Origin: {t.get('origin', 'N/A')}\n"
        f"     File: {t['file']}"
    )


def main():
    parser = argparse.ArgumentParser(
        description="Find templates in the master library",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("query", nargs="?", help="Search query (title, partial name, keywords)")
    parser.add_argument("--id", dest="template_id", help="Exact Vitec template ID (UUID)")
    parser.add_argument("--category", help="Filter by category name")
    parser.add_argument("--grep", help="Search inside HTML content")
    parser.add_argument("--json", action="store_true", help="Output results as JSON")
    parser.add_argument("--limit", type=int, default=10, help="Max results to show (default: 10)")
    args = parser.parse_args()

    if not any([args.query, args.template_id, args.category, args.grep]):
        parser.print_help()
        sys.exit(1)

    results = find_template(
        query=args.query,
        template_id=args.template_id,
        category=args.category,
        grep=args.grep,
    )

    if args.json:
        print(json.dumps(results[:args.limit], indent=2, ensure_ascii=False))
    else:
        if not results:
            print("No templates found.")
            sys.exit(1)

        total = len(results)
        showing = min(total, args.limit)
        print(f"Found {total} template(s), showing {showing}:\n")
        for t in results[:args.limit]:
            print(format_result(t))
            print()

        if total > args.limit:
            print(f"  ... and {total - args.limit} more. Use --limit to show more.")


if __name__ == "__main__":
    main()
