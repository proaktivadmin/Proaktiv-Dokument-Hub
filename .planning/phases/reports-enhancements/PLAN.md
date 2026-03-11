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

## Item 7: Franchise Report for CEO

**Goal:** One report showing all departments with expandable sections per department and brokers.

**Scope:**
- New view/mode: "Franchise" vs "Avdeling"
- When "Franchise" is selected, fetch report data for all departments (or a configurable list)
- UI: Accordion or nested table: Department → Brokers → Properties
- Each department expandable; each broker expandable under department

**Backend:**
- New endpoint: `GET /api/reports/sales-report/franchise?year=&from_date=&to_date=&include_vat=`
- Or extend existing `department_id` to accept `all` or a list
- Fetch data per department; aggregate in service layer

**Frontend:**
- Toggle: "Enkelt avdeling" | "Hele franchisen"
- When franchise: show department tree with expand/collapse

---

## Item 8: Franchise Summary

**Goal:** Summary across all departments (total sales, total revenue, department breakdown).

**Scope:**
- Summary card/section at top of franchise report
- Totals: sum of all departments
- Table: department name, antall salg, sum revenue, % of total

**Implementation:** Part of Item 7; add summary aggregation in service and display in UI.

---

## Item 9: Budgeting Feature

**Goal:** CEO can set budget per month and track progress toward yearly budget.

**Scope:**
- New DB table: `report_budgets` (department_id, year, month, budget_amount, created_at)
- UI: Budget input (per month or yearly) for each department
- Dashboard: Compare actual vs budget for each month
- Visual: "On track" / "Behind" indicator
- Calculation: "If we continue at X% of budget, we will reach Y by year end"

**Backend:**
- `POST/GET/PUT /api/reports/budgets` – CRUD for budgets
- `GET /api/reports/sales-report/data` already returns data; can add budget comparison in response or separate endpoint

**Frontend:**
- Budget settings page or section
- Budget vs actual chart/table
- Trend/projection indicator

---

## Item 10: Best Performers

**Goal:** Highlight best performers per week/month and provide a weekly report.

**Scope:**
- Categories: best eiendomsmegler, best eiendomsmeglerfullmektig, best department
- Time period: week or month
- Report: "Best performers" section, easy to collect before each Friday

**Implementation:**
- Reuse `sales-report/data` with `from_date`/`to_date` for week/month
- Add ranking logic: sort brokers by revenue, take top N
- Role: eiendomsmegler vs eiendomsmeglerfullmektig from Vitec API (Employees or job title)
- New endpoint or extend existing: `GET /api/reports/best-performers?from_date=&to_date=&scope=week|month`

**Frontend:**
- "Best performers" card/section
- "Last ned ukesrapport" (download weekly report) button

---

## Item 11: Automatic Report Delivery by Email

**Goal:** Schedule report delivery to selected recipients.

**Scope:**
- DB: `report_subscriptions` (user_email, report_type, schedule, department_ids, created_at)
- Schedule: weekly (e.g. Friday 08:00), monthly (e.g. 1st of month)
- Recipients: configurable list of emails
- Backend job: cron/scheduler that runs report, builds Excel/PDF, sends email

**Implementation:**
- Use existing GraphService for sending emails (if available) or SMTP
- Scheduler: APScheduler, Celery, or Railway cron
- UI: "Abonnementer" – add/remove subscriptions, schedule, recipients

---

## Suggested Order

1. **Item 7** – Franchise report (foundation)
2. **Item 8** – Franchise summary (part of 7)
3. **Item 10** – Best performers (reuses existing data)
4. **Item 9** – Budgeting (new DB + UI)
5. **Item 11** – Email delivery (new infra + scheduling)

---

## Dependencies

- Vitec Hub API: employee roles (eiendomsmegler vs eiendomsmeglerfullmektig) for Item 10
- Email service: Graph API or SMTP for Item 11
- Scheduler: Railway cron or external (e.g. GitHub Actions)
