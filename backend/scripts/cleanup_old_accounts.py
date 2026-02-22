"""Delete specific old accounts from scraping."""

import os

from sqlalchemy import create_engine, text

DATABASE_URL = os.environ["DATABASE_URL"]

engine = create_engine(DATABASE_URL)

# Old accounts to delete
emails_to_delete = [
    "gs@proa.no",  # Grunde Skillebekk - old account
    "line.skancke@azets.com",  # Line Skancke - old account
]

with engine.connect() as conn:
    for email in emails_to_delete:
        result = conn.execute(
            text("""
            DELETE FROM employees WHERE email = :email
            RETURNING id, first_name, last_name, email
        """),
            {"email": email},
        )

        deleted = result.fetchone()
        if deleted:
            print(f"DELETED: {deleted[1]} {deleted[2]} ({deleted[3]})")
        else:
            print(f"NOT FOUND: {email}")

    conn.commit()

    # Show remaining count
    result = conn.execute(text("SELECT COUNT(*) FROM employees WHERE status = 'active'"))
    count = result.fetchone()[0]
    print(f"\nRemaining active employees: {count}")
