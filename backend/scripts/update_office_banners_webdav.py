"""
Update office banner_image_url to use WebDAV hosted photos.

The new URL pattern is:
    https://proaktiv.no/photos/offices/{office_slug}.jpg

Where office_slug is the office name converted to:
    - lowercase
    - spaces and special chars replaced with hyphens
    - Norwegian chars converted (æ->ae, ø->o, å->a)
    - multiple hyphens collapsed to single
    - leading/trailing hyphens removed

Example:
    "Proaktiv Drammen Lier Holmestrand" -> proaktiv-drammen-lier-holmestrand.jpg

Usage:
    python scripts/update_office_banners_webdav.py --dry-run    # Preview changes
    python scripts/update_office_banners_webdav.py              # Apply changes
    python scripts/update_office_banners_webdav.py --filter "Drammen"  # Update matching offices
"""

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text

from app.config import settings

# WebDAV base URL for office banners
WEBDAV_BANNER_BASE = "https://proaktiv.no/photos/offices/"

# Norwegian character replacements
NORWEGIAN_CHARS = {
    "æ": "ae",
    "ø": "o",
    "å": "a",
    "Æ": "ae",
    "Ø": "o",
    "Å": "a",
}

# Offices to skip (non-location offices that don't have banners)
SKIP_OFFICES = {
    "aktiv oppgjør as",
    "kjedeledelse",
    "proaktiv gruppen as",
    "proaktiv kjedeledelse",
    "proaktiv properties",
    "test office",
}


def slugify(name: str) -> str:
    """
    Convert office name to URL-friendly slug.

    Example:
        "Proaktiv Eiendomsmegling Jæren" -> "proaktiv-eiendomsmegling-jaeren"
        "Proaktiv Drammen Lier Holmestrand" -> "proaktiv-drammen-lier-holmestrand"
    """
    # Lowercase
    slug = name.lower()

    # Replace Norwegian characters
    for char, replacement in NORWEGIAN_CHARS.items():
        slug = slug.replace(char, replacement)

    # Replace non-alphanumeric with hyphens
    slug = re.sub(r"[^a-z0-9]+", "-", slug)

    # Collapse multiple hyphens
    slug = re.sub(r"-+", "-", slug)

    # Remove leading/trailing hyphens
    slug = slug.strip("-")

    return slug


def office_to_webdav_url(name: str) -> str:
    """Convert office name to full WebDAV banner URL."""
    slug = slugify(name)
    if not slug:
        return ""
    return f"{WEBDAV_BANNER_BASE}{slug}.jpg"


def update_banner_urls(
    dry_run: bool = False,
    filter_name: str | None = None,
    force: bool = False,
    include_all: bool = False,
) -> None:
    """Update office banner URLs to WebDAV pattern."""
    print("\n" + "=" * 70)
    print("UPDATE OFFICE BANNER URLs TO WEBDAV")
    print("=" * 70)
    print(f"Mode: {'DRY RUN (no changes)' if dry_run else 'LIVE (applying changes)'}")
    print(f"Base URL: {WEBDAV_BANNER_BASE}")
    if filter_name:
        print(f"Filter: {filter_name}")
    if force:
        print("Force: Updating even if already set")
    if include_all:
        print("Include all: Processing non-location offices too")
    print("-" * 70)

    engine = create_engine(settings.DATABASE_URL)

    updated_count = 0
    skipped_count = 0
    excluded_count = 0

    with engine.connect() as conn:
        # Get all offices
        query = "SELECT id, name, banner_image_url FROM offices ORDER BY name"
        result = conn.execute(text(query))
        offices = result.fetchall()

        print(f"Found {len(offices)} offices")
        print("-" * 70)

        for row in offices:
            office_id, name, current_url = row

            # Apply filter if specified
            if filter_name and filter_name.lower() not in name.lower():
                continue

            # Skip non-location offices unless include_all
            if not include_all and name.lower() in SKIP_OFFICES:
                excluded_count += 1
                print(f"[SKIP] {name} (non-location office)")
                continue

            # Generate new WebDAV URL
            new_url = office_to_webdav_url(name)

            if not new_url:
                excluded_count += 1
                continue

            # Skip if already using this URL (unless force)
            if current_url == new_url and not force:
                skipped_count += 1
                continue

            # Check if URL is different
            url_changed = current_url != new_url

            if url_changed:
                print(f"\n[UPDATE] {name}")
                if current_url:
                    display_url = current_url[:50] + "..." if len(current_url) > 50 else current_url
                    print(f"         From: {display_url}")
                else:
                    print("         From: (none)")
                print(f"         To:   {new_url}")

                if not dry_run:
                    conn.execute(
                        text("UPDATE offices SET banner_image_url = :url WHERE id = :office_id"),
                        {"url": new_url, "office_id": str(office_id)},
                    )

            updated_count += 1

        if not dry_run and updated_count > 0:
            conn.commit()
            print("\n" + "-" * 70)
            print("Changes committed to database")

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Updated:      {updated_count}")
    print(f"Already OK:   {skipped_count}")
    print(f"Excluded:     {excluded_count}")
    print("=" * 70)

    if dry_run:
        print("\n[INFO] This was a dry run. No changes were made.")
        print("[INFO] Run without --dry-run to apply changes.")


def main():
    parser = argparse.ArgumentParser(description="Update office banner URLs to WebDAV")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without applying them",
    )
    parser.add_argument(
        "--filter",
        type=str,
        dest="filter_name",
        help="Only update offices matching this name (case-insensitive)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Update even if URL is already set",
    )
    parser.add_argument(
        "--include-all",
        action="store_true",
        help="Include non-location offices (Kjedeledelse, Gruppen, etc.)",
    )
    args = parser.parse_args()

    update_banner_urls(
        dry_run=args.dry_run,
        filter_name=args.filter_name,
        force=args.force,
        include_all=args.include_all,
    )


if __name__ == "__main__":
    main()
