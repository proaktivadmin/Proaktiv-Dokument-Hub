"""Fix database schema manually."""

import asyncio
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine


async def fix():
    # Detect and prefer public URL if running externally
    db_url = os.environ.get("DATABASE_PUBLIC_URL") or os.environ.get("DATABASE_URL")

    if not db_url:
        print("Error: No DATABASE_URL found in environment")
        return

    # Transform postgresql:// to postgresql+asyncpg:// for SQLAlchemy async
    if db_url.startswith("postgresql://") and not db_url.startswith("postgresql+asyncpg://"):
        db_url = db_url.replace("postgresql://", "postgresql+asyncpg://", 1)

    print(f"Connecting to: {db_url.split('@')[-1]}")

    engine = create_async_engine(db_url)
    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

    async with session_factory() as db:
        print("\n1. Fixing 'offices' table columns...")
        columns = [
            ("entra_group_id", "VARCHAR(64)"),
            ("entra_group_name", "VARCHAR(255)"),
            ("entra_group_mail", "VARCHAR(255)"),
            ("entra_group_description", "TEXT"),
            ("entra_sharepoint_url", "TEXT"),
            ("entra_member_count", "INTEGER"),
            ("entra_mismatch_fields", "JSONB NOT NULL DEFAULT '[]'::jsonb"),
            ("entra_last_synced_at", "TIMESTAMP WITH TIME ZONE"),
        ]

        for col_name, col_type in columns:
            try:
                await db.execute(text(f"ALTER TABLE offices ADD COLUMN IF NOT EXISTS {col_name} {col_type}"))
                print(f"  ✓ Processed {col_name}")
            except Exception as e:
                print(f"  ✗ Error adding {col_name}: {e}")

        print("\n2. Updating 'office_territories' source check constraint...")
        try:
            # Drop existing constraint
            await db.execute(
                text(
                    "ALTER TABLE office_territories DROP CONSTRAINT IF EXISTS ck_office_territories_ck_office_territories_source"
                )
            )

            # Add new constraint with all sources
            sources = [
                "vitec_next",
                "finn",
                "anbudstjenester",
                "homepage",
                "other",
                "tjenestetorget",
                "eiendomsmegler",
                "meglersmart",
            ]
            sources_str = ", ".join([f"'{s}'" for s in sources])
            await db.execute(
                text(
                    f"ALTER TABLE office_territories ADD CONSTRAINT ck_office_territories_ck_office_territories_source CHECK (source IN ({sources_str}))"
                )
            )

            print("  ✓ Updated source check constraint")
        except Exception as e:
            print(f"  ✗ Error updating check constraint: {e}")

        await db.commit()
        print("\n✅ Schema fixes applied successfully.")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(fix())
