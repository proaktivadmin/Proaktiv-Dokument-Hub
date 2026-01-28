"""
Seed Territory Data Script

Seeds postal codes from Bring API and office territories from CSV data.
Run with: python -m scripts.seed_territories
"""

import asyncio
import csv
import os
import sys
import uuid
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import async_session_factory
from app.models.office import Office
from app.models.office_territory import OfficeTerritory
from app.models.postal_code import PostalCode
from app.services.territory_service import PostalCodeService

# Source mappings from CSV columns to database source types
SOURCE_MAPPING = {
    "Tjenestetorget": "tjenestetorget",
    "Eiendomsmegler": "eiendomsmegler",
    "MeglerSmart": "meglersmart",
}

# Manual mapping from CSV office names to database office names
# CSV names use short form, database uses full legal names
CSV_TO_DB_OFFICE_MAPPING = {
    # Bergen region - map to Småstrandgaten (main Bergen office)
    "Proaktiv Bergen Sentrum": "Proaktiv Eiendomsmegling Småstrandgaten",
    # Trondheim region
    "Proaktiv Trondheim Sentrum": "Proaktiv Trondheim Sentrum",
    "Proaktiv Trondheim Syd": "Proaktiv Trondheim Syd",
    "Proaktiv Trondheim Øst": "Proaktiv Eiendomsmegling Moholt",  # Øst = Moholt
    # Rogaland region
    "Proaktiv Haugesund": "Proaktiv Eiendomsmegling Haugesund",
    "Proaktiv Jæren": "Proaktiv Eiendomsmegling Jæren",
    "Proaktiv Sandnes": "Proaktiv Eiendomsmegling Sandnes",
    "Proaktiv Sola": "Proaktiv Eiendomsmegling Sola",
    # Vestlandet
    "Proaktiv Voss": "Proaktiv Eiendomsmegling Voss",
    # Østlandet
    "Proaktiv Drammen, Lier & Holmestrand": "Proaktiv Drammen Lier Holmestrand",
    "Proaktiv Lillestrøm": "Proaktiv Lillestrøm",
    "Proaktiv Lørenskog": "Proaktiv Lørenskog",
    # Vestlandet/Others
    "Proaktiv Ålesund": "Proaktiv Ålesund",
    # Not in database - inactive
    # "Proaktiv Bodø": None,
}

# CSV file path
CSV_PATH = Path(r"C:\Users\Adrian\Documents\postalcode data\Alle_postnummer.csv")


async def get_office_mapping(db: AsyncSession) -> dict[str, str]:
    """Build a mapping of office names to office IDs."""
    result = await db.execute(select(Office.id, Office.name))
    offices = result.all()

    # Build mapping from database office names to IDs
    db_name_to_id = {}
    for office_id, name in offices:
        db_name_to_id[name] = str(office_id)
        db_name_to_id[name.lower().strip()] = str(office_id)

    # Build final mapping that includes CSV name -> database ID translation
    mapping = {}
    for csv_name, db_name in CSV_TO_DB_OFFICE_MAPPING.items():
        if db_name and db_name in db_name_to_id:
            mapping[csv_name] = db_name_to_id[db_name]
            mapping[csv_name.lower()] = db_name_to_id[db_name]

    # Also include direct database name mappings for any that match exactly
    for office_id, name in offices:
        mapping[name] = str(office_id)
        mapping[name.lower()] = str(office_id)

    return mapping


def normalize_office_name(name: str) -> str:
    """Normalize office name for matching."""
    if not name:
        return ""
    # Handle encoding issues with Norwegian characters (Latin-1 to proper UTF-8)
    replacements = {
        "ø": "ø",
        "Ø": "Ø",
        "å": "å",
        "Å": "Å",
        "æ": "æ",
        "Æ": "Æ",
    }
    for bad, good in replacements.items():
        name = name.replace(bad, good)
    return name.strip()


async def seed_postal_codes(db: AsyncSession) -> int:
    """Seed postal codes from Bring API."""
    print("📮 Syncing postal codes from Bring API...")
    try:
        result = await PostalCodeService.sync_from_bring(db)
        await db.commit()
        synced = result.get("synced", 0)
        print(f"  ✓ Synced {synced} postal codes")
        return synced
    except Exception as e:
        print(f"  ✗ Failed to sync postal codes: {e}")
        return 0


async def seed_territories_from_csv(db: AsyncSession, office_mapping: dict[str, str]) -> dict:
    """Seed office territories from CSV data."""
    print(f"\n📊 Reading CSV from: {CSV_PATH}")

    if not CSV_PATH.exists():
        print(f"  ✗ CSV file not found: {CSV_PATH}")
        return {"created": 0, "errors": 0}

    stats = {
        "created": 0,
        "skipped": 0,
        "errors": 0,
        "office_not_found": set(),
        "postal_not_found": set(),
    }

    territories_to_insert = []

    # Read CSV with ANSI encoding for Norwegian characters
    with open(CSV_PATH, encoding="latin-1") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    print(f"  Found {len(rows)} rows in CSV")

    # Get all existing postal codes for validation
    result = await db.execute(select(PostalCode.postal_code))
    valid_postal_codes = {row[0] for row in result.all()}
    print(f"  Found {len(valid_postal_codes)} valid postal codes in database")

    for row in rows:
        postal_code = row.get("Postnummer", "").strip()
        if not postal_code:
            continue

        # Validate postal code exists
        if postal_code not in valid_postal_codes:
            stats["postal_not_found"].add(postal_code)
            continue

        # Process each source column
        for csv_col, db_source in SOURCE_MAPPING.items():
            office_name = row.get(csv_col, "").strip()
            if not office_name:
                continue

            # Normalize and lookup office
            office_name = normalize_office_name(office_name)
            office_id = office_mapping.get(office_name) or office_mapping.get(office_name.lower())

            if not office_id:
                stats["office_not_found"].add(office_name)
                continue

            territories_to_insert.append(
                {
                    "id": str(uuid.uuid4()),
                    "office_id": office_id,
                    "postal_code": postal_code,
                    "source": db_source,
                    "priority": 1,
                    "is_blacklisted": False,
                }
            )

    # Batch insert with upsert (on conflict do nothing)
    if territories_to_insert:
        print(f"\n  Inserting {len(territories_to_insert)} territory assignments...")

        # Insert in batches of 500
        batch_size = 500
        for i in range(0, len(territories_to_insert), batch_size):
            batch = territories_to_insert[i : i + batch_size]
            stmt = pg_insert(OfficeTerritory).values(batch)
            stmt = stmt.on_conflict_do_nothing(index_elements=["office_id", "postal_code", "source"])
            await db.execute(stmt)
            stats["created"] += len(batch)
            print(f"    Inserted batch {i // batch_size + 1}...")

        await db.commit()

    # Report issues
    if stats["office_not_found"]:
        print(f"\n  ⚠ Offices not found in database ({len(stats['office_not_found'])}):")
        for name in sorted(stats["office_not_found"])[:10]:
            print(f"    - {name}")
        if len(stats["office_not_found"]) > 10:
            print(f"    ... and {len(stats['office_not_found']) - 10} more")

    if stats["postal_not_found"]:
        print(f"\n  ⚠ Postal codes not in database ({len(stats['postal_not_found'])}): ", end="")
        print(", ".join(sorted(stats["postal_not_found"])[:5]), "...")

    return stats


async def main():
    """Run the territory seeding script."""
    print("🌱 Territory Data Seeding Script")
    print("=" * 50)

    async with async_session_factory() as db:
        # Step 1: Sync postal codes from Bring
        postal_count = await seed_postal_codes(db)

        # Step 2: Build office mapping
        print("\n🏢 Loading office mapping...")
        office_mapping = await get_office_mapping(db)
        print(f"  Found {len(office_mapping) // 2} offices in database")

        if not office_mapping:
            print("  ✗ No offices found! Please seed offices first.")
            return

        # Step 3: Seed territories from CSV
        stats = await seed_territories_from_csv(db, office_mapping)

        # Summary
        print("\n" + "=" * 50)
        print("✅ Seeding Complete!")
        print(f"   Postal codes synced: {postal_count}")
        print(f"   Territories created: {stats['created']}")
        if stats["office_not_found"]:
            print(f"   ⚠ Offices not found: {len(stats['office_not_found'])}")


if __name__ == "__main__":
    asyncio.run(main())
