# Frontend Design System & Brand Guidelines

> **This is the authoritative reference for frontend design in Proaktiv Dokument Hub.**
> All new components and pages MUST follow these guidelines.

---

## Brand Identity

### Company
**Proaktiv Eiendomsmegling** — Premium Norwegian real estate brokerage with offices across Norway.

### Brand Personality
- **Premium** — High-end, sophisticated, trustworthy
- **Professional** — Clean, organized, efficient
- **Modern** — Contemporary design, not flashy
- **Norwegian** — Local feel, Scandinavian minimalism

---

## Color Palette

### Primary Colors

| Name | Hex | HSL | Usage |
|------|-----|-----|-------|
| **Navy** | `#272630` | `245 8% 17%` | Primary text, buttons, headers |
| **Bronze** | `#BCAB8A` | `38 28% 64%` | Accents, highlights, selection states, links |
| **White** | `#FFFFFF` | `0 0% 100%` | Cards, dialogs, content backgrounds |

### Secondary Colors

| Name | Hex | HSL | Usage |
|------|-----|-----|-------|
| **Beige** | `#E9E7DC` | `43 22% 89%` | Header background, secondary surfaces |
| **Cream** | `#f9f9f7` | `40 20% 98%` | Page background alternative |
| **Light Beige** | `#F5F5F0` | Hover states, subtle backgrounds |

### Semantic Colors

| State | Color | Usage |
|-------|-------|-------|
| **Success** | Emerald (`emerald-500`) | Active status, confirmations |
| **Warning** | Amber (`amber-500`) | Offboarding, attention needed |
| **Error** | Red (`destructive`) | Errors, delete actions |
| **Info** | Sky (`sky-500`) | Onboarding, informational |

### Color Rules

1. **Navy for primary actions** — Default buttons, primary text
2. **Bronze for accents** — Links, focus rings, selection glow, highlights
3. **Never use harsh blues** — Prefer emerald/sky for status colors
4. **Maintain contrast** — Text on colored backgrounds must be readable

---

## Typography

### Font Stack

```css
--font-sans: 'Inter', system-ui, -apple-system, sans-serif;
--font-serif: 'Playfair Display', Georgia, serif;
```

### Hierarchy

| Element | Font | Size | Weight | Usage |
|---------|------|------|--------|-------|
| **Page Title** | Serif | `text-3xl` | `font-bold` | Main page headings |
| **Section Title** | Serif | `text-2xl` | `font-semibold` | Section headings, card titles |
| **Subsection** | Serif | `text-lg` | `font-semibold` | Smaller section headings |
| **Body** | Sans | `text-sm`/`text-base` | `font-normal` | Regular content |
| **Label** | Sans | `text-sm` | `font-medium` | Form labels, metadata |
| **Caption** | Sans | `text-xs` | `font-normal` | Secondary info, timestamps |

### Typography Rules

1. **Serif for headings** — Creates premium feel, use `font-serif` class
2. **Sans for body** — Inter for readability
3. **Never use more than 3 sizes** on a single component
4. **Truncate long text** — Use `truncate` class, never wrap excessively

---

## Spacing & Layout

### Spacing Scale

Use Tailwind's default spacing scale. Common values:

| Token | Value | Usage |
|-------|-------|-------|
| `gap-1` | 4px | Tight spacing (badges, icons) |
| `gap-2` | 8px | Related elements |
| `gap-3` | 12px | List items |
| `gap-4` | 16px | Card padding, section gaps |
| `gap-6` | 24px | Major sections |
| `gap-8` | 32px | Page sections |

### Container

```tsx
<main className="container mx-auto px-6 py-8">
```

### Card Padding

- **Standard**: `p-6` for card content
- **Compact**: `p-4` for smaller cards
- **Content area**: `pt-0` when following header

---

## Shadows & Depth

### Shadow Tokens

| Token | CSS Variable | Usage |
|-------|--------------|-------|
| `shadow-soft` | `--shadow-soft` | Subtle depth on buttons |
| `shadow-medium` | `--shadow-medium` | Elevated elements, header on scroll |
| `shadow-elevated` | `--shadow-elevated` | Dropdowns, dialogs |
| `shadow-card` | `--shadow-card` | Default card state |
| `shadow-card-hover` | `--shadow-card-hover` | Card hover state |
| `shadow-glow` | `--shadow-glow` | Selection state (bronze glow) |

### Shadow Values

```css
--shadow-soft: 0 2px 8px -2px rgba(39, 38, 48, 0.06);
--shadow-medium: 0 4px 16px -4px rgba(39, 38, 48, 0.1);
--shadow-elevated: 0 8px 24px -6px rgba(39, 38, 48, 0.12);
--shadow-card: 0 1px 3px rgba(39, 38, 48, 0.04), 0 1px 2px rgba(39, 38, 48, 0.06);
--shadow-card-hover: 0 10px 30px -10px rgba(39, 38, 48, 0.15);
--shadow-glow: 0 0 20px -5px rgba(188, 171, 138, 0.4);
```

### Depth Rules

1. **Cards always have shadow** — `shadow-card` as base
2. **Add ring for subtle depth** — `ring-1 ring-black/[0.03]`
3. **Hover elevates** — Use `shadow-card-hover` with lift
4. **Selection uses glow** — Bronze glow for selected state

---

## Transitions & Animation

### Duration Tokens

| Token | Value | Usage |
|-------|-------|-------|
| `duration-fast` | 150ms | Focus rings, quick feedback |
| `duration-normal` | 200ms | Standard transitions |
| `duration-slow` | 300ms | Card hover, complex animations |

### Easing

```css
--transition-ease-standard: cubic-bezier(0.2, 0, 0, 1);
```

Use `ease-standard` class for all interactive transitions.

### Animation Patterns

| Pattern | Classes | Usage |
|---------|---------|-------|
| **Card hover** | `hover:shadow-card-hover hover:-translate-y-0.5 transition-all duration-slow` | All interactive cards |
| **Button press** | `active:scale-[0.98]` | Button feedback |
| **Avatar scale** | `hover:scale-105 transition-transform duration-fast` | Avatar hover |
| **Chevron rotate** | `group-data-[state=open]:rotate-180 transition-transform duration-fast` | Dropdown indicators |
| **Scroll shadow** | Conditional `shadow-medium` based on scroll position | Header |

### Reduced Motion

Always respect user preferences:

```css
@media (prefers-reduced-motion: reduce) {
  *, *::before, *::after {
    animation-duration: 0.01ms !important;
    transition-duration: 0.01ms !important;
  }
}
```

---

## Component Patterns

### Card Pattern

```tsx
<Card className="group cursor-pointer hover:shadow-card-hover hover:-translate-y-0.5 transition-all duration-slow">
  <CardContent className="p-4">
    {/* Content */}
  </CardContent>
</Card>
```

### Selection Pattern

```tsx
<Card className={cn(
  "group cursor-pointer hover:shadow-card-hover hover:-translate-y-0.5 transition-all duration-slow",
  selected && "ring-2 ring-strong shadow-glow"
)}>
```

### Avatar Pattern

```tsx
<Avatar className="h-12 w-12 shrink-0 transition-transform duration-fast ease-standard hover:scale-105">
  <AvatarImage src={resolveAvatarUrl(url, 128)} alt={name} />
  <AvatarFallback style={{ backgroundColor: color }}>
    {initials}
  </AvatarFallback>
</Avatar>
```

### Button Variants

| Variant | Usage |
|---------|-------|
| `default` | Primary actions (navy background) |
| `secondary` | Secondary actions (beige background) |
| `outline` | Tertiary actions (navy border) |
| `ghost` | Minimal actions (no background) |
| `accent` | Highlight actions (bronze background) |
| `destructive` | Delete/dangerous actions |

### Dropdown Pattern

```tsx
<DropdownMenuContent className="w-48 bg-white">
  <DropdownMenuItem>
    <Icon className="h-4 w-4 mr-2" />
    Label
  </DropdownMenuItem>
</DropdownMenuContent>
```

---

## Golden Rules

### DO

1. ✅ **Use design tokens** — Never hardcode shadows, transitions, or colors
2. ✅ **Apply hover states** — All interactive elements need visual feedback
3. ✅ **Use bronze for accents** — Selection, focus, highlights
4. ✅ **Serif for headings** — Maintains premium feel
5. ✅ **Consistent card pattern** — Same shadow/hover across all cards
6. ✅ **Respect reduced motion** — Animations have fallbacks
7. ✅ **Use `resolveAvatarUrl()`** — For proper avatar sizing
8. ✅ **Add transition classes** — Smooth state changes

### DON'T

1. ❌ **Hardcode colors** — Use brand tokens or Tailwind semantic colors
2. ❌ **Skip hover states** — Users need feedback
3. ❌ **Use harsh blues** — Prefer emerald/sky for status
4. ❌ **Mix shadow approaches** — Stick to shadow tokens
5. ❌ **Forget focus rings** — Accessibility requirement
6. ❌ **Use `opacity-50` directly** — Use `opacity-disabled` token
7. ❌ **Instant transitions** — Always add `duration-*` and `ease-standard`
8. ❌ **Oversized animations** — Keep subtle (150-300ms)

---

## File Reference

### Design Token Files

| File | Purpose |
|------|---------|
| `frontend/src/app/globals.css` | CSS variables, base styles |
| `frontend/tailwind.config.ts` | Tailwind extensions, custom utilities |

### Base UI Components

All in `frontend/src/components/ui/`:

| Component | Key Styles |
|-----------|------------|
| `button.tsx` | Variants, shadows, active scale |
| `card.tsx` | Shadow-card, ring, serif title |
| `dialog.tsx` | Shadow-elevated, bg-white |
| `dropdown-menu.tsx` | Shadow-elevated, rounded-lg, hover states |
| `input.tsx` | Focus ring-strong transition |
| `skeleton.tsx` | Shimmer animation |

### Feature Components

| Component | Location |
|-----------|----------|
| `Header` | `components/layout/Header.tsx` |
| `OfficeCard` | `components/offices/OfficeCard.tsx` |
| `EmployeeCard` | `components/employees/EmployeeCard.tsx` |
| `TemplateCard` | `components/shelf/TemplateCard.tsx` |
| `AssetCard` | `components/assets/AssetCard.tsx` |

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2026-01-23 | Initial design system documentation |
| 1.1 | 2026-01-23 | Added animation tokens, completed enhancement pipeline |

---

*Last updated: 2026-01-23*
