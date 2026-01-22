# IMPL PLAN: V3.2 Operations Enhancement

**Status:** Proposed
**Feature:** Employee Roles, Supplier Hub, Photo Automation

## 1. Employee Management Advanced
*   **Goal:** Enhance employee records with Vitec roles and enable group communications.
*   **Database Updates:**
    *   Add `system_roles` column to `Employee` (JSONB/Array of Strings).
    *   Add `email_groups` logic (Virtual or Table?).
*   **Integrations:**
    *   **Microsoft Teams:** Add `teams_group_id` to Employee/Office.
    *   **SharePoint:** Add `sharepoint_folder_url`.
*   **UI Updates:**
    *   **Filter Bar:** Add "Role" dropdown (Eiendomsmegler, Daglig leder, etc.).
    *   **Actions:** "Email Group" button (mailto link generator).

## 2. Supplier Hub (Leverandører)
*   **Goal:** Centralized directory for 3rd party partners.
*   **New Models:**
    *   `Supplier`:
        *   `id`, `name`, `category`, `status` ('connected' | 'available').
        *   `contact_info` (JSONB), `logo_url`.
    *   `SupplierIssue`:
        *   `id`, `supplier_id`, `title`, `description`.
        *   `status` ('open', 'in_progress', 'resolved').
        *   `logged_at`, `resolved_at`.
*   **UI Pages:**
    *   `/suppliers`: Dashboard with 2 tabs (Connected, Available).
    *   `/suppliers/[id]`: Detail view with Issue Tracker.

## 3. Photo Export Automation
*   **Goal:** Automate the manual photo export process.
*   **Script:** `backend/scripts/photo_export_bot.py`
*   **Tech Stack:** Python + Playwright.
*   **Workflow:**
    1.  Parse input Excel (yellow rows).
    2.  Login to `proaktiv.no/export`.
    3.  Submit reference -> Wait for WebDAV.
    4.  Copy folder from WebDAV to local path.
*   **Requirements:**
    *   `openpyxl` for Excel.
    *   `playwright` for browser.
    *   `shutil` for file ops.

## Agent Tasks hierarchy
1.  **Systems Architect:** Define `Supplier` models and `Employee` updates.
2.  **Frontend Architect:** Design Supplier Dashboard and Employee Filters.
3.  **Builder:** Implement schema, UI, and the Python Script.
