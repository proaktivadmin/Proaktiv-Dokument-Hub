"""
Vitec Sync Check — compares stored templates against Vitec Next production.

Three modes:

TARGETED (primary — newsletter/hotfix triggered):
    python vitec_sync_check.py --templates "Kjopekontrakt FORBRUKER" "Oppdragsavtale" \
        --reason "March 2026 newsletter"

FULL SCAN (fallback — compare index dates):
    python vitec_sync_check.py --full-scan --index-file vitec_current_index.json

COMPARE (single template diff):
    python vitec_sync_check.py --compare fetched.html \
        --stored templates/master/vitec-system/Template.html --reason "hotfix"

Reports are written to scripts/qa_artifacts/SYNC-REPORT-{date}.md.

Derivative tracking convention:
    System template entries in templates/index.json may include a "derivatives" field
    that lists kundemal copies based on that system template. Example:
        { "title": "Kjopekontrakt FORBRUKER", "origin": "vitec-system",
          "derivatives": ["Kjopekontrakt_Bruktbolig"] }
    The sync check uses this field to flag kundemal templates that may need updating
    when their upstream system template changes.
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent.parent
TEMPLATES_ROOT = PROJECT_ROOT / "templates"
INDEX_PATH = TEMPLATES_ROOT / "index.json"
QA_ARTIFACTS_DIR = PROJECT_ROOT / "scripts" / "qa_artifacts"

sys.path.insert(0, str(SCRIPT_DIR))
from template_diff import analyze_structural_changes, generate_report  # noqa: E402


def load_index(path: Path | None = None) -> dict:
    p = path or INDEX_PATH
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def read_file(path: str | Path) -> str:
    with open(path, encoding="utf-8") as f:
        return f.read()


def _ascii_fold(text: str) -> str:
    """Fold Norwegian characters to ASCII for loose matching."""
    return (text.lower()
            .replace("æ", "ae").replace("ø", "o").replace("å", "a")
            .replace("é", "e").replace("ü", "u"))


def find_templates_by_names(index: dict, names: list[str]) -> list[tuple[str, dict | None]]:
    """Match requested names to index entries. Returns (query, match_or_None) pairs."""
    results = []
    for name in names:
        name_lower = name.lower().strip()
        match = None
        # Pass 1: exact substring (case-insensitive)
        for t in index["templates"]:
            if name_lower in t["title"].lower():
                match = t
                break
        # Pass 2: ASCII-folded substring (handles ø→o, æ→ae, å→a)
        if not match:
            name_folded = _ascii_fold(name)
            for t in index["templates"]:
                if name_folded in _ascii_fold(t["title"]):
                    match = t
                    break
        # Pass 3: alphanumeric-only comparison
        if not match:
            name_norm = re.sub(r"[^a-z0-9]", "", _ascii_fold(name))
            for t in index["templates"]:
                title_norm = re.sub(r"[^a-z0-9]", "", _ascii_fold(t["title"]))
                if name_norm in title_norm or title_norm in name_norm:
                    match = t
                    break
        results.append((name, match))
    return results


def find_derivatives(index: dict, template_entry: dict) -> list[dict]:
    """Find kundemal derivatives listed in a system template's 'derivatives' field."""
    derivative_names = template_entry.get("derivatives", [])
    if not derivative_names:
        return []
    found = []
    for dname in derivative_names:
        dname_lower = dname.lower()
        for t in index["templates"]:
            if t.get("origin") == "kundemal" and dname_lower in t["title"].lower():
                found.append(t)
                break
    return found


def detect_css_changes(before: str, after: str) -> bool:
    """Check whether <style> blocks differ between the two templates."""
    style_re = re.compile(r"<style[^>]*>(.*?)</style>", re.DOTALL | re.IGNORECASE)
    before_styles = sorted(style_re.findall(before))
    after_styles = sorted(style_re.findall(after))
    return before_styles != after_styles


def detect_new_merge_fields(before: str, after: str) -> list[str]:
    field_re = re.compile(r"\[\[[\*]?([^\]]+)\]\]")
    before_fields = set(field_re.findall(before))
    after_fields = set(field_re.findall(after))
    return sorted(after_fields - before_fields)


def detect_new_conditions(before: str, after: str) -> list[str]:
    cond_re = re.compile(r'vitec-if="([^"]*)"')
    before_conds = set(cond_re.findall(before))
    after_conds = set(cond_re.findall(after))
    return sorted(after_conds - before_conds)


# ---------------------------------------------------------------------------
# COMPARE mode
# ---------------------------------------------------------------------------

def run_compare(fetched_path: str, stored_path: str, reason: str) -> dict:
    """Compare a single fetched HTML against its stored version."""
    fetched_html = read_file(fetched_path)
    stored_html = read_file(stored_path)

    analysis = analyze_structural_changes(stored_html, fetched_html)
    css_changed = detect_css_changes(stored_html, fetched_html)
    new_fields = detect_new_merge_fields(stored_html, fetched_html)
    new_conds = detect_new_conditions(stored_html, fetched_html)
    is_identical = stored_html.strip() == fetched_html.strip()

    return {
        "stored_path": stored_path,
        "fetched_path": fetched_path,
        "reason": reason,
        "identical": is_identical,
        "css_changed": css_changed,
        "new_merge_fields": new_fields,
        "new_conditions": new_conds,
        "analysis": analysis,
        "diff_report": None if is_identical else generate_report(
            stored_path, fetched_path, stored_html, fetched_html, analysis
        ),
    }


# ---------------------------------------------------------------------------
# TARGETED mode
# ---------------------------------------------------------------------------

def run_targeted(template_names: list[str], reason: str) -> dict:
    """Find stored templates by name and prepare the local side for sync.

    The actual fetching from Vitec Next happens via browser in the agent command —
    this function handles the LOCAL side: finding stored templates, checking for
    derivatives, and producing a pre-diff report.
    """
    index = load_index()
    matches = find_templates_by_names(index, template_names)

    found = []
    not_found = []
    for query, entry in matches:
        if entry:
            stored_path = TEMPLATES_ROOT / entry["file"]
            derivatives = find_derivatives(index, entry)
            found.append({
                "query": query,
                "entry": entry,
                "stored_path": str(stored_path),
                "stored_exists": stored_path.exists(),
                "derivatives": [
                    {"title": d["title"], "file": d["file"]}
                    for d in derivatives
                ],
            })
        else:
            not_found.append(query)

    return {
        "reason": reason,
        "requested": template_names,
        "found": found,
        "not_found": not_found,
    }


# ---------------------------------------------------------------------------
# FULL SCAN mode
# ---------------------------------------------------------------------------

def run_full_scan(vitec_index_path: str) -> dict:
    """Compare a freshly-exported Vitec index against the stored index.

    The vitec index file should be a JSON export with a 'templates' array,
    each entry having at least 'vitec_template_id' and 'title'.
    """
    stored_index = load_index()
    vitec_index = load_index(Path(vitec_index_path))

    stored_by_id = {t["vitec_template_id"]: t for t in stored_index["templates"]}
    vitec_by_id = {}
    for t in vitec_index.get("templates", []):
        tid = t.get("vitec_template_id") or t.get("id")
        if tid:
            vitec_by_id[tid] = t

    changed = []
    new_templates = []
    unchanged = []
    removed = []

    for tid, vt in vitec_by_id.items():
        if tid in stored_by_id:
            st = stored_by_id[tid]
            v_title = (vt.get("title") or vt.get("name") or "").strip()
            s_title = st.get("title", "").strip()
            title_changed = v_title.lower() != s_title.lower()
            status_changed = vt.get("status") != st.get("status")

            if title_changed or status_changed:
                changed.append({
                    "vitec_template_id": tid,
                    "stored_title": s_title,
                    "vitec_title": v_title,
                    "title_changed": title_changed,
                    "status_changed": status_changed,
                    "stored_file": st.get("file"),
                })
            else:
                unchanged.append(tid)
        else:
            new_templates.append({
                "vitec_template_id": tid,
                "title": (vt.get("title") or vt.get("name") or "").strip(),
                "channel": vt.get("channel", "unknown"),
                "status": vt.get("status", "unknown"),
            })

    for tid, st in stored_by_id.items():
        if tid not in vitec_by_id:
            removed.append({
                "vitec_template_id": tid,
                "title": st.get("title", ""),
                "file": st.get("file", ""),
            })

    return {
        "stored_count": len(stored_by_id),
        "vitec_count": len(vitec_by_id),
        "changed": changed,
        "new_templates": new_templates,
        "unchanged_count": len(unchanged),
        "removed": removed,
    }


# ---------------------------------------------------------------------------
# Report generation
# ---------------------------------------------------------------------------

def generate_sync_report(
    mode: str,
    reason: str,
    data: dict,
    compare_results: list[dict] | None = None,
) -> str:
    """Build the full SYNC-REPORT markdown."""
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    lines = [
        "# Vitec Sync Report",
        "",
        f"**Date**: {now}",
        f"**Trigger**: {reason}",
        f"**Mode**: {mode}",
        "",
    ]

    if mode == "targeted":
        lines.append("## Summary")
        lines.append("")
        lines.append(f"- Templates requested: {len(data['requested'])}")
        lines.append(f"- Found in library: {len(data['found'])}")
        lines.append(f"- Not found: {len(data['not_found'])}")
        lines.append("")

        if data["not_found"]:
            lines.append("### Not Found")
            lines.append("")
            for q in data["not_found"]:
                lines.append(f"- `{q}` — not matched in index.json")
            lines.append("")

        lines.append("### Templates to Check")
        lines.append("")
        for item in data["found"]:
            entry = item["entry"]
            lines.append(f"#### {entry['title']}")
            lines.append("")
            lines.append(f"- **ID**: `{entry['vitec_template_id']}`")
            lines.append(f"- **Origin**: {entry.get('origin', 'N/A')}")
            lines.append(f"- **Category**: {entry.get('category', 'N/A')}")
            lines.append(f"- **Stored file**: `{entry['file']}`")
            lines.append(f"- **File exists**: {'Yes' if item['stored_exists'] else 'NO — MISSING'}")
            if item["derivatives"]:
                lines.append(f"- **Kundemal derivatives**: {len(item['derivatives'])}")
                for d in item["derivatives"]:
                    lines.append(f"  - `{d['title']}` → `{d['file']}`")
            lines.append("")

    elif mode == "full-scan":
        lines.append("## Summary")
        lines.append("")
        lines.append(f"- Stored templates: {data['stored_count']}")
        lines.append(f"- Vitec templates: {data['vitec_count']}")
        lines.append(f"- Changed (metadata): {len(data['changed'])}")
        lines.append(f"- New (not in library): {len(data['new_templates'])}")
        lines.append(f"- Unchanged: {data['unchanged_count']}")
        lines.append(f"- Removed from Vitec: {len(data['removed'])}")
        lines.append("")

        if data["changed"]:
            lines.append("### Changed Templates")
            lines.append("")
            for c in data["changed"]:
                lines.append(f"- **{c['stored_title']}**")
                lines.append(f"  - ID: `{c['vitec_template_id']}`")
                if c["title_changed"]:
                    lines.append(f"  - Title changed → `{c['vitec_title']}`")
                if c["status_changed"]:
                    lines.append("  - Status changed")
                lines.append(f"  - File: `{c.get('stored_file', 'N/A')}`")
            lines.append("")

        if data["new_templates"]:
            lines.append("### New Templates (not in library)")
            lines.append("")
            for n in data["new_templates"]:
                lines.append(f"- **{n['title']}** — {n['channel']} — {n['status']}")
                lines.append(f"  - ID: `{n['vitec_template_id']}`")
            lines.append("")

        if data["removed"]:
            lines.append("### Removed from Vitec")
            lines.append("")
            for r in data["removed"]:
                lines.append(f"- **{r['title']}** — `{r['file']}`")
            lines.append("")

    if compare_results:
        changed_results = [r for r in compare_results if not r["identical"]]
        unchanged_results = [r for r in compare_results if r["identical"]]

        lines.append("## Comparison Results")
        lines.append("")
        lines.append(f"- Checked: {len(compare_results)}")
        lines.append(f"- Changed: {len(changed_results)}")
        lines.append(f"- Unchanged: {len(unchanged_results)}")
        lines.append("")

        if changed_results:
            lines.append("### Changed Templates")
            lines.append("")
            for r in changed_results:
                lines.append(f"#### {Path(r['stored_path']).name}")
                lines.append("")
                lines.append(f"- **Stored**: `{r['stored_path']}`")
                lines.append(f"- **CSS changes**: {'Yes' if r['css_changed'] else 'No'}")
                if r["new_merge_fields"]:
                    lines.append(f"- **New merge fields**: {', '.join(f'`[[{f}]]`' for f in r['new_merge_fields'])}")
                if r["new_conditions"]:
                    lines.append(f"- **New conditions**: {', '.join(f'`{c}`' for c in r['new_conditions'])}")
                a = r["analysis"]
                lines.append(f"- **Size delta**: {a['size']['delta_bytes']:+,} bytes")
                mf = a["merge_fields"]
                lines.append(f"- **Merge fields**: {mf['before_count']} → {mf['after_count']} "
                             f"(+{len(mf['added'])}, -{len(mf['removed'])})")
                lines.append(f"- **Action**: Review diff and accept/skip/reconcile")
                lines.append("")

        if unchanged_results:
            lines.append("### Unchanged Templates")
            lines.append("")
            for r in unchanged_results:
                lines.append(f"- `{Path(r['stored_path']).name}` — identical")
            lines.append("")

    # Knowledge base impact section
    if compare_results:
        any_css = any(r["css_changed"] for r in compare_results if not r["identical"])
        all_new_fields = []
        all_new_conds = []
        for r in compare_results:
            all_new_fields.extend(r["new_merge_fields"])
            all_new_conds.extend(r["new_conditions"])

        lines.append("## Knowledge Base Impact")
        lines.append("")
        lines.append(f"- CSS patterns changed: {'Yes' if any_css else 'No'}")
        lines.append(f"- New merge fields: {len(all_new_fields)} ({', '.join(f'`{f}`' for f in all_new_fields) if all_new_fields else 'none'})")
        lines.append(f"- New conditional patterns: {len(all_new_conds)} ({', '.join(f'`{c}`' for c in all_new_conds) if all_new_conds else 'none'})")
        lines.append(f"- PATTERNS.md update needed: {'Yes' if any_css or all_new_fields or all_new_conds else 'No'}")
        lines.append(f"- LESSONS.md update needed: {'Yes' if any_css else 'No'}")
        lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Compare stored templates against Vitec Next production",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Targeted check after newsletter
  python vitec_sync_check.py --templates "Kjopekontrakt FORBRUKER" "Oppdragsavtale" \\
      --reason "March 2026 newsletter"

  # Full scan against fresh export
  python vitec_sync_check.py --full-scan --index-file vitec_current_index.json

  # Single template compare
  python vitec_sync_check.py --compare fetched.html \\
      --stored templates/master/vitec-system/Template.html --reason "hotfix"
        """,
    )

    mode_group = parser.add_mutually_exclusive_group(required=True)
    mode_group.add_argument(
        "--templates", nargs="+", metavar="NAME",
        help="Template names/titles to check (targeted mode)",
    )
    mode_group.add_argument(
        "--full-scan", action="store_true",
        help="Compare full index against Vitec export (full scan mode)",
    )
    mode_group.add_argument(
        "--compare", metavar="FETCHED_HTML",
        help="Path to fetched HTML file (compare mode)",
    )

    parser.add_argument("--reason", default="manual check", help="Reason for the sync check")
    parser.add_argument("--index-file", help="Path to freshly-exported Vitec index JSON (full scan mode)")
    parser.add_argument("--stored", help="Path to stored HTML file (compare mode)")
    parser.add_argument("--output", "-o", help="Write report to file (default: auto-generated path)")
    parser.add_argument("--json", action="store_true", help="Output structured JSON instead of markdown")

    args = parser.parse_args()

    if args.full_scan and not args.index_file:
        parser.error("--full-scan requires --index-file")
    if args.compare and not args.stored:
        parser.error("--compare requires --stored")

    compare_results = None

    if args.templates:
        mode = "targeted"
        data = run_targeted(args.templates, args.reason)
    elif args.full_scan:
        mode = "full-scan"
        data = run_full_scan(args.index_file)
    else:
        mode = "compare"
        result = run_compare(args.compare, args.stored, args.reason)
        data = {"reason": args.reason}
        compare_results = [result]

    if args.json:
        output_data = {"mode": mode, "data": data}
        if compare_results:
            for r in compare_results:
                r.pop("diff_report", None)
            output_data["compare_results"] = compare_results
        print(json.dumps(output_data, indent=2, ensure_ascii=False, default=str))
        return

    report = generate_sync_report(mode, args.reason, data, compare_results)

    if args.output:
        out_path = Path(args.output)
    else:
        date_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        out_path = QA_ARTIFACTS_DIR / f"SYNC-REPORT-{date_str}.md"

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"Sync report written to: {out_path}")


if __name__ == "__main__":
    main()
