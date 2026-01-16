---
name: Proaktiv Premium UI Refactor
overview: Refactor the frontend to enforce the Proaktiv brand identity (Navy/Bronze/Cream palette), fix category navigation by reading URL params on the templates page, and improve UX by making template rows clickable with a slide-out Sheet for preview.
todos:
  - id: add-shadcn
    content: Add Shadcn Sheet and Breadcrumb components via CLI
    status: completed
  - id: theme-header
    content: Replace slate/sky colors with semantic colors in Header.tsx
    status: completed
  - id: theme-dashboard
    content: Replace hardcoded colors in Dashboard page.tsx
    status: completed
  - id: theme-templates
    content: Replace hardcoded colors in templates/page.tsx
    status: completed
  - id: theme-preview
    content: Replace hardcoded colors in TemplatePreview.tsx
    status: completed
  - id: backend-category
    content: Add category_id filter to backend templates API with UUID validation (400 on invalid UUID)
    status: completed
  - id: frontend-api-category
    content: Add category_id to frontend API and useTemplates hook
    status: completed
  - id: templates-searchparams
    content: Read searchParams.category and pre-select filter in TemplatesPage
    status: completed
  - id: create-detail-sheet
    content: Create TemplateDetailSheet component with preview, metadata, actions
    status: completed
  - id: clickable-rows
    content: Make template table rows clickable to open Sheet
    status: completed
  - id: add-breadcrumbs
    content: Add Breadcrumb navigation to templates page
    status: completed
  - id: polish-upload-btn
    content: Style Upload button with Bronze accent color
    status: completed
---

# Proaktiv Premium UI Refactor

## Current State Analysis

**Good news:** The theme infrastructure is already in place:

- [frontend/src/app/globals.css](frontend/src/app/globals.css) - CSS variables for Proaktiv Navy/Bronze/Cream are correctly defined
- [frontend/src/tailwind.config.ts](frontend/src/tailwind.config.ts) - Font families and `proaktiv` color palette configured
- [frontend/src/app/layout.tsx](frontend/src/app/layout.tsx) - Inter + Playfair Display fonts loaded

**Problems identified:**

1. Components hardcode `slate-*`, `sky-*` colors instead of semantic `bg-primary`, `text-muted-foreground`, etc.
2. Category links on Dashboard already work (`/templates?category=${id}`), but `TemplatesPage` ignores the query param
3. Template rows require "..." menu click - not directly clickable
4. No Sheet or Breadcrumb components installed

---

## Task 1: Global Theme Enforcement

**Files to modify:**

- [frontend/src/app/globals.css](frontend/src/app/globals.css) - Minor tweaks (already correct)
- [frontend/src/components/layout/Header.tsx](frontend/src/components/layout/Header.tsx) - Replace `slate-*`, `sky-*` with semantic colors
- [frontend/src/app/page.tsx](frontend/src/app/page.tsx) - Replace gradient/hardcoded colors
- [frontend/src/app/templates/page.tsx](frontend/src/app/templates/page.tsx) - Replace gradient/hardcoded colors
- [frontend/src/components/templates/TemplatePreview.tsx](frontend/src/components/templates/TemplatePreview.tsx) - Replace `slate-*`, `sky-*`

**Key changes:**

```tsx
// Before (Header.tsx line 36)
className="bg-gradient-to-br from-sky-500 to-sky-700"

// After
className="bg-primary" // Uses Proaktiv Navy
```
```tsx
// Before (Header.tsx line 83)
className="bg-sky-600 hover:bg-sky-700"

// After  
className="bg-secondary text-secondary-foreground hover:bg-secondary/90" // Bronze button
```

---

## Task 2: Fix Category Navigation

**Backend change required:**

- [backend/app/routers/templates.py](backend/app/routers/templates.py) - Add `category_id` query parameter with UUID validation
- [backend/app/services/template_service.py](backend/app/services/template_service.py) - Filter by category

**UUID Validation (prevent 500 errors):**

The `category_id` parameter must be validated as a proper UUID before querying the database. If someone manually types `?category=bad-id` in the URL, return a 400 Bad Request instead of crashing.

```python
# backend/app/routers/templates.py
from uuid import UUID

@router.get("")
async def list_templates(
    # ... existing params ...
    category_id: Optional[str] = Query(None, description="Filter by category UUID"),
):
    # Validate category_id is a valid UUID if provided
    validated_category_id: Optional[UUID] = None
    if category_id:
        try:
            validated_category_id = UUID(category_id)
        except ValueError:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid category_id format: '{category_id}' is not a valid UUID"
            )
    
    templates, total = await TemplateService.get_list(
        db,
        category_id=validated_category_id,
        # ... rest of params
    )
```

**Frontend changes:**

- [frontend/src/lib/api.ts](frontend/src/lib/api.ts) - Add `category_id` to params type
- [frontend/src/hooks/useTemplates.ts](frontend/src/hooks/useTemplates.ts) - Add `category_id` to hook params
- [frontend/src/app/templates/page.tsx](frontend/src/app/templates/page.tsx) - Read `searchParams.category`, pre-select filter
```tsx
// templates/page.tsx - convert to handle searchParams
export default function TemplatesPage({ 
  searchParams 
}: { 
  searchParams: { category?: string } 
}) {
  const [categoryFilter, setCategoryFilter] = useState<string | undefined>(
    searchParams.category
  );
  // ...
}
```


---

## Task 3: Improve Template List UX (Sheet Drawer)

**Add Shadcn components:**

```bash
npx shadcn-ui@latest add sheet
npx shadcn-ui@latest add breadcrumb
```

**New component:**

- Create [frontend/src/components/templates/TemplateDetailSheet.tsx](frontend/src/components/templates/TemplateDetailSheet.tsx)

**Modify:**

- [frontend/src/app/templates/page.tsx](frontend/src/app/templates/page.tsx) - Make rows clickable, open Sheet
```tsx
// Row becomes clickable
<div
  onClick={() => handleRowClick(template)}
  className="grid grid-cols-12 gap-4 p-4 items-center cursor-pointer hover:bg-muted/50 transition-colors"
>
```


**Sheet content structure:**

```
+---------------------------+
| Template Title        [X] |
+---------------------------+
| [Iframe Preview]          |
|                           |
+---------------------------+
| Metadata:                 |
| - File: example.html      |
| - Size: 12.5 KB           |
| - Status: Published       |
| - Category: Akseptbrev    |
+---------------------------+
| [Download]  [Edit]        |
+---------------------------+
```

---

## Task 4: Polish

**Breadcrumbs:**

Add to templates page header when a category is selected:

```
Dashboard / Maler / Akseptbrev
```

**Upload button:**

Style with Bronze/Navy to stand out:

```tsx
<Button className="bg-secondary text-secondary-foreground hover:bg-secondary/90">
  <Upload className="h-4 w-4 mr-2" />
  Last opp
</Button>
```

---

## File Change Summary

| File | Change Type |

|------|-------------|

| `frontend/src/app/globals.css` | Minor cleanup (already good) |

| `frontend/src/components/layout/Header.tsx` | Replace hardcoded colors |

| `frontend/src/app/page.tsx` | Replace hardcoded colors |

| `frontend/src/app/templates/page.tsx` | Major: searchParams, Sheet, Breadcrumbs, colors |

| `frontend/src/components/templates/TemplatePreview.tsx` | Replace hardcoded colors |

| `frontend/src/components/templates/TemplateDetailSheet.tsx` | **New file** |

| `frontend/src/components/ui/sheet.tsx` | **New (Shadcn)** |

| `frontend/src/components/ui/breadcrumb.tsx` | **New (Shadcn)** |

| `frontend/src/lib/api.ts` | Add category_id param |

| `frontend/src/hooks/useTemplates.ts` | Add category_id param |

| `backend/app/routers/templates.py` | Add category_id filter |

| `backend/app/services/template_service.py` | Filter by category |

---

## Execution Order

1. Add Shadcn components (Sheet, Breadcrumb)
2. Theme enforcement across all components
3. Backend: Add category filter support
4. Frontend: API + hook updates for category
5. TemplatesPage: Read searchParams, add category filter UI
6. Create TemplateDetailSheet component
7. Make rows clickable, integrate Sheet
8. Add Breadcrumbs
9. Final polish and testing