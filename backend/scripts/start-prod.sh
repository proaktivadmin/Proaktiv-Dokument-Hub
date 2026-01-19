#!/bin/bash
set -e

echo "🚀 Starting Proaktiv Dokument Hub Backend..."

cd /app

# Wait for database if using Postgres
echo "⏳ Checking database availability..."
python - <<'PY'
import os
import socket
import time
from urllib.parse import urlparse

url = os.environ.get("DATABASE_URL", "")
if not url or url.startswith("sqlite"):
    print("ℹ️ DATABASE_URL not set or SQLite detected; skipping DB wait.")
    raise SystemExit(0)

# Normalize async URLs for parsing
url = url.replace("postgresql+asyncpg://", "postgresql://").replace("postgresql+psycopg2://", "postgresql://")
parsed = urlparse(url)
host = parsed.hostname or "localhost"
port = parsed.port or 5432
timeout = int(os.environ.get("DB_WAIT_TIMEOUT", "60"))
deadline = time.time() + timeout

while time.time() < deadline:
    try:
        with socket.create_connection((host, port), timeout=2):
            print(f"✅ Database is reachable at {host}:{port}")
            raise SystemExit(0)
    except OSError:
        time.sleep(2)

print(f"❌ Database not reachable after {timeout}s at {host}:{port}")
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
    print("ℹ️ DATABASE_URL not set or SQLite detected; skipping Alembic version check.")
    raise SystemExit(0)

engine = create_engine(get_sync_database_url(url))
try:
    with engine.connect() as conn:
        rows = [r[0] for r in conn.execute(text("SELECT version_num FROM alembic_version"))]
except Exception as exc:
    print(f"ℹ️ Alembic version table not found or not accessible: {exc}")
    raise SystemExit(0)

if len(rows) <= 1:
    print("✅ Alembic version table has a single head.")
    raise SystemExit(0)

config = Config(os.path.join(os.getcwd(), "alembic.ini"))
script = ScriptDirectory.from_config(config)

def is_ancestor(ancestor: str, descendant: str) -> bool:
    try:
        for rev in script.iterate_revisions(descendant, ancestor):
            if rev.revision == ancestor:
                return True
    except Exception:
        return False
    return False

top = []
for rev in rows:
    if not any(rev != other and is_ancestor(rev, other) for other in rows):
        top.append(rev)

if len(top) != 1:
    print(f"❌ Multiple independent heads in alembic_version: {rows}. Manual intervention required.")
    raise SystemExit(1)

keep = top[0]
print(f"⚠️ Multiple alembic heads found: {rows}. Keeping {keep} and removing others.")
with engine.begin() as conn:
    conn.execute(text("DELETE FROM alembic_version WHERE version_num != :keep"), {"keep": keep})
print("✅ Alembic version table repaired.")
PY

# Run Alembic migrations
echo "📦 Running database migrations..."
alembic upgrade head
echo "✅ Migrations complete!"

# Start the application
echo "🌐 Starting FastAPI server on port ${PORT:-8000}..."
exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}" "$@"
