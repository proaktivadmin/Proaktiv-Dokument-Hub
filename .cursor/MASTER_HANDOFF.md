# MASTER HANDOFF DOCUMENT
# Proaktiv Dokument Hub - Agent Pipeline Context

**Last Updated:** 2026-01-15
**Purpose:** Comprehensive context for AI agents working on this project

---

## 1. PROJECT STATE SUMMARY

### What Works
- Frontend UI loads and renders correctly
- Navigation between pages works
- Template shelf view displays 43 templates
- Template preview with merge field highlighting
- Code editor (Monaco) in template viewer
- Simulator panel detects variables
- Flettekoder page with 142 merge fields
- Azure Blob Storage connection (templates stored correctly)
- GitHub Actions CI/CD pipeline (builds and deploys)
- Container Apps run and respond to requests

### What Is Broken
- **Dashboard API:** Returns 500 error because `/api/dashboard/stats` endpoint doesn't exist
- **Database Persistence:** SQLite in container filesystem resets on every restart
- **No Auto-Migration:** Database tables not created automatically on startup
- **No Seed Data:** Fresh database has no categories, no merge fields
- **Volume Mount Removed:** Azure Files mount was causing container startup failures

---

## 2. CRITICAL FILES LIST

### Infrastructure (Agent 0 - Azure Architect)
| File | Purpose |
|------|---------|
| `infrastructure/bicep/main.bicep` | Azure resource definitions |
| `.github/workflows/deploy-azure.yml` | CI/CD pipeline |
| `backend/Dockerfile` | Backend container image |
| `frontend/Dockerfile` | Frontend container image |
| `backend/scripts/start.sh` | Container startup script |

### Backend (Agent 1 - Systems Architect)
| File | Purpose |
|------|---------|
| `backend/app/main.py` | FastAPI application entry |
| `backend/app/config.py` | Environment configuration |
| `backend/app/database.py` | Database connection |
| `backend/app/models/` | SQLAlchemy models |
| `backend/app/routers/` | API endpoints |
| `backend/app/services/` | Business logic |
| `backend/app/schemas/` | Pydantic schemas |
| `backend/alembic/` | Database migrations |

### Frontend (Agent 2 - Frontend Architect)
| File | Purpose |
|------|---------|
| `frontend/next.config.js` | Next.js config with API rewrites |
| `frontend/src/lib/api.ts` | API client (uses relative URLs) |
| `frontend/src/app/page.tsx` | Dashboard page |
| `frontend/src/app/templates/page.tsx` | Templates shelf view |
| `frontend/src/components/` | React components |
| `frontend/src/hooks/` | Custom React hooks |
| `frontend/src/types/` | TypeScript interfaces |

### Context Files
| File | Purpose |
|------|---------|
| `CLAUDE.md` | Project quick reference |
| `.cursor/active_context.md` | Current phase and status |
| `.cursorrules` | Coding patterns and rules |

---

## 3. KNOWN ISSUES (With Error Details)

### Issue 1: Missing Dashboard Stats API
```
URL: /api/dashboard/stats
Expected: { total: number, published: number, draft: number, downloads: number }
Actual: 404 Not Found
Frontend Error: "Request failed with status code 500"
```

**Fix Required:** Create endpoint in `backend/app/routers/dashboard.py`

### Issue 2: Ephemeral Database
```
Current Config (main.bicep):
  DATABASE_URL = 'sqlite:///./app.db'
  
Problem: Container filesystem is ephemeral
Result: All data lost when container restarts
```

**Fix Options:**
1. Azure Files volume mount (was tried, failed)
2. Azure PostgreSQL Flexible Server ($15/mo)
3. SQLite with blob backup on shutdown

### Issue 3: No Startup Initialization
```
Current: Container starts FastAPI directly
Missing: 
  1. Run alembic upgrade head
  2. Seed default data
  3. Then start uvicorn
```

**Fix Required:** Create proper `start.sh` entrypoint script

### Issue 4: Volume Mount Failure (Historical)
```
Error: MountVolume.Setup failed for volume "database-volume"
       mount failed: exit status 32
       Permission denied
       
Root Cause: Azure Files storage not linked to Container Apps Environment
```

**Was "Fixed" By:** Removing volume mount entirely (not a real fix)

---

## 4. DEPLOYMENT INFORMATION

### URLs
| Service | URL | Status |
|---------|-----|--------|
| Frontend | https://dokumenthub-web.greenmushroom-2067e5c8.norwayeast.azurecontainerapps.io/ | Running |
| Backend | https://dokumenthub-api.greenmushroom-2067e5c8.norwayeast.azurecontainerapps.io/ | Running |
| API Docs | https://dokumenthub-api.greenmushroom-2067e5c8.norwayeast.azurecontainerapps.io/docs | Working |
| Health | https://dokumenthub-api.greenmushroom-2067e5c8.norwayeast.azurecontainerapps.io/api/health | Healthy |

### Azure Resources
| Resource | Value |
|----------|-------|
| Subscription ID | `1b7869ae-d3a4-445f-9ebf-bf0c3bf52309` |
| Resource Group | `rg-dokumenthub-prod` |
| Location | `norwayeast` |
| Container Apps Environment | `dokumenthub-env` |
| Backend App | `dokumenthub-api` |
| Frontend App | `dokumenthub-web` |

### GitHub Repository
- **URL:** https://github.com/Adrian12341234-code/Proaktiv-Dokument-Hub
- **Branch:** `V2-development` (triggers deployment)
- **Workflow:** `.github/workflows/deploy-azure.yml`

---

## 5. GITHUB SECRETS

| Secret Name | Purpose | Status |
|-------------|---------|--------|
| `AZURE_CREDENTIALS` | Service Principal JSON | Configured |
| `AZURE_STORAGE_CONNECTION_STRING` | Blob storage connection | Configured |
| `AZURE_STORAGE_ACCOUNT_NAME` | Storage account name | Configured |
| `AZURE_STORAGE_ACCOUNT_KEY` | Storage account key | Configured |
| `SECRET_KEY` | JWT/session signing | Auto-generated if missing |

---

## 6. TECH STACK

| Layer | Technology | Version |
|-------|------------|---------|
| Frontend | Next.js | 14.1.0 |
| UI Components | Shadcn/UI | Latest |
| Styling | Tailwind CSS | 3.x |
| Backend | FastAPI | 0.104+ |
| Database | SQLite (ephemeral) | - |
| ORM | SQLAlchemy | 2.x |
| Migrations | Alembic | 1.x |
| Container | Docker | - |
| Cloud | Azure Container Apps | - |
| Storage | Azure Blob Storage | - |
| CI/CD | GitHub Actions | - |

---

## 7. SUCCESS CRITERIA

The deployment is considered "fixed" when ALL of these pass:

- [ ] Backend `/api/health` returns `{"status": "healthy"}`
- [ ] Frontend loads without any error banners
- [ ] Dashboard shows template counts (not 500 error)
- [ ] Template list populates correctly
- [ ] Upload a new template and verify it persists
- [ ] Restart the container and verify data is still there
- [ ] API docs page loads at `/docs`

---

## 8. AGENT PIPELINE

### Execution Order
1. **Azure DevOps Architect** (`/azure-architect`) → Fixes infrastructure
2. **Systems Architect** (`/architect`) → Backend specifications
3. **Frontend Architect** (`/frontend-architect`) → Frontend specifications  
4. **Builder** (`/builder`) → Implementation
5. **Debugger Mode** → QA verification

### Model Recommendations
| Agent | Model | Reason |
|-------|-------|--------|
| Azure DevOps Architect | Claude Opus 4.5 / o1-pro | Complex infrastructure |
| Systems Architect | Claude Opus 4.5 | Backend architecture |
| Frontend Architect | Claude Sonnet 4 | Fast, good at UI |
| Builder | Claude Sonnet 4 | Fast execution |
| Debugger | Claude Opus 4.5 | Deep debugging |

---

## 9. QUICK COMMANDS

```bash
# Local development
docker compose up -d

# Check backend health
curl http://localhost:8000/api/health

# Run migrations locally
docker compose exec backend alembic upgrade head

# View logs
docker compose logs -f backend

# Trigger GitHub deployment
git push origin V2-development
```

---

## 10. NOTES FOR AGENTS

### Do NOT:
- Skip reading context files
- Mark issues as "fixed" without verification
- Remove working code to "simplify"
- Add features not in the spec
- Use `any` type in TypeScript
- Put business logic in routers

### DO:
- Read all context files first
- Test each change before moving on
- Document any new issues discovered
- Ask if something is unclear
- Follow existing code patterns
- Keep solutions simple (single-user app)
