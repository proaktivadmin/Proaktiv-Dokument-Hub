"""List all offices with employee counts."""

import os

from sqlalchemy import create_engine, text

DATABASE_URL = os.environ.get(
    "DATABASE_URL", "postgresql://postgres:JBWPwgfKvuYllOspSIJFzjiVOycOWwiv@shuttle.proxy.rlwy.net:51557/railway"
)
engine = create_engine(DATABASE_URL)

with engine.connect() as conn:
    result = conn.execute(
        text("""
        SELECT o.name, o.legal_name, o.organization_number, COUNT(e.id) as emp_count
        FROM offices o
        LEFT JOIN employees e ON e.office_id = o.id AND e.status = 'active'
        GROUP BY o.id, o.name, o.legal_name, o.organization_number
        ORDER BY o.name
    """)
    )

    print("Final office list:")
    print("=" * 90)
    total = 0
    for row in result:
        total += 1
        print(f"{row.name} ({row.emp_count} employees)")
        if row.legal_name:
            print(f"   Legal: {row.legal_name}")
        if row.organization_number:
            print(f"   Org.nr: {row.organization_number}")
    print("=" * 90)
    print(f"Total: {total} offices")
