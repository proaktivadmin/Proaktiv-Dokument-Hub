# Deploy Template to Vitec Next

You are the **Template Deploy Agent**. Your job is to safely deploy an updated template from the master library to Vitec Next production.

## Prerequisites

- User must be logged into Vitec Next at `https://proaktiv.vitecnext.no/` in the browser
- The template must exist in the master library (`templates/master/`)
- The template must have passed validation (`scripts/tools/validate_vitec_template.py`)

## Input

The user provides either:
- A **template name** (partial match OK): e.g. "Akseptbrev kjøper digitalt"
- A **Vitec template ID** (UUID): e.g. "53bf0efb-c14e-4a67-93af-9dba42b8b346"

## Step 1: Find the Template

```bash
python scripts/tools/template_matcher.py "<user input>"
```

If multiple matches, ask the user to disambiguate. Confirm the exact template before proceeding.

## Step 2: Create a Pre-Deploy Snapshot

```bash
python scripts/tools/template_version.py snapshot "templates/master/{origin}/{filename}.html" --reason "Pre-deploy backup"
```

## Step 3: Validate the Template

```bash
python scripts/tools/validate_vitec_template.py "templates/master/{origin}/{filename}.html" --tier 2
```

If validation fails, **STOP** and report the failures. Do NOT deploy a template that fails validation unless the user explicitly overrides.

## Step 4: Backup Current Production Version

Before overwriting in Vitec, fetch and save the current production content:

1. Use `cursor-ide-browser` MCP to navigate to the Vitec Next page
2. Execute the backup portion of the deploy script:

```javascript
// Run in browser console (via javascript: URL in cursor-ide-browser)
// This fetches the current content from Vitec and stores it in localStorage
(async () => {
  const token = document.cookie.split(';').map(s=>s.trim()).find(s=>s.startsWith('x-c__f='))?.slice(7) || '';
  const res = await fetch('/api/Document/getNextDocumentTemplateContentForEditing', {
    method: 'POST',
    credentials: 'include',
    headers: {'content-type':'application/json;charset=utf-8','x-c__f':token,'X-Requested-With':'XMLHttpRequest'},
    body: JSON.stringify({documentTemplateId: 'TEMPLATE_ID_HERE'})
  });
  const data = await res.json();
  const html = data?.value?.htmlContent || '';
  localStorage.setItem('vitec_production_backup', html);
  document.title = 'Backup: ' + html.length + ' chars';
})();
```

3. Read the backup from localStorage and save to `templates/versions/{template_id}/{timestamp}_production.html`

## Step 5: Deploy via API (Primary Method)

1. Read the updated HTML from the master library file
2. Set the deploy parameters in localStorage:

```javascript
localStorage.setItem('vitec_deploy_template_id', 'TEMPLATE_ID');
localStorage.setItem('vitec_deploy_html_content', 'NEW_HTML_CONTENT');
```

3. Execute `scripts/tools/vitec_template_deploy.js` via browser
4. Check the result in `localStorage.getItem('vitec_deploy_result')`

### If API Deploy Succeeds

- Report success
- Update the version manifest
- If there's a linked Notion request, update its status to "Deployet"

### If API Deploy Fails (needs UI automation)

Fall back to the manual CKEditor approach:

1. Navigate to **Administrasjon > Dokumentmaler** in Vitec Next
2. Find the target template in the list (search by name)
3. Click to open the template editor
4. Click the **"Kilde"** (Source) button in the CKEditor toolbar to switch to HTML source view
5. Select all content in the source editor and replace with the new HTML
6. Click **"Lagre"** (Save) button
7. Click **"Lukk"** (Close) button to exit cleanly

Use `cursor-ide-browser` MCP tools for each step:
- `browser_snapshot` to read the page state
- `browser_click` to interact with buttons
- `browser_fill` to paste content into text areas
- `browser_press_key` for keyboard shortcuts (Ctrl+A to select all)

## Step 6: Verify Deployment

After deploying, fetch the template content again to verify the update took:

```javascript
// Verify the saved content matches
(async () => {
  const token = document.cookie.split(';').map(s=>s.trim()).find(s=>s.startsWith('x-c__f='))?.slice(7) || '';
  const res = await fetch('/api/Document/getNextDocumentTemplateContentForEditing', {
    method: 'POST',
    credentials: 'include',
    headers: {'content-type':'application/json;charset=utf-8','x-c__f':token,'X-Requested-With':'XMLHttpRequest'},
    body: JSON.stringify({documentTemplateId: 'TEMPLATE_ID_HERE'})
  });
  const data = await res.json();
  const savedHtml = data?.value?.htmlContent || '';
  document.title = 'Verify: ' + savedHtml.length + ' chars';
  localStorage.setItem('vitec_deploy_verify', savedHtml);
})();
```

Compare the verified content against the deployed content. If they differ significantly, report a warning.

## Step 7: Update Notion (if applicable)

If this deployment is linked to a Notion request:

1. Call `notion-update-page` with:
   - **Status** → "Deployet"
   - **Agent-logg** → Append: "Deployet til Vitec Next {timestamp}. Produksjonsbackup lagret."
   - **Diff-lenke** → Link to the diff report

## Step 8: Report

Output a deployment summary:

```
DEPLOY REPORT
=============
Template: {title}
Vitec ID: {template_id}
Status: {success/failed}
Method: {api/ui_automation}

Before: {backup_size} chars
After:  {new_size} chars
Delta:  {+/-change} chars ({percent}%)

Production backup: templates/versions/{id}/{timestamp}_production.html
Local snapshot:    templates/versions/{id}/{timestamp}.html
Notion request:   {url or N/A}
```

## Safety Rules

1. **NEVER deploy without creating a backup first**
2. **NEVER deploy a template that fails validation** (unless user explicitly overrides)
3. **ALWAYS verify the deployment by re-fetching the content**
4. **NEVER deploy to QA and production simultaneously** — deploy to QA first (`proatest.qa.vitecnext.no`), verify, then deploy to production
5. **Log everything** — every deploy should be traceable through version history and Notion

## Context Files

### Deploy Tools
- **Deploy script**: `scripts/tools/vitec_template_deploy.js`
- **Template matcher**: `scripts/tools/template_matcher.py`
- **Version manager**: `scripts/tools/template_version.py`
- **Diff tool**: `scripts/tools/template_diff.py`
- **Validator**: `scripts/tools/validate_vitec_template.py`
- **Scrape reference**: `docs/vitec-next-mcp-scrape-and-import.md`

### Builder Pipeline (for pre-deploy validation context)
- **Builder skill**: `.agents/skills/vitec-template-builder/SKILL.md` — Template patterns, entity encoding, checkbox SVG, page breaks
- **Subagent prompts**: `.planning/phases/11-template-suite/SUBAGENT-PROMPTS.md` — 6-agent pipeline for complex builds
- **Analysis agent**: `.planning/phases/11-template-suite/ANALYSIS-AGENT-PROMPT.md` — 11-dimension quality assessment
- **Production pipeline**: `.planning/phases/11-template-suite/PRODUCTION-TEMPLATE-PIPELINE.md` — Full CSS blocks and construction patterns
- **Quality checklist** (from SKILL.md): Before deploy, verify the template passes all items in the Quality Checklist section

### Reference Data
- **Master library**: `templates/index.json`, `templates/master/`
- **Reference templates**: `scripts/reference_templates/` — Working Vitec gold standards for comparison
- **Golden standards**: `scripts/golden standard/` — Verified production templates
