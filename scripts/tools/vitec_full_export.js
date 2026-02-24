/**
 * Vitec Next Full Export Script
 *
 * Complete re-export: fetches template list, details, and HTML content
 * for all templates. Produces a full vitec-next-export.json.
 *
 * Same as the script in docs/vitec-next-mcp-scrape-and-import.md but
 * with batch/resume support via localStorage.
 *
 * Usage:
 *   1. Log into Vitec Next in Chrome
 *   2. Run via browser_evaluate — processes 25 templates per batch
 *   3. Re-run until status is 'complete'
 *   4. Final run downloads vitec-next-export.json
 */
async () => {
  const BATCH_SIZE = 25;
  const STORAGE_KEY = "vitec_full_export_progress";

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
    if (!res.ok) return { ok: false, status: res.status, json: null };
    try {
      const json = await res.json();
      return { ok: true, status: res.status, json };
    } catch {
      return { ok: false, status: res.status, json: null };
    }
  };

  const token = getToken();
  if (!token) throw new Error("Missing x-c__f token — are you logged into Vitec Next?");

  const listUrl = new URL("/api/Document/getDocumentTemplateList", location.origin).toString();
  const detailUrl = new URL("/api/Document/getDocumentTemplateDetails", location.origin).toString();
  const contentUrl = new URL("/api/Document/getNextDocumentTemplateContentForEditing", location.origin).toString();

  const channelMap = { 0: "pdf_email", 1: "email", 2: "sms", 3: "pdf" };
  const receiverTypeMap = { 0: "Systemstandard", 1: "Kommunale", 2: "Egne/kundetilpasset" };

  // Load or fetch template list
  let progress = {};
  try {
    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved) progress = JSON.parse(saved);
  } catch {}

  if (!progress.list || !Array.isArray(progress.list)) {
    const listRes = await fetchJson(listUrl, { credentials: "include" });
    progress.list = listRes.json?.value?.documentTemplates || [];
    progress.templates = progress.templates || {};
    localStorage.setItem(STORAGE_KEY, JSON.stringify(progress));
  }

  const list = progress.list;
  const completedIds = new Set(Object.keys(progress.templates || {}));
  const remaining = list.filter((t) => !completedIds.has(t.id));

  if (remaining.length === 0) {
    // Build final export
    const templates = list.map((t) => {
      const saved = (progress.templates || {})[t.id] || {};
      return saved.template || {
        vitec_template_id: t.id,
        title: (t.name || "").trim(),
        content: "",
        metadata: { vitec_raw: t },
      };
    });

    const exportObj = {
      export_version: "1",
      exported_at: new Date().toISOString(),
      source: { system: "vitec-next", method: "api", note: "batched export with resume" },
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

    localStorage.removeItem(STORAGE_KEY);

    return {
      status: "complete",
      total: list.length,
      templates_exported: templates.length,
      message: "Download triggered! Save the file.",
    };
  }

  const batch = remaining.slice(0, BATCH_SIZE);
  let fetchedCount = 0;
  let errorCount = 0;

  for (const t of batch) {
    try {
      const headers = {
        "content-type": "application/json;charset=utf-8",
        "x-c__f": token,
        "X-Requested-With": "XMLHttpRequest",
      };

      const detailRes = await fetchJson(detailUrl, {
        method: "POST",
        credentials: "include",
        headers,
        body: JSON.stringify({ documentTemplateId: t.id }),
      });
      const detail = detailRes.ok ? detailRes.json?.value || {} : {};

      const contentRes = await fetchJson(contentUrl, {
        method: "POST",
        credentials: "include",
        headers,
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

      const template = {
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
      };

      progress.templates = progress.templates || {};
      progress.templates[t.id] = { template, fetched_at: new Date().toISOString() };
      fetchedCount++;
    } catch (err) {
      progress.templates = progress.templates || {};
      progress.templates[t.id] = {
        template: {
          vitec_template_id: t.id,
          title: (t.name || "").trim(),
          content: "",
          metadata: { vitec_raw: t, error: String(err) },
        },
        fetched_at: new Date().toISOString(),
        error: String(err),
      };
      errorCount++;
    }

    localStorage.setItem(STORAGE_KEY, JSON.stringify(progress));
    await sleep(jitter(1500, 800));
  }

  const totalCompleted = Object.keys(progress.templates || {}).length;
  const totalRemaining = list.length - totalCompleted;

  return {
    status: totalRemaining === 0 ? "complete" : "in_progress",
    total: list.length,
    fetched_this_batch: fetchedCount,
    errors_this_batch: errorCount,
    total_completed: totalCompleted,
    remaining: totalRemaining,
    message: totalRemaining > 0
      ? `Run again to fetch next batch (${totalRemaining} remaining, ~${Math.ceil(totalRemaining / BATCH_SIZE)} more runs)`
      : "All done! Run once more to trigger download.",
  };
}
