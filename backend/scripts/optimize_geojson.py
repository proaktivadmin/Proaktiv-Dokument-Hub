import asyncio
import json
import os
import sys
from pathlib import Path

# Add backend to path
sys.path.append(os.path.join(os.getcwd(), "backend"))

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine


async def process_geojson():
    # 1. Get database connection
    db_url = os.environ.get("DATABASE_PUBLIC_URL") or os.environ.get("DATABASE_URL")
    if not db_url:
        print("Error: No DATABASE_URL found in environment")
        return

    if db_url.startswith("postgresql://") and not db_url.startswith("postgresql+asyncpg://"):
        db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)

    print("Connecting to database...")
    engine = create_async_engine(db_url)
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    from app.models.office_territory import OfficeTerritory

    async with session_factory() as db:
        # Get unique postal codes from territories
        result = await db.execute(select(OfficeTerritory.postal_code).distinct())
        used_postal_codes = {row[0] for row in result.all()}
        print(f"Found {len(used_postal_codes)} unique postal codes with assignments.")

    await engine.dispose()

    # 2. Process the large JSON file
    src_path = Path("c:/Users/Adrian/Documents/Proaktiv-Dokument-Hub/frontend/public/postal-codes.json")
    dst_path = Path("c:/Users/Adrian/Documents/Proaktiv-Dokument-Hub/frontend/public/territory-geometry.json")

    if not src_path.exists():
        print(f"Error: Source file {src_path} not found")
        return

    print(f"Reading {src_path}...")
    with open(src_path, encoding="utf-8") as f:
        full_data = json.load(f)

    print("Extracting relevant geometries...")
    subset = {}
    missing = []

    for pc in used_postal_codes:
        # Normalize postal code (leading zeros might be missing in some datasets)
        pc_str = str(pc).zfill(4)
        if pc_str in full_data:
            pc_data = full_data[pc_str]
            if "geojson" in pc_data and pc_data["geojson"]:
                subset[pc_str] = pc_data["geojson"]
            else:
                missing.append(pc_str)
        else:
            missing.append(pc_str)

    print(f"Successfully extracted {len(subset)} geometries.")
    if missing:
        print(f"Missing geometries for {len(missing)} postal codes (e.g., {missing[:5]})")

    # 3. Save as a lighter file (just a mapping of PC to GeoJSON)
    print(f"Saving to {dst_path}...")
    with open(dst_path, "w", encoding="utf-8") as f:
        json.dump(subset, f)

    print("Done!")


if __name__ == "__main__":
    asyncio.run(process_geojson())
