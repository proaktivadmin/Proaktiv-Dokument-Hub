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
- Updates fields: `name`, `email`, `phone`, `street_address`, `postal_code`, `city`, `description`, `profile_image_url`, social links
- Returns updated office data
- Response: `200 OK` with updated `OfficeWithStats`
- Error: `404` if office not found, `400` if no `homepage_url` set

#### `POST /api/employees/{id}/scrape`
- Scrapes the employee's `homepage_profile_url`
- Updates fields: `first_name`, `last_name`, `title`, `email`, `phone`, `profile_image_url`, `description`
- Returns updated employee data
- Response: `200 OK` with updated `EmployeeWithOffice`
- Error: `404` if employee not found, `400` if no `homepage_profile_url` set

## Implementation Notes

### Backend Service
- Create `backend/app/services/single_scrape_service.py`
- Reuse parsing logic from `sync_proaktiv_directory.py`
- Extract single-page scraping functions:
  - `scrape_office_page(url: str) -> dict`
  - `scrape_employee_page(url: str) -> dict`
- Use direct HTTP fetch (no Firecrawl needed for single pages)
- Add 1-second delay before scraping to be polite
- Handle errors gracefully (network issues, parsing failures)

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
- [ ] Success toast shows "Data oppdatert fra hjemmeside"
- [ ] Error toast shows helpful message if scraping fails
- [ ] Rate limiting prevents abuse (1 scrape/minute per resource)
- [ ] Scraping works for both local and Railway databases
