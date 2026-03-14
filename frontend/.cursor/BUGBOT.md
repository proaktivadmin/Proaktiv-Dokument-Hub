# Bugbot — Frontend (Next.js + React)

Frontend-specific rules for PR reviews. See root `.cursor/BUGBOT.md` for project-wide context.

## Critical (blocking)

- **No `any` in TypeScript** — Use proper types.
- **No direct Railway URLs** — Use relative `/api/*` or `lib/api` wrapper. Never `fetch('https://proaktiv-admin.up.railway.app/...')`.
- **Design tokens, not hardcoded values** — Use `shadow-card`, `text-foreground`, `ring-strong`, etc. No hardcoded hex colors, shadows, or transitions.
- **Server Components by default** — Use `"use client"` only when hooks or browser APIs required.

## Patterns

- Use `frontend/src/lib/api.ts` or related API modules — no ad hoc `fetch()` in components
- Shadcn/UI components over custom primitives
- Document preview primary, code view secondary
- Dim filtered cards (opacity), do not hide them

## Design system

- **Colors:** Navy `#272630`, Bronze `#BCAB8A`, Beige `#E9E7DC`. No harsh blues; use emerald/sky for status.
- **Typography:** Serif for headings (`font-serif`), sans for body
- **Cards:** `shadow-card`, `shadow-card-hover`, `hover:-translate-y-0.5`
- **Selection:** `ring-strong`, `shadow-glow`
- See `.planning/codebase/DESIGN-SYSTEM.md`

## Component naming

- Viewer: `*Frame.tsx`
- Library: `*Library.tsx`, `*Card.tsx`
- Inspector: `ElementInspector.tsx`

## Tests

- Frontend changes should include or update tests
- Run: `npm run lint`, `npx tsc --noEmit`, `npm run test:run`
