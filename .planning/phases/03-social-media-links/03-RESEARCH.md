# Phase 3: Social Media Links - Research

**Researched:** 2026-01-20
**Domain:** Social Media Profile Links & Featured Brokers
**Confidence:** HIGH

## Summary

Phase 3 adds social media URLs to employee profiles and implements a "featured broker" display on office pages. Most infrastructure already exists - offices have full social media support, employees only have LinkedIn.

**Primary recommendation:** Extend Employee model with missing social fields, add featured_on_homepage flag, and build Featured Brokers UI section.

## Current State Analysis

### Already Implemented

**Office Model** (complete):
- `facebook_url` - DB field, form field, detail display
- `instagram_url` - DB field, form field (detail display MISSING)
- `linkedin_url` - DB field, form field, detail display
- `google_my_business_url` - DB field, form field, detail display

**Employee Model** (partial):
- `linkedin_url` - DB field, form field, detail display
- Missing: facebook_url, instagram_url, twitter_url

### Missing Features

1. **Employee social fields**: Add facebook_url, instagram_url to Employee model
2. **Office Instagram display**: Add Instagram icon to office detail page
3. **Featured broker flag**: Add is_featured_broker boolean to Employee
4. **Featured brokers section**: Display featured employees on office page

## Data Model Changes

### Employee Model Additions

```python
# backend/app/models/employee.py - ADD THESE FIELDS
facebook_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
instagram_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
twitter_url: Mapped[Optional[str]] = mapped_column(Text, nullable=True)  # X/Twitter
is_featured_broker: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
```

### Migration Required

```python
# Add to employees table
op.add_column("employees", sa.Column("facebook_url", sa.Text(), nullable=True))
op.add_column("employees", sa.Column("instagram_url", sa.Text(), nullable=True))
op.add_column("employees", sa.Column("twitter_url", sa.Text(), nullable=True))
op.add_column("employees", sa.Column("is_featured_broker", sa.Boolean(), nullable=False, server_default="false"))
```

## UI Components

### Existing Components to Modify

1. **EmployeeForm.tsx** - Add social URL input fields
2. **Employee detail page** - Add social icons display
3. **Office detail page** - Add Instagram icon (currently missing)

### New Components to Create

1. **FeaturedBrokers.tsx** - Grid of featured broker cards
2. **SocialLinksDisplay.tsx** - Reusable social icons component

### Social Icons Mapping

```typescript
const SOCIAL_PLATFORMS = {
  facebook: { icon: Facebook, label: "Facebook", color: "#1877F2" },
  instagram: { icon: Instagram, label: "Instagram", color: "#E4405F" },
  linkedin: { icon: Linkedin, label: "LinkedIn", color: "#0A66C2" },
  twitter: { icon: Twitter, label: "X/Twitter", color: "#000000" },
  google: { icon: MapPin, label: "Google Business", color: "#4285F4" },
};
```

## API Changes

### Employee Schema Updates

```python
# backend/app/schemas/employee.py
class EmployeeBase(BaseModel):
    # ... existing fields ...
    facebook_url: Optional[str] = Field(None, description="Facebook profile URL")
    instagram_url: Optional[str] = Field(None, description="Instagram profile URL")
    twitter_url: Optional[str] = Field(None, description="X/Twitter profile URL")
    is_featured_broker: bool = Field(False, description="Display on office featured section")
```

### New Endpoint (Optional)

```
GET /api/offices/{id}/featured-brokers -> List[EmployeeWithOffice]
```

Or use existing employee list with filter: `GET /api/employees?office_id={id}&is_featured=true`

## Plan Breakdown

| Plan | Focus | Scope |
|------|-------|-------|
| 03-01 | Database Schema | Add employee social fields + featured flag, migration |
| 03-02 | Backend Updates | Update schemas, services, ensure router handles new fields |
| 03-03 | Employee UI | Form fields, detail page social display |
| 03-04 | Featured Brokers | Featured flag toggle, office page section |

## Simplified Scope

Since offices already have full social support, Phase 3 is smaller than originally estimated:

**Must Have:**
- Employee social fields (FB, IG, Twitter)
- Featured broker flag
- Featured brokers section on office page

**Nice to Have:**
- Reusable SocialLinksDisplay component
- Social link validation (URL format)

## Sources

- `backend/app/models/employee.py` - Current employee model
- `backend/app/models/office.py` - Office model (reference for social fields)
- `frontend/src/components/offices/OfficeForm.tsx` - Office social form pattern
- `frontend/src/app/offices/[id]/page.tsx` - Office detail social display

## Metadata

**Confidence breakdown:**
- Schema: HIGH - Simple field additions following existing patterns
- UI: HIGH - Copying existing office patterns
- Featured Brokers: MEDIUM - New component but straightforward

**Research date:** 2026-01-20
**Valid until:** 90 days (stable, low complexity)
