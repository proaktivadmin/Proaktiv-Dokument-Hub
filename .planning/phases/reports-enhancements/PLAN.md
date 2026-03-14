# Reports Enhancements – Franchise, Budgeting, Best Performers, Email Delivery

Plan for items 7–11 from the Formidlingsrapport feedback (March 2026).

## Completed (Items 1–6)

- ✅ Revenue numbers shown as positive (removed dash)
- ✅ Property address instead of EstateID (from streetAddress, postalCode, city)
- ✅ Exclude brokers with 0 sales (oppgjørsansvarlig)
- ✅ Exclude oppgjør offices from department dropdown
- ✅ Date range scope: from_date, to_date, presets (Hele året, Denne måneden, Siste 7 dager, Siste 2 uker)
- ⚠️ VAT: exkl/inkl may still match if Vitec API returns vatAmount=0; logic is correct

---

## Completed (Items 7–11)

### Item 7: Franchise Report for CEO ✅

- Mode toggle: "Enkelt avdeling" | "Hele franchisen"
- `GET /api/reports/sales-report/franchise` — fetch all departments
- Accordion UI: Department → Brokers → Properties

### Item 8: Franchise Summary ✅

- Summary card at top with totals
- Department breakdown table (antall salg, revenue, % of total)

### Item 9: Budgeting Feature ✅

- `report_budgets` table, CRUD via `/api/reports/budgets`
- `GET /api/reports/budgets/comparison` — actual vs budget
- Budget tab on reports page with per-month inputs

### Item 10: Best Performers ✅

- `GET /api/reports/best-performers` — role split (eiendomsmegler vs eiendomsmeglerfullmektig)
- Weekly/monthly presets, Excel export
- "Best performers" card + "Last ned ukesrapport" button

### Item 11: Automatic Report Delivery ✅

- `report_subscriptions` table, CRUD via `/api/reports/subscriptions`
- `POST /api/reports/subscriptions/run-due` — sends due emails via Graph API
- Abonnementer tab: add/remove, recipients, cadence (weekly/monthly)
- **Scheduler:** GitHub Actions workflow `.github/workflows/reports-scheduler.yml` — Fridays 07:00 UTC

---

## Scheduler Setup (Item 11)

The reports scheduler runs via GitHub Actions. To enable:

1. **GitHub:** Add secret `REPORTS_SCHEDULER_TOKEN` (Settings → Secrets and variables → Actions)
2. **Railway:** Set `REPORTS_SCHEDULER_TOKEN` on the backend service (must match)
3. **Optional:** Set variable `REPORTS_BACKEND_URL` to override backend URL (default: `https://proaktiv-admin.up.railway.app`)

Manual run: Actions → Reports Scheduler → Run workflow

---

## Dependencies (resolved)

- Vitec Hub API: employee roles used for best performers
- Email: GraphService (Microsoft Graph API)
- Scheduler: GitHub Actions (`.github/workflows/reports-scheduler.yml`)

---

## Future Enhancements (2026-03-14 feedback)

- **Budget persistence:** Store monthly actuals so past months don't require re-fetch from Vitec each time. Would need `report_monthly_actuals` table and sync logic.
- **Best performers broker pictures:** Add employee avatars to leaderboard cards.
- **Best performers expandable rows:** Show property-level detail per broker (like main report).
