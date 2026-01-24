#!/usr/bin/env python3
"""
Mark employees with external developer email domains as external and inactive.

Domains to mark:
- @vitecsoftware.com -> Vitec Software (system vendor)
- @destino.no -> Destino (integration partner)
- @funbit.no -> Funbit (development partner)
"""

import argparse
import os
import sys

from sqlalchemy import create_engine, or_
from sqlalchemy.orm import sessionmaker

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models.employee import Employee

EXTERNAL_DOMAINS = {
    "vitecsoftware.com": "Vitec Software",
    "destino.no": "Destino",
    "desti.no": "Destino",
    "funbit.no": "Funbit",
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Mark external developers as inactive.")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes without updating.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    database_url = os.environ.get("DATABASE_URL")
    if not database_url:
        print("ERROR: DATABASE_URL not set")
        sys.exit(1)

    engine = create_engine(database_url)
    Session = sessionmaker(bind=engine)

    print("\n" + "=" * 70)
    print("MARK EXTERNAL DEVELOPERS")
    print("=" * 70)
    print(f"Domains: {', '.join(EXTERNAL_DOMAINS.keys())}")
    print(f"Mode: {'DRY-RUN' if args.dry_run else 'LIVE'}")
    print("=" * 70 + "\n")

    with Session() as session:
        # Build filter for all external domains
        domain_filters = []
        for domain in EXTERNAL_DOMAINS.keys():
            domain_filters.append(Employee.email.ilike(f"%@{domain}"))

        # Find matching employees
        employees = session.query(Employee).filter(or_(*domain_filters)).all()

        print(f"Found {len(employees)} employees with external developer domains:\n")

        updated = 0
        for emp in employees:
            email_domain = emp.email.split("@")[1].lower() if emp.email and "@" in emp.email else None
            company = EXTERNAL_DOMAINS.get(email_domain, "External")

            was_internal = emp.employee_type == "internal"
            was_active = emp.status == "active"

            print(f"  {emp.full_name}")
            print(f"    Email: {emp.email}")
            print(f"    Current: type={emp.employee_type}, status={emp.status}")

            if was_internal or was_active or emp.external_company != company:
                emp.employee_type = "external"
                emp.external_company = company
                emp.status = "inactive"
                updated += 1
                print(f"    -> Updated: type=external, status=inactive, company={company}")
            else:
                print("    -> Already marked as external/inactive")
            print()

        if args.dry_run:
            session.rollback()
            print(f"DRY-RUN: Would update {updated} employees")
        else:
            session.commit()
            print(f"Updated {updated} employees")

    print("\n" + "=" * 70)
    print("DONE")
    print("=" * 70)


if __name__ == "__main__":
    main()
