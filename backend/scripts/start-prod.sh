#!/bin/bash
set -e

echo "🚀 Starting Proaktiv Dokument Hub Backend..."

# Skip PostgreSQL wait in SQLite mode
if [[ "$DATABASE_URL" == sqlite* ]]; then
    echo "📦 SQLite mode detected - skipping database wait"
else
    echo "⏳ Waiting for PostgreSQL database..."
    while ! nc -z ${DB_HOST:-db} ${DB_PORT:-5432}; do
        sleep 1
    done
    echo "✅ Database is ready!"
fi

# Initialize database (creates tables for SQLite)
echo "📦 Initializing database..."
cd /app
python -c "
import asyncio
from app.database import init_db
asyncio.run(init_db())
print('✅ Database initialized!')
"

# Seed data if database is empty
echo "🌱 Checking if seeding is needed..."
python -c "
import asyncio
import sys
sys.path.insert(0, '/app')

async def check_and_seed():
    from app.database import async_session_factory
    from sqlalchemy import select, func
    from app.models.category import Category
    
    async with async_session_factory() as db:
        count = await db.scalar(select(func.count(Category.id)))
        if count == 0:
            print('Database is empty, seeding...')
            # Import and run seed functions
            from scripts.seed_data import seed_tags, seed_categories
            await seed_tags(db)
            await seed_categories(db)
            await db.commit()
            print('✅ Seed data created!')
        else:
            print(f'✅ Database already has {count} categories, skipping seed.')

asyncio.run(check_and_seed())
"

# Start the application
echo "🌐 Starting FastAPI server..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 "$@"
