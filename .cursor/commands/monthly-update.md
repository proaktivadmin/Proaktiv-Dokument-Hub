# /monthly-update — Vitec Next Monthly Release Sync

Run after each Vitec Next monthly release to keep the master template library current,
update the knowledge base, and track what changed.

## Usage

```
/monthly-update
Vitec Next February 2026 monthly release
```

Or with specific release notes from Vitec's changelog email:

```
/monthly-update
February 2026: updated Kjøpekontrakt FORBRUKER (§27 revision),
new template Overdragelsesdokument Næring, removed Gammelt Skjøte.
```

---

## Agent Workflow

### Phase 0: Pre-flight Check

1. Check if a fresh export already exists:
   - `data/vitec-next-export.json` — modified today?
   - `~/Downloads/vitec-next-export.json` — downloaded recently?

   If a fresh export exists (modified within the last few hours), skip to **Phase 2**.
   Otherwise, proceed to **Phase 1** (browser scrape).

2. Check what we're working with:
   ```bash
   # How many templates in the current library?
   python -c "import json; d=json.load(open('templates/index.json')); print(d['total_templates'], 'stored templates, generated at', d['generated_at'])"
   ```

---

### Phase 1: Scrape Fresh Export from Vitec Next

This requires an active Vitec Next browser session.

1. **Check browser tabs** — use `browser_tabs` to see if Vitec Next is open.
   - If not open, navigate to `https://proatest.qa.vitecnext.no` (test) or production Vitec Next URL.
   - Prompt the user to log in if needed (we need the `x-c__f` session cookie).

2. **Verify authentication** — run in the Vitec page context:
   ```javascript
   async () => {
     const cookie = document.cookie.split(";").map(s => s.trim()).find(s => s.startsWith("x-c__f="));
     return cookie ? "Authenticated: " + cookie.slice(0, 30) + "..." : "NOT authenticated";
   }
   ```

3. **Export all templates** — use the full export script from `docs/vitec-next-mcp-scrape-and-import.md`.

   The script fetches the list endpoint, then iterates each template ID to fetch content.
   It downloads `vitec-next-export.json` to the user's Downloads folder.

   Key safety rules (enforce these):
   - Sequential requests only (no parallel fetching)
   - 1–2 second delays + jitter between template fetches
   - Stop on HTTP errors (don't retry silently)
   - Log progress to console every 10 templates

4. **Move the export** to `data/vitec-next-export.json`:
   ```powershell
   # Windows
   Move-Item "$env:USERPROFILE\Downloads\vitec-next-export.json" "data\vitec-next-export.json" -Force
   ```
   ```bash
   # Mac/Linux
   mv ~/Downloads/vitec-next-export.json data/vitec-next-export.json
   ```

---

### Phase 2: Run Content Diff

Run the monthly diff tool to compare the new export against the stored library:

```bash
python scripts/tools/monthly_diff.py \
    --reason "Vitec Next {YYYY-MM} monthly release" \
    --json-output scripts/qa_artifacts/monthly-diff-{YYYY-MM-DD}.json
```

This produces:
- `scripts/qa_artifacts/MONTHLY-DIFF-{date}.md` — human-readable report
- `scripts/qa_artifacts/monthly-diff-{date}.json` — structured data (for agent)

Read both outputs. The JSON provides the structured data; the markdown is the decision document.

**Key numbers to report to the user:**
- Total changed / new / removed / unchanged
- Risk breakdown: critical / structural / cosmetic / trivial
- KB impact: new merge fields, CSS changes

---

### Phase 3: Present Tier-1 Summary

Present a concise summary to the user before going into details:

```
Monthly update diff complete for Vitec Next {month} release.

Summary:
  Changed:   {N} templates  (🔴 {critical} critical, 🟠 {structural} structural, 🟡 {cosmetic} cosmetic, ⚪ {trivial} trivial)
  New:       {N} templates
  Removed:   {N} templates
  Unchanged: {N} templates

Knowledge base impact:
  New merge fields: {list or "none"}
  CSS changes: {N} templates affected
  PATTERNS.md update needed: Yes/No
  LESSONS.md update needed: Yes/No
```

Ask the user how they want to proceed:
- **A** — "Review each changed template in detail" (start with critical/structural)
- **B** — "Accept all trivial/cosmetic, review structural/critical only"
- **C** — "Accept all changes and rebuild the library" (use only if user is confident)

---

### Phase 4: Per-Template Review (for critical and structural changes)

For each critical/structural template (in score order, highest first):

1. **Show the diff summary** from the JSON (merge fields added/removed, conditions, size delta).

2. **Show the actual HTML diff** — use `vitec_sync_check.py --compare`:
   ```bash
   # Extract the new template content to a staging file
   python -c "
   import json
   data = json.load(open('data/vitec-next-export.json'))
   tmpl = next(t for t in data['templates'] if t['vitec_template_id'] == '{UUID}')
   open('templates/sync-staging/{safe_name}.html', 'w', encoding='utf-8').write(tmpl.get('content',''))
   print('Written')
   "

   python scripts/tools/vitec_sync_check.py \
       --compare templates/sync-staging/{safe_name}.html \
       --stored templates/master/{origin}/{filename}.html \
       --reason "{reason}"
   ```

3. **Present three choices** to the user for each template:

   **Accept** — Take the upstream change. Actions:
   - Copy `sync-staging/{name}.html` → `templates/master/{origin}/{filename}.html`
   - Also update `templates/by-category/{category}/{filename}.html`
   - If template has derivatives → flag them (see Reconcile)

   **Skip** — Keep our stored version.
   - Log skip reason in the monthly report
   - No file changes

   **Reconcile** — Accept upstream AND flag kundemal derivatives for rebuild.
   - Accept the system template (same as Accept)
   - List derivatives that need updating
   - Create build requests per `/process-template-requests` command

4. **For trivial/cosmetic** — batch accept unless user wants individual review.

---

### Phase 5: Handle New Templates

For each template in the "new" list:

1. Confirm with user: should this be added to the library?
2. If yes → it will be added when we rebuild (`build_template_library.py`)
3. If no → skip (note in report)

For templates with `vitec-system` origin — generally accept.
For `kundemal` templates — confirm with user (may be deprecated Proaktiv templates).

---

### Phase 6: Apply Changes — Rebuild Library

After decisions are made, rebuild the library from the new export:

```bash
# Preview first (dry-run)
python scripts/tools/build_template_library.py --input data/vitec-next-export.json --dry-run

# Apply (this overwrites templates/master/ and templates/by-category/ completely)
python scripts/tools/build_template_library.py --input data/vitec-next-export.json
```

**⚠️ Important:** `build_template_library.py` replaces the entire `templates/master/` directory.
Any per-template decisions (skip/reconcile) made in Phase 4 are lost after a full rebuild.

Two strategies to handle this:
- **Full rebuild** (simpler) — accept all changes, run full rebuild, then manually restore
  any "skipped" templates from git (`git checkout HEAD -- templates/master/...`).
- **Selective update** (precise) — only copy accepted templates individually, then rebuild
  just the `index.json` by running `build_template_library.py --dry-run` and manually
  updating the index.

For monthly updates where most templates are trivial/cosmetic changes, **full rebuild** is recommended.
For releases with significant skip/reconcile decisions, use **selective update**.

After rebuild:
```bash
# Verify the new library
python -c "import json; d=json.load(open('templates/index.json')); print('Library rebuilt:', d['total_templates'], 'templates')"
```

---

### Phase 7: Update Knowledge Base

Re-mine the library to detect any new patterns from the updated templates:

```bash
python scripts/tools/mine_template_library.py
```

Compare the new `LIBRARY-MINING-REPORT.md` against the previous one.

Check for:
- **New merge fields** — if the monthly diff found new fields, verify they appear in the mining report
- **New CSS patterns** — if CSS changed, check the patterns section
- **Structural changes** — new `vitec-foreach` patterns, new `vitec-if` conditions

If the mining report reveals new patterns not yet in the knowledge base:

1. **New merge fields** → add to `PATTERNS.md` field reference section (MF7)
2. **New CSS patterns** → add as a lesson in `LESSONS.md` (S-category or new category)
3. **New vitec-if expressions** → add to LESSONS.md VIF category if non-obvious
4. **New vitec-resources** → add to LESSONS.md MF8 (resource catalog)

Follow the knowledge base maintenance rule: any change to LESSONS.md or PATTERNS.md
MUST be accompanied by a CHANGELOG.md entry.

---

### Phase 8: Generate Monthly Report + Changelog

1. **Finalize the sync report** — the `MONTHLY-DIFF-{date}.md` is the base.
   Edit it to reflect actual decisions (mark Accept/Skip/Reconcile for each template).

2. **Append to CHANGELOG.md** in the knowledge base:

   ```
   ## {YYYY-MM-DD} — Monthly Sync: Vitec Next {Month YYYY} Release

   **Trigger:** Monthly release sync
   **Library:** {old_count} → {new_count} templates
   **Changed:** {changed_count} ({critical} critical, {structural} structural, {cosmetic} cosmetic, {trivial} trivial)
   **New:** {new_count}
   **Removed:** {removed_count}

   **Decisions:**
   - Accepted: {list of template names}
   - Skipped: {list with reasons}
   - Reconciled (derivatives flagged): {list}

   **KB updates:**
   - {any LESSONS.md / PATTERNS.md changes, or "None — no new patterns found"}
   ```

3. **Clean up staging:**
   ```bash
   # Remove staging files (PowerShell)
   Remove-Item templates/sync-staging/* -ErrorAction SilentlyContinue
   ```

4. **Commit the update:**
   ```bash
   git add templates/ scripts/qa_artifacts/MONTHLY-DIFF-{date}.md .agents/skills/vitec-template-builder/CHANGELOG.md
   git commit -m "chore(templates): Vitec Next {Month YYYY} monthly sync — {N} templates updated"
   ```

---

## Derivative Tracking

When a system template changes and has derivatives (kundemal copies), the reconcile decision
means:
1. Accept the upstream change to the system template
2. For each derivative — create a Mode A2 (reconcile) build request

Derivatives are tracked in `templates/index.json` under the `"derivatives"` field.
When a system template is synced, ask the user if they know of any kundemal copies
not already listed, and update the `"derivatives"` array accordingly.

---

## Context Files

### Scripts
- `scripts/tools/monthly_diff.py` — content-level bulk diff (the primary Phase 2 tool)
- `scripts/tools/vitec_sync_check.py` — targeted diff and compare modes
- `scripts/tools/build_template_library.py` — rebuilds `templates/master/` from export
- `scripts/tools/mine_template_library.py` — re-mines library for KB updates

### Data & Reports
- `data/vitec-next-export.json` — the fresh Vitec export (input for all tools)
- `templates/index.json` — current library index (updated by build_template_library.py)
- `scripts/qa_artifacts/MONTHLY-DIFF-{date}.md` — the primary decision document
- `scripts/qa_artifacts/monthly-diff-{date}.json` — structured data for agent

### Knowledge Base
- `.agents/skills/vitec-template-builder/LESSONS.md` — lessons registry
- `.agents/skills/vitec-template-builder/PATTERNS.md` — copy-pasteable patterns
- `.agents/skills/vitec-template-builder/CHANGELOG.md` — KB + sync changelog

### Reference Docs
- `docs/vitec-next-mcp-scrape-and-import.md` — full export procedure
- `docs/vitec-next-export-format.md` — export JSON schema

---

## Quick Decision Matrix

| Change type | Default action | When to deviate |
|-------------|---------------|-----------------|
| Trivial (whitespace, encoding) | Accept all | Never |
| Cosmetic CSS only | Accept | Skip if we intentionally customized CSS |
| New merge field added | Accept + add to PATTERNS.md MF7 | Only skip if field is deprecated in our workflow |
| Merge field removed | Review carefully — may break derivatives | Skip if field is still used in kundemal copies |
| Condition logic changed | Review the before/after logic | Accept if logic improvement is clear |
| Legal text changed | Flag as critical, read the actual text diff | Always review — never auto-accept |
| Template renamed | Update index + derivatives mapping | — |
| Template removed | Check for derivatives before removing | Don't remove if derivatives exist |
| New template (vitec-system) | Accept (add to library) | Skip only if clearly irrelevant to Proaktiv |
| New template (kundemal) | Ask user | May be a deleted Proaktiv template being re-imported |
