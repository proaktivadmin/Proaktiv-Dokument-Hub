import asyncio

from sqlalchemy import text

from app.database import async_session_maker


async def count_templates():
    async with async_session_maker() as db:
        result = await db.execute(text("SELECT count(*) FROM templates;"))
        count = result.scalar()
        print(f"TEMPLATE_COUNT_DEBUG: {count}")

        # Also check created_at distribution to see if they are new or old
        result = await db.execute(text("SELECT created_at, title FROM templates ORDER BY created_at DESC LIMIT 5;"))
        rows = result.fetchall()
        print("\nLatest 5 Templates:")
        for row in rows:
            print(f"- {row[0]}: {row[1]}")


if __name__ == "__main__":
    asyncio.run(count_templates())
