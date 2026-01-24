"""Check production offices for org numbers and legal names."""

import os

from sqlalchemy import create_engine, text

db_url = os.environ.get("DATABASE_URL")
engine = create_engine(db_url)

with engine.connect() as conn:
    print("Offices with legal names from Vitec:")
    print("-" * 80)
    result = conn.execute(
        text("""
        SELECT name, legal_name, organization_number, vitec_department_id
        FROM offices
        WHERE legal_name IS NOT NULL
        ORDER BY name
        LIMIT 20
    """)
    )
    for row in result:
        org = row[2] if row[2] else "-"
        vid = row[3] if row[3] else "-"
        print(f"Name: {row[0]}")
        print(f"  Legal: {row[1]}")
        print(f"  Org: {org}, Vitec ID: {vid}")
        print()
