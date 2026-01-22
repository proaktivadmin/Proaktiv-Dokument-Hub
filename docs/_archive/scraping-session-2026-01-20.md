# Proaktiv Directory Scraping Session - 2026-01-20

## Overview
Ran the Proaktiv directory scraper targeting the **Railway production database** to complete the seeding of offices and employees from proaktiv.no.

## Execution Details

### Command
```powershell
$env:RAILWAY_DATABASE_URL = "postgresql://postgres:***@shuttle.proxy.rlwy.net:51557/railway"
.\backend\scripts\run_proaktiv_directory_sync.ps1 -TargetDb railway -Preset all -DeepEmployees $true -Overwrite
```

### Target URLs (Preset: "all")
The scraper processed the following office pages:
- https://proaktiv.no/eiendomsmegler/oslo
- https://proaktiv.no/eiendomsmegler/drammen-lier
- https://proaktiv.no/eiendomsmegler/lillestrom
- https://proaktiv.no/eiendomsmegler/lorenskog
- https://proaktiv.no/eiendomsmegler/bergen
- https://proaktiv.no/eiendomsmegler/voss
- https://proaktiv.no/eiendomsmegler/stavanger
- https://proaktiv.no/eiendomsmegler/sandnes
- https://proaktiv.no/eiendomsmegler/sola
- https://proaktiv.no/eiendomsmegler/trondheim
- https://proaktiv.no/eiendomsmegler/alesund
- https://proaktiv.no/eiendomsmegler/skien
- https://proaktiv.no/eiendomsmegler/haugesund
- https://proaktiv.no/eiendomsmegler/sarpsborg
- https://proaktiv.no/eiendomsmegler/kristiansand
- https://proaktiv.no/om-oss/kjedeledelse (corporate directory)

### Configuration
- **Target Database**: Railway PostgreSQL (production)
- **Delay**: 1500ms between requests (rate limiting)
- **Max Pages**: 220 total
- **Max Office Pages**: 24
- **Max Employee Pages**: 220
- **Max Runtime**: 40 minutes
- **Deep Employees**: Yes (scrape individual employee profile pages)
- **Overwrite**: Yes (update existing records)

## Data Scraped

### Office Data
For each office location, the scraper extracts:
- **Basic Info**: name, short_code, email, phone, address, postal_code, city
- **URLs**: homepage_url, facebook_url, instagram_url, linkedin_url
- **Images**: profile_image_url (banner/hero image)
- **Content**: description (office presentation text)
- **Metadata**: color (for UI theming)

### Employee Data
For each employee (broker), the scraper extracts:
- **Basic Info**: first_name, last_name, title, email, phone
- **URLs**: homepage_profile_url, linkedin_url
- **Images**: profile_image_url (headshot)
- **Content**: description (employee bio/presentation)
- **Relationships**: office_id (which office they belong to)
- **Roles**: system_roles (derived from title)
- **Status**: status (active/onboarding based on presence)

## Observed Results

### New Offices Created
- ✅ **Kjedeledelse** (Corporate leadership team)
  - Address: Småstrandgaten 6, 5014 Bergen
  - Email: post@proaktiv.no
  - Phone: 55 36 40 71
  - Homepage: https://proaktiv.no/om-oss/kjedeledelse

### Employees Updated
- ✅ Multiple employees successfully linked to their offices
- ✅ Employee profile URLs captured (e.g., Malin Aanerud Eriksen)
- ✅ Office associations updated for existing employees

### Database Operations
The scraper performed:
1. **Upsert operations** - Insert new records or update existing ones
2. **Office matching** - By `homepage_url`, then `name`, then `short_code`
3. **Employee matching** - By `email` (primary key for deduplication)
4. **Relationship updates** - Linking employees to correct offices

## Safety Features

### Rate Limiting
- 1.5 second delay between requests
- Respects robots.txt and server load

### Bounded Execution
- Maximum 220 pages total
- Maximum 40-minute runtime
- Automatic timeout and graceful shutdown

### Data Integrity
- Upsert logic prevents duplicates
- Existing data preserved unless `--overwrite` flag used
- Transaction-based database operations

## Technical Details

### Database Connection
- Connected to Railway PostgreSQL via public URL
- SSL connection with asyncpg driver
- Connection pooling for performance

### Scraping Method
- Direct HTTP requests with `httpx` (no Firecrawl API)
- HTML parsing with `BeautifulSoup4`
- Async/await for concurrent operations

### Data Flow
```
proaktiv.no → HTTP GET → HTML Parser → Data Extractor → Database Upsert
```

## Next Steps

### Verify Results
1. Check Railway database for new offices and employees
2. Verify profile images and descriptions are populated
3. Confirm office-employee relationships are correct

### Frontend Display
1. Office cards should now show banner images
2. Employee avatars should display profile pictures
3. Descriptions should appear on detail pages

### Territory Map (Next Feature)
1. Add geocoding for office addresses
2. Plot offices on Norway map
3. Display territory assignments

## Monitoring

### Check Scraper Status
The scraper logs to stdout with SQLAlchemy query logging enabled. Monitor for:
- `INSERT INTO offices` - New offices created
- `UPDATE employees` - Existing employees updated
- `SELECT ... WHERE email =` - Employee deduplication checks

### Database Verification
```sql
-- Count offices
SELECT COUNT(*) FROM offices;

-- Count employees
SELECT COUNT(*) FROM employees;

-- Check new offices
SELECT name, city, homepage_url 
FROM offices 
ORDER BY created_at DESC 
LIMIT 10;

-- Check employees with profiles
SELECT first_name, last_name, email, profile_image_url 
FROM employees 
WHERE profile_image_url IS NOT NULL 
ORDER BY updated_at DESC 
LIMIT 20;
```

## Notes

- The scraper ran for approximately 10+ minutes before timeout
- Multiple offices and employees were successfully processed
- The scraper will continue running until completion (max 40 minutes)
- All data written directly to Railway production database
- No local database involved in this session

## Resources

- **Scraper Documentation**: `docs/proaktiv-directory-sync.md`
- **Command Reference**: `.cursor/commands/scrape-proaktiv.md`
- **PowerShell Script**: `backend/scripts/run_proaktiv_directory_sync.ps1`
- **Python Module**: `backend/scripts/sync_proaktiv_directory.py`
