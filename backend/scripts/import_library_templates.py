#!/usr/bin/env python3
"""
Script to import all HTML templates from the library folder into the database.
Run this inside the backend container or with the correct environment.
"""
import asyncio
import os
from pathlib import Path
from uuid import uuid4
from datetime import datetime, timezone

# Add parent directory to path for imports
import sys
sys.path.insert(0, '/app')

from sqlalchemy import text
from app.database import async_session_factory


LIBRARY_PATH = Path("/app/library")


async def import_templates():
    """Import all HTML templates from the library folder."""
    
    if not LIBRARY_PATH.exists():
        print(f"Library path not found: {LIBRARY_PATH}")
        print("Make sure the library folder is mounted in the container.")
        return
    
    # Find all HTML files
    html_files = list(LIBRARY_PATH.rglob("*.html"))
    print(f"Found {len(html_files)} HTML files in {LIBRARY_PATH}")
    
    async with async_session_factory() as session:
        # Get existing templates to avoid duplicates
        result = await session.execute(text("SELECT file_name FROM templates"))
        existing_files = {row[0] for row in result.fetchall()}
        print(f"Found {len(existing_files)} existing templates in database")
        
        imported = 0
        skipped = 0
        
        for html_file in html_files:
            file_name = html_file.name
            
            # Skip if already exists
            if file_name in existing_files:
                print(f"  Skipping (exists): {file_name}")
                skipped += 1
                continue
            
            try:
                # Read file content
                content = html_file.read_text(encoding='utf-8')
                file_size = html_file.stat().st_size
                
                # Create title from filename (remove extension, clean up)
                title = html_file.stem
                
                # Get relative path for description
                rel_path = html_file.relative_to(LIBRARY_PATH)
                category_hint = str(rel_path.parent) if rel_path.parent != Path('.') else None
                description = f"Importert fra library/{rel_path}"
                
                # Insert into database
                template_id = str(uuid4())
                now = datetime.now(timezone.utc)
                
                await session.execute(
                    text("""
                        INSERT INTO templates (
                            id, title, description, file_name, file_type, 
                            file_size_bytes, azure_blob_url, status, 
                            created_by, updated_by, created_at, updated_at, content
                        ) VALUES (
                            :id, :title, :description, :file_name, :file_type,
                            :file_size, :blob_url, :status,
                            :created_by, :updated_by, :created_at, :updated_at, :content
                        )
                    """),
                    {
                        "id": template_id,
                        "title": title,
                        "description": description,
                        "file_name": file_name,
                        "file_type": "html",
                        "file_size": file_size,
                        "blob_url": f"file://library/{rel_path}",
                        "status": "published",
                        "created_by": "system@import",
                        "updated_by": "system@import",
                        "created_at": now,
                        "updated_at": now,
                        "content": content,
                    }
                )
                
                print(f"  Imported: {title}")
                imported += 1
                
            except Exception as e:
                print(f"  Error importing {file_name}: {e}")
        
        await session.commit()
        print(f"\nDone! Imported {imported} templates, skipped {skipped} duplicates.")


if __name__ == "__main__":
    asyncio.run(import_templates())

