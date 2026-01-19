# Proaktiv Directory Sync (Scraper)

This repo includes a bounded web crawler to **extract offices + employees** from `proaktiv.no` and **upsert** the data into the database.

## What it writes

- **Offices** (`offices`)
  - Key: `homepage_url` (used for upsert match)
  - Fields: `name`, `email`, `phone`, `street_address`, `postal_code`, `city`, `description`, `profile_image_url`, + social/links when present
- **Employees** (`employees`)
  - Key: `email` (primary match) then `homepage_profile_url` (fallback match)
  - Fields: `first_name`, `last_name`, `title`, `email`, `phone`, `homepage_profile_url`, `profile_image_url`, `description`

## Script location

- Python scraper: `backend/scripts/sync_proaktiv_directory.py`
- PowerShell runner: `backend/scripts/run_proaktiv_directory_sync.ps1`
- Windows launcher: `run-proaktiv-scraper.bat`

## Safety rules (for humans + agents)

- **Never run unbounded**: always set `--max-pages`, `--max-runtime-minutes`, and `--delay-ms`.
- **Don’t hammer the site**: keep `--delay-ms >= 1000` for any multi-city run.
- **Start with a bounded test**: small `--max-pages` (10–30) before larger runs.
- **Avoid token waste**: prefer direct HTTP fetch unless you need Firecrawl (Firecrawl costs money/tokens).
- **No secrets**: don’t commit DB URLs, passwords, API keys, or Railway variables.

## Running locally (Docker DB)

1. Start Postgres:

```bash
docker compose up -d db
```

2. Run a safe bounded crawl:

```bash
run-proaktiv-scraper.bat -Preset all -Migrate -Overwrite
```

## Running against Railway DB (recommended for “real” data)

If you want scraped data to show up in the production app, you must write to the **Railway Postgres database**.

### Option A (recommended): run locally, connect to Railway DB

1. Get your Railway Postgres connection string (from Railway dashboard variables).
2. Set it for the current terminal session (don’t save in git):

PowerShell:

```powershell
$env:RAILWAY_DATABASE_URL="<railway postgres url>"
```

3. Run the scraper pointing at Railway:

```powershell
run-proaktiv-scraper.bat -TargetDb railway -Preset all -Migrate -Overwrite
```

### Notes on SSL

Railway external Postgres URLs sometimes require SSL. If you see SSL-related connection errors:
- Use the Railway-provided external connection string (often includes `sslmode=require`)
- Ensure your backend supports this mode for async DB connections (see `backend/app/database.py`)

## CLI flags (advanced)

The underlying Python module supports:
- `--start <url>` (repeatable)
- `--delay-ms <int>`
- `--max-pages <int>`
- `--max-runtime-minutes <int>`
- `--max-office-pages <int>`
- `--max-employee-pages <int>`
- `--deep-employees` (prioritize employee profile pages for richer bios)
- `--overwrite` (fill/replace data)
- `--dry-run` (no DB writes)
- `--use-firecrawl` (fetch HTML via Firecrawl)

## Agent instructions (copy/paste)

When another agent is asked to “run a Proaktiv scrape”:
1. Confirm the target DB (local vs Railway). **Default to local** unless explicitly asked to write production data.
2. Ensure migrations are applied to the target DB (`alembic upgrade head`).
3. Run a bounded test first (`--max-pages 20`, `--max-runtime-minutes 10`, `--delay-ms 1500`).
4. Only scale up after verifying data quality (no bogus “Logg inn” etc).
5. Never print or paste DB URLs/secrets into committed files.

