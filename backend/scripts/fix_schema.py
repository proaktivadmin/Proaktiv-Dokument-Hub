"""Fix database schema manually."""

import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text

from app.database import async_session_factory


async def fix():
    async with async_session_factory() as db:
        print("Manually adding missing columns to 'offices'...")

        # Columns to add
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
                print(f"  Added {col_name}")
            except Exception as e:
                print(f"  Error adding {col_name}: {e}")

        await db.commit()
        print("Schema fix applied.")


if __name__ == "__main__":
    asyncio.run(fix())
