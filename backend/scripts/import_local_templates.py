"""
Import templates from local library/ folder to Railway PostgreSQL database.

Usage:
    python scripts/import_local_templates.py --api-url https://proaktiv-dokument-hub-production.up.railway.app

This script reads HTML templates from the library/ folder and imports them
to the database via the admin API endpoint.
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Any

import requests


def get_category_from_path(file_path: Path, library_root: Path) -> str:
    """Extract category from file path relative to library root."""
    relative = file_path.relative_to(library_root)
    parts = relative.parts

    if len(parts) > 1:
        return parts[0]  # First folder is category
    return "Uncategorized"


def get_channel_from_filename(filename: str) -> str:
    """Determine channel (PDF, Email, SMS) from filename."""
    lower = filename.lower()
    if "sms" in lower or filename.endswith(".txt"):
        return "SMS"
    elif "email" in lower or "e-post" in lower or "epost" in lower:
        return "Email"
    return "PDF"


def parse_meta_file(meta_path: Path) -> dict[str, Any]:
    """Parse a .meta.json file if it exists."""
    if meta_path.exists():
        try:
            with open(meta_path, encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            print(f"  [WARN] Could not parse {meta_path}: {e}")
    return {}


def read_file_content(file_path: Path) -> str | None:
    """Read file content with fallback encodings."""
    for encoding in ["utf-8", "utf-8-sig", "latin-1", "cp1252"]:
        try:
            with open(file_path, encoding=encoding) as f:
                return f.read()
        except UnicodeDecodeError:
            continue
    return None


def collect_templates(library_path: Path) -> list[dict[str, Any]]:
    """Collect all templates from the library folder."""
    templates = []

    # Find all HTML files
    html_files = list(library_path.rglob("*.html"))

    for html_file in html_files:
        # Skip system files
        if "System" in str(html_file) and not html_file.name.startswith("Vitec"):
            continue

        # Skip if it's a copy/backup
        if "-copy" in html_file.name.lower():
            continue

        content = read_file_content(html_file)
        if not content:
            print(f"  [WARN] Could not read: {html_file}")
            continue

        # Check for meta file
        meta_path = html_file.with_suffix(".meta.json")
        meta = parse_meta_file(meta_path)

        # Extract metadata
        category = get_category_from_path(html_file, library_path)
        channel = meta.get("channel", get_channel_from_filename(html_file.name))
        title = meta.get("title", html_file.stem.replace("_", " ").replace("-", " "))

        template_data = {
            "title": title,
            "file_name": html_file.name,
            "file_type": "html",
            "file_size_bytes": len(content.encode("utf-8")),
            "status": "published",
            "channel": channel,
            "template_type": category,
            "content": content,
            "created_by": "import@proaktiv.no",
            "updated_by": "import@proaktiv.no",
            "description": meta.get("description", f"Imported from {category}/{html_file.name}"),
        }

        # Add optional fields from meta
        if "phases" in meta:
            template_data["phases"] = meta["phases"]
        if "receiver_types" in meta:
            template_data["receiver_types"] = meta["receiver_types"]
        if "departments" in meta:
            template_data["departments"] = meta["departments"]

        templates.append(template_data)

    return templates


def import_templates(api_url: str, templates: list[dict[str, Any]], dry_run: bool = False) -> None:
    """Import templates to the API using the multipart upload endpoint."""

    if dry_run:
        print(f"\n[DRY RUN] Would import {len(templates)} templates:")
        for t in templates:
            print(f"  - {t['title']} ({t['channel']}, {t['template_type']})")
        return

    # Use the standard template upload endpoint
    endpoint = f"{api_url.rstrip('/')}/api/templates"

    print(f"\n[INFO] Importing {len(templates)} templates to {endpoint}...")

    success_count = 0
    error_count = 0

    for template in templates:
        try:
            # Create file-like object from content
            content = template["content"].encode("utf-8")
            files = {"file": (template["file_name"], content, "text/html")}
            data = {
                "title": template["title"],
                "description": template.get("description", ""),
                "status": "published",
                "auto_sanitize": "false",  # Don't sanitize imports
            }

            response = requests.post(endpoint, files=files, data=data, timeout=30)

            if response.status_code == 201:
                success_count += 1
                print(f"  [OK] {template['title']}")
            else:
                error_count += 1
                print(f"  [FAIL] {template['title']}: {response.status_code} - {response.text[:100]}")

        except requests.exceptions.RequestException as e:
            error_count += 1
            print(f"  [FAIL] {template['title']}: {e}")

    print(f"\n[RESULT] Imported {success_count}/{len(templates)} templates ({error_count} errors)")


def main():
    parser = argparse.ArgumentParser(description="Import templates from library folder to database")
    parser.add_argument(
        "--api-url", required=True, help="API base URL (e.g., https://proaktiv-dokument-hub-production.up.railway.app)"
    )
    parser.add_argument("--library-path", default="library", help="Path to library folder")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be imported without actually importing")

    args = parser.parse_args()

    library_path = Path(args.library_path)
    if not library_path.exists():
        print(f"[ERROR] Library path not found: {library_path}")
        sys.exit(1)

    print(f"[INFO] Scanning {library_path}...")
    templates = collect_templates(library_path)
    print(f"[INFO] Found {len(templates)} templates")

    if not templates:
        print("[WARN] No templates found to import")
        sys.exit(0)

    import_templates(args.api_url, templates, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
