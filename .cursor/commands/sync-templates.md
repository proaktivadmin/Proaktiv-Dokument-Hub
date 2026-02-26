# /sync-templates — Vitec Newsletter & Hotfix Sync

Sync templates after receiving a Vitec newsletter or hotfix notification about upstream changes.

## Usage Patterns

### Newsletter
User provides template names and a change description from a Vitec newsletter:
```
/sync-templates
Vitec newsletter March 2026: updated Kjøpekontrakt FORBRUKER (new §27 clause),
Oppdragsavtale (margin changes), Akseptbrev kjøper (new merge field).
```

### Hotfix
User provides a single affected template from a system notification:
```
/sync-templates
Hotfix: Kjøpekontrakt FORBRUKER — critical fix for konsesjon field rendering.
```

## Agent Workflow

### Phase 1: Parse & Prepare

1. Extract template names and change context from the user message.
2. Run the targeted sync check to locate stored templates:
   ```bash
   python scripts/tools/vitec_sync_check.py --templates "Template Name 1" "Template Name 2" \
       --reason "{newsletter/hotfix description}"
   ```
3. Review the output. For each template, confirm:
   - Found in `templates/index.json` (title + file path + origin)
   - Stored HTML file exists on disk
   - Derivatives (kundemal copies) are identified

### Phase 2: Fetch from Vitec Next

4. **Verify browser session**: Check browser tabs for an active Vitec Next session.
   - If not logged in, navigate to Vitec Next and prompt the user to log in.
   - The agent needs the `x-c__f` auth cookie to call Vitec API.

5. **For each template**, fetch the current HTML from Vitec Next:

   Use `browser_evaluate` to run in the Vitec Next page context:
   ```javascript
   async () => {
     const getToken = () => {
       const cookie = document.cookie
         .split(";").map(s => s.trim())
         .find(s => s.startsWith("x-c__f="));
       return cookie ? cookie.slice("x-c__f=".length) : "";
     };
     const token = getToken();
     if (!token) throw new Error("Missing x-c__f token — ensure you are logged into Vitec Next");

     const contentUrl = new URL("/api/Document/getNextDocumentTemplateContentForEditing", location.origin).toString();
     const res = await fetch(contentUrl, {
       method: "POST",
       credentials: "include",
       headers: {
         "content-type": "application/json;charset=utf-8",
         "x-c__f": token,
         "X-Requested-With": "XMLHttpRequest",
       },
       body: JSON.stringify({ documentTemplateId: "TEMPLATE_UUID_HERE" }),
     });
     const data = await res.json();
     return { ok: res.ok, html: data?.value?.htmlContent || "" };
   }
   ```

6. Save fetched HTML to staging:
   ```
   templates/sync-staging/{sanitized_template_name}.html
   ```

### Phase 3: Compare & Report

7. **For each fetched template**, run the compare:
   ```bash
   python scripts/tools/vitec_sync_check.py --compare templates/sync-staging/{name}.html \
       --stored templates/master/{origin}/{filename}.html --reason "{reason}"
   ```

8. Check `templates/index.json` for the `derivatives` field on the stored entry. If derivatives exist, note them for the reconciliation step.

### Phase 4: Present & Decide

9. For each template, present findings to the user with three options:

   **Accept** — The upstream change is good. Actions:
   - Copy from `templates/sync-staging/{name}.html` → `templates/master/{origin}/{filename}.html`
   - Also update `templates/by-category/{category}/{filename}.html`
   - Update `templates/index.json` entry (bump any date/version fields if present)

   **Skip** — Keep the current stored version. Actions:
   - Log the skip decision in the sync report
   - No file changes

   **Reconcile** — A kundemal derivative needs updating. Actions:
   - Accept the system template update (as above)
   - For each affected derivative, create a build request
   - Reference the Notion pipeline integration from `/process-template-requests` if available
   - At minimum, document the needed derivative updates in the sync report

### Phase 5: Knowledge Base & Reporting

10. For accepted templates with CSS or structural changes, flag for review:
    - `.agents/skills/vitec-template-builder/PATTERNS.md` — new CSS patterns, merge fields
    - `.agents/skills/vitec-template-builder/LESSONS.md` — new lessons from upstream changes

11. Generate the full sync report:
    ```
    scripts/qa_artifacts/SYNC-REPORT-{YYYY-MM-DD}.md
    ```

12. Append a sync entry to the changelog:
    ```
    .agents/skills/vitec-template-builder/CHANGELOG.md
    ```
    Format:
    ```
    ## {YYYY-MM-DD} — Vitec Sync: {reason}
    - Checked: {count} templates
    - Accepted: {list}
    - Skipped: {list}
    - Derivatives flagged: {list}
    ```

### Phase 6: Cleanup

13. Clean up `templates/sync-staging/` after all decisions are made.
14. Summarize actions taken and any follow-up needed.

## Derivative Tracking Convention

System template entries in `templates/index.json` may include a `"derivatives"` field —
a list of kundemal template names (titles or filename stems) that are based on that system template.

Example:
```json
{
  "vitec_template_id": "abc-123",
  "title": "Kjopekontrakt FORBRUKER",
  "origin": "vitec-system",
  "derivatives": ["Kjopekontrakt_Bruktbolig", "Kjopekontrakt_Bruktbolig_Proaktiv"]
}
```

When a system template changes, the agent should:
1. Check the `derivatives` field on the matched entry
2. Report which kundemal copies may need updating
3. Offer the **Reconcile** option for each affected derivative

The agent should also help **maintain** this field:
- When accepting a sync update, ask the user if they know of kundemal copies
- If the user identifies a derivative, add it to the `derivatives` array in `index.json`
- This builds the mapping incrementally over time

## Context Files

### Sync Tools
- **Sync checker**: `scripts/tools/vitec_sync_check.py` — local-side comparison and reporting
- **Template matcher**: `scripts/tools/template_matcher.py` — multi-strategy name resolution
- **Template diff**: `scripts/tools/template_diff.py` — structural HTML comparison
- **Master index**: `templates/index.json` — template metadata and file paths

### Fetching Reference
- **Vitec MCP scraping guide**: `docs/vitec-next-mcp-scrape-and-import.md` — API endpoints and auth
- **Template IDs**: `data/template-ids.json` — known Vitec template UUIDs

### Knowledge Base
- **Lessons**: `.agents/skills/vitec-template-builder/LESSONS.md`
- **Patterns**: `.agents/skills/vitec-template-builder/PATTERNS.md`
- **Changelog**: `.agents/skills/vitec-template-builder/CHANGELOG.md`

### Pipeline Integration
- **Build requests**: `.cursor/commands/process-template-requests.md` — for derivative rebuilds
- **Sync reports**: `scripts/qa_artifacts/SYNC-REPORT-*.md` — generated output
