# Phase 4: Stack Upgrade - Agent Handover

**Created:** 2026-01-20
**Purpose:** Complete context for upgrading Next.js 15 + React 19 + Tailwind 4

---

## MASTER PROMPT

You are implementing Phase 4 of the Proaktiv Dokument Hub project: **Stack Upgrade**. This fixes a critical security vulnerability (CVE-2025-29927) and modernizes the frontend stack.

### Your Mission

Upgrade the frontend from:
- Next.js 14.1.0 â†’ 15.1.x (CRITICAL: fixes auth bypass vulnerability)
- React 18.2.0 â†’ 19.x
- Tailwind 3.4.1 â†’ 4.x

### Upgrade Order (IMPORTANT)

1. **React 19 first** - Required dependency for Next.js 15
2. **Next.js 15 second** - Run codemod for async APIs
3. **Tailwind 4 last** - Independent, can be separate commit

---

## SECURITY ISSUE

**CVE-2025-29927** (CVSS 9.1 Critical)
- Authentication bypass via middleware
- Current version 14.1.0 is VULNERABLE
- Fixed in Next.js 15.x

---

## CODEMODS TO RUN

```bash
# Next.js async APIs (run after Next.js 15 installed)
cd frontend
npx @next/codemod@canary next-async-request-api .

# Tailwind upgrade (interactive)
npx @tailwindcss/upgrade
```

---

## KEY BREAKING CHANGES

### Next.js 15 - Async APIs

```javascript
// BEFORE (14.x)
const cookieStore = cookies();
const headerList = headers();
const { slug } = params;

// AFTER (15.x) - must await
const cookieStore = await cookies();
const headerList = await headers();
const { slug } = await params;
```

### Tailwind 4 - CSS Import

```css
/* BEFORE (3.x) */
@tailwind base;
@tailwind components;
@tailwind utilities;

/* AFTER (4.x) */
@import "tailwindcss";
```

### Tailwind 4 - PostCSS

```javascript
// postcss.config.js
module.exports = {
  plugins: {
    '@tailwindcss/postcss': {},  // Changed from 'tailwindcss'
    autoprefixer: {},
  },
}
```

### Tailwind 4 - Renamed Classes

```
flex-grow    â†’ grow
flex-shrink  â†’ shrink
bg-opacity-* â†’ bg-color/opacity (e.g., bg-black/50)
```

---

## PACKAGE.JSON TARGETS

```json
{
  "dependencies": {
    "next": "^15.1.0",
    "react": "^19.0.0",
    "react-dom": "^19.0.0",
    "tailwindcss": "^4.0.0"
  },
  "devDependencies": {
    "@tailwindcss/postcss": "^4.0.0",
    "@types/react": "^19.0.0",
    "@types/react-dom": "^19.0.0",
    "eslint-config-next": "^15.1.0"
  }
}
```

---

## FILES TO CHECK

### Async API Usage (search these patterns)

Files using `cookies()`:
- Auth-related pages/components
- Session handling

Files using `headers()`:
- Request inspection

Files using `params` or `searchParams`:
- Dynamic route pages `[id]/page.tsx`
- Any page.tsx with query params

### Tailwind Classes (search and replace)

```
flex-grow â†’ grow
flex-shrink â†’ shrink
bg-opacity-50 â†’ /50 modifier
text-opacity-50 â†’ /50 modifier
```

---

## VERIFICATION STEPS

After each upgrade:
1. `npm run build` - Must pass
2. `npm run lint` - Check for new errors
3. `npm run dev` - Smoke test UI

Final verification:
- Dashboard loads
- Login/logout works
- Template preview renders
- Styles look correct

---

## ROLLBACK

If upgrade fails catastrophically:
```bash
git checkout main -- frontend/package.json frontend/package-lock.json
cd frontend && npm install
```

---

## COMMIT MESSAGE

```
feat: upgrade to Next.js 15, React 19, Tailwind 4

Security: Fixes CVE-2025-29927 (critical auth bypass)

- Next.js 14.1.0 -> 15.1.x
- React 18.2.0 -> 19.x
- Tailwind 3.4.1 -> 4.x
- Updated async APIs (cookies, headers, params)
- Migrated to CSS-first Tailwind config
```

---

## START COMMAND

Read and execute `.planning/phases/04-stack-upgrade/04-01-PLAN.md` first.
Auto-write and commit after each plan without asking for approval.
Run codemods when specified - they handle most of the work.
