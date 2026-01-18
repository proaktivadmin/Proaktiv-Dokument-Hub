# PROGRESS.md - Session Tracker

**Last Updated**: 2026-01-18 23:15
**Current Focus**: V3.1 verification + QA signoff (employees + templates)

---

## 🟢 CURRENT STATUS

### Structure: ✅ COMPLETE
- [x] Installed comprehensive `docs/AGENTS.md` (Master Guide)
- [x] Created `docs/features/employee-management/TASKS.md`
- [x] Created `docs/features/leverandorer/TASKS.md`
- [x] Created `docs/features/photo-export/TASKS.md`

### V3.1 QA Fixes: ✅ DEPLOYED
- [x] Added `/api/ping`, `/api/territories/stats`, and fixed `/employees/email-group` routing.
- [x] Hardened template receiver filtering + template settings audit JSON serialization.
- [x] Shelf view now loads all templates (pagination).

### Next Immediate Task
**Feature:** Employee Management
**Task:** F4/F5 - Add Teams group display + include status filters in email group







---

## 📋 FEATURE STATUS

| Feature | Status | Next Task |
|---------|--------|-----------|
| Employee Management | 🟡 In Progress | F4/F5: Teams groups + email group filters |
| V3.1 QA Fixes | 🟢 Complete | Monitor Railway deploy |





| Leverandører | 🔵 Planned | B1: Supplier model |
| Photo Export | 🔵 Planned | S1: Create script |


---

## 📝 SESSION LOG

### 2026-01-18 (Evening)
- Pivoted from complex multi-agent to RALPH LOOP workflow
- Installed comprehensive AGENTS.md
- Created all 3 feature task breakdowns
- **B1 COMPLETE:** Added `system_roles` JSONB field to Employee model
  - Created Alembic migration: `20260118_0001_add_employee_system_roles.py`
  - Added `has_role()` helper method
- **B2 COMPLETE:** Added Microsoft 365 integration fields
  - Office: `teams_group_id`, `sharepoint_folder_url`
  - Employee: `sharepoint_folder_url`
  - Created migration: `20260118_0002_add_microsoft_integration.py`
- **B3 COMPLETE:** Added role & search filtering to GET /api/employees
  - Filter by `role` (Vitec system role)
  - Search by `name` or `email`
  - Updated Pydantic schemas with new fields
- **B4 COMPLETE:** Created Microsoft Graph client
  - `backend/app/integrations/microsoft_graph.py`
  - Teams groups listing, email sending
  - Placeholder credentials in config.py
- **B5 COMPLETE:** Added email group endpoint
  - `GET /api/employees/email-group?role=eiendomsmegler`
  - Returns emails list + mailto link

**✅ Backend Tasks Complete! Moving to Frontend.**
- **F1 COMPLETE:** Created role filter sidebar
  - `RoleFilter.tsx` component with all 5 Vitec roles
  - Integrated into `/employees` page
  - Updated API client and hook to support `role` and `search` params

### 2026-01-18 (Late)
- QA fixes completed for template receiver filtering, settings save, and shelf pagination.
- Backend endpoints added/fixed: `/api/ping`, `/api/territories/stats`, `/api/employees/email-group`.
- Deployed to `main` (commit `068ec02`) to trigger Railway auto-deploy.







---

## 🚧 BLOCKERS
None currently.

## ❓ QUESTIONS FOR USER
- Confirm the canonical role value for managing director (`daglig leder` vs `daglig_leder`).
