# Reports Page 502 Errors — Debugging Guide

## Root Cause

The "Request failed with status code 502" on the Rapporter page is raised by the **backend** when Vitec Hub API calls fail. The backend's `VitecHubService` returns 502 in these cases:

1. **Connection/timeout** — `httpx.HTTPError` (e.g. Vitec Hub unreachable, 30s timeout)
2. **Vitec returns error** — 4xx/5xx from Vitec Hub
3. **Invalid response** — JSON parse failure from Vitec

## Affected Endpoints

| Endpoint | Trigger |
|----------|---------|
| `GET /api/reports/sales-report/data` | "Last inn rapport" or "Oppdater fra live data" |
| `GET /api/reports/best-performers` | Best performers tab / refresh |
| `GET /api/reports/budgets/comparison` | Budget tab / refresh |
| `GET /api/reports/cache-events` | Live updates (SSE priming) |

## Debugging Steps

### 1. Check Railway logs

```bash
railway logs
```

Look for `get_sales_report_data failed`, `Vitec Hub request failed`, or stack traces.

### 2. Verify Vitec Hub credentials

- `VITEC_HUB_BASE_URL` — e.g. `https://hub.megler.vitec.net`
- `VITEC_HUB_PRODUCT_LOGIN` / `VITEC_HUB_ACCESS_KEY`
- `VITEC_INSTALLATION_ID`

### 3. Verify reports cache schema (500 on cache-events)

```powershell
$env:DATABASE_URL = "postgresql://postgres:PASSWORD@shuttle.proxy.rlwy.net:51557/railway"
cd backend
python scripts/verify_reports_cache_schema.py
```

Apply migrations `20260312_0001` and `20260312_0002` if tables/columns are missing. See `.cursor/rules/database-migrations.mdc`.

### 4. Test Vitec Hub directly

```bash
curl -u "PRODUCT_LOGIN:ACCESS_KEY" "https://hub.megler.vitec.net/INSTALLATION_ID/Accounting/Estates?departmentId=1120"
```

### 5. Improve error visibility

As of this fix, the frontend extracts `detail` from API error responses. Instead of "Request failed with status code 502", you should now see messages like:

- "Vitec Hub request failed."
- "Vitec Hub error 503: Service Unavailable"

## Mitigations

- **Transient failures**: Retry "Last inn rapport" or "Oppdater fra live data".
- **Vitec timeout**: Backend uses 30s per Vitec request; slow responses can cause 502.
- **Cold start**: Railway may sleep when idle; first request can be slow.
- **Rate limiting**: VitecHubService throttles to 50 req/sec by default (well below ~600/sec limit). Override with `VITEC_RATE_LIMIT_REQUESTS_PER_SECOND` (1–200).

## Scheduler (Email Subscriptions)

Scheduled report delivery runs via GitHub Actions (`.github/workflows/reports-scheduler.yml`). Setup: add `REPORTS_SCHEDULER_TOKEN` to GitHub secrets and Railway. See `.planning/phases/reports-enhancements/PLAN.md`.

## Railway CLI

If `railway logs` shows "No deployments found":

1. Run `railway service` and select **Proaktiv-Dokument-Hub** (not Postgres).
2. Ensure the project has at least one deployment.
3. Run `railway logs` again.
