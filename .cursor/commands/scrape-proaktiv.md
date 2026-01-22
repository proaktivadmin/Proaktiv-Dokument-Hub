# Scrape Proaktiv Directory (offices + employees)

This runs the bounded Proaktiv directory scraper and upserts data into the database.

## Safety rules (must follow)
- **Always bounded**: use max pages + max runtime + delay.
- **No DDoS**: keep `--delay-ms >= 1000` for wider runs.
- **Start small**: do a limited run first (few pages, short runtime) before scaling.
- **No secrets in repo**: never paste Railway DB URLs or API keys into git-tracked files.
- **Production writes are risky**: Railway DB runs will update real data. Use `--dry-run` first if unsure.

## Recommended way (Windows)

### Local DB (Docker)
1. Start DB (if not running): `docker compose up -d db`
2. Run scraper (safe defaults + migrations):
   - `run-proaktiv-scraper.bat -Preset all -Migrate -Overwrite`

### Railway DB (writes to production DB)
1. Set Railway DB URL for *this terminal session* (don’t commit it anywhere):
   - PowerShell: `$env:RAILWAY_DATABASE_URL="<railway postgres url>"`
2. Run scraper against Railway:
   - `run-proaktiv-scraper.bat -TargetDb railway -Preset all -Migrate -Overwrite`

## Notes
- The underlying script is `backend/scripts/sync_proaktiv_directory.py`.
- Use `-DryRun` to preview actions without DB writes.
- `-Overwrite` fills missing fields and can replace existing values (depending on the field); use with care.
