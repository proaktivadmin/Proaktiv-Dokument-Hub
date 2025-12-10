# Developer Context & Memory

> **🤖 AI AGENTS START HERE:** Please read `AI_HANDOFF.md` first for the immediate project status and critical protocols.

## Project Overview
**Proaktiv Dokument Hub** is a local-first web application for managing, editing, and previewing HTML templates for the Vitec Next real estate system.

### Tech Stack
- **Frontend:** React (Vite), TailwindCSS, Lucide React icons, Monaco Editor (`@monaco-editor/react`).
- **Backend:** Node.js (Express).
- **Storage:** Local Filesystem (`fs`).
- **Styling:** Modular CSS (`vitec-structure.css`, `theme-base.css`, `theme-proaktiv.css`) bundled dynamically for export.
- **Brand Guide:** See `documentation/BRAND_GUIDE.md` for strict color/font rules.

## Key Architectures

### 1. The Migration Factory
- **Goal:** Mass update legacy templates to the new modular CSS system.
- **Frontend:** `MigrationView.jsx` (Batch UI).
- **Backend:** `/api/sanitize/batch` endpoint in `server.js`.
- **Logic:** `sanitizer.js` uses Regex to:
    - Strip inline styles.
    - Remove `<font>` tags.
    - Update `vitec-template` resource pointers to the new system.
- **Workflow:** Drop files in `library/Legacy_Import` -> Run Batch -> Collect from `library/Ready_For_Export`.

### 2. Vitec Export & Bundling
- Vitec Next **does not support** external CSS files or `@import`.
- **Solution:** `handleExportForVitec` in `App.jsx` fetches `vitec-structure.css` + `theme-base.css` + `Active Theme` and **inlines** them into a single `<style>` block before saving.

### 3. Preview System
- Uses an `iframe` with dynamically injected CSS links (with cache-busting timestamps) to simulate Vitec's rendering.
- **Dynamic Scaling:** `ResizeObserver` scales the preview container to fit the viewport (Mobile/Desktop/A4 modes).

## Lessons Learned & "Gotchas"
- **Vitec CSS:** Never use `@import` in production exports. Always bundle.
- **Filesystem Dependency:** The project relies heavily on `fs`. It **cannot** run on serverless platforms (Firebase Functions, Vercel) without rewriting the storage layer to use Cloud Storage.
- **Azure Compatibility:** Azure App Service is the preferred deployment target because it supports **Azure Files mounts**, allowing the legacy code to work without refactoring.
- **React Syntax:** Be careful with ternary operators in `App.jsx`. Comments inside ternaries can break the parser (Syntax Error fix: 2025-12-10).

## Standard Operating Procedures (SOP)

### How to Run Locally
1.  **Backend:** `node server.js` (Port 5000)
2.  **Frontend:** `cd client && npm run dev` (Port 5173)

### How to Verify
1.  **Manual:** Open `http://localhost:5173`, select a file, verified "Eksporter til Vitec Next" button appears.
2.  **Automated:** Run the "Sanitizer Batch" from the settings menu using `legacy_test.html`.

### Artifact Maintenance Strategy (CRITICAL)
To ensure no "brain notes" (implementation plans, task lists, walkthroughs) are lost between sessions:
1.  **Before ending a session:** The Agent MUST archive all active artifacts from the `.gemini` folder to `documentation/archive/`.
2.  **Naming Convention:** Use `v{n}_[artifact_name].md` (e.g., `v1_task.md`).
3.  **Update Handoff:** You MUST update `AI_HANDOFF.md` with the current "State of the World" and "Next Actions" before signing off.
4.  **Git Commit:** All archives and the updated `AI_HANDOFF.md` must be included in the final commit.
5.  **Git Push:** You MUST push the commit to `origin` (`git push origin main`) to ensure cloud backup.
6.  **Notify User:** Confirm that both commit and push were successful.

## Deployment Strategy
- **Current:** Local Host.
- **Planned:** Azure App Service (B1 Tier) + Azure Files Mount + Entra ID (Easy Auth).
