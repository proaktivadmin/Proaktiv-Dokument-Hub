"""
Cleanup duplicate offices created by scraping vs Vitec Next sync.

Strategy:
1. Keep offices with vitec_department_id (from Vitec Next) as source of truth
2. Create missing Vitec offices that exist in Next but not in DB
3. Merge employees from scraped offices to Vitec offices
4. Delete scraped duplicates with 0 employees
5. Deactivate regional/parent offices that shouldn't show in main view
"""

import sys

sys.path.insert(0, ".")
import os
import uuid

from sqlalchemy import create_engine, text

# Use Railway DATABASE_URL
db_url = os.environ.get("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/dokument_hub")
engine = create_engine(db_url)

# Missing Vitec offices that need to be created first
# Format: (vitec_id, marketing_name, legal_name, org_number)
MISSING_VITEC_OFFICES = [
    (2400, "Proaktiv Kristiansand", "Proffmegleren AS", "933456056"),
]

# Mapping of scraped offices (no vitec_id) to their Vitec counterparts (with vitec_id)
# Format: "scraped_name": "vitec_office_name"
OFFICE_MERGES = {
    # Scraped office -> Vitec office to merge into
    "Proaktiv Eiendomsmegling Haugesund": "Proaktiv Haugesund",
    "Proaktiv Eiendomsmegling Jæren": "Proaktiv Jæren",
    "Proaktiv Eiendomsmegling Sandnes": "Proaktiv Sandnes",
    "Proaktiv Eiendomsmegling Sola": "Proaktiv Sola",
    "Proaktiv Eiendomsmegling Stavanger": "Proaktiv Stavanger",
    "Proaktiv Eiendomsmegling Voss": "Proaktiv Voss",
    "Proaktiv Eiendomsmegling Lillestrøm": "Proaktiv Lillestrøm",
    "Proaktiv Eiendomsmegling Lørenskog": "Proaktiv Lørenskog",
    "Proaktiv Eiendomsmegling Moholt": "Proaktiv Trondheim Øst",  # Moholt = Trondheim Øst
    "Proaktiv Trondheim Sentrum": "Proakiv Trondheim Sentrum",  # Typo in Vitec name!
    "Proaktiv Eiendomsmegling Sandviken": "Proaktiv Sandviken og Bergen Nord",
    "Proaktiv Eiendomsmegling Småstrandgaten": "Proaktiv Bergen Sentrum",
    "Proaktiv Eiendomsmegling Skien": "Proaktiv Skien",
    "Proaktiv Eiendomsmegling Kristiansand": "Proaktiv Kristiansand",  # New vitec 2400
    "Proaktiv Drammen Lier Holmestrand": "Proaktiv Drammen, Lier og Holmestrand",
    "Proaktiv Sarpsborg Næring": "Proaktiv Sarpsborg - Næring",
    "Aktiv Oppgjør As": "Aktiv oppgjør",
    "Proaktiv Gruppen As": "Proaktiv Gruppen",
    "Proaktiv Kjedeledelse": "Kjedeledelse",
    "Proaktiv Properties": "Proaktiv Briskeby",  # Legal name for Briskeby (vitec 1000)
}

# Offices to deactivate (not delete, but hide from main view)
OFFICES_TO_DEACTIVATE = [
    # Regional groupings (parent offices with no real employees)
    "Romerike",
    "Sør",
    "Sør-Rogaland",
    "Trøndelag",
    "Vest",
    "Øst",
    "Proaktiv",  # Generic parent
    "Kjedeledelse",
]

# Sub-offices that should remain as sub (already set, just verify)
SUB_OFFICES = [
    "Proaktiv Sarpsborg - Næring",
    "Proaktiv Sarpsborg Næringsoppgjør",
    "Proaktiv Skien - Næring",
    "Proaktiv Skien - Næringsoppgjør",
]

DRY_RUN = False  # Set to False to actually make changes

with engine.connect() as conn:
    print(f"{'=' * 60}")
    print(f"OFFICE CLEANUP SCRIPT (DRY_RUN={DRY_RUN})")
    print(f"{'=' * 60}\n")

    # Step 0: Create missing Vitec offices
    print("STEP 0: Create missing Vitec offices")
    print("-" * 50)

    for vitec_id, name, legal_name, org_number in MISSING_VITEC_OFFICES:
        # Check if already exists
        existing = conn.execute(
            text("SELECT id FROM offices WHERE vitec_department_id = :vitec_id"), {"vitec_id": vitec_id}
        ).first()

        if existing:
            print(f"  EXISTS: '{name}' (vitec_id={vitec_id})")
        else:
            # Generate short_code from name (e.g., "Proaktiv Kristiansand" -> "KRIST")
            short_code = name.replace("Proaktiv ", "").upper()[:5]
            print(f"  CREATE: '{name}' (vitec_id={vitec_id}, org={org_number}, code={short_code})")
            if not DRY_RUN:
                new_id = str(uuid.uuid4())
                conn.execute(
                    text("""
                    INSERT INTO offices (id, name, short_code, vitec_department_id, organization_number,
                                         legal_name, is_active, office_type, created_at, updated_at)
                    VALUES (:id, :name, :short_code, :vitec_id, :org_number, :legal_name, TRUE, 'main', NOW(), NOW())
                """),
                    {
                        "id": new_id,
                        "name": name,
                        "short_code": short_code,
                        "vitec_id": vitec_id,
                        "org_number": org_number,
                        "legal_name": legal_name,
                    },
                )

    # Step 1: Find and merge duplicate offices
    print("\nSTEP 1: Merge scraped offices into Vitec offices")
    print("-" * 50)

    for scraped_name, vitec_name in OFFICE_MERGES.items():
        # Find scraped office
        scraped = conn.execute(
            text(
                "SELECT id, name, employee_count FROM ("
                "  SELECT o.id, o.name, COUNT(e.id) as employee_count "
                "  FROM offices o LEFT JOIN employees e ON e.office_id = o.id "
                "  WHERE o.name = :name GROUP BY o.id"
                ") sub"
            ),
            {"name": scraped_name},
        ).first()

        if not scraped:
            continue

        if vitec_name is None:
            # Delete this office (it's not real)
            print(f"  DELETE: '{scraped_name}' (no Vitec equivalent)")
            if not DRY_RUN:
                # Move any employees first (shouldn't have any)
                conn.execute(text("DELETE FROM offices WHERE id = :id"), {"id": scraped.id})
            continue

        # Find Vitec office
        vitec = conn.execute(text("SELECT id, name FROM offices WHERE name = :name"), {"name": vitec_name}).first()

        if not vitec:
            print(f"  SKIP: '{scraped_name}' -> '{vitec_name}' (Vitec office not found)")
            continue

        print(f"  MERGE: '{scraped_name}' ({scraped.employee_count} emp) -> '{vitec_name}'")

        if not DRY_RUN:
            # Move employees to Vitec office
            conn.execute(
                text("UPDATE employees SET office_id = :vitec_id WHERE office_id = :scraped_id"),
                {"vitec_id": vitec.id, "scraped_id": scraped.id},
            )
            # Delete scraped office
            conn.execute(text("DELETE FROM offices WHERE id = :id"), {"id": scraped.id})

    # Step 2: Deactivate regional/parent offices
    print("\nSTEP 2: Deactivate regional/parent offices")
    print("-" * 50)

    for office_name in OFFICES_TO_DEACTIVATE:
        result = conn.execute(
            text("SELECT id, name, is_active FROM offices WHERE name = :name"), {"name": office_name}
        ).first()

        if result and result.is_active:
            print(f"  DEACTIVATE: '{office_name}'")
            if not DRY_RUN:
                conn.execute(text("UPDATE offices SET is_active = FALSE WHERE id = :id"), {"id": result.id})
        elif result:
            print(f"  ALREADY INACTIVE: '{office_name}'")

    # Step 3: Ensure sub-offices are marked correctly
    print("\nSTEP 3: Verify sub-office settings")
    print("-" * 50)

    for sub_name in SUB_OFFICES:
        result = conn.execute(
            text("SELECT id, name, office_type FROM offices WHERE name = :name"), {"name": sub_name}
        ).first()

        if result:
            if result.office_type != "sub":
                print(f"  SET SUB: '{sub_name}' (was {result.office_type})")
                if not DRY_RUN:
                    conn.execute(text("UPDATE offices SET office_type = 'sub' WHERE id = :id"), {"id": result.id})
            else:
                print(f"  OK: '{sub_name}' (already sub)")

    if not DRY_RUN:
        conn.commit()
        print(f"\n{'=' * 60}")
        print("CHANGES COMMITTED")
        print(f"{'=' * 60}")
    else:
        print(f"\n{'=' * 60}")
        print("DRY RUN - No changes made. Set DRY_RUN=False to apply.")
        print(f"{'=' * 60}")
