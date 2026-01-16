---
name: V2_Transition_MasterPlan
overview: Comprehensive plan to transition to V2, featuring a UI overhaul, master cloud library with versioning, strict sanitization, header/footer management, and a snippet generator.
todos:
  - id: ui-glass-refactor
    content: Refactor Dashboard UI to 'Proaktiv Glass' (translucent/blur theme)
    status: pending
  - id: backend-versioning
    content: Implement Template Versioning (Backend + DB migration)
    status: pending
  - id: frontend-bulk-ops
    content: Implement Bulk Operations UI (Select rows -> Batch Action)
    status: pending
    dependencies:
      - ui-glass-refactor
  - id: backend-sanitizer-strict
    content: Enhance SanitizerService with Strict Mode and Diff Logic
    status: pending
  - id: feature-header-footer
    content: Create Header/Footer Management (DB Schema + Preview Modes)
    status: pending
    dependencies:
      - backend-versioning
  - id: feature-snippet-gen
    content: Build Vitec Snippet Generator (Data Model + Builder UI)
    status: pending
    dependencies:
      - ui-glass-refactor
---

# V2 Transition & Modernization Master Plan

## 1. UI Overhaul: "Proaktiv Glass" Design

**Goal:** Replace "Dark Aether" with a minimalistic, translucent, professional aesthetic.

- **Design Token System:** Define CSS variables for glassmorphism (background blur, translucent whites/grays) in `globals.css`.
- **Dashboard Refactor:**
- Remove solid dark blocks (e.g., `#272630` backgrounds).
- Implement `<GlassCard />` component using `backdrop-filter: blur()`, `bg-white/40`, and thin light borders.
- Update `Header` and `Sidebar` (if exists) to match the new translucent theme.
- Typography: Ensure crisp, professional serif/sans-serif pairing (Proaktiv brand fonts).

## 2. Master Cloud Library & Versioning

**Goal:** Robust cloud storage with history and bulk operations.

- **Backend (`LibraryService`):**
- **Versioning:** When updating a template, move the old blob to `archive/{id}/{timestamp}_{filename}` in Azure, then update the DB record to point to the new blob. Keep a `template_versions` table for history.
- **Backup:** Implement a nightly job (Azure Function or Cron in Backend) to snapshot the `templates` container to a separate `backup` container.
- **Frontend (Bulk Operations):**
- Add checkboxes to `TemplateTable`.
- Implement Batch Actions Bar: "Archive Selected", "Update Category", "Sanitize Selected".

## 3. Advanced Sanitizer Tool

**Goal:** Enforce strict code standards and strip built-in design.

- **Backend (`SanitizerService` Enhancements):**
- **Strict Mode:** Create a `strict=True` flag that ignores "already valid" checks if forced.
- **Strip Logic:** Enhance `BeautifulSoup` logic to aggressively remove `style` tags, `class` attributes (unless whitelisted), and specific wrapper divs that aren't `#vitecTemplate`.
- **Enforcement:** Ensure every template wraps content in `#vitecTemplate` with the correct theme class.
- **Frontend (Sanitizer UI):**
- Add "Sanitize" button to Template Detail view.
- Show "Diff View" (Original vs. Sanitized) before saving.

## 4. Header & Footer Management

**Goal:** Specialized management for header/footer partials with multi-context preview.

- **Database:**
- Create `headers` and `footers` tables (or add `type` enum to `templates`).
- Add `context` field: `pdf_email`, `email_only`, `sms`.
- **Preview Engine:**
- Create `LayoutPreview` component.
- **Modes:**
- **PDF/Email:** Header + Body + Footer (A4 simulation).
- **Email Only:** Simplified Header + Body + Footer (Mobile/Desktop view).
- **SMS:** Text-only preview (strip HTML).
- Simulate Vitec padding/layout rules using CSS Grid/Flexbox in the preview iframe.

## 5. Vitec Snippet Generator

**Goal:** No-code tool to generate Vitec-specific HTML snippets.

- **Data Model:**
- `snippets` table: `id`, `name`, `code_template`, `variables` (JSON schema).
- **Snippet Builder UI:**
- **Library View:** List of available Vitec snippets (e.g., "Broker Info", "Property Details").
- **Builder View:** Form inputs based on `variables` JSON.
- *Example:* User types "John Doe" into "Broker Name" input -> Real-time HTML generation.
- **Clipboard Action:** "Copy HTML" button.
- **Variable Picker:** Click-to-add variables (`${megler_navn}`) into the builder.

## 6. V1 Feature Parity Check

- **Audit:** Since V1 source is compiled, relying on user feedback for specific missing "tools".
- **Assumption:** The above tools (Sanitizer, Header/Footer) cover the major functional gaps.

## Implementation Phases

1. **Phase 1 (UI & Core):** Glass UI Refactor + Master Library Versioning.
2. **Phase 2 (Tools):** Advanced Sanitizer + Header/Footer Management.
3. **Phase 3 (Automation):** Snippet Generator + Batch Operations.