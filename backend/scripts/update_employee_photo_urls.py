"""
Update employee profile_image_url from Vitec API paths to WebDAV hosted URLs.

This script reads the manifest from the photo scraper and updates the database
to point to the WebDAV-hosted copies instead of proxying through Vitec API.

Usage:
    python scripts/update_employee_photo_urls.py [--dry-run] [--manifest PATH]

Examples:
    python scripts/update_employee_photo_urls.py --dry-run
    python scripts/update_employee_photo_urls.py --manifest C:\\Users\\Adrian\\Documents\\ProaktivPhotos\\homepage-webdav\\manifest.json
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text

from app.config import settings

# Default manifest location
DEFAULT_MANIFEST = Path.home() / "Documents" / "ProaktivPhotos" / "homepage-webdav" / "manifest.json"


def update_photo_urls(manifest_path: Path, dry_run: bool = False) -> None:
    """Update employee photo URLs from manifest."""
    if not manifest_path.exists():
        print(f"[ERROR] Manifest not found: {manifest_path}")
        print("Run the photo scraper first to generate the manifest.")
        return

    with open(manifest_path, encoding="utf-8") as f:
        manifest = json.load(f)

    employees = manifest.get("employees", [])
    print("\n" + "=" * 70)
    print("UPDATE EMPLOYEE PHOTO URLs")
    print("=" * 70)
    print(f"Mode: {'DRY RUN (no changes)' if dry_run else 'LIVE (applying changes)'}")
    print(f"Manifest: {manifest_path}")
    print(f"Employees in manifest: {len(employees)}")
    print("-" * 70)

    engine = create_engine(settings.DATABASE_URL)

    updated_count = 0
    skipped_count = 0
    not_found_count = 0
    missing_url_count = 0

    with engine.connect() as conn:
        for emp in employees:
            email = emp.get("email")
            public_url = emp.get("public_url")
            download_status = emp.get("download_status")

            if not email:
                continue

            # Skip employees without a valid photo URL
            if not public_url or download_status in ("missing_image_url", "missing_filename", "failed"):
                missing_url_count += 1
                continue

            # Only process successfully downloaded photos
            if download_status not in ("success", "dry-run", "copied"):
                skipped_count += 1
                continue

            # Find employee in database
            result = conn.execute(
                text(
                    """
                    SELECT id, first_name, last_name, profile_image_url
                    FROM employees
                    WHERE email = :email AND status = 'active'
                    """
                ),
                {"email": email},
            )
            row = result.fetchone()

            if not row:
                not_found_count += 1
                continue

            emp_id, first_name, last_name, current_url = row
            emp_name = f"{first_name} {last_name}"

            # Check if already pointing to WebDAV
            if current_url == public_url:
                print(f"[OK] {emp_name} - already using WebDAV URL")
                skipped_count += 1
                continue

            # Check if currently using Vitec API
            is_vitec_url = current_url and "/api/vitec" in current_url

            print(f"\n[UPDATE] {emp_name} ({email})")
            if is_vitec_url:
                print("         Vitec API -> WebDAV")
            else:
                print(f"         {current_url[:40] if current_url else 'None'}... -> WebDAV")
            print(f"         New URL: {public_url}")

            if not dry_run:
                conn.execute(
                    text("UPDATE employees SET profile_image_url = :url WHERE id = :emp_id"),
                    {"url": public_url, "emp_id": str(emp_id)},
                )

            updated_count += 1

        if not dry_run:
            conn.commit()
            print("\n" + "-" * 70)
            print("Changes committed to database")

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Updated:        {updated_count}")
    print(f"Already OK:     {skipped_count}")
    print(f"Not in DB:      {not_found_count}")
    print(f"Missing photo:  {missing_url_count}")
    print("=" * 70)


def main():
    parser = argparse.ArgumentParser(description="Update employee photo URLs to WebDAV")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without applying them",
    )
    parser.add_argument(
        "--manifest",
        type=Path,
        default=DEFAULT_MANIFEST,
        help=f"Path to manifest.json (default: {DEFAULT_MANIFEST})",
    )
    args = parser.parse_args()

    update_photo_urls(args.manifest, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
