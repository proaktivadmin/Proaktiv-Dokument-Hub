#!/usr/bin/env python
"""Check employee data in database."""

import os
import sys

from sqlalchemy import create_engine, text


def main():
    email = sys.argv[1] if len(sys.argv) > 1 else "froyland@proaktiv.no"

    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        print("No DATABASE_URL found")
        sys.exit(1)

    engine = create_engine(db_url)
    with engine.connect() as conn:
        result = conn.execute(
            text("""
            SELECT e.first_name, e.last_name, e.email, e.title, e.phone, e.status, e.profile_image_url,
                   o.name as office_name, o.city, o.street_address, o.postal_code, o.phone as office_phone
            FROM employees e
            LEFT JOIN offices o ON e.office_id = o.id
            WHERE e.email ILIKE :email_pattern
            OR e.last_name ILIKE :email_pattern
        """),
            {"email_pattern": f"%{email.split('@')[0]}%"},
        )

        rows = result.fetchall()
        if rows:
            for row in rows:
                print(f"Found: {row[0]} {row[1]}")
                print(f"Email: {row[2]}")
                print(f"Title: {row[3]}")
                print(f"Phone: {row[4]}")
                print(f"Status: {row[5]}")
                print(f"Profile Image: {row[6]}")
                print(f"Office: {row[7]}")
                print(f"Office City: {row[8]}")
                print(f"Office Address: {row[9]}")
                print(f"Office Postal: {row[10]}")
                print(f"Office Phone: {row[11]}")
        else:
            print(f"Not found: {email}")
            print("\nListing all emails:")
            result2 = conn.execute(text("SELECT email FROM employees WHERE email IS NOT NULL ORDER BY email LIMIT 30"))
            for r in result2:
                print(f"  - {r[0]}")


if __name__ == "__main__":
    main()
