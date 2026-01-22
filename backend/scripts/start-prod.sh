#!/bin/bash
set -e

echo "🚀 Starting Proaktiv Dokument Hub Backend..."

cd /app

# Wait for database if using Postgres (with actual connection test, not just socket)
echo "⏳ Waiting for database to be ready..."
python - <<'PY'
import os
import time

url = os.environ.get("DATABASE_URL", "")
if not url or url.startswith("sqlite"):
    print("ℹ️ DATABASE_URL not set or SQLite detected; skipping DB wait.")
    raise SystemExit(0)

# Normalize URL for psycopg2 (remove async drivers)
sync_url = url.replace("postgresql+asyncpg://", "postgresql://").replace("postgresql+psycopg2://", "postgresql://")

timeout = int(os.environ.get("DB_WAIT_TIMEOUT", "90"))  # Increased timeout for Railway cold starts
deadline = time.time() + timeout
attempt = 0

while time.time() < deadline:
    attempt += 1
    try:
        import psycopg2
        conn = psycopg2.connect(sync_url, connect_timeout=5)
        conn.close()
        print(f"✅ Database is ready and accepting connections (attempt {attempt})")
        raise SystemExit(0)
    except Exception as e:
        remaining = int(deadline - time.time())
        if remaining > 0:
            print(f"⏳ Database not ready yet (attempt {attempt}): {type(e).__name__}. Retrying... ({remaining}s left)")
            time.sleep(3)
        else:
            print(f"❌ Database not ready after {timeout}s: {e}")
            raise SystemExit(1)

print(f"❌ Database not ready after {timeout}s")
raise SystemExit(1)
PY

# Fix overlapping Alembic heads (if any)
echo "🧰 Checking Alembic version table..."
python - <<'PY'
import os
from sqlalchemy import create_engine, text
from alembic.config import Config
from alembic.script import ScriptDirectory

def get_sync_database_url(url: str) -> str:
    if "+asyncpg" in url:
        return url.replace("+asyncpg", "")
    if "+aiosqlite" in url:
        return url.replace("+aiosqlite", "")
    return url

url = os.environ.get("DATABASE_URL", "")
if not url or url.startswith("sqlite"):
    print("INFO: DATABASE_URL not set or SQLite detected; skipping Alembic version check.")
    raise SystemExit(0)

engine = create_engine(get_sync_database_url(url))
try:
    with engine.connect() as conn:
        rows = [r[0] for r in conn.execute(text("SELECT version_num FROM alembic_version"))]
except Exception as exc:
    print(f"INFO: Alembic version table not found or not accessible: {exc}")
    raise SystemExit(0)

if len(rows) <= 1:
    print("OK: Alembic version table has a single head.")
    raise SystemExit(0)

print(f"WARNING: Multiple alembic versions found in DB: {rows}")

config = Config(os.path.join(os.getcwd(), "alembic.ini"))
script = ScriptDirectory.from_config(config)

# Build a list of all revisions in the current migration chain
all_revisions = []
try:
    for rev in script.walk_revisions():
        all_revisions.append(rev.revision)
except Exception as e:
    print(f"ERROR: Failed to walk revisions: {e}")
    raise SystemExit(1)

print(f"INFO: Migration chain has {len(all_revisions)} revisions")

# Filter to only revisions that exist in the current chain
valid_rows = [r for r in rows if r in all_revisions]
invalid_rows = [r for r in rows if r not in all_revisions]

if invalid_rows:
    print(f"WARNING: Removing revisions not in current chain: {invalid_rows}")

if not valid_rows:
    print("ERROR: No valid revisions found in alembic_version that match current chain")
    raise SystemExit(1)

# Find which valid revision is furthest along (earliest in walk = latest revision)
# walk_revisions() returns from newest to oldest
keep = None
for rev in all_revisions:
    if rev in valid_rows:
        keep = rev
        break

if not keep:
    # Fallback: keep the first valid one
    keep = valid_rows[0]

if len(rows) > 1 or invalid_rows:
    print(f"INFO: Keeping revision '{keep}' and removing others")
    with engine.begin() as conn:
        conn.execute(text("DELETE FROM alembic_version WHERE version_num != :keep"), {"keep": keep})
    print("OK: Alembic version table repaired.")
else:
    print("OK: No repair needed.")
PY

# Run Alembic migrations
echo "📦 Running database migrations..."
alembic upgrade head
echo "✅ Migrations complete!"

# Start the application
echo "🌐 Starting FastAPI server on port ${PORT:-8000}..."
exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}" "$@"
