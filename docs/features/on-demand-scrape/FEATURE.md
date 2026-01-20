# On-Demand Homepage Scrape Feature

## Overview
Add a scrape button to office and employee detail pages that allows users to refresh data from the linked homepage with a single click.

## User Story
As an admin, I want to click a button on an office or employee profile page to scrape and update their information from their homepage, so I can keep data fresh without running the full scraper.

## UI Placement

### Office Detail Page
- Add a "Oppdater fra hjemmeside" (Update from Homepage) button next to the "Rediger" button
- Only show if `homepage_url` is present
- Icon: `RefreshCw` from lucide-react
- Variant: `outline`

### Employee Detail Page
- Add a "Oppdater fra profil" (Update from Profile) button next to the "Rediger" button
- Only show if `homepage_profile_url` is present
- Icon: `RefreshCw` from lucide-react
- Variant: `outline`

## Backend API

### New Endpoints

#### `POST /api/offices/{id}/scrape`
- Scrapes the office's `homepage_url`
- Updates fields: 
  - Basic info: `name`, `email`, `phone`, `street_address`, `postal_code`, `city`
  - **Banner image**: `profile_image_url` (office homepage banner/hero image)
  - Description: `description` (office presentation text)
  - Social links: `facebook_url`, `instagram_url`, `linkedin_url`, `google_my_business_url`
- Returns updated office data
- Response: `200 OK` with updated `OfficeWithStats`
- Error: `404` if office not found, `400` if no `homepage_url` set

#### `POST /api/employees/{id}/scrape`
- Scrapes the employee's `homepage_profile_url`
- Updates fields:
  - Basic info: `first_name`, `last_name`, `title`, `email`, `phone`
  - **Profile picture**: `profile_image_url` (employee photo from profile page)
  - **Presentation text**: `description` (employee bio/presentation from profile page)
  - Social: `linkedin_url` (if available on profile)
- Returns updated employee data
- Response: `200 OK` with updated `EmployeeWithOffice`
- Error: `404` if employee not found, `400` if no `homepage_profile_url` set

## Implementation Notes

### Backend Service
- Create `backend/app/services/single_scrape_service.py`
- Reuse parsing logic from `sync_proaktiv_directory.py`
- Extract single-page scraping functions:
  - `scrape_office_page(url: str) -> dict`
    - Parse office name, contact info, address
    - **Extract banner/hero image URL** (usually first large image or header background)
    - Extract office description/presentation text
    - Extract social media links
  - `scrape_employee_page(url: str) -> dict`
    - Parse employee name, title, contact info
    - **Extract profile picture URL** (usually `.employee-photo`, `.profile-image`, or similar)
    - **Extract presentation text** (bio, description, "Om meg" section)
    - Extract LinkedIn link if present
- Use direct HTTP fetch (no Firecrawl needed for single pages)
- Add 1-second delay before scraping to be polite
- Handle errors gracefully (network issues, parsing failures)
- Download and validate images before saving URLs

### Frontend Components
- Add scrape button to `frontend/src/app/offices/[id]/page.tsx`
- Add scrape button to `frontend/src/app/employees/[id]/page.tsx`
- Show loading state while scraping
- Show toast notification on success/failure
- Refetch data after successful scrape

### API Client
- Add `officesApi.scrape(id: string)` to `frontend/src/lib/api/offices.ts`
- Add `employeesApi.scrape(id: string)` to `frontend/src/lib/api/employees.ts`

## Safety Considerations
- Rate limiting: max 1 scrape per resource per minute (prevent abuse)
- Timeout: 10 seconds max per scrape request
- Error handling: graceful fallback if scraping fails
- No automatic scraping: only on explicit user action

## Future Enhancements
- Bulk scrape: select multiple offices/employees and scrape all
- Schedule: auto-scrape on a schedule (e.g., weekly)
- Diff view: show what changed before applying updates
- Selective update: choose which fields to update

## Files to Create/Modify

### Backend
- [ ] `backend/app/services/single_scrape_service.py` (new)
- [ ] `backend/app/routers/offices.py` (add scrape endpoint)
- [ ] `backend/app/routers/employees.py` (add scrape endpoint)

### Frontend
- [ ] `frontend/src/lib/api/offices.ts` (add scrape method)
- [ ] `frontend/src/lib/api/employees.ts` (add scrape method)
- [ ] `frontend/src/app/offices/[id]/page.tsx` (add scrape button)
- [ ] `frontend/src/app/employees/[id]/page.tsx` (add scrape button)

## Acceptance Criteria
- [ ] Scrape button appears on office detail page when `homepage_url` exists
- [ ] Scrape button appears on employee detail page when `homepage_profile_url` exists
- [ ] Clicking scrape button shows loading state
- [ ] Successful scrape updates the displayed data
- [ ] **Office banner image** is scraped and displayed after update
- [ ] **Employee profile picture** is scraped and displayed after update
- [ ] **Employee presentation text** is scraped and shown in description
- [ ] Office and employee cards already link to homepage/profile (verify existing functionality)
- [ ] Success toast shows "Data oppdatert fra hjemmeside"
- [ ] Error toast shows helpful message if scraping fails
- [ ] Rate limiting prevents abuse (1 scrape/minute per resource)
- [ ] Scraping works for both local and Railway databases

## Current Implementation Status
- ✅ Office cards already link to `homepage_url` (clickable)
- ✅ Employee cards already link to `homepage_profile_url` (clickable)
- ✅ Office `profile_image_url` field exists and displays as banner
- ✅ Employee `profile_image_url` field exists and displays as avatar
- ✅ Employee `description` field exists for presentation text
- ⏳ Scraping logic needs to extract images and presentation text
- ⏳ On-demand scrape endpoints need to be created
