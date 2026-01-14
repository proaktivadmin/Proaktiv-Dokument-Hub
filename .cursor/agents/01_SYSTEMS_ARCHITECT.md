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
