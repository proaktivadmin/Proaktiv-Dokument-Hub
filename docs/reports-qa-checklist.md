# Reports Page QA Checklist (2026-03-14)

Run this checklist after starting the full stack: `docker compose up -d` (or backend + frontend separately).

## Prerequisites

1. **Start stack:** `docker compose up -d` (or `npm run dev` in frontend + `uvicorn app.main:app --reload` in backend with DATABASE_URL)
2. **Login** at http://localhost:3000/login (or 3001 if 3000 in use)
3. **Navigate** to Rapporter (Formidlingsrapport) via header or /reports

---

## Page Accessibility Check (2026-03-14)

All main routes return HTTP 200 when the stack is running:

| Route | Status |
|-------|--------|
| / | ✅ 200 |
| /login | ✅ 200 |
| /reports | ✅ 200 |
| /offices | ✅ 200 |
| /employees | ✅ 200 |
| /templates | ✅ 200 |
| /assets | ✅ 200 |
| /storage | ✅ 200 |
| /notifications | ✅ 200 |
| /sync | ✅ 200 |
| /portal/preview | ✅ 200 |
| /flettekoder | ✅ 200 |
| /categories | ✅ 200 |
| /mottakere | ✅ 200 |
| /territories | ✅ 200 |
| /tools/image-optimizer | ✅ 200 |
| /tools/office-overview | ✅ 200 |
| /sanitizer | ✅ 200 |
| /templates/dedup | ✅ 200 |

---

## Dark Mode QA (2026-03-14)

- **Trigger:** Oslo time 18:00–07:00, or `?dark=1` / `?dark=0` for manual override
- **Login page:** `http://localhost:3000/login?dark=1` — uses semantic tokens (bg-card, text-foreground, etc.)
- **Reports page:** `http://localhost:3000/reports?dark=1` — uses semantic tokens (Card, bg-background)
- **Manual check:** Open any page with `?dark=1` and verify navy-based background, readable text contrast
- **Header toggle:** Sun/Moon switch in header (between Verktøy and Notifications) — toggles `?dark=1` / `?dark=0`

### Cursor Browser QA (2026-03-14, homelab 192.168.77.127:3000)

| Page | URL | Result | Notes |
|------|-----|--------|-------|
| Reports | `/reports?dark=1` | ⚠️ Light theme | Cards, inputs, buttons still light; semantic tokens present but `.dark` may not apply on nav |
| Dashboard | `/?dark=1` | ❌ Light theme | Heavy use of `bg-white`, `text-[#272630]`, `border-[#E5E5E5]` — needs token migration |

**Findings:**
- Reports page uses semantic tokens (`bg-background`, `bg-card`, `text-foreground`) — should support dark mode when `.dark` is applied
- Dashboard (`page.tsx`) uses hardcoded colors throughout — blocks dark mode
- Theme provider (`ThemeProvider`) applies `.dark` from URL, Oslo time, or manual toggle
- **Next steps:** (1) Add pathname/search listener to theme provider for immediate `?dark=1` response; (2) Migrate Dashboard to semantic tokens

### Fixes applied (2026-03-14)

- **ThemeProvider:** Replaced OsloTimeThemeProvider with ThemeContext; provides `isDark` + `setDark` for header toggle; still respects `?dark=1`/`?dark=0` and Oslo time when no param.
- **Dashboard:** Migrated all hardcoded colors to semantic tokens (`bg-card`, `text-foreground`, `border-border`, `bg-muted`, `bg-secondary`, `text-accent`, etc.).

---

## Visual QA Results (2026-03-14, Cursor Browser)

**Login:** ✅ Verified with qa-credentials.json  
**Reports page load:** ✅ Page renders correctly

| Item | Status | Notes |
|------|--------|-------|
| "Nye data i Vitec" | ✅ | Replaces "Nye cache-events" in Live dataoppdateringer |
| Best performers period selector | ✅ | Independent "Denne uken (9. mars – 15. mars)" |
| Scope display | ✅ | "Omfang: Proaktiv Bergen Sentrum" |
| "Inkluder mva i beløp" | ✅ | Checkbox present (implies eksl. mva. default) |
| Report data load | ⚠️ | API returns 500 — VITEC_INSTALLATION_ID or migration may be missing |
| Property rows / number formatting | ⏳ | Blocked until report loads successfully |

---

## 1. Spelling & Labels

- [ ] **"eksl. mva."** — All instances show "eksl." not "exkl." (summary, column headers, Best performers)
- [ ] **"inkl. mva."** — Consistent with period when VAT included

## 2. Number Formatting

- [ ] **Whole numbers only** — No decimals or commas in revenue (e.g. `382 770` not `382 770,62`)
- [ ] Applies to: broker totals, property rows, Best performers, budget YTD, budget table

## 3. Live Data Updates

- [x] **"Nye data i Vitec"** — Replaces "Nye cache-events" ✅
- [ ] **"Sist oppdatert:"** — Replaces "Sist:" (visible when sync events exist)

## 4. Property Rows (Formidlingsrapport)

- [ ] **No raw UUIDs** — Expanded property rows show address + oppdragsnummer, never estate_id
- [ ] **"Adresse ukjent (oppdragsnummer)"** when address missing
- [ ] **Address (oppdragsnummer)** when both available

## 5. Best Performers

- [x] **Independent period selector** — Uke/Måned dropdown, week selector ✅
- [x] **Scope display** — "Omfang: [Avdeling X]" ✅
- [ ] **Period display** — "Viser: [from] – [to] (eksl. mva.)" when data loaded
- [ ] **Load/Download** use Best performers period, not main report period

## 6. Column Headers

- [ ] **Antall salg** and **Eiendomstype** — Separate columns (not concatenated)
- [ ] **Oppdragstype** — Present
- [ ] **Sum (eksl. mva.) (kr)** — Correct spelling

## 7. Backend Migration

- [ ] **Apply migration:** `alembic upgrade head` (or `run_sql.py` for Railway)
- [ ] **assignment_number** column exists on `report_sales_estate_cache`

---

## Automated Verification (no browser)

```bash
# Frontend build
cd frontend && npm run build

# Frontend tests
cd frontend && npm run test:run

# Backend tests
cd backend && pytest tests/test_reports_router.py -v
```
