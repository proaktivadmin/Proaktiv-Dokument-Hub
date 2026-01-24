# Signature Portal - Agent Commands Archive

> These are the agent prompts used to build the self-service signature portal.
> Archived for reference. See `.planning/codebase/AGENT-PIPELINE.md` for the reusable pattern.

---

## Agent 1: Backend Signature Service

```markdown
# Signature Portal - Agent 1: Backend Signature Service

You are building a signature portal for Proaktiv Eiendomsmegling. Create the backend service that renders personalized email signatures.

## READ SPEC FIRST
- .planning/phases/09-signature-portal/SPEC.md (full technical specification)

## READ THESE FILES (mandatory)
- backend/scripts/templates/email-signature.html
- backend/app/models/employee.py
- backend/app/models/office.py
- backend/app/routers/employees.py
- backend/app/services/employee_service.py

## DELIVERABLES

### 1. Create Signature Service
File: backend/app/services/signature_service.py

- Async method render_signature(db, employee_id: UUID, version: str) -> dict
- Fetch employee with office relationship
- Read HTML template from backend/scripts/templates/email-signature.html
- Replace placeholders:
  - {{DisplayName}} → employee.full_name
  - {{JobTitle}} → employee.title (empty string if None)
  - {{MobilePhone}} → employee.phone (empty string if None)
  - {{Email}} → employee.email
  - {{OfficeName}} → employee.office.name
  - {{OfficeAddress}} → employee.office.street_address
  - {{OfficePostal}} → f"{employee.office.postal_code} {employee.office.city}"
- Generate plain text version by stripping HTML tags
- Return dict with: html, text, employee_name, employee_email

### 2. Create No-Photo Template
File: backend/scripts/templates/email-signature-no-photo.html

Copy existing template, remove the profile photo <td> column (lines 13-16 area).

### 3. Create Signature Router
File: backend/app/routers/signatures.py

Endpoint: GET /api/signatures/{employee_id}?version=with-photo|no-photo

Response Pydantic model with: html, text, employee_name, employee_email

### 4. Register Router
File: backend/app/main.py - Add the signatures router

## RULES
- Follow existing async patterns in the codebase
- Use Pydantic for response schemas
- Handle missing employee with 404
- DO NOT commit or push any code
- ASK for clarification if anything is unclear

## HANDOVER FORMAT
When complete, respond with:

**AGENT 1 COMPLETE**

Files created:
- backend/app/services/signature_service.py
- backend/scripts/templates/email-signature-no-photo.html
- backend/app/routers/signatures.py
- Modified backend/app/main.py

Endpoint: GET /api/signatures/{employee_id}?version=with-photo|no-photo

Issues: (list any or "None")
```

---

## Agent 2: Backend Graph Email Service

```markdown
# Signature Portal - Agent 2: Backend Graph Email Service

You are extending the signature portal backend. Create a Graph API service to send signature notification emails.

## READ SPEC FIRST
- .planning/phases/09-signature-portal/SPEC.md (full technical specification)

## READ THESE FILES (mandatory)
- backend/.env (for ENTRA_TENANT_ID, ENTRA_CLIENT_ID, ENTRA_CLIENT_SECRET)
- backend/app/services/signature_service.py (just created by Agent 1)
- backend/app/routers/signatures.py (just created by Agent 1)
- backend/scripts/Sync-EntraIdEmployees.ps1 (Graph auth reference)

## DELIVERABLES

### 1. Create Graph Service
File: backend/app/services/graph_service.py

- Async get_access_token() -> str using client credentials flow
- Async send_mail(sender_email: str, recipient_email: str, subject: str, html_body: str) -> bool
- Use httpx for HTTP requests
- Read Entra credentials from os.environ
- Token endpoint: https://login.microsoftonline.com/{tenant_id}/oauth2/v2.0/token
- Mail endpoint: https://graph.microsoft.com/v1.0/users/{sender}/sendMail

### 2. Create Email Template
File: backend/scripts/templates/signature-notification-email.html

Create this HTML template:
- Greeting: "Hei {{FirstName}},"
- Message about signature being ready
- Link to {{SignatureUrl}}
- List of two versions (med/uten bilde)
- Instructions to copy and paste
- Signed "IT-avdelingen"

### 3. Add Send Endpoint
File: backend/app/routers/signatures.py (modify)

Add: POST /api/signatures/{employee_id}/send

Request body (optional): sender_email with default "it@proaktiv.no"
Response: success (bool), sent_to (str), message (str)

Logic: Fetch employee, render notification email, call graph_service.send_mail()

### 4. Environment Variables
Add to backend/.env.example:
- SIGNATURE_SENDER_EMAIL=it@proaktiv.no
- FRONTEND_URL=https://proaktiv-dokument-hub.vercel.app

## RULES
- Use httpx for async HTTP (already in dependencies)
- Handle Graph API errors gracefully with logging
- DO NOT commit or push any code
- ASK if credentials or patterns are unclear

## HANDOVER FORMAT
When complete, respond with:

**AGENT 2 COMPLETE**

Files created/modified:
- backend/app/services/graph_service.py
- backend/scripts/templates/signature-notification-email.html
- Modified backend/app/routers/signatures.py

Endpoint: POST /api/signatures/{employee_id}/send

New env vars needed: SIGNATURE_SENDER_EMAIL, FRONTEND_URL
Graph permission needed: Mail.Send (Application)

Issues: (list any or "None")
```

---

## Agent 3: Frontend Signature Preview Component

```markdown
# Signature Portal - Agent 3: Frontend Signature Preview Component

You are building the frontend SignaturePreview component for the admin dashboard.

## READ SPEC FIRST
- .planning/phases/09-signature-portal/SPEC.md (full technical specification)

## READ THESE FILES (mandatory)
- frontend/src/app/employees/[id]/page.tsx
- frontend/src/components/ui/tabs.tsx
- frontend/src/components/ui/button.tsx
- frontend/src/components/ui/card.tsx
- frontend/src/lib/api.ts
- .planning/codebase/DESIGN-SYSTEM.md

## DELIVERABLES

### 1. Create Signature Hook
File: frontend/src/hooks/v3/useSignature.ts

Two hooks:
- useSignature(employeeId, version) - fetches GET /api/signatures/{id}?version={version}
  Returns: { signature, isLoading, error, refetch }
- useSendSignature(employeeId) - posts to /api/signatures/{id}/send
  Returns: { send, isSending, error }

### 2. Create SignaturePreview Component
File: frontend/src/components/employees/SignaturePreview.tsx

Props: employeeId (string), employeeEmail (string), employeeName (string)

Features:
- Two tabs: "Med bilde" / "Uten bilde"
- Signature in sandboxed iframe
- "Send signatur til ansatt" button with loading state
- Success/error toasts using react-hot-toast
- Shows target email address

### 3. Export Component
File: frontend/src/components/employees/index.ts - Add SignaturePreview export

### 4. Export Hook
File: frontend/src/hooks/v3/index.ts - Add useSignature, useSendSignature exports

## RULES
- Use existing UI components from @/components/ui/*
- Follow design system tokens from DESIGN-SYSTEM.md
- Use react-hot-toast for notifications
- Iframe must have sandbox attribute
- DO NOT commit or push any code
- ASK if design patterns are unclear

## HANDOVER FORMAT
When complete, respond with:

**AGENT 3 COMPLETE**

Files created/modified:
- frontend/src/hooks/v3/useSignature.ts
- frontend/src/components/employees/SignaturePreview.tsx
- Modified frontend/src/components/employees/index.ts
- Modified frontend/src/hooks/v3/index.ts

Component: <SignaturePreview employeeId={id} employeeEmail={email} employeeName={name} />

Issues: (list any or "None")
```

---

## Agent 4: Employee Page Tab Integration

```markdown
# Signature Portal - Agent 4: Employee Page Tab Integration

You are adding the Signatur tab to the employee detail page.

## READ SPEC FIRST
- .planning/phases/09-signature-portal/SPEC.md (full technical specification)

## READ THESE FILES (mandatory)
- frontend/src/app/employees/[id]/page.tsx
- frontend/src/components/employees/SignaturePreview.tsx (just created by Agent 3)
- frontend/src/components/employees/index.ts

## DELIVERABLES

### 1. Modify Employee Detail Page
File: frontend/src/app/employees/[id]/page.tsx

Changes:
1. Import SignaturePreview from @/components/employees
2. Import PenLine icon from lucide-react
3. Add tab trigger after "Sjekklister" tab:

<TabsTrigger value="signature" className="gap-2">
  <PenLine className="h-4 w-4" />
  Signatur
</TabsTrigger>

4. Add TabsContent:

<TabsContent value="signature">
  <SignaturePreview
    employeeId={employeeId}
    employeeEmail={employee.email || ''}
    employeeName={employee.full_name}
  />
</TabsContent>

## RULES
- Minimal changes only - just add the tab
- Follow existing tab patterns exactly
- Handle null employee.email
- DO NOT commit or push any code
- ASK if anything looks inconsistent

## HANDOVER FORMAT
When complete, respond with:

**AGENT 4 COMPLETE**

Files modified:
- frontend/src/app/employees/[id]/page.tsx

Tab added: "Signatur" (after Sjekklister)

Issues: (list any or "None")
```

---

## Agent 5: Public Signature Page

```markdown
# Signature Portal - Agent 5: Public Signature Page

You are creating the public self-service signature page where employees copy their signature.

## READ SPEC FIRST
- .planning/phases/09-signature-portal/SPEC.md (full technical specification)

## READ THESE FILES (mandatory)
- frontend/src/hooks/v3/useSignature.ts (reuse hook from Agent 3)
- frontend/src/app/employees/[id]/page.tsx (structure reference)
- .planning/codebase/DESIGN-SYSTEM.md
- frontend/public/assets/proaktiv-logo-black.png

## DELIVERABLES

### 1. Create Public Signature Page
File: frontend/src/app/signature/[id]/page.tsx

NO authentication - fully public page.

Features:
- Proaktiv logo at top
- "Din e-postsignatur, {Name}" heading
- Two tabs: "Med bilde" / "Uten bilde"
- Signature preview in styled container
- "Kopier signatur" primary button
- Instructions accordion for Outlook, Gmail, Apple Mail

Copy to clipboard (HTML format):
const blob = new Blob([html], { type: 'text/html' });
const clipboardItem = new ClipboardItem({ 'text/html': blob });
await navigator.clipboard.write([clipboardItem]);

Toast on success: "Signatur kopiert! Lim inn i e-postprogrammet ditt."

### 2. Loading State
Show skeleton while signature loads.

### 3. Error State
Friendly "Signatur ikke funnet" message with Proaktiv branding.

## RULES
- Page must be public (no auth)
- Mobile responsive
- Use design tokens
- DO NOT commit or push any code
- ASK if design unclear

## HANDOVER FORMAT
When complete, respond with:

**AGENT 5 COMPLETE**

Files created:
- frontend/src/app/signature/[id]/page.tsx

URL: /signature/{employee-uuid}

Features:
- Tab switching
- Copy HTML to clipboard
- Instructions accordion
- Loading/error states
- Mobile responsive

Issues: (list any or "None")
```

---

## Agent 6: PowerShell Bulk Email Script

```markdown
# Signature Portal - Agent 6: PowerShell Bulk Email Script

You are creating the PowerShell script for bulk-sending signature emails to 120+ employees.

## READ SPEC FIRST
- .planning/phases/09-signature-portal/SPEC.md (full technical specification)

## READ THESE FILES (mandatory)
- backend/.env (Entra credentials)
- backend/scripts/Sync-EntraIdEmployees.ps1 (Graph auth pattern)
- backend/scripts/Deploy-OutlookSignature.ps1 (.env loading pattern)

## DELIVERABLES

### 1. Create Bulk Send Script
File: backend/scripts/Send-SignatureEmails.ps1

Parameters:
param(
    [string]$ApiBaseUrl = "https://proaktiv-admin.up.railway.app",
    [string]$FrontendUrl = "https://proaktiv-dokument-hub.vercel.app",
    [string]$SenderEmail = "it@proaktiv.no",
    [string[]]$FilterEmails,  # For testing specific users
    [switch]$DryRun,
    [switch]$Force
)

Flow:
1. Load .env for Entra credentials
2. Get Graph access token
3. Fetch employees from API
4. Filter: active status, has email
5. For each: generate URL, send email (unless -DryRun)
6. Show progress and summary

Features:
- Progress bar
- Color output (green=sent, yellow=skipped, red=error)
- Summary report at end
- -DryRun mode
- -FilterEmails for testing
- Confirmation prompt (unless -Force)
- Rate limiting (500ms between sends)

### 2. Create Launcher
File: run-signature-emails.bat

@echo off
echo Sending signature emails...
powershell -ExecutionPolicy Bypass -File "backend\scripts\Send-SignatureEmails.ps1" %*
pause

## RULES
- PowerShell 5.1 compatible (no ?? operator)
- Use HTML entities for Norwegian chars in strings
- Proper try/catch error handling
- DO NOT commit or push any code
- ASK if Graph patterns unclear

## HANDOVER FORMAT
When complete, respond with:

**AGENT 6 COMPLETE**

Files created:
- backend/scripts/Send-SignatureEmails.ps1
- run-signature-emails.bat

Usage:
- Dry run: .\backend\scripts\Send-SignatureEmails.ps1 -DryRun
- Test one: .\backend\scripts\Send-SignatureEmails.ps1 -FilterEmails "you@proaktiv.no"
- Send all: .\backend\scripts\Send-SignatureEmails.ps1

Issues: (list any or "None")
```

---

## Execution Summary

| Agent | Status | Issues |
|-------|--------|--------|
| 1 | ✅ Complete | Added /api/signatures to public routes |
| 2 | ✅ Complete | Default sender updated to froyland@proaktiv.no |
| 3 | ✅ Complete | None |
| 4 | ✅ Complete | Nested Card removed by orchestrator |
| 5 | ✅ Complete | Updated AuthProvider for public access |
| 6 | ✅ Complete | None |

**Lint fixes by orchestrator:**
- Removed unused `err` variable in catch block
- Escaped quotes with `&quot;` in JSX
- Extracted `signature?.html` to separate variable for React Compiler
