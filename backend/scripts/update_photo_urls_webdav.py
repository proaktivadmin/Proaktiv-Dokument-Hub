"""
Update employee profile_image_url to use WebDAV hosted photos.

The new URL pattern is:
    https://proaktiv.no/photos/employees/{email_encoded}.jpg

Where email_encoded converts:
    example@proaktiv.no -> example@proaktiv_no.jpg
    (@ stays as @, . in domain becomes _)

Usage:
    python scripts/update_photo_urls_webdav.py --dry-run    # Preview changes
    python scripts/update_photo_urls_webdav.py              # Apply changes
    python scripts/update_photo_urls_webdav.py --filter ca@proaktiv.no  # Update specific employee
"""

import argparse
import sys
from pathlib import Path
from urllib.parse import quote

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text

from app.config import settings

# WebDAV base URL for employee photos
WEBDAV_PHOTO_BASE = "https://proaktiv.no/photos/employees/"


def email_to_filename(email: str) -> str:
    """
    Convert email to filename format.

    example@proaktiv.no -> example@proaktiv_no.jpg

    The @ symbol stays, but the . in the domain becomes _
    """
    if not email or "@" not in email:
        return ""

    local, domain = email.rsplit("@", 1)
    # Replace . with _ in domain part
    domain_encoded = domain.replace(".", "_")
    return f"{local}@{domain_encoded}.jpg"


def email_to_webdav_url(email: str) -> str:
    """Convert email to full WebDAV URL."""
    filename = email_to_filename(email)
    if not filename:
        return ""
    # URL encode the filename (@ becomes %40)
    encoded_filename = quote(filename, safe="")
    return f"{WEBDAV_PHOTO_BASE}{encoded_filename}"


def update_photo_urls(
    dry_run: bool = False,
    filter_email: str | None = None,
    force: bool = False,
) -> None:
    """Update employee photo URLs to WebDAV pattern."""
    print("\n" + "=" * 70)
    print("UPDATE EMPLOYEE PHOTO URLs TO WEBDAV")
    print("=" * 70)
    print(f"Mode: {'DRY RUN (no changes)' if dry_run else 'LIVE (applying changes)'}")
    print(f"Base URL: {WEBDAV_PHOTO_BASE}")
    if filter_email:
        print(f"Filter: {filter_email}")
    if force:
        print("Force: Updating even if already set")
    print("-" * 70)

    engine = create_engine(settings.DATABASE_URL)

    updated_count = 0
    skipped_count = 0
    no_email_count = 0

    with engine.connect() as conn:
        # Get all active employees
        query = """
            SELECT id, email, first_name, last_name, profile_image_url
            FROM employees
            WHERE status = 'active'
        """
        if filter_email:
            query += " AND LOWER(email) = LOWER(:email)"
            result = conn.execute(text(query), {"email": filter_email})
        else:
            result = conn.execute(text(query))

        employees = result.fetchall()
        print(f"Found {len(employees)} active employees")
        print("-" * 70)

        for row in employees:
            emp_id, email, first_name, last_name, current_url = row
            emp_name = f"{first_name} {last_name}"

            if not email:
                no_email_count += 1
                continue

            # Generate new WebDAV URL
            new_url = email_to_webdav_url(email)

            # Skip if already using this URL (unless force)
            if current_url == new_url and not force:
                skipped_count += 1
                continue

            # Check if current URL is different
            url_changed = current_url != new_url

            if url_changed:
                print(f"\n[UPDATE] {emp_name} ({email})")
                if current_url:
                    # Truncate long URLs for display
                    display_url = current_url[:50] + "..." if len(current_url) > 50 else current_url
                    print(f"         From: {display_url}")
                else:
                    print("         From: (none)")
                print(f"         To:   {new_url}")

                if not dry_run:
                    conn.execute(
                        text("UPDATE employees SET profile_image_url = :url WHERE id = :emp_id"),
                        {"url": new_url, "emp_id": str(emp_id)},
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
    print(f"No email:     {no_email_count}")
    print("=" * 70)

    if dry_run:
        print("\n[INFO] This was a dry run. No files were modified.")
        print("[INFO] Run without --dry-run to apply changes.")


def main():
    parser = argparse.ArgumentParser(description="Update employee photo URLs to WebDAV")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without applying them",
    )
    parser.add_argument(
        "--filter",
        type=str,
        dest="filter_email",
        help="Only update specific employee by email",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Update even if URL is already set",
    )
    args = parser.parse_args()

    update_photo_urls(
        dry_run=args.dry_run,
        filter_email=args.filter_email,
        force=args.force,
    )


if __name__ == "__main__":
    main()
