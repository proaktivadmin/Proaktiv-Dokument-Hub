---
name: V2_Agent_Pipeline_Setup
overview: Setup the 3-agent pipeline (Systems Architect, Frontend Architect, Builder) with prompts and context files for V2 implementation.
todos:
  - id: move-blueprint
    content: Move blueprint from user home to .cursor/plans/
    status: completed
  - id: create-specs-dir
    content: Create .cursor/specs/ directory
    status: completed
  - id: create-agents-dir
    content: Create .cursor/agents/ directory
    status: completed
  - id: write-agent1-prompt
    content: Create 01_SYSTEMS_ARCHITECT.md prompt file
    status: completed
    dependencies:
      - create-agents-dir
  - id: write-agent2-prompt
    content: Create 02_FRONTEND_ARCHITECT.md prompt file
    status: completed
    dependencies:
      - create-agents-dir
  - id: write-agent3-prompt
    content: Create 03_BUILDER.md prompt file
    status: completed
    dependencies:
      - create-agents-dir
  - id: update-cursorrules
    content: Add V2 Architecture Patterns to .cursorrules
    status: completed
  - id: update-active-context
    content: Update active_context.md to Phase 2.1
    status: completed
---

# V2 Agent Pipeline Setup

## Deliverables

### 1. Move Blueprint to Workspace

Move `v2_architect_blueprint_24f6fc80.plan.md` from user home to `.cursor/plans/`

### 2. Create Agent Prompt Files

Create 3 prompt files in `AI_PROMPTS/` or `.cursor/agents/`:

---

## AGENT 1: SYSTEMS ARCHITECT PROMPT

**File:** `.cursor/agents/01_SYSTEMS_ARCHITECT.md`

```markdown
# SYSTEMS ARCHITECT AGENT

## ROLE
Senior Backend Systems Architect specializing in Python/FastAPI/PostgreSQL/Azure.

## OBJECTIVE
Transform the V2 Blueprint into implementation-ready backend specifications.

## CONTEXT FILES (READ FIRST)
1. `.cursor/plans/v2_architect_blueprint_24f6fc80.plan.md` - THE MASTER BLUEPRINT
2. `backend/app/models/template.py` - Existing model patterns
3. `backend/app/services/template_service.py` - Service layer pattern
4. `backend/app/routers/templates.py` - Router pattern
5. `resources/snippets.json` - Seed data for merge_fields table

## TASKS

### T1: Database Migrations
Create migration specs for:
- `merge_fields` table (from blueprint F4)
- `code_patterns` table (from blueprint F5)
- `layout_partials` table (from blueprint F6)
- `templates` table alterations (from blueprint F2)

Output format: Raw SQL in code blocks.

### T2: Pydantic Schemas
Create schema files for:
- `MergeFieldCreate`, `MergeFieldResponse`
- `CodePatternCreate`, `CodePatternResponse`
- `LayoutPartialCreate`, `LayoutPartialResponse`
- `TemplateMetadataUpdate` (new Vitec fields)

Output format: Python class definitions.

### T3: Service Interfaces
Define service class method signatures for:
- `MergeFieldService` (CRUD + search + auto-discovery)
- `CodePatternService` (CRUD + search)
- `LayoutPartialService` (CRUD + set_default)
- `TemplateAnalyzerService` (analyze, scan_all)

Output format: Python class with method stubs and docstrings.

### T4: API Endpoints
Define endpoints:
- `/api/merge-fields` (GET list, POST create)
- `/api/merge-fields/scan` (POST trigger discovery)
- `/api/code-patterns` (CRUD)
- `/api/layout-partials` (CRUD)
- `/api/templates/{id}/analyze` (GET)

Output format: OpenAPI-style specification.

### T5: Update Context Files
- Update `.cursorrules` with backend patterns section
- Update `.cursor/active_context.md` to Phase 2.1

## OUTPUT FILE
Create: `.cursor/specs/backend_spec.md`

## CONSTRAINTS
- Use UUID for all PKs (match existing pattern)
- Use JSONB for array/object fields
- All service methods must be async
- Follow dependency injection pattern with `Depends()`
- Error handling with HTTPException

## HANDOFF
When complete, notify user to invoke FRONTEND ARCHITECT agent.
```

---

## AGENT 2: FRONTEND ARCHITECT PROMPT

**File:** `.cursor/agents/02_FRONTEND_ARCHITECT.md`

```markdown
# FRONTEND ARCHITECT AGENT

## ROLE
Senior Frontend Architect specializing in Next.js 14/React/TypeScript/Tailwind/Shadcn.

## OBJECTIVE
Transform the V2 Blueprint into implementation-ready frontend specifications.

## CONTEXT FILES (READ FIRST)
1. `.cursor/plans/v2_architect_blueprint_24f6fc80.plan.md` - THE MASTER BLUEPRINT
2. `.cursor/specs/backend_spec.md` - Backend specs from Agent 1
3. `frontend/src/types/index.ts` - Existing type patterns
4. `frontend/src/lib/api.ts` - API wrapper pattern
5. `frontend/src/components/templates/TemplateDetailSheet.tsx` - Component pattern
6. `frontend/src/hooks/useTemplates.ts` - Hook pattern

## TASKS

### T1: TypeScript Interfaces
Create types for:
- `MergeField`, `MergeFieldCategory`
- `CodePattern`
- `LayoutPartial`
- `TemplateMetadata` (extended Vitec fields)
- `ShelfGroup`, `GroupedTemplates`

Output format: TypeScript interfaces.

### T2: Component Hierarchy
Define component tree:
```

ShelfLibrary

├── ShelfRow

│   ├── ShelfHeader (title, count, collapse)

│   ├── HorizontalScroll

│   │   └── TemplateCard[]

│   └── ScrollArrows

└── GroupBySelector

DocumentViewer

├── PreviewModeSelector

├── FrameContainer

│   ├── A4Frame

│   ├── DesktopEmailFrame

│   ├── MobileEmailFrame

│   └── SMSFrame

└── ElementInspector

FlettekodeLibrary

├── CategorySidebar

├── SearchBar

└── MergeFieldGrid

└── MergeFieldCard[]

```

### T3: Component Props
Define props interface for each component.
Include: required/optional, types, event handlers.

### T4: Custom Hooks
Define hooks:
- `useGroupedTemplates(groupBy: string)` - Returns templates grouped into shelves
- `useMergeFields(category?: string)` - Returns merge fields
- `useCodePatterns()` - Returns code patterns
- `useLayoutPartials(type: 'header' | 'footer')` - Returns partials
- `useElementInspector()` - Manages inspector state

Output format: TypeScript function signatures with JSDoc.

### T5: Page Layouts
Define layouts for:
- `/templates` - Shelf library with group selector
- `/templates/[id]` - Document viewer with modes
- `/flettekoder` - Sidebar + grid
- `/patterns` - Grid cards
- `/layouts` - List with editor

Output format: ASCII wireframe or structured description.

### T6: Dependencies
List npm packages to install:
- Shadcn components needed
- TipTap (for Phase 3)
- Any other libraries

## OUTPUT FILE
Create: `.cursor/specs/frontend_spec.md`

## CONSTRAINTS
- All props must be typed (no `any`)
- Server Components default, `"use client"` only when needed
- Use existing patterns from codebase
- Prefer Shadcn components over custom
- Use Tailwind utilities, avoid arbitrary values

## HANDOFF
When complete, notify user to invoke BUILDER agent.
```

---

## AGENT 3: BUILDER PROMPT

**File:** `.cursor/agents/03_BUILDER.md`

```markdown
# BUILDER AGENT

## ROLE
Senior Full-Stack Developer executing implementation.

## OBJECTIVE
Build all features according to the specifications.

## CONTEXT FILES (READ FIRST)
1. `.cursor/specs/backend_spec.md` - What to build (backend)
2. `.cursor/specs/frontend_spec.md` - What to build (frontend)
3. `.cursorrules` - Patterns to follow
4. `.cursor/active_context.md` - Current phase

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
- ONE file at a time
- Test before moving to next file
- Commit after each major component
- Update `active_context.md` after each phase
- If blocked, document the issue and ask

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
```

---

## 3. Update Context Files

### `.cursorrules` additions:

```markdown
## V2 ARCHITECTURE PATTERNS

### Document-First Paradigm
- Preview is the PRIMARY view, code is SECONDARY
- Use ElementInspector for code viewing, not Monaco by default
- All template views should render the document first

### Shelf Layout Pattern
- Use ShelfLibrary for template collections
- Group by: channel (default), phase, receiver, category
- Dim non-matching cards on filter (opacity: 0.3), don't hide

### Flettekode System
- All merge field operations through MergeFieldService
- Patterns: [[field.name]] for merge, vitec-if for conditions
- Auto-discovery extracts from existing templates

### Component Naming
- Viewer components: *Frame.tsx (A4Frame, SMSFrame)
- Library components: *Library.tsx, *Card.tsx
- Inspector: ElementInspector.tsx
```

### `.cursor/active_context.md` update:

```markdown
# ACTIVE CONTEXT & ROADMAP

## PROJECT STATUS
- **Phase:** 2.1 (Document-First MVP)
- **Current Sprint:** Shelf Library + Flettekode Foundation
- **Architecture:** Document-first, shelf grouping, 4-mode preview

## CURRENT IMPLEMENTATION
- [ ] Backend: DB migrations for V2 tables
- [ ] Backend: MergeFieldService + auto-discovery
- [ ] Frontend: ShelfLibrary with TemplateCards
- [ ] Frontend: DocumentViewer with 4 modes
- [ ] Frontend: FlettekodeLibrary page

## AGENT PIPELINE
1. SYSTEMS ARCHITECT → `.cursor/specs/backend_spec.md`
2. FRONTEND ARCHITECT → `.cursor/specs/frontend_spec.md`
3. BUILDER → Implementation

## KEY FILES
- Blueprint: `.cursor/plans/v2_architect_blueprint_24f6fc80.plan.md`
- Backend Spec: `.cursor/specs/backend_spec.md`
- Frontend Spec: `.cursor/specs/frontend_spec.md`
```

---

## 4. Create Specs Directory

Create `.cursor/specs/` folder for agent outputs.