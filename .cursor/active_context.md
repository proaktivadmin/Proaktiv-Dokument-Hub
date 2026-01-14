# ACTIVE CONTEXT & ROADMAP

## PROJECT STATUS
- **Phase:** 2.6 (Document Preview & Simulator Enhancements)
- **Current Sprint:** ✅ COMPLETED & READY FOR DEPLOYMENT
- **Architecture:** Document-first, shelf grouping, 4-tab viewer
- **Last Milestone:** ✅ V2.6 Feature Complete (2026-01-15)

## V2.6 NEW FEATURES (2026-01-15)

### 1. Live Document Preview Thumbnails
- Template cards now show **live document previews** instead of static icons
- Uses IntersectionObserver for **lazy loading** (only loads when visible)
- 15% scale transform fits full document into thumbnail area
- File type icons for non-HTML files (PDF, DOCX, XLSX)
- Loading spinner and error fallback states

### 2. A4 Page Break Visualization
- Toggle button "Vis A4" / "Skjul A4" in preview toolbar
- Shows **red dashed lines** at A4 page boundaries (257mm content height)
- Yellow info banner explains the feature
- Badge indicator "A4 Sideskift" when active
- Helps identify where forced page breaks should be inserted

### 3. Simulator Test Data Persistence
- Default test data **pre-populated** with common Norwegian real estate fields
- **"Lagre" button** - Saves current values to localStorage as user defaults
- **"Standard" button** - Resets to hardcoded system defaults
- **"Tøm alle" button** - Clears all test values
- **Quick toggle** in preview toolbar to switch between original/test data
- Test data survives browser refresh

### 4. Code Generator (Flettekoder Page)
- New "Kodegenerator" tab in Flettekoder page
- Visual interface for building Vitec code snippets
- Supports: `vitec-if/else`, `vitec-foreach`, inline conditions
- One-click copy to clipboard
- Nesting support for complex conditions

## BROWSER TESTING RESULTS (2026-01-15)

### Templates Page (/templates)
- ✅ Shelf view is default (43 templates in "PDF & E-post" shelf)
- ✅ **NEW:** Live document preview thumbnails on cards
- ✅ Template cards display with titles, status badges
- ✅ Dropdown menus on cards (Preview/Edit/Download/Delete)
- ✅ Wrapped grid layout utilizes screen space efficiently
- ✅ Group-by selector (Kanal, Category, Status)
- ✅ Collapse/Expand all functionality

### Document Viewer (Centered Dialog)
- ✅ Opens as centered modal instead of side sheet
- ✅ 4 tabs: Forhåndsvisning, Kode, Innstillinger, Simulator
- ✅ Template preview with merge field highlighting (yellow)
- ✅ **NEW:** A4 page break visualization toggle
- ✅ **NEW:** Test data toggle in preview toolbar
- ✅ Monaco code editor loads with proper syntax highlighting
- ✅ Download and Edit buttons in header
- ✅ File size and timestamp in footer

### Simulator Tab
- ✅ Detects 67 variables from OPPDRAGSAVTALE template
- ✅ **NEW:** 39 variables pre-filled with default test data
- ✅ **NEW:** Save/Reset/Clear buttons for test data management
- ✅ "Forhåndsvis med testdata" applies substitutions
- ✅ Shows required field warnings

### Flettekoder Page (/flettekoder)
- ✅ 4 tabs: Variabler, Vitec Logic, Layout, **Kodegenerator**
- ✅ Category sidebar (Alle, Eiendom, Kjøper, Megler, Selger, etc.)
- ✅ 142 merge fields loaded from database
- ✅ **NEW:** Code Generator for building Vitec snippets visually
- ✅ Copy-to-clipboard functionality on each field

### Dashboard (/)
- ✅ Clean light theme with stats cards
- ✅ Totalt maler: 43, Publiserte: 43
- ✅ Nylig opplastet section with 5 recent templates
- ✅ Kategorier sidebar with category icons

## KEY FILES CHANGED (V2.6)

| File | Changes |
|------|---------|
| `frontend/src/components/shelf/TemplateCard.tsx` | Live document preview thumbnails |
| `frontend/src/components/templates/TemplatePreview.tsx` | A4 page break visualization, test data toggle |
| `frontend/src/components/templates/SimulatorPanel.tsx` | Persistent test data, save/reset/clear buttons |
| `frontend/src/components/templates/TemplateDetailSheet.tsx` | Test data state management |
| `frontend/src/components/flettekoder/CodeGenerator.tsx` | Visual code snippet builder |
| `frontend/src/app/flettekoder/page.tsx` | Added Kodegenerator tab |
| `frontend/public/vitec-theme.css` | A4 page break CSS styles |

## V2 CORE CONCEPTS

### Document-First Paradigm
- Preview is PRIMARY, code is SECONDARY
- Live thumbnails on cards for visual recognition
- Click elements to inspect code (ElementInspector)
- Monaco editor available in "Kode" tab

### Shelf Layout
- Templates grouped in horizontal shelves (wrapped grid)
- Default grouping: Channel (PDF, Email, SMS)
- Filtering dims non-matching cards (doesn't hide)

### Flettekode System
- Merge fields: `[[field.name]]` or `[[*field.name]]` (required)
- Conditions: `vitec-if="expression"`
- Loops: `vitec-foreach="item in collection"`
- Auto-discovery scans existing templates
- Visual code generator for non-coders

## COMPLETED (Phase 2.0-2.6)
- ✅ Dashboard Hydration
- ✅ Template Upload to Azure
- ✅ Template Preview (iframe + CSS)
- ✅ Template Detail Dialog (centered modal)
- ✅ Smart Sanitizer (page + API)
- ✅ Legacy Migration (43 templates)
- ✅ Shelf Library (wrapped grid)
- ✅ Monaco Code Editor
- ✅ Settings Panel (margins/header/footer/theme)
- ✅ Simulator Panel (variable detection + persistence)
- ✅ Flettekoder Library (Variables + Vitec Logic + Layout)
- ✅ **NEW:** Live document preview thumbnails
- ✅ **NEW:** A4 page break visualization
- ✅ **NEW:** Simulator test data persistence
- ✅ **NEW:** Visual code generator

## AZURE STORAGE STATUS
- **Container:** `templates`
- **Folders:** `legacy/` (38 files), `company-portal/` (5 files)
- **Total:** 43 templates with real Azure URLs
- **Connection:** ✅ Verified

## DEPLOYMENT READY
This version (V2.6) is ready for:
1. Git commit and push to GitHub
2. Azure deployment via existing CI/CD pipeline

## NEXT STEPS (Future)
- [ ] Backend endpoint for saving template content (PUT /api/templates/{id}/content)
- [ ] Backend endpoint for saving template settings
- [ ] Add more Vitec Logic patterns to snippets.json
- [ ] Static thumbnail generation for faster card loading
- [ ] Template versioning UI
