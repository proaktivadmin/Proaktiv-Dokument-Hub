/**
 * Vitec Next Template Deploy Script
 *
 * Deploys an updated template to Vitec Next by:
 * 1. Backing up the current production version via API
 * 2. Updating the template content via the save API endpoint
 *
 * This script runs in the browser context on a Vitec Next page.
 * It uses the same API patterns as the export script.
 *
 * Usage (via cursor-ide-browser MCP):
 *   1. Log into Vitec Next in the browser
 *   2. Navigate to any page on proaktiv.vitecnext.no
 *   3. Run this script via browser_navigate with javascript: URL
 *
 * The script expects these variables to be set in localStorage:
 *   - vitec_deploy_template_id: the UUID of the template to update
 *   - vitec_deploy_html_content: the new HTML content to deploy
 *
 * Set them before running:
 *   localStorage.setItem('vitec_deploy_template_id', '<uuid>');
 *   localStorage.setItem('vitec_deploy_html_content', '<html>...');
 *
 * After execution, results are stored in:
 *   localStorage.getItem('vitec_deploy_result') -> JSON with status
 */
(async () => {
  const STORAGE_KEY_ID = "vitec_deploy_template_id";
  const STORAGE_KEY_HTML = "vitec_deploy_html_content";
  const STORAGE_KEY_RESULT = "vitec_deploy_result";

  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

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

  const storeResult = (result) => {
    localStorage.setItem(STORAGE_KEY_RESULT, JSON.stringify(result));
    document.title = `Deploy: ${result.status}`;
  };

  try {
    const token = getToken();
    if (!token) {
      storeResult({
        status: "error",
        error: "Missing x-c__f token. Are you logged into Vitec Next?",
      });
      return;
    }

    const templateId = localStorage.getItem(STORAGE_KEY_ID);
    const newHtml = localStorage.getItem(STORAGE_KEY_HTML);

    if (!templateId) {
      storeResult({
        status: "error",
        error: `No template ID set. Run: localStorage.setItem('${STORAGE_KEY_ID}', '<uuid>')`,
      });
      return;
    }

    if (!newHtml) {
      storeResult({
        status: "error",
        error: `No HTML content set. Run: localStorage.setItem('${STORAGE_KEY_HTML}', '<html>')`,
      });
      return;
    }

    document.title = "Deploy: backing up...";

    // Step 1: Fetch the current template content as a backup
    const contentUrl = new URL(
      "/api/Document/getNextDocumentTemplateContentForEditing",
      location.origin
    ).toString();

    const headers = {
      "content-type": "application/json;charset=utf-8",
      "x-c__f": token,
      "X-Requested-With": "XMLHttpRequest",
    };

    const backupRes = await fetchJson(contentUrl, {
      method: "POST",
      credentials: "include",
      headers,
      body: JSON.stringify({ documentTemplateId: templateId }),
    });

    const backupHtml = backupRes.ok
      ? backupRes.json?.value?.htmlContent || ""
      : "";

    if (!backupRes.ok) {
      storeResult({
        status: "error",
        error: `Failed to fetch current content for backup. HTTP ${backupRes.status}`,
        template_id: templateId,
      });
      return;
    }

    document.title = "Deploy: saving...";

    // Step 2: Save the new content
    // Try the known save endpoint pattern
    const saveUrl = new URL(
      "/api/Document/saveNextDocumentTemplateContent",
      location.origin
    ).toString();

    const saveRes = await fetchJson(saveUrl, {
      method: "POST",
      credentials: "include",
      headers,
      body: JSON.stringify({
        documentTemplateId: templateId,
        htmlContent: newHtml,
      }),
    });

    if (saveRes.ok) {
      storeResult({
        status: "success",
        template_id: templateId,
        backup_html_length: backupHtml.length,
        new_html_length: newHtml.length,
        deployed_at: new Date().toISOString(),
        method: "api",
      });

      // Store backup for safety
      localStorage.setItem(
        `vitec_deploy_backup_${templateId}`,
        backupHtml
      );

      // Clean up deploy inputs
      localStorage.removeItem(STORAGE_KEY_ID);
      localStorage.removeItem(STORAGE_KEY_HTML);
      return;
    }

    // If the save API endpoint doesn't exist or fails,
    // fall back to the UI automation approach
    document.title = "Deploy: API save failed, trying UI approach...";
    await sleep(1000);

    // Store backup and signal that manual UI automation is needed
    localStorage.setItem(
      `vitec_deploy_backup_${templateId}`,
      backupHtml
    );

    storeResult({
      status: "needs_ui_automation",
      template_id: templateId,
      api_error: `Save API returned HTTP ${saveRes.status}`,
      backup_html_length: backupHtml.length,
      new_html_length: newHtml.length,
      instructions: [
        "The save API endpoint was not found or failed.",
        "Use browser automation to deploy via the CKEditor UI:",
        "1. Navigate to Administrasjon > Dokumentmaler",
        "2. Find and open the template in the editor",
        "3. Switch to source view (Kilde button)",
        "4. Clear and paste the new HTML content",
        "5. Save and close the editor",
      ],
    });
  } catch (err) {
    storeResult({
      status: "error",
      error: err.message || String(err),
    });
  }
})();
