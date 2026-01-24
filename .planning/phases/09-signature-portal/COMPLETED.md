# Phase 09: Self-Service Signature Portal

**Status:** ✅ Completed  
**Completed:** 2026-01-24  
**Commit:** `4241eb8`

---

## Summary

A self-service email signature system for 120+ employees. Admins preview and send personalized signature links from the dashboard. Employees visit their personal page to copy and paste the signature into their email client.

---

## Deliverables

### Backend

| File | Purpose |
|------|---------|
| `backend/app/services/signature_service.py` | Renders personalized HTML signatures |
| `backend/app/services/graph_service.py` | Microsoft Graph API client for sending emails |
| `backend/app/routers/signatures.py` | GET/POST API endpoints |
| `backend/scripts/templates/email-signature-no-photo.html` | No-photo signature variant |
| `backend/scripts/templates/signature-notification-email.html` | Email template for notifications |

### Frontend

| File | Purpose |
|------|---------|
| `frontend/src/hooks/v3/useSignature.ts` | API hooks for signature fetching/sending |
| `frontend/src/components/employees/SignaturePreview.tsx` | Admin preview component |
| `frontend/src/app/signature/[id]/page.tsx` | Public self-service page |

### Scripts

| File | Purpose |
|------|---------|
| `backend/scripts/Send-SignatureEmails.ps1` | Bulk email sender |
| `run-signature-emails.bat` | Launcher script |

---

## API Endpoints

### GET /api/signatures/{employee_id}

Returns personalized HTML signature.

- **Query:** `version=with-photo|no-photo`
- **Auth:** None (public, UUID provides security)
- **Response:** `{ html, text, employee_name, employee_email }`

### POST /api/signatures/{employee_id}/send

Sends signature notification email to employee.

- **Auth:** Required (dashboard session)
- **Response:** `{ success, sent_to, message }`

---

## Environment Variables

Required on Railway backend:

```
SIGNATURE_SENDER_EMAIL=froyland@proaktiv.no
FRONTEND_URL=https://proaktiv-dokument-hub.vercel.app
```

---

## Azure Permissions

Add to Entra app `PROAKTIV-Entra-Sync`:

- **Microsoft Graph** → **Application permissions** → **Mail.Send**
- Grant admin consent

---

## Usage

### Admin Dashboard

1. Navigate to employee detail page
2. Click "Signatur" tab
3. Preview signature (with-photo / no-photo)
4. Click "Send signatur" to email link to employee

### Employee Self-Service

1. Employee receives email with personal link
2. Clicks link → `/signature/{uuid}`
3. Selects version (med bilde / uten bilde)
4. Clicks "Kopier signatur"
5. Pastes into email client

### Bulk Rollout

```powershell
# Dry run (test without sending)
.\backend\scripts\Send-SignatureEmails.ps1 -DryRun

# Send to specific person (testing)
.\backend\scripts\Send-SignatureEmails.ps1 -FilterEmails "adrian@proaktiv.no"

# Send to all (production)
.\backend\scripts\Send-SignatureEmails.ps1
```

---

## Agent Pipeline

This feature was built using a 6-agent pipeline:

| Agent | Scope | Files |
|-------|-------|-------|
| 1 | Backend signature service + router | signature_service.py, signatures.py |
| 2 | Backend graph service + send endpoint | graph_service.py, notification template |
| 3 | Frontend hooks + SignaturePreview | useSignature.ts, SignaturePreview.tsx |
| 4 | Employee page tab integration | page.tsx modification |
| 5 | Public signature page | /signature/[id]/page.tsx |
| 6 | PowerShell bulk sender | Send-SignatureEmails.ps1 |

See `.planning/codebase/AGENT-PIPELINE.md` for reusable pipeline documentation.
