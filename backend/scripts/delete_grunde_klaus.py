"""Delete Grunde and Klaus accounts."""

import os

from sqlalchemy import create_engine, text

DATABASE_URL = os.environ["DATABASE_URL"]

engine = create_engine(DATABASE_URL)

# Accounts to delete (case-insensitive search)
names_to_delete = ["grunde", "klaus"]

with engine.connect() as conn:
    for name in names_to_delete:
        result = conn.execute(
            text("""
            DELETE FROM employees
            WHERE first_name ILIKE :name
            RETURNING id, first_name, last_name, email
        """),
            {"name": f"%{name}%"},
        )

        deleted = list(result)
        if deleted:
            for row in deleted:
                print(f"DELETED: {row[1]} {row[2]} ({row[3]})")
        else:
            print(f"NOT FOUND: {name}")

    conn.commit()

    # Show remaining count
    result = conn.execute(text("SELECT COUNT(*) FROM employees"))
    count = result.fetchone()[0]
    print(f"\nRemaining employees: {count}")
