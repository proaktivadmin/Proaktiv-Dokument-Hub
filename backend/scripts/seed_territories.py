"""
Seed Territory Data Script

Seeds office territories from CSV data.
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
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.models.office import Office
from app.models.office_territory import OfficeTerritory
from app.models.postal_code import PostalCode


# Use a custom setup for the engine to handle public/private URLs
def get_engine_and_session():
    db_url = os.environ.get("DATABASE_PUBLIC_URL") or os.environ.get("DATABASE_URL")

    if not db_url:
        raise RuntimeError("No DATABASE_URL found in environment")

    # Transform postgresql:// to postgresql+asyncpg:// for SQLAlchemy async
    if db_url.startswith("postgresql://") and not db_url.startswith("postgresql+asyncpg://"):
        db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)

    print(f"Connecting to: {db_url.split('@')[-1]}")

    engine = create_async_engine(db_url)
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    return engine, session_factory


# Source mappings from CSV columns to database source types
SOURCE_MAPPING = {
    "Tjenestetorget": "tjenestetorget",
    "Eiendomsmegler": "eiendomsmegler",
    "MeglerSmart": "meglersmart",
}

# Manual mapping from CSV office names to database office names
CSV_TO_DB_OFFICE_MAPPING = {
    "Proaktiv Bergen Sentrum": "Proaktiv Eiendomsmegling Småstrandgaten",
    "Proaktiv Trondheim Sentrum": "Proaktiv Trondheim Sentrum",
    "Proaktiv Trondheim Syd": "Proaktiv Trondheim Syd",
    "Proaktiv Trondheim Øst": "Proaktiv Eiendomsmegling Moholt",
    "Proaktiv Haugesund": "Proaktiv Eiendomsmegling Haugesund",
    "Proaktiv Jæren": "Proaktiv Eiendomsmegling Jæren",
    "Proaktiv Sandnes": "Proaktiv Eiendomsmegling Sandnes",
    "Proaktiv Sola": "Proaktiv Eiendomsmegling Sola",
    "Proaktiv Voss": "Proaktiv Eiendomsmegling Voss",
    "Proaktiv Drammen, Lier & Holmestrand": "Proaktiv Drammen Lier Holmestrand",
    "Proaktiv Lillestrøm": "Proaktiv Lillestrøm",
    "Proaktiv Lørenskog": "Proaktiv Lørenskog",
    "Proaktiv Ålesund": "Proaktiv Ålesund",
}

# CSV file path - Try relative first, then absolute
CSV_PATH = Path("backend/scripts/Alle_postnummer.csv")
if not CSV_PATH.exists():
    CSV_PATH = Path("scripts/Alle_postnummer.csv")
if not CSV_PATH.exists():
    CSV_PATH = Path(r"C:\Users\Adrian\Documents\postalcode data\Alle_postnummer.csv")


async def get_office_mapping(db: AsyncSession) -> dict[str, str]:
    """Build a mapping of office names to office IDs."""
    result = await db.execute(select(Office.id, Office.name))
    offices = result.all()

    mapping = {}
    db_name_to_id = {name: str(office_id) for office_id, name in offices}
    db_name_to_id.update({name.lower().strip(): str(office_id) for office_id, name in offices})

    for csv_name, db_name in CSV_TO_DB_OFFICE_MAPPING.items():
        if db_name in db_name_to_id:
            mapping[csv_name] = db_name_to_id[db_name]
            mapping[csv_name.lower()] = db_name_to_id[db_name]

    for office_id, name in offices:
        mapping[name] = str(office_id)
        mapping[name.lower()] = str(office_id)

    return mapping


def normalize_office_name(name: str) -> str:
    """Normalize office name for matching."""
    if not name:
        return ""
    return name.strip()


async def seed_territories_from_csv(db: AsyncSession, office_mapping: dict[str, str]) -> dict:
    """Seed office territories from CSV data."""
    print(f"\n📊 Reading CSV from: {CSV_PATH}")

    if not CSV_PATH.exists():
        print(f"  ✗ CSV file not found: {CSV_PATH}")
        return {"created": 0, "errors": 0}

    stats = {"created": 0, "skipped": 0, "errors": 0, "office_not_found": set(), "postal_not_found": set()}
    territories_to_insert = []

    with open(CSV_PATH, encoding="latin-1") as f:
        rows = list(csv.DictReader(f))

    print(f"  Found {len(rows)} rows in CSV")

    # Get all existing postal codes for validation
    result = await db.execute(select(PostalCode.postal_code))
    valid_postal_codes = {row[0] for row in result.all()}
    print(f"  Found {len(valid_postal_codes)} valid postal codes in database")

    for row in rows:
        postal_code = row.get("Postnummer", "").strip()
        if not postal_code or postal_code not in valid_postal_codes:
            if postal_code:
                stats["postal_not_found"].add(postal_code)
            continue

        for csv_col, db_source in SOURCE_MAPPING.items():
            office_name = normalize_office_name(row.get(csv_col, ""))
            if not office_name:
                continue

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

    if territories_to_insert:
        print(f"\n  Inserting {len(territories_to_insert)} territory assignments...")
        batch_size = 500
        for i in range(0, len(territories_to_insert), batch_size):
            batch = territories_to_insert[i : i + batch_size]
            stmt = pg_insert(OfficeTerritory).values(batch)
            stmt = stmt.on_conflict_do_nothing(index_elements=["office_id", "postal_code", "source"])
            await db.execute(stmt)
            stats["created"] += len(batch)
            print(f"    Inserted batch {i // batch_size + 1}...")
        await db.commit()

    return stats


async def main():
    """Run the territory seeding script."""
    print("🌱 Territory Data Seeding Script (Production Ready)")
    print("=" * 60)

    try:
        engine, session_factory = get_engine_and_session()
    except Exception as e:
        print(f"✗ Configuration error: {e}")
        return

    async with session_factory() as db:
        # SKIP postal logic as it's already verified in prod
        print("📮 Skipping postal code sync (already verified in prod)")

        print("\n🏢 Loading office mapping...")
        office_mapping = await get_office_mapping(db)
        print(f"  Found {len(office_mapping) // 2} offices in database")

        if not office_mapping:
            print("  ✗ No offices found! Please seed offices first.")
            return

        stats = await seed_territories_from_csv(db, office_mapping)

        print("\n" + "=" * 60)
        print("✅ Seeding Complete!")
        print(f"   Territories processed: {stats['created']}")
        if stats["office_not_found"]:
            print(f"   ⚠ Offices not found: {len(stats['office_not_found'])}")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
