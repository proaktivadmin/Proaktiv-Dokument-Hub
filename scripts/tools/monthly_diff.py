"""
Monthly Update Diff — content-level comparison between a fresh Vitec export and the stored library.

Unlike vitec_sync_check.py --full-scan (metadata only), this script compares ACTUAL HTML content,
making it suitable for detecting real upstream changes after a Vitec Next monthly release.

Workflow:
    1. Fetch fresh export from Vitec Next (browser session)
    2. Run this script: python scripts/tools/monthly_diff.py --input vitec-next-export.json
    3. Review the report and the JSON output
    4. Feed results to the /monthly-update command for per-template decisions

Outputs:
    scripts/qa_artifacts/MONTHLY-DIFF-{date}.md   (human-readable report)
    scripts/qa_artifacts/monthly-diff-{date}.json  (structured data for agent)

Usage:
    python scripts/tools/monthly_diff.py
    python scripts/tools/monthly_diff.py --input ~/Downloads/vitec-next-export.json
    python scripts/tools/monthly_diff.py --input data/vitec-next-export.json --json
    python scripts/tools/monthly_diff.py --changed-only
"""

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INPUT = REPO_ROOT / "data" / "vitec-next-export.json"
FALLBACK_INPUT = Path.home() / "Downloads" / "vitec-next-export.json"
LIBRARY_DIR = REPO_ROOT / "templates"
INDEX_PATH = LIBRARY_DIR / "index.json"
QA_ARTIFACTS_DIR = REPO_ROOT / "scripts" / "qa_artifacts"

# Change significance thresholds
TRIVIAL_BYTE_DELTA = 50   # changes smaller than this are flagged as trivial
CSS_CHANGE_WEIGHT = 3     # CSS changes count as 3x for significance scoring


def read_file(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="latin-1")


def _extract_merge_fields(html: str) -> set[str]:
    return set(re.findall(r"\[\[\*?([^\]]+)\]\]", html))


def _extract_vitec_ifs(html: str) -> set[str]:
    return set(re.findall(r'vitec-if="([^"]*)"', html))


def _extract_vitec_foreachs(html: str) -> set[str]:
    return set(re.findall(r'vitec-foreach="([^"]*)"', html))


def _extract_css_blocks(html: str) -> list[str]:
    return re.findall(r"<style[^>]*>(.*?)</style>", html, re.DOTALL | re.IGNORECASE)


def _extract_text(html: str) -> str:
    """Strip tags to extract plain text for heuristic comparison."""
    text = re.sub(r"<style[^>]*>.*?</style>", "", html, flags=re.DOTALL)
    text = re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)
    text = re.sub(r"<[^>]+>", " ", text)
    return re.sub(r"\s+", " ", text).strip()


def _score_change(delta: dict) -> int:
    """Score a change for significance (higher = more impactful).

    This drives the risk classification:
        >= 10 → critical (legal/structural)
        >= 4  → structural
        >= 1  → cosmetic
        0     → trivial (whitespace / encoding)
    """
    score = 0
    score += len(delta["merge_fields"]["added"]) * 3
    score += len(delta["merge_fields"]["removed"]) * 3
    score += len(delta["conditions"]["added"]) * 2
    score += len(delta["conditions"]["removed"]) * 2
    score += len(delta["loops"]["added"]) * 2
    score += len(delta["loops"]["removed"]) * 2
    if delta["css_changed"]:
        score += CSS_CHANGE_WEIGHT
    abs_bytes = abs(delta["size_delta_bytes"])
    if abs_bytes > 5000:
        score += 4
    elif abs_bytes > 1000:
        score += 2
    elif abs_bytes > TRIVIAL_BYTE_DELTA:
        score += 1
    return score


def _risk_label(score: int) -> str:
    if score >= 10:
        return "critical"
    if score >= 4:
        return "structural"
    if score >= 1:
        return "cosmetic"
    return "trivial"


def _normalize_html(html: str) -> str:
    """Normalize line endings and trailing whitespace for stable comparison.

    Vitec Next export JSON uses CRLF line endings (Windows server). Stored files
    may have been written with LF normalization by Python's text mode. Normalizing
    before comparison prevents false-positive "changed" detections.
    """
    return html.replace("\r\n", "\n").replace("\r", "\n").strip()


def diff_template(stored_html: str, new_html: str) -> dict:
    """Compute a structured delta between stored and new HTML."""
    stored_norm = _normalize_html(stored_html)
    new_norm = _normalize_html(new_html)

    stored_fields = _extract_merge_fields(stored_norm)
    new_fields = _extract_merge_fields(new_norm)
    stored_ifs = _extract_vitec_ifs(stored_norm)
    new_ifs = _extract_vitec_ifs(new_norm)
    stored_loops = _extract_vitec_foreachs(stored_norm)
    new_loops = _extract_vitec_foreachs(new_norm)
    stored_css = _extract_css_blocks(stored_norm)
    new_css = _extract_css_blocks(new_norm)

    delta = {
        "identical": stored_norm == new_norm,
        "size_delta_bytes": len(new_norm.encode()) - len(stored_norm.encode()),
        "size_stored_bytes": len(stored_norm.encode()),
        "size_new_bytes": len(new_norm.encode()),
        "merge_fields": {
            "stored_count": len(stored_fields),
            "new_count": len(new_fields),
            "added": sorted(new_fields - stored_fields),
            "removed": sorted(stored_fields - new_fields),
        },
        "conditions": {
            "stored_count": len(stored_ifs),
            "new_count": len(new_ifs),
            "added": sorted(new_ifs - stored_ifs),
            "removed": sorted(stored_ifs - new_ifs),
        },
        "loops": {
            "stored_count": len(stored_loops),
            "new_count": len(new_loops),
            "added": sorted(new_loops - stored_loops),
            "removed": sorted(stored_loops - new_loops),
        },
        "css_changed": sorted(stored_css) != sorted(new_css),
    }
    delta["score"] = _score_change(delta)
    delta["risk"] = _risk_label(delta["score"])
    return delta


def load_stored_index() -> dict:
    if not INDEX_PATH.exists():
        return {"templates": []}
    return json.loads(INDEX_PATH.read_text(encoding="utf-8"))


def build_stored_lookup(index: dict) -> tuple[dict, dict]:
    """Build {vitec_template_id: entry} and {normalized_title: entry} lookups."""
    by_id: dict[str, dict] = {}
    by_title: dict[str, dict] = {}

    for entry in index.get("templates", []):
        tid = entry.get("vitec_template_id")
        if tid:
            by_id[tid] = entry
        title = entry.get("title", "")
        if title:
            by_title[_normalize_title(title)] = entry

    return by_id, by_title


def _normalize_title(title: str) -> str:
    """Normalize title for fuzzy matching (lowercase, collapse whitespace, strip)."""
    t = title.lower().strip()
    t = re.sub(r"\s+", " ", t)
    return t


def _ascii_fold(text: str) -> str:
    return (text.lower()
            .replace("æ", "ae").replace("ø", "o").replace("å", "a")
            .replace("é", "e").replace("ü", "u"))


def match_to_stored(new_template: dict, by_id: dict, by_title: dict) -> dict | None:
    """Match a new export template to a stored index entry.

    Priority: ID match > exact title > ASCII-folded title.
    """
    tid = new_template.get("vitec_template_id") or new_template.get("id")
    if tid and tid in by_id:
        return by_id[tid]

    title = new_template.get("title", "")
    norm = _normalize_title(title)
    if norm in by_title:
        return by_title[norm]

    folded = _ascii_fold(norm)
    for stored_norm, entry in by_title.items():
        if _ascii_fold(stored_norm) == folded:
            return entry

    return None


def run_monthly_diff(
    new_templates: list[dict],
    *,
    changed_only: bool = False,
) -> dict:
    """Compare each template in the fresh export against the stored library.

    Returns structured results split into four categories:
        unchanged   — identical HTML content (or both lack content)
        changed     — HTML differs; each entry has a `delta` sub-dict
        new         — present in new export, not found in library
        removed     — present in library, not found in new export
    """
    stored_index = load_stored_index()
    by_id, by_title = build_stored_lookup(stored_index)

    # Track which stored IDs we matched (to detect removed templates)
    matched_stored_ids: set[str] = set()

    unchanged: list[dict] = []
    changed: list[dict] = []
    new_templates_list: list[dict] = []

    for tmpl in new_templates:
        tid = tmpl.get("vitec_template_id") or tmpl.get("id") or ""
        title = tmpl.get("title", "Untitled")
        new_content = _normalize_html(tmpl.get("content") or "")
        channel = tmpl.get("channel", "pdf_email")
        status = tmpl.get("status", "published")

        stored_entry = match_to_stored(tmpl, by_id, by_title)

        if stored_entry is None:
            new_templates_list.append({
                "vitec_template_id": tid,
                "title": title,
                "channel": channel,
                "status": status,
                "has_content": bool(new_content),
            })
            continue

        stored_id = stored_entry.get("vitec_template_id", "")
        if stored_id:
            matched_stored_ids.add(stored_id)

        stored_file = stored_entry.get("file")
        if not stored_file:
            # Stored entry exists but has no file — treat as new if we have content now
            if new_content:
                new_templates_list.append({
                    "vitec_template_id": tid,
                    "title": title,
                    "channel": channel,
                    "status": status,
                    "has_content": True,
                    "note": "Previously had no content in library",
                })
            continue

        stored_path = LIBRARY_DIR / stored_file
        if not stored_path.exists():
            new_templates_list.append({
                "vitec_template_id": tid,
                "title": title,
                "channel": channel,
                "status": status,
                "has_content": bool(new_content),
                "note": f"Stored file missing: {stored_file}",
            })
            continue

        stored_content = _normalize_html(read_file(stored_path))

        if not new_content:
            # Content disappeared upstream — flag as changed
            changed.append({
                "vitec_template_id": tid,
                "title": title,
                "channel": channel,
                "status": status,
                "stored_file": stored_file,
                "stored_entry": stored_entry,
                "delta": {
                    "identical": False,
                    "size_delta_bytes": -len(stored_content.encode()),
                    "size_stored_bytes": len(stored_content.encode()),
                    "size_new_bytes": 0,
                    "merge_fields": {"stored_count": 0, "new_count": 0, "added": [], "removed": []},
                    "conditions": {"stored_count": 0, "new_count": 0, "added": [], "removed": []},
                    "loops": {"stored_count": 0, "new_count": 0, "added": [], "removed": []},
                    "css_changed": False,
                    "score": 20,
                    "risk": "critical",
                    "note": "Content removed in new export",
                },
                "derivatives": stored_entry.get("derivatives", []),
            })
            continue

        delta = diff_template(stored_content, new_content)

        entry_data = {
            "vitec_template_id": tid,
            "title": title,
            "channel": channel,
            "status": status,
            "stored_file": stored_file,
            "stored_entry": stored_entry,
            "delta": delta,
            "derivatives": stored_entry.get("derivatives", []),
        }

        if delta["identical"]:
            if not changed_only:
                unchanged.append(entry_data)
        else:
            changed.append(entry_data)

    # Find removed: stored entries not matched by any new export template
    removed: list[dict] = []
    for entry in stored_index.get("templates", []):
        sid = entry.get("vitec_template_id", "")
        if sid and sid not in matched_stored_ids:
            removed.append({
                "vitec_template_id": sid,
                "title": entry.get("title", ""),
                "stored_file": entry.get("file", ""),
                "origin": entry.get("origin", ""),
                "derivatives": entry.get("derivatives", []),
            })

    # Sort changed by risk score descending (highest impact first)
    changed.sort(key=lambda x: x["delta"]["score"], reverse=True)

    # Knowledge base impact analysis
    all_new_fields: list[str] = []
    all_new_conds: list[str] = []
    all_new_loops: list[str] = []
    css_changed_count = 0
    critical_count = 0
    structural_count = 0
    for c in changed:
        d = c["delta"]
        all_new_fields.extend(d["merge_fields"]["added"])
        all_new_conds.extend(d["conditions"]["added"])
        all_new_loops.extend(d["loops"]["added"])
        if d["css_changed"]:
            css_changed_count += 1
        if d["risk"] == "critical":
            critical_count += 1
        elif d["risk"] == "structural":
            structural_count += 1

    return {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "stored_count": len(stored_index.get("templates", [])),
        "new_export_count": len(new_templates),
        "summary": {
            "unchanged": len(unchanged),
            "changed": len(changed),
            "new": len(new_templates_list),
            "removed": len(removed),
        },
        "risk_breakdown": {
            "critical": critical_count,
            "structural": structural_count,
            "cosmetic": sum(1 for c in changed if c["delta"]["risk"] == "cosmetic"),
            "trivial": sum(1 for c in changed if c["delta"]["risk"] == "trivial"),
        },
        "kb_impact": {
            "new_merge_fields": sorted(set(all_new_fields)),
            "new_conditions_count": len(set(all_new_conds)),
            "new_loops_count": len(set(all_new_loops)),
            "css_changes_count": css_changed_count,
            "patterns_md_update_needed": bool(all_new_fields or css_changed_count > 0 or all_new_loops),
            "lessons_md_update_needed": css_changed_count > 0 or critical_count > 0,
        },
        "changed": changed,
        "new": new_templates_list,
        "removed": removed,
        "unchanged_count": len(unchanged),
    }


# ---------------------------------------------------------------------------
# Report generation
# ---------------------------------------------------------------------------

def _fmt_list(items: list[str], max_show: int = 5) -> str:
    if not items:
        return "none"
    shown = [f"`{x}`" for x in items[:max_show]]
    if len(items) > max_show:
        shown.append(f"… +{len(items) - max_show} more")
    return ", ".join(shown)


def generate_monthly_report(results: dict, reason: str) -> str:
    now = results["generated_at"]
    s = results["summary"]
    risk = results["risk_breakdown"]
    kb = results["kb_impact"]

    lines = [
        "# Vitec Next Monthly Update — Diff Report",
        "",
        f"**Date**: {now}",
        f"**Trigger**: {reason}",
        f"**Stored templates**: {results['stored_count']}",
        f"**New export templates**: {results['new_export_count']}",
        "",
        "---",
        "",
        "## Executive Summary",
        "",
        f"| Category | Count |",
        f"|----------|-------|",
        f"| Changed  | **{s['changed']}** |",
        f"| New      | {s['new']} |",
        f"| Removed  | {s['removed']} |",
        f"| Unchanged | {s['unchanged']} |",
        "",
    ]

    if s["changed"] > 0:
        lines += [
            "### Risk Breakdown (Changed Templates)",
            "",
            f"| Risk | Count | Action |",
            f"|------|-------|--------|",
            f"| 🔴 Critical  | {risk['critical']} | Review HTML diff, check legal text |",
            f"| 🟠 Structural | {risk['structural']} | Review merge fields / conditions |",
            f"| 🟡 Cosmetic  | {risk['cosmetic']} | Accept or skip |",
            f"| ⚪ Trivial   | {risk['trivial']} | Accept (whitespace/encoding) |",
            "",
        ]

    if kb["patterns_md_update_needed"] or kb["lessons_md_update_needed"]:
        lines += [
            "### Knowledge Base Impact",
            "",
            f"- New merge fields: {_fmt_list(kb['new_merge_fields'])}",
            f"- Templates with CSS changes: {kb['css_changes_count']}",
            f"- New condition patterns: {kb['new_conditions_count']}",
            f"- New loop patterns: {kb['new_loops_count']}",
            f"- **PATTERNS.md update needed**: {'Yes' if kb['patterns_md_update_needed'] else 'No'}",
            f"- **LESSONS.md update needed**: {'Yes' if kb['lessons_md_update_needed'] else 'No'}",
            "",
        ]

    # New templates
    if results["new"]:
        lines += [
            "---",
            "",
            "## New Templates (not in library)",
            "",
            f"These {len(results['new'])} templates exist in Vitec Next but are not in `templates/master/`.",
            "Run `build_template_library.py` after deciding to add them.",
            "",
        ]
        for tmpl in results["new"]:
            note = f" — _{tmpl.get('note', '')}_" if tmpl.get("note") else ""
            lines.append(
                f"- **{tmpl['title']}** ({tmpl['channel']}, {tmpl['status']})"
                f" `{tmpl['vitec_template_id']}`{note}"
            )
        lines.append("")

    # Removed templates
    if results["removed"]:
        lines += [
            "---",
            "",
            "## Removed Templates (in library but not in export)",
            "",
            f"These {len(results['removed'])} templates are in the library but absent from the new export.",
            "They may have been deleted in Vitec Next or renamed.",
            "",
        ]
        for tmpl in results["removed"]:
            deriv_note = f" | Derivatives: {', '.join(tmpl['derivatives'])}" if tmpl.get("derivatives") else ""
            lines.append(
                f"- **{tmpl['title']}** ({tmpl['origin']}) `{tmpl['vitec_template_id']}`{deriv_note}"
            )
            if tmpl.get("stored_file"):
                lines.append(f"  - Stored at: `{tmpl['stored_file']}`")
        lines.append("")

    # Changed templates — detailed
    if results["changed"]:
        lines += [
            "---",
            "",
            "## Changed Templates",
            "",
            "Sorted by impact score (highest first). For each: decide **Accept**, **Skip**, or **Reconcile**.",
            "",
        ]

        for tmpl in results["changed"]:
            d = tmpl["delta"]
            risk_icon = {"critical": "🔴", "structural": "🟠", "cosmetic": "🟡", "trivial": "⚪"}.get(d["risk"], "")
            lines += [
                f"### {risk_icon} {tmpl['title']}",
                "",
                f"- **Risk**: {d['risk']} (score: {d['score']})",
                f"- **ID**: `{tmpl['vitec_template_id']}`",
                f"- **Channel**: {tmpl['channel']} | **Status**: {tmpl['status']}",
                f"- **Stored file**: `{tmpl['stored_file']}`",
                f"- **Size delta**: {d['size_delta_bytes']:+,} bytes "
                f"({d['size_stored_bytes']:,} → {d['size_new_bytes']:,})",
                f"- **CSS changed**: {'Yes' if d['css_changed'] else 'No'}",
            ]

            mf = d["merge_fields"]
            if mf["added"] or mf["removed"]:
                lines.append(f"- **Merge fields**: {mf['stored_count']} → {mf['new_count']}")
                if mf["added"]:
                    lines.append(f"  - Added: {_fmt_list(mf['added'])}")
                if mf["removed"]:
                    lines.append(f"  - Removed: {_fmt_list(mf['removed'])}")

            cond = d["conditions"]
            if cond["added"] or cond["removed"]:
                lines.append(f"- **Conditions**: {cond['stored_count']} → {cond['new_count']}")
                if cond["added"]:
                    lines.append(f"  - Added: {_fmt_list(cond['added'])}")
                if cond["removed"]:
                    lines.append(f"  - Removed: {_fmt_list(cond['removed'])}")

            loop = d["loops"]
            if loop["added"] or loop["removed"]:
                lines.append(f"- **Loops**: {loop['stored_count']} → {loop['new_count']}")
                if loop["added"]:
                    lines.append(f"  - Added: {_fmt_list(loop['added'])}")
                if loop["removed"]:
                    lines.append(f"  - Removed: {_fmt_list(loop['removed'])}")

            if d.get("note"):
                lines.append(f"- **Note**: _{d['note']}_")

            if tmpl.get("derivatives"):
                lines.append(f"- **Kundemal derivatives**: {', '.join(tmpl['derivatives'])}")

            lines += [
                "",
                "**Decision**: [ ] Accept &nbsp; [ ] Skip &nbsp; [ ] Reconcile",
                "",
            ]

    # Recommendations
    lines += [
        "---",
        "",
        "## Recommended Next Steps",
        "",
        "1. Review critical/structural changes above — read the actual HTML diff for each",
        "2. Make Accept/Skip/Reconcile decisions per template",
        "3. Run `build_template_library.py` with the new export to apply accepted updates",
        "4. Run `mine_template_library.py` to refresh knowledge base data",
        "5. If new merge fields or CSS patterns found, update PATTERNS.md / LESSONS.md",
        "6. Append sync entry to `.agents/skills/vitec-template-builder/CHANGELOG.md`",
        "",
    ]

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Content-level monthly diff: new Vitec export vs stored library",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Default (reads data/vitec-next-export.json or ~/Downloads/vitec-next-export.json)
  python scripts/tools/monthly_diff.py

  # Explicit input
  python scripts/tools/monthly_diff.py --input ~/Downloads/vitec-next-export.json

  # Only show what changed (skip unchanged in output)
  python scripts/tools/monthly_diff.py --changed-only

  # JSON output for agent consumption
  python scripts/tools/monthly_diff.py --json

  # Custom reason label in report
  python scripts/tools/monthly_diff.py --reason "February 2026 monthly update"
        """,
    )
    parser.add_argument(
        "--input", type=Path, default=None,
        help="Path to vitec-next-export.json (default: data/ or ~/Downloads/)",
    )
    parser.add_argument(
        "--reason", default="monthly update",
        help="Reason/label for this update cycle (appears in report header)",
    )
    parser.add_argument(
        "--changed-only", action="store_true",
        help="Omit unchanged templates from output (smaller report)",
    )
    parser.add_argument(
        "--output", "-o", type=Path, default=None,
        help="Write report to this path (default: qa_artifacts/MONTHLY-DIFF-{date}.md)",
    )
    parser.add_argument(
        "--json", action="store_true",
        help="Output structured JSON instead of the markdown report",
    )
    parser.add_argument(
        "--json-output", type=Path, default=None,
        help="Also write JSON to this path alongside the markdown report",
    )

    args = parser.parse_args()

    # Resolve input
    input_path = args.input
    if input_path is None:
        input_path = DEFAULT_INPUT if DEFAULT_INPUT.exists() else FALLBACK_INPUT
    if not input_path.exists():
        sys.exit(
            f"Export file not found: {input_path}\n"
            "Run a browser scrape first (see docs/vitec-next-mcp-scrape-and-import.md) "
            "or place the export at data/vitec-next-export.json"
        )

    print(f"Reading export: {input_path}", file=sys.stderr)
    export_data = json.loads(input_path.read_text(encoding="utf-8"))
    new_templates = export_data.get("templates", [])
    if not new_templates:
        sys.exit("No templates found in export file")

    print(f"Comparing {len(new_templates)} templates against stored library...", file=sys.stderr)
    results = run_monthly_diff(new_templates, changed_only=args.changed_only)

    s = results["summary"]
    print(
        f"\nDiff complete: {s['changed']} changed, {s['new']} new, "
        f"{s['removed']} removed, {s['unchanged']} unchanged",
        file=sys.stderr,
    )

    if args.json:
        # Strip stored_entry bulk from JSON output (not needed for agent)
        for item in results.get("changed", []):
            item.pop("stored_entry", None)
        print(json.dumps(results, indent=2, ensure_ascii=False, default=str))
        return

    report = generate_monthly_report(results, args.reason)

    # Write markdown report
    date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    if args.output:
        out_path = args.output
    else:
        QA_ARTIFACTS_DIR.mkdir(parents=True, exist_ok=True)
        out_path = QA_ARTIFACTS_DIR / f"MONTHLY-DIFF-{date_str}.md"

    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(report, encoding="utf-8")
    print(f"Report written: {out_path}", file=sys.stderr)

    # Optionally write JSON alongside
    if args.json_output:
        for item in results.get("changed", []):
            item.pop("stored_entry", None)
        args.json_output.write_text(
            json.dumps(results, indent=2, ensure_ascii=False, default=str),
            encoding="utf-8",
        )
        print(f"JSON written:   {args.json_output}", file=sys.stderr)


if __name__ == "__main__":
    main()
