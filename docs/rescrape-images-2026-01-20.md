# Rescraping Images for Existing Records - 2026-01-20

## Objective
Update all existing offices and employees in the Railway production database with their profile pictures, banner images, and descriptions from proaktiv.no.

## Why This Is Needed
The initial database seeding may have been incomplete or missing image URLs. This rescrape ensures:
- ✅ All **office banner images** (`profile_image_url`) are captured
- ✅ All **employee profile pictures** (`profile_image_url`) are captured
- ✅ All **descriptions** (bios and presentation text) are updated
- ✅ All **social media links** are current

## Execution

### Command
```powershell
$env:RAILWAY_DATABASE_URL = "postgresql://postgres:***@shuttle.proxy.rlwy.net:51557/railway"
cd backend
py -3.12 -m scripts.sync_proaktiv_directory \
  --delay-ms 1500 \
  --max-pages 220 \
  --max-office-pages 24 \
  --max-employee-pages 220 \
  --max-runtime-minutes 40 \
  --start "https://proaktiv.no/eiendomsmegler/oslo" \
  --start "https://proaktiv.no/eiendomsmegler/drammen-lier" \
  --start "https://proaktiv.no/eiendomsmegler/lillestrom" \
  --start "https://proaktiv.no/eiendomsmegler/lorenskog" \
  --start "https://proaktiv.no/eiendomsmegler/bergen" \
  --start "https://proaktiv.no/eiendomsmegler/voss" \
  --start "https://proaktiv.no/eiendomsmegler/stavanger" \
  --start "https://proaktiv.no/eiendomsmegler/sandnes" \
  --start "https://proaktiv.no/eiendomsmegler/sola" \
  --start "https://proaktiv.no/eiendomsmegler/trondheim" \
  --start "https://proaktiv.no/eiendomsmegler/alesund" \
  --start "https://proaktiv.no/eiendomsmegler/skien" \
  --start "https://proaktiv.no/eiendomsmegler/haugesund" \
  --start "https://proaktiv.no/eiendomsmegler/sarpsborg" \
  --start "https://proaktiv.no/eiendomsmegler/kristiansand" \
  --start "https://proaktiv.no/om-oss/kjedeledelse" \
  --deep-employees \
  --overwrite
```

### Key Flags
- `--overwrite`: **Critical** - Updates existing records instead of skipping them
- `--deep-employees`: Scrapes individual employee profile pages for detailed info
- `--delay-ms 1500`: Rate limiting to respect server resources

## What Gets Updated

### For Offices
```python
# Fields updated with --overwrite flag:
{
  "profile_image_url": "https://proaktiv.no/...",  # Banner/hero image
  "description": "Office presentation text...",
  "facebook_url": "https://facebook.com/...",
  "instagram_url": "https://instagram.com/...",
  "linkedin_url": "https://linkedin.com/...",
  "email": "office@proaktiv.no",
  "phone": "+47 123 45 678",
  # ... other fields
}
```

### For Employees
```python
# Fields updated with --overwrite flag:
{
  "profile_image_url": "https://proaktiv.no/...",  # Headshot
  "description": "Employee bio and presentation...",
  "linkedin_url": "https://linkedin.com/in/...",
  "homepage_profile_url": "https://proaktiv.no/eiendomsmegler/.../...",
  "title": "Eiendomsmegler MNEF",
  "phone": "+47 987 65 432",
  # ... other fields
}
```

## Scraper Behavior with --overwrite

### Matching Logic
1. **Offices**: Match by `homepage_url` → `name` → `short_code`
2. **Employees**: Match by `email` (unique identifier)

### Update Strategy
```python
if record_exists:
    if --overwrite:
        UPDATE record SET field1=new_value, field2=new_value, updated_at=NOW()
    else:
        SKIP (keep existing data)
else:
    INSERT new record
```

### What Gets Preserved
- `id` (UUID primary key)
- `created_at` timestamp
- `vitec_department_id` / `vitec_employee_id` (if set)
- Custom fields not scraped from homepage

### What Gets Updated
- All scraped fields (images, descriptions, URLs, contact info)
- `updated_at` timestamp (set to NOW())

## Expected Results

### Before Rescrape
```sql
-- Check current state
SELECT 
  COUNT(*) as total,
  COUNT(profile_image_url) as with_images,
  COUNT(description) as with_descriptions
FROM offices;

-- Example: 15 offices, 3 with images, 5 with descriptions
```

### After Rescrape
```sql
-- Expected state
SELECT 
  COUNT(*) as total,
  COUNT(profile_image_url) as with_images,
  COUNT(description) as with_descriptions
FROM offices;

-- Expected: 15 offices, 15 with images, 15 with descriptions
```

## Monitoring Progress

### Check Scraper Logs
The scraper outputs SQL queries showing updates:
```
UPDATE offices SET profile_image_url=$1, description=$2, updated_at=now() WHERE id = $3
UPDATE employees SET profile_image_url=$1, description=$2, updated_at=now() WHERE id = $3
```

### Verify Results
```sql
-- Offices with banner images
SELECT name, city, profile_image_url 
FROM offices 
WHERE profile_image_url IS NOT NULL
ORDER BY updated_at DESC;

-- Employees with profile pictures
SELECT first_name, last_name, email, profile_image_url 
FROM employees 
WHERE profile_image_url IS NOT NULL
ORDER BY updated_at DESC;

-- Recently updated records
SELECT name, updated_at 
FROM offices 
WHERE updated_at > NOW() - INTERVAL '1 hour'
ORDER BY updated_at DESC;
```

## Safety Features

### Rate Limiting
- 1.5 second delay between requests
- Prevents server overload
- Respects robots.txt

### Bounded Execution
- Max 220 pages total
- Max 40-minute runtime
- Graceful shutdown on timeout

### Data Integrity
- Transactional updates (all-or-nothing)
- Preserves existing data if scrape fails
- Logs all operations for audit trail

## Timeline

### Estimated Duration
- **16 office pages** × 1.5s = ~24 seconds
- **~100-200 employee pages** × 1.5s = ~2.5-5 minutes
- **Total**: ~5-10 minutes (with overhead)

### Progress Indicators
1. **Phase 1** (0-2 min): Scraping office pages
2. **Phase 2** (2-8 min): Scraping employee profile pages
3. **Phase 3** (8-10 min): Final database commits and cleanup

## Post-Scrape Verification

### Frontend Checks
1. Visit https://blissful-quietude-production.up.railway.app/offices
2. Verify office cards show banner images
3. Click into office detail pages
4. Verify employee avatars display profile pictures
5. Check that descriptions render correctly

### Database Checks
```sql
-- Count records with images
SELECT 
  'Offices' as entity,
  COUNT(*) as total,
  COUNT(profile_image_url) as with_images,
  ROUND(100.0 * COUNT(profile_image_url) / COUNT(*), 1) as percentage
FROM offices
UNION ALL
SELECT 
  'Employees' as entity,
  COUNT(*) as total,
  COUNT(profile_image_url) as with_images,
  ROUND(100.0 * COUNT(profile_image_url) / COUNT(*), 1) as percentage
FROM employees;
```

### Expected Output
```
entity      | total | with_images | percentage
------------|-------|-------------|------------
Offices     |    15 |          15 |      100.0
Employees   |   150 |         145 |       96.7
```

## Troubleshooting

### If Images Are Still Missing
1. **Check image URLs**: Some pages may not have banner images
2. **Verify HTML structure**: proaktiv.no may have changed their layout
3. **Check scraper logs**: Look for parsing errors or 404s
4. **Manual verification**: Visit the homepage and confirm image exists

### If Scraper Fails
1. **Check database connection**: Verify Railway DB URL is correct
2. **Check rate limiting**: May have hit server limits (wait and retry)
3. **Check logs**: Look for Python exceptions or network errors

## Next Steps

1. ✅ **Wait for scraper to complete** (~10 minutes)
2. ✅ **Verify images in database** (SQL queries above)
3. ✅ **Test frontend display** (visit office/employee pages)
4. ✅ **Document any missing images** (for manual follow-up)

## Related Documentation
- **Scraper Documentation**: `docs/proaktiv-directory-sync.md`
- **Initial Scraping Session**: `docs/scraping-session-2026-01-20.md`
- **Command Reference**: `.cursor/commands/scrape-proaktiv.md`
