"""
Clean up Trondheim Sentrum offices:
1. Create Proaktiv Trondheim Sentrum (Pacta Eiendom AS, org.nr: 983374654)
2. Move all employees from both Oppgjør offices to the main office
3. Delete the Oppgjør sub-offices

Usage:
    python scripts/cleanup_trondheim.py --dry-run   # Preview
    python scripts/cleanup_trondheim.py             # Apply
"""

import os
import sys
import uuid

from sqlalchemy import create_engine, text

DATABASE_URL = os.environ.get(
    "DATABASE_URL", "postgresql://postgres:JBWPwgfKvuYllOspSIJFzjiVOycOWwiv@shuttle.proxy.rlwy.net:51557/railway"
)

engine = create_engine(DATABASE_URL)

DRY_RUN = "--dry-run" in sys.argv

# Trondheim Sentrum Oppgjør offices to merge and delete
TRONDHEIM_OPPGJOR_OFFICES = [
    "286af524-7ed1-4d2e-8ea7-c8b174eda23e",  # Christian Vehn Breida (no org nr)
    "a571ea1d-aab5-4b12-b0d7-bcd78bd1c669",  # 17 employees (has org nr)
]


def main():
    print("=" * 70)
    print("TRONDHEIM SENTRUM CLEANUP")
    print("=" * 70)
    print(f"Mode: {'DRY RUN' if DRY_RUN else 'LIVE'}")
    print()

    with engine.connect() as conn:
        # 1. Create Proaktiv Trondheim Sentrum
        trondheim_id = str(uuid.uuid4())
        print("1. CREATE: Proaktiv Trondheim Sentrum")
        print("   Legal Name: Pacta Eiendom AS")
        print("   Org Nr: 983374654")
        print(f"   New ID: {trondheim_id}")

        if not DRY_RUN:
            conn.execute(
                text("""
                INSERT INTO offices (id, name, short_code, legal_name, organization_number, created_at, updated_at)
                VALUES (:id, :name, :short_code, :legal_name, :org_nr, NOW(), NOW())
            """),
                {
                    "id": trondheim_id,
                    "name": "Proaktiv Trondheim Sentrum",
                    "short_code": "TRD_SENTR",
                    "legal_name": "Pacta Eiendom AS",
                    "org_nr": "983374654",
                },
            )
        print()

        # 2. Move all employees from Oppgjør offices to main office
        print("2. MOVE: Employees to Proaktiv Trondheim Sentrum")
        for office_id in TRONDHEIM_OPPGJOR_OFFICES:
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
                        {"new_office_id": trondheim_id, "emp_id": row.id},
                    )
        print()

        # 3. Delete Oppgjør offices
        print("3. DELETE: Trondheim Sentrum Oppgjør offices")
        for office_id in TRONDHEIM_OPPGJOR_OFFICES:
            result = conn.execute(text("SELECT name FROM offices WHERE id = :id"), {"id": office_id})
            row = result.fetchone()
            if row:
                print(f"   - {row.name} ({office_id})")
                if not DRY_RUN:
                    conn.execute(
                        text("UPDATE offices SET parent_office_id = NULL WHERE parent_office_id = :id"),
                        {"id": office_id},
                    )
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
