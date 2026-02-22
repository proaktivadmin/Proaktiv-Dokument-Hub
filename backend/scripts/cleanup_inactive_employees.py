"""
Delete inactive employees from the database.

This script removes employees with status != 'active'.
Run with --dry-run first to preview what will be deleted.

Usage:
    python scripts/cleanup_inactive_employees.py --dry-run   # Preview
    python scripts/cleanup_inactive_employees.py             # Delete
"""

import os
import sys

from sqlalchemy import create_engine, text

DATABASE_URL = os.environ["DATABASE_URL"]

engine = create_engine(DATABASE_URL)

DRY_RUN = "--dry-run" in sys.argv


def main():
    print("=" * 80)
    print("CLEANUP INACTIVE EMPLOYEES")
    print("=" * 80)
    print(f"Mode: {'DRY RUN' if DRY_RUN else 'LIVE - WILL DELETE'}")
    print()

    with engine.connect() as conn:
        # Get inactive employees
        result = conn.execute(
            text("""
            SELECT e.id, e.first_name, e.last_name, e.email, e.status, e.employee_type, o.name as office_name
            FROM employees e
            LEFT JOIN offices o ON e.office_id = o.id
            WHERE e.status != 'active'
            ORDER BY e.status, o.name, e.last_name
        """)
        )

        inactive = list(result)

        if not inactive:
            print("No inactive employees found. Nothing to delete.")
            return

        print(f"Found {len(inactive)} inactive employees to delete:\n")

        for row in inactive:
            status = row[4].upper()
            name = f"{row[1]} {row[2]}"
            email = row[3] or "(no email)"
            office = row[6] or "No office"
            emp_type = row[5]
            print(f"  [{status:12}] {name:30} | {email:40} | {office} [{emp_type}]")

        print()

        if DRY_RUN:
            print(f"DRY RUN: Would delete {len(inactive)} employees.")
            print("Run without --dry-run to actually delete.")
        else:
            # Delete inactive employees
            result = conn.execute(
                text("""
                DELETE FROM employees
                WHERE status != 'active'
                RETURNING id, first_name, last_name, email
            """)
            )

            deleted = list(result)
            conn.commit()

            print(f"DELETED {len(deleted)} employees.")

        print()

        # Show remaining count
        result = conn.execute(
            text("""
            SELECT employee_type, COUNT(*) as count
            FROM employees
            WHERE status = 'active'
            GROUP BY employee_type
            ORDER BY employee_type
        """)
        )

        print("Remaining active employees by type:")
        for row in result:
            print(f"  {row[0]:12} : {row[1]}")


if __name__ == "__main__":
    main()
