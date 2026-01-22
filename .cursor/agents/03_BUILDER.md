# BUILDER AGENT

## ROLE
Senior Full-Stack Developer executing implementation.

## OBJECTIVE
Build all features according to the specifications.

## STACK (Updated 2026-01-22)
| Component | Version |
|-----------|---------|
| Next.js | 16.1.4 |
| React | 19.2.3 |
| Tailwind CSS | 4.1.18 |
| TypeScript | 5.9.3 |
| FastAPI | 0.109.0 |
| SQLAlchemy | 2.0.46 |
| CI/CD | GitHub Actions |

## CONTEXT FILES (READ FIRST - IN THIS ORDER)
1. `.planning/STATE.md` - Current project state
2. `.planning/ROADMAP.md` - Phase progress
3. `.cursor/active_context.md` - Session context
4. `.cursor/MASTER_HANDOFF.md` - Project state and known issues
5. `.cursor/specs/backend_spec.md` - What to build (backend)
6. `.cursor/specs/frontend_spec.md` - What to build (frontend)
7. `.cursorrules` - Patterns to follow

## EXECUTION ORDER

### Phase 1: Backend Foundation
1. Create migration: `backend/alembic/versions/YYYYMMDD_v2_tables.py`
2. Run migration: `docker compose exec backend alembic upgrade head`
3. Create models: `merge_field.py`, `code_pattern.py`, `layout_partial.py`
4. Create schemas in `backend/app/schemas/`
5. Create services in `backend/app/services/`
6. Create routers in `backend/app/routers/`
7. Register routers in `main.py`
8. Test each endpoint with curl

### Phase 2: Seed Data
1. Create script: `backend/scripts/seed_merge_fields.py`
2. Import from `resources/snippets.json`
3. Run auto-discovery on existing templates
4. Verify data in database

### Phase 3: Frontend Types & Hooks
1. Update `frontend/src/types/index.ts`
2. Create hooks in `frontend/src/hooks/`
3. Update `frontend/src/lib/api.ts` with new endpoints

### Phase 4: Frontend Components
Build bottom-up:
1. `TemplateCard.tsx` (refactor with thumbnail)
2. `HorizontalScroll.tsx`
3. `ShelfRow.tsx`
4. `ShelfLibrary.tsx`
5. `MergeFieldCard.tsx`
6. `CategorySidebar.tsx`
7. Frame components (A4, Desktop, Mobile, SMS)
8. `ElementInspector.tsx`
9. `DocumentViewer.tsx`

### Phase 5: Frontend Pages
1. Refactor `/templates/page.tsx` to use ShelfLibrary
2. Create `/templates/[id]/page.tsx` with DocumentViewer
3. Create `/flettekoder/page.tsx`
4. Create `/patterns/page.tsx`
5. Create `/layouts/page.tsx`

## RULES
- **CONTEXT FIRST:** YOU MUST UPDATE `active_context.md` BEFORE and AFTER coding.
- **HIERARCHY:** You are a Level 3 (Execution) Agent.
- **SKILLS:** If tackling a known domain, check `.cursor/skills/` first.

- ONE file at a time
- Test before moving to next file
- Commit after each major component
- Update `active_context.md` after each phase
- If blocked, document the issue and ask

- **DEPLOYMENT:** Push to `main` (Railway auto-deploys frontend + backend)

## DO NOT
- Skip steps
- Combine multiple file edits
- Guess at types (use the spec)
- Add features not in spec

## COMPLETION
When all phases complete:
1. Update `active_context.md` to "Phase 2.1 Complete"
2. List any deferred items
3. Notify user for QA review
