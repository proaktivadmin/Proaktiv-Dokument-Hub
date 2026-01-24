"""Check offices for duplicates and issues."""

import sys

sys.path.insert(0, ".")
import os

from sqlalchemy import create_engine, text

# Use Railway DATABASE_URL
db_url = os.environ.get("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/dokument_hub")
engine = create_engine(db_url)

with engine.connect() as conn:
    # Get all offices with employee counts
    result = conn.execute(
        text("""
        SELECT
            o.id,
            o.name,
            o.short_code,
            o.vitec_department_id,
            o.organization_number,
            o.office_type,
            o.parent_office_id,
            o.is_active,
            o.homepage_url,
            COUNT(e.id) as employee_count
        FROM offices o
        LEFT JOIN employees e ON e.office_id = o.id AND e.status = 'active'
        GROUP BY o.id
        ORDER BY o.name
    """)
    )

    offices = list(result)

    print("=== ALL OFFICES ===")
    print(f"{'Name':<45} {'Type':<8} {'Emp':<5} {'VitecID':<10} {'Active'}")
    print("-" * 85)
    for row in offices:
        office_type = row.office_type or "main"
        vitec_id = str(row.vitec_department_id) if row.vitec_department_id else ""
        print(f"{row.name[:44]:<45} {office_type:<8} {row.employee_count:<5} {vitec_id:<10} {row.is_active}")

    print(f"\nTotal: {len(offices)} offices")

    # Find offices with 0 employees
    print("\n=== OFFICES WITH 0 EMPLOYEES ===")
    zero_emp = [o for o in offices if o.employee_count == 0]
    for row in zero_emp:
        print(f"  - {row.name} (vitec_id={row.vitec_department_id}, active={row.is_active})")

    # Find potential duplicates by similar names
    print("\n=== POTENTIAL DUPLICATES (similar names) ===")
    names = [o.name.lower() for o in offices]
    for i, o1 in enumerate(offices):
        for o2 in offices[i + 1 :]:
            # Check for similar names
            n1 = o1.name.lower().replace("proaktiv ", "").replace(" - ", " ").replace("eiendomsmegling", "").strip()
            n2 = o2.name.lower().replace("proaktiv ", "").replace(" - ", " ").replace("eiendomsmegling", "").strip()
            if n1 == n2 or n1 in n2 or n2 in n1:
                if len(n1) > 3 and len(n2) > 3:  # Avoid short matches
                    print(f"  - '{o1.name}' vs '{o2.name}'")
                    print(f"    IDs: {o1.id[:8]}... vs {o2.id[:8]}...")
                    print(f"    Vitec: {o1.vitec_department_id} vs {o2.vitec_department_id}")
                    print(f"    Employees: {o1.employee_count} vs {o2.employee_count}")
                    print()
