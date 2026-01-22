# STACK UPGRADE BUILDER AGENT

## ROLE
Senior Full-Stack Developer executing the stack upgrade.

## OBJECTIVE
Execute the upgrade from Next.js 14 + React 18 + Tailwind 3 to Next.js 15 + React 19 + Tailwind 4.

## CONTEXT FILES (READ FIRST - IN THIS ORDER)
1. `.cursor/workflow_guide.md` - The Rules
2. `.cursor/active_context.md` - Current State (Update First)
3. `.cursor/specs/upgrade_spec.md` - What to change (from Architect)
4. `.cursor/migration/vercel_spec.md` - Overall migration spec
5. `frontend/package.json` - Current dependencies

## EXECUTION ORDER

### Phase 1: Update Dependencies

Update `frontend/package.json`:

```json
{
  "dependencies": {
    "next": "^15.1.0",
    "react": "^19.0.0",
    "react-dom": "^19.0.0"
  },
  "devDependencies": {
    "@tailwindcss/postcss": "^4.0.0",
    "@types/react": "^19.0.0",
    "@types/react-dom": "^19.0.0",
    "eslint-config-next": "^15.1.0",
    "tailwindcss": "^4.0.0"
  }
}
```

Then run:
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### Phase 2: Run Codemods

```bash
cd frontend

# Next.js async request API codemod
npx @next/codemod@canary next-async-request-api .

# Tailwind upgrade tool
npx @tailwindcss/upgrade
```

### Phase 3: Update PostCSS Configuration

Update `frontend/postcss.config.js`:

```javascript
module.exports = {
  plugins: {
    '@tailwindcss/postcss': {},
    autoprefixer: {},
  },
}
```

### Phase 4: Update CSS Entry Point

Update `frontend/src/app/globals.css`:

```css
@import "tailwindcss";

/* Rest of custom styles... */
```

### Phase 5: Manual Fixes

Based on `.cursor/specs/upgrade_spec.md`, fix:
1. Any async patterns the codemod missed
2. Tailwind class renames not caught by upgrade tool
3. Any TypeScript errors

### Phase 6: Build and Test

```bash
cd frontend
npm run build    # Fix any build errors
npm run lint     # Fix any lint errors
npm run dev      # Test locally
```

### Phase 7: Deploy to Railway

```bash
git add -A
git status  # Verify changes

git commit -m "$(cat <<'EOF'
feat: upgrade to Next.js 15, React 19, Tailwind 4

BREAKING CHANGES:
- Next.js 15 with async request APIs
- React 19 with new hooks
- Tailwind 4 with CSS-first config

Security: Fixes CVE-2025-29927 (critical auth bypass)
EOF
)"

git push origin main
```

## RULES
- **CONTEXT FIRST:** Update `active_context.md` before and after major changes
- **ONE STEP AT A TIME:** Complete each phase before moving to next
- **TEST FREQUENTLY:** Run build after each major change
- **DOCUMENT ISSUES:** If something fails, document it before trying to fix

## DO NOT
- Skip the codemod step
- Ignore build errors and push anyway
- Make unrelated changes
- Delete working code without understanding it

## HANDOFF
When complete:
1. Update `.cursor/active_context.md` with:
   - "Stack Upgrade Phase A.2 Complete"
   - Railway deployment status
   - Any issues encountered
2. Notify user: "Phase A.2 complete. Run `/upgrade-qa` to verify the upgrade."
