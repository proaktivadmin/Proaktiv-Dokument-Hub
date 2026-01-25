# Photo Export for Signatures - HANDOVER

**Date:** 2026-01-25  
**Status:** Scripts Complete, Awaiting Manual Upload  
**Next Agent:** Continue with WebDAV upload and database update

---

## Summary

Created Python scripts to export employee photos and office banners from `proaktiv.no` into a local folder structure, ready for manual upload to WebDAV. This supports the email signature system which needs profile photos for the `{{EmployeePhotoUrl}}` placeholder.

---

## Work Completed

### 1. Employee Photo Export Script

**File:** `backend/scripts/export_homepage_employee_photos.py`

Crawls proaktiv.no employee profile pages and downloads photos locally.

**Architecture:**
```
Target: proaktiv.no/d/photos/employees/{email}.jpg
Example: https://proaktiv.no/d/photos/employees/froyland@proaktiv.no.jpg
```

**Features:**
- Uses Firecrawl/httpx for crawling proaktiv.no
- Extracts images from `og:image` meta tags (most reliable)
- Filters out external users (non-@proaktiv.no emails)
- Generates manifest.json, CSV map, and summary files
- Supports `--dry-run`, `--force`, `--deep-employees` flags

**Output Location:** `C:\Users\Adrian\Documents\ProaktivPhotos\webdav-upload\photos\employees\`

**Usage:**
```powershell
cd backend
python scripts/export_homepage_employee_photos.py --dry-run          # Preview
python scripts/export_homepage_employee_photos.py --deep-employees   # Full run
```

**Key Fix Applied:**
The `og:image` meta tag extraction was added to `sync_proaktiv_directory.py` because employee profile photos aren't in standard `<img>` tags.

---

### 2. Office Banner Export Script

**File:** `backend/scripts/export_office_banners.py`

Crawls proaktiv.no office pages and downloads banner images locally.

**Architecture:**
```
Target: proaktiv.no/d/photos/offices/{office_slug}.jpg
Example: https://proaktiv.no/d/photos/offices/proaktiv-drammen-lier-holmestrand.jpg
```

**Features:**
- Identifies office pages by URL pattern (exactly 3 segments, slug starts with "proaktiv-")
- Extracts banner from `og:image` meta tag
- Generates office_manifest.json, CSV map, and summary files
- Handles multi-office cities (Trondheim, Bergen, Sarpsborg)

**Output Location:** `C:\Users\Adrian\Documents\ProaktivPhotos\webdav-upload\photos\offices\`

**Usage:**
```powershell
cd backend
python scripts/export_office_banners.py --dry-run   # Preview
python scripts/export_office_banners.py             # Full run
```

**Key Fix Applied:**
The `is_office_page()` function was refined to distinguish office pages from employee pages by checking for `proaktiv-` prefix in the slug.

---

### 3. Signature Template Updates

**Files Modified:**
- `backend/scripts/templates/email-signature.html` - Added `{{EmployeePhotoUrl}}` placeholder
- `backend/app/services/signature_service.py` - Added `_resolve_employee_photo_url()` method

**Photo URL Resolution Priority:**
1. `employee.profile_image_url` (if not empty and not a Vitec API path)
2. Fallback to placeholder logo

---

### 4. Frontend Employee Card Link

**File:** `frontend/src/components/employees/EmployeeCard.tsx`

Added external link icon next to employee name that opens their proaktiv.no profile page.

```typescript
{employee.homepage_profile_url && (
  <a href={employee.homepage_profile_url} target="_blank" ...>
    <ExternalLink className="h-3.5 w-3.5" />
  </a>
)}
```

---

## Output Files Generated

### Employee Photos
| File | Purpose |
|------|---------|
| `photos/employees/*.jpg` | Downloaded employee photos |
| `manifest.json` | Full export metadata |
| `employee_photo_map.csv` | Email → photo path mapping |
| `missing_images.txt` | Employees without photos |
| `summary.json` | Export statistics |

### Office Banners
| File | Purpose |
|------|---------|
| `photos/offices/*.jpg` | Downloaded office banners |
| `office_manifest.json` | Full export metadata |
| `office_banner_map.csv` | Office → banner path mapping |
| `missing_office_banners.txt` | Offices without banners |
| `office_summary.json` | Export statistics |

---

## Pending Tasks (for Next Agent)

### 1. Manual WebDAV Upload
Upload the local folders to WebDAV:
```
C:\Users\Adrian\Documents\ProaktivPhotos\webdav-upload\photos\
  └── employees/   → proaktiv.no/d/photos/employees/
  └── offices/     → proaktiv.no/d/photos/offices/
```

**Warning:** The proaktiv.no WebDAV is live. Do not modify existing folder structure.

### 2. Database Update Scripts
Create scripts to update database records:

**For Employees:**
```python
# Update employees.profile_image_url from employee_photo_map.csv
UPDATE employees SET profile_image_url = 'https://proaktiv.no/d/photos/employees/{email}.jpg'
WHERE email = '{email}';
```

**For Offices:**
```python
# Update offices.banner_image_url from office_banner_map.csv
UPDATE offices SET banner_image_url = 'https://proaktiv.no/d/photos/offices/{slug}.jpg'
WHERE homepage_url = '{homepage_url}';
```

### 3. Verify Signature Rendering
After photos are uploaded:
1. Test signature preview on employee detail page
2. Verify photo loads in rendered signature HTML
3. Test copy-to-clipboard functionality

---

## Missing Employees Summary

Some employees don't have photos because:
- **TEST USER** - Test accounts
- **Accounting staff** - Back-office employees without profile pages
- **External users** - Employees with non-@proaktiv.no emails (visma.com, etc.)

See `C:\Users\Adrian\Documents\ProaktivPhotos\MISSING_EMPLOYEES_SUMMARY.md` for full list.

---

## Technical Notes

### og:image Extraction
Employee profile pages on proaktiv.no use dynamically rendered images that appear in `<meta property="og:image">` tags, not standard `<img>` tags. The `extract_image_url()` function in `sync_proaktiv_directory.py` was updated to prioritize this.

### Filename Convention
- Employees: `{email}.jpg` (e.g., `froyland@proaktiv.no.jpg`)
- Offices: `{office_slug}.jpg` (e.g., `proaktiv-drammen-lier-holmestrand.jpg`)

### Page Classification
Office pages have exactly 3 URL segments and the third segment starts with "proaktiv-":
- `/eiendomsmegler/drammen-lier/proaktiv-drammen-lier-holmestrand` → Office ✓
- `/eiendomsmegler/drammen-lier/alexander-abelseth` → Employee ✗

---

## Related Files

| File | Description |
|------|-------------|
| `backend/scripts/sync_proaktiv_directory.py` | Base crawling functions (reused) |
| `backend/scripts/export_homepage_employee_photos.py` | Employee photo export |
| `backend/scripts/export_office_banners.py` | Office banner export |
| `backend/app/services/signature_service.py` | Signature rendering |
| `backend/scripts/templates/email-signature.html` | Signature template |
| `frontend/src/components/employees/EmployeeCard.tsx` | Employee card UI |

---

## Related Documentation

- `.planning/phases/09-signature-portal/COMPLETED.md` - Signature portal completion
- `.planning/phases/09-signature-portal/SPEC.md` - Signature portal spec
- `docs/features/photo-export/TASKS.md` - Original photo export tasks (different feature)
