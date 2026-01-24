"""
Set up sub-department relationships for Næring and Næringsoppgjør offices.

These offices exist as separate departments in Vitec Next due to system restrictions,
but should be displayed as sub-departments of their parent offices.

Mapping:
- "Meland Eiendomsmegling - Næring" -> sub of "Proaktiv Skien"
- "Meland Eiendomsmegling - Næringsoppgjør" -> sub of "Proaktiv Skien"
- "Proaktiv Sarpsborg - Næring" -> sub of "Proaktiv Sarpsborg"
- "Proaktiv Sarpsborg Næringsoppgjør" -> sub of "Proaktiv Sarpsborg"

Usage:
    python scripts/setup_sub_departments.py --dry-run  # Preview
    python scripts/setup_sub_departments.py            # Execute
"""

import argparse
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Sub-department mapping: (exact sub_office name, exact parent_office name)
SUB_DEPARTMENT_MAPPING = [
    # Skien
    ("Proaktiv Skien - Næring", "Proaktiv Skien"),
    ("Proaktiv Skien - Næringsoppgjør", "Proaktiv Skien"),
    # Sarpsborg
    ("Proaktiv Sarpsborg - Næring", "Proaktiv Sarpsborg"),
    ("Proaktiv Sarpsborg Næringsoppgjør", "Proaktiv Sarpsborg"),
]


def setup_sub_departments(dry_run: bool = True):
    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        print("ERROR: DATABASE_URL not set")
        sys.exit(1)

    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine)

    with Session() as session:
        print("=" * 70)
        print("SETUP SUB-DEPARTMENTS")
        print("=" * 70)
        print(f"Mode: {'DRY RUN (no changes)' if dry_run else 'LIVE (applying changes)'}")
        print()

        # Check if office_type column exists
        has_office_type = False
        try:
            session.execute(text("SELECT office_type FROM offices LIMIT 1"))
            has_office_type = True
        except Exception:
            session.rollback()
            print("ERROR: office_type column doesn't exist. Run migration first.")
            print("       alembic upgrade head")
            sys.exit(1)

        # Get all offices
        result = session.execute(text("SELECT id, name FROM offices"))
        offices = {row[1].lower(): row[0] for row in result}

        print(f"Found {len(offices)} offices in database")
        print()

        linked = 0
        for sub_name_exact, parent_name_exact in SUB_DEPARTMENT_MAPPING:
            # Find sub-office (exact match, case-insensitive)
            sub_id = offices.get(sub_name_exact.lower())

            # Find parent office (exact match, case-insensitive)
            parent_id = offices.get(parent_name_exact.lower())

            if sub_id and parent_id:
                print(f"[LINK] '{sub_name_exact}' -> '{parent_name_exact}'")
                if not dry_run:
                    session.execute(
                        text("""
                        UPDATE offices
                        SET parent_office_id = :parent_id, office_type = 'sub'
                        WHERE id = :sub_id
                    """),
                        {"parent_id": parent_id, "sub_id": sub_id},
                    )
                linked += 1
            elif not sub_id:
                print(f"[SKIP] '{sub_name_exact}' - not found in database")
            elif not parent_id:
                print(f"[WARN] '{sub_name_exact}' - parent '{parent_name_exact}' not found")

        if not dry_run:
            session.commit()
            print()
            print("CHANGES COMMITTED")

        print()
        print("=" * 70)
        print(f"Sub-departments linked: {linked}")
        print("=" * 70)

        # Show current sub-departments
        if has_office_type:
            result = session.execute(
                text("""
                SELECT s.name as sub_name, p.name as parent_name
                FROM offices s
                JOIN offices p ON s.parent_office_id = p.id
                WHERE s.office_type = 'sub'
                ORDER BY p.name, s.name
            """)
            )
            subs = list(result)
            if subs:
                print()
                print("Current sub-department structure:")
                for row in subs:
                    print(f"  {row[1]} -> {row[0]}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Setup sub-department relationships")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes only")
    args = parser.parse_args()

    setup_sub_departments(dry_run=args.dry_run)
