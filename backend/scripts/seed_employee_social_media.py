"""
Seed script to populate social media URLs for employees.

Updates facebook_url, instagram_url, and linkedin_url for specific employees.

Usage:
    python scripts/seed_employee_social_media.py [--dry-run]

Examples:
    python scripts/seed_employee_social_media.py --dry-run  # Preview changes
    python scripts/seed_employee_social_media.py            # Apply changes
"""

import argparse
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text

from app.config import settings

# =============================================================================
# EMPLOYEE SOCIAL MEDIA MAPPINGS
# =============================================================================
# Format: "email": {
#     "facebook_url": "...",
#     "instagram_url": "...",
#     "linkedin_url": "...",
# }
#
# Match by email address (unique identifier).
# Only include employees who have shared their social media profiles.
# =============================================================================

EMPLOYEE_SOCIAL_DATA: dict[str, dict[str, str | None]] = {
    # Caroline Ringså Ask - Proaktiv Briskeby
    "cr@proaktiv.no": {
        "facebook_url": None,
        "instagram_url": "https://www.instagram.com/meglercarolineringsaask/",
        "linkedin_url": "https://www.linkedin.com/in/caroline-rings%C3%A5-ask-3b3a84398/",
    },
    # Christer A. Pedersen - uses "realestatebycap"
    "cap@proaktiv.no": {
        "facebook_url": None,
        "instagram_url": "https://www.instagram.com/realestatebycap/",
        "linkedin_url": None,
    },
    # Ken Martin Wigand
    "kmw@proaktiv.no": {
        "facebook_url": None,
        "instagram_url": "https://www.instagram.com/kenmartinwigand/",
        "linkedin_url": None,
    },
    # Christina Pedersen
    "cp@proaktiv.no": {
        "facebook_url": None,
        "instagram_url": "https://www.instagram.com/chriped/",
        "linkedin_url": "https://www.linkedin.com/in/christina-pedersen-46a007b9/",
    },
    # Ida-Amalie Larsen
    "ial@proaktiv.no": {
        "facebook_url": None,
        "instagram_url": "https://www.instagram.com/megleridaamalie/",
        "linkedin_url": "https://www.linkedin.com/in/ida-amalie-larsen-76a429236/",
    },
    # Andrea Birkeland
    "ab@proaktiv.no": {
        "facebook_url": None,
        "instagram_url": "https://www.instagram.com/meglerandreabirkeland/",
        "linkedin_url": None,
    },
    # Zuzanna Muszkiet
    "zuzanna@proaktiv.no": {
        "facebook_url": None,
        "instagram_url": "https://www.instagram.com/meglerzuzanna/",
        "linkedin_url": None,
    },
    # Bjarne Edland
    "edland@proaktiv.no": {
        "facebook_url": "https://www.facebook.com/MeglerBjarneEdland/",
        "instagram_url": None,
        "linkedin_url": None,
    },
    # Thea Langeland Solheim
    "tls@proaktiv.no": {
        "facebook_url": None,
        "instagram_url": None,
        "linkedin_url": "https://www.linkedin.com/in/thea-langeland-solheim-b3944b236/",
    },
    # Kristian Bjørnstad Hansen
    "kbh@proaktiv.no": {
        "facebook_url": None,
        "instagram_url": None,
        "linkedin_url": "https://www.linkedin.com/in/kristian-bj%C3%B8rnstad-hansen-2207821b6/",
    },
    # Camilla Krokeide (both emails)
    "camilla.krokeide@proaktiv.no": {
        "facebook_url": None,
        "instagram_url": None,
        "linkedin_url": "https://www.linkedin.com/in/camilla-krokeide-abb93156/",
    },
    "camilla@proaktiv.no": {
        "facebook_url": None,
        "instagram_url": None,
        "linkedin_url": "https://www.linkedin.com/in/camilla-krokeide-abb93156/",
    },
    # Vibeke Stavenes
    "vs@proaktiv.no": {
        "facebook_url": None,
        "instagram_url": None,
        "linkedin_url": "https://www.linkedin.com/in/vibeke-stavenes-88621a39/",
    },
    # Eirik Døsen
    "ed@proaktiv.no": {
        "facebook_url": None,
        "instagram_url": None,
        "linkedin_url": "https://www.linkedin.com/in/eirik-d%C3%B8sen-ab22ba27/",
    },
    # Kjersti Tunestveit Dyre
    "ktd@proaktiv.no": {
        "facebook_url": None,
        "instagram_url": None,
        "linkedin_url": "https://www.linkedin.com/in/kjersti-dyre-0716191b/",
    },
}


def seed_employee_social_media(dry_run: bool = False) -> None:
    """Seed social media URLs for employees."""
    engine = create_engine(settings.DATABASE_URL)

    updated_count = 0
    skipped_count = 0
    not_found_count = 0

    print("\n" + "=" * 70)
    print("EMPLOYEE SOCIAL MEDIA SEEDING")
    print("=" * 70)
    print(f"Mode: {'DRY RUN (no changes)' if dry_run else 'LIVE (applying changes)'}")
    print(f"Employees to update: {len(EMPLOYEE_SOCIAL_DATA)}")
    print("-" * 70)

    with engine.connect() as conn:
        for email, social_data in EMPLOYEE_SOCIAL_DATA.items():
            # Find employee by email
            result = conn.execute(
                text(
                    """
                    SELECT id, first_name, last_name, facebook_url, instagram_url, linkedin_url
                    FROM employees
                    WHERE email = :email AND status = 'active'
                    """
                ),
                {"email": email},
            )
            row = result.fetchone()

            if not row:
                print(f"\n[!] {email}")
                print("    Employee not found in database")
                not_found_count += 1
                continue

            emp_id, first_name, last_name, current_fb, current_ig, current_li = row
            emp_name = f"{first_name} {last_name}"

            changes = []
            updates = {}

            current_values = {
                "facebook_url": current_fb,
                "instagram_url": current_ig,
                "linkedin_url": current_li,
            }

            for field in ["facebook_url", "instagram_url", "linkedin_url"]:
                new_value = social_data.get(field)
                current_value = current_values[field]

                if new_value is not None and current_value != new_value:
                    short_current = (
                        (current_value[:35] + "...") if current_value and len(current_value) > 35 else current_value
                    )
                    short_new = (new_value[:35] + "...") if len(new_value) > 35 else new_value
                    changes.append(f"{field}: '{short_current}' -> '{short_new}'")
                    updates[field] = new_value

            if changes:
                print(f"\n[UPDATE] {emp_name} ({email})")
                for change in changes:
                    print(f"         {change}")
                updated_count += 1

                if not dry_run and updates:
                    set_clauses = ", ".join(f"{k} = :{k}" for k in updates.keys())
                    updates["emp_id"] = str(emp_id)
                    conn.execute(
                        text(f"UPDATE employees SET {set_clauses} WHERE id = :emp_id"),
                        updates,
                    )
            else:
                print(f"\n[OK] {emp_name} ({email}) - already up to date")
                skipped_count += 1

        if not dry_run:
            conn.commit()
            print("\n" + "-" * 70)
            print("Changes committed to database")

    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)
    print(f"Updated:      {updated_count}")
    print(f"No changes:   {skipped_count}")
    print(f"Not found:    {not_found_count}")
    print("=" * 70)


def main():
    parser = argparse.ArgumentParser(description="Seed social media URLs for employees")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without applying them",
    )
    args = parser.parse_args()

    seed_employee_social_media(dry_run=args.dry_run)


if __name__ == "__main__":
    main()
