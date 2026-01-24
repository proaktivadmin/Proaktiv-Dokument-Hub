# Signature Portal - Agent Pipeline

## Overview

This document contains ready-to-use agent prompts for building the Self-Service Email Signature Portal. Execute agents in order, returning summaries to the orchestrator (main agent) for inspection before proceeding.

**Total Agents: 6**
**Estimated Time: 3-4 hours**

---

## Pre-Flight Checklist

Before starting, ensure:
- [ ] Backend is running locally or you have Railway access
- [ ] Frontend dev server can be started
- [ ] You have access to Azure portal for Entra permissions
- [ ] Plan file reviewed: `.cursor/plans/self-service_signature_portal_719e7726.plan.md`

---

## Agent 1: Backend Signature Service

### Command

```
/agent
```

### Prompt

```markdown
# TASK: Create Backend Signature Rendering Service

## CONTEXT
You are building a signature portal for Proaktiv Eiendomsmegling. This agent creates the backend service that renders personalized email signatures for employees.

## FILES TO READ FIRST (mandatory)
1. `backend/scripts/templates/email-signature.html` - Current HTML template
2. `backend/app/models/employee.py` - Employee model with all fields
3. `backend/app/models/office.py` - Office model with address fields
4. `backend/app/routers/employees.py` - Existing employee router pattern
5. `backend/app/services/employee_service.py` - Service pattern to follow

## DELIVERABLES

### 1. Create Signature Service
**File:** `backend/app/services/signature_service.py`

The service must:
- Have async method `render_signature(employee_id: UUID, version: str) -> SignatureResponse`
- Fetch employee with office relationship from database
- Read HTML template from `backend/scripts/templates/email-signature.html`
- Replace placeholders:
  - `{{DisplayName}}` → `employee.full_name`
  - `{{JobTitle}}` → `employee.title` (or empty string if None)
  - `{{MobilePhone}}` → `employee.phone` (or empty string if None)
  - `{{Email}}` → `employee.email`
  - `{{OfficeName}}` → `employee.office.name`
  - `{{OfficeAddress}}` → `employee.office.street_address`
  - `{{OfficePostal}}` → `f"{employee.office.postal_code} {employee.office.city}"`
- Generate plain text version by stripping HTML
- Return dataclass/TypedDict with: html, text, employee_name, employee_email

### 2. Create No-Photo Template
**File:** `backend/scripts/templates/email-signature-no-photo.html`

Copy existing template and remove the profile photo column (the `<td>` containing the profile image).

### 3. Create Signature Router
**File:** `backend/app/routers/signatures.py`

Endpoints:
```python
GET /api/signatures/{employee_id}?version=with-photo|no-photo
```

Response schema:
```python
class SignatureResponse(BaseModel):
    html: str
    text: str
    employee_name: str
    employee_email: str
```

### 4. Register Router
**File:** `backend/app/main.py`

Add the new router to the FastAPI app.

## RULES
- Follow existing code patterns in the codebase
- All services must be async
- Use Pydantic for response schemas
- Handle missing employee gracefully (404)
- Handle missing office gracefully (use fallback values)
- NO commits or pushes - just make the changes
- If anything is unclear, ASK before proceeding

## HANDOVER
When complete, provide a summary in this exact format:

---
**AGENT 1 COMPLETE**

Files created:
- [ ] `backend/app/services/signature_service.py`
- [ ] `backend/scripts/templates/email-signature-no-photo.html`
- [ ] `backend/app/routers/signatures.py`
- [ ] Modified `backend/app/main.py`

Endpoint ready: `GET /api/signatures/{employee_id}?version=with-photo|no-photo`

Issues encountered: (list any or "None")

Ready for Agent 2: (Yes/No)
---
```

---

## Agent 2: Backend Graph Email Service

### Command

```
/agent
```

### Prompt

```markdown
# TASK: Create Graph API Email Service for Signature Notifications

## CONTEXT
You are extending the signature portal backend. This agent creates a service to send personalized emails via Microsoft Graph API, plus an endpoint to trigger sending from the dashboard.

## FILES TO READ FIRST (mandatory)
1. `backend/.env` - Contains ENTRA_TENANT_ID, ENTRA_CLIENT_ID, ENTRA_CLIENT_SECRET
2. `backend/app/services/signature_service.py` - Just created by Agent 1
3. `backend/app/routers/signatures.py` - Just created by Agent 1
4. `backend/scripts/Sync-EntraIdEmployees.ps1` - Reference for Graph auth pattern

## DELIVERABLES

### 1. Create Graph Service
**File:** `backend/app/services/graph_service.py`

The service must:
- Have async method `get_access_token() -> str` using client credentials flow
- Have async method `send_mail(sender_email: str, recipient_email: str, subject: str, html_body: str) -> bool`
- Use httpx for async HTTP requests
- Read credentials from environment variables (use pydantic-settings or os.environ)
- Token endpoint: `https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token`
- Send mail endpoint: `https://graph.microsoft.com/v1.0/users/{sender}/sendMail`

### 2. Create Email Template
**File:** `backend/scripts/templates/signature-notification-email.html`

HTML email template with:
```html
<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"></head>
<body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
  <p>Hei {{FirstName}},</p>
  
  <p>Din personlige e-postsignatur er nå klar til bruk.</p>
  
  <p><strong>Klikk her for å hente signaturen din:</strong><br>
  <a href="{{SignatureUrl}}">{{SignatureUrl}}</a></p>
  
  <p>På siden finner du to versjoner:</p>
  <ul>
    <li>Med profilbilde</li>
    <li>Uten profilbilde</li>
  </ul>
  
  <p>Velg den du foretrekker, klikk "Kopier signatur", og lim inn i e-postprogrammet ditt.</p>
  
  <p>Hilsen<br>IT-avdelingen</p>
</body>
</html>
```

### 3. Add Send Endpoint to Router
**File:** `backend/app/routers/signatures.py` (modify)

Add endpoint:
```python
POST /api/signatures/{employee_id}/send
```

Request body (optional):
```python
class SendSignatureRequest(BaseModel):
    sender_email: str = "it@proaktiv.no"  # Default sender
```

Response:
```python
class SendSignatureResponse(BaseModel):
    success: bool
    sent_to: str
    message: str
```

Logic:
1. Fetch employee
2. Load and render notification email template
3. Call graph_service.send_mail()
4. Return success/failure

## ENVIRONMENT VARIABLES NEEDED
The following must exist in `backend/.env`:
- `ENTRA_TENANT_ID`
- `ENTRA_CLIENT_ID`
- `ENTRA_CLIENT_SECRET`
- `SIGNATURE_SENDER_EMAIL` (new, default: it@proaktiv.no)
- `FRONTEND_URL` (new, for signature page links)

## RULES
- Follow existing async patterns
- Use httpx for HTTP requests (already in dependencies)
- Handle Graph API errors gracefully
- Log errors with proper context
- NO commits or pushes
- If credentials are missing, raise clear error message
- ASK if anything is unclear

## HANDOVER
When complete, provide a summary in this exact format:

---
**AGENT 2 COMPLETE**

Files created/modified:
- [ ] `backend/app/services/graph_service.py`
- [ ] `backend/scripts/templates/signature-notification-email.html`
- [ ] Modified `backend/app/routers/signatures.py`

Endpoint ready: `POST /api/signatures/{employee_id}/send`

Environment variables needed:
- [ ] SIGNATURE_SENDER_EMAIL
- [ ] FRONTEND_URL

Graph permissions required: `Mail.Send` (Application)

Issues encountered: (list any or "None")

Ready for Agent 3: (Yes/No)
---
```

---

## Agent 3: Frontend Signature Preview Component

### Command

```
/agent
```

### Prompt

```markdown
# TASK: Create Signature Preview Component for Dashboard

## CONTEXT
You are building the frontend component that displays signature previews on employee pages in the admin dashboard. This allows admins to visually QA signatures before sending.

## FILES TO READ FIRST (mandatory)
1. `frontend/src/app/employees/[id]/page.tsx` - Employee detail page (add tab here)
2. `frontend/src/components/ui/tabs.tsx` - Tab component pattern
3. `frontend/src/components/ui/button.tsx` - Button styling
4. `frontend/src/components/ui/card.tsx` - Card component
5. `frontend/src/lib/api.ts` - API client pattern
6. `.planning/codebase/DESIGN-SYSTEM.md` - Design tokens and patterns

## DELIVERABLES

### 1. Create API Hook
**File:** `frontend/src/hooks/v3/useSignature.ts`

```typescript
interface SignatureData {
  html: string;
  text: string;
  employee_name: string;
  employee_email: string;
}

interface UseSignatureReturn {
  signature: SignatureData | null;
  isLoading: boolean;
  error: Error | null;
  refetch: () => void;
}

export function useSignature(employeeId: string, version: 'with-photo' | 'no-photo'): UseSignatureReturn

interface SendSignatureReturn {
  send: () => Promise<void>;
  isSending: boolean;
  error: Error | null;
}

export function useSendSignature(employeeId: string): SendSignatureReturn
```

### 2. Create Signature Preview Component
**File:** `frontend/src/components/employees/SignaturePreview.tsx`

Features:
- Two tabs: "Med bilde" / "Uten bilde"
- Signature rendered in sandboxed iframe
- "Send signatur til ansatt" button with:
  - Loading spinner while sending
  - Success toast on completion
  - Error toast on failure
- Shows target email address
- Copy signature URL button (secondary action)

Props:
```typescript
interface SignaturePreviewProps {
  employeeId: string;
  employeeEmail: string;
  employeeName: string;
}
```

Design requirements:
- Use `shadow-card` for preview container
- Use `ring-strong` for active tab
- Button uses primary variant
- Follow existing component patterns

### 3. Export from Index
**File:** `frontend/src/components/employees/index.ts` (modify)

Add export for SignaturePreview component.

### 4. Export Hook from Index
**File:** `frontend/src/hooks/v3/index.ts` (modify)

Add exports for useSignature and useSendSignature.

## RULES
- Use existing UI components from `@/components/ui/*`
- Follow design system tokens (read DESIGN-SYSTEM.md)
- Use react-hot-toast for notifications (already installed)
- Iframe must have `sandbox` attribute for security
- NO commits or pushes
- ASK if design decisions are unclear

## HANDOVER
When complete, provide a summary in this exact format:

---
**AGENT 3 COMPLETE**

Files created/modified:
- [ ] `frontend/src/hooks/v3/useSignature.ts`
- [ ] `frontend/src/components/employees/SignaturePreview.tsx`
- [ ] Modified `frontend/src/components/employees/index.ts`
- [ ] Modified `frontend/src/hooks/v3/index.ts`

Component ready: `<SignaturePreview employeeId={id} employeeEmail={email} employeeName={name} />`

Issues encountered: (list any or "None")

Ready for Agent 4: (Yes/No)
---
```

---

## Agent 4: Employee Page Tab Integration

### Command

```
/agent
```

### Prompt

```markdown
# TASK: Add Signature Tab to Employee Detail Page

## CONTEXT
You are integrating the SignaturePreview component (created by Agent 3) into the employee detail page as a new tab.

## FILES TO READ FIRST (mandatory)
1. `frontend/src/app/employees/[id]/page.tsx` - Employee detail page to modify
2. `frontend/src/components/employees/SignaturePreview.tsx` - Component to integrate
3. `frontend/src/components/employees/index.ts` - Verify export exists

## DELIVERABLES

### 1. Modify Employee Detail Page
**File:** `frontend/src/app/employees/[id]/page.tsx`

Changes:
1. Import `SignaturePreview` from `@/components/employees`
2. Import `FileSignature` or `Signature` icon from lucide-react (use `PenLine` if Signature not available)
3. Add new tab trigger after "Sjekklister":
```tsx
<TabsTrigger value="signature" className="gap-2">
  <PenLine className="h-4 w-4" />
  Signatur
</TabsTrigger>
```

4. Add new TabsContent:
```tsx
<TabsContent value="signature">
  <Card>
    <CardHeader>
      <CardTitle>E-postsignatur</CardTitle>
    </CardHeader>
    <CardContent>
      <SignaturePreview
        employeeId={employeeId}
        employeeEmail={employee.email || ''}
        employeeName={employee.full_name}
      />
    </CardContent>
  </Card>
</TabsContent>
```

## RULES
- Minimal changes - only add the tab
- Follow existing tab patterns exactly
- Handle case where employee.email is null
- NO commits or pushes
- ASK if anything looks wrong

## HANDOVER
When complete, provide a summary in this exact format:

---
**AGENT 4 COMPLETE**

Files modified:
- [ ] `frontend/src/app/employees/[id]/page.tsx`

New tab added: "Signatur" (4th tab after Sjekklister)

Issues encountered: (list any or "None")

Ready for Agent 5: (Yes/No)
---
```

---

## Agent 5: Public Signature Page

### Command

```
/agent
```

### Prompt

```markdown
# TASK: Create Public Signature Self-Service Page

## CONTEXT
You are creating the public-facing page where employees visit to copy their email signature. This page is accessed via the link sent in the notification email.

## FILES TO READ FIRST (mandatory)
1. `frontend/src/hooks/v3/useSignature.ts` - Reuse the signature fetching hook
2. `frontend/src/app/employees/[id]/page.tsx` - Reference for page structure
3. `.planning/codebase/DESIGN-SYSTEM.md` - Design tokens
4. `frontend/public/assets/proaktiv-logo-black.png` - Logo to use

## DELIVERABLES

### 1. Create Public Signature Page
**File:** `frontend/src/app/signature/[id]/page.tsx`

Features:
- NO authentication required (public page)
- Clean, branded layout with Proaktiv logo
- Employee name displayed at top
- Two tabs: "Med bilde" / "Uten bilde"
- Signature preview in styled container
- **"Kopier signatur" button** - copies HTML to clipboard
- Success toast: "Signatur kopiert! Lim inn i e-postprogrammet ditt."
- Instructions accordion with steps for:
  - Outlook (desktop)
  - Outlook (web)
  - Gmail
  - Apple Mail

Copy to clipboard must use:
```typescript
const blob = new Blob([html], { type: 'text/html' });
const clipboardItem = new ClipboardItem({ 'text/html': blob });
await navigator.clipboard.write([clipboardItem]);
```

### 2. Create Loading State
Show skeleton while signature loads.

### 3. Create Error State
If employee not found, show friendly error with Proaktiv branding.

## PAGE LAYOUT

```
┌─────────────────────────────────────────────┐
│  [Proaktiv Logo]                            │
│                                             │
│  Din e-postsignatur, {Name}                 │
│                                             │
│  ┌─────────────┬──────────────┐             │
│  │ Med bilde   │ Uten bilde   │             │
│  └─────────────┴──────────────┘             │
│                                             │
│  ┌─────────────────────────────────────┐    │
│  │                                     │    │
│  │    [Signature Preview]              │    │
│  │                                     │    │
│  └─────────────────────────────────────┘    │
│                                             │
│  [ Kopier signatur ]  (primary button)      │
│                                             │
│  ▸ Slik legger du inn signaturen            │
│    (expandable instructions)                │
│                                             │
└─────────────────────────────────────────────┘
```

## RULES
- Page must be fully public (no auth checks)
- Use design system tokens
- Mobile responsive
- Accessible (proper ARIA labels)
- NO commits or pushes
- ASK if design decisions unclear

## HANDOVER
When complete, provide a summary in this exact format:

---
**AGENT 5 COMPLETE**

Files created:
- [ ] `frontend/src/app/signature/[id]/page.tsx`

Page accessible at: `/signature/{employee-uuid}`

Features implemented:
- [ ] Tab switching (with-photo / no-photo)
- [ ] Copy to clipboard (HTML)
- [ ] Instructions accordion
- [ ] Loading state
- [ ] Error state
- [ ] Mobile responsive

Issues encountered: (list any or "None")

Ready for Agent 6: (Yes/No)
---
```

---

## Agent 6: PowerShell Bulk Email Script

### Command

```
/agent
```

### Prompt

```markdown
# TASK: Create PowerShell Script for Bulk Signature Email Sending

## CONTEXT
You are creating a PowerShell script for the initial rollout to 120+ employees. This script fetches all employees and sends each one their personalized signature link via Graph API.

## FILES TO READ FIRST (mandatory)
1. `backend/.env` - Entra credentials
2. `backend/scripts/Sync-EntraIdEmployees.ps1` - Reference for Graph auth pattern
3. `backend/scripts/Deploy-OutlookSignature.ps1` - Reference for .env loading pattern

## DELIVERABLES

### 1. Create Bulk Send Script
**File:** `backend/scripts/Send-SignatureEmails.ps1`

Parameters:
```powershell
param(
    [Parameter(Mandatory = $false)]
    [string]$ApiBaseUrl = "https://proaktiv-admin.up.railway.app",
    
    [Parameter(Mandatory = $false)]
    [string]$FrontendUrl = "https://proaktiv-dokument-hub.vercel.app",
    
    [Parameter(Mandatory = $false)]
    [string]$SenderEmail = "it@proaktiv.no",
    
    [Parameter(Mandatory = $false)]
    [string[]]$FilterEmails,  # Send only to these emails (for testing)
    
    [switch]$DryRun,  # Don't actually send, just show what would be sent
    
    [switch]$Force    # Skip confirmation prompt
)
```

Flow:
1. Load .env file for Entra credentials
2. Get Graph access token (client credentials flow)
3. Fetch all employees from `$ApiBaseUrl/api/employees`
4. Filter to only active employees with email addresses
5. For each employee:
   - Generate signature page URL: `$FrontendUrl/signature/{id}`
   - Load email template
   - Replace placeholders
   - Send via Graph API (unless -DryRun)
   - Show progress
6. Print summary report

Features:
- Progress bar with percentage
- Color-coded output (green = sent, yellow = skipped, red = error)
- Summary at end (sent, skipped, failed)
- -DryRun mode for testing
- -FilterEmails for testing with specific users
- Confirmation prompt before bulk send (unless -Force)

### 2. Create Launcher Script
**File:** `run-signature-emails.bat`

```batch
@echo off
echo Sending signature emails to all employees...
echo.
powershell -ExecutionPolicy Bypass -File "backend\scripts\Send-SignatureEmails.ps1" %*
pause
```

## EMAIL TEMPLATE (embedded in script)

```
Subject: Din nye e-postsignatur er klar

Body:
Hei {FirstName},

Din personlige e-postsignatur er nå klar til bruk.

Klikk her for å hente signaturen din:
{SignatureUrl}

På siden finner du to versjoner:
- Med profilbilde
- Uten profilbilde

Velg den du foretrekker, klikk "Kopier signatur", og lim inn i e-postprogrammet ditt.

Hilsen
IT-avdelingen
Proaktiv Eiendomsmegling
```

## RULES
- Use PowerShell 5.1 compatible syntax (no ?? operator)
- Use HTML entities for Norwegian characters in hardcoded strings
- Proper error handling with try/catch
- Rate limiting (small delay between sends to avoid throttling)
- NO commits or pushes
- ASK if Graph API patterns unclear

## HANDOVER
When complete, provide a summary in this exact format:

---
**AGENT 6 COMPLETE**

Files created:
- [ ] `backend/scripts/Send-SignatureEmails.ps1`
- [ ] `run-signature-emails.bat`

Usage:
```powershell
# Dry run (test without sending)
.\backend\scripts\Send-SignatureEmails.ps1 -DryRun

# Send to specific person (testing)
.\backend\scripts\Send-SignatureEmails.ps1 -FilterEmails "adrian@proaktiv.no"

# Send to all (production)
.\backend\scripts\Send-SignatureEmails.ps1
```

Issues encountered: (list any or "None")

Ready for final review: (Yes/No)
---
```

---

## Post-Agent Checklist

After all agents complete, return summaries to orchestrator for:

1. **Code Review** - Verify all files created correctly
2. **Lint Check** - Run linters on new files
3. **Integration Test** - Test the full flow locally
4. **Entra Permission** - Add Mail.Send to Azure app
5. **Commit & Push** - Single commit with all changes

### Final Commit Command (to be run by orchestrator)

```bash
git add .
git commit -m "feat(signatures): Add self-service email signature portal

- Backend: Signature rendering endpoint with photo/no-photo variants
- Backend: Graph API service for sending signature notification emails
- Frontend: SignaturePreview component with send button
- Frontend: New Signatur tab on employee detail page
- Frontend: Public /signature/[id] page for self-service
- Scripts: Bulk email sender for initial 120+ employee rollout

Closes: Signature portal implementation"

git push origin main
```

---

## Rollback Plan

If issues occur after deployment:

1. Revert commit: `git revert HEAD`
2. Push revert: `git push origin main`
3. Investigate and fix
4. Re-run affected agents
