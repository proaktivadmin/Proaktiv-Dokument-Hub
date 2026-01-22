# SalesScreen API Research

**Created:** 2026-01-22
**Status:** Research Complete

---

## Overview

SalesScreen is a sales performance and gamification platform that helps teams track KPIs, run competitions, and celebrate achievements. Proaktiv already has offices using SalesScreen, but the user management is done manually.

**Goal:** Push employee data (name, title, phone, photo) from our app to SalesScreen for offices that have an active agreement.

---

## Existing Vitec Integration

SalesScreen already has a **native Vitec integration** ([source](https://salesscreen.dev/integrations/vitec)):

> "Vitec supports the broker's everyday life, from tips and leads through the entire deal to follow-up of buyers and sellers after the deal is closed. Our real-time integration lets you synchronize Vitec activities within SalesScreen."

**Features:**
- Gamify Vitec activities (estates, meetings, tips)
- Easy-to-read dashboards for goal tracking
- Competitions and achievements
- Real-time sync

**Note:** This integration syncs *activities* from Vitec, not user/employee profiles. Our integration will complement this by syncing employee profile data.

---

## API Capabilities

Based on [SalesScreen's developer portal](https://salesscreen.dev/integrations/):

### Available Features
- Full REST API for custom integrations
- OpenAPI/Swagger specifications
- Webhooks and webhook management
- OAuth authentication
- Sandbox environment for testing
- Postman/Insomnia collections
- Zapier integration (1,500+ apps)

### API Reference
- **Documentation:** https://docs.salesscreen.com/
- **Base endpoint:** Not publicly documented (requires API access)
- **Authentication:** OAuth / API tokens

---

## Integration Strategy

### Option 1: Direct API Integration (Preferred)
Contact SalesScreen to get:
1. API credentials (client ID, client secret)
2. Access to sandbox environment
3. Documentation for user management endpoints

**Expected endpoints (based on standard patterns):**
```
POST   /api/users          - Create user
GET    /api/users/{id}     - Get user
PUT    /api/users/{id}     - Update user
DELETE /api/users/{id}     - Delete/deactivate user
POST   /api/users/{id}/photo - Upload user photo
```

### Option 2: Zapier Integration (Fallback)
If direct API access is limited:
- Use Zapier to connect our app to SalesScreen
- Trigger on employee updates in our database
- Map fields to SalesScreen user properties

### Option 3: Manual CSV/Bulk Import
If API doesn't support user provisioning:
- Generate CSV export from our app
- Admin imports manually in SalesScreen

---

## Data Mapping

| Our Database | SalesScreen (Expected) |
|--------------|----------------------|
| `first_name` | `firstName` |
| `last_name` | `lastName` |
| `email` | `email` (unique key) |
| `title` | `title` or `jobTitle` |
| `phone` | `phone` or `mobilePhone` |
| `profile_image_url` | User photo (upload) |
| `office.name` | `team` or `department` |

---

## Office-Level Control

### New Field: `salesscreen_enabled`

Add to Office model:
```python
# SalesScreen Integration
salesscreen_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
salesscreen_team_id: Mapped[str | None] = mapped_column(String(100), nullable=True)
```

Only sync employees from offices where `salesscreen_enabled = True`.

---

## Sync Flow

### From Our App to SalesScreen

```
1. User clicks "Sync to SalesScreen" on employee
2. Check if employee's office has salesscreen_enabled = True
3. If not, show error: "This office doesn't have SalesScreen"
4. If yes, call SalesScreen API to update/create user
5. If photo changed, upload new photo
6. Log result and show success/error
```

### Onboarding Flow

When onboarding a new employee:
1. Create employee in our database
2. If office has SalesScreen enabled:
   - Auto-push to SalesScreen after basic info is saved
   - Or add to onboarding checklist: "Push to SalesScreen"

---

## Required Actions

### Before Implementation

1. **Contact SalesScreen** - Request API documentation and credentials
   - Email: support@salesscreen.com or through customer portal
   - Request: API access, sandbox environment, user management docs

2. **Identify Offices** - Which offices have active SalesScreen agreements?
   - Add `salesscreen_enabled` flag to those offices
   - Get team IDs from SalesScreen admin

3. **Get API Credentials** - Store securely
   - `SALESSCREEN_API_URL`
   - `SALESSCREEN_CLIENT_ID`
   - `SALESSCREEN_CLIENT_SECRET`
   - Or API token if using bearer auth

---

## Implementation Plan

### Phase 1: Backend API (06-13, 06-14)
- Add `salesscreen_enabled` and `salesscreen_team_id` to Office model
- Create SalesScreen service with mock API client
- Create endpoints for sync preview and execution

### Phase 2: Frontend UI (06-15)
- Add SalesScreen toggle to office settings
- Add "Sync to SalesScreen" action on employee cards
- Add to onboarding flow

### Phase 3: Live Integration (After API access)
- Implement actual SalesScreen API calls
- Test with sandbox
- Deploy to production

---

## Security Considerations

1. **Store credentials in environment variables** (never in code)
2. **Log all API calls** for audit trail
3. **Rate limit** to avoid being blocked
4. **Handle failures gracefully** - don't block other operations
5. **Validate office permission** before every sync

---

## Questions for SalesScreen

When contacting SalesScreen, ask:

1. Does the API support user provisioning (create/update users)?
2. What authentication method is used (OAuth2, API key, bearer token)?
3. Is there a sandbox environment for testing?
4. What are the rate limits?
5. Can we upload user photos via API?
6. How do we map users to teams/departments?
7. Is there a webhook for user changes (for 2-way sync)?

---

## References

- [SalesScreen Integrations](https://salesscreen.dev/integrations/)
- [SalesScreen + Vitec](https://salesscreen.dev/integrations/vitec)
- [SalesScreen Help Center](https://help.salesscreen.com/)
- [SalesScreen API Tracker](https://apitracker.io/a/salesscreen)
