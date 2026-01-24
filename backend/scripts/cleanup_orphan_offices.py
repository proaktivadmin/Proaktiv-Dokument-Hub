"""
Cleanup orphaned offices and migrate employees to Vitec offices.

This script:
1. Maps orphaned offices (from proaktiv.no scraping) to Vitec offices
2. Migrates employees from orphaned offices to their Vitec counterparts
3. Deletes orphaned offices

Run with --dry-run first to preview changes.

Usage:
    python scripts/cleanup_orphan_offices.py --dry-run  # Preview
    python scripts/cleanup_orphan_offices.py            # Execute
"""

import argparse
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Manual mapping: orphan office name -> Vitec office name
# These are offices from proaktiv.no scraping that should map to Vitec departments
OFFICE_MAPPING = {
    # Direct matches (name variations)
    "Aktiv Oppgjør As": "Aktiv oppgjør",
    "Proaktiv Gruppen As": "Proaktiv Gruppen",
    "Proaktiv Trondheim Sentrum": "Proakiv Trondheim Sentrum",  # Note: Vitec has typo
    "Proaktiv Properties": "Proaktiv Briskeby",  # Same legal name
    # "Proaktiv Eiendomsmegling X" -> "Proaktiv X"
    "Proaktiv Eiendomsmegling Haugesund": "Proaktiv Haugesund",
    "Proaktiv Eiendomsmegling Jæren": "Proaktiv Jæren",
    "Proaktiv Eiendomsmegling Kristiansand": "Sør",  # Kristiansand not in Vitec - map to Sør region temporarily
    "Proaktiv Eiendomsmegling Lillestrøm": "Proaktiv Lillestrøm",
    "Proaktiv Eiendomsmegling Lørenskog": "Proaktiv Lørenskog",
    "Proaktiv Eiendomsmegling Moholt": "Proaktiv Trondheim Øst",  # Moholt is in Trondheim Øst
    "Proaktiv Eiendomsmegling Sandnes": "Proaktiv Sandnes",
    "Proaktiv Eiendomsmegling Sandviken": "Proaktiv Sandviken og Bergen Nord",
    "Proaktiv Eiendomsmegling Skien": "Proaktiv Skien",
    "Proaktiv Eiendomsmegling Småstrandgaten": "Proaktiv Bergen Sentrum",  # Småstrandgaten is Bergen Sentrum
    "Proaktiv Eiendomsmegling Sola": "Proaktiv Sola",
    "Proaktiv Eiendomsmegling Stavanger": "Proaktiv Stavanger",
    "Proaktiv Eiendomsmegling Voss": "Proaktiv Voss",
    "Proaktiv Drammen Lier Holmestrand": "Proaktiv Drammen, Lier og Holmestrand",
    "Proaktiv Sarpsborg Næring": "Proaktiv Sarpsborg - Næring",
    # No Vitec equivalent - will be deleted (no employees expected)
    "Kjedeledelse": None,
    "Proaktiv Kjedeledelse": None,
}


def cleanup_offices(dry_run: bool = True):
    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        print("ERROR: DATABASE_URL not set")
        sys.exit(1)

    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine)

    with Session() as session:
        print("=" * 70)
        print("OFFICE CLEANUP - Migrate to Vitec as Single Source of Truth")
        print("=" * 70)
        print(f"Mode: {'DRY RUN (no changes)' if dry_run else 'LIVE (applying changes)'}")
        print()

        # Build lookup of Vitec offices by name (case-insensitive)
        result = session.execute(
            text("""
            SELECT id, name FROM offices WHERE vitec_department_id IS NOT NULL
        """)
        )
        vitec_lookup = {row[1].lower(): row[0] for row in result}

        # Get orphaned offices
        result = session.execute(
            text("""
            SELECT o.id, o.name, COUNT(e.id) as emp_count
            FROM offices o
            LEFT JOIN employees e ON e.office_id::uuid = o.id
            WHERE o.vitec_department_id IS NULL
            GROUP BY o.id, o.name
            ORDER BY o.name
        """)
        )
        orphans = [(row[0], row[1], row[2]) for row in result]

        migrated_employees = 0
        deleted_offices = 0
        manual_review = []

        for orphan_id, orphan_name, emp_count in orphans:
            # Look up the mapping
            target_name = OFFICE_MAPPING.get(orphan_name)

            if target_name is None:
                # No mapping - delete if no employees, flag for review if employees exist
                if emp_count > 0:
                    manual_review.append((orphan_name, emp_count))
                    print(f"[REVIEW] {orphan_name} ({emp_count} employees) - needs manual mapping")
                else:
                    print(f"[DELETE] {orphan_name} (no employees, no Vitec equivalent)")
                    if not dry_run:
                        session.execute(text("DELETE FROM offices WHERE id = :id"), {"id": orphan_id})
                    deleted_offices += 1
                continue

            # Find target Vitec office
            target_id = vitec_lookup.get(target_name.lower())
            if not target_id:
                print(f"[ERROR] {orphan_name} -> {target_name} (target not found!)")
                if emp_count > 0:
                    manual_review.append((orphan_name, emp_count))
                continue

            # Migrate employees
            if emp_count > 0:
                print(f"[MIGRATE] {orphan_name} -> {target_name} ({emp_count} employees)")
                if not dry_run:
                    session.execute(
                        text("""
                        UPDATE employees SET office_id = :target_id
                        WHERE office_id::uuid = :orphan_id
                    """),
                        {"target_id": str(target_id), "orphan_id": orphan_id},
                    )
                migrated_employees += emp_count
            else:
                print(f"[DELETE] {orphan_name} -> {target_name} (0 employees, duplicate)")

            # Delete orphan office
            if not dry_run:
                session.execute(text("DELETE FROM offices WHERE id = :id"), {"id": orphan_id})
            deleted_offices += 1

        if not dry_run:
            session.commit()

        print()
        print("=" * 70)
        print("SUMMARY")
        print("=" * 70)
        print(f"Employees migrated:  {migrated_employees}")
        print(f"Offices deleted:     {deleted_offices}")
        print(f"Need manual review:  {len(manual_review)}")

        if manual_review:
            print()
            print("MANUAL REVIEW REQUIRED:")
            for name, count in manual_review:
                print(f"  - {name} ({count} employees)")
            print()
            print("Add these to OFFICE_MAPPING dict and re-run.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Cleanup orphaned offices")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes only")
    args = parser.parse_args()

    cleanup_offices(dry_run=args.dry_run)
