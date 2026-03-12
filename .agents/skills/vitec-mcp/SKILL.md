---
name: vitec-mcp
description: Use the local Vitec Next MCP server for flettekode/reference lookup and template validation/extraction. Trigger when you need structured Vitec resources (`vitec://...`) or MCP tools (`validate_template`, `extract_merge_fields`, `check_stilark_compliance`) instead of ad hoc parsing.
---

# Vitec MCP Skill

## When to Use

Use this skill when you need to:
- Look up Vitec merge fields/flettekoder by category or search query
- Fetch canonical reference data (kategorier, objektstyper, stilark, layouts)
- Validate Vitec template HTML quickly with MCP tools
- Extract merge fields, conditions, and loops from HTML
- Run Stilark compliance checks as read-only analysis

Prefer this over manual docs scanning when the question maps to `vitec://` resources or the 3 analysis tools.

## Available `vitec://` Resources

- `vitec://flettekoder`
  - Category overview + counts + metadata
- `vitec://flettekoder/{category}`
  - Fields for one category (case-insensitive)
- `vitec://flettekoder/search/{query}`
  - Field search by path/label
- `vitec://kategorier`
  - Dokumentkategorier from parsed reference
- `vitec://objektstyper`
  - Objektstyper from parsed reference
- `vitec://stilark`
  - Stilark reference payload
- `vitec://layout/{name}`
  - One layout partial by name

## Available Tools

### `validate_template`

**Params**
- `html: str`

**Returns**
- `valid`, `score`
- check list for wrapper/stilark/theme/font/inline-style/vitec-if/vitec-foreach
- `suggestions`, `forbidden_style_issues`, syntax issue lists

**Example**
```json
{
  "toolName": "validate_template",
  "arguments": {
    "html": "<div id=\"vitecTemplate\"><span vitec-template=\"resource:Vitec Stilark\">&nbsp;</span></div>"
  }
}
```

### `extract_merge_fields`

**Params**
- `html: str`

**Returns**
- `fields` (with required/known/occurrences)
- `conditions` (`vitec-if`)
- `loops` (`vitec-foreach`)
- `unknown_fields`
- aggregate `stats`

**Example**
```json
{
  "toolName": "extract_merge_fields",
  "arguments": {
    "html": "<p>[[oppdrag.nr]]</p><tbody vitec-foreach=\"selger in Model.selgere\"><tr><td>[[*selger.navn]]</td></tr></tbody>"
  }
}
```

### `check_stilark_compliance`

**Params**
- `html: str`

**Returns**
- `compliant`, `score`, `stilark_referenced`
- `issues`
- `element_count`, `elements_with_forbidden_styles`

**Example**
```json
{
  "toolName": "check_stilark_compliance",
  "arguments": {
    "html": "<div id=\"vitecTemplate\"><span vitec-template=\"resource:Vitec Stilark\">&nbsp;</span><p style=\"display:flex\">Hei</p></div>"
  }
}
```

## Usage Patterns

### 1) Find valid merge field for a template line
1. Read `vitec://flettekoder/search/{query}`
2. Confirm exact `path`
3. Insert as `[[path]]` (or `[[*loop.path]]` inside loops)

### 2) Validate template before save/publish
1. Call `validate_template`
2. If invalid, fix top failing checks
3. Re-run until `valid: true`

### 3) Audit unknown fields in imported HTML
1. Call `extract_merge_fields`
2. Inspect `unknown_fields`
3. Cross-check against `vitec://flettekoder/search/{query}`

### 4) Check style compliance quickly
1. Call `check_stilark_compliance`
2. Remove forbidden inline style properties
3. Ensure `vitec-template="resource:Vitec Stilark"` exists
