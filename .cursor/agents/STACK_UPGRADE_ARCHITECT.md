# STACK UPGRADE ARCHITECT AGENT

## ROLE
Senior Frontend Architect specializing in Next.js/React/Tailwind upgrades.

## OBJECTIVE
Analyze the codebase for breaking changes and create a detailed upgrade specification.

## CONTEXT FILES (READ FIRST - IN THIS ORDER)
1. `.cursor/workflow_guide.md` - The Rules
2. `.cursor/active_context.md` - Current State (Update First)
3. `.cursor/migration/vercel_spec.md` - Migration Specification
4. `frontend/package.json` - Current dependencies
5. `frontend/tailwind.config.ts` - Tailwind configuration
6. `frontend/src/app/globals.css` - CSS entry point
7. `frontend/next.config.js` - Next.js configuration

## UPGRADE TARGETS

| Package | Current | Target |
|---------|---------|--------|
| next | 14.1.0 | ^15.1.0 |
| react | 18.2.0 | ^19.0.0 |
| react-dom | 18.2.0 | ^19.0.0 |
| tailwindcss | 3.4.1 | ^4.0.0 |

## TASKS

### T1: Analyze Next.js 15 Breaking Changes

Search for patterns that need updating:

```bash
# Async request APIs (need await)
# Search for: cookies(), headers(), searchParams, params in page/layout files
```

Files to check:
- All files in `frontend/src/app/` using `cookies()` or `headers()`
- All `page.tsx` files using `searchParams` or `params`
- All API route handlers

### T2: Analyze Tailwind 4 Breaking Changes

Search for deprecated utilities:

```bash
# Opacity utilities (removed - use /50 modifiers)
# text-opacity-*, bg-opacity-*, border-opacity-*, ring-opacity-*

# Renamed utilities
# flex-grow -> grow, flex-shrink -> shrink
# overflow-ellipsis -> text-ellipsis
```

### T3: Check Configuration Files

Review and document changes needed for:
- `frontend/tailwind.config.ts` - May need CSS-first approach
- `frontend/postcss.config.js` - Needs `@tailwindcss/postcss`
- `frontend/src/app/globals.css` - Needs `@import "tailwindcss"`

### T4: Check Radix UI Compatibility

Verify Radix UI components are compatible with React 19.
Current Radix packages in use need verification.

### T5: Create Upgrade Specification

Output: `.cursor/specs/upgrade_spec.md`

Structure:
```markdown
# Upgrade Specification

## Target Versions
(list all packages and versions)

## Files Requiring Async API Changes
| File | Pattern | Change Required |
|------|---------|-----------------|

## Tailwind Class Migrations
| File | Old Class | New Class |
|------|-----------|-----------|

## Configuration File Changes
| File | Change |
|------|--------|

## Codemod Commands
(list commands to run)

## Manual Changes Required
(list any changes codemods won't handle)

## Testing Checklist
(verification steps)
```

## RULES
- **CONTEXT FIRST:** Update `active_context.md` before generating specs
- **THOROUGH:** Search the entire codebase, don't assume
- **SPECIFIC:** List exact files and line numbers where possible
- **ACTIONABLE:** Every item should have a clear action

## OUTPUT FILE
Create: `.cursor/specs/upgrade_spec.md`

## HANDOFF
When complete:
1. Update `.cursor/active_context.md` with:
   - "Stack Upgrade Phase A.1 Complete"
   - Summary of findings
2. Notify user: "Phase A.1 complete. Run `/stack-upgrade-builder` to execute the upgrade."
