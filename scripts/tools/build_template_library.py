#!/usr/bin/env python3
"""
Build a git-tracked master template library from a Vitec Next export.

Reads vitec-next-export.json and writes individual HTML files organized
by origin (vitec-system / kundemal) and by category, plus an index.json
for agent consumption.

Usage:
    python scripts/tools/build_template_library.py
    python scripts/tools/build_template_library.py --input data/vitec-next-export.json
    python scripts/tools/build_template_library.py --input ~/Downloads/vitec-next-export.json --dry-run
"""

import argparse
import json
import re
import shutil
from collections import Counter, defaultdict
from datetime import UTC, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_INPUT = REPO_ROOT / "data" / "vitec-next-export.json"
FALLBACK_INPUT = Path.home() / "Downloads" / "vitec-next-export.json"
LIBRARY_DIR = REPO_ROOT / "templates"


def _safe_filename(title: str, ext: str = ".html") -> str:
    """Convert a template title to a safe, readable filename."""
    name = title.strip()
    name = re.sub(r"[<>:\"/\\|?*]", "", name)
    name = re.sub(r"\s+", "_", name)
    name = re.sub(r"[^\w\-_.()æøåÆØÅ]", "", name)
    name = name.strip("_. ")
    if not name:
        name = "unnamed"
    if len(name) > 120:
        name = name[:120]
    return name + ext


def _safe_dirname(name: str) -> str:
    """Convert a category name to a safe directory name."""
    dirname = name.strip().lower()
    dirname = re.sub(r"[<>:\"/\\|?*]", "", dirname)
    dirname = re.sub(r"\s+", "-", dirname)
    dirname = re.sub(r"[^\w\-æøåÆØÅ]", "", dirname)
    dirname = dirname.strip("-_ ")
    return dirname or "ukategorisert"


def _determine_origin(template: dict) -> str:
    tags = [t.lower() for t in template.get("tags", [])]
    if any("vitec" in t for t in tags):
        return "vitec-system"
    return "kundemal"


def _get_category(template: dict) -> str:
    cats = template.get("categories", [])
    if cats and isinstance(cats[0], dict):
        return cats[0].get("name", "Ukategorisert") or "Ukategorisert"
    return "Ukategorisert"


def build_library(
    templates: list[dict],
    output_dir: Path,
    *,
    dry_run: bool = False,
) -> dict:
    stats = {
        "total": len(templates),
        "with_content": 0,
        "without_content": 0,
        "by_origin": Counter(),
        "by_channel": Counter(),
        "by_category": Counter(),
        "files_written": 0,
    }

    index_entries = []
    used_filenames: dict[str, int] = defaultdict(int)

    if not dry_run and output_dir.exists():
        for subdir in ("master", "by-category"):
            target = output_dir / subdir
            if target.exists():
                shutil.rmtree(target)

    for template in templates:
        tid = template.get("vitec_template_id", "unknown")
        title = template.get("title", "Untitled")
        content = (template.get("content") or "").strip()
        channel = template.get("channel", "pdf_email")
        status = template.get("status", "published")
        origin = _determine_origin(template)
        category = _get_category(template)

        stats["by_origin"][origin] += 1
        stats["by_channel"][channel] += 1
        stats["by_category"][category] += 1

        # Normalize CRLF from Vitec's Windows server before writing to disk.
        # Without this, Python text mode on Windows double-converts \r\n → \r\r\n,
        # which reads back as \n\n (extra blank lines in stored files).
        content = content.replace("\r\n", "\n").replace("\r", "\n")

        if not content:
            stats["without_content"] += 1
            index_entries.append({
                "vitec_template_id": tid,
                "title": title,
                "channel": channel,
                "status": status,
                "origin": origin,
                "category": category,
                "has_content": False,
                "file": None,
                "category_file": None,
            })
            continue

        stats["with_content"] += 1

        base_name = _safe_filename(title)
        used_filenames[base_name] += 1
        if used_filenames[base_name] > 1:
            stem = base_name.rsplit(".", 1)[0]
            base_name = f"{stem}_{used_filenames[base_name]}.html"

        master_rel = f"master/{origin}/{base_name}"
        cat_dir_name = _safe_dirname(category)
        category_rel = f"by-category/{cat_dir_name}/{base_name}"

        index_entries.append({
            "vitec_template_id": tid,
            "title": title,
            "channel": channel,
            "status": status,
            "origin": origin,
            "category": category,
            "has_content": True,
            "file": master_rel,
            "category_file": category_rel,
        })

        if dry_run:
            continue

        master_path = output_dir / master_rel
        master_path.parent.mkdir(parents=True, exist_ok=True)
        master_path.write_text(content, encoding="utf-8")
        stats["files_written"] += 1

        cat_path = output_dir / category_rel
        cat_path.parent.mkdir(parents=True, exist_ok=True)
        cat_path.write_text(content, encoding="utf-8")

    if not dry_run:
        index_path = output_dir / "index.json"
        index_data = {
            "generated_at": datetime.now(UTC).isoformat(),
            "total_templates": stats["total"],
            "with_content": stats["with_content"],
            "without_content": stats["without_content"],
            "origins": dict(stats["by_origin"]),
            "channels": dict(stats["by_channel"]),
            "categories": dict(stats["by_category"]),
            "templates": index_entries,
        }
        index_path.write_text(
            json.dumps(index_data, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

        _write_readme(output_dir, stats, index_entries)

    return stats


def _write_readme(output_dir: Path, stats: dict, entries: list[dict]) -> None:
    lines = [
        "# Vitec Next Master Template Library",
        "",
        "Auto-generated from `vitec-next-export.json`.",
        "Re-generate with: `python scripts/tools/build_template_library.py`",
        "",
        "## Stats",
        "",
        f"- **Total templates:** {stats['total']}",
        f"- **With HTML content:** {stats['with_content']}",
        f"- **Without content:** {stats['without_content']}",
        "",
        "### By Origin",
        "",
    ]
    for origin, count in sorted(stats["by_origin"].items()):
        lines.append(f"- {origin}: {count}")

    lines += ["", "### By Channel", ""]
    for channel, count in sorted(stats["by_channel"].items()):
        lines.append(f"- {channel}: {count}")

    lines += ["", "### By Category", ""]
    for cat, count in sorted(stats["by_category"].items()):
        lines.append(f"- {cat}: {count}")

    lines += [
        "",
        "## Structure",
        "",
        "```",
        "templates/",
        "  master/              # All templates by origin",
        "    vitec-system/      # Vitec standard templates",
        "    kundemal/          # Custom (Proaktiv) templates",
        "  by-category/         # Same templates grouped by Vitec category",
        "    kontrakt/",
        "    oppdragsavtale/",
        "    ...",
        "  index.json           # Machine-readable index",
        "  README.md            # This file",
        "```",
        "",
        "## Template Index",
        "",
        "| Title | Origin | Channel | Category | Status |",
        "|-------|--------|---------|----------|--------|",
    ]

    for entry in sorted(entries, key=lambda e: (e["category"], e["title"])):
        content_mark = "x" if entry["has_content"] else "-"
        lines.append(
            f"| {entry['title'][:60]} | {entry['origin']} | "
            f"{entry['channel']} | {entry['category']} | "
            f"{entry['status']} ({content_mark}) |"
        )

    lines.append("")
    readme_path = output_dir / "README.md"
    readme_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Build master template library from Vitec export")
    parser.add_argument(
        "--input", type=Path, default=None,
        help=f"Vitec export JSON (default: {DEFAULT_INPUT} or {FALLBACK_INPUT})",
    )
    parser.add_argument("--output", type=Path, default=LIBRARY_DIR, help="Output directory")
    parser.add_argument("--dry-run", action="store_true", help="Print stats without writing files")
    args = parser.parse_args()

    input_path = args.input
    if input_path is None:
        input_path = DEFAULT_INPUT if DEFAULT_INPUT.exists() else FALLBACK_INPUT
    if not input_path.exists():
        raise SystemExit(f"Input not found: {input_path}")

    print(f"Reading: {input_path}")
    export_data = json.loads(input_path.read_text(encoding="utf-8"))
    templates = export_data.get("templates", [])

    if not templates:
        raise SystemExit("No templates found in export file")

    prefix = "[DRY RUN] " if args.dry_run else ""
    print(f"{prefix}Building library from {len(templates)} templates...")

    stats = build_library(templates, args.output, dry_run=args.dry_run)

    print(f"\n{prefix}Results:")
    print(f"  Total: {stats['total']}")
    print(f"  With content: {stats['with_content']}")
    print(f"  Without content: {stats['without_content']}")
    print(f"  Files written: {stats['files_written']}")
    print(f"\n  By origin: {dict(stats['by_origin'])}")
    print(f"  By channel: {dict(stats['by_channel'])}")

    if not args.dry_run:
        print(f"\nLibrary: {args.output}")
        print(f"Index:   {args.output / 'index.json'}")


if __name__ == "__main__":
    main()
