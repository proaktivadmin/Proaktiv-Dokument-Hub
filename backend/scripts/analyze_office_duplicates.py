"""Analyze office duplicates between Vitec and scraped data."""

import os

from sqlalchemy import create_engine, text

db_url = os.environ.get("DATABASE_URL")
engine = create_engine(db_url)

with engine.connect() as conn:
    print("=== VITEC OFFICES (source of truth) ===")
    print()
    result = conn.execute(
        text("""
        SELECT name, legal_name, organization_number, vitec_department_id
        FROM offices
        WHERE vitec_department_id IS NOT NULL
        ORDER BY name
    """)
    )
    vitec_offices = []
    for row in result:
        org = row[2] if row[2] else "-"
        legal = row[1][:40] if row[1] else "-"
        print(f"{row[0]}")
        print(f"  Legal: {legal}, Org: {org}, VitecID: {row[3]}")
        vitec_offices.append(row[0].lower())

    print()
    print("=" * 60)
    print()
    print("=== ORPHANED OFFICES (from scraping) ===")
    print()
    result = conn.execute(
        text("""
        SELECT o.id, o.name, COUNT(e.id) as emp_count
        FROM offices o
        LEFT JOIN employees e ON e.office_id::uuid = o.id
        WHERE o.vitec_department_id IS NULL
        GROUP BY o.id, o.name
        ORDER BY o.name
    """)
    )

    for row in result:
        emp_info = f" ({row[2]} employees)" if row[2] > 0 else ""
        name_lower = row[1].lower()

        # Check for potential matches
        matches = []
        for vitec_name in vitec_offices:
            # Simple fuzzy match
            if name_lower in vitec_name or vitec_name in name_lower:
                matches.append(vitec_name)
            # Check for similar start
            elif name_lower[:15] == vitec_name[:15]:
                matches.append(vitec_name)

        match_info = f" -> likely: {matches[0]}" if matches else " -> NO MATCH"
        print(f"{row[1]}{emp_info}{match_info}")
