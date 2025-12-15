#!/usr/bin/env python3
"""
Upload unique files from company-portal/library to Azure and create template records.
Then report on completion for manual deletion.
"""

import asyncio
import os
import sys
import io
from pathlib import Path
from datetime import datetime, timezone

# Add parent to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from app.services.azure_storage_service import get_azure_storage_service
from app.services.sanitizer_service import get_sanitizer_service

# Files to upload (copied to temp_upload folder for Docker access)
FILES_TO_UPLOAD = [
    "/app/scripts/temp_upload/oppdra.html",
    "/app/scripts/temp_upload/oppdra.v2.html",
    "/app/scripts/temp_upload/oppdra.v3.html",
    "/app/scripts/temp_upload/oppdra.v4.html",
    "/app/scripts/temp_upload/OPPDRAGSAVTALE (TEST).html",
]

async def main():
    # Setup
    db_url = os.environ.get('DATABASE_URL', 'postgresql+asyncpg://postgres:postgres@db:5432/dokument_hub')
    db_url = db_url.replace('postgresql://', 'postgresql+asyncpg://')
    
    engine = create_async_engine(db_url)
    async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    
    storage = get_azure_storage_service()
    sanitizer = get_sanitizer_service()
    
    if not storage.is_configured:
        print("ERROR: Azure Storage not configured!")
        return
    
    print(f"Uploading {len(FILES_TO_UPLOAD)} files to Azure...")
    print("=" * 50)
    
    uploaded = 0
    failed = 0
    
    async with async_session() as session:
        for file_path in FILES_TO_UPLOAD:
            path = Path(file_path)
            
            if not path.exists():
                print(f"SKIP: {path.name} - File not found")
                continue
            
            try:
                # Read file
                try:
                    content = path.read_text(encoding='utf-8')
                except UnicodeDecodeError:
                    content = path.read_text(encoding='latin-1')
                
                file_size = path.stat().st_size
                
                # Sanitize HTML
                sanitized_content = sanitizer.sanitize(content)
                
                # Generate blob name
                timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
                blob_name = f"company-portal/{timestamp}_{path.name}"
                
                # Upload to Azure
                file_bytes = sanitized_content.encode('utf-8')
                blob_url = await storage.upload_file(
                    file_data=io.BytesIO(file_bytes),
                    blob_name=blob_name,
                    content_type='text/html'
                )
                
                if not blob_url:
                    print(f"FAIL: {path.name} - Upload failed")
                    failed += 1
                    continue
                
                # Create template record
                title = path.stem  # filename without extension
                
                await session.execute(
                    text("""
                        INSERT INTO templates (
                            id, title, file_name, file_type, file_size_bytes,
                            azure_blob_url, created_by, updated_by, description,
                            azure_blob_container, status, version, language, content
                        ) VALUES (
                            gen_random_uuid(), :title, :file_name, 'html', :file_size,
                            :blob_url, 'import@system', 'import@system', :description,
                            'templates', 'published', 1, 'nb-NO', :content
                        )
                    """),
                    {
                        'title': title,
                        'file_name': path.name,
                        'file_size': file_size,
                        'blob_url': blob_url,
                        'description': f'Imported from company-portal/library/{path.name}',
                        'content': sanitized_content
                    }
                )
                
                print(f"OK: {path.name} -> {blob_url[:60]}...")
                uploaded += 1
                
            except Exception as e:
                print(f"FAIL: {path.name} - {e}")
                failed += 1
        
        await session.commit()
    
    print("=" * 50)
    print(f"Uploaded: {uploaded}")
    print(f"Failed: {failed}")
    print("\nYou can now safely delete: C:\\Users\\Adrian\\Documents\\company-portal\\library")

if __name__ == "__main__":
    asyncio.run(main())

