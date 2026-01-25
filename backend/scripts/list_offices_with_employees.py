"""List all offices with their employee count."""

import os
import sys

from sqlalchemy import create_engine, text

DATABASE_URL = os.environ.get(
    "DATABASE_URL", "postgresql://postgres:JBWPwgfKvuYllOspSIJFzjiVOycOWwiv@shuttle.proxy.rlwy.net:51557/railway"
)

engine = create_engine(DATABASE_URL)


def list_offices():
    with engine.connect() as conn:
        result = conn.execute(
            text("""
            SELECT o.id, o.name, o.city,
                   COUNT(e.id) FILTER (WHERE e.status = 'active') as active_count,
                   COUNT(e.id) as total_count
            FROM offices o
            LEFT JOIN employees e ON e.office_id = o.id
            GROUP BY o.id, o.name, o.city
            ORDER BY o.name
        """)
        )

        print("=" * 80)
        print("OFFICES AND EMPLOYEE COUNTS")
        print("=" * 80)

        for row in result:
            print(f"{row[1]}")
            print(f"    City: {row[2]}")
            print(f"    Active: {row[3]} / Total: {row[4]}")
            print()


def list_office_employees(office_name: str):
    with engine.connect() as conn:
        result = conn.execute(
            text("""
            SELECT e.id, e.first_name, e.last_name, e.email, e.status, e.employee_type
            FROM employees e
            JOIN offices o ON e.office_id = o.id
            WHERE o.name ILIKE :search
            ORDER BY e.status, e.last_name
        """),
            {"search": f"%{office_name}%"},
        )

        rows = list(result)
        if rows:
            print(f"Employees in offices matching '{office_name}':")
            for row in rows:
                print(f"  [{row[4]:10}] {row[1]} {row[2]} ({row[3]}) [{row[5]}]")
            print(f"Total: {len(rows)}")
        else:
            print(f"No employees found in office matching '{office_name}'")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        list_office_employees(sys.argv[1])
    else:
        list_offices()
