# Vitec Next MCP Server

Local MCP server that exposes structured Vitec Next reference data (`vitec://...`) and template analysis tools for merge fields and Stilark/template compliance checks.

## What This Server Does

- Serves Vitec reference resources from parsed JSON data in `data/`
- Provides merge-field extraction from template HTML
- Validates template structure and syntax (wrapper, Stilark, `vitec-if`, `vitec-foreach`, etc.)
- Runs a focused Stilark compliance check for inline style usage + Stilark reference

## Install and Run

From repo root:

```bash
uv --directory mcp/vitec-next sync
uv --directory mcp/vitec-next run server.py
```

Cursor MCP config (`.cursor/mcp.json`) uses:

```json
{
  "mcpServers": {
    "vitec-next": {
      "command": "uv",
      "args": ["--directory", "mcp/vitec-next", "run", "server.py"],
      "env": {}
    }
  }
}
```

## Resources

- `vitec://flettekoder`
- `vitec://flettekoder/{category}`
- `vitec://flettekoder/search/{query}`
- `vitec://kategorier`
- `vitec://objektstyper`
- `vitec://stilark`
- `vitec://layout/{name}`

## Tools

- `validate_template(html: str)`
  - Returns validation checks, score, suggestions, and syntax/style issues
- `extract_merge_fields(html: str)`
  - Returns fields, conditions, loops, unknown fields, and stats
- `check_stilark_compliance(html: str)`
  - Returns compliance boolean, score, and style-related issues

## Data Freshness

When Vitec releases a new flettekoder/reference version:

1. Drop updated source documentation into `docs/`
2. Re-run parser scripts:
   - `uv --directory mcp/vitec-next run parsers/parse_flettekoder.py`
   - `uv --directory mcp/vitec-next run parsers/parse_reference.py`
3. Verify generated files:
   - `mcp/vitec-next/data/flettekoder.json`
   - `mcp/vitec-next/data/reference_data.json`
4. Commit the updated JSON artifacts

Optional future enhancement: add a `/refresh-vitec-data` command wrapper that automates this refresh workflow and validation checks.
