# API Tooling

This folder contains API request collections for testing and debugging.

## Tools

| Tool | Use Case |
|------|----------|
| **Bruno** | Full-featured API client with GUI, environments, and request history |
| **REST Client** | Quick `.http` file calls directly in Cursor/VS Code |

---

## Bruno Setup

1. Open Bruno app
2. Click **Open Collection** → navigate to this `api/` folder
3. Select environment (QA or Production) from dropdown
4. **Add secrets**: When prompted, enter `hubProductLogin` and `hubAccessKey`
   - Secrets are stored locally in `*.bru.secrets` files (gitignored)

### Folder Structure

```
api/
├── bruno.json              # Collection config
├── environments/
│   ├── qa.bru              # QA environment (proatest.qa.vitecnext.no)
│   └── production.bru      # Production environment (hub.megler.vitec.net)
├── vitec-hub/              # Direct Vitec Hub API calls
│   ├── Account Methods.bru
│   ├── Get Departments.bru
│   └── Get Employees.bru
└── backend/                # Our backend API calls
    ├── Sync Offices.bru
    ├── Sync Employees.bru
    ├── List Offices.bru
    └── List Employees.bru
```

---

## REST Client Setup (Cursor/VS Code)

1. Install extension: `humao.rest-client`
2. Open `requests.http`
3. Add secrets to `.vscode/settings.json`:

```json
{
  "rest-client.environmentVariables": {
    "qa": {
      "hubProductLogin": "YOUR_PRODUCT_LOGIN",
      "hubAccessKey": "YOUR_ACCESS_KEY"
    }
  }
}
```

4. Select environment: `Ctrl+Shift+P` → "Rest Client: Switch Environment" → `qa`
5. Click "Send Request" above any request

---

## Common Workflows

### Verify Vitec Hub Access
1. Run **Account Methods** to confirm credentials work
2. Check response for allowed `installationIds` and `functions`

### Sync Data
1. Run **Sync Offices** first (employees need offices to exist)
2. Run **Sync Employees**
3. Check results in **List Offices** / **List Employees**

### Debug Sync Issues
1. Run **Get Departments** / **Get Employees** directly against Hub
2. Compare with **List Offices** / **List Employees** from our DB
3. Check for missing `vitec_department_id` or `vitec_employee_id`
