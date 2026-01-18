# Leverandører (Suppliers) - Task Breakdown

## Overview
Supplier contact management with issue tracking for connected partners.

## Tasks

### Backend
- [ ] **B1**: Create `Supplier` model (name, category, is_connected, contact_info)
- [ ] **B2**: Create `SupplierIssue` model (title, status, dates, notes)
- [ ] **B3**: Create `GET/POST /api/suppliers` endpoints
- [ ] **B4**: Create `GET/POST /api/suppliers/{id}/issues` endpoints
- [ ] **B5**: Add metrics endpoint (resolution time, issue counts)

### Frontend
- [ ] **F1**: Create `/suppliers` page with Connected/Available tabs
- [ ] **F2**: Create SupplierCard component (contact card style)
- [ ] **F3**: Create IssueTracker component
- [ ] **F4**: Create issue logging form
- [ ] **F5**: Create metrics dashboard (open issues, avg resolution)

### Data
- [ ] **D1**: Seed ~15-20 connected suppliers
- [ ] **D2**: Seed ~105-110 available suppliers

## Supplier Categories
- Megling services
- Insurance
- Marketing
- Property data
- Legal services

## Issue Statuses
- `open` - New issue
- `in_progress` - Being worked on
- `resolved` - Completed
