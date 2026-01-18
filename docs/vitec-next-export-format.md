# Vitec Next → Proaktiv Dokument Hub export format (JSON)

This repo supports importing **Vitec Next document template source** into Proaktiv Dokument Hub by first exporting templates to a single JSON file (usually produced via a Chrome-controlled workflow).

The importer expects a JSON object with this shape.

## Top-level fields

- **`export_version`**: string. Bump when you change the structure.
- **`exported_at`**: ISO timestamp.
- **`source`**: object with non-secret context (optional).
- **`templates`**: array of template objects.

## Template object (`templates[]`)

Required:

- **`vitec_template_id`**: string|number. Unique identifier from Vitec Next.
- **`title`**: string. Template name.
- **`content`**: string. The template source (HTML) as shown in Vitec Next.

Recommended (imported into first-class fields when present):

- **`description`**: string|null
- **`status`**: `"draft"|"published"|"archived"` (defaults to `published`)
- **`channel`**: `"pdf"|"email"|"sms"|"pdf_email"` (defaults to `pdf_email`)
- **`template_type`**: `"Objekt/Kontakt"|"System"` (defaults to `Objekt/Kontakt`)
- **`receiver_type`**: string|null
- **`receiver`**: string|null
- **`extra_receivers`**: string[]
- **`phases`**: string[]
- **`assignment_types`**: string[]
- **`ownership_types`**: string[]
- **`departments`**: string[]
- **`email_subject`**: string|null
- **`margins_cm`**: object with optional `top|bottom|left|right` numbers/strings
- **`tags`**: string[] (tag names, include origin tag like `Vitec Next` or `Kundemal`)
- **`categories`**: array of category objects (usually 1)
- **`attachments`**: array of attachment objects or strings (optional; stored in metadata)

Category object (`categories[]`):

- **`vitec_id`**: number|null (preferred for mapping)
- **`name`**: string|null

Everything else:

- **`metadata`**: arbitrary object (stored into `Template.metadata_json`).
  - Put *raw Vitec payloads* / extra fields here; the importer will keep it.

Note: fields like `receiver_type`, `phases`, `assignment_types`, `ownership_types`, and `departments` typically come
from the Vitec Next **Kategorisering** panel. Make sure those values are set before exporting, and include the template
details payload in your export if possible.

## Minimal example

```json
{
  "export_version": "1",
  "exported_at": "2026-01-17T12:00:00Z",
  "source": {
    "system": "vitec-next",
    "note": "Exported via Chrome MCP"
  },
  "templates": [
    {
      "vitec_template_id": 12345,
      "title": "Akseptbrev til kjøper",
      "channel": "pdf",
      "categories": [{ "vitec_id": 1, "name": "Akseptbrev" }],
      "tags": ["Vitec Next", "Standard"],
      "email_subject": null,
      "margins_cm": { "top": 1.5, "bottom": 1.0, "left": 1.0, "right": 1.2 },
      "content": "<div id=\"vitecTemplate\">...</div>",
      "metadata": {
        "vitec_last_modified": "2026-01-10T08:30:00Z"
      }
    }
  ]
}
```

