# Phase 4: Stack Upgrade - Research

**Researched:** 2026-01-20
**Domain:** Next.js 15 + React 19 + Tailwind 4 Upgrade
**Confidence:** HIGH

## Summary

Phase 4 upgrades the frontend stack to fix a critical security vulnerability (CVE-2025-29927) and modernize dependencies. The upgrade is substantial but well-documented with official codemods available.

**Primary recommendation:** Run official codemods first, then manually fix remaining issues. Test on Railway before Vercel migration.

## Security Issue

**CVE-2025-29927** (CVSS 9.1 Critical)
- Authentication bypass via middleware
- Affects Next.js 14.0.0 - 14.2.24
- **Fixed in:** Next.js 14.2.25+ and 15.x
- Current version: 14.1.0 (VULNERABLE)

## Current Stack

| Package | Current | Target | Breaking Changes |
|---------|---------|--------|------------------|
| Next.js | 14.1.0 | 15.1.x | Async APIs, caching defaults |
| React | 18.2.0 | 19.x | Ref handling, new hooks |
| React DOM | 18.2.0 | 19.x | Required by React 19 |
| Tailwind CSS | 3.4.1 | 4.x | CSS-first config, utility renames |
| @types/react | 18.x | 19.x | Type changes |

## Breaking Changes Analysis

### Next.js 14 to 15

**1. Async Request APIs (HIGH IMPACT)**
```javascript
// BEFORE (Next.js 14)
const cookieStore = cookies();
const headerList = headers();
const { slug } = params;
const { page } = searchParams;

// AFTER (Next.js 15)
const cookieStore = await cookies();
const headerList = await headers();
const { slug } = await params;
const { page } = await searchParams;
```

**2. Caching Defaults Changed**
- `fetch()` no longer cached by default
- Route handlers no longer cached
- Add `cache: 'force-cache'` for old behavior

**3. React 19 Required**
- Must upgrade React alongside Next.js

### React 18 to 19

**1. Ref Handling**
- `ref` now a regular prop (no forwardRef needed for simple cases)
- Existing forwardRef still works

**2. New Features** (optional to use)
- `use()` hook for promises
- `useOptimistic()` hook
- Server Actions improvements

### Tailwind 3 to 4

**1. CSS-First Configuration**
```css
/* BEFORE (globals.css) */
@tailwind base;
@tailwind components;
@tailwind utilities;

/* AFTER */
@import "tailwindcss";
```

**2. Renamed Utilities**
```
flex-grow    -> grow
flex-shrink  -> shrink
overflow-clip -> overflow-hidden (context-dependent)
```

**3. Removed Opacity Utilities**
```css
/* BEFORE */
bg-black bg-opacity-50

/* AFTER */
bg-black/50
```

**4. PostCSS Plugin Change**
```javascript
// postcss.config.js BEFORE
module.exports = {
  plugins: {
    tailwindcss: {},
    autoprefixer: {},
  },
}

// AFTER
module.exports = {
  plugins: {
    '@tailwindcss/postcss': {},
    autoprefixer: {},
  },
}
```

**5. Config File Migration**
- `tailwind.config.ts` may need updates
- Most config auto-migrates with codemod

## Files Likely Needing Changes

### Async API Usage (search for these patterns)
- `cookies()` - auth, session handling
- `headers()` - request inspection
- `params` in page/layout props
- `searchParams` in page props

### Tailwind Classes
- `flex-grow` / `flex-shrink` usage
- `bg-opacity-*` / `text-opacity-*` patterns
- Any custom config in tailwind.config.ts

## Codemods Available

```bash
# Next.js async APIs codemod
npx @next/codemod@canary next-async-request-api .

# Tailwind upgrade (interactive)
npx @tailwindcss/upgrade
```

## Upgrade Order

1. **React 19** first (required by Next.js 15)
2. **Next.js 15** second
3. **Tailwind 4** last (independent, can be separate commit)

## Plan Breakdown

| Plan | Focus | Risk |
|------|-------|------|
| 04-01 | React 19 Upgrade | Low - mostly compatible |
| 04-02 | Next.js 15 Upgrade | Medium - async API changes |
| 04-03 | Tailwind 4 Upgrade | Medium - class migrations |
| 04-04 | Build Verification | Low - testing |
| 04-05 | Railway Deployment | Low - deploy and verify |

## Rollback Plan

If upgrade fails:
```bash
git checkout main -- frontend/package.json frontend/package-lock.json
cd frontend && npm install
```

## Testing Strategy

1. Local build: `npm run build`
2. Local dev: `npm run dev`
3. Type check: `npx tsc --noEmit`
4. Lint: `npm run lint`
5. Manual test: Dashboard, auth, template preview

## Sources

- Next.js 15 Upgrade Guide: https://nextjs.org/docs/app/building-your-application/upgrading/version-15
- React 19 Blog: https://react.dev/blog/2024/12/05/react-19
- Tailwind 4 Docs: https://tailwindcss.com/docs/upgrade-guide
- CVE-2025-29927: https://nextjs.org/blog/security-update-2025-12-11

## Metadata

**Confidence breakdown:**
- React 19: HIGH - incremental, backward compatible
- Next.js 15: MEDIUM - async API changes require codemod
- Tailwind 4: MEDIUM - config changes, class renames

**Research date:** 2026-01-20
**Valid until:** 30 days (framework versions change quickly)
