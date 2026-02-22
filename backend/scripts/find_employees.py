"""Find employees by name for merging/updating."""

import os
import sys

from sqlalchemy import create_engine, text

DATABASE_URL = os.environ["DATABASE_URL"]

engine = create_engine(DATABASE_URL)


def find_employees(search_term: str):
    with engine.connect() as conn:
        result = conn.execute(
            text("""
            SELECT id, first_name, last_name, email, profile_image_url, title, phone, office_id, homepage_profile_url, employee_type
            FROM employees
            WHERE first_name ILIKE :search OR last_name ILIKE :search OR email ILIKE :search
            ORDER BY last_name, first_name
        """),
            {"search": f"%{search_term}%"},
        )

        for row in result:
            print(f"ID: {row[0]}")
            print(f"  Name: {row[1]} {row[2]}")
            print(f"  Email: {row[3]}")
            print(f"  Photo: {row[4]}")
            print(f"  Title: {row[5]}")
            print(f"  Phone: {row[6]}")
            print(f"  Office ID: {row[7]}")
            print(f"  Homepage: {row[8]}")
            print(f"  Type: {row[9]}")
            print("---")


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python find_employees.py <search_term>")
        sys.exit(1)

    find_employees(sys.argv[1])
