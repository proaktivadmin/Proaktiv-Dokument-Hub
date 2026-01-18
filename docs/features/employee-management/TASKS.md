# Employee Management - Task Breakdown

## Overview
Role-based user management with Microsoft Teams integration and email group functionality.

## Tasks

### Backend
- [x] **B1**: Add `system_roles` field to Employee model (Array of strings)

- [x] **B2**: Add `teams_group_id` and `sharepoint_folder_url` to Employee/Office

- [x] **B3**: Create `GET /api/employees` with role & office filtering

- [x] **B4**: Create Microsoft Graph client for Teams groups

- [x] **B5**: Add endpoint for email group generation


### Frontend  
- [x] **F1**: Create role filter sidebar component

- [ ] **F2**: Update EmployeeList to use new filters
- [ ] **F3**: Create "Email Group" action button (mailto generator)
- [ ] **F4**: Add Teams group display in employee cards

### Testing
- [ ] **T1**: Test role filtering with sample data
- [ ] **T2**: Verify email mailto links work correctly

## Vitec Next Roles
- `eiendomsmegler` - Real estate agent
- `eiendomsmeglerfullmektig` - Associate agent
- `daglig leder` - Managing director
- `superbruker` - Super user
- `oppgjør` - Settlement

## Dependencies
- Existing Employee model (V3.0)
- Microsoft Graph API credentials
