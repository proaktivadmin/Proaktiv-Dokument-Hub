"""
Template Diff Tool — generates before/after comparison for template changes.

Produces both a human-readable diff report and a structured JSON summary
for the pipeline's QA review process.

Usage:
    python template_diff.py <before.html> <after.html>
    python template_diff.py <before.html> <after.html> --output diff_report.md
    python template_diff.py <before.html> <after.html> --json
"""

import argparse
import difflib
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path


def read_file(path: str) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read()


def extract_merge_fields(html: str) -> set[str]:
    return set(re.findall(r"\[\[[\*]?([^\]]+)\]\]", html))


def extract_vitec_ifs(html: str) -> set[str]:
    return set(re.findall(r'vitec-if="([^"]*)"', html))


def extract_vitec_foreachs(html: str) -> set[str]:
    return set(re.findall(r'vitec-foreach="([^"]*)"', html))


def extract_text_content(html: str) -> str:
    """Strip HTML tags to get plain text for content comparison."""
    text = re.sub(r"<style[^>]*>.*?</style>", "", html, flags=re.DOTALL)
    text = re.sub(r"<[^>]+>", " ", text)
    text = re.sub(r"\s+", " ", text).strip()
    return text


def analyze_structural_changes(before: str, after: str) -> dict:
    """Analyze structural differences between two templates."""
    before_fields = extract_merge_fields(before)
    after_fields = extract_merge_fields(after)

    before_ifs = extract_vitec_ifs(before)
    after_ifs = extract_vitec_ifs(after)

    before_loops = extract_vitec_foreachs(before)
    after_loops = extract_vitec_foreachs(after)

    before_articles = len(re.findall(r"<article\b", before))
    after_articles = len(re.findall(r"<article\b", after))

    before_tables = len(re.findall(r"<table\b", before))
    after_tables = len(re.findall(r"<table\b", after))

    return {
        "merge_fields": {
            "added": sorted(after_fields - before_fields),
            "removed": sorted(before_fields - after_fields),
            "unchanged": len(before_fields & after_fields),
            "before_count": len(before_fields),
            "after_count": len(after_fields),
        },
        "conditions": {
            "added": sorted(after_ifs - before_ifs),
            "removed": sorted(before_ifs - after_ifs),
            "before_count": len(before_ifs),
            "after_count": len(after_ifs),
        },
        "loops": {
            "added": sorted(after_loops - before_loops),
            "removed": sorted(before_loops - after_loops),
            "before_count": len(before_loops),
            "after_count": len(after_loops),
        },
        "structure": {
            "articles_before": before_articles,
            "articles_after": after_articles,
            "tables_before": before_tables,
            "tables_after": after_tables,
        },
        "size": {
            "before_bytes": len(before.encode("utf-8")),
            "after_bytes": len(after.encode("utf-8")),
            "delta_bytes": len(after.encode("utf-8")) - len(before.encode("utf-8")),
        },
    }


def generate_unified_diff(before: str, after: str, before_path: str, after_path: str) -> str:
    """Generate a unified diff of the two files."""
    before_lines = before.splitlines(keepends=True)
    after_lines = after.splitlines(keepends=True)
    diff = difflib.unified_diff(
        before_lines,
        after_lines,
        fromfile=before_path,
        tofile=after_path,
        lineterm="",
    )
    return "\n".join(diff)


def generate_report(
    before_path: str,
    after_path: str,
    before: str,
    after: str,
    analysis: dict,
) -> str:
    """Generate a human-readable markdown diff report."""
    lines = []
    lines.append("# Template Diff Report")
    lines.append("")
    lines.append(f"**Generated**: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}")
    lines.append(f"**Before**: `{os.path.basename(before_path)}`")
    lines.append(f"**After**: `{os.path.basename(after_path)}`")
    lines.append("")

    size = analysis["size"]
    delta_pct = (size["delta_bytes"] / max(size["before_bytes"], 1)) * 100
    sign = "+" if size["delta_bytes"] >= 0 else ""
    lines.append(f"**Size**: {size['before_bytes']:,} -> {size['after_bytes']:,} bytes ({sign}{size['delta_bytes']:,}, {sign}{delta_pct:.1f}%)")
    lines.append("")

    # Risk assessment
    fields = analysis["merge_fields"]
    conds = analysis["conditions"]
    loops = analysis["loops"]

    risk_factors = []
    if fields["removed"]:
        risk_factors.append(f"REMOVED merge fields: {', '.join(fields['removed'])}")
    if conds["removed"]:
        risk_factors.append(f"REMOVED conditions: {', '.join(conds['removed'])}")
    if loops["removed"]:
        risk_factors.append(f"REMOVED loops: {', '.join(loops['removed'])}")

    if risk_factors:
        lines.append("## !! Risk Warnings")
        lines.append("")
        for r in risk_factors:
            lines.append(f"- {r}")
        lines.append("")

    # Merge field changes
    lines.append("## Merge Fields")
    lines.append("")
    lines.append(f"Before: {fields['before_count']} | After: {fields['after_count']} | Unchanged: {fields['unchanged']}")
    if fields["added"]:
        lines.append(f"**Added**: {', '.join(f'`[[{f}]]`' for f in fields['added'])}")
    if fields["removed"]:
        lines.append(f"**Removed**: {', '.join(f'`[[{f}]]`' for f in fields['removed'])}")
    lines.append("")

    # Condition changes
    lines.append("## Conditions")
    lines.append("")
    lines.append(f"Before: {conds['before_count']} | After: {conds['after_count']}")
    if conds["added"]:
        lines.append(f"**Added**: {', '.join(f'`{c}`' for c in conds['added'])}")
    if conds["removed"]:
        lines.append(f"**Removed**: {', '.join(f'`{c}`' for c in conds['removed'])}")
    lines.append("")

    # Loop changes
    if loops["before_count"] > 0 or loops["after_count"] > 0:
        lines.append("## Loops")
        lines.append("")
        lines.append(f"Before: {loops['before_count']} | After: {loops['after_count']}")
        if loops["added"]:
            lines.append(f"**Added**: {', '.join(f'`{l}`' for l in loops['added'])}")
        if loops["removed"]:
            lines.append(f"**Removed**: {', '.join(f'`{l}`' for l in loops['removed'])}")
        lines.append("")

    # Structure
    struct = analysis["structure"]
    lines.append("## Structure")
    lines.append("")
    lines.append(f"Articles: {struct['articles_before']} -> {struct['articles_after']}")
    lines.append(f"Tables: {struct['tables_before']} -> {struct['tables_after']}")
    lines.append("")

    # Text content diff (summary)
    before_text = extract_text_content(before)
    after_text = extract_text_content(after)
    text_ratio = difflib.SequenceMatcher(None, before_text, after_text).ratio()
    lines.append(f"## Content Similarity: {text_ratio:.1%}")
    lines.append("")

    # Unified diff (truncated for readability)
    diff_text = generate_unified_diff(before, after, before_path, after_path)
    diff_lines = diff_text.split("\n")
    if len(diff_lines) > 200:
        lines.append(f"## Unified Diff (showing first 200 of {len(diff_lines)} lines)")
        lines.append("")
        lines.append("```diff")
        lines.extend(diff_lines[:200])
        lines.append("```")
        lines.append(f"\n*... {len(diff_lines) - 200} more lines truncated*")
    else:
        lines.append("## Unified Diff")
        lines.append("")
        lines.append("```diff")
        lines.extend(diff_lines)
        lines.append("```")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Generate a diff report between two template versions",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("before", help="Path to the before (original) HTML template")
    parser.add_argument("after", help="Path to the after (modified) HTML template")
    parser.add_argument("--output", "-o", help="Write report to file (default: stdout)")
    parser.add_argument("--json", action="store_true", help="Output structured JSON instead of markdown")
    args = parser.parse_args()

    for path in [args.before, args.after]:
        if not os.path.isfile(path):
            print(f"ERROR: File not found: {path}", file=sys.stderr)
            sys.exit(2)

    before = read_file(args.before)
    after = read_file(args.after)

    analysis = analyze_structural_changes(before, after)

    if args.json:
        analysis["before_file"] = args.before
        analysis["after_file"] = args.after
        analysis["generated_at"] = datetime.now(timezone.utc).isoformat()
        output = json.dumps(analysis, indent=2, ensure_ascii=False)
    else:
        output = generate_report(args.before, args.after, before, after, analysis)

    if args.output:
        Path(args.output).parent.mkdir(parents=True, exist_ok=True)
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output)
        print(f"Report written to: {args.output}")
    else:
        print(output)


if __name__ == "__main__":
    main()
