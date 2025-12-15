#!/usr/bin/env python3
"""Check template Azure URLs to see how many are real vs mock."""

import asyncio
import os
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession

async def main():
    db_url = os.environ.get('DATABASE_URL', 'postgresql+asyncpg://postgres:postgres@db:5432/dokument_hub')
    db_url = db_url.replace('postgresql://', 'postgresql+asyncpg://')
    
    engine = create_async_engine(db_url)
    
    async with AsyncSession(engine) as session:
        result = await session.execute(text("SELECT azure_blob_url FROM templates"))
        urls = [row[0] for row in result.fetchall()]
        
        azure_count = len([u for u in urls if u and u.startswith('https://')])
        mock_count = len([u for u in urls if u and u.startswith('mock://')])
        file_count = len([u for u in urls if u and u.startswith('file://')])
        other_count = len(urls) - azure_count - mock_count - file_count
        
        print(f"Total templates: {len(urls)}")
        print(f"  Azure (real uploads): {azure_count}")
        print(f"  Mock URLs: {mock_count}")
        print(f"  File URLs: {file_count}")
        print(f"  Other: {other_count}")
        
        if azure_count > 0:
            print("\nReal Azure URLs:")
            for u in urls:
                if u and u.startswith('https://'):
                    print(f"  {u[:100]}...")

if __name__ == "__main__":
    asyncio.run(main())

