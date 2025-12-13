# Proaktiv Dokument Hub - System Context

## 🏗 System Architecture (Azure Cloud)
The application has been migrated from a local-only tool to a cloud-hosted solution on **Azure App Service (Linux)**.

### Core Components
1.  **Frontend:** React (Vite) - Served as static files from `client/dist`.
2.  **Backend:** Node.js (Express) - Handling API requests and file operations.
3.  **Storage:** Azure Blob Storage (File Share) - Mounted to `/home/site/wwwroot/library`.

### 💾 Data Persistence Strategy (CRITICAL)
*   **The Difference:** We strictly separate **Code** (Logic) from **Data** (Templates).
*   **Code:** Lives in GitHub. Deployed via GitHub Actions. State is ephemeral (reset on redeploy).
*   **Data:** Lives in Azure Files (`library` share). Mounted as a network drive. **State is persistent.**
*   **The "Masking" Effect:** The Azure Mount overlays the git-cloned `library` folder. The app *only* sees what is in the Azure Share.

### 🎨 System Component Handling
*   **Hidden System Folder:** The `library/System` folder is logically hidden from the frontend sidebar to reduce clutter.
*   **Theme Engine:** The app explicitly looks for CSS files in `library/System/Styles` to populate the "Theme" dropdown.
*   **Vitec Integration:** The app bundles these remote CSS files during the "Export to Vitec" process.

### ⚠️ Known Constraints
*   **No Git Push:** The app's logic for "Git Push" has been removed. Users save directly to the mounted drive.
*   **Azure Mount Latency:** Changes are usually instant, but if files appear missing, a restart of the App Service forces a remount.
