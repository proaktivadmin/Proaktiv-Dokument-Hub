"""Move specific employees to new offices."""

import os

from sqlalchemy import create_engine, text

DATABASE_URL = os.environ["DATABASE_URL"]
engine = create_engine(DATABASE_URL)

with engine.connect() as conn:
    # Get office IDs
    gruppen = conn.execute(text("SELECT id FROM offices WHERE name = 'Proaktiv Gruppen'")).fetchone()
    aktiv = conn.execute(text("SELECT id FROM offices WHERE name = 'Aktiv oppgjør'")).fetchone()

    print("Moving employees:")

    # Move edl@proaktiv.no to Proaktiv Gruppen
    result = conn.execute(
        text("SELECT id, first_name, last_name FROM employees WHERE email = 'edl@proaktiv.no'")
    ).fetchone()
    if result:
        print(f"  - {result.first_name} {result.last_name} (edl@proaktiv.no) -> Proaktiv Gruppen")
        conn.execute(
            text("UPDATE employees SET office_id = :office_id WHERE id = :emp_id"),
            {"office_id": gruppen.id, "emp_id": result.id},
        )

    # Move alo@proaktiv.no to Aktiv Oppgjør
    result = conn.execute(
        text("SELECT id, first_name, last_name FROM employees WHERE email = 'alo@proaktiv.no'")
    ).fetchone()
    if result:
        print(f"  - {result.first_name} {result.last_name} (alo@proaktiv.no) -> Aktiv oppgjør")
        conn.execute(
            text("UPDATE employees SET office_id = :office_id WHERE id = :emp_id"),
            {"office_id": aktiv.id, "emp_id": result.id},
        )

    conn.commit()
    print("Done!")
