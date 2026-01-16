---
name: Fix Import Script Gaps
overview: ""
todos:
  - id: skip-junk
    content: Add ~ prefix skip for Office lock files
    status: completed
  - id: extend-extensions
    content: Add DOCX/PDF/XLSX to supported extensions + MIME types
    status: completed
  - id: binary-handling
    content: "Branch logic: HTML=sanitize, Binary=read_bytes"
    status: completed
  - id: progress-counter
    content: Add simple [x/Total] progress logging
    status: completed
---

# Fix Import Script - 3 Critical Gaps

## Overview

Update [`backend/scripts/import_library_templates.py`](backend/scripts/import_library_templates.py) to handle binary files, skip junk files, and add progress logging.

## Changes

### 1. Support Binary Files

**Extend supported extensions:**

```python
# Line 51 - Update
SUPPORTED_EXTENSIONS = {'.html', '.htm', '.docx', '.doc', '.pdf', '.xlsx', '.xls'}
```

**Update `_import_template()` method to branch on file type:**

```python
is_html = file_path.suffix.lower() in {'.html', '.htm'}

if is_html:
    # Read as text with encoding fallback
    try:
        content = file_path.read_text(encoding='utf-8')
    except UnicodeDecodeError:
        content = file_path.read_text(encoding='latin-1')
    
    # Sanitize HTML content
    sanitized_content = self.sanitizer.sanitize(content)
    file_bytes = sanitized_content.encode('utf-8')
    db_content = sanitized_content  # Store in DB content field
else:
    # Read binary file (docx/pdf/xlsx)
    file_bytes = file_path.read_bytes()
    db_content = None  # Binary files don't store content in DB

# Upload to Azure (both use io.BytesIO)
blob_url = await self.storage_service.upload_file(
    file_data=io.BytesIO(file_bytes),
    blob_name=blob_name,
    content_type=content_type  # Set based on extension
)
```

**Add MIME type mapping:**

```python
MIME_TYPES = {
    '.html': 'text/html',
    '.htm': 'text/html',
    '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
    '.doc': 'application/msword',
    '.pdf': 'application/pdf',
    '.xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    '.xls': 'application/vnd.ms-excel',
}
```

### 2. Ignore Junk Files

**Update file skip check (line 156):**

```python
# Current
if item.name.startswith('.') or item.name in SKIP_FOLDERS:

# Updated - also skip Office lock files (~$)
if item.name.startswith('.') or item.name.startswith('~') or item.name in SKIP_FOLDERS:
```

### 3. Progress Visualization

**Add simple counter logging (no new dependencies):**

In `_process_directory()`, first collect all files, then process with counter:

```python
# Collect all files first
all_files = list(self._collect_files(self.source_path))
total = len(all_files)

for idx, (file_path, category_name) in enumerate(all_files, 1):
    logger.info(f"Processing [{idx}/{total}]: {category_name}/{file_path.name}")
    await self._import_template(session, file_path, category_name)
```

## Verification

1. Run with `--dry-run` to verify file discovery
2. Check that `~$` and `.` files are skipped
3. Confirm binary files upload without sanitization errors