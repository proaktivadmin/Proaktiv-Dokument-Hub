# ACTIVE CONTEXT & ROADMAP

## 📌 PROJECT STATUS
- **Phase:** 2.0 (Cloud-Ready MVP)
- **Current Sprint:** UI Polish + Template Previewer Enhancements.
- **Last Milestone:** ✅ Azure Blob Storage Integration + Legacy Migration Complete.
- **Next Milestone:** Production Deployment & Entra ID Authentication.

## 🏗️ ARCHITECTURE DECISIONS
1. **Stack:** Next.js 14 (Frontend) + FastAPI (Backend) in a Monorepo.
2. **Database:** PostgreSQL (Docker container, `dokument-hub-db`).
3. **Storage:** Azure Blob Storage (`proaktivgruppen.blob.core.windows.net/templates`).
4. **Auth:** Azure Easy Auth (Mocked locally via headers).
5. **Vitec Integration:** 
   - Uses a "Proxy Pattern" (Frontend -> Python Backend -> Vitec API).
   - Currently running in "Mock Mode" for development.

## ✅ COMPLETED FEATURES
- Dashboard "Hydration" (Real stats from backend).
- Template Upload (Files go to Azure Blob Storage, DB record created).
- Template Preview (HTML rendered in sandboxed iframe with Vitec CSS).
- Template Detail Sheet (Slide-out panel with preview, metadata, actions).
- Smart Sanitizer (Detects if HTML needs cleaning, skips valid templates).
- Legacy Migration (43 templates imported from `_legacy_v1/library` to Azure).
- **Proaktiv Premium UI** (Navy/Bronze/Beige brand identity, serif typography).
- Client Management (Create/List).
- Invoice Management (Basic CRUD).

## 🚧 IN PROGRESS / TODO
1. **Preview Enhancements:** A4 page simulation, Mobile/iMessage preview modes.
2. **Category Management:** Associate templates with categories in UI.
3. **Download Functionality:** Enable file download from Azure Blob Storage.

## ⚠️ KNOWN ISSUES / CONSTRAINTS
- **CORS:** Frontend runs on varying ports (3000/3001), Backend whitelist must match.
- **Validation:** Frontend `api.ts` types must strictly match Pydantic models.
- **Docker:** Backend container name may change on restart (use `docker ps` to verify).

## 📊 AZURE STORAGE STATUS
- **Container:** `templates`
- **Folders:** `legacy/` (38 files), `company-portal/` (5 files)
- **Total Templates:** 43 (all with real Azure URLs)
- **Connection:** ✅ Verified and working
