# Frontend Design Rules

> **This rule applies to ALL frontend design work in this project.**
> Read this BEFORE planning or implementing any UI changes.

---

## REQUIRED: Read Design System First

Before planning or implementing ANY frontend design work, you MUST read:

1. **`.planning/codebase/DESIGN-SYSTEM.md`** - Complete design system guide
2. **`.cursor/specs/frontend-design-enhancement-status.md`** - Implementation reference (if available)

---

## Quick Reference

### Brand Colors

| Name | Hex | Usage |
|------|-----|-------|
| **Navy** | `#272630` | Primary text, buttons, headers |
| **Bronze** | `#BCAB8A` | Accents, highlights, selection, focus rings |
| **Beige** | `#E9E7DC` | Header background, secondary surfaces |
| **Cream** | `#f9f9f7` | Page background alternative |
| **White** | `#FFFFFF` | Cards, dialogs |

### Shadow Tokens

| Token | Usage |
|-------|-------|
| `shadow-soft` | Subtle button depth |
| `shadow-medium` | Header on scroll, elevated elements |
| `shadow-elevated` | Dropdowns, dialogs |
| `shadow-card` | Default card state |
| `shadow-card-hover` | Card hover state |
| `shadow-glow` | Selection state (bronze glow) |

### Transition Tokens

| Token | Value | Usage |
|-------|-------|-------|
| `duration-fast` | 150ms | Quick feedback, focus rings |
| `duration-normal` | 200ms | Standard transitions |
| `duration-slow` | 300ms | Card hover, complex animations |
| `ease-standard` | cubic-bezier(0.2, 0, 0, 1) | All interactive transitions |

### Typography

- **Headings**: `font-serif` class (Playfair Display)
- **Body**: Default sans (Inter)

---

## Component Patterns

### Interactive Cards
```tsx
className="hover:shadow-card-hover hover:-translate-y-0.5 transition-all duration-slow"
```

### Selection State
```tsx
className={cn("...", selected && "ring-2 ring-strong shadow-glow")}
```

### Avatar Hover
```tsx
className="transition-transform duration-fast ease-standard hover:scale-105"
```

### Dropdown Chevron Rotation
```tsx
<ChevronDown className="transition-transform duration-fast ease-standard group-data-[state=open]:rotate-180" />
```

---

## Golden Rules

### DO

1. ✅ **Read DESIGN-SYSTEM.md first** before any UI work
2. ✅ **Use design tokens** — Never hardcode shadows, transitions, or colors
3. ✅ **Apply hover states** — All interactive elements need visual feedback
4. ✅ **Use bronze for accents** — Selection, focus, highlights
5. ✅ **Serif for headings** — Maintains premium feel
6. ✅ **Add transition classes** — Smooth state changes

### DON'T

1. ❌ **Hardcode colors** — Use brand tokens
2. ❌ **Skip hover states** — Users need feedback
3. ❌ **Use harsh blues** — Prefer emerald/sky for status
4. ❌ **Use `opacity-50` directly** — Use `opacity-disabled` token
5. ❌ **Instant transitions** — Always add `duration-*` and `ease-standard`
6. ❌ **Create components without checking patterns** — Reuse existing patterns

---

## File Locations

| File | Purpose |
|------|---------|
| `frontend/src/app/globals.css` | CSS variables, design tokens |
| `frontend/tailwind.config.ts` | Tailwind extensions |
| `.planning/codebase/DESIGN-SYSTEM.md` | Full design guide |

---

*Last updated: 2026-01-23*
