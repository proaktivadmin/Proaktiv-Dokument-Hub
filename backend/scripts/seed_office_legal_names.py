"""
Seed script to populate legal company names (juridisk foretaksnavn) for offices.

The legal name is the registered company name ending in "AS" (Aksjeselskap)
that owns each Proaktiv franchise department.

Usage:
    python scripts/seed_office_legal_names.py [--dry-run]

Examples:
    python scripts/seed_office_legal_names.py --dry-run  # Preview changes
    python scripts/seed_office_legal_names.py            # Apply changes
"""

import argparse
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config import settings
from app.models.office import Office

# =============================================================================
# OFFICE LEGAL NAME MAPPINGS
# =============================================================================
# Format: "Marketing Name": ("Organization Number", "Legal Name AS")
#
# IMPORTANT: Organization number (organisasjonsnummer) is the PRIMARY KEY for
# matching departments between Vitec Next and Entra ID. It never changes.
#
# The legal name (juridisk foretaksnavn) will be synced to Entra ID's department
# field. It should end with "AS" (Aksjeselskap) for Norwegian stock companies.
#
# Find org numbers and legal names at: https://www.brreg.no/
# =============================================================================

OFFICE_LEGAL_DATA: dict[str, tuple[str | None, str | None]] = {
    # Format: "Marketing Name": ("Org Number", "Legal Name AS")
    # Trondheim offices
    "Proaktiv Trondheim Sentrum": (None, "Pacta Eiendom AS"),  # TODO: Add org number
    "Proaktiv Trondheim Syd": (None, None),
    "Proaktiv Eiendomsmegling Moholt": (None, None),
    # Bergen offices
    "Proaktiv Eiendomsmegling Sandviken": (None, None),
    "Proaktiv Eiendomsmegling Småstrandgaten": (None, None),
    "Proaktiv Eiendomsmegling Voss": (None, None),
    # Stavanger/Rogaland offices
    "Proaktiv Eiendomsmegling Stavanger": (None, None),
    "Proaktiv Eiendomsmegling Sandnes": (None, None),
    "Proaktiv Eiendomsmegling Sola": (None, None),
    "Proaktiv Eiendomsmegling Jæren": (None, None),
    "Proaktiv Eiendomsmegling Haugesund": (None, None),
    # Other offices
    "Proaktiv Eiendomsmegling Kristiansand": (None, None),
    "Proaktiv Eiendomsmegling Skien": (None, None),
    "Proaktiv Drammen Lier Holmestrand": (None, None),
    "Proaktiv Sarpsborg": (None, None),
    "Proaktiv Sarpsborg Næring": (None, None),
    # Group/holding companies
    "Proaktiv Gruppen As": (None, "Proaktiv Gruppen AS"),
    "Proaktiv Properties": (None, None),
    "Aktiv Oppgjør As": (None, "Aktiv Oppgjør AS"),
    "Proaktiv Kjedeledelse": (None, None),
    "Kjedeledelse": (None, None),
}


def seed_legal_names(dry_run: bool = False) -> None:
    """Seed legal names and organization numbers for offices."""
    engine = create_engine(settings.DATABASE_URL)
    Session = sessionmaker(bind=engine)
    db = Session()

    try:
        offices = db.query(Office).filter(Office.is_active).all()

        updated_count = 0
        skipped_count = 0
        not_found_count = 0

        print("\n" + "=" * 60)
        print("OFFICE LEGAL NAME SEEDING")
        print("=" * 60)
        print(f"Mode: {'DRY RUN (no changes)' if dry_run else 'LIVE (applying changes)'}")
        print(f"Found {len(offices)} active offices")
        print("-" * 60)

        for office in offices:
            legal_data = OFFICE_LEGAL_DATA.get(office.name)

            if legal_data is None:
                print(f"\n[!] {office.name}")
                print("    Not in mapping - add to OFFICE_LEGAL_DATA dict")
                not_found_count += 1
                continue

            legal_name, org_number = legal_data

            if legal_name is None and org_number is None:
                print(f"\n[SKIP] {office.name}")
                print("       No data provided yet (TODO)")
                skipped_count += 1
                continue

            changes = []

            if legal_name and office.legal_name != legal_name:
                changes.append(f"legal_name: '{office.legal_name}' -> '{legal_name}'")
                if not dry_run:
                    office.legal_name = legal_name

            if org_number and office.organization_number != org_number:
                changes.append(f"organization_number: '{office.organization_number}' -> '{org_number}'")
                if not dry_run:
                    office.organization_number = org_number

            if changes:
                print(f"\n[UPDATE] {office.name}")
                for change in changes:
                    print(f"         {change}")
                updated_count += 1
            else:
                print(f"\n[OK] {office.name} - already up to date")

        if not dry_run:
            db.commit()
            print("\n" + "-" * 60)
            print("Changes committed to database")

        print("\n" + "=" * 60)
        print("SUMMARY")
        print("=" * 60)
        print(f"Updated:   {updated_count}")
        print(f"Skipped:   {skipped_count} (no data provided)")
        print(f"Not found: {not_found_count} (not in mapping)")
        print("=" * 60)

        if not_found_count > 0:
            print("\n[!] Some offices are not in the mapping. Add them to OFFICE_LEGAL_DATA.")

        if skipped_count > 0:
            print("\n[i] Some offices have TODO entries. Fill in the legal names and org numbers.")

    except Exception as e:
        db.rollback()
        print(f"\n[ERROR] {e}")
        raise
    finally:
        db.close()


def main():
    parser = argparse.ArgumentParser(description="Seed legal company names for offices")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without applying them",
    )
    args = parser.parse_args()

    seed_legal_names(dry_run=args.dry_run)


if __name__ == "__main__":
    main()
