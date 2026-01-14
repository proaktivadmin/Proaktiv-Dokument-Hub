---
name: V2_Architect_Blueprint
overview: Agent-ready architectural blueprint for V2 Dokument Hub. Document-first approach with shelf-based template library, Flettekode system, and 4-mode preview. For Architect agent to create implementation specs for Builder agent.
todos:
  - id: architect-update-cursorrules
    content: Update .cursorrules with V2 patterns (document-first, shelf-layout, etc.)
    status: pending
  - id: architect-update-context
    content: Update .cursor/active_context.md with Phase 2.1 roadmap
    status: pending
  - id: architect-db-migrations
    content: Spec out all DB migrations (metadata fields + new tables)
    status: pending
    dependencies:
      - architect-update-context
  - id: architect-shelf-layout-spec
    content: Create ShelfLayout component spec with props and behavior
    status: pending
  - id: architect-viewer-spec
    content: Create DocumentViewer spec with 4 frame modes
    status: pending
  - id: architect-flettekode-spec
    content: Create MergeField system spec (model, service, analyzer)
    status: pending
  - id: architect-file-structure
    content: Document complete file structure additions
    status: pending
  - id: architect-handoff-doc
    content: Create Builder Agent handoff document with implementation order
    status: pending
    dependencies:
      - architect-db-migrations
      - architect-shelf-layout-spec
      - architect-viewer-spec
      - architect-flettekode-spec
---

# V2 ARCHITECT BLUEPRINT

## AGENT INSTRUCTIONS

```
ROLE: System/Frontend Architect
INPUT: This blueprint
OUTPUT: 
  1. Updated .cursorrules with new patterns
  2. Updated .cursor/active_context.md with V2 roadmap
  3. Technical implementation specs per feature
  4. File structure additions
  5. DB migration specs
  6. Component hierarchy diagrams

HANDOFF TO: Builder Agent
HANDOFF FORMAT: Implementation-ready specs with file paths, function signatures, and test criteria
```

---

## CORE PHILOSOPHY

```yaml
paradigm: document-first
primary_view: rendered_preview
secondary_view: code_inspector
code_editing: last_resort_only
visual_recognition: thumbnail_cards
grouping: shelf_swimlanes
```

---

## FEATURE SPECIFICATIONS

### F1: TEMPLATE LIBRARY (SHELF LAYOUT)

```yaml
feature_id: template-library-shelf
priority: P0
dependencies: []

view:
  default: grid_cards
  grouping: 
    default: channel  # PDF | E-post | SMS
    options: [phase, receiver, category, ownership_type]
  
cards:
  thumbnail: 
    source: preview_thumbnail_url
    fallback: file_type_icon
    dimensions: 160x200
  badges: [channel_type, status]
  actions: [settings, code_view, preview]
  
shelves:
  layout: horizontal_scroll
  features:
    - collapse_expand
    - card_count_badge
    - scroll_arrows
    
filtering:
  behavior: dim_non_matching  # opacity: 0.3
  hide_empty_shelves: true
  search_scope: [title, description, category]
```

**DB Changes:**

```sql
ALTER TABLE templates ADD COLUMN preview_thumbnail_url TEXT;
ALTER TABLE templates ADD COLUMN channel VARCHAR(20) DEFAULT 'pdf_email';
-- channel ENUM: 'pdf', 'email', 'sms', 'pdf_email'
```

**Files to create:**

- `frontend/src/app/templates/page.tsx` (refactor)
- `frontend/src/components/templates/ShelfLayout.tsx`
- `frontend/src/components/templates/TemplateCard.tsx`
- `frontend/src/components/templates/HorizontalScroll.tsx`
- `frontend/src/hooks/useGroupedTemplates.ts`

---

### F2: TEMPLATE METADATA (VITEC PARITY)

```yaml
feature_id: template-metadata-vitec
priority: P0
dependencies: [template-library-shelf]

fields:
  # Core Identity
  - name: template_type
    label: Maltype
    type: select
    options: [Objekt/Kontakt, System]
    priority: P1
    
  - name: receiver_type
    label: Mottakertype
    type: select
    options: [Egne/kundetilpasset, Systemstandard]
    priority: P1
    
  - name: receiver
    label: Mottaker
    type: select
    options: [Selger, Kjøper, Megler, Bank, Forretningsfører]
    priority: P1
    
  - name: extra_receivers
    label: Ekstra mottakere
    type: multiselect
    priority: P2
    
  # Filtering
  - name: channel
    label: Kanaler
    type: select
    options: [PDF, E-post, SMS, PDF og e-post]
    priority: P1
    
  - name: phases
    label: Faser
    type: multiselect
    options: [Oppdrag, Markedsføring, Visning, Budrunde, Kontrakt, Oppgjør]
    priority: P1
    
  - name: assignment_types
    label: Oppdragstyper
    type: multiselect
    priority: P2
    
  - name: ownership_types
    label: Eierformer
    type: multiselect
    options: [Bolig, Aksje, Tomt, Næring, Hytte]
    priority: P2
    
  - name: departments
    label: Avdelinger
    type: multiselect
    priority: P2
    
  # Email
  - name: email_subject
    label: Emne
    type: text_with_merge_fields
    priority: P1
    
  # PDF
  - name: header_template_id
    label: Topptekst
    type: foreign_key
    references: layout_partials
    priority: P1
    
  - name: footer_template_id
    label: Bunntekst
    type: foreign_key
    references: layout_partials
    priority: P1
    
  - name: margin_top
    label: Topp
    type: decimal
    unit: cm
    default: 1.5
    priority: P1
    
  - name: margin_bottom
    label: Bunn
    type: decimal
    unit: cm
    default: 1.0
    priority: P1
    
  - name: margin_left
    label: Venstre
    type: decimal
    unit: cm
    default: 1.0
    priority: P1
    
  - name: margin_right
    label: Høyre
    type: decimal
    unit: cm
    default: 1.2
    priority: P1
```

**DB Migration:**

```sql
-- backend/alembic/versions/YYYYMMDD_vitec_metadata.py
ALTER TABLE templates 
  ADD COLUMN template_type VARCHAR(50) DEFAULT 'Objekt/Kontakt',
  ADD COLUMN receiver_type VARCHAR(50),
  ADD COLUMN receiver VARCHAR(100),
  ADD COLUMN extra_receivers JSONB DEFAULT '[]',
  ADD COLUMN phases JSONB DEFAULT '[]',
  ADD COLUMN assignment_types JSONB DEFAULT '[]',
  ADD COLUMN ownership_types JSONB DEFAULT '[]',
  ADD COLUMN departments JSONB DEFAULT '[]',
  ADD COLUMN email_subject VARCHAR(500),
  ADD COLUMN header_template_id UUID REFERENCES layout_partials(id),
  ADD COLUMN footer_template_id UUID REFERENCES layout_partials(id),
  ADD COLUMN margin_top DECIMAL(4,2) DEFAULT 1.5,
  ADD COLUMN margin_bottom DECIMAL(4,2) DEFAULT 1.0,
  ADD COLUMN margin_left DECIMAL(4,2) DEFAULT 1.0,
  ADD COLUMN margin_right DECIMAL(4,2) DEFAULT 1.2;
```

---

### F3: DOCUMENT-FIRST VIEWER

```yaml
feature_id: document-viewer
priority: P0
dependencies: [template-metadata-vitec]

modes:
  - id: a4
    label: A4/PDF
    dimensions: 210mm x 297mm
    show_margins: true
    show_header_footer: true
    
  - id: desktop_email
    label: Desktop E-post
    dimensions: 960px width
    wrapper: outlook_desktop_chrome
    
  - id: mobile_email
    label: Mobil E-post
    dimensions: 340px width
    wrapper: iphone_bezel
    
  - id: sms
    label: SMS/iMessage
    dimensions: 340px width
    wrapper: imessage_bubble
    strip_html: true

inspector:
  trigger: click_on_element
  panel_position: bottom
  features:
    - show_html_code
    - copy_button
    - element_path_breadcrumb
    - highlight_merge_fields
```

**Files to create:**

- `frontend/src/app/templates/[id]/page.tsx`
- `frontend/src/components/viewer/DocumentViewer.tsx`
- `frontend/src/components/viewer/A4Frame.tsx`
- `frontend/src/components/viewer/DesktopEmailFrame.tsx`
- `frontend/src/components/viewer/MobileEmailFrame.tsx`
- `frontend/src/components/viewer/SMSFrame.tsx`
- `frontend/src/components/viewer/ElementInspector.tsx`
- `frontend/src/components/viewer/PreviewModeSelector.tsx`

---

### F4: FLETTEKODE LIBRARY

```yaml
feature_id: flettekode-library
priority: P1
dependencies: []

data_model:
  table: merge_fields
  columns:
    - id: UUID PK
    - path: VARCHAR(200) UNIQUE  # e.g., "eiendom.adresse"
    - category: VARCHAR(100)     # e.g., "Eiendom", "Selger"
    - label: VARCHAR(200)        # e.g., "Adresse"
    - description: TEXT
    - example_value: VARCHAR(500)
    - data_type: VARCHAR(50)     # string, number, date, boolean
    - is_iterable: BOOLEAN       # can use in vitec-foreach
    - parent_model: VARCHAR(100) # Model.selgere

seed_data:
  source: resources/snippets.json
  count: 23
  
auto_discovery:
  scan_templates: true
  patterns:
    merge_field: '\[\[(\*?)([^\]]+)\]\]'
    vitec_if: 'vitec-if="([^"]+)"'
    vitec_foreach: 'vitec-foreach="(\w+)\s+in\s+([^"]+)"'

ui:
  page: /flettekoder
  layout: sidebar_categories + main_grid
  features:
    - search_with_autocomplete
    - category_filter_sidebar
    - click_to_copy
    - usage_count_badge
```

**Files to create:**

- `backend/app/models/merge_field.py`
- `backend/app/services/merge_field_service.py`
- `backend/app/services/template_analyzer_service.py`
- `backend/app/routers/merge_fields.py`
- `frontend/src/app/flettekoder/page.tsx`
- `frontend/src/components/flettekoder/MergeFieldCard.tsx`
- `frontend/src/components/flettekoder/CategorySidebar.tsx`
- `frontend/src/hooks/useMergeFields.ts`

---

### F5: PATTERN LIBRARY

```yaml
feature_id: pattern-library
priority: P1
dependencies: [flettekode-library]

data_model:
  table: code_patterns
  columns:
    - id: UUID PK
    - name: VARCHAR(200)
    - category: VARCHAR(100)
    - description: TEXT
    - html_code: TEXT
    - variables_used: JSONB  # array of merge_field paths
    - preview_thumbnail_url: TEXT
    - usage_count: INTEGER DEFAULT 0

examples:
  - name: "Selger-tabell med kontaktinfo"
    category: "Tabeller"
    html_code: "<table vitec-foreach='selger in Model.selgere'>..."
    
  - name: "Eiendom aksje-betingelse"
    category: "Betingelser"
    html_code: "<div vitec-if='Model.eiendom.eieform == \"Aksje\"'>..."

ui:
  page: /patterns
  layout: grid_cards
  features:
    - thumbnail_preview
    - click_to_copy
    - monaco_detail_view
```

**Files to create:**

- `backend/app/models/code_pattern.py`
- `backend/app/services/code_pattern_service.py`
- `backend/app/routers/code_patterns.py`
- `frontend/src/app/patterns/page.tsx`
- `frontend/src/components/patterns/PatternCard.tsx`
- `frontend/src/components/patterns/PatternDetail.tsx`

---

### F6: LAYOUT PARTIALS (HEADER/FOOTER)

```yaml
feature_id: layout-partials
priority: P1
dependencies: []

data_model:
  table: layout_partials
  columns:
    - id: UUID PK
    - name: VARCHAR(200)
    - type: VARCHAR(20)  # 'header' | 'footer'
    - context: VARCHAR(50)  # 'pdf' | 'email' | 'all'
    - html_content: TEXT
    - is_default: BOOLEAN DEFAULT FALSE

ui:
  page: /layouts
  features:
    - list_grouped_by_type
    - inline_preview
    - monaco_editor
    - set_as_default
```

**Files to create:**

- `backend/app/models/layout_partial.py`
- `backend/app/services/layout_partial_service.py`
- `backend/app/routers/layout_partials.py`
- `frontend/src/app/layouts/page.tsx`
- `frontend/src/components/layouts/PartialEditor.tsx`

---

### F7: VERSIONING (WIRE UP)

```yaml
feature_id: template-versioning
priority: P2
dependencies: []

existing_model: backend/app/models/template.py#TemplateVersion
status: model_exists_not_wired

implementation:
  location: backend/app/services/template_service.py#update()
  logic: |
    Before updating template:
    1. Create TemplateVersion record with current state
    2. Increment template.version
    3. Apply updates
    4. If file changed, archive old blob to Azure archive/{id}/
```

---

### F8: VISUAL BUILDER (PHASE 3)

```yaml
feature_id: visual-builder
priority: P3
dependencies: [flettekode-library, pattern-library]

technology: TipTap (ProseMirror)
npm_packages:
  - "@tiptap/react"
  - "@tiptap/starter-kit"
  - "@tiptap/extension-placeholder"

custom_nodes:
  - MergeFieldNode: renders [[field]] as inline badge
  - ConditionalBlock: renders vitec-if as bordered section
  - LoopBlock: renders vitec-foreach as repeated section

features:
  - insert_merge_field_from_picker
  - wrap_selection_in_condition
  - visual_condition_builder_modal
  - code_view_toggle (Monaco)
  - bidirectional_sync
```

---

### F9: GLASS UI

```yaml
feature_id: glass-ui
priority: P2
dependencies: []

design_tokens:
  --glass-bg: rgba(255, 255, 255, 0.7)
  --glass-blur: 12px
  --glass-border: rgba(255, 255, 255, 0.3)
  --surface: '#FAFAF8'
  --surface-elevated: rgba(255, 255, 255, 0.9)
  --accent-gold: '#BCAB8A'
  --accent-navy: '#272630'

components_to_create:
  - GlassCard
  - GlassInput
  - GlassSelect
```

---

## NAVIGATION STRUCTURE

```
/                     → Dashboard (stats, quick actions)
/templates            → Shelf Library (grid cards, grouped)
/templates/[id]       → Document Viewer (4 modes + inspector)
/flettekoder          → Merge Field Library
/patterns             → Code Pattern Library
/layouts              → Header/Footer Management
```

---

## CONTEXT FILES TO UPDATE

### .cursorrules additions:

```
## V2 PATTERNS
- DOCUMENT-FIRST: Preview is primary view, code is secondary
- SHELF-LAYOUT: Use ShelfLayout for template grouping
- CLICK-TO-INSPECT: ElementInspector for code viewing
- FLETTEKODE: All merge field operations through MergeFieldService
```

### .cursor/active_context.md updates:

```
## PHASE: 2.1 (Document-First MVP)
## CURRENT SPRINT: Template Library Shelf + Flettekode Foundation
## ARCHITECTURE: Document-first, shelf-based grouping, 4-mode preview
```

---

## IMPLEMENTATION ORDER

```
PHASE 1 (Foundation):
  1. DB migrations (metadata fields, merge_fields, code_patterns, layout_partials)
  2. Backend services (MergeFieldService, TemplateAnalyzerService)
  3. Auto-discovery scan of 43 templates
  4. Seed merge_fields from snippets.json

PHASE 2 (Library):
  5. ShelfLayout component
  6. TemplateCard with thumbnails
  7. Grouping logic (by channel)
  8. Dim filtering behavior
  9. /flettekoder page

PHASE 3 (Viewer):
  10. DocumentViewer with 4 modes
  11. Frame components (A4, Desktop, Mobile, SMS)
  12. ElementInspector (click-to-view-code)
  13. PreviewModeSelector

PHASE 4 (Polish):
  14. Glass UI tokens + components
  15. Pattern Library page
  16. Layout Partials management
  17. Wire up TemplateVersion

PHASE 5 (Visual Builder - Future):
  18. TipTap integration
  19. Custom nodes
  20. Condition builder modal
```