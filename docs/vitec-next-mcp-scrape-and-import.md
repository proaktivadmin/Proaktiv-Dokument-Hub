# Vitec Next → Proaktiv Dokument Hub (Chrome/MCP scraping + import)

This is the practical workflow to:

1) **Export** all Vitec Next document templates (including HTML source + metadata) via a Chrome-controlled session.
2) **Import** them into Proaktiv Dokument Hub with categories, tags, and Vitec settings.

## Prerequisites

- **Chrome browser control via MCP**: this repo already has the MCP server `cursor-browser-extension` available in Cursor (see `mcps/cursor-browser-extension` tool descriptors).
- **Ensure the browser MCP is connected**:
  - Install/enable the **Cursor Browser Extension** in Chrome/Edge.
  - In Cursor, ensure the MCP server **`cursor-browser-extension`** is enabled and connected.
  - Open a normal (non-incognito) Chrome tab so your Vitec session cookies are available.
- **Database access**: your backend must be able to connect to the database configured in `DATABASE_URL`.
- **Vitec categories seeded (recommended)**:

```bash
python backend/scripts/seed_vitec_categories.py
```

## 1) Export from Vitec Next (in Chrome)

Because Vitec Next is an external system, the exact selectors/endpoints can vary by tenant/version. The most robust approach is:

- **Prefer API/network scraping** (fastest): open the template list + a template, then inspect which API calls return the template list and template HTML.
- **Fallback to DOM scraping**: iterate templates in the UI and read the editor content from the page.

### Production safety (rate limits + clean exit)

- **Go slow**: keep requests strictly sequential and add delays (e.g., 1–2 seconds + small jitter) between template fetches.
- **Pause/resume**: write progress to disk every N templates so you can safely stop without re-fetching everything.
- **Avoid duplicate hits**: use the list endpoint once, then only fetch content per template ID.
- **Close templates with “Lukk”**: when leaving the editor, click the **Lukk** button to avoid the “leave/cancel” browser dialog.

Important: if you want all **Kategorisering** fields (phases, assignment types, ownership types, departments, receiver, etc.)
to be imported, fill them out in Vitec Next **before** exporting. The API export below pulls those values from
the template details endpoint.

### Option A: Network/API-driven export (recommended)

1. Open Vitec Next in Chrome and go to the **Document Templates** page.
2. Open **one template** in the editor (so Vitec loads the “template details/source” API calls).
3. Use your browser tooling (or MCP `browser_network_requests`) to identify:
   - the request that returns the **template list**
   - the request that returns **template content/source** for a given template id
4. Run an evaluation script (via MCP `browser_evaluate`) that:
   - fetches the list endpoint
   - iterates ids and fetches detail/source endpoints
   - assembles the JSON in the format described in `docs/vitec-next-export-format.md`
   - triggers a download of `vitec-next-export.json`

Example API export script (list + details + content):

```javascript
async () => {
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
  const jitter = (base, spread) => base + Math.floor(Math.random() * spread);

  const getToken = () => {
    const cookie = document.cookie
      .split(";")
      .map((s) => s.trim())
      .find((s) => s.startsWith("x-c__f="));
    return cookie ? cookie.slice("x-c__f=".length) : "";
  };

  const fetchJson = async (url, options) => {
    const res = await fetch(url, options);
    const json = await res.json();
    return { ok: res.ok, status: res.status, json };
  };

  const token = getToken();
  if (!token) throw new Error("Missing x-c__f token");

  const listUrl = new URL("/api/Document/getDocumentTemplateList", location.origin).toString();
  const detailUrl = new URL("/api/Document/getDocumentTemplateDetails", location.origin).toString();
  const contentUrl = new URL("/api/Document/getNextDocumentTemplateContentForEditing", location.origin).toString();

  const listRes = await fetchJson(listUrl, { credentials: "include" });
  const list = listRes.json?.value?.documentTemplates || [];

  const channelMap = { 0: "pdf_email", 1: "email", 2: "sms", 3: "pdf" };
  const receiverTypeMap = { 0: "Systemstandard", 1: "Kommunale", 2: "Egne/kundetilpasset" };

  const templates = [];

  for (const t of list) {
    const detailRes = await fetchJson(detailUrl, {
      method: "POST",
      credentials: "include",
      headers: {
        "content-type": "application/json;charset=utf-8",
        "x-c__f": token,
        "X-Requested-With": "XMLHttpRequest",
      },
      body: JSON.stringify({ documentTemplateId: t.id }),
    });
    const detail = detailRes.ok ? detailRes.json?.value || {} : {};

    const contentRes = await fetchJson(contentUrl, {
      method: "POST",
      credentials: "include",
      headers: {
        "content-type": "application/json;charset=utf-8",
        "x-c__f": token,
        "X-Requested-With": "XMLHttpRequest",
      },
      body: JSON.stringify({ documentTemplateId: t.id }),
    });
    const contentVal = contentRes.ok ? contentRes.json?.value || {} : {};
    const margins = contentVal.margins || {};
    const attachments = detail.attachments
      ?? detail.attachmentTemplates
      ?? detail.attachmentTemplateList
      ?? detail.documentTemplateAttachments
      ?? [];

    const receiverTypeRaw = receiverTypeMap[detail.receiverType ?? t.receiverType] || null;
    const receiverType = receiverTypeRaw === "Kommunale" ? null : receiverTypeRaw;
    const isVitecTemplate = Boolean(detail.isVitecTemplate ?? t.isVitec ?? false);
    const originTag = isVitecTemplate ? "Vitec Next" : "Kundemal";

    templates.push({
      vitec_template_id: t.id,
      title: (detail.name || t.name || "").trim(),
      description: null,
      status: (detail.isActive ?? t.isActive) === false ? "archived" : "published",
      channel: channelMap[detail.targetedChannel ?? t.targetedChannel] || "pdf_email",
      template_type: (detail.isSystem || t.isSystem || (detail.systemTemplateType ?? t.systemTemplateType) > 0)
        ? "System"
        : "Objekt/Kontakt",
      receiver_type: receiverType,
      receiver: (detail.receiverName || t.receiverName || "").trim() || null,
      extra_receivers: Array.isArray(detail.extraReceivers) ? detail.extraReceivers : [],
      phases: Array.isArray(detail.phases) ? detail.phases : (Array.isArray(t.phases) ? t.phases : []),
      assignment_types: Array.isArray(detail.assignmentTypes) ? detail.assignmentTypes : (Array.isArray(t.assignmentTypes) ? t.assignmentTypes : []),
      ownership_types: Array.isArray(detail.ownershipTypes) ? detail.ownershipTypes : (Array.isArray(t.ownershipTypes) ? t.ownershipTypes : []),
      departments: Array.isArray(detail.departments) ? detail.departments : (Array.isArray(t.departments) ? t.departments : []),
      email_subject: detail.emailSubject || t.emailSubject || null,
      categories: (detail.categoryName || t.categoryName)
        ? [{ name: detail.categoryName || t.categoryName, vitec_id: detail.categoryId ?? t.categoryId ?? null }]
        : [],
      tags: [originTag],
      attachments,
      margins_cm: {
        top: margins.top ?? t.paddingTop ?? null,
        bottom: margins.bottom ?? t.paddingBottom ?? null,
        left: margins.left ?? t.paddingLeft ?? null,
        right: margins.right ?? t.paddingRight ?? null,
      },
      header_template_id: detail.headerTemplateId ?? t.headerTemplateId ?? null,
      footer_template_id: detail.footerTemplateId ?? t.footerTemplateId ?? null,
      content: typeof contentVal.htmlContent === "string" ? contentVal.htmlContent : "",
      metadata: {
        vitec_raw: t,
        vitec_details: detail,
        content_meta: { margins, udf_fields: contentVal.udfFields || [] },
      },
    });

    await sleep(jitter(1500, 800));
  }

  const exportObj = {
    export_version: "1",
    exported_at: new Date().toISOString(),
    source: { system: "vitec-next", method: "api", note: "sequential, rate-limited" },
    templates,
  };

  const blob = new Blob([JSON.stringify(exportObj, null, 2)], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "vitec-next-export.json";
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);

  return { templates_exported: templates.length };
}
```

### Option B: DOM-driven export (generic fallback)

If you can’t find stable API endpoints, start with this generic snippet and **only change the selectors** at the top to match the Vitec Next UI.

Run this in the page context (via MCP `browser_evaluate`):

```javascript
async () => {
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

  // TODO: adjust these selectors to your Vitec Next UI
  const cfg = {
    templateRowSelector: "a", // selector that matches each template entry in the list
    titleSelector: "input[name='title'], input[type='text']",
    categorySelector: "select[name='category']",
    channelSelector: "select[name='channel']",
    editorSelector: "textarea, .monaco-editor",
  };

  const readEditorValue = () => {
    // Monaco (best effort)
    if (window.monaco?.editor?.getModels?.) {
      const model = window.monaco.editor.getModels()[0];
      if (model) return model.getValue();
    }
    // textarea
    const ta = document.querySelector("textarea");
    if (ta && "value" in ta) return ta.value;
    // fallback: capture DOM text
    const el = document.querySelector(cfg.editorSelector);
    return el ? (el.textContent || "").trim() : "";
  };

  const readSelectText = (sel) => {
    const el = document.querySelector(sel);
    if (!el) return null;
    if (el.tagName === "SELECT") {
      const opt = el.selectedOptions?.[0];
      return opt ? (opt.textContent || "").trim() : null;
    }
    return (el.textContent || "").trim();
  };

  const readInputValue = (sel) => {
    const el = document.querySelector(sel);
    if (!el) return null;
    return ("value" in el ? String(el.value) : (el.textContent || "")).trim();
  };

  const templateLinks = Array.from(document.querySelectorAll(cfg.templateRowSelector));
  const templates = [];

  for (let i = 0; i < templateLinks.length; i++) {
    const link = templateLinks[i];
    link.click();
    await sleep(400); // may need to increase

    const title = readInputValue(cfg.titleSelector) || link.textContent?.trim() || `Template ${i + 1}`;
    const categoryName = readSelectText(cfg.categorySelector);
    const channel = readSelectText(cfg.channelSelector) || "pdf_email";
    const content = readEditorValue();

    // Skip non-templates / empty editor
    if (!content) continue;

    templates.push({
      vitec_template_id: `${title}__${i}`, // TODO: replace with real Vitec ID when available
      title,
      channel,
      categories: categoryName ? [{ vitec_id: null, name: categoryName }] : [],
      tags: ["Vitec Next"],
      content,
      metadata: {
        dom_export_index: i,
      },
    });
  }

  const exportObj = {
    export_version: "1",
    exported_at: new Date().toISOString(),
    source: { system: "vitec-next", method: "dom" },
    templates,
  };

  const blob = new Blob([JSON.stringify(exportObj, null, 2)], { type: "application/json" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "vitec-next-export.json";
  document.body.appendChild(a);
  a.click();
  a.remove();
  URL.revokeObjectURL(url);

  return { templates_exported: templates.length };
}
```

Notes:
- You’ll get the best results if you can export a **real** `vitec_template_id` from the UI or the network payload.
- If Vitec uses multiple pages, add pagination to the loop.

## 2) Import into Proaktiv Dokument Hub

Put the exported file somewhere under `data/` (it’s gitignored):

- `data/vitec-next-export.json`

Then run:

```bash
python backend/scripts/import_vitec_next_export.py --input data/vitec-next-export.json
```

Useful flags:

- `--dry-run`: prints what would be created/updated without writing
- `--update-existing`: updates records when the derived `file_name` already exists
- `--match-title`: when `file_name` is new, match existing templates by title (case-insensitive)
- `--auto-sanitize`: sanitize HTML during import
- `--created-by "you@proaktiv.no"`: sets `created_by/updated_by`

