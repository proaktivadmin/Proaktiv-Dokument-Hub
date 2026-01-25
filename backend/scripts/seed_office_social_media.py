"""
Seed script to populate social media URLs for offices.

Updates facebook_url, instagram_url, and linkedin_url for each office.

Usage:
    python scripts/seed_office_social_media.py [--dry-run]

Examples:
    python scripts/seed_office_social_media.py --dry-run  # Preview changes
    python scripts/seed_office_social_media.py            # Apply changes
"""

import argparse
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text

from app.config import settings

# =============================================================================
# OFFICE SOCIAL MEDIA MAPPINGS
# =============================================================================
# Format: "Office Name": {
#     "facebook_url": "...",
#     "instagram_url": "...",
#     "linkedin_url": "...",
# }
#
# Note: Some offices share the company-wide accounts (Proaktiv Gruppen).
# If an office doesn't have its own social media, leave the field as None
# to inherit company defaults in the signature template.
# =============================================================================

# Company-wide defaults (used as fallback for offices without their own accounts)
COMPANY_DEFAULTS = {
    "facebook_url": "https://www.facebook.com/proaktiveiendom",
    "instagram_url": "https://www.instagram.com/proaktiveiendomsmegling/",
    "linkedin_url": "https://no.linkedin.com/company/proaktiv-eiendomsmegling",
}

# Standard social media data for each office
# Keys can have multiple name variants (local DB vs production DB naming)
_SOCIAL_DATA = {
    # Haugesund
    "haugesund": {
        "facebook_url": "https://www.facebook.com/Proaktivhaugesund/",
        "instagram_url": "https://www.instagram.com/proaktivhaugesund/",
        "linkedin_url": None,
    },
    # Sandnes
    "sandnes": {
        "facebook_url": "https://www.facebook.com/Proaktiv-Eiendomsmegling-Sandnes/",
        "instagram_url": "https://www.instagram.com/proaktivsandnes/",
        "linkedin_url": None,
    },
    # Stavanger
    "stavanger": {
        "facebook_url": "https://www.facebook.com/ProaktivStavanger",
        "instagram_url": "https://www.instagram.com/proaktivstavanger/",
        "linkedin_url": None,
    },
    # Bergen Sentrum (Småstrandgaten)
    "bergen_sentrum": {
        "facebook_url": "https://www.facebook.com/proaktivbergensentrum",
        "instagram_url": "https://www.instagram.com/proaktivbergensentrum/",
        "linkedin_url": None,
    },
    # Drammen, Lier & Holmestrand
    "drammen": {
        "facebook_url": "https://www.facebook.com/profile.php?id=100095470026479",
        "instagram_url": "https://www.instagram.com/proaktivdrammenoglier",
        "linkedin_url": None,
    },
    # Jæren
    "jaeren": {
        "facebook_url": "https://www.facebook.com/profile.php?id=61575762700836",
        "instagram_url": "https://www.instagram.com/proaktivjaeren/",
        "linkedin_url": None,
    },
    # Sola
    "sola": {
        "facebook_url": "https://www.facebook.com/profile.php?id=61574069210559",
        "instagram_url": "https://www.instagram.com/proaktivsola/",
        "linkedin_url": None,
    },
    # Kristiansand
    "kristiansand": {
        "facebook_url": "https://www.facebook.com/profile.php?id=61586269120163",
        "instagram_url": None,
        "linkedin_url": None,
    },
    # Briskeby / Properties (Oslo)
    "briskeby": {
        "facebook_url": "https://www.facebook.com/proaktivbriskeby",
        "instagram_url": "https://www.instagram.com/proaktivproperties/",
        "linkedin_url": None,
    },
    # Skien
    "skien": {
        "facebook_url": "https://www.facebook.com/profile.php?id=61581094785903",
        "instagram_url": "https://www.instagram.com/proaktivskien/",
        "linkedin_url": None,
    },
    # Sarpsborg
    "sarpsborg": {
        "facebook_url": "https://www.facebook.com/meglerhusetborg",
        "instagram_url": "https://www.instagram.com/proaktivsarpsborg/",
        "linkedin_url": None,
    },
    # Trondheim Sentrum
    "trondheim_sentrum": {
        "facebook_url": "https://www.facebook.com/ProaEiendomsmeglingTrondheim",
        "instagram_url": "https://www.instagram.com/proaktivtrondheim/",
        "linkedin_url": None,
    },
    # Trondheim Øst / Moholt
    "trondheim_ost": {
        "facebook_url": None,
        "instagram_url": "https://www.instagram.com/proaktivmoholt/",
        "linkedin_url": None,
    },
    # Trondheim Syd / Heimdal
    "trondheim_syd": {
        "facebook_url": None,
        "instagram_url": "https://www.instagram.com/proaktivheimdal/",
        "linkedin_url": None,
    },
    # Voss
    "voss": {
        "facebook_url": "https://www.facebook.com/proaktivvoss",
        "instagram_url": "https://www.instagram.com/proaktivvoss/",
        "linkedin_url": None,
    },
    # Sandviken & Bergen Nord
    "sandviken": {
        "facebook_url": None,  # Outdated, use main account
        "instagram_url": "https://www.instagram.com/proaktivsandvikenogbergennord/",
        "linkedin_url": None,
    },
    # Ålesund
    "alesund": {
        "facebook_url": "https://www.facebook.com/profile.php?id=100065148054944",
        "instagram_url": "https://www.instagram.com/proaktivaalesund/",
        "linkedin_url": None,
    },
    # Lørenskog (Romerike)
    "lorenskog": {
        "facebook_url": "https://www.facebook.com/ProaktivRomerike",
        "instagram_url": "https://www.instagram.com/proaktivromerike/",
        "linkedin_url": None,
    },
    # Lillestrøm (Romerike)
    "lillestrom": {
        "facebook_url": "https://www.facebook.com/ProaktivRomerike",
        "instagram_url": "https://www.instagram.com/proaktivromerike/",
        "linkedin_url": None,
    },
    # Group / holding companies - use company defaults
    "gruppen": {
        "facebook_url": "https://www.facebook.com/proaktiveiendom",
        "instagram_url": "https://www.instagram.com/proaktiveiendomsmegling/",
        "linkedin_url": "https://no.linkedin.com/company/proaktiv-eiendomsmegling",
    },
}


def _normalize_office_name(name: str) -> str:
    """Normalize office name to a key for lookup."""
    name_lower = name.lower()

    # Map various office name patterns to their canonical keys
    patterns = {
        "haugesund": "haugesund",
        "sandnes": "sandnes",
        "stavanger": "stavanger",
        "bergen sentrum": "bergen_sentrum",
        "småstrandgaten": "bergen_sentrum",
        "drammen": "drammen",
        "lier": "drammen",
        "holmestrand": "drammen",
        "jæren": "jaeren",
        "jaeren": "jaeren",
        "sola": "sola",
        "kristiansand": "kristiansand",
        "briskeby": "briskeby",
        "properties": "briskeby",
        "skien": "skien",
        "sarpsborg": "sarpsborg",
        "trondheim sentrum": "trondheim_sentrum",
        "trondheim øst": "trondheim_ost",
        "trondheim ost": "trondheim_ost",
        "moholt": "trondheim_ost",
        "trondheim syd": "trondheim_syd",
        "heimdal": "trondheim_syd",
        "voss": "voss",
        "sandviken": "sandviken",
        "bergen nord": "sandviken",
        "ålesund": "alesund",
        "alesund": "alesund",
        "lørenskog": "lorenskog",
        "lorenskog": "lorenskog",
        "lillestrøm": "lillestrom",
        "lillestrom": "lillestrom",
        "gruppen": "gruppen",
        "kjedeledelse": "gruppen",
        "oppgjør": "gruppen",
    }

    for pattern, key in patterns.items():
        if pattern in name_lower:
            return key

    return ""


def get_social_data(office_name: str) -> dict[str, str | None] | None:
    """Get social media data for an office by name."""
    key = _normalize_office_name(office_name)
    if key:
        return _SOCIAL_DATA.get(key)
    return None


# Legacy format for backwards compatibility (maps exact names)
OFFICE_SOCIAL_DATA: dict[str, dict[str, str | None]] = {}


def seed_social_media(dry_run: bool = False) -> None:
    """Seed social media URLs for offices."""
    engine = create_engine(settings.DATABASE_URL)

    updated_count = 0
    skipped_count = 0
    not_found_count = 0

    print("\n" + "=" * 70)
    print("OFFICE SOCIAL MEDIA SEEDING")
    print("=" * 70)
    print(f"Mode: {'DRY RUN (no changes)' if dry_run else 'LIVE (applying changes)'}")

    with engine.connect() as conn:
        # Fetch offices using raw SQL to avoid ORM schema issues
        result = conn.execute(
            text("""
                SELECT id, name, facebook_url, instagram_url, linkedin_url
                FROM offices
                WHERE is_active = true
                ORDER BY name
            """)
        )
        offices = result.fetchall()

        print(f"Found {len(offices)} active offices")
        print("-" * 70)

        for office in offices:
            office_id, office_name, current_fb, current_ig, current_li = office
            social_data = get_social_data(office_name)

            if social_data is None:
                print(f"\n[!] {office_name}")
                print("    Not in mapping - add to OFFICE_SOCIAL_DATA dict")
                not_found_count += 1
                continue

            changes = []
            updates = {}

            # Check each social media field
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
                        (current_value[:40] + "...") if current_value and len(current_value) > 40 else current_value
                    )
                    short_new = (new_value[:40] + "...") if len(new_value) > 40 else new_value
                    changes.append(f"{field}: '{short_current}' -> '{short_new}'")
                    updates[field] = new_value

            if changes:
                print(f"\n[UPDATE] {office_name}")
                for change in changes:
                    print(f"         {change}")
                updated_count += 1

                if not dry_run and updates:
                    # Build dynamic UPDATE statement
                    set_clauses = ", ".join(f"{k} = :{k}" for k in updates.keys())
                    updates["office_id"] = str(office_id)
                    conn.execute(
                        text(f"UPDATE offices SET {set_clauses} WHERE id = :office_id"),
                        updates,
                    )
            else:
                print(f"\n[OK] {office_name} - already up to date or no changes")
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
    print(f"Not in map:   {not_found_count}")
    print("=" * 70)

    if not_found_count > 0:
        print("\n[!] Some offices are not in the mapping. Add them to OFFICE_SOCIAL_DATA.")


def main():
    parser = argparse.ArgumentParser(description="Seed social media URLs for offices")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without applying them",
    )
    args = parser.parse_args()

    seed_social_media(dry_run=args.dry_run)


if __name__ == "__main__":
    main()
