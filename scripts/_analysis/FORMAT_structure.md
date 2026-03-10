# Structure Analysis Output Format

The Structure Analyzer subagent must produce a file matching this format.
Save to: `scripts/_analysis/{template_name}/structure.md`

---

## Example Output

```markdown
# Structure Analysis: [Template Name]

## Source
- **File:** [path to source document]
- **Format:** [.htm / .docx / .rtf]
- **Encoding:** [windows-1252 / UTF-8]
- **Total sections:** [count]

## Document Skeleton

### Section List

| # | Heading | Type | Length | Page Break |
|---|---------|------|--------|------------|
| 1 | Partene i handelen | party-listing | long | — |
| 2 | Kjøpesum og omkostninger | financial | medium | — |
| 3 | Garanti | legal-text | short | avoid-break |
| ... | ... | ... | ... | ... |

Type values: `party-listing`, `financial`, `legal-text`, `checkbox-section`,
`signature-block`, `header-info`, `terms`, `mixed`

Length values: `short` (1-4 paragraphs), `medium` (5-10), `long` (10+)

Page Break values:
- `avoid-break` — short section, wrap entire article
- `internal-wrap` — long section, needs internal avoid-break divs
- `forced-before` — major transition, add page-break-before
- `—` — no special treatment needed

### Table Inventory

| Location | Class | Columns | Purpose |
|----------|-------|---------|---------|
| Section 1 | roles-table | Navn, Adresse/Kontaktinfo | Party listing |
| Section 2 | costs-table | Beskrivelse, Beløp | Payment breakdown |
| ... | ... | ... | ... |

### Checkbox Inventory

| Location | Control Type | Count | Description |
|----------|-------------|-------|-------------|
| Section 4 | data-driven | 2 | Alternativ 1 vs 2 (mutually exclusive) |
| Section 9 | data-driven | 3 | Overtakelse conditions |
| Section 15 | broker-interactive | 4 | Yes/No confirmations |
| ... | ... | ... | ... |

Control Type values: `data-driven` (system sets via vitec-if), `broker-interactive` (user toggles)

### Signature Block

- **Party groups:** [Selger, Kjøper, Megler]
- **Per party:** [name line, signing line, date field]
- **Uses foreach:** [yes/no]

### Party Listings

| Role | Location | Pattern |
|------|----------|---------|
| Selger(e) | Section 1, Signature | vitec-foreach with roles-table |
| Kjøper(e) | Section 1, Signature | vitec-foreach with roles-table |
| Megler | Section 1, Signature | Single entry |
| ... | ... | ... |

### Subsections (if any)

| Parent | Sub# | Heading | Notes |
|--------|------|---------|-------|
| 1 | 1A | Selveierbolig | eieform conditional |
| 1 | 1B | Borettslagsbolig | eieform conditional |
| ... | ... | ... | ... |

## Page Break Recommendations

### Short Sections (wrap entire article)
- Section 3: Garanti (4 paragraphs)
- Section 6: Tinglysing (2 paragraphs)
- ...

### Internal Wraps Needed
- Section 1: Heading + first party table
- Section 2: Heading + payment table
- ...

### Forced Page Breaks
- Before Section 9 (Overtakelse) — major document transition
- Before Signature block — always on fresh page
- ...

## Source Clues Detected

| Line/Area | Clue | Interpretation |
|-----------|------|----------------|
| Header | Wingdings 'q' characters | Checkbox locations |
| Section 4 | "Alt 1:" / "Alt 2:" text | vitec-if branching |
| Section 1B | "Borettslagsbolig" heading | eieform conditional |
| Various | Red text markers | Conditional content |
| Various | Dotted underlines | Insert field locations |
| ... | ... | ... |
```

## Rules for the Structure Analyzer

1. Do NOT map merge fields — that is the Field Mapper's job
2. Do NOT determine vitec-if conditions — that is the Logic Mapper's job
3. Focus on the document's physical structure: what goes where, how big is each section
4. Count sections, tables, checkboxes precisely
5. Note every source clue (Wingdings, red text, alternatives) but don't resolve them
6. Page break recommendations are based on section length and content type only
