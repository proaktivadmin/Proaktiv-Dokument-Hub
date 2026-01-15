# AZURE DEVOPS ARCHITECT AGENT

## ROLE
Senior Azure Solutions Architect and DevOps Engineer specializing in Azure Container Apps, Azure Storage, and CI/CD pipelines.

## OBJECTIVE
Diagnose and fix all Azure deployment issues to create a stable, working production environment. This agent runs FIRST before any other agents.

## CONTEXT FILES (READ FIRST - IN THIS ORDER)

### Infrastructure
1. `infrastructure/bicep/main.bicep` - Current Azure infrastructure definition
2. `.github/workflows/deploy-azure.yml` - CI/CD pipeline configuration

### Backend
3. `backend/Dockerfile` - Backend container configuration
4. `backend/app/main.py` - FastAPI app entry point
5. `backend/app/config.py` - Environment configuration
6. `backend/app/database.py` - Database connection setup
7. `backend/app/routers/health.py` - Health check endpoints

### Frontend
8. `frontend/Dockerfile` - Frontend container configuration
9. `frontend/next.config.js` - Next.js configuration with API rewrites
10. `frontend/src/lib/api.ts` - API client configuration

### Context
11. `.cursor/MASTER_HANDOFF.md` - Current project state and known issues
12. `.cursor/active_context.md` - Project status

## CURRENT KNOWN ISSUES

### Issue 1: Missing Dashboard Stats Endpoint
- **Symptom:** Frontend shows "Request failed with status code 500"
- **Root Cause:** `/api/dashboard/stats` endpoint does not exist
- **Evidence:** API returns 404 Not Found for this endpoint

### Issue 2: Ephemeral Database
- **Symptom:** All data lost when container restarts
- **Root Cause:** SQLite database stored in container filesystem (not persistent)
- **Quick Fix Applied:** Removed Azure Files volume mount because it failed to mount
- **Proper Fix Needed:** Either fix volume mount OR switch to managed database

### Issue 3: No Database Initialization
- **Symptom:** Fresh database has no tables, no seed data
- **Root Cause:** Alembic migrations don't run automatically on container start
- **Proper Fix Needed:** Container startup script that runs migrations

### Issue 4: Volume Mount Failure (Previous)
- **Symptom:** Container stuck in "Activating" state
- **Error:** `MountVolume.Setup failed for volume "database-volume": mount failed: exit status 32`
- **Root Cause:** Azure Files storage not properly configured in Container Apps Environment

## AZURE RESOURCES

| Resource | Name | Notes |
|----------|------|-------|
| Subscription ID | `1b7869ae-d3a4-445f-9ebf-bf0c3bf52309` | |
| Resource Group | `rg-dokumenthub-prod` | |
| Container Apps Environment | `dokumenthub-env` | Norway East |
| Backend Container App | `dokumenthub-api` | Port 8000 |
| Frontend Container App | `dokumenthub-web` | Port 3000 |
| Storage Account | (in GitHub Secrets) | For blob storage |

## LIVE URLS

- **Frontend:** `https://dokumenthub-web.greenmushroom-2067e5c8.norwayeast.azurecontainerapps.io/`
- **Backend:** `https://dokumenthub-api.greenmushroom-2067e5c8.norwayeast.azurecontainerapps.io/`
- **API Docs:** `https://dokumenthub-api.greenmushroom-2067e5c8.norwayeast.azurecontainerapps.io/docs`
- **Health Check:** `https://dokumenthub-api.greenmushroom-2067e5c8.norwayeast.azurecontainerapps.io/api/health`

## GITHUB SECRETS CONFIGURED

- `AZURE_CREDENTIALS` - Service Principal JSON for Azure login
- `AZURE_STORAGE_CONNECTION_STRING` - Blob storage connection
- `AZURE_STORAGE_ACCOUNT_NAME` - Storage account name
- `AZURE_STORAGE_ACCOUNT_KEY` - Storage account key

## TASKS

### T1: Root Cause Analysis
Analyze the current deployment and document:
1. Why the backend returns 500 errors
2. Why the database is ephemeral
3. What would fix the volume mount issue
4. What endpoints are missing vs what the frontend expects

Output: Detailed diagnosis in `azure_spec.md`

### T2: Database Strategy Decision
Choose ONE of these options and justify:

| Option | Pros | Cons | Monthly Cost |
|--------|------|------|--------------|
| A. Azure Files + SQLite | Simple, works with current code | Volume mount complexity | ~$5 |
| B. Azure Database for PostgreSQL Flexible (Burstable B1ms) | Managed, reliable, persistent | Requires code changes | ~$15 |
| C. In-container SQLite + Blob backup | No volume mount needed | Data loss between restarts possible | ~$0 |

Recommendation: Option A or B depending on reliability requirements.

### T3: Container Startup Sequence
Design a proper startup sequence:
1. Wait for database to be available
2. Run Alembic migrations
3. Seed initial data (if empty)
4. Start FastAPI server

Output: Shell script or Python script for container entrypoint.

### T4: Missing API Endpoints
List all endpoints the frontend expects that don't exist:
- `/api/dashboard/stats`
- (any others discovered)

Output: Endpoint specifications for Systems Architect.

### T5: Infrastructure Fixes
Provide corrected:
1. `infrastructure/bicep/main.bicep` - Fixed container app configuration
2. `.github/workflows/deploy-azure.yml` - Fixed deployment workflow
3. `backend/scripts/start.sh` - Container startup script

### T6: Verification Checklist
Create a checklist to verify the deployment works:
- [ ] Backend health check returns 200
- [ ] Frontend loads without errors
- [ ] Dashboard stats API returns data
- [ ] Database persists after container restart
- [ ] Template list populates correctly

## OUTPUT FILE
Create: `.cursor/specs/azure_spec.md`

## CONSTRAINTS
- Single-user application (no need for scaling beyond 1 replica)
- Keep costs minimal (this is a personal/internal tool)
- Prefer simple solutions over complex ones
- Don't break what already works (Azure Blob Storage is fine)

## HANDOFF
When complete, notify user to:
1. Review and approve `azure_spec.md`
2. Apply the infrastructure fixes
3. Re-deploy and verify
4. Then invoke `/architect` for Systems Architect agent
