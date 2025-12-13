# AI Handoff Protocol 🤖

**READ THIS FIRST.**
This file is the **living status report** of the project.
*   **Incoming Agent:** Read this to orient yourself.
*   **Outgoing Agent:** You **MUST** update this file, Commit, and **Push to Origin** before you leave.

## 1. State of the World (Last Updated: 2025-12-11)
*   **Project:** Proaktiv Dokument Hub (Azure Cloud App).
*   **Current Phase:** "Cloud Optimization" (Deployment Complete).
*   **Status:** The system is **Live on Azure**. Architecture is **Code (Git) vs. Data (Azure Files)**.

## 2. Critical Context Files
You do not need to read every file. Read these three in order:
1.  **`.agent/context.md`**: The technical bible for the Cloud Architecture. **READ THIS.**
2.  **`ROADMAP.md`**: Future plans (Security/Entra ID).
3.  **`documentation/BRAND_GUIDE.md`**: Strict design rules.

## 3. "Don't Do This" (Common Pitfalls)
*   ❌ **Do NOT Push Templates to Git:** The app reads from Azure Storage (`/library`), not the code repo.
*   ❌ **Do NOT Edit `server.js` Paths:** The mount points are critical for Azure function.
*   ❌ **Do NOT Overwrite `System/Styles`:** This is the CSS source of truth.

## 4. Operational Protocols (MANDATORY)
*   **Atomic Git Ops:** Always `commit` and `push` in one sequence. Do not leave unpushed commits.
*   **Commit Quality:** EVERY commit must have a **Title** (feat/fix/docs) AND a **Body** description.
*   **Docs Sync:** Never change code without updating the relevant documentation (`README`, `ROADMAP`, or `HANDOFF`). They must go hand-in-hand.

## 5. Next Actions
Check `ROADMAP.md`. The immediate priorities are:
1.  Monitor the Azure deployment stability.
2.  Plan the **Entra ID** implementation (Security).
3.  Assist user with batch uploading legacy templates to the Azure Share.

*Good luck.*
