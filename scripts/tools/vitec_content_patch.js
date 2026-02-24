/**
 * Vitec Next Content Patch Script
 *
 * Fetches HTML content + details for templates that are missing content
 * in the existing vitec-next-export.json. Run via browser_evaluate while
 * logged into Vitec Next.
 *
 * Usage:
 *   1. Log into Vitec Next in Chrome
 *   2. Run this script via browser_evaluate (MCP cursor-ide-browser)
 *   3. The script processes templates in batches, saving progress to localStorage
 *   4. Re-run if interrupted — it resumes from where it left off
 *   5. When done, it triggers a download of vitec-next-content-patch.json
 *
 * The script fetches from two endpoints per template:
 *   - POST /api/Document/getDocumentTemplateDetails
 *   - POST /api/Document/getNextDocumentTemplateContentForEditing
 */
async () => {
  const BATCH_SIZE = 25;
  const STORAGE_KEY = "vitec_content_patch_progress";
  const STORAGE_RESULTS_KEY = "vitec_content_patch_results";

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

  const detailUrl = new URL("/api/Document/getDocumentTemplateDetails", location.origin).toString();
  const contentUrl = new URL("/api/Document/getNextDocumentTemplateContentForEditing", location.origin).toString();

  const templateIds = %%TEMPLATE_IDS%%;

  // Resume support
  let completedMap = {};
  try {
    const saved = localStorage.getItem(STORAGE_RESULTS_KEY);
    if (saved) completedMap = JSON.parse(saved);
  } catch {}

  const remaining = templateIds.filter((id) => !completedMap[id]);

  if (remaining.length === 0) {
    // All done — trigger download
    const blob = new Blob([JSON.stringify(completedMap, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "vitec-next-content-patch.json";
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);

    localStorage.removeItem(STORAGE_KEY);
    localStorage.removeItem(STORAGE_RESULTS_KEY);

    return {
      status: "complete",
      total: templateIds.length,
      fetched: Object.keys(completedMap).length,
      remaining: 0,
    };
  }

  const batch = remaining.slice(0, BATCH_SIZE);
  let fetchedCount = 0;
  let errorCount = 0;

  for (const id of batch) {
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
        body: JSON.stringify({ documentTemplateId: id }),
      });

      const contentRes = await fetchJson(contentUrl, {
        method: "POST",
        credentials: "include",
        headers,
        body: JSON.stringify({ documentTemplateId: id }),
      });

      const detail = detailRes.ok ? detailRes.json?.value || {} : {};
      const contentVal = contentRes.ok ? contentRes.json?.value || {} : {};

      completedMap[id] = {
        content: typeof contentVal.htmlContent === "string" ? contentVal.htmlContent : "",
        margins: contentVal.margins || {},
        udf_fields: contentVal.udfFields || [],
        details: detail,
        fetched_at: new Date().toISOString(),
        detail_ok: detailRes.ok,
        content_ok: contentRes.ok,
      };

      fetchedCount++;
    } catch (err) {
      completedMap[id] = {
        content: "",
        margins: {},
        udf_fields: [],
        details: {},
        fetched_at: new Date().toISOString(),
        error: String(err),
        detail_ok: false,
        content_ok: false,
      };
      errorCount++;
    }

    // Save progress after each template
    localStorage.setItem(STORAGE_RESULTS_KEY, JSON.stringify(completedMap));
    await sleep(jitter(1500, 800));
  }

  const totalCompleted = Object.keys(completedMap).length;
  const totalRemaining = templateIds.length - totalCompleted;

  if (totalRemaining === 0) {
    // Finished with this batch — trigger download
    const blob = new Blob([JSON.stringify(completedMap, null, 2)], { type: "application/json" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "vitec-next-content-patch.json";
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);

    localStorage.removeItem(STORAGE_KEY);
    localStorage.removeItem(STORAGE_RESULTS_KEY);
  }

  return {
    status: totalRemaining === 0 ? "complete" : "in_progress",
    total: templateIds.length,
    fetched_this_batch: fetchedCount,
    errors_this_batch: errorCount,
    total_completed: totalCompleted,
    remaining: totalRemaining,
    message: totalRemaining > 0
      ? `Run this script again to fetch the next batch (${totalRemaining} remaining)`
      : "All templates fetched! Download triggered.",
  };
}
