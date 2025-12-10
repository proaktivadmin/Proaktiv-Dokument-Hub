# AI Handoff Protocol 🤖

**READ THIS FIRST.**
This file is the **living status report** of the project.
*   **Incoming Agent:** Read this to orient yourself.
*   **Outgoing Agent:** You **MUST** update this file before you leave.

## 1. State of the World (Last Updated: 2025-12-10)
*   **Project:** Proaktiv Dokument Hub (Localhost React/Node app).
*   **Current Phase:** "Migration Factory" (Mass sanitization of legacy templates).
*   **Status:** The system is **Live and Verified**. The user can run batch jobs.

## 2. Critical Context Files
You do not need to read every file. Read these three in order:
1.  **`CONTEXT.md`**: Tech stack, architecture, and "gotchas" (like the Vitec CSS bundling).
2.  **`ROADMAP.md`**: What was just finished and what is next (Azure Deployment).
3.  **`documentation/BRAND_GUIDE.md`**: Strict design rules (Hex codes, fonts).

## 3. "Don't Do This" (Common Pitfalls)
*   ❌ **Do NOT use `@import` in final CSS:** Vitec doesn't support it. Use the "Bundler" logic.
*   ❌ **Do NOT try to deploy to Vercel/Netlify:** This app uses the local filesystem (`fs`). It needs a persistent server (Azure App Service).
*   ❌ **Do NOT overwrite `library/System`:** This contains the source of truth for styles.

## 4. Next Actions
Check `ROADMAP.md`. The likely next steps are:
1.  Helping the user mass-import templates into `library/Legacy_Import`.
2.  Refining the `sanitizer.js` regex if edge cases appear.
3.  Starting the Azure deployment process.

*Good luck.*
