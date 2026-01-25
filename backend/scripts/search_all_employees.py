"""Search all employees including by first/last name."""

import os
import sys

from sqlalchemy import create_engine, text

DATABASE_URL = os.environ.get(
    "DATABASE_URL", "postgresql://postgres:JBWPwgfKvuYllOspSIJFzjiVOycOWwiv@shuttle.proxy.rlwy.net:51557/railway"
)

engine = create_engine(DATABASE_URL)


def search(term: str):
    with engine.connect() as conn:
        result = conn.execute(
            text("""
            SELECT e.id, e.first_name, e.last_name, e.email, e.status, e.employee_type,
                   o.name as office_name, e.profile_image_url
            FROM employees e
            LEFT JOIN offices o ON e.office_id = o.id
            WHERE e.first_name ILIKE :search
               OR e.last_name ILIKE :search
               OR e.email ILIKE :search
            ORDER BY e.last_name, e.first_name
        """),
            {"search": f"%{term}%"},
        )

        rows = list(result)
        if rows:
            for row in rows:
                print(f"ID: {row[0]}")
                print(f"  Name: {row[1]} {row[2]}")
                print(f"  Email: {row[3]}")
                print(f"  Status: {row[4]}")
                print(f"  Type: {row[5]}")
                print(f"  Office: {row[6]}")
                print(f"  Photo URL: {row[7][:60] if row[7] else '(none)'}...")
                print("---")
            print(f"Found {len(rows)} employees")
        else:
            print(f"No employees found matching '{term}'")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python search_all_employees.py <search_term>")
        sys.exit(1)
    search(sys.argv[1])
