/**
 * Reports API
 *
 * Sales report and other downloadable reports.
 */

import { apiClient } from "./config";

export interface SalesReportParams {
  year?: number;
  department_id?: number;
  include_vat?: boolean;
}

/**
 * Download sales report as Excel file.
 * Returns blob for file download.
 */
export async function downloadSalesReport(params?: SalesReportParams): Promise<Blob> {
  const searchParams = new URLSearchParams();
  if (params?.year) searchParams.set("year", String(params.year));
  if (params?.department_id) searchParams.set("department_id", String(params.department_id));
  if (params?.include_vat) searchParams.set("include_vat", "true");

  const url = `/reports/sales-report${searchParams.toString() ? `?${searchParams}` : ""}`;
  try {
    const response = await apiClient.get(url, {
      responseType: "blob",
      validateStatus: (status) => status === 200,
    });

    return response.data as Blob;
  } catch (err) {
    const axiosErr = err as { response?: { data?: Blob | string; status?: number } };
    const data = axiosErr.response?.data;
    let detail = "Kunne ikke laste ned rapporten.";
    if (data) {
      try {
        const text = typeof data === "string" ? data : await (data as Blob).text();
        const json = JSON.parse(text) as { detail?: string };
        if (json.detail) detail = json.detail;
      } catch {
        // ignore
      }
    }
    throw new Error(detail);
  }
}
