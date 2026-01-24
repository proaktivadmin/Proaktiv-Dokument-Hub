"""
Complete cleanup to use Vitec Next as the single source of truth.

This script:
1. Migrates employees from orphaned offices to Vitec offices
2. Deletes orphaned offices (from proaktiv.no scraping)
3. Removes employees without Vitec IDs (scraped, not in Vitec)
4. Tags specific emails as external developers (keep in system but exclude from sync)

Run with --dry-run first to preview changes.

Usage:
    python scripts/cleanup_to_vitec_truth.py --dry-run  # Preview
    python scripts/cleanup_to_vitec_truth.py            # Execute
"""

import argparse
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# =============================================================================
# OFFICE MAPPING: orphan office name -> Vitec office name
# =============================================================================
OFFICE_MAPPING = {
    "Aktiv Oppgjør As": "Aktiv oppgjør",
    "Proaktiv Gruppen As": "Proaktiv Gruppen",
    "Proaktiv Trondheim Sentrum": "Proakiv Trondheim Sentrum",  # Note: Vitec has typo
    "Proaktiv Properties": "Proaktiv Briskeby",
    "Proaktiv Eiendomsmegling Haugesund": "Proaktiv Haugesund",
    "Proaktiv Eiendomsmegling Jæren": "Proaktiv Jæren",
    "Proaktiv Eiendomsmegling Kristiansand": "Sør",  # Kristiansand -> Sør region
    "Proaktiv Eiendomsmegling Lillestrøm": "Proaktiv Lillestrøm",
    "Proaktiv Eiendomsmegling Lørenskog": "Proaktiv Lørenskog",
    "Proaktiv Eiendomsmegling Moholt": "Proaktiv Trondheim Øst",
    "Proaktiv Eiendomsmegling Sandnes": "Proaktiv Sandnes",
    "Proaktiv Eiendomsmegling Sandviken": "Proaktiv Sandviken og Bergen Nord",
    "Proaktiv Eiendomsmegling Skien": "Proaktiv Skien",
    "Proaktiv Eiendomsmegling Småstrandgaten": "Proaktiv Bergen Sentrum",
    "Proaktiv Eiendomsmegling Sola": "Proaktiv Sola",
    "Proaktiv Eiendomsmegling Stavanger": "Proaktiv Stavanger",
    "Proaktiv Eiendomsmegling Voss": "Proaktiv Voss",
    "Proaktiv Drammen Lier Holmestrand": "Proaktiv Drammen, Lier og Holmestrand",
    "Proaktiv Sarpsborg Næring": "Proaktiv Sarpsborg - Næring",
    "Kjedeledelse": None,
    "Proaktiv Kjedeledelse": None,
}

# =============================================================================
# EXTERNAL DEVELOPERS: emails to tag as external (keep but exclude from sync)
# =============================================================================
EXTERNAL_DEVELOPERS = {
    # Format: "email@domain.com": ("Company Name", "Office to assign")
    # Add your external developer emails here
    # Example: "developer@agency.com": ("Digital Agency AS", "Proaktiv Gruppen"),
}

# =============================================================================
# EMPLOYEE MERGE: scraped email -> Vitec email (same person, different email)
# These will be merged (scraped record deleted, Vitec record kept)
# =============================================================================
EMPLOYEE_MERGE = {
    # Scraped email -> Vitec email (same person)
    "elisabeth@proaktiv.no": "ebn@proaktiv.no",  # Elisabeth Brenne Nilsson
    "mk@proaktiv.no": "mads@proaktiv.no",  # Mads Kirkeslett
    "camilla@proaktiv.no": "camilla.krokeide@proaktiv.no",  # Camilla Krokeide
    "jorgen@proaktiv.no": "jorgen.molvik@proaktiv.no",  # Jørgen Molvik
}

# =============================================================================
# EMPLOYEES MISSING FROM VITEC: Real employees that need to be added to Vitec Next
# These will NOT be deleted - instead flagged for manual addition to Vitec
# =============================================================================
EMPLOYEES_MISSING_FROM_VITEC = [
    # These employees are real but not in Vitec Next - need to be added there
    "geir@proaktiv.no",  # Geir Flaa Johansen - not in Vitec
    "kg@proaktiv.no",  # Kristin Gåsland - not in Vitec
    "asbjorn@proaktiv.no",  # Asbjørn Svaland - not in Vitec
    "vvi@proaktiv.no",  # Veslemøy Vidvei Isaksen - not in Vitec
]

# =============================================================================
# UNIDENTIFIED: Scraped employees to check manually against homepage
# =============================================================================
UNIDENTIFIED_EMPLOYEES = [
    # These may be old accounts that should be hidden/removed from homepage
    "hh@proa.no",  # Henrik Hammersborg
    "sm@proaktiv.no",  # Sofie Johanne Berge Matthiesen
    "kks@proaktiv.no",  # Knut Kristian Schatvet
    "line.skancke@azets.com",  # Line Skancke (regnskapsfører)
    "Gs@proa.no",  # Grunde Skillebekk
    "klaus.westersund@proaktiv.no",  # Klaus Westersund
    "owl@proaktiv.no",  # Ole Westfal-Larsen
]


def cleanup_to_vitec_truth(dry_run: bool = True):
    db_url = os.environ.get("DATABASE_URL")
    if not db_url:
        print("ERROR: DATABASE_URL not set")
        sys.exit(1)

    engine = create_engine(db_url)
    Session = sessionmaker(bind=engine)

    with Session() as session:
        print("=" * 70)
        print("VITEC NEXT AS SINGLE SOURCE OF TRUTH - CLEANUP")
        print("=" * 70)
        print(f"Mode: {'DRY RUN (no changes)' if dry_run else 'LIVE (applying changes)'}")
        print()

        # Build lookup of Vitec offices by name (case-insensitive)
        result = session.execute(
            text("""
            SELECT id, name FROM offices WHERE vitec_department_id IS NOT NULL
        """)
        )
        vitec_office_lookup = {row[1].lower(): row[0] for row in result}

        # =================================================================
        # STEP 1: Migrate employees from orphaned offices to Vitec offices
        # =================================================================
        print("STEP 1: Migrate employees from orphaned offices")
        print("-" * 50)

        result = session.execute(
            text("""
            SELECT o.id, o.name, COUNT(e.id) as emp_count
            FROM offices o
            LEFT JOIN employees e ON e.office_id::uuid = o.id
            WHERE o.vitec_department_id IS NULL
            GROUP BY o.id, o.name
            ORDER BY o.name
        """)
        )
        orphan_offices = [(row[0], row[1], row[2]) for row in result]

        migrated_employees = 0
        deleted_offices = 0

        for orphan_id, orphan_name, emp_count in orphan_offices:
            target_name = OFFICE_MAPPING.get(orphan_name)

            if target_name is None:
                if emp_count > 0:
                    print(f"  [WARN] {orphan_name} ({emp_count} emp) - no mapping, employees will be orphaned")
                else:
                    print(f"  [DEL] {orphan_name} (no Vitec equivalent)")
                    if not dry_run:
                        session.execute(text("DELETE FROM offices WHERE id = :id"), {"id": orphan_id})
                    deleted_offices += 1
                continue

            target_id = vitec_office_lookup.get(target_name.lower())
            if not target_id:
                print(f"  [ERR] {orphan_name} -> {target_name} (target not found!)")
                continue

            if emp_count > 0:
                print(f"  [MIG] {orphan_name} -> {target_name} ({emp_count} emp)")
                if not dry_run:
                    session.execute(
                        text("""
                        UPDATE employees SET office_id = :target_id
                        WHERE office_id::uuid = :orphan_id
                    """),
                        {"target_id": str(target_id), "orphan_id": orphan_id},
                    )
                migrated_employees += emp_count
            else:
                print(f"  [DEL] {orphan_name} (0 emp, duplicate)")

            if not dry_run:
                session.execute(text("DELETE FROM offices WHERE id = :id"), {"id": orphan_id})
            deleted_offices += 1

        print()
        print(f"  Employees migrated: {migrated_employees}")
        print(f"  Offices deleted: {deleted_offices}")
        print()

        # =================================================================
        # STEP 2: Tag external developers
        # =================================================================
        print("STEP 2: Tag external developers")
        print("-" * 50)

        # Check if employee_type column exists (migration may not have run yet)
        has_employee_type = False
        try:
            session.execute(text("SELECT employee_type FROM employees LIMIT 1"))
            has_employee_type = True
        except Exception:
            session.rollback()

        tagged_external = 0
        for email, (company, office_name) in EXTERNAL_DEVELOPERS.items():
            result = session.execute(
                text("""
                SELECT id, first_name, last_name FROM employees WHERE LOWER(email) = LOWER(:email)
            """),
                {"email": email},
            )
            row = result.fetchone()

            if row:
                print(f"  [TAG] {row[1]} {row[2]} <{email}> -> external ({company})")
                if not dry_run and has_employee_type:
                    # Tag as external
                    session.execute(
                        text("""
                        UPDATE employees
                        SET employee_type = 'external', external_company = :company
                        WHERE id = :id
                    """),
                        {"id": row[0], "company": company},
                    )

                    # Optionally move to a specific office
                    if office_name:
                        target_id = vitec_office_lookup.get(office_name.lower())
                        if target_id:
                            session.execute(
                                text("""
                                UPDATE employees SET office_id = :office_id WHERE id = :id
                            """),
                                {"office_id": str(target_id), "id": row[0]},
                            )
                elif not has_employee_type:
                    print("    (employee_type column doesn't exist - run migration first)")
                tagged_external += 1
            else:
                print(f"  [SKIP] {email} (not found)")

        if not EXTERNAL_DEVELOPERS:
            print("  (no external developers configured)")

        print()
        print(f"  Tagged as external: {tagged_external}")
        print()

        # =================================================================
        # STEP 3: Merge duplicate employees (same person, different email)
        # =================================================================
        print("STEP 3: Merge duplicate employees")
        print("-" * 50)

        merged_employees = 0
        for scraped_email, vitec_email in EMPLOYEE_MERGE.items():
            # Find both records
            result = session.execute(
                text("""
                SELECT id, first_name, last_name FROM employees
                WHERE LOWER(email) = LOWER(:email)
            """),
                {"email": scraped_email},
            )
            scraped_row = result.fetchone()

            result = session.execute(
                text("""
                SELECT id, first_name, last_name, vitec_employee_id FROM employees
                WHERE LOWER(email) = LOWER(:email)
            """),
                {"email": vitec_email},
            )
            vitec_row = result.fetchone()

            if scraped_row and vitec_row:
                print(
                    f"  [MERGE] {scraped_row[1]} {scraped_row[2]} <{scraped_email}> -> <{vitec_email}> (ID: {vitec_row[3]})"
                )
                if not dry_run:
                    session.execute(text("DELETE FROM employees WHERE id = :id"), {"id": scraped_row[0]})
                merged_employees += 1
            elif scraped_row and not vitec_row:
                print(f"  [SKIP] {scraped_row[1]} {scraped_row[2]} <{scraped_email}> - Vitec record not found")
            elif not scraped_row:
                print(f"  [SKIP] {scraped_email} - scraped record not found (already cleaned?)")

        print()
        print(f"  Merged (duplicates removed): {merged_employees}")
        print()

        # =================================================================
        # STEP 4: Flag employees missing from Vitec (keep but report)
        # =================================================================
        print("STEP 4: Employees missing from Vitec (need to add to Vitec Next)")
        print("-" * 50)

        missing_from_vitec = 0
        for email in EMPLOYEES_MISSING_FROM_VITEC:
            result = session.execute(
                text("""
                SELECT id, first_name, last_name FROM employees
                WHERE LOWER(email) = LOWER(:email)
            """),
                {"email": email},
            )
            row = result.fetchone()
            if row:
                print(f"  [KEEP] {row[1]} {row[2]} <{email}> - ADD TO VITEC NEXT")
                missing_from_vitec += 1

        if missing_from_vitec == 0:
            print("  (none)")

        print()
        print(f"  Missing from Vitec (kept): {missing_from_vitec}")
        print()

        # =================================================================
        # STEP 5: Report unidentified employees (to check manually)
        # =================================================================
        print("STEP 5: Unidentified employees (check homepage manually)")
        print("-" * 50)

        unidentified_count = 0
        deleted_unidentified = 0
        for email in UNIDENTIFIED_EMPLOYEES:
            result = session.execute(
                text("""
                SELECT id, first_name, last_name FROM employees
                WHERE LOWER(email) = LOWER(:email)
            """),
                {"email": email},
            )
            row = result.fetchone()
            if row:
                print(f"  [DEL] {row[1]} {row[2]} <{email}> - check if visible on homepage")
                if not dry_run:
                    session.execute(text("DELETE FROM employees WHERE id = :id"), {"id": row[0]})
                deleted_unidentified += 1
                unidentified_count += 1

        if unidentified_count == 0:
            print("  (none)")

        print()
        print(f"  Unidentified deleted: {deleted_unidentified}")
        print()

        # =================================================================
        # STEP 6: Check for any remaining orphan employees
        # =================================================================
        print("STEP 6: Remaining orphan employees (unexpected)")
        print("-" * 50)

        # Check if employee_type column exists
        has_employee_type = False
        try:
            session.execute(text("SELECT employee_type FROM employees LIMIT 1"))
            has_employee_type = True
        except Exception:
            session.rollback()

        # Find any remaining employees without Vitec IDs that aren't in our lists
        all_known_emails = set(EMPLOYEE_MERGE.keys()) | set(EMPLOYEES_MISSING_FROM_VITEC) | set(UNIDENTIFIED_EMPLOYEES)

        result = session.execute(
            text("""
            SELECT e.id, e.first_name, e.last_name, e.email
            FROM employees e
            WHERE e.vitec_employee_id IS NULL
            ORDER BY e.last_name, e.first_name
        """)
        )

        remaining_orphans = 0
        for row in result:
            email_lower = row[3].lower() if row[3] else ""
            if email_lower not in [e.lower() for e in all_known_emails]:
                print(f"  [UNEXPECTED] {row[1]} {row[2]} <{row[3]}>")
                remaining_orphans += 1

        if remaining_orphans == 0:
            print("  (none - all accounted for)")

        print()
        print(f"  Unexpected orphans: {remaining_orphans}")

        # =================================================================
        # COMMIT
        # =================================================================
        if not dry_run:
            session.commit()
            print("=" * 70)
            print("CHANGES COMMITTED")

        # =================================================================
        # SUMMARY
        # =================================================================
        print("=" * 70)
        print("SUMMARY")
        print("=" * 70)

        # Final counts
        result = session.execute(text("SELECT COUNT(*) FROM offices"))
        office_count = result.scalar()

        result = session.execute(text("SELECT COUNT(*) FROM offices WHERE vitec_department_id IS NOT NULL"))
        vitec_office_count = result.scalar()

        result = session.execute(text("SELECT COUNT(*) FROM employees"))
        emp_count = result.scalar()

        result = session.execute(text("SELECT COUNT(*) FROM employees WHERE vitec_employee_id IS NOT NULL"))
        vitec_emp_count = result.scalar()

        try:
            result = session.execute(text("SELECT COUNT(*) FROM employees WHERE employee_type = 'external'"))
            external_emp_count = result.scalar()
        except Exception:
            external_emp_count = 0

        print(f"Offices:            {office_count} ({vitec_office_count} with Vitec ID)")
        print(f"Employees:          {emp_count} ({vitec_emp_count} with Vitec ID, {external_emp_count} external)")
        print()
        print("Actions taken:")
        print(f"  - Employees migrated to Vitec offices: {migrated_employees}")
        print(f"  - Orphan offices deleted: {deleted_offices}")
        print(f"  - Employees tagged as external: {tagged_external}")
        print(f"  - Duplicate employees merged: {merged_employees}")
        print(f"  - Unidentified employees deleted: {deleted_unidentified}")
        print(f"  - Missing from Vitec (kept): {missing_from_vitec}")
        print(f"  - Unexpected orphans: {remaining_orphans}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Cleanup to Vitec as single source of truth")
    parser.add_argument("--dry-run", action="store_true", help="Preview changes only")
    args = parser.parse_args()

    cleanup_to_vitec_truth(dry_run=args.dry_run)
