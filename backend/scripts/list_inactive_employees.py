"""List all inactive employees for cleanup review."""

import os

from sqlalchemy import create_engine, text

DATABASE_URL = os.environ["DATABASE_URL"]

engine = create_engine(DATABASE_URL)


def main():
    print("=" * 80)
    print("INACTIVE EMPLOYEES (candidates for deletion)")
    print("=" * 80)

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

        if inactive:
            current_status = None
            for row in inactive:
                if row[4] != current_status:
                    current_status = row[4]
                    print(f"\n--- Status: {current_status.upper()} ---")
                print(f"  {row[3]} ({row[1]} {row[2]}) - {row[6] or 'No office'} [{row[5]}]")
            print(f"\nTotal inactive: {len(inactive)}")
        else:
            print("No inactive employees found.")

        print()
        print("=" * 80)
        print("ACTIVE EMPLOYEE COUNT BY TYPE")
        print("=" * 80)

        result = conn.execute(
            text("""
            SELECT employee_type, status, COUNT(*) as count
            FROM employees
            GROUP BY employee_type, status
            ORDER BY employee_type, status
        """)
        )

        for row in result:
            print(f"  {row[0]:12} | {row[1]:12} | {row[2]}")


if __name__ == "__main__":
    main()
