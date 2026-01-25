"""List all offices with vital signature information."""

from sqlalchemy import create_engine, text

DATABASE_URL = "postgresql://postgres:lOZBFAkACyDixRzjSHjRQCrdVTwuDrxA@shuttle.proxy.rlwy.net:51557/railway"
engine = create_engine(DATABASE_URL)

with engine.connect() as conn:
    result = conn.execute(
        text("""
        SELECT
            o.name,
            o.legal_name,
            o.organization_number,
            o.email,
            o.phone,
            o.street_address,
            o.postal_code,
            o.city,
            o.homepage_url,
            (SELECT COUNT(*) FROM employees e WHERE e.office_id = o.id) as employee_count
        FROM offices o
        WHERE o.is_active = true
        ORDER BY o.name
    """)
    ).fetchall()

    print("=" * 120)
    print(f"{'OFFICE':<35} {'LEGAL NAME':<30} {'ORG.NR':<12} {'EMPLOYEES':<10}")
    print("=" * 120)

    missing_info = []

    for row in result:
        print(
            f"{row.name:<35} {(row.legal_name or '-'):<30} {(row.organization_number or '-'):<12} {row.employee_count:<10}"
        )
        print(f"  Email: {row.email or 'MISSING'}")
        print(f"  Phone: {row.phone or 'MISSING'}")
        addr = row.street_address or "MISSING"
        postal = row.postal_code or "?"
        city = row.city or "MISSING"
        print(f"  Address: {addr}, {postal} {city}")
        print(f"  Homepage: {row.homepage_url or 'MISSING'}")
        print()

        # Track missing vital fields for offices with employees
        if row.employee_count > 0:
            missing = []
            if not row.phone:
                missing.append("phone")
            if not row.street_address:
                missing.append("address")
            if not row.city:
                missing.append("city")
            if not row.postal_code:
                missing.append("postal_code")
            if missing:
                missing_info.append((row.name, row.employee_count, missing))

    print("=" * 120)
    print(f"Total: {len(result)} offices")
    print()

    if missing_info:
        print("WARNING - OFFICES WITH EMPLOYEES MISSING SIGNATURE INFO:")
        print("-" * 80)
        for name, count, fields in missing_info:
            print(f"  {name} ({count} employees): Missing {', '.join(fields)}")
    else:
        print("All offices with employees have complete signature information!")
