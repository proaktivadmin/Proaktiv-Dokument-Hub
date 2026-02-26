---
name: markdown-converter
description: Convert HTML/PDF/Word and similar files to Markdown using markitdown. Use when normalizing external source material for analysis, template intake, or agent processing.
---

# Markdown Converter

Use this when source material is difficult to analyze in raw binary or HTML form.

## When to Use

- Converting `.html`, `.pdf`, `.docx`, `.rtf` before template analysis
- Preparing source docs for subagent pipelines and content comparison
- Creating deterministic text artifacts for handoffs or QA review

## Preferred Command

```bash
python scripts/tools/markdown_convert.py "<input-file>" -o "<output-file>.md"
```

## Notes

- Wrapper uses `uvx markitdown`.
- If `uvx` is missing, install `uv` first.
- Keep converted markdown artifacts alongside analysis outputs when possible.

## Validation

- Confirm output markdown exists and is non-empty.
- Spot-check headers/tables/critical legal sections for extraction fidelity.
