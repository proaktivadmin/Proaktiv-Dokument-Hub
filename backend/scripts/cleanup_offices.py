"""
Clean up office/department structure:
1. Remove region offices: Sør, Vest, Trøndelag, Sør-Rogaland, Romerike
2. Create Proaktiv Sarpsborg (Meglerhuset Borg AS) and move næring employees there
3. Create Proaktiv Skien (Meland Eiendomsmegling AS) and move næring employees there
4. Delete the næring/næringsoppgjør sub-offices

Usage:
    python scripts/cleanup_offices.py --dry-run   # Preview
    python scripts/cleanup_offices.py             # Apply
"""

import os
import sys
import uuid

from sqlalchemy import create_engine, text

DATABASE_URL = os.environ["DATABASE_URL"]

engine = create_engine(DATABASE_URL)

DRY_RUN = "--dry-run" in sys.argv

# Region offices to delete (no employees)
REGION_OFFICES = [
    "9dd62fa4-0a90-4fc6-9c81-ead10003f449",  # Sør
    "bdd7a5e0-47d1-4973-9cae-88368592d037",  # Vest
    "8b04c548-601d-4367-8c1d-c34b8f63aa86",  # Trøndelag
    "e0af5fba-d117-4012-85e4-42fdf2bfee8a",  # Sør-Rogaland
    "fe91f21a-e456-4bcd-a89c-e84e03fc10b1",  # Romerike
]

# Sarpsborg næring offices to merge
SARPSBORG_NAERING_OFFICES = [
    "620235fc-2e15-4357-b726-8cba5aeca71b",  # Proaktiv Sarpsborg - Næring
    "486928bc-49b7-4cc2-8e48-2a9795c496c9",  # Proaktiv Sarpsborg Næringsoppgjør (parent)
    "1247bed5-5e4c-41ed-99b4-e1fb547c92d0",  # Proaktiv Sarpsborg Næringsoppgjør (child)
]

# Skien næring offices to merge
SKIEN_NAERING_OFFICES = [
    "212bb150-f090-408a-9993-95671efbb443",  # Proaktiv Skien - Næring
    "92f2afd8-be94-4ae9-8fa1-e8bc3fa2234a",  # Proaktiv Skien - Næringsoppgjør (child)
    "6f651a5b-9ca2-458c-8250-8614df56a962",  # Proaktiv Skien - Næringsoppgjør (parent)
]


def main():
    print("=" * 70)
    print("OFFICE CLEANUP")
    print("=" * 70)
    print(f"Mode: {'DRY RUN' if DRY_RUN else 'LIVE'}")
    print()

    with engine.connect() as conn:
        # 1. Create Proaktiv Sarpsborg
        sarpsborg_id = str(uuid.uuid4())
        print("1. CREATE: Proaktiv Sarpsborg")
        print("   Legal Name: Meglerhuset Borg AS")
        print("   Org Nr: 994976192")
        print(f"   New ID: {sarpsborg_id}")

        if not DRY_RUN:
            conn.execute(
                text("""
                INSERT INTO offices (id, name, short_code, legal_name, organization_number, created_at, updated_at)
                VALUES (:id, :name, :short_code, :legal_name, :org_nr, NOW(), NOW())
            """),
                {
                    "id": sarpsborg_id,
                    "name": "Proaktiv Sarpsborg",
                    "short_code": "SARPSBORG",
                    "legal_name": "Meglerhuset Borg AS",
                    "org_nr": "994976192",
                },
            )
        print()

        # 2. Move Sarpsborg næring employees to main office
        print("2. MOVE: Sarpsborg næring employees to Proaktiv Sarpsborg")
        for office_id in SARPSBORG_NAERING_OFFICES:
            result = conn.execute(
                text("""
                SELECT id, first_name, last_name, email FROM employees
                WHERE office_id = :office_id
            """),
                {"office_id": office_id},
            )

            for row in result:
                print(f"   - {row.first_name} {row.last_name} ({row.email})")
                if not DRY_RUN:
                    conn.execute(
                        text("""
                        UPDATE employees SET office_id = :new_office_id WHERE id = :emp_id
                    """),
                        {"new_office_id": sarpsborg_id, "emp_id": row.id},
                    )
        print()

        # 3. Create Proaktiv Skien
        skien_id = str(uuid.uuid4())
        print("3. CREATE: Proaktiv Skien")
        print("   Legal Name: Meland Eiendomsmegling AS")
        print("   Org Nr: 997898400")
        print(f"   New ID: {skien_id}")

        if not DRY_RUN:
            conn.execute(
                text("""
                INSERT INTO offices (id, name, short_code, legal_name, organization_number, created_at, updated_at)
                VALUES (:id, :name, :short_code, :legal_name, :org_nr, NOW(), NOW())
            """),
                {
                    "id": skien_id,
                    "name": "Proaktiv Skien",
                    "short_code": "SKIEN",
                    "legal_name": "Meland Eiendomsmegling AS",
                    "org_nr": "997898400",
                },
            )
        print()

        # 4. Move Skien næring employees to main office
        print("4. MOVE: Skien næring employees to Proaktiv Skien")
        for office_id in SKIEN_NAERING_OFFICES:
            result = conn.execute(
                text("""
                SELECT id, first_name, last_name, email FROM employees
                WHERE office_id = :office_id
            """),
                {"office_id": office_id},
            )

            for row in result:
                print(f"   - {row.first_name} {row.last_name} ({row.email})")
                if not DRY_RUN:
                    conn.execute(
                        text("""
                        UPDATE employees SET office_id = :new_office_id WHERE id = :emp_id
                    """),
                        {"new_office_id": skien_id, "emp_id": row.id},
                    )
        print()

        # 5. Delete Sarpsborg næring offices (clear parent references first)
        print("5. DELETE: Sarpsborg næring offices")
        for office_id in SARPSBORG_NAERING_OFFICES:
            result = conn.execute(text("SELECT name FROM offices WHERE id = :id"), {"id": office_id})
            row = result.fetchone()
            if row:
                print(f"   - {row.name}")
                if not DRY_RUN:
                    # Clear parent references first
                    conn.execute(
                        text("UPDATE offices SET parent_office_id = NULL WHERE parent_office_id = :id"),
                        {"id": office_id},
                    )
                    conn.execute(text("DELETE FROM offices WHERE id = :id"), {"id": office_id})
        print()

        # 6. Delete Skien næring offices
        print("6. DELETE: Skien næring offices")
        for office_id in SKIEN_NAERING_OFFICES:
            result = conn.execute(text("SELECT name FROM offices WHERE id = :id"), {"id": office_id})
            row = result.fetchone()
            if row:
                print(f"   - {row.name}")
                if not DRY_RUN:
                    conn.execute(
                        text("UPDATE offices SET parent_office_id = NULL WHERE parent_office_id = :id"),
                        {"id": office_id},
                    )
                    conn.execute(text("DELETE FROM offices WHERE id = :id"), {"id": office_id})
        print()

        # 7. Delete region offices
        print("7. DELETE: Region offices (Sør, Vest, Trøndelag, Sør-Rogaland, Romerike)")
        for office_id in REGION_OFFICES:
            result = conn.execute(text("SELECT name FROM offices WHERE id = :id"), {"id": office_id})
            row = result.fetchone()
            if row:
                print(f"   - {row.name}")
                if not DRY_RUN:
                    conn.execute(text("DELETE FROM offices WHERE id = :id"), {"id": office_id})
        print()

        if not DRY_RUN:
            conn.commit()

        print("=" * 70)
        if DRY_RUN:
            print("DRY RUN: No changes made. Run without --dry-run to apply.")
        else:
            print("COMPLETE: All changes applied.")
        print("=" * 70)


if __name__ == "__main__":
    main()
