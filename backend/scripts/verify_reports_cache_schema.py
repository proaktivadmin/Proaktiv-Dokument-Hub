"""
Verify reports cache schema for troubleshooting 500 errors on /api/reports/cache-events.

Run against Railway (use public DATABASE_URL):
    $env:DATABASE_URL = "postgresql://postgres:PASSWORD@shuttle.proxy.rlwy.net:51557/railway"
    cd backend
    python scripts/verify_reports_cache_schema.py

Or locally with docker compose:
    docker compose exec backend python scripts/verify_reports_cache_schema.py
"""

import asyncio
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text

from app.database import async_session_factory

REQUIRED_TABLES = [
    "report_sales_sync_events",
    "report_sales_estate_cache",
    "report_sales_transaction_cache",
    "report_sales_cache_state",
]

REQUIRED_COLUMNS = {
    "report_sales_sync_events": ["id", "installation_id", "department_id", "event_type", "payload", "created_at"],
    "report_sales_estate_cache": ["estate_key", "data_source", "brokers"],
    "report_sales_transaction_cache": ["transaction_key", "data_source"],
}


async def verify():
    db_url = os.environ.get("DATABASE_URL", "")
    if not db_url:
        print("ERROR: DATABASE_URL not set")
        sys.exit(1)
    # Mask password in output
    safe_url = db_url.split("@")[-1] if "@" in db_url else "(local)"
    print(f"Checking schema against: ...@{safe_url}\n")

    async with async_session_factory() as db:
        # 1. Alembic version
        try:
            result = await db.execute(text("SELECT version_num FROM alembic_version"))
            row = result.fetchone()
            version = row[0] if row else "unknown"
            print(f"Alembic version: {version}")
            if version != "20260312_0002":
                print(
                    "  WARNING: Expected 20260312_0002 (reports cache + data_source). "
                    "Run: python -m alembic upgrade head"
                )
        except Exception as e:
            print(f"Alembic version: ERROR - {e}")

        # 2. Table existence
        print("\nTables:")
        for table in REQUIRED_TABLES:
            result = await db.execute(
                text("SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = :t)"),
                {"t": table},
            )
            exists = result.scalar()
            status = "OK" if exists else "MISSING"
            print(f"  {table}: {status}")
            if not exists:
                print("    -> Migration 20260312_0001 may not be applied")

        # 3. Required columns
        print("\nRequired columns:")
        for table, cols in REQUIRED_COLUMNS.items():
            for col in cols:
                result = await db.execute(
                    text(
                        "SELECT EXISTS (SELECT 1 FROM information_schema.columns "
                        "WHERE table_name = :t AND column_name = :c)"
                    ),
                    {"t": table, "c": col},
                )
                exists = result.scalar()
                status = "OK" if exists else "MISSING"
                print(f"  {table}.{col}: {status}")
                if not exists and table.endswith("_cache") and col == "data_source":
                    print("    -> Migration 20260312_0002 may not be applied")

        # 4. Row count for sync_events (informational)
        try:
            result = await db.execute(text("SELECT COUNT(*) FROM report_sales_sync_events"))
            count = result.scalar()
            print(f"\nreport_sales_sync_events row count: {count}")
        except Exception as e:
            print(f"\nreport_sales_sync_events: ERROR - {e}")

    print("\nDone. If any MISSING, apply migrations manually to Railway (see .cursor/rules/database-migrations.mdc)")


if __name__ == "__main__":
    asyncio.run(verify())
