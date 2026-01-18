# PROAKTIV HUB - PRODUCT REQUIREMENTS (PRD)

## V3.0 CORE FEATURES (Verification Phase)
*   **1. Office & Employee Hub:** Central CRM for filtered directories.
*   **2. Company Assets:** Scoped file storage (Global/Office/Employee).
*   **3. Territory Map:** Postal code heatmap.
*   **4. Document Categories:** Seeded from Vitec.
*   **5. System Templates:** Versioned partials (headers/footers).

## V3.2 OPERATIONS ENHANCEMENT (New)

### 1. Employee Management Advanced
*   **Goal:** Role-based filtering and group email.
*   **Data:** Add `system_roles` (Array) and `email_groups` to Employee.
*   **UI:** Filter Sidebar (Role/Office), "Email Group" Action.
*   **Integrations:** Microsoft Teams mirror, SharePoint links.

### 2. Supplier Hub (Leverandører)
*   **Goal:** Central directory for partners.
*   **Connected Suppliers:** Rich cards + Issue Tracker (Open/Resolved).
*   **Available Suppliers:** Simple directory.
*   **Data:** `Supplier`, `SupplierIssue` models.

### 3. Photo Export Automation
*   **Goal:** Automate manual Vitec/WebDAV workflow.
*   **Tooling:** Python Script + Playwright.
*   **Workflow:** Read Excel (Yellow rows) -> Login -> Submit -> Copy from WebDAV.

## TECHNICAL STACK
*   **Backend:** FastAPI, PostgreSQL (Railway), SQLAlchemy.
*   **Frontend:** Next.js 14, Shadcn UI, Tailwind.
*   **Auth:** Simple Password (JWT).
