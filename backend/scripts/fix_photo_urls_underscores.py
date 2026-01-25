"""
Fix all photo URLs to use underscores instead of dots.

Updates profile_image_url for all employees to use the underscore format:
- alexander.abelseth@proaktiv.no -> alexander_abelseth@proaktiv_no

Usage:
    python scripts/fix_photo_urls_underscores.py --dry-run   # Preview
    python scripts/fix_photo_urls_underscores.py             # Apply
"""

import os
import sys

from sqlalchemy import create_engine, text

DATABASE_URL = os.environ.get(
    "DATABASE_URL", "postgresql://postgres:JBWPwgfKvuYllOspSIJFzjiVOycOWwiv@shuttle.proxy.rlwy.net:51557/railway"
)

engine = create_engine(DATABASE_URL)

DRY_RUN = "--dry-run" in sys.argv


def email_to_photo_filename(email: str) -> str:
    """Convert email to WebDAV photo filename format."""
    if not email:
        return None

    # Replace dots with underscores, keeping the @ symbol
    # e.g., alexander.abelseth@proaktiv.no -> alexander_abelseth@proaktiv_no
    name = email.lower().replace(".", "_")

    # URL encode the @ symbol
    name = name.replace("@", "%40")

    return f"https://proaktiv.no/photos/employees/{name}.jpg"


def main():
    print("=" * 70)
    print("FIX PHOTO URLs TO USE UNDERSCORES")
    print("=" * 70)
    print(f"Mode: {'DRY RUN' if DRY_RUN else 'LIVE'}")
    print()

    with engine.connect() as conn:
        # Get all employees with their current photo URLs
        result = conn.execute(
            text("""
            SELECT id, first_name, last_name, email, profile_image_url
            FROM employees
            WHERE email IS NOT NULL
            ORDER BY email
        """)
        )

        employees = list(result)
        print(f"Found {len(employees)} employees with email\n")

        updated_count = 0
        skipped_count = 0

        for row in employees:
            emp_id, first_name, last_name, email, current_url = row

            new_url = email_to_photo_filename(email)

            if current_url == new_url:
                skipped_count += 1
                continue

            print(f"UPDATE: {first_name} {last_name} ({email})")
            print(f"  OLD: {current_url}")
            print(f"  NEW: {new_url}")
            print()

            if not DRY_RUN:
                conn.execute(
                    text("""
                    UPDATE employees SET profile_image_url = :url WHERE id = :id
                """),
                    {"id": emp_id, "url": new_url},
                )

            updated_count += 1

        if not DRY_RUN:
            conn.commit()

        print("=" * 70)
        print(f"Updated: {updated_count}")
        print(f"Skipped: {skipped_count} (already correct)")
        print("=" * 70)

        if DRY_RUN:
            print("\nDRY RUN: No changes made. Run without --dry-run to apply.")


if __name__ == "__main__":
    main()
