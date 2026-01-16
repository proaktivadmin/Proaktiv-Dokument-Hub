#!/bin/bash
set -e

echo "🚀 Starting Proaktiv Dokument Hub Backend..."

# Skip PostgreSQL wait in SQLite mode or Railway (Railway's Postgres is always ready)
if [[ "$DATABASE_URL" == sqlite* ]]; then
    echo "📦 SQLite mode detected - skipping database wait"
elif [[ "$PLATFORM" == "railway" ]] || [[ "$RAILWAY_ENVIRONMENT" != "" ]]; then
    echo "🚂 Railway platform detected - Postgres is ready"
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

# Sync templates from Azure Blob Storage
echo "☁️ Syncing templates from Azure Storage..."
python -c "
import asyncio
import sys
import warnings
warnings.filterwarnings('ignore', category=DeprecationWarning)
sys.path.insert(0, '/app')

async def sync_templates():
    from app.database import async_session_factory
    from app.services.azure_storage_service import get_azure_storage_service
    from app.models.template import Template
    from sqlalchemy import select
    from pathlib import Path
    
    storage = get_azure_storage_service()
    
    if not storage.is_configured:
        print('⚠️ Azure Storage not configured, skipping sync')
        return
    
    blobs = await storage.list_blobs()
    print(f'Found {len(blobs)} blobs in Azure Storage')
    
    async with async_session_factory() as db:
        created = 0
        skipped = 0
        
        for blob in blobs:
            blob_name = blob['name']
            
            # Check if already exists
            existing = await db.execute(
                select(Template).where(Template.file_name == blob_name)
            )
            if existing.scalar_one_or_none():
                skipped += 1
                continue
            
            # Get file type
            file_ext = blob_name.split('.')[-1].lower() if '.' in blob_name else 'unknown'
            title = Path(blob_name).stem.replace('_', ' ').replace('-', ' ').title()
            
            # Download HTML content
            content = None
            if file_ext in ['html', 'htm']:
                content_bytes = await storage.download_file(blob_name)
                if content_bytes:
                    try:
                        content = content_bytes.decode('utf-8')
                    except UnicodeDecodeError:
                        content = content_bytes.decode('latin-1')
            
            # Create template
            template = Template(
                title=title,
                file_name=blob_name,
                file_type=file_ext,
                file_size_bytes=blob['size'] or 0,
                azure_blob_url=f'https://{storage.client.account_name}.blob.core.windows.net/templates/{blob_name}',
                azure_blob_container='templates',
                status='published',
                created_by='system@proaktiv.no',
                updated_by='system@proaktiv.no',
                content=content,
            )
            db.add(template)
            created += 1
        
        await db.commit()
        print(f'✅ Synced {created} templates, skipped {skipped} existing')

asyncio.run(sync_templates())
"

# Start the application
echo "🌐 Starting FastAPI server on port ${PORT:-8000}..."
exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}" "$@"
