"""
Sync Norwegian postal codes from Bring Postnummerregister.

Run with: python -m scripts.sync_postal_codes
"""

import asyncio
import os
import sys

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

from app.database import async_engine
from app.services.territory_service import PostalCodeService


async def sync_postal_codes() -> None:
    async_session = sessionmaker(async_engine, class_=AsyncSession, expire_on_commit=False)

    async with async_session() as session:
        result = await PostalCodeService.sync_from_bring(session)
        await session.commit()
        message = result.get("message", "Sync completed")
        synced = result.get("synced", 0)
        print(f"[PostalCode Sync] {message} (synced={synced})")


if __name__ == "__main__":
    asyncio.run(sync_postal_codes())
