"""Check database schema for offices."""

import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text

from app.database import async_session_factory


async def check():
    async with async_session_factory() as db:
        print("Checking columns for 'offices'...")
        result = await db.execute(
            text("SELECT column_name FROM information_schema.columns WHERE table_name = 'offices'")
        )
        rows = result.fetchall()
        print(f"Found {len(rows)} columns:")
        for row in rows:
            print(f"  - {row[0]}")


if __name__ == "__main__":
    asyncio.run(check())
