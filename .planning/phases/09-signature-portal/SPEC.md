# Signature Portal - Technical Specification

**Phase:** 09 - Self-Service Email Signature Portal  
**Status:** Ready for Implementation  
**Created:** 2026-01-24  

---

## Overview

A self-service email signature system for 120+ employees. Admins preview and send personalized signature links from the dashboard. Employees visit their personal page to copy and paste the signature into their email client.

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        ADMIN DASHBOARD                               │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │  Employee Detail Page (/employees/{id})                      │    │
│  │  ┌─────────────────────────────────────────────────────┐    │    │
│  │  │  New "Signatur" Tab                                  │    │    │
│  │  │  - Preview signature (with-photo / no-photo)         │    │    │
│  │  │  - "Send signatur til ansatt" button                 │    │    │
│  │  └─────────────────────────────────────────────────────┘    │    │
│  └─────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────┘
                                   │
                                   │ POST /api/signatures/{id}/send
                                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│                        RAILWAY BACKEND                               │
│  ┌──────────────────────┐  ┌──────────────────────┐                 │
│  │  signature_service   │  │  graph_service       │                 │
│  │  - render_signature  │  │  - get_access_token  │                 │
│  │  - load templates    │  │  - send_mail         │                 │
│  └──────────────────────┘  └──────────────────────┘                 │
│                                   │                                  │
│  GET /api/signatures/{id}         │ Microsoft Graph API              │
│  POST /api/signatures/{id}/send   │ (Mail.Send permission)           │
└─────────────────────────────────────────────────────────────────────┘
                                   │
                                   │ Email with personal link
                                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│                           EMPLOYEE                                   │
│  1. Receives email with link                                         │
│  2. Clicks link → Public signature page                              │
│  3. Selects version (with/without photo)                             │
│  4. Clicks "Kopier signatur"                                         │
│  5. Pastes into email client                                         │
└─────────────────────────────────────────────────────────────────────┘
                                   │
                                   │ GET /api/signatures/{id}
                                   ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     PUBLIC SIGNATURE PAGE                            │
│  URL: /signature/{employee-uuid}                                     │
│  ┌─────────────────────────────────────────────────────────────┐    │
│  │  [Proaktiv Logo]                                             │    │
│  │  Din e-postsignatur, {Name}                                  │    │
│  │                                                              │    │
│  │  [Med bilde] [Uten bilde]  ← tabs                            │    │
│  │  ┌────────────────────────────────────────────┐              │    │
│  │  │         Signature Preview                   │              │    │
│  │  └────────────────────────────────────────────┘              │    │
│  │  [ Kopier signatur ]                                         │    │
│  │  ▸ Slik legger du inn signaturen                             │    │
│  └─────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────┘
```

---

## API Endpoints

### GET /api/signatures/{employee_id}

Renders a personalized email signature for an employee.

**Query Parameters:**
- `version`: `with-photo` (default) or `no-photo`

**Response:**
```json
{
  "html": "<table>...</table>",
  "text": "Med vennlig hilsen\nJohn Doe\n...",
  "employee_name": "John Doe",
  "employee_email": "john.doe@proaktiv.no"
}
```

**Authentication:** None (public endpoint, UUID provides security)

---

### POST /api/signatures/{employee_id}/send

Sends a signature notification email to the employee.

**Request Body (optional):**
```json
{
  "sender_email": "it@proaktiv.no"
}
```

**Response:**
```json
{
  "success": true,
  "sent_to": "john.doe@proaktiv.no",
  "message": "Signature email sent successfully"
}
```

**Authentication:** Required (dashboard session)

---

## Template Placeholders

The HTML signature template uses these placeholders:

| Placeholder | Source |
|-------------|--------|
| `{{DisplayName}}` | `employee.full_name` |
| `{{JobTitle}}` | `employee.title` or empty |
| `{{MobilePhone}}` | `employee.phone` or empty |
| `{{Email}}` | `employee.email` |
| `{{OfficeName}}` | `employee.office.name` |
| `{{OfficeAddress}}` | `employee.office.street_address` |
| `{{OfficePostal}}` | `f"{office.postal_code} {office.city}"` |

---

## Files to Create

### Backend

| File | Purpose |
|------|---------|
| `backend/app/services/signature_service.py` | Signature rendering logic |
| `backend/app/services/graph_service.py` | Microsoft Graph API client |
| `backend/app/routers/signatures.py` | API endpoints |
| `backend/scripts/templates/email-signature-no-photo.html` | No-photo variant |
| `backend/scripts/templates/signature-notification-email.html` | Email template |

### Frontend

| File | Purpose |
|------|---------|
| `frontend/src/hooks/v3/useSignature.ts` | API hooks |
| `frontend/src/components/employees/SignaturePreview.tsx` | Admin preview component |
| `frontend/src/app/signature/[id]/page.tsx` | Public self-service page |

### Scripts

| File | Purpose |
|------|---------|
| `backend/scripts/Send-SignatureEmails.ps1` | Bulk email sender |
| `run-signature-emails.bat` | Launcher script |

---

## Files to Modify

| File | Change |
|------|--------|
| `backend/app/main.py` | Register signatures router |
| `frontend/src/app/employees/[id]/page.tsx` | Add Signatur tab |
| `frontend/src/components/employees/index.ts` | Export SignaturePreview |
| `frontend/src/hooks/v3/index.ts` | Export signature hooks |

---

## Environment Variables

Add to `backend/.env`:

```
SIGNATURE_SENDER_EMAIL=it@proaktiv.no
FRONTEND_URL=https://proaktiv-dokument-hub.vercel.app
```

Existing variables used:
- `ENTRA_TENANT_ID`
- `ENTRA_CLIENT_ID`
- `ENTRA_CLIENT_SECRET`

---

## Azure Permission Required

Add to Entra app `PROAKTIV-Entra-Sync`:

- **Microsoft Graph** → **Application permissions** → **Mail.Send**
- Grant admin consent

---

## Existing Resources to Reference

### Backend Patterns
- `backend/app/services/employee_service.py` - Service pattern
- `backend/app/routers/employees.py` - Router pattern
- `backend/scripts/Sync-EntraIdEmployees.ps1` - Graph auth pattern

### Frontend Patterns
- `frontend/src/app/employees/[id]/page.tsx` - Page structure, tabs
- `frontend/src/hooks/v3/useEmployees.ts` - Hook pattern
- `frontend/src/components/employees/` - Component patterns

### Templates
- `backend/scripts/templates/email-signature.html` - Base signature template

### Design System
- `.planning/codebase/DESIGN-SYSTEM.md` - UI tokens and patterns

---

## Agent Assignment

| Agent | Scope | Dependencies |
|-------|-------|--------------|
| 1 | Backend signature service + router | None |
| 2 | Backend graph service + send endpoint | Agent 1 |
| 3 | Frontend hooks + SignaturePreview component | Agent 1, 2 |
| 4 | Employee page tab integration | Agent 3 |
| 5 | Public signature page | Agent 1, 3 |
| 6 | PowerShell bulk sender | Agent 1, 2 |

---

## Success Criteria

1. Admin can preview signature on employee page
2. Admin can send signature email with one click
3. Employee receives email with personal link
4. Employee can copy signature in two versions
5. Signature renders correctly in Outlook, Gmail, Apple Mail
6. Bulk send works for 120+ employees

---

## Out of Scope

- Automatic signature injection (requires Outlook add-in)
- Tracking signature adoption
- Multiple signature templates per employee
- Mobile app signature setup
