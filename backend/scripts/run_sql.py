#!/usr/bin/env python3
"""
Run SQL directly against the database. Use from Cursor's terminal to apply
schema changes or fixes when Alembic fails, without going through Railway deploy.

Usage:
  # Via Railway (gets DATABASE_URL from Railway - recommended):
  railway run python scripts/run_sql.py "ALTER TABLE x ADD COLUMN IF NOT EXISTS y TEXT"

  # With local .env containing DATABASE_PUBLIC_URL:
  python scripts/run_sql.py "SELECT count(*) FROM templates"

  # Multi-statement:
  railway run python scripts/run_sql.py "ALTER TABLE x ADD COLUMN z TEXT; UPDATE alembic_version SET version_num = 'xxx'"

Requires: DATABASE_URL or DATABASE_PUBLIC_URL in environment.
"""

import os
import sys
from pathlib import Path

# Ensure backend app is on path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError


def main() -> None:
    url = os.environ.get("DATABASE_URL") or os.environ.get("DATABASE_PUBLIC_URL")
    if not url:
        print("ERROR: Set DATABASE_URL or DATABASE_PUBLIC_URL", file=sys.stderr)
        print("  Use: railway run python scripts/run_sql.py \"SQL\"", file=sys.stderr)
        sys.exit(1)

    if len(sys.argv) < 2:
        print("Usage: run_sql.py \"SQL statement(s)\"", file=sys.stderr)
        sys.exit(1)

    sql = sys.argv[1].strip()
    if not sql:
        print("ERROR: Empty SQL", file=sys.stderr)
        sys.exit(1)

    # Use sync engine (psycopg2) - strip asyncpg if present
    sync_url = url.replace("postgresql+asyncpg://", "postgresql://", 1)
    if sync_url.startswith("postgresql://") and "+psycopg2" not in sync_url:
        sync_url = sync_url.replace("postgresql://", "postgresql+psycopg2://", 1)
    engine = create_engine(sync_url)

    try:
        with engine.connect() as conn:
            for stmt in _split_statements(sql):
                stmt = stmt.strip()
                if not stmt:
                    continue
                result = conn.execute(text(stmt))
                conn.commit()
                if result.returns_rows:
                    rows = result.fetchall()
                    if rows:
                        for row in rows:
                            print(dict(row._mapping))
                    else:
                        print("(0 rows)")
                else:
                    print(f"OK (rowcount: {result.rowcount})")
    except SQLAlchemyError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(1)


def _split_statements(sql: str) -> list[str]:
    """Split on semicolons, preserving those inside strings (naive)."""
    parts: list[str] = []
    current: list[str] = []
    in_string = False
    quote = None
    i = 0
    while i < len(sql):
        c = sql[i]
        if in_string:
            if c == quote and (i + 1 >= len(sql) or sql[i + 1] != quote):
                in_string = False
            current.append(c)
            i += 1
            continue
        if c in ("'", '"'):
            in_string = True
            quote = c
            current.append(c)
            i += 1
            continue
        if c == ";" and not in_string:
            parts.append("".join(current))
            current = []
            i += 1
            # Skip whitespace after ;
            while i < len(sql) and sql[i] in " \t\n":
                i += 1
            continue
        current.append(c)
        i += 1
    if current:
        parts.append("".join(current))
    return parts


if __name__ == "__main__":
    main()
