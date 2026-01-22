# Phase 3: Social Media Links - Agent Handover

**Created:** 2026-01-20
**Updated:** 2026-01-22
**Status:** Not Started
**Prerequisites:** Phase 4 ✅ Complete

### Stack (Updated 2026-01-22)
- **Backend:** FastAPI 0.109 + SQLAlchemy 2.0.46 + Pydantic 2.x + PostgreSQL
- **Frontend:** Next.js 16 + React 19 + Shadcn/UI + Tailwind CSS 4 + TypeScript 5.9
- **Testing:** Vitest (frontend) + Pytest (backend)
- **CI/CD:** GitHub Actions (lint, typecheck, test, build)
- **Deployment:** Railway (backend + DB + frontend)

---

## MASTER PROMPT

You are implementing Phase 3 of the Proaktiv Dokument Hub project: **Social Media Links**. This feature adds social media profile URLs to employees and creates a "Featured Brokers" section on office pages.

### Your Mission

1. Add social media fields to Employee model (Facebook, Instagram, Twitter)
2. Add is_featured_broker flag to Employee
3. Update forms and detail pages to show social links
4. Build Featured Brokers component for office pages

### Key Insight

**Most work is already done for offices** - they have full social media support. You are primarily extending the employee side and building the featured brokers UI.

### Execution Order

| Plan | Focus | Complexity |
|------|-------|------------|
| **03-01** | Database Schema | Simple - add 4 fields to employees |
| **03-02** | Backend Updates | Simple - update service/router |
| **03-03** | Employee UI | Medium - form fields + detail display |
| **03-04** | Featured Brokers | Medium - new component + office page |

---

## WHAT ALREADY EXISTS

### Office Social Media (COMPLETE - copy this pattern)

**Model fields:** facebook_url, instagram_url, linkedin_url, google_my_business_url
**Form:** All fields in OfficeForm.tsx
**Display:** Office detail page shows Facebook, LinkedIn icons

### Employee Social Media (PARTIAL)

**Model fields:** linkedin_url only
**Form:** LinkedIn field in EmployeeForm.tsx
**Display:** Employee detail shows LinkedIn icon

---

## DATABASE CHANGES

### Add to Employee Model

```python
# backend/app/models/employee.py
# Add after linkedin_url field:
facebook_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
instagram_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
twitter_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

# Add after status field:
is_featured_broker: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
```

### Migration

```python
def upgrade():
    op.add_column("employees", sa.Column("facebook_url", sa.Text(), nullable=True))
    op.add_column("employees", sa.Column("instagram_url", sa.Text(), nullable=True))
    op.add_column("employees", sa.Column("twitter_url", sa.Text(), nullable=True))
    op.add_column("employees", sa.Column("is_featured_broker", sa.Boolean(), 
                                          nullable=False, server_default="false"))
```

---

## TYPESCRIPT TYPES

### Update Employee Interface

```typescript
// frontend/src/types/v3/index.ts
export interface Employee {
  // ... existing fields ...
  linkedin_url: string | null;
  facebook_url: string | null;      // ADD
  instagram_url: string | null;     // ADD
  twitter_url: string | null;       // ADD
  is_featured_broker: boolean;      // ADD
}
```

---

## UI PATTERNS TO FOLLOW

### Social Icons (from office detail page)

```tsx
import { Facebook, Instagram, Linkedin, Twitter } from "lucide-react";

{employee.facebook_url && (
  <a href={employee.facebook_url} target="_blank" rel="noopener noreferrer">
    <Facebook className="h-5 w-5 text-muted-foreground hover:text-primary" />
  </a>
)}
```

### Form Fields (copy from OfficeForm.tsx)

```tsx
<div className="grid gap-4 sm:grid-cols-2">
  <div className="space-y-2">
    <Label htmlFor="facebook_url">Facebook</Label>
    <Input
      id="facebook_url"
      type="url"
      {...register("facebook_url")}
      placeholder="https://facebook.com/..."
    />
  </div>
  <div className="space-y-2">
    <Label htmlFor="instagram_url">Instagram</Label>
    <Input
      id="instagram_url"
      type="url"
      {...register("instagram_url")}
      placeholder="https://instagram.com/..."
    />
  </div>
</div>
```

---

## FEATURED BROKERS COMPONENT

### Design

```tsx
// frontend/src/components/employees/FeaturedBrokers.tsx
interface FeaturedBrokersProps {
  officeId: string;
}

export function FeaturedBrokers({ officeId }: FeaturedBrokersProps) {
  // Fetch employees with is_featured_broker=true for this office
  // Display as responsive grid of cards
  // Each card: photo, name, title, social icons
}
```

### Card Layout

```
+------------------+
|    [Avatar]      |
|   Per Hansen     |
|  Eiendomsmegler  |
|  [FB] [IG] [LI]  |
+------------------+
```

---

## API FILTER

Add filter to employee list endpoint:

```python
# backend/app/routers/employees.py
@router.get("/")
async def list_employees(
    is_featured: Optional[bool] = Query(None, description="Filter by featured status"),
    # ... other params
):
    # Pass to service
```

---

## TESTING CHECKLIST

**Plan 03-01:** Migration runs, new fields in DB
**Plan 03-02:** API returns new fields, accepts updates
**Plan 03-03:** Form has fields, detail page shows icons
**Plan 03-04:** Featured section appears on office page

---

## START COMMAND

Read and execute `.planning/phases/03-social-media-links/03-01-PLAN.md` first.
Auto-write and commit after each plan without asking for approval.
