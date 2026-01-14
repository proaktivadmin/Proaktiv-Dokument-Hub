# QA Review Checklist - V2 Implementation

**Date:** 2026-01-14  
**Phase:** 2.1 Document-First MVP  
**Status:** Ready for QA

---

## ✅ Backend Setup Complete

### Database Migrations
- [x] Migration `20260114_0001_v2_tables.py` applied successfully
- [x] All V2 tables created:
  - `merge_fields` (142 records)
  - `code_patterns` (0 records - ready for user input)
  - `layout_partials` (0 records - ready for user input)
- [x] Vitec metadata columns added to `templates` table

### API Endpoints Verified
- [x] `GET /api/merge-fields` - Returns 142 merge fields
- [x] `GET /api/merge-fields/categories` - Returns 6 categories
- [x] `GET /api/code-patterns` - Returns empty list (ready for data)
- [x] `GET /api/layout-partials` - Returns empty list (ready for data)
- [x] `GET /api/templates/{id}/analyze` - Analyzes template and finds merge fields

---

## 🧪 Frontend Manual Testing Required

### Test 1: Templates Page - Shelf View Toggle
**URL:** http://localhost:3000/templates

**Steps:**
1. Navigate to `/templates`
2. Look for view toggle buttons in top-right (Liste / Hylle)
3. Click "Hylle" button to switch to shelf view
4. Verify:
   - [ ] Templates are grouped in horizontal shelves
   - [ ] Each shelf has a header with title and count
   - [ ] Cards show thumbnail, title, and metadata
   - [ ] Horizontal scroll works with arrow buttons
   - [ ] Can switch back to "Liste" view
   - [ ] Group-by selector works (Channel, Category, Status)

**Expected Behavior:**
- Default view: Table (existing functionality preserved)
- Shelf view: Templates grouped by channel (PDF, Email, SMS)
- Smooth transitions between views
- No console errors

---

### Test 2: Flettekode Library Page
**URL:** http://localhost:3000/flettekoder

**Steps:**
1. Navigate to `/flettekoder`
2. Verify left sidebar shows categories:
   - [ ] Eiendom
   - [ ] Kjøper
   - [ ] Megler
   - [ ] Selger
   - [ ] Økonomi
   - [ ] Ukjent
3. Test category filtering:
   - [ ] Click on a category
   - [ ] Grid updates to show only that category
   - [ ] Count updates in sidebar
4. Test search:
   - [ ] Type "eiendom" in search box
   - [ ] Results filter in real-time
   - [ ] Autocomplete suggestions appear
5. Test merge field cards:
   - [ ] Each card shows path, label, category
   - [ ] Click "Kopier" button copies `[[path]]` to clipboard
   - [ ] Toast notification appears on copy

**Expected Behavior:**
- 142 merge fields displayed
- Fast filtering and search
- Copy functionality works
- No console errors

---

### Test 3: Document Viewer Page
**URL:** http://localhost:3000/templates/{template_id}

**Test Template ID:** `678824da-b620-4412-af8d-174ded5f3ffa`

**Steps:**
1. Navigate to `/templates/678824da-b620-4412-af8d-174ded5f3ffa`
2. Verify 4 preview modes:
   - [ ] A4 (PDF) - Default view
   - [ ] Desktop (1200px)
   - [ ] Mobile (375px)
   - [ ] SMS (plain text)
3. Test mode switching:
   - [ ] Click each tab
   - [ ] Preview updates correctly
   - [ ] Dimensions change appropriately
4. Test Element Inspector:
   - [ ] Click on an element in the preview
   - [ ] Inspector panel opens on right
   - [ ] Shows HTML code for clicked element
   - [ ] Syntax highlighting works
   - [ ] Can close inspector
5. Test template analysis:
   - [ ] Analysis panel shows detected merge fields
   - [ ] Shows loops and conditions
   - [ ] Lists unknown fields

**Expected Behavior:**
- Preview renders HTML correctly
- Click-to-inspect works
- Mode switching is smooth
- No console errors

---

## 🔍 Browser Console Checks

For each page, check browser console (F12) for:
- [ ] No TypeScript errors
- [ ] No React errors
- [ ] No 404 errors for API calls
- [ ] No CORS errors
- [ ] API responses are 200 OK

---

## 📊 Performance Checks

- [ ] `/templates` page loads in < 2 seconds
- [ ] `/flettekoder` page loads in < 2 seconds
- [ ] Shelf view renders 40+ templates smoothly
- [ ] Search/filter is responsive (< 300ms)
- [ ] No memory leaks (check DevTools Memory tab)

---

## 🎨 UI/UX Checks

### Consistency
- [ ] Proaktiv Premium theme applied (Navy/Bronze/Beige)
- [ ] Shadcn/UI components styled correctly
- [ ] Responsive design works on different screen sizes
- [ ] Icons from Lucide React display properly

### Accessibility
- [ ] Buttons have hover states
- [ ] Focus states visible for keyboard navigation
- [ ] Color contrast meets WCAG standards
- [ ] Loading states show spinners/skeletons

---

## 🐛 Known Issues / Deferred Items

### Minor Issues
1. **snippets.json path**: Seed script couldn't find `/resources/snippets.json` in Docker container
   - **Workaround**: Auto-discovery worked and found 142 fields
   - **Fix needed**: Update Docker volume mount or script path

### Future Enhancements
1. Code Patterns page (`/patterns`) - Not implemented (not in spec)
2. Layout Partials page (`/layouts`) - Not implemented (not in spec)
3. Merge field category counts - Currently hardcoded to 0, needs dedicated endpoint
4. Template thumbnails - Using placeholder, needs Azure Blob integration

---

## ✅ Sign-Off

### Developer
- **Name:** BUILDER Agent
- **Date:** 2026-01-14
- **Status:** Implementation Complete

### QA Reviewer
- **Name:** _____________
- **Date:** _____________
- **Status:** [ ] Approved / [ ] Needs Fixes

### Notes:
_Add any additional findings or comments here_

---

## 📝 Next Steps After QA

1. Fix any critical bugs found
2. Address UI/UX feedback
3. Update documentation with screenshots
4. Create user guide for Flettekode system
5. Plan Phase 2.2 features
