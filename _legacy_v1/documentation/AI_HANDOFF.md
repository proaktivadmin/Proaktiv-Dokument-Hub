# AI Handoff Protocol 🤖

**READ THIS FIRST.**
This file is the **living status report** of the project.
*   **Incoming Agent:** Read this to orient yourself.
*   **Outgoing Agent:** You **MUST** update this file, Commit, and **Push to Origin** before you leave.

---

## 1. State of the World (Last Updated: 2026-01-15)

| Aspect | Status |
|--------|--------|
| **Project** | Proaktiv Dokument Hub V2.6 |
| **Phase** | Document Preview & Simulator Enhancements |
| **Status** | ✅ **READY FOR AZURE DEPLOYMENT** |
| **Stack** | Next.js 14 + FastAPI + PostgreSQL + Azure Blob Storage |
| **Templates** | 43 templates live in Azure Storage |

---

## 2. What Was Just Completed (V2.6)

### New Features
1. **Live Document Preview Thumbnails** - Template cards show scaled-down previews of actual document content using lazy-loaded iframes
2. **A4 Page Break Visualization** - Toggle to show red dashed lines where A4 pages would break (257mm content height)
3. **Simulator Test Data Persistence** - Default test values saved to localStorage, with Save/Reset/Clear buttons
4. **Quick Test Data Toggle** - Button in preview toolbar to switch between original and test data
5. **Visual Code Generator** - Flettekoder page now has a "Kodegenerator" tab for building Vitec code snippets without coding

### Files Changed
- `frontend/src/components/shelf/TemplateCard.tsx` - Live previews
- `frontend/src/components/templates/TemplatePreview.tsx` - A4 visualization + toggle
- `frontend/src/components/templates/SimulatorPanel.tsx` - Persistence
- `frontend/src/components/templates/TemplateDetailSheet.tsx` - State management
- `frontend/src/components/flettekoder/CodeGenerator.tsx` - Visual builder
- `frontend/public/vitec-theme.css` - A4 page break CSS

---

## 3. Critical Context Files

Read these in order:
1. **`.cursor/active_context.md`** - Current status and feature list
2. **`CLAUDE.md`** - Project conventions and patterns
3. **`documentation/BRAND_GUIDE.md`** - Design rules
4. **`.cursor/specs/backend_spec.md`** - Backend architecture
5. **`.cursor/specs/frontend_spec.md`** - Frontend architecture

---

## 4. Architecture Quick Reference

### Document-First Paradigm
- **Preview is PRIMARY**, code is SECONDARY
- Templates displayed as cards with live thumbnails
- Shelf layout with horizontal grouping by channel

### Key Patterns
- **Merge Fields:** `[[field.name]]` or `[[*field.name]]` (required)
- **Conditions:** `vitec-if="expression"`
- **Loops:** `vitec-foreach="item in collection"`

### Directory Structure
```
frontend/
├── src/app/           # Next.js pages (templates, flettekoder, sanitizer)
├── src/components/    # React components (shelf/, templates/, flettekoder/)
├── src/hooks/         # Custom hooks (useMergeFields, useTemplates)
├── src/lib/           # API client, utilities
└── public/            # Static assets (vitec-theme.css)

backend/
├── app/models/        # SQLAlchemy models
├── app/services/      # Business logic (async)
├── app/routers/       # FastAPI endpoints
└── app/schemas/       # Pydantic models
```

---

## 5. "Don't Do This" (Common Pitfalls)

| ❌ Don't | ✅ Do Instead |
|----------|---------------|
| Use `any` in TypeScript | Use proper types from `@/types` |
| Put logic in routers | Put it in `services/` |
| Edit templates via Git | Use the app UI or Azure Storage |
| Skip the specs | Read `.cursor/specs/` before building |
| Use Monaco as default view | Show document preview first |
| Hide filtered cards | Dim them (opacity 0.3) |

---

## 6. Operational Protocols (MANDATORY)

### Git Operations
- **Atomic Commits:** Always `commit` AND `push` in sequence
- **Commit Quality:** Every commit needs a **Title** (feat/fix/docs) AND **Body**
- **Docs Sync:** Update README, HANDOFF, or active_context.md with code changes

### Before Leaving
1. Update this file with what you did
2. Update `.cursor/active_context.md` with current status
3. Commit all changes with descriptive message
4. Push to GitHub
5. Deploy to Azure if applicable

---

## 7. Environment Setup

```bash
# Start development environment
docker compose up -d

# Backend health check
curl http://localhost:8000/api/health

# Frontend
http://localhost:3000

# Database access
docker compose exec db psql -U postgres -d dokument_hub
```

---

## 8. Next Actions (For Future Sessions)

Priority order:
1. [ ] Backend: PUT `/api/templates/{id}/content` - Save edited content
2. [ ] Backend: PUT `/api/templates/{id}/settings` - Save settings
3. [ ] Add more Vitec Logic patterns to `snippets.json`
4. [ ] Generate static thumbnails for faster card loading
5. [ ] Template versioning UI

---

## 9. Deployment Info

| Environment | URL |
|-------------|-----|
| **Local** | http://localhost:3000 |
| **Azure Production** | (Deploy via existing CI/CD) |
| **Azure Storage** | templates container with legacy/ and company-portal/ folders |

---

*Good luck, agent. The codebase is in good shape.* 🚀
