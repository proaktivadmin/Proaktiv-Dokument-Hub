# Photo Export Automation - Task Breakdown

## Overview
Python script to automate bulk property photo exports from proaktiv.no/export.

## Tasks

### Script Core
- [ ] **S1**: Create `backend/scripts/photo_export_bot.py`
- [ ] **S2**: Implement Excel parser (detect yellow highlighted rows)
- [ ] **S3**: Implement Playwright browser automation
- [ ] **S4**: Implement login flow (manual login, script continues)
- [ ] **S5**: Implement reference submission loop

### File Operations
- [ ] **F1**: Implement WebDAV polling (wait for export completion)
- [ ] **F2**: Implement folder copy from WebDAV to local Downloads
- [ ] **F3**: Add progress logging and error handling

### Testing
- [ ] **T1**: Test with small batch (2-3 references)
- [ ] **T2**: Test full workflow end-to-end

## Technical Details
- **Input**: Excel file (.xls) with yellow highlighted rows
- **Export Target**: `proaktiv.no/shared/[reference]/`
- **Local Output**: `~/Downloads/[reference]/`
- **Runtime**: ~1-2 min per property, 20-40 min total

## Dependencies
- `openpyxl` - Excel parsing
- `playwright` - Browser automation
- `shutil` - File operations
