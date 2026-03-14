# Database Access Workflow (Preferred)

**Agents: Use this workflow instead of Docker + Alembic for database inspection and schema fixes.**

Railway's Alembic migrations during deploy are unreliable. This workflow lets you query and modify the production database directly from Cursor without going through Railway deployment.

---

## Quick Reference

| Task | Tool | Command / Method |
|------|------|------------------|
| **Read** (inspect schema, run queries) | Postgres MCP | Use `query` tool with server `user-postgres` |
| **Write** (schema changes, fixes when Alembic fails) | `run_sql.py` | `railway run python scripts/run_sql.py "SQL"` |

---

## Read Access: Postgres MCP

Cursor connects to Railway Postgres via the **Postgres MCP** (`@modelcontextprotocol/server-postgres`).

- **Read-only** — safe for inspection
- No Docker or Alembic needed
- Connection string in `~/.cursor/mcp.json` (must use `DATABASE_PUBLIC_URL`, not internal)

**When the Postgres password changes** (e.g. after Railway credential fix), update `mcp.json` with the new `DATABASE_PUBLIC_URL` from Railway → Postgres → Variables. See `.cursor/docs/postgres-mcp-sync.md`.

**Example queries agents can run:**
- `SELECT * FROM information_schema.columns WHERE table_name = 'employees'`
- `SELECT count(*) FROM templates`
- `SELECT * FROM report_sales_sync_events ORDER BY id DESC LIMIT 5`

---

## Write Access: run_sql.py

For schema changes, fixes when migrations fail, or one-off updates:

```powershell
cd backend

# Via Railway (gets DATABASE_URL from backend service):
railway run python scripts/run_sql.py "ALTER TABLE x ADD COLUMN IF NOT EXISTS y TEXT"

# With DATABASE_URL or DATABASE_PUBLIC_URL in env:
python scripts/run_sql.py "UPDATE alembic_version SET version_num = '20260314_0001'"
```

**Multi-statement (e.g. when Alembic fails):**
```powershell
railway run python scripts/run_sql.py "ALTER TABLE offices ADD COLUMN IF NOT EXISTS new_col TEXT; UPDATE alembic_version SET version_num = '20260314_0001'"
```

**Requirements:** `DATABASE_URL` or `DATABASE_PUBLIC_URL` in environment. Use `railway run` to inject from Railway, or set manually for local `.env`.

---

## When to Use What

| Scenario | Use |
|----------|-----|
| Inspect table structure | Postgres MCP `query` |
| Check row counts, sample data | Postgres MCP `query` |
| Debug schema mismatch | Postgres MCP + `run_sql.py` |
| Migration failed on Railway deploy | `run_sql.py` with migration's SQL + `alembic_version` update |
| New migration (normal flow) | Create migration → apply locally → apply to Railway via `run_sql.py` or manual `alembic upgrade head` |

---

## Deprecated Workflow (Avoid)

- ~~Running `alembic upgrade head` during Railway deploy~~ — unreliable
- ~~Using Docker only to run migrations~~ — unnecessary when `run_sql.py` works
- ~~Creating one-off Python scripts for each fix~~ — use `run_sql.py` instead

---

## Related

- `.cursor/rules/database-migrations.mdc` — migration safety rules
- `.cursor/docs/postgres-mcp-sync.md` — keeping MCP connection string in sync
