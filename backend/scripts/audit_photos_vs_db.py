"""
Audit photos vs database employees.

Compares photos in a folder with employees in the database to find:
1. Photos without matching employees
2. Employees without photos
3. Duplicate photo entries (same email in multiple folders)

Usage:
    python scripts/audit_photos_vs_db.py
"""

import os
import re
from collections import defaultdict
from pathlib import Path

from sqlalchemy import create_engine, text

DATABASE_URL = os.environ.get(
    "DATABASE_URL", "postgresql://postgres:JBWPwgfKvuYllOspSIJFzjiVOycOWwiv@shuttle.proxy.rlwy.net:51557/railway"
)
PHOTOS_DIR = Path.home() / "Documents" / "ProaktivPhotos"

engine = create_engine(DATABASE_URL)


def extract_email_from_filename(filename: str) -> str | None:
    """Extract email from filename like 'email@domain.jpg' or 'email@domain_tld.jpg'."""
    # Remove extension
    name = Path(filename).stem

    # Handle both formats: email@domain.no and email@domain_no
    # Also handle .original suffix
    name = name.replace(".original", "")

    # Replace underscore with dot for domain (email@proaktiv_no -> email@proaktiv.no)
    if "_no" in name or "_com" in name:
        name = re.sub(r"_(\w+)$", r".\1", name)

    # Check if it looks like an email
    if "@" in name:
        return name.lower()

    return None


def scan_photos(photos_dir: Path) -> dict[str, list[Path]]:
    """Scan all photos and group by email."""
    email_to_paths: dict[str, list[Path]] = defaultdict(list)

    for path in photos_dir.rglob("*"):
        if path.is_file() and path.suffix.lower() in [".jpg", ".jpeg", ".png"]:
            email = extract_email_from_filename(path.name)
            if email:
                email_to_paths[email].append(path)

    return email_to_paths


def get_db_employees() -> dict[str, dict]:
    """Get all employees from database."""
    employees = {}

    with engine.connect() as conn:
        result = conn.execute(
            text("""
            SELECT id, first_name, last_name, email, profile_image_url, employee_type, status
            FROM employees
            ORDER BY email
        """)
        )

        for row in result:
            if row[3]:  # Has email
                employees[row[3].lower()] = {
                    "id": str(row[0]),
                    "name": f"{row[1]} {row[2]}",
                    "email": row[3],
                    "profile_image_url": row[4],
                    "employee_type": row[5],
                    "status": row[6],
                }

    return employees


def main():
    print("=" * 80)
    print("PHOTO vs DATABASE AUDIT")
    print("=" * 80)
    print(f"Photos directory: {PHOTOS_DIR}")
    print()

    # Scan photos
    print("Scanning photos...")
    email_to_paths = scan_photos(PHOTOS_DIR)
    print(f"Found {len(email_to_paths)} unique emails in photos")

    # Get DB employees
    print("Fetching employees from database...")
    db_employees = get_db_employees()
    print(f"Found {len(db_employees)} employees with email in database")
    print()

    # Find duplicates (same email in multiple folders)
    print("-" * 80)
    print("DUPLICATE PHOTOS (same email in multiple locations)")
    print("-" * 80)
    duplicates = {email: paths for email, paths in email_to_paths.items() if len(paths) > 1}

    if duplicates:
        for email, paths in sorted(duplicates.items()):
            print(f"\n{email}:")
            for p in paths:
                relative = p.relative_to(PHOTOS_DIR) if p.is_relative_to(PHOTOS_DIR) else p
                print(f"  - {relative}")
        print(f"\nTotal: {len(duplicates)} emails with duplicates")
    else:
        print("No duplicates found.")
    print()

    # Find photos without DB employees
    print("-" * 80)
    print("PHOTOS WITHOUT MATCHING EMPLOYEES (orphaned photos)")
    print("-" * 80)
    orphaned_photos = set(email_to_paths.keys()) - set(db_employees.keys())

    if orphaned_photos:
        for email in sorted(orphaned_photos):
            paths = email_to_paths[email]
            print(f"  {email}")
        print(f"\nTotal: {len(orphaned_photos)} photos without DB employee")
    else:
        print("All photos have matching employees.")
    print()

    # Find employees without photos (in any folder)
    print("-" * 80)
    print("EMPLOYEES WITHOUT ANY PHOTOS")
    print("-" * 80)
    employees_without_photos = set(db_employees.keys()) - set(email_to_paths.keys())

    if employees_without_photos:
        for email in sorted(employees_without_photos):
            emp = db_employees[email]
            print(f"  {email} ({emp['name']}) [{emp['employee_type']}]")
        print(f"\nTotal: {len(employees_without_photos)} employees without any photos in folder")
    else:
        print("All employees have photos in the folder.")
    print()

    # Find employees without WebDAV photo URL set
    print("-" * 80)
    print("EMPLOYEES WITHOUT WebDAV PROFILE_IMAGE_URL")
    print("-" * 80)
    no_webdav_url = {
        email: emp
        for email, emp in db_employees.items()
        if not emp["profile_image_url"] or "proaktiv.no" not in str(emp["profile_image_url"])
    }

    if no_webdav_url:
        for email, emp in sorted(no_webdav_url.items()):
            current_url = emp["profile_image_url"] or "(none)"
            # Check if we have a photo for this employee
            has_photo = "Y" if email in email_to_paths else "N"
            print(f"  [{has_photo}] {email} ({emp['name']}) - {current_url[:50]}...")
        print(f"\nTotal: {len(no_webdav_url)} employees without WebDAV URL")
        print("Legend: [Y] = photo exists in folder, [N] = no photo found")
    else:
        print("All employees have WebDAV profile URLs.")
    print()

    # Summary
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print(f"Unique photo emails:           {len(email_to_paths)}")
    print(f"Database employees:            {len(db_employees)}")
    print(f"Duplicate photo entries:       {len(duplicates)}")
    print(f"Photos without DB match:       {len(orphaned_photos)}")
    print(f"Employees without any photo:   {len(employees_without_photos)}")
    print(f"Employees without WebDAV URL:  {len(no_webdav_url)}")
    print("=" * 80)


if __name__ == "__main__":
    main()
