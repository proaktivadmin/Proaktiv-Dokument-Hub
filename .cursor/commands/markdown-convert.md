# Markdown Convert

Convert source files (HTML/PDF/DOCX/RTF) to Markdown for analysis workflows.

## Command

```bash
python scripts/tools/markdown_convert.py "<input-file>" -o "<output-file>.md"
```

## Usage Notes

- Use before template analysis if source format is noisy.
- Store resulting markdown in analysis/handoff artifacts when relevant.
- If command fails due to missing `uvx`, install `uv` and retry.
