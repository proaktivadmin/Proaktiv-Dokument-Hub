# Azure Deployment Strategy for Proaktiv Document Hub

## Why Azure is a Perfect Fit
Unlike Firebase (which is serverless and ephemeral), **Azure App Service** allows us to run the application almost exactly as it runs on your local machine, but in the cloud.

### Key Benefits for Your Use Case
1.  **No Code Rewrites needed:** We can mount **Persistent Storage** (Azure Files) effectively giving the cloud server a "hard drive" that persists data. Your current `fs.writeFile` code will continue to work.
2.  **Corporate Security:** We can enable **Microsoft Entra ID (Azure AD)** authentication with a single switch. This puts the entire app behind your corporate login (SSO), satisfying the "safety notifications" concern.
3.  **Tenant Integration:** It lives inside your Microsoft tenant, compliant with your organization's policies.

---

## Technical Implementation Plan

### 1. Compute: Azure App Service (Node.js)
*   **Resource:** Create a **Web App** (Linux or Windows plan).
*   **Runtime:** Node.js 18 or 20 LTS.
*   **Scaling:** "Basic" (B1) tier is sufficient for internal tools and supports custom domains/SSL.

### 2. Storage: Azure Files Mount
*   **Resource:** Create a **Storage Account** and a **File Share** (e.g., `proaktiv-hub-data`).
*   **Configuration:** largely done in the Azure Portal > Configuration > **Path mappings**.
    *   We mount the Azure File Share to the path `/home/site/wwwroot/library` (Linux) or similar.
*   **Result:** When `server.js` writes to `library/`, it actually saves to the Azure Storage Account, ensuring data is safe even if the app restarts.

### 3. Security: "Easy Auth"
*   **Feature:** **App Service Authentication**.
*   **Provider:** Microsoft Identity Provider.
*   **Action:** Restrict access to "Require authentication".
*   **Result:** Anyone accessing the URL must sign in with their `@proaktiv.no` (or tenant) email. The app doesn't need to handle login logic itself!

### 4. Deployment Pipeline
*   **Method:** Connect your GitHub repository to the App Service Deployment Center.
*   **Process:** Pushing to `main` triggers a build and deploy automatically.

## Comparison: Firebase vs. Azure

| Feature | Firebase Hosting/Functions | Azure App Service |
| :--- | :--- | :--- |
| **Code Changes** | **High** (Must rewrite `fs` to Cloud Storage) | **None/Low** (Standard Node.js support) |
| **Persistence** | Ephemeral (Data lost on restart) | **Persistent** (Volume Mounts) |
| **Auth** | Manual Firebase Auth integration | **Automatic** (Entra ID Overlay) |
| **Complexity** | High (Serverless architecture) | **Low** (Traditional Server model) |

## Next Steps (When you are ready)
Since you have GA access:
1.  Create a **Resource Group** (e.g., `rg-proaktiv-hub`).
2.  Create a **Storage Account** for the library files.
3.  Create the **Web App**.
4.  Configure the **Path Mapping** to mount the storage.
5.  Push the code.
