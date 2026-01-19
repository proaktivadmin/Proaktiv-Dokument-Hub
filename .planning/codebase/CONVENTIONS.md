# Coding Conventions

**Analysis Date:** 2025-01-20

## Naming Patterns

**Files:**
- TypeScript components: PascalCase (`TemplateCard.tsx`, `DocumentViewer.tsx`)
- TypeScript utilities/hooks: camelCase (`useTemplates.ts`, `api.ts`)
- Python modules: snake_case (`template_service.py`, `sanitizer_service.py`)
- Type definition files: snake_case or kebab-case in subdirs (`v2/merge-fields.ts`)

**Functions:**
- TypeScript: camelCase (`fetchTemplates`, `handleError`, `loadPreviewContent`)
- Python: snake_case (`get_list`, `sync_from_hub`, `_normalize_text`)
- Private Python methods: prefix with underscore (`_map_employee_payload`, `_extract_department_id`)

**Variables:**
- TypeScript: camelCase (`isLoading`, `templateId`, `previewContent`)
- Python: snake_case (`template_id`, `page_count`, `created_at`)
- Constants: UPPER_SNAKE_CASE in Python (`PRESERVE_STYLES`, `SYSTEM_MARKERS`)

**Types/Interfaces:**
- TypeScript: PascalCase with descriptive suffixes (`TemplateListResponse`, `UseTemplatesReturn`, `ButtonProps`)
- Python Pydantic models: PascalCase (`TemplateUpdateRequest`, `EmployeeCreate`)

**React Components:**
- Functional components only, using arrow function or function declaration
- Props interfaces named `{ComponentName}Props`
- Viewer components: `*Frame.tsx` (`A4Frame.tsx`)
- Library components: `*Library.tsx`, `*Card.tsx` (`ShelfLibrary.tsx`, `TemplateCard.tsx`)
- Dialogs: `*Dialog.tsx` (`NewFolderDialog.tsx`, `PreviewDialog.tsx`)

**Database Models:**
- SQLAlchemy models: PascalCase class names (`Template`, `Employee`, `Office`)
- Table names: auto-generated snake_case plural (`templates`, `employees`)
- Junction tables: explicit snake_case (`template_tags`, `template_categories`)

## Code Style

**Formatting:**
- Frontend: No explicit Prettier config (Next.js defaults)
- Backend: No explicit formatter config (standard Python conventions)
- Indentation: 2 spaces (TypeScript), 4 spaces (Python)

**Linting:**
- Frontend: ESLint with `eslint-config-next` (v14.1.0)
- Config: Default Next.js ESLint rules (`next lint`)
- Backend: No explicit linting tool configured

**TypeScript Configuration:**
- Strict mode enabled (`"strict": true`)
- Path alias: `@/*` maps to `./src/*`
- No `any` type allowed (per project guidelines)
- Module resolution: `bundler`

## Import Organization

**Frontend Order:**
1. React imports (`"use client"` directive first if needed)
2. External library imports (`lucide-react`, `@radix-ui/*`)
3. Internal UI components (`@/components/ui/*`)
4. Internal feature components (`@/components/*`)
5. Hooks (`@/hooks/*`)
6. Lib/utilities (`@/lib/*`)
7. Types (`@/types/*`)

**Example from `frontend/src/components/viewer/DocumentViewer.tsx`:**
```typescript
"use client";

import { useState, useEffect } from "react";
import { Settings, Download, ArrowLeft } from "lucide-react";
import { Button } from "@/components/ui/button";
import { PreviewModeSelector, type PreviewMode } from "./PreviewModeSelector";
import { A4Frame } from "./A4Frame";
import { ElementInspector } from "./ElementInspector";
import { useElementInspector } from "@/hooks/v2";
import { templateApi } from "@/lib/api";
```

**Backend Order:**
1. Standard library imports
2. Third-party imports (FastAPI, SQLAlchemy, Pydantic)
3. Internal app imports (`app.models`, `app.services`, `app.schemas`)

**Example from `backend/app/services/template_service.py`:**
```python
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_, Text, cast
from sqlalchemy.orm import selectinload
from typing import Optional, List, Tuple
from uuid import UUID
import logging

from app.models.template import Template, TemplateVersion
from app.models.tag import Tag
from app.models.category import Category
```

**Path Aliases:**
- Frontend: `@/*` → `./src/*`
- Backend: Absolute imports from `app.*`

## Error Handling

**Frontend Patterns:**
- Use try/catch with typed error handling
- Centralized error handler in API client (`handleError` function)
- Log errors to console with context prefix (`[API Error]`, `[useTemplates]`)
- Throw user-friendly error messages (Norwegian for UI)

```typescript
function handleError(error: unknown, context: string): never {
  console.error(`[API Error] ${context}:`, error);

  if (error instanceof AxiosError) {
    if (error.code === "ERR_NETWORK") {
      throw new Error("Nettverksfeil: Kan ikke koble til serveren...");
    }
    if (error.response?.data?.detail) {
      throw new Error(error.response.data.detail);
    }
  }
  throw new Error("En uventet feil oppstod");
}
```

**Backend Patterns:**
- Raise `HTTPException` for API errors with status code and detail
- Use Python logging module for internal logging
- No bare try/except blocks observed in routers

```python
if not template:
    raise HTTPException(status_code=404, detail="Template not found")
```

**State Error Display:**
- Frontend components track `error: string | null` state
- Display errors in UI with appropriate styling (`text-red-500`)

## Logging

**Framework:**
- Frontend: `console.log`, `console.error` with context prefixes
- Backend: Python `logging` module

**Backend Patterns:**
```python
logger = logging.getLogger(__name__)
logger.info(f"Created template: {template.id} - {template.title}")
logger.warning(f"Azure upload failed for {file.filename}, using mock URL")
```

**Frontend Patterns:**
```typescript
console.log("[API] Uploading template:", { fileName, fileSize, ... });
console.error("[useTemplates] Error:", err);
```

## Comments

**When to Comment:**
- Module-level docstrings for Python files (always)
- Class/method docstrings with Args/Returns sections (Python)
- JSDoc for complex TypeScript functions
- Inline comments for non-obvious logic

**Python Docstrings:**
```python
"""
Template Service - Business logic for template operations.
"""

async def get_list(
    db: AsyncSession,
    ...
) -> Tuple[List[Template], int]:
    """
    Get paginated list of templates with filters.

    Args:
        db: Database session
        status: Filter by status (draft, published, archived)
        ...

    Returns:
        Tuple of (templates list, total count)
    """
```

**TypeScript/JSDoc:**
```typescript
/**
 * DocumentViewer - Main viewer container with multiple preview modes
 */

/**
 * Handle API errors with detailed logging
 */
```

## Function Design

**Size:**
- Keep functions focused on single responsibility
- Extract helper functions for complex operations (see `_map_employee_payload`, `_normalize_text`)

**Parameters:**
- Python: Use keyword-only arguments with `*` separator for clarity
- TypeScript: Use object destructuring for multiple optional params

```python
async def get_list(
    db: AsyncSession,
    *,  # Everything after is keyword-only
    status: Optional[str] = None,
    search: Optional[str] = None,
    ...
) -> Tuple[List[Template], int]:
```

**Return Values:**
- Python services return tuples for paginated data: `(items, total_count)`
- TypeScript hooks return objects with named properties: `{ templates, pagination, isLoading, error, refetch }`

## Module Design

**Backend Service Pattern:**
- Business logic in service classes (`TemplateService`, `EmployeeService`)
- Static methods (no instance state)
- Database session passed as first argument
- Services live in `backend/app/services/`

**Backend Router Pattern:**
- Thin routers that delegate to services
- FastAPI dependency injection for db session (`Depends(get_db)`)
- Pydantic models for request/response validation
- Routers live in `backend/app/routers/`

**Frontend API Pattern:**
- API clients as exported objects with methods (`templateApi`, `categoryApi`)
- Shared axios instance with interceptors (`apiClient`)
- API modules live in `frontend/src/lib/api/`

**Exports:**
- Python: Implicit module exports (import from module)
- TypeScript: Named exports preferred, barrel files (`index.ts`) for re-exports

**Barrel Files:**
- `frontend/src/types/index.ts` re-exports from `v2.ts`, `v3.ts`
- `frontend/src/lib/api/index.ts` exports all API clients

## UI Component Patterns

**Shadcn/UI Usage:**
- All base UI components from `@/components/ui/`
- Components use `cn()` utility for className merging
- Variants defined with `class-variance-authority` (cva)

```typescript
const buttonVariants = cva(
  "inline-flex items-center justify-center...",
  {
    variants: {
      variant: { default: "bg-[#272630]...", outline: "...", ... },
      size: { default: "h-10 px-4 py-2", sm: "h-9...", ... },
    },
    defaultVariants: { variant: "default", size: "default" },
  }
);
```

**Color Palette (Proaktiv Brand):**
- Primary Navy: `#272630`
- Bronze/Gold: `#BCAB8A`
- Warm Beige: `#E9E7DC`, `#F5F5F0`
- Applied via Tailwind classes

**Client Components:**
- Mark with `"use client"` directive at file top
- Use for components with hooks/state/browser APIs

---

*Convention analysis: 2025-01-20*
