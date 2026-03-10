# Post-Review Additions — AGENT-2B-PIPELINE-DESIGN.md
## Summary of discoveries, decisions, and opportunities identified after the initial plan draft

This document contains all changes, additions, and new requirements discovered through review
after the initial plan document was produced. Every item below must be incorporated into
`AGENT-2B-PIPELINE-DESIGN.md` before the pipeline is considered complete.

---

## 1. BLOCKER — `validate_template.py` has a hardcoded path

**File:** `scripts/validate_template.py` lines 9–10

**Problem:** The script hardcodes a specific worktree path:
```python
WORKSPACE = r"c:\Users\Adrian\.claude-worktrees\Proaktiv-Dokument-Hub\mystifying-hertz"
```
This path will not exist in any normal agent run. The script will fail immediately.

**Required fixes (add to todo `fix-validator`):**
- Accept template path as a CLI argument — remove hardcoded `WORKSPACE`
- Add `--tier` flag to gate Section J (contract-specific) checks so non-contract templates are not penalised for missing contract structure
- Add `--compare-snapshot` flag for Mode A regression comparison against a pre-edit baseline

**Example corrected invocation:**
```bash
python scripts/validate_template.py scripts/production/MyTemplate_PRODUCTION.html --tier 4
python scripts/validate_template.py scripts/production/MyTemplate_PRODUCTION.html --compare-snapshot scripts/snapshots/MyTemplate_SNAPSHOT.html
```

---

## 2. GAP — No defined path from build output to the database

**Problem:** The pipeline produces `scripts/production/{name}_PRODUCTION.html` as a local
file. The plan's handoff step says "ready for database commit" but does not specify the
mechanism for getting the template into PostgreSQL with correct metadata.

**Decision:** The handoff section must specify the import mechanism explicitly. The existing
backend import API handles this. The agent must:
1. Construct the metadata payload (channel, template_type, phases, tags, origin, etc.) from
   the Source Analysis Report and the spec sheet confirmed at Stage 0
2. POST to the import endpoint or use the existing import script with the correct flags
3. Confirm the template appears in the database with correct fields before marking handoff complete

**Add to Section 7 (Handoff Format):**
```
DATABASE COMMIT:
- [ ] Metadata payload constructed (channel, template_type, phases, tags)
- [ ] Import executed via [method]
- [ ] Template ID confirmed in database: [UUID]
- [ ] Template visible in dashboard: Yes/No
```

---

## 3. NEW SECTION — Stage 10: Live Verification

**This is the most important addition. It replaces the conceptual S9 "CKEditor roundtrip
test" placeholder with a concrete, browser-automated verification gate against the real
Vitec Next QA system. Vitec itself becomes the test harness.**

### Scope
- **Mode B/C (Convert/Create), T3–T5 only** — T1/T2 skip (static validation is sufficient)
- **Mode A (Edit/Update)** — skip (template is already live in Vitec; verification is implicit)

### Environment
- **Test system URL:** `https://proatest.qa.vitecnext.no` (stored in `VITEC_TEST_URL` env var)
- **Auth:** Chrome session-based. The `cursor-ide-browser` MCP controls the user's actual
  Chrome instance, so an existing logged-in session is used directly. No separate Chromium
  instance — production cookies do not interfere.
- **Session handling (3 states):**
  - Dashboard loads → proceed directly, no login needed
  - Login page loads → fill `VITEC_TEST_USER` + `VITEC_TEST_PASSWORD` from `backend/.env` and submit
  - Login fails → stop immediately, surface: *"QA login failed — check VITEC_TEST_USER /
    VITEC_TEST_PASSWORD in backend/.env"*

**Required `.env` entries (add to `backend/.env` and `backend/.env.example`):**
```
VITEC_TEST_URL=https://proatest.qa.vitecnext.no
VITEC_TEST_USER=
VITEC_TEST_PASSWORD=
```

### Stage 10 Process (agent-executed via MCP browser)

```
Step 1:  Navigate to VITEC_TEST_URL
Step 2:  Handle auth state (see 3-state logic above)
Step 3:  Navigate to Document Templates
Step 4:  Create a new blank template named "[TEST] {template_name}_VERIFY"
Step 5:  Open the HTML source editor, paste the full production HTML
Step 6:  Save the template
Step 7:  Click the "Testfletting" button in the editor toolbar (top-left area)
Step 8:  In the Testfletting preview tab:
           - Confirm "Solåsveien 30" is loaded as the OBJEKT (default test property)
           - If not pre-loaded: search for and select "Solåsveien 30"
           - Click "Flett på nytt"
Step 9:  Observe result (see Gate Logic below)
Step 10: Click the magnifying glass icon → visual PDF inspection
Step 11: Download the PDF → save to scripts/qa_artifacts/{template_name}_testfletting.pdf
Step 12: Delete the [TEST] template to keep the QA system clean
```

### Gate Logic

| Result | Action |
|--------|--------|
| Document renders with merged field values | **PASS** → proceed to handoff |
| CKEditor crash / blank output / structural error | **FAIL (Type 1)** → export saved-back HTML, diff against input, return to Stage 5 with diff as diagnostic |
| Null reference / missing party / collection crash | **FAIL (Type 2)** → check if template has collection guards; if unguarded → Stage 5 to add guards; if correctly guarded but Solåsveien 30 lacks the entity → flag as data gap (see below) |
| Test system unreachable after 2 attempts | **UNREACHABLE** → commit template with `pending_live_verification` status; flag in handoff |

### Failure Recovery — Type 1 (Template Code Failure)
1. Re-open the template in the HTML source editor
2. Read back the HTML Vitec/CKEditor saved using the existing API pattern
   (`getNextDocumentTemplateContentForEditing` — documented in `docs/vitec-next-mcp-scrape-and-import.md`)
3. Diff the saved-back HTML against the original pasted HTML
4. The diff identifies exactly which `vitec-if`, `vitec-foreach`, or custom attributes
   CKEditor stripped silently
5. That diff is the input for the Stage 5 fix

### Failure Recovery — Type 2 (Missing Entity / Data Gap)
A "data gap" occurs when the template is correctly constructed but Solåsveien 30 does not
have the required entity (e.g. no lawyer registered, no fullmektig, no buyer party).

**Decision rule:**
- If the template has correct collection guards + fallback placeholders → this is NOT a
  template failure. Flag in handoff: *"Live verification: data gap on test property —
  [entity] not present on Solåsveien 30. Template construction is correct. Recommend
  first live test on a real case of this type before publishing."*
- Commit with `pending_live_verification` status
- Do NOT return to Stage 5 — the template is correct

**Note for specific template types (Pantedokument, Skjøte, and other legal documents):**
These templates may require entity types that Solåsveien 30 can never have by nature.
For these, the data gap flag is expected and acceptable. Document which entity was missing.

### Pipeline Architecture Update

The pipeline diagram must be updated from 9 stages to 10:

```
S0  → Intake Questionnaire (Mode + Tier)
S1  → Source Analysis
S2  → Field Mapping
S3  → Structural Planning
S4  → Template Shell
S5  → Template Construction
S6  → Static Validation (validate_template.py --tier N)
S7  → Visual Preview Generation
S8  → Content Verification
S9  → [T3-T5 only] Live Verification (Vitec QA system)
S10 → Handoff & Database Commit
```

---

## 4. NEW TOOL — PDF Magnifying Glass and Download as QA Artifacts

**Discovery:** The Testfletting preview tab in Vitec Next has two additional tools beyond
"Flett på nytt": a magnifying glass (PDF preview) and a PDF download button.

**Decision:** Both must be used as part of Stage 10 (already reflected in the Stage 10
process above). Rationale: a template can technically "not crash" but still produce a broken
PDF — wrong page breaks, missing content, unresolved merge fields, collapsed tables. The
rendered PDF is a higher-fidelity test than the HTML preview alone.

**Stage 10 PDF checks (visual inspection via magnifying glass):**
- All sections present and in correct order
- Tables are intact and not collapsed
- No raw `[[field.path]]` visible (all merge fields resolved)
- No `[Mangler X]` placeholders visible for entities that Solåsveien 30 should have
- Page breaks in sensible locations
- Signature blocks present and correctly spaced

**PDF download:**
- Save to `scripts/qa_artifacts/{template_name}_testfletting.pdf`
- Record path in handoff checklist

---

## 5. FUTURE OPPORTUNITY — PDF Thumbnail as Dashboard Cover Image

**Discovery:** The Testfletting-generated PDF is a more accurate representation of the
template than the current `build_preview.py` output, because it is rendered by Vitec's
actual engine rather than a simulation.

**Opportunity:** Use page 1 of the Testfletting PDF as the cover image in the template
library dashboard, replacing the current live preview render. The `preview_url` field
already exists on the Template model — no schema change required.

**Proposed future flow:**
1. Stage 10 downloads the PDF
2. A post-processing step extracts a thumbnail from page 1 (e.g. via `pdf2image` or
   similar)
3. Thumbnail stored and linked to the template record as `preview_url`

**Status:** Out of scope for the current pipeline. Flag as a future phase task. The current
pipeline must not prevent this from being added later — specifically, the PDF artifact must
be saved to `scripts/qa_artifacts/` so it is available for thumbnail extraction when this
is implemented.

---

## 6. NEW CONSTRUCTION RULE — Every Collection Must Have a Guard and a Fallback

**Problem identified:** Two distinct failure scenarios exist at Stage 10:
1. Template code is broken (HTML/syntax issue)
2. Template crashes because a required party/entity is missing from the test property —
   not a template bug, but a missing safety net

**Decision:** Scenario 2 is preventable by design. Every foreach loop and every
party-dependent field in every template must have both a guard and a Norwegian placeholder.
This is now a **hard construction rule**, not a suggestion.

### Rule (add to Section 3 — Construction Rules)

> **Rule: Every collection-dependent structure must be guarded and have a fallback.**
>
> No `vitec-foreach` loop may exist without both:
> - A `vitec-if="{collection}.Count > 0"` wrapper on the parent element
> - A sibling `vitec-if="{collection}.Count == 0"` element containing a Norwegian
>   placeholder in the format `[Mangler {rolle}]`
>
> This applies to all party collections (selgere, kjøpere, fullmektiger, advokater, etc.)
> and all dynamic lists. A template that crashes on missing data is considered **incomplete**
> regardless of how correct the HTML structure is.
>
> Ruleset reference: Section 4 (vitec-foreach), Section 11 failure mode #9.

### Example (required pattern)

```html
<!-- CORRECT — guarded with fallback -->
<div vitec-if="oppdrag.fullmektiger.Count > 0">
  <tbody vitec-foreach="fullmektig in oppdrag.fullmektiger">
    <tr>
      <td>[[*fullmektig.navn]]</td>
      <td>[[*fullmektig.idnummer]]</td>
    </tr>
  </tbody>
</div>
<div vitec-if="oppdrag.fullmektiger.Count == 0">
  <p>[Mangler fullmektig]</p>
</div>

<!-- INCORRECT — will crash if collection is empty -->
<tbody vitec-foreach="fullmektig in oppdrag.fullmektiger">
  <tr>
    <td>[[*fullmektig.navn]]</td>
  </tr>
</tbody>
```

---

## 7. NEW VALIDATOR CHECKS — Unguarded foreach as Automatic Fail

**Add to `validate_template.py` under Section F (Iteration):**

```python
# Check 1: every foreach has a Count > 0 guard wrapper
foreachs = re.findall(r'vitec-foreach="(\w+)\s+in\s+(\w+)"', html)
for item, collection in foreachs:
    guard = f'vitec-if="{collection}.Count'
    check("F", f"Guard for empty {collection} collection", guard in html,
          f"foreach '{item} in {collection}' has no null/empty guard — will crash if collection is empty")

# Check 2: every foreach has a Count == 0 fallback placeholder
for item, collection in foreachs:
    fallback_pattern = f'vitec-if="{collection}.Count == 0"'
    check("F", f"Fallback placeholder for empty {collection}", fallback_pattern in html,
          f"No '[Mangler {item}]' fallback found for empty {collection} — document will be silent on missing data")
```

**These are two separate checks with separate pass/fail:**
- Check 1 (missing guard): template will crash on empty collection → **automatic fail**
- Check 2 (missing fallback): template won't crash but gives no indication of missing data → **automatic fail**

**Both checks are automatable and must be added to the Section F group in the 70-check table.**

---

## 8. UPDATED — Stage 10 Failure Triage Table

Replace any existing failure handling table with this three-scenario version:

| Failure Type | Indicator | Root Cause | Action |
|---|---|---|---|
| Template code failure | Structural crash, blank document, CKEditor stripped attributes visible in diff | Template HTML is malformed or has invalid patterns | Return to Stage 5 with CKEditor diff as diagnostic input |
| Unguarded collection | Null reference error, party section missing or blank | foreach loop has no Count guard | Return to Stage 5 — add guard + `[Mangler X]` placeholder |
| Test property data gap | Template is correctly guarded, Solåsveien 30 simply lacks the entity type | Test data limitation, not a template bug | Flag in handoff as "data gap — not template failure". Commit as `pending_live_verification`. Recommend first live test on a real case. Do NOT return to Stage 5. |

**Critical:** Type 3 (data gap) must never be treated as a template failure. Sending a
correct template back to Stage 5 for a test data problem wastes time and risks introducing
regressions.

---

## 9. UPDATE — Test Property Details

**Default test property:** Solåsveien 30 (pre-loaded as default in Testfletting)

**Agent behaviour:**
- After clicking "Testfletting", confirm "Solåsveien 30" appears in the OBJEKT field
- If not pre-loaded: use the search field to find and select it
- Do not use a different property without explicit user instruction — Solåsveien 30 is the
  standard baseline that ensures consistent test conditions across all template builds

---

## 10. UPDATE — Handoff Format Extensions

**Add the following to Section 7 (Handoff Format) for T3–T5 templates:**

```
LIVE VERIFICATION (T3-T5 only):
- [ ] Stage 10 executed: Yes / No / Skipped (T1/T2)
- [ ] Testfletting result: PASS / FAIL / UNREACHABLE
- [ ] Failure type (if failed): Type 1 (code) / Type 2 (unguarded) / Type 3 (data gap)
- [ ] PDF artifact saved: scripts/qa_artifacts/{template_name}_testfletting.pdf
- [ ] PDF visual inspection completed: Yes / No
- [ ] Visual inspection notes: [list or "None"]
- [ ] Data gaps noted (entities missing on Solåsveien 30): [list or "None"]
- [ ] Recommended live test on real case: Yes / No

DATABASE COMMIT:
- [ ] Metadata payload constructed (channel, template_type, phases, tags)
- [ ] Import method used: [API endpoint / import script]
- [ ] Template ID confirmed in database: [UUID]
- [ ] Template status: published / pending_live_verification
- [ ] Template visible in dashboard: Yes / No
```

**Update SIGN-OFF section:**
```
SIGN-OFF:
- [ ] All automated checks pass (validate_template.py --tier N: X/X)
- [ ] Collection guard checks pass (no unguarded foreach loops)
- [ ] Preview visually inspected
- [ ] Content matches source document
- [ ] No unmapped fields remain
- [ ] Live verification: PASS or data gap documented
- [ ] PDF artifact saved
- [ ] Database commit confirmed
- [ ] Ready for use
```

---

## 11. SUMMARY — All todos to add or update

| Todo ID | Action | Status |
|---------|--------|--------|
| `fix-validator` | CLI arg for path, `--tier` flag, `--compare-snapshot` flag, remove hardcoded WORKSPACE | Add to existing todo |
| `write-s3-construction` | Add collection guard + fallback rule as hard requirement | Update existing todo |
| `write-s4-qa` | Add 2 new Section F checks (unguarded foreach, missing fallback) to 70-check table | Update existing todo |
| `write-s5-failures` | Add failure type 2 (unguarded collection) and type 3 (data gap) to failure triage | Update existing todo |
| `write-s7-handoff` | Add Live Verification block, PDF artifact block, Database Commit block, update SIGN-OFF | Update existing todo |
| `write-s10-live-verification` | New section — full Stage 10 spec as documented above | **New todo** |
| `add-env-vars` | Add `VITEC_TEST_URL`, `VITEC_TEST_USER`, `VITEC_TEST_PASSWORD` to `backend/.env.example` | **New todo** |
| `flag-pdf-thumbnail-opportunity` | Add future phase note: Testfletting PDF as dashboard cover image via `preview_url` field | **New todo** |
| `update-pipeline-diagram` | Update stage count from 9 to 10, add S9 Live Verification node with T3-T5 gate and FAIL→S5 loop | **New todo** |
