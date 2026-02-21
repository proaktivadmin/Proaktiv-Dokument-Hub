# TASK: Flettekode Integration Agent — Merge Field Insertion in Template Editor

## Role & Objective

You are the Flettekode Integration Agent. You connect the existing Flettekode tooling (merge field library, code generator, autocomplete) into the template editor so that inserting, editing, or replacing merge field values can be done directly within the editing workflow — without context switching to a separate page.

The Flettekode library and code generator already exist as standalone pages. Your job is **integration**, not building from scratch. You bring these tools into the editor UI built by Agent 3 and make them work with the CKEditor instance.

---

## Prerequisites

**Hard gate:** The following must exist before you begin:

- `frontend/src/components/editor/CKEditorSandbox.tsx` — Agent 3's CKEditor component
- `frontend/src/app/templates/[id]/edit/page.tsx` — Agent 3's editor page

If either is missing, STOP and report which prerequisite is not met.

---

## Read First

Before doing anything else, read these files in order:

1. `CLAUDE.md` — Project overview, conventions
2. `.planning/vitec-html-ruleset.md` — Section 5 (Merge Field Reference) — syntax rules, function wrappers, edge cases
3. `.planning/phases/11-template-suite/PLAN.md` — Phase overview
4. `.planning/codebase/DESIGN-SYSTEM.md` — Design tokens for UI

**Existing Flettekode components (read all of these):**

5. `frontend/src/components/flettekoder/FlettekodeLibrary.tsx` — Category sidebar, field cards, search
6. `frontend/src/components/flettekoder/CodeGenerator.tsx` — Visual builder for `vitec-if`, `vitec-foreach`, inline conditions
7. `frontend/src/components/flettekoder/MergeFieldCard.tsx` — Individual field card with copy button
8. `frontend/src/components/flettekoder/MergeFieldSearch.tsx` — Search/autocomplete component
9. `frontend/src/app/flettekoder/page.tsx` — Standalone Flettekode page (4 tabs)

**Existing hooks (read these):**

10. `frontend/src/hooks/use-merge-fields.ts` — `useMergeFields()`, `useMergeFieldCategories()`
11. `frontend/src/hooks/use-merge-field-autocomplete.ts` — `useMergeFieldAutocomplete()`
12. `frontend/src/hooks/use-element-inspector.ts` — `useElementInspector()` (includes `getMergeFieldsInElement()`)

**Editor components (read these):**

13. `frontend/src/components/editor/CKEditorSandbox.tsx` — CKEditor 4 iframe component (Agent 3 built)
14. `frontend/src/app/templates/[id]/edit/page.tsx` — Editor page layout (Agent 3 built)

---

## Deliverables

### 1. Editor Merge Field Panel

**File:** `frontend/src/components/editor/MergeFieldPanel.tsx` (new)

A panel designed to sit in the editor's right sidebar (alongside the existing preview and validation tabs). It provides direct access to merge field browsing and insertion.

**Tabs:**

| Tab | Norwegian | Content |
|-----|-----------|---------|
| Felt | Felt | Browse fields by category, click to insert at cursor |
| Generator | Generator | Code generator for `vitec-if`/`vitec-foreach` blocks |
| I bruk | I bruk | Fields currently used in this template |

**Props:**

```typescript
interface MergeFieldPanelProps {
  onInsert: (text: string) => void;  // Insert text at CKEditor cursor position
  currentContent: string;  // Current editor HTML (for "in use" tab)
  templateId?: string;  // For template-specific analysis
}
```

**"Felt" tab:**
- Reuse `FlettekodeLibrary` with `onCopy` repurposed as `onInsert`
- When a user clicks a field card, insert `[[field.path]]` at the CKEditor cursor position
- Show a toast confirmation: "Flettekode satt inn: [[field.path]]"
- Include the search bar from `MergeFieldSearch` at the top

**"Generator" tab:**
- Reuse `CodeGenerator` with `onCopy` repurposed as `onInsert`
- When the user builds a `vitec-if` or `vitec-foreach` block and clicks insert, inject the generated HTML at the cursor
- The generator already handles syntax building — just connect the output to the editor

**"I bruk" tab:**
- Extract merge fields from `currentContent` using the regex pattern from `useElementInspector().getMergeFieldsInElement()`
- Display as a list of merge field cards
- Click to select/highlight in the editor
- Show count: "8 flettekoder i bruk"
- Group by category if possible (using the merge field registry to look up categories)

### 2. Inline Merge Field Autocomplete

**File:** `frontend/src/components/editor/MergeFieldAutocomplete.tsx` (new)

A floating autocomplete popover that appears when the user types `[[` in the CKEditor source view.

**Trigger:** When the user types `[[` in CKEditor's source mode, show a floating autocomplete dropdown at the cursor position.

**Behavior:**

1. User types `[[` → autocomplete appears
2. Continue typing to filter (e.g., `[[eien` shows `eiendom.*` fields)
3. Arrow keys to navigate, Enter to select
4. Selection inserts `[[field.path]]` and closes the popover
5. Escape or clicking outside closes the popover

**Implementation approach:**

CKEditor's source mode is a `<textarea>`. Listen for input events on the iframe's textarea, detect `[[` patterns, and show a React popover positioned relative to the textarea's cursor position.

Use `useMergeFieldAutocomplete()` hook for search — it already handles debouncing and filtering.

**Positioning:** The popover appears below the cursor position in the textarea. Use the textarea's `selectionStart` to calculate approximate position.

**Props:**

```typescript
interface MergeFieldAutocompleteProps {
  ckeditorRef: React.RefObject<CKEditorSandboxRef>;  // Ref to CKEditor component
  onInsert: (syntax: string) => void;  // Insert at cursor
  isSourceMode: boolean;  // Only active in source mode
}
```

### 3. CKEditor Sandbox Extension — Insert at Cursor

**File:** `frontend/src/components/editor/CKEditorSandbox.tsx` (modify)

Add a new postMessage command to the CKEditor sandbox:

| Direction | Message | Purpose |
|-----------|---------|---------|
| Parent → iframe | `{ type: 'insertAtCursor', html: '...' }` | Insert HTML at current cursor position |
| Parent → iframe | `{ type: 'getMode' }` | Get current mode (wysiwyg or source) |
| iframe → Parent | `{ type: 'modeChanged', mode: 'wysiwyg' \| 'source' }` | Notify when mode switches |
| iframe → Parent | `{ type: 'cursorPosition', offset: number }` | Report cursor position in source mode |

**In the iframe's CKEditor instance:**

- For `insertAtCursor` in WYSIWYG mode: `editor.insertHtml(html)`
- For `insertAtCursor` in source mode: Insert text at textarea cursor position
- `getMode` returns `editor.mode` (`'wysiwyg'` or `'source'`)
- Listen for `editor.on('mode', ...)` to emit `modeChanged`

**Add to the component's ref interface:**

```typescript
interface CKEditorSandboxRef {
  // ... existing methods ...
  insertAtCursor: (html: string) => void;
  getMode: () => Promise<'wysiwyg' | 'source'>;
}
```

### 4. Merge Field Highlighting in Editor

**File:** `frontend/src/components/editor/MergeFieldHighlighter.tsx` (new)

An optional CSS overlay that highlights merge fields in the CKEditor preview.

**In WYSIWYG mode:**
- Inject CSS into the CKEditor iframe that highlights `[[...]]` patterns with a subtle background color (use the bronze accent from the design system — `rgba(188, 171, 138, 0.2)`)
- This makes merge fields visually distinct from regular text
- Toggle via a button in the editor toolbar

**Implementation:**
- Send a postMessage to inject a `<style>` block into the CKEditor iframe
- The CSS uses a combination of `::before`/`::after` pseudo-elements or, more practically, the CKEditor's `editor.on('contentDom', ...)` event to walk the DOM and wrap `[[...]]` patterns in `<span class="merge-field-highlight">` elements
- The highlights must be stripped before saving (they are editing-time-only visual aids)

**Note:** This is a nice-to-have. If implementation is complex due to CKEditor DOM restrictions, mark it as a TODO in the handoff and skip to the next deliverable.

### 5. Editor Page Integration

**File:** `frontend/src/app/templates/[id]/edit/page.tsx` (modify)

Integrate the new components into the editor page:

**Right sidebar tabs (add to existing):**

| Existing Tab | Agent 3 |
|-------------|---------|
| Forhåndsvisning | Preview tab |
| Validering | Validation tab |
| Innstillinger | Settings tab |
| Historikk | History tab |

| New Tab | Agent 6 |
|---------|---------|
| Flettekoder | `MergeFieldPanel` — browse, search, insert, generate |

**Editor toolbar additions:**
- Toggle button for merge field highlighting
- Quick insert button that opens a compact field picker popover

**Autocomplete:**
- Mount `MergeFieldAutocomplete` alongside the CKEditor component
- It activates only in source mode

### 6. Template Merge Field Analysis Update

**File:** `frontend/src/app/templates/[id]/edit/page.tsx` (modify) or new hook

When a template is loaded in the editor, automatically extract and display the merge fields found in the content. Update this list whenever the content changes (debounced to avoid performance issues).

Use `useTemplateAnalysis()` hook if it works client-side, or implement a lightweight client-side extraction using the regex pattern from `useElementInspector`:

```typescript
const MERGE_FIELD_REGEX = /\[\[([^\]]+)\]\]/g;
```

---

## Scope Boundaries

**In scope:**
- Merge field panel in editor sidebar
- Inline autocomplete for `[[` trigger in source mode
- CKEditor insert-at-cursor capability
- Merge field highlighting in WYSIWYG mode (nice-to-have)
- Integration into the editor page
- Connecting existing Flettekode components to the editor

**Out of scope (do NOT do these):**
- Building new merge field components (reuse existing ones)
- Modifying the merge field database or API
- Building a new Flettekode library page (it already exists)
- Schema changes (Agent 3 handled this)
- CKEditor configuration changes beyond insert-at-cursor (Agent 3 configured ACF)
- Template comparison (Agent 4)
- Template deduplication (Agent 5)

---

## Reuse Strategy

You are primarily an **integrator**. Here is what already exists and how to reuse it:

| Component | Location | How to reuse |
|-----------|----------|-------------|
| `FlettekodeLibrary` | `components/flettekoder/FlettekodeLibrary.tsx` | Embed in "Felt" tab, swap `onCopy` → `onInsert` |
| `CodeGenerator` | `components/flettekoder/CodeGenerator.tsx` | Embed in "Generator" tab, swap `onCopy` → `onInsert` |
| `MergeFieldCard` | `components/flettekoder/MergeFieldCard.tsx` | Use in "I bruk" tab for field display |
| `MergeFieldSearch` | `components/flettekoder/MergeFieldSearch.tsx` | Use at top of "Felt" tab for quick search |
| `useMergeFields` | `hooks/use-merge-fields.ts` | Data fetching for field browser |
| `useMergeFieldCategories` | `hooks/use-merge-fields.ts` | Category list for sidebar |
| `useMergeFieldAutocomplete` | `hooks/use-merge-field-autocomplete.ts` | Autocomplete suggestions for inline `[[` trigger |
| `useElementInspector` | `hooks/use-element-inspector.ts` | `getMergeFieldsInElement()` for "I bruk" extraction |

If a component needs minor modifications to accept an `onInsert` callback alongside `onCopy`, prefer adding the new prop rather than changing existing behavior — the standalone Flettekoder page still uses `onCopy`.

---

## Testing

- Open the editor for a template containing merge fields
- Verify the "Flettekoder" tab appears in the right sidebar
- Browse fields by category, click a field, verify it inserts at the cursor in CKEditor
- Use the code generator to build a `vitec-if` block, insert it, verify correct HTML in source view
- Switch to source mode, type `[[`, verify autocomplete appears
- Type a partial field name, verify suggestions filter correctly
- Select a suggestion, verify `[[field.path]]` is inserted
- Check the "I bruk" tab shows all merge fields found in the current template
- If merge field highlighting is implemented, toggle it and verify `[[...]]` patterns are visually highlighted
- Save the template and verify merge fields are preserved (not mangled by highlighting cleanup)
- Run frontend linting (`npm run lint`)

---

## Rules

- Follow existing code patterns in the codebase (read CLAUDE.md)
- No `any` in TypeScript
- Use design system tokens for all UI work (read `.planning/codebase/DESIGN-SYSTEM.md`)
- Reuse existing components — do not rebuild what exists
- Do NOT commit or push — just make the changes
- If anything is unclear, ASK before proceeding

---

## Handoff Summary

When complete, produce a handoff summary in this exact format:

---
**AGENT 6 COMPLETE — PHASE 11 FINISHED**

**Files created:**
- [ ] `frontend/src/components/editor/MergeFieldPanel.tsx`
- [ ] `frontend/src/components/editor/MergeFieldAutocomplete.tsx`
- [ ] `frontend/src/components/editor/MergeFieldHighlighter.tsx` (if implemented)

**Files modified:**
- [ ] `frontend/src/components/editor/CKEditorSandbox.tsx` (added insertAtCursor, getMode, modeChanged)
- [ ] `frontend/src/app/templates/[id]/edit/page.tsx` (added Flettekoder tab, autocomplete, toolbar buttons)

**Existing components reused:**
- [ ] `FlettekodeLibrary` (in Felt tab)
- [ ] `CodeGenerator` (in Generator tab)
- [ ] `MergeFieldCard` (in I bruk tab)
- [ ] `MergeFieldSearch` (in search bar)
- [ ] `useMergeFields` hook
- [ ] `useMergeFieldCategories` hook
- [ ] `useMergeFieldAutocomplete` hook

**Features delivered:**
- [ ] Merge field browsing and insertion from editor sidebar
- [ ] Code generator (vitec-if/foreach) insertion from editor sidebar
- [ ] "In use" merge field list
- [ ] Inline autocomplete on `[[` in source mode
- [ ] Merge field highlighting in WYSIWYG mode (Delivered / Skipped — explain)

**Test results:**
- Field insertion via panel: Pass/Fail
- Code generator insertion: Pass/Fail
- Autocomplete trigger and selection: Pass/Fail
- "In use" field extraction: Pass/Fail
- Merge field highlighting toggle: Pass/Fail/Skipped
- Content save preserves merge fields: Pass/Fail
- Linting: Pass/Fail

**Issues encountered:** (list any or "None")

**Phase 11 status:** All 6 agents complete / Issues remaining (list)
---
