#!/usr/bin/env python3
"""Clean up base64 image data from database to free space."""

import asyncio
import os
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.pool import NullPool

async def cleanup():
    database_url = os.environ.get("DATABASE_URL")
    
    if not database_url:
        print("ERROR: DATABASE_URL not set")
        return
    
    # Convert to asyncpg format
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql+asyncpg://", 1)
    elif database_url.startswith("postgresql://"):
        database_url = database_url.replace("postgresql://", "postgresql+asyncpg://", 1)
    
    print("Connecting to database...")
    engine = create_async_engine(database_url, poolclass=NullPool)
    
    try:
        async with engine.begin() as conn:
            # Check current sizes
            result = await conn.execute(text("""
                SELECT 
                    'offices' as table_name,
                    COUNT(*) as rows,
                    pg_size_pretty(pg_total_relation_size('offices')) as size
                UNION ALL
                SELECT 
                    'employees' as table_name,
                    COUNT(*) as rows,
                    pg_size_pretty(pg_total_relation_size('employees')) as size
            """))
            print("\nTable sizes before cleanup:")
            for row in result.fetchall():
                print(f"  {row[0]}: {row[1]} rows, {row[2]}")
            
            # Clear base64 image data from offices - replace with proxy URLs
            result = await conn.execute(text("""
                UPDATE offices 
                SET banner_image_url = '/api/vitec/departments/' || vitec_department_id || '/picture'
                WHERE banner_image_url LIKE 'data:image%'
                AND vitec_department_id IS NOT NULL
            """))
            print(f"\n[OK] Converted {result.rowcount} office images to proxy URLs")
            
            # Clear offices without vitec_department_id
            result = await conn.execute(text("""
                UPDATE offices 
                SET banner_image_url = NULL 
                WHERE banner_image_url LIKE 'data:image%'
                AND vitec_department_id IS NULL
            """))
            print(f"[OK] Cleared {result.rowcount} office images (no vitec ID)")
            
            # Clear base64 image data from employees - replace with proxy URLs
            result = await conn.execute(text("""
                UPDATE employees 
                SET profile_image_url = '/api/vitec/employees/' || vitec_employee_id || '/picture'
                WHERE profile_image_url LIKE 'data:image%'
                AND vitec_employee_id IS NOT NULL
            """))
            print(f"[OK] Converted {result.rowcount} employee images to proxy URLs")
            
            # Clear employees without vitec_employee_id
            result = await conn.execute(text("""
                UPDATE employees 
                SET profile_image_url = NULL 
                WHERE profile_image_url LIKE 'data:image%'
                AND vitec_employee_id IS NULL
            """))
            print(f"[OK] Cleared {result.rowcount} employee images (no vitec ID)")
        
        # Run VACUUM outside transaction to reclaim space
        print("\nRunning VACUUM to reclaim disk space...")
        async with engine.connect() as conn:
            await conn.execute(text("COMMIT"))  # End any implicit transaction
            await conn.execute(text("VACUUM FULL offices"))
            print("[OK] Vacuumed offices table")
            await conn.execute(text("VACUUM FULL employees"))
            print("[OK] Vacuumed employees table")
        
        # Check sizes after cleanup
        async with engine.begin() as conn:
            result = await conn.execute(text("""
                SELECT 
                    'offices' as table_name,
                    COUNT(*) as rows,
                    pg_size_pretty(pg_total_relation_size('offices')) as size
                UNION ALL
                SELECT 
                    'employees' as table_name,
                    COUNT(*) as rows,
                    pg_size_pretty(pg_total_relation_size('employees')) as size
            """))
            print("\nTable sizes after cleanup:")
            for row in result.fetchall():
                print(f"  {row[0]}: {row[1]} rows, {row[2]}")
                
    except Exception as e:
        print(f"\n[ERROR] {e}")
        raise
    finally:
        await engine.dispose()
    
    print("\n[OK] Cleanup complete!")

if __name__ == "__main__":
    asyncio.run(cleanup())
