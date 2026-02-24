"""
Template Version Manager — creates snapshots and manages version history.

Stores versioned copies of templates before edits for rollback support
and audit trails. Each version is saved to templates/versions/{template_id}/.

Usage:
    python template_version.py snapshot <template_file> [--reason "Pre-edit backup"]
    python template_version.py list <template_id>
    python template_version.py restore <version_file> <target_file>
    python template_version.py diff <template_id> [--latest]
"""

import argparse
import json
import os
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

TEMPLATES_ROOT = Path(__file__).resolve().parent.parent.parent / "templates"
VERSIONS_DIR = TEMPLATES_ROOT / "versions"
INDEX_PATH = TEMPLATES_ROOT / "index.json"


def load_index() -> dict:
    with open(INDEX_PATH, encoding="utf-8") as f:
        return json.load(f)


def find_template_by_file(file_path: str) -> dict | None:
    """Find a template entry in index.json by its file path."""
    index = load_index()
    abs_path = Path(file_path).resolve()

    try:
        rel_path = str(abs_path.relative_to(TEMPLATES_ROOT.resolve())).replace("\\", "/")
    except ValueError:
        rel_path = str(Path(file_path)).replace("\\", "/")
        if rel_path.startswith("templates/"):
            rel_path = rel_path[len("templates/"):]

    for t in index["templates"]:
        if t["file"] == rel_path or t.get("category_file") == rel_path:
            return t
    return None


def find_template_by_id(template_id: str) -> dict | None:
    """Find a template entry by its Vitec template ID."""
    index = load_index()
    for t in index["templates"]:
        if t["vitec_template_id"] == template_id:
            return t
    return None


def create_snapshot(
    template_path: str,
    reason: str = "Pre-edit backup",
    template_id: str | None = None,
) -> str:
    """
    Create a versioned snapshot of a template file.
    Returns the path to the snapshot file.
    """
    template_file = Path(template_path)
    if not template_file.exists():
        raise FileNotFoundError(f"Template not found: {template_path}")

    if not template_id:
        tmpl = find_template_by_file(template_path)
        if tmpl:
            template_id = tmpl["vitec_template_id"]
        else:
            template_id = template_file.stem

    version_dir = VERSIONS_DIR / template_id
    version_dir.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    snapshot_name = f"{timestamp}.html"
    snapshot_path = version_dir / snapshot_name

    shutil.copy2(template_file, snapshot_path)

    manifest_path = version_dir / "manifest.json"
    manifest = []
    if manifest_path.exists():
        with open(manifest_path, encoding="utf-8") as f:
            manifest = json.load(f)

    manifest.append({
        "version": snapshot_name,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "reason": reason,
        "source_file": str(template_file),
        "size_bytes": template_file.stat().st_size,
    })

    with open(manifest_path, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2, ensure_ascii=False)

    return str(snapshot_path)


def list_versions(template_id: str) -> list[dict]:
    """List all version snapshots for a template."""
    version_dir = VERSIONS_DIR / template_id
    manifest_path = version_dir / "manifest.json"

    if not manifest_path.exists():
        return []

    with open(manifest_path, encoding="utf-8") as f:
        return json.load(f)


def restore_version(version_file: str, target_file: str) -> None:
    """Restore a version snapshot to the target location (creates a backup first)."""
    version_path = Path(version_file)
    target_path = Path(target_file)

    if not version_path.exists():
        raise FileNotFoundError(f"Version file not found: {version_file}")

    if target_path.exists():
        create_snapshot(target_file, reason="Pre-restore backup")

    shutil.copy2(version_path, target_path)


def get_latest_version(template_id: str) -> str | None:
    """Get the path to the most recent version snapshot."""
    versions = list_versions(template_id)
    if not versions:
        return None

    latest = versions[-1]
    return str(VERSIONS_DIR / template_id / latest["version"])


def main():
    parser = argparse.ArgumentParser(
        description="Manage template version history",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    snap = subparsers.add_parser("snapshot", help="Create a version snapshot")
    snap.add_argument("template_file", help="Path to the template HTML file")
    snap.add_argument("--reason", default="Pre-edit backup", help="Reason for snapshot")
    snap.add_argument("--id", dest="template_id", help="Override template ID")

    ls = subparsers.add_parser("list", help="List version snapshots")
    ls.add_argument("template_id", help="Vitec template ID")

    rest = subparsers.add_parser("restore", help="Restore a version snapshot")
    rest.add_argument("version_file", help="Path to the version snapshot file")
    rest.add_argument("target_file", help="Path to restore to")

    diff_cmd = subparsers.add_parser("diff", help="Show diff between latest version and current")
    diff_cmd.add_argument("template_id", help="Vitec template ID")
    diff_cmd.add_argument("--latest", action="store_true", help="Compare with latest snapshot")

    args = parser.parse_args()

    if args.command == "snapshot":
        try:
            path = create_snapshot(args.template_file, args.reason, args.template_id)
            print(f"Snapshot created: {path}")
        except FileNotFoundError as e:
            print(f"ERROR: {e}", file=sys.stderr)
            sys.exit(1)

    elif args.command == "list":
        versions = list_versions(args.template_id)
        if not versions:
            print(f"No versions found for template {args.template_id}")
            sys.exit(1)

        print(f"Versions for {args.template_id} ({len(versions)} snapshots):\n")
        for v in versions:
            print(f"  {v['version']}")
            print(f"    Timestamp: {v['timestamp']}")
            print(f"    Reason: {v['reason']}")
            print(f"    Size: {v['size_bytes']:,} bytes")
            print()

    elif args.command == "restore":
        try:
            restore_version(args.version_file, args.target_file)
            print(f"Restored {args.version_file} -> {args.target_file}")
        except FileNotFoundError as e:
            print(f"ERROR: {e}", file=sys.stderr)
            sys.exit(1)

    elif args.command == "diff":
        tmpl = find_template_by_id(args.template_id)
        if not tmpl:
            print(f"ERROR: Template not found: {args.template_id}", file=sys.stderr)
            sys.exit(1)

        latest = get_latest_version(args.template_id)
        if not latest:
            print(f"No versions found for template {args.template_id}")
            sys.exit(1)

        current_path = str(TEMPLATES_ROOT / tmpl["file"])
        print(f"Run diff manually:")
        print(f"  python scripts/tools/template_diff.py \"{latest}\" \"{current_path}\"")


if __name__ == "__main__":
    main()
